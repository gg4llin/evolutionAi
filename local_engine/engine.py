"""Core orchestration engine that pairs with the AdaptiveAgent CustomGPT."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .rubric_profile import RubricProfile
from .specialization import SpecializationTrack, resolve_specialization
from .optimization_profile import CYCLES, Cycle
from .metadata_repository import MetadataRepository
from .judgement_system import JudgementSystem


@dataclass
class WorkerRecord:
    worker_id: str
    specialization: str
    track: SpecializationTrack
    status: str = "initializing"
    spawned_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    composite_score: float = 0.0


class AdaptiveAgentEngine:
    """In-memory control-plane coordinator for Tadpole workers."""

    def __init__(self, control_plane_cfg: Dict[str, Any]) -> None:
        self._cfg = control_plane_cfg
        self._workers: Dict[str, WorkerRecord] = {}
        self._event_log: List[Dict[str, Any]] = []
        self._last_heartbeat: Optional[float] = None
        self._rubric = RubricProfile()
        self._cycles: Dict[str, Cycle] = CYCLES
        self._cycle_history: List[Dict[str, Any]] = []
        self._metadata_repository = MetadataRepository(self._rubric)
        self._judgement_system = JudgementSystem(self._metadata_repository)

    # ---------------------------- lifecycle ----------------------------
    def spawn_worker(self, payload: Dict[str, Any]) -> WorkerRecord:
        template = self._cfg["worker_fleets"]["tadpole_workers"]
        if len(self._workers) >= template["max_parallel_workers"]:
            raise RuntimeError("Worker limit reached; adjust max_parallel_workers before spawning.")

        worker_id = payload.get("worker_id") or str(uuid.uuid4())
        track = resolve_specialization(payload.get("trigger"), payload.get("specialization"))
        record = WorkerRecord(worker_id=worker_id, specialization=track.name, track=track)
        record.metadata.update({"focus_metrics": track.focus_metrics})
        record.metadata.update(payload.get("metadata", {}))

        self._workers[worker_id] = record
        self._append_event("spawn", record=record)
        return record

    def retire_worker(self, worker_id: str, reason: Optional[str] = None) -> WorkerRecord:
        record = self._workers.pop(worker_id, None)
        if not record:
            raise KeyError(f"Worker {worker_id} not found.")

        record.status = "retired"
        record.metadata["retired_at"] = time.time()
        if reason:
            record.metadata["retire_reason"] = reason
        self._append_event("retire", record=record)
        return record

    def record_status(self, worker_id: str, status: str, details: Optional[Dict[str, Any]] = None) -> WorkerRecord:
        if worker_id not in self._workers:
            raise KeyError(f"Worker {worker_id} not found.")
        record = self._workers[worker_id]
        record.status = status
        if details:
            record.metadata.update(details)
            metrics_payload = details.get("metrics") if isinstance(details, dict) else None
            if isinstance(metrics_payload, dict):
                record.composite_score = self._rubric.composite_score(metrics_payload)
                self._metadata_repository.ingest(record.worker_id, record.specialization, metrics_payload)
        self._append_event("status", record=record)
        return record

    def trigger_cycle(self, cycle_name: str, initiator: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if cycle_name not in self._cycles:
            raise KeyError(f"Unknown optimization cycle: {cycle_name}")
        cycle = self._cycles[cycle_name]
        entry = {
            "cycle": cycle.name,
            "duration": cycle.duration,
            "focus": cycle.focus,
            "scope": cycle.scope,
            "targets": cycle.targets,
            "triggered_at": time.time(),
            "initiator": initiator or self._cfg["main_engine"].get("identity"),
            "metadata": metadata or {},
        }
        self._cycle_history.append(entry)
        if len(self._cycle_history) > 50:
            self._cycle_history = self._cycle_history[-50:]
        self._append_event("optimization_cycle", metadata={
            "cycle": cycle.name,
            "initiator": entry["initiator"],
            "targets": cycle.targets,
        })
        return entry

    def revise_egg(self) -> Dict[str, Any]:
        revision = self._judgement_system.build_revision()
        self._append_event("egg_revision", metadata={"adjustments": revision["adjustments"]})
        return revision

    # ----------------------------- telemetry -----------------------------
    def heartbeat(self) -> Dict[str, Any]:
        now = time.time()
        self._last_heartbeat = now
        return {
            "identity": self._cfg["main_engine"]["identity"],
            "timestamp": now,
            "active_workers": len(self._workers),
            "topics": {
                "commands": self._cfg["main_engine"]["command_topic"],
                "heartbeat": self._cfg["main_engine"]["heartbeat_topic"],
            },
        }

    def metrics_snapshot(self) -> Dict[str, Any]:
        return {
            "active_workers": len(self._workers),
            "worker_ids": list(self._workers.keys()),
            "last_heartbeat": self._last_heartbeat,
            "event_log_length": len(self._event_log),
            "composite_scores": {
                worker_id: record.composite_score for worker_id, record in self._workers.items()
            },
            "focus_metrics": {
                worker_id: record.track.focus_metrics for worker_id, record in self._workers.items()
            },
            "recent_cycles": self._cycle_history[-5:],
            "aggregate_metrics": self._metadata_repository.metrics_mean(),
            "principle_scores": self._metadata_repository.principle_averages(),
        }

    # ---------------------------- internals ----------------------------
    def _append_event(
        self,
        event_type: str,
        *,
        record: Optional[WorkerRecord] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        base_metadata = record.metadata.copy() if record else {}
        event: Dict[str, Any] = {
            "event": event_type,
            "timestamp": time.time(),
            "metadata": base_metadata,
        }
        if metadata:
            event["metadata"].update(metadata)
        if record:
            event.update(
                {
                    "worker_id": record.worker_id,
                    "status": record.status,
                    "specialization": record.specialization,
                    "composite_score": record.composite_score,
                }
            )
        self._event_log.append(event)

    # ----------------------------- helpers -----------------------------
    @property
    def config(self) -> Dict[str, Any]:
        return self._cfg

    @property
    def workers(self) -> Dict[str, WorkerRecord]:
        return self._workers

    @property
    def event_log(self) -> List[Dict[str, Any]]:
        return self._event_log
