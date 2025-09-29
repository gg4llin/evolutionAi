"""Core orchestration engine that pairs with the AdaptiveAgent CustomGPT."""
from __future__ import annotations

import concurrent.futures
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .rubric_profile import RubricProfile
from .specialization import SpecializationTrack, resolve_specialization
from .optimization_profile import CYCLES, Cycle
from .metadata_repository import MetadataRepository
from .judgement_system import JudgementSystem
from .resource_manager import ResourceChunk, ResourcePool, InsufficientResourcesError


@dataclass
class WorkerRecord:
    worker_id: str
    specialization: str
    track: SpecializationTrack
    status: str = "initializing"
    spawned_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    composite_score: float = 0.0
    job_id: Optional[str] = None
    allocated_resources: Optional[ResourceChunk] = None


@dataclass
class JobRecord:
    job_id: str
    objective: str
    status: str = "queued"
    reward_signal: float = 0.0
    requested_resources: Dict[str, int] = field(default_factory=dict)
    allocated_resources: Optional[ResourceChunk] = None
    tadpole_ids: List[str] = field(default_factory=list)
    submitted_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    expected_duration_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    worker_id: Optional[str] = None


@dataclass
class WorkerAgent:
    worker_id: str
    state: str = "idle"
    active_job: Optional[str] = None
    improvement_metrics: Dict[str, float] = field(
        default_factory=lambda: {
            "quest_success_rate": 0.0,
            "resource_efficiency": 0.0,
            "protocol_innovation_score": 0.0,
            "toolchain_adoption_rate": 0.0,
        }
    )
    quest_log: List[Dict[str, Any]] = field(default_factory=list)
    known_protocols: List[str] = field(
        default_factory=lambda: ["mesh_networking_protocol", "binary_symbolic_protocol"]
    )
    discovered_tools: List[str] = field(default_factory=list)


class AdaptiveAgentEngine:
    """In-memory control-plane coordinator for Tadpole workers."""

    def __init__(self, connectivity_cfg: Dict[str, Any]) -> None:
        control_plane_cfg = connectivity_cfg.get("control_plane", connectivity_cfg)
        self._cfg = control_plane_cfg
        self._tadpoles: Dict[str, WorkerRecord] = {}
        self._workers: Dict[str, WorkerAgent] = {}
        self._event_log: List[Dict[str, Any]] = []
        self._last_heartbeat: Optional[float] = None
        self._rubric = RubricProfile()
        self._cycles: Dict[str, Cycle] = CYCLES
        self._cycle_history: List[Dict[str, Any]] = []
        self._metadata_repository = MetadataRepository(self._rubric)
        self._judgement_system = JudgementSystem(self._metadata_repository)
        resource_cfg = connectivity_cfg.get("resource_pools", {})
        min_chunk = resource_cfg.get("min_chunk", {"compute_units": 1, "memory_mb": 128, "bandwidth_mbps": 50})
        self._resource_pool = ResourcePool(
            compute_units_total=resource_cfg.get("compute_units_total", 256),
            memory_mb_total=resource_cfg.get("memory_mb_total", 65536),
            bandwidth_mbps_total=resource_cfg.get("bandwidth_mbps_total", 10000),
            max_threads=resource_cfg.get("max_threads", 128),
            min_chunk=min_chunk,
        )
        self._jobs: Dict[str, JobRecord] = {}
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=self._resource_pool.capacity()["threads_total"])

    # ---------------------------- lifecycle ----------------------------
    def spawn_worker(self, payload: Dict[str, Any]) -> WorkerRecord:
        template = self._cfg["worker_fleets"]["tadpole_workers"]
        if len(self._tadpoles) >= template["max_parallel_workers"]:
            raise RuntimeError("Worker limit reached; adjust max_parallel_workers before spawning.")

        worker_id = payload.get("worker_id") or str(uuid.uuid4())
        track = resolve_specialization(payload.get("trigger"), payload.get("specialization"))
        record = WorkerRecord(worker_id=worker_id, specialization=track.name, track=track)
        record.metadata.update({"focus_metrics": track.focus_metrics})
        record.metadata.update(payload.get("metadata", {}))
        record.job_id = payload.get("job_id")
        if "allocated_resources" in payload:
            record.allocated_resources = payload["allocated_resources"]

        self._tadpoles[worker_id] = record
        self._append_event("spawn", record=record)
        return record

    def retire_worker(self, worker_id: str, reason: Optional[str] = None) -> WorkerRecord:
        record = self._tadpoles.pop(worker_id, None)
        if not record:
            raise KeyError(f"Worker {worker_id} not found.")

        record.status = "retired"
        record.metadata["retired_at"] = time.time()
        if reason:
            record.metadata["retire_reason"] = reason
        self._append_event("retire", record=record)
        return record

    def record_status(self, worker_id: str, status: str, details: Optional[Dict[str, Any]] = None) -> WorkerRecord:
        if worker_id not in self._tadpoles:
            raise KeyError(f"Worker {worker_id} not found.")
        record = self._tadpoles[worker_id]
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

    # --------------------------- worker control ---------------------------
    def assign_worker(self, payload: Dict[str, Any]) -> WorkerAgent:
        worker_id = payload.get("worker_id") or str(uuid.uuid4())
        if worker_id in self._workers:
            raise ValueError(f"Worker {worker_id} already exists")

        worker = WorkerAgent(worker_id=worker_id)
        worker.state = payload.get("state", "idle")
        worker.known_protocols = payload.get("known_protocols", worker.known_protocols)
        worker.discovered_tools = payload.get("discovered_tools", [])
        self._workers[worker_id] = worker

        self._append_event(
            "worker_created",
            metadata={
                "worker_id": worker.worker_id,
                "state": worker.state,
                "known_protocols": worker.known_protocols,
            },
        )
        return worker

    def get_worker(self, worker_id: str) -> WorkerAgent:
        if worker_id not in self._workers:
            raise KeyError(f"Worker {worker_id} not found")
        return self._workers[worker_id]

    def list_workers(self) -> List[Dict[str, Any]]:
        return [self._worker_snapshot(worker) for worker in self._workers.values()]

    def get_worker_snapshot(self, worker_id: str) -> Dict[str, Any]:
        return self._worker_snapshot(self.get_worker(worker_id))

    def update_worker_metrics(self, worker_id: str, metrics_payload: Dict[str, float]) -> None:
        worker = self.get_worker(worker_id)
        for key, value in metrics_payload.items():
            if key in worker.improvement_metrics:
                # simple moving average with emphasis on recent data
                worker.improvement_metrics[key] = round(
                    (worker.improvement_metrics[key] * 0.7) + (value * 0.3), 4
                )
        worker.quest_log.append({"metrics": metrics_payload, "timestamp": time.time()})

    def retire_worker_agent(self, worker_id: str, reason: str = "engine_request") -> WorkerAgent:
        worker = self._workers.pop(worker_id, None)
        if not worker:
            raise KeyError(f"Worker {worker_id} not found")
        worker.state = "archived"
        self._append_event(
            "worker_archived",
            metadata={"worker_id": worker.worker_id, "reason": reason},
        )
        return worker

    def submit_job(self, payload: Dict[str, Any]) -> JobRecord:
        job_id = payload.get("job_id")
        if not job_id:
            raise ValueError("assign_job requires args.job_id")
        if job_id in self._jobs:
            raise ValueError(f"Job {job_id} already exists")

        requested_resources = payload.get("requested_resources", {})
        try:
            allocation = self._resource_pool.allocate(requested_resources)
        except InsufficientResourcesError as exc:
            raise RuntimeError(str(exc)) from exc

        job = JobRecord(
            job_id=job_id,
            objective=payload.get("objective", "unspecified"),
            reward_signal=float(payload.get("reward_signal", 0.0)),
            requested_resources=requested_resources,
            allocated_resources=allocation,
            expected_duration_seconds=payload.get("expected_duration_seconds"),
            metadata=payload.get("metadata", {}),
        )
        job.status = "running"
        job.started_at = time.time()

        worker_id = payload.get("worker_id")
        worker_agent: WorkerAgent
        if worker_id:
            worker_agent = self.get_worker(worker_id)
        else:
            worker_agent = self.assign_worker({"state": "scaffolding"})
            worker_id = worker_agent.worker_id

        worker_agent.state = "questing"
        worker_agent.active_job = job_id
        worker_agent.quest_log.append(
            {
                "quest_id": job_id,
                "objective": job.objective,
                "requested_resources": requested_resources,
                "protocol_overrides": payload.get("protocol_overrides", []),
                "external_endpoints": payload.get("external_endpoints", []),
                "timestamp": job.started_at,
            }
        )

        new_protocols = payload.get("protocol_overrides") or []
        for protocol in new_protocols:
            if protocol not in worker_agent.known_protocols:
                worker_agent.known_protocols.append(protocol)

        job.worker_id = worker_id

        tadpole_count = max(int(payload.get("tadpole_count", 1)), 1)
        for _ in range(tadpole_count):
            worker = self.spawn_worker(
                {
                    "job_id": job_id,
                    "metadata": {
                        "resource_allocation": {
                            "compute_units": allocation.compute_units // tadpole_count,
                            "memory_mb": allocation.memory_mb // tadpole_count,
                            "bandwidth_mbps": allocation.bandwidth_mbps // tadpole_count,
                            "threads": max(1, allocation.threads // tadpole_count),
                        },
                        "communication_mode": "binary_symbolic",
                    },
                    "allocated_resources": allocation,
                }
            )
            job.tadpole_ids.append(worker.worker_id)

        self._jobs[job_id] = job
        duration = job.expected_duration_seconds or 10
        self._executor.submit(self._simulate_job, job.job_id, duration)
        self._append_event(
            "job_started",
            metadata={
                "job_id": job.job_id,
                "objective": job.objective,
                "requested_resources": requested_resources,
                "allocated_resources": job.allocated_resources.__dict__ if job.allocated_resources else {},
                "worker_id": worker_id,
            },
        )
        return job

    def get_job(self, job_id: str) -> JobRecord:
        if job_id not in self._jobs:
            raise KeyError(f"Job {job_id} not found")
        return self._jobs[job_id]

    def get_job_snapshot(self, job_id: str) -> Dict[str, Any]:
        return self._job_snapshot(self.get_job(job_id))

    def list_jobs(self) -> List[Dict[str, Any]]:
        return [self._job_snapshot(job) for job in self._jobs.values()]

    # ----------------------------- telemetry -----------------------------
    def heartbeat(self) -> Dict[str, Any]:
        now = time.time()
        self._last_heartbeat = now
        return {
            "identity": self._cfg["main_engine"]["identity"],
            "timestamp": now,
            "active_workers": len(self._tadpoles),
            "topics": {
                "commands": self._cfg["main_engine"]["command_topic"],
                "heartbeat": self._cfg["main_engine"]["heartbeat_topic"],
            },
            "resource_utilisation": self._resource_pool.utilisation(),
        }

    def metrics_snapshot(self) -> Dict[str, Any]:
        return {
            "active_workers": len(self._tadpoles),
            "worker_ids": list(self._tadpoles.keys()),
            "last_heartbeat": self._last_heartbeat,
            "event_log_length": len(self._event_log),
            "composite_scores": {
                worker_id: record.composite_score for worker_id, record in self._tadpoles.items()
            },
            "focus_metrics": {
                worker_id: record.track.focus_metrics for worker_id, record in self._tadpoles.items()
            },
            "recent_cycles": self._cycle_history[-5:],
            "aggregate_metrics": self._metadata_repository.metrics_mean(),
            "principle_scores": self._metadata_repository.principle_averages(),
            "jobs": self.list_jobs(),
            "workers": self.list_workers(),
            "resource_utilisation": self._resource_pool.utilisation(),
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

    def _simulate_job(self, job_id: str, duration: int) -> None:
        job = self._jobs.get(job_id)
        if not job:
            return
        time.sleep(max(duration, 1))
        job.status = "completed"
        job.completed_at = time.time()
        utilisation_before_release = self._resource_pool.utilisation()
        metrics_payload = {
            "job_latency_seconds": (job.completed_at - job.started_at) if job.started_at and job.completed_at else 0.0,
            "compute_efficiency_ratio": self._compute_efficiency(job),
            "thread_utilisation": utilisation_before_release.get("threads", 0.0) * 100,
            "binary_channel_entropy": 0.35,
            "resource_pressure": max(utilisation_before_release.values()) if utilisation_before_release else 0.0,
            "reward_realisation": job.reward_signal,
            "bandwidth_mbps_utilised": job.allocated_resources.bandwidth_mbps if job.allocated_resources else 0,
            "discoveries": job.metadata.get("discoveries", []),
        }
        for worker_id in job.tadpole_ids:
            if worker_id in self._tadpoles:
                try:
                    self.record_status(worker_id, "completed", {"metrics": metrics_payload})
                    self.retire_worker(worker_id, "job_completed")
                except Exception:
                    continue
        if job.allocated_resources:
            self._resource_pool.release(job.allocated_resources)
        if job.worker_id and job.worker_id in self._workers:
            worker_agent = self._workers[job.worker_id]
            discovery_entries = metrics_payload.get("discoveries") or []
            if isinstance(discovery_entries, list):
                worker_agent.discovered_tools.extend([tool for tool in discovery_entries if tool not in worker_agent.discovered_tools])
            self.update_worker_metrics(
                job.worker_id,
                {
                    "quest_success_rate": metrics_payload.get("reward_realisation", 0.0),
                    "resource_efficiency": metrics_payload.get("compute_efficiency_ratio", 0.0),
                    "protocol_innovation_score": metrics_payload.get("binary_channel_entropy", 0.0),
                    "toolchain_adoption_rate": float(len(discovery_entries)) if isinstance(discovery_entries, list) else 0.0,
                },
            )
            worker_agent.state = "evaluating"
            worker_agent.active_job = None
            if worker_agent.quest_log:
                worker_agent.quest_log[-1].update(
                    {
                        "job_id": job.job_id,
                        "completed_at": job.completed_at,
                        "metrics": metrics_payload,
                    }
                )
        self._append_event(
            "job_completed",
            metadata={
                "job_id": job.job_id,
                "latency_seconds": (job.completed_at - job.started_at) if job.started_at and job.completed_at else None,
                "reward_signal": job.reward_signal,
            },
        )

    def _job_snapshot(self, job: JobRecord) -> Dict[str, Any]:
        return {
            "job_id": job.job_id,
            "objective": job.objective,
            "status": job.status,
            "reward_signal": job.reward_signal,
            "requested_resources": job.requested_resources,
            "allocated_resources": job.allocated_resources.__dict__ if job.allocated_resources else None,
            "tadpole_ids": job.tadpole_ids,
            "submitted_at": job.submitted_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "expected_duration_seconds": job.expected_duration_seconds,
            "worker_id": job.worker_id,
        }

    def _compute_efficiency(self, job: JobRecord) -> float:
        if not job.allocated_resources:
            return 0.0
        requested_compute = job.requested_resources.get("compute_units", job.allocated_resources.compute_units)
        if requested_compute == 0:
            return 1.0
        return round(job.allocated_resources.compute_units / requested_compute, 3)

    def _worker_snapshot(self, worker: WorkerAgent) -> Dict[str, Any]:
        return {
            "worker_id": worker.worker_id,
            "state": worker.state,
            "active_job": worker.active_job,
            "improvement_metrics": worker.improvement_metrics,
            "known_protocols": worker.known_protocols,
            "discovered_tools": worker.discovered_tools,
            "quests": worker.quest_log[-5:],
        }

    # ----------------------------- helpers -----------------------------
    @property
    def config(self) -> Dict[str, Any]:
        return self._cfg

    @property
    def tadpoles(self) -> Dict[str, WorkerRecord]:
        return self._tadpoles

    @property
    def workers(self) -> Dict[str, WorkerAgent]:
        return self._workers

    @property
    def event_log(self) -> List[Dict[str, Any]]:
        return self._event_log
