"""Persistence layer backed by PostgreSQL for job and worker telemetry."""
from __future__ import annotations

import contextlib
import datetime as _dt
from typing import Any, Dict, Iterable, List, Optional, Sequence

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    objective: Mapped[Optional[str]] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="queued")
    reward_signal: Mapped[float] = mapped_column(Float, default=0.0)
    requested_resources: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    spawned_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[Optional[_dt.datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[_dt.datetime]] = mapped_column(DateTime(timezone=True))

    resource_allocations: Mapped[List[ResourceAllocation]] = relationship(back_populates="job")
    metrics: Mapped[List[JobMetric]] = relationship(back_populates="job")
    histories: Mapped[List[ImprovementReport]] = relationship(back_populates="job")
    analysis_runs: Mapped[List[AnalysisRun]] = relationship(back_populates="job")


class JobMetric(Base):
    __tablename__ = "job_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.job_id", ondelete="CASCADE"))
    metric_name: Mapped[str] = mapped_column(String(128))
    metric_value: Mapped[float] = mapped_column(Float)
    observed_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))

    job: Mapped[Job] = relationship(back_populates="metrics")


class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.job_id", ondelete="CASCADE"))
    compute_units: Mapped[int] = mapped_column(Integer)
    memory_mb: Mapped[int] = mapped_column(Integer)
    bandwidth_mbps: Mapped[int] = mapped_column(Integer)
    thread_count: Mapped[int] = mapped_column(Integer)
    allocated_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))
    released_at: Mapped[Optional[_dt.datetime]] = mapped_column(DateTime(timezone=True))

    job: Mapped[Job] = relationship(back_populates="resource_allocations")


class Worker(Base):
    __tablename__ = "workers"

    worker_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    job_id: Mapped[Optional[str]] = mapped_column(ForeignKey("jobs.job_id", ondelete="SET NULL"))
    worker_type: Mapped[str] = mapped_column(String(32))
    specialization: Mapped[Optional[str]] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32))
    spawned_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))
    retired_at: Mapped[Optional[_dt.datetime]] = mapped_column(DateTime(timezone=True))
    ttl_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    expiry_at: Mapped[Optional[_dt.datetime]] = mapped_column(DateTime(timezone=True))
    code_version_id: Mapped[Optional[int]] = mapped_column(ForeignKey("code_versions.id", ondelete="SET NULL"))
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    events: Mapped[List[WorkerEvent]] = relationship(back_populates="worker")
    tadpole_instances: Mapped[List[TadpoleInstance]] = relationship(back_populates="worker")


class WorkerEvent(Base):
    __tablename__ = "worker_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[str] = mapped_column(ForeignKey("workers.worker_id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(String(64))
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    occurred_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))

    worker: Mapped[Worker] = relationship(back_populates="events")


class TadpoleInstance(Base):
    __tablename__ = "tadpole_instances"

    tadpole_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    worker_id: Mapped[str] = mapped_column(ForeignKey("workers.worker_id", ondelete="CASCADE"))
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.job_id", ondelete="CASCADE"))
    ttl_seconds: Mapped[int] = mapped_column(Integer)
    communication_protocol: Mapped[Optional[str]] = mapped_column(String(128))
    resource_allocation: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32))
    spawned_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))
    expiry_at: Mapped[Optional[_dt.datetime]] = mapped_column(DateTime(timezone=True))

    worker: Mapped[Worker] = relationship(back_populates="tadpole_instances")
    job: Mapped[Job] = relationship()
    metrics: Mapped[List[TadpoleMetric]] = relationship(back_populates="tadpole")


class TadpoleMetric(Base):
    __tablename__ = "tadpole_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tadpole_id: Mapped[str] = mapped_column(ForeignKey("tadpole_instances.tadpole_id", ondelete="CASCADE"))
    metric_name: Mapped[str] = mapped_column(String(128))
    metric_value: Mapped[float] = mapped_column(Float)
    observed_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))

    tadpole: Mapped[TadpoleInstance] = relationship(back_populates="metrics")


class SchemaChangeLog(Base):
    __tablename__ = "schema_change_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    initiated_by: Mapped[str] = mapped_column(String(128))
    entity_name: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(64))
    ddl_statement: Mapped[str] = mapped_column(Text)
    rationale: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))


class DynamicAttribute(Base):
    __tablename__ = "dynamic_attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(32))
    entity_id: Mapped[str] = mapped_column(String(128))
    attribute_key: Mapped[str] = mapped_column(String(128))
    attribute_value: Mapped[Dict[str, Any]] = mapped_column(JSON)
    weight_hint: Mapped[Optional[float]] = mapped_column(Float)
    observed_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))


class CodeVersion(Base):
    __tablename__ = "code_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    artifact_digest: Mapped[str] = mapped_column(String(128), unique=True)
    source_ref: Mapped[Optional[str]] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))

    reports: Mapped[List[CodeUpdateReport]] = relationship(back_populates="suggested_version")


class CodeUpdateReport(Base):
    __tablename__ = "code_update_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[Optional[str]] = mapped_column(ForeignKey("workers.worker_id", ondelete="SET NULL"))
    suggested_version_id: Mapped[Optional[int]] = mapped_column(ForeignKey("code_versions.id", ondelete="SET NULL"))
    summary: Mapped[str] = mapped_column(Text)
    impact: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))

    suggested_version: Mapped[Optional[CodeVersion]] = relationship(back_populates="reports")


class AnalysisRequest(Base):
    __tablename__ = "analysis_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_text: Mapped[str] = mapped_column(Text)
    requester: Mapped[Optional[str]] = mapped_column(String(128))
    context_tags: Mapped[Optional[List[str]]] = mapped_column(JSON)
    submitted_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32))

    runs: Mapped[List[AnalysisRun]] = relationship(back_populates="request")
    findings: Mapped[List[AnalysisFinding]] = relationship(back_populates="request")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("analysis_requests.id", ondelete="CASCADE"))
    worker_id: Mapped[Optional[str]] = mapped_column(ForeignKey("workers.worker_id", ondelete="SET NULL"))
    job_id: Mapped[Optional[str]] = mapped_column(ForeignKey("jobs.job_id", ondelete="SET NULL"))
    tadpole_strategy: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    started_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[_dt.datetime]] = mapped_column(DateTime(timezone=True))
    outcome_summary: Mapped[Optional[str]] = mapped_column(Text)

    request: Mapped[AnalysisRequest] = relationship(back_populates="runs")
    job: Mapped[Optional[Job]] = relationship(back_populates="analysis_runs")


class AnalysisFinding(Base):
    __tablename__ = "analysis_findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("analysis_requests.id", ondelete="CASCADE"))
    run_id: Mapped[Optional[int]] = mapped_column(ForeignKey("analysis_runs.id", ondelete="SET NULL"))
    audience: Mapped[str] = mapped_column(String(32))
    finding_type: Mapped[str] = mapped_column(String(64))
    body: Mapped[str] = mapped_column(Text)
    monetization_score: Mapped[Optional[float]] = mapped_column(Float)
    novelty_score: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))

    request: Mapped[AnalysisRequest] = relationship(back_populates="findings")
    run: Mapped[Optional[AnalysisRun]] = relationship()
    artifacts: Mapped[List[FindingArtifact]] = relationship(back_populates="finding")


class FindingArtifact(Base):
    __tablename__ = "finding_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    finding_id: Mapped[int] = mapped_column(ForeignKey("analysis_findings.id", ondelete="CASCADE"))
    artifact_uri: Mapped[str] = mapped_column(String(512))
    checksum: Mapped[Optional[str]] = mapped_column(String(128))
    content_type: Mapped[Optional[str]] = mapped_column(String(64))

    finding: Mapped[AnalysisFinding] = relationship(back_populates="artifacts")


class ImprovementReport(Base):
    __tablename__ = "improvement_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[Optional[str]] = mapped_column(ForeignKey("jobs.job_id", ondelete="SET NULL"))
    request_id: Mapped[Optional[int]] = mapped_column(ForeignKey("analysis_requests.id", ondelete="SET NULL"))
    recommended_actions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    requires_code_change: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))

    job: Mapped[Optional[Job]] = relationship(back_populates="histories")
    request: Mapped[Optional[AnalysisRequest]] = relationship()


class LearningSnapshot(Base):
    __tablename__ = "learning_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(32))
    entity_id: Mapped[str] = mapped_column(String(128))
    principle_scores: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    rubric_version: Mapped[Optional[str]] = mapped_column(String(64))
    captured_at: Mapped[_dt.datetime] = mapped_column(DateTime(timezone=True))


def _now() -> _dt.datetime:
    return _dt.datetime.now(tz=_dt.timezone.utc)


def _ts_to_datetime(timestamp: Optional[float]) -> Optional[_dt.datetime]:
    if timestamp is None:
        return None
    return _dt.datetime.fromtimestamp(timestamp, tz=_dt.timezone.utc)


class PersistenceLayer:
    """High-level helper for recording engine state transitions."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        config = config or {}
        url = config.get("database_url")
        env_key = config.get("database_url_env")
        if not url and env_key:
            import os

            url = os.getenv(env_key)
        self._enabled = bool(url)
        self._engine = None
        self._session_factory = None
        if not self._enabled:
            return
        self._engine = create_engine(url, echo=bool(config.get("echo")), future=True)
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(self._engine, expire_on_commit=False, future=True)

    @property
    def enabled(self) -> bool:
        return self._enabled

    @contextlib.contextmanager
    def _session(self):
        if not self._session_factory:
            yield None
            return
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def record_job_start(self, payload: Dict[str, Any]) -> None:
        if not self._enabled:
            return
        job_id = payload["job_id"]
        with self._session() as session:
            job = session.get(Job, job_id)
            if not job:
                job = Job(job_id=job_id, spawned_at=_now())
            job.objective = payload.get("objective")
            job.status = payload.get("status", "running")
            job.reward_signal = float(payload.get("reward_signal", 0.0))
            job.requested_resources = payload.get("requested_resources")
            job.metadata = payload.get("metadata")
            started_at_ts = payload.get("started_at")
            job.started_at = _ts_to_datetime(started_at_ts) or job.started_at or _now()
            session.add(job)

            allocation = payload.get("allocation")
            if allocation:
                record = ResourceAllocation(
                    job_id=job_id,
                    compute_units=int(allocation.get("compute_units", 0)),
                    memory_mb=int(allocation.get("memory_mb", 0)),
                    bandwidth_mbps=int(allocation.get("bandwidth_mbps", 0)),
                    thread_count=int(allocation.get("threads", 0)),
                    allocated_at=_now(),
                )
                session.add(record)

    def record_job_completion(
        self,
        job_id: str,
        status: str,
        completed_at: Optional[float],
        metrics: Optional[Dict[str, Any]] = None,
        adjustments: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> None:
        if not self._enabled:
            return
        with self._session() as session:
            job = session.get(Job, job_id)
            if job:
                job.status = status
                job.completed_at = _ts_to_datetime(completed_at) or _now()
                session.add(job)
            allocations = (
                session.query(ResourceAllocation)
                .filter(ResourceAllocation.job_id == job_id, ResourceAllocation.released_at.is_(None))
                .all()
            )
            now = _now()
            for allocation in allocations:
                allocation.released_at = now
                session.add(allocation)

            if metrics:
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        metric = JobMetric(
                            job_id=job_id,
                            metric_name=key,
                            metric_value=float(value),
                            observed_at=now,
                        )
                        session.add(metric)

            if metrics:
                snapshot = LearningSnapshot(
                    entity_type="job",
                    entity_id=job_id,
                    principle_scores=metrics,
                    rubric_version=None,
                    captured_at=now,
                )
                session.add(snapshot)

            if adjustments:
                report = ImprovementReport(
                    job_id=job_id,
                    recommended_actions={"adjustments": list(adjustments)},
                    requires_code_change=False,
                    created_at=now,
                )
                session.add(report)

    def record_worker_spawn(self, payload: Dict[str, Any]) -> None:
        if not self._enabled:
            return
        worker_id = payload["worker_id"]
        with self._session() as session:
            worker = session.get(Worker, worker_id) or Worker(worker_id=worker_id, spawned_at=_now())
            worker.worker_type = payload.get("worker_type", "tadpole")
            worker.job_id = payload.get("job_id")
            worker.specialization = payload.get("specialization")
            worker.status = payload.get("status", "initializing")
            worker.ttl_seconds = payload.get("ttl_seconds")
            worker.expiry_at = _ts_to_datetime(payload.get("expiry_at_ts"))
            worker.metadata = payload.get("metadata")
            session.add(worker)

            instance_info = payload.get("tadpole_instance")
            if instance_info:
                tadpole = TadpoleInstance(
                    tadpole_id=instance_info["tadpole_id"],
                    worker_id=worker_id,
                    job_id=payload.get("job_id", ""),
                    ttl_seconds=int(instance_info.get("ttl_seconds", 0)),
                    communication_protocol=instance_info.get("communication_protocol"),
                    resource_allocation=instance_info.get("resource_allocation"),
                    status=payload.get("status", "initializing"),
                    spawned_at=_now(),
                    expiry_at=_ts_to_datetime(payload.get("expiry_at_ts")),
                )
                session.add(tadpole)

            self._insert_worker_event(session, worker_id, "spawn", payload.get("metadata"))

    def record_worker_status(self, worker_id: str, status: str, metadata: Optional[Dict[str, Any]]) -> None:
        if not self._enabled:
            return
        with self._session() as session:
            worker = session.get(Worker, worker_id)
            if worker:
                worker.status = status
                if metadata:
                    worker.metadata = (worker.metadata or {}) | metadata
                session.add(worker)
            self._insert_worker_event(session, worker_id, "status", metadata)

    def record_worker_retire(self, worker_id: str, reason: Optional[str]) -> None:
        if not self._enabled:
            return
        payload = {"reason": reason} if reason else None
        with self._session() as session:
            worker = session.get(Worker, worker_id)
            if worker:
                worker.status = "retired"
                worker.retired_at = _now()
                session.add(worker)
            self._insert_worker_event(session, worker_id, "retire", payload)

    def record_tadpole_status(self, worker_id: str, status: str, metrics: Optional[Dict[str, Any]]) -> None:
        if not self._enabled:
            return
        with self._session() as session:
            instance = session.get(TadpoleInstance, worker_id)
            if instance:
                instance.status = status
                session.add(instance)
                if metrics:
                    now = _now()
                    for key, value in metrics.items():
                        if isinstance(value, (int, float)):
                            record = TadpoleMetric(
                                tadpole_id=instance.tadpole_id,
                                metric_name=key,
                                metric_value=float(value),
                                observed_at=now,
                            )
                            session.add(record)

    def record_dynamic_attribute(
        self,
        entity_type: str,
        entity_id: str,
        attribute_key: str,
        attribute_value: Dict[str, Any],
        weight_hint: Optional[float] = None,
    ) -> None:
        if not self._enabled:
            return
        with self._session() as session:
            entry = DynamicAttribute(
                entity_type=entity_type,
                entity_id=entity_id,
                attribute_key=attribute_key,
                attribute_value=attribute_value,
                weight_hint=weight_hint,
                observed_at=_now(),
            )
            session.add(entry)

    def register_schema_change(self, entity_name: str, ddl: str, rationale: str, initiator: str) -> None:
        if not self._enabled:
            return
        with self._session() as session:
            record = SchemaChangeLog(
                initiated_by=initiator,
                entity_name=entity_name,
                action="proposed",
                ddl_statement=ddl,
                rationale=rationale,
                created_at=_now(),
            )
            session.add(record)

    def register_analysis_request(
        self,
        question_text: str,
        requester: Optional[str],
        context_tags: Optional[List[str]],
    ) -> Optional[int]:
        if not self._enabled:
            return None
        with self._session() as session:
            request = AnalysisRequest(
                question_text=question_text,
                requester=requester,
                context_tags=context_tags,
                submitted_at=_now(),
                status="queued",
            )
            session.add(request)
            session.flush()
            return request.id

    def record_analysis_run(
        self,
        request_id: int,
        worker_id: Optional[str],
        job_id: Optional[str],
        tadpole_strategy: Optional[Dict[str, Any]],
        outcome_summary: Optional[str],
    ) -> Optional[int]:
        if not self._enabled:
            return None
        with self._session() as session:
            run = AnalysisRun(
                request_id=request_id,
                worker_id=worker_id,
                job_id=job_id,
                tadpole_strategy=tadpole_strategy,
                started_at=_now(),
                completed_at=_now(),
                outcome_summary=outcome_summary,
            )
            session.add(run)
            session.flush()
            request = session.get(AnalysisRequest, request_id)
            if request:
                request.status = "completed"
                session.add(request)
            return run.id

    def record_analysis_finding(
        self,
        request_id: int,
        run_id: Optional[int],
        audience: str,
        finding_type: str,
        body: str,
        monetization_score: Optional[float],
        novelty_score: Optional[float],
        artifacts: Optional[Iterable[Dict[str, Any]]] = None,
    ) -> None:
        if not self._enabled:
            return
        with self._session() as session:
            finding = AnalysisFinding(
                request_id=request_id,
                run_id=run_id,
                audience=audience,
                finding_type=finding_type,
                body=body,
                monetization_score=monetization_score,
                novelty_score=novelty_score,
                created_at=_now(),
            )
            session.add(finding)
            session.flush()
            if artifacts:
                for artifact in artifacts:
                    record = FindingArtifact(
                        finding_id=finding.id,
                        artifact_uri=artifact.get("artifact_uri", ""),
                        checksum=artifact.get("checksum"),
                        content_type=artifact.get("content_type"),
                    )
                    session.add(record)

    def record_improvement_report(
        self,
        job_id: Optional[str],
        request_id: Optional[int],
        recommended_actions: Dict[str, Any],
        requires_code_change: bool,
    ) -> None:
        if not self._enabled:
            return
        with self._session() as session:
            report = ImprovementReport(
                job_id=job_id,
                request_id=request_id,
                recommended_actions=recommended_actions,
                requires_code_change=requires_code_change,
                created_at=_now(),
            )
            session.add(report)

    def record_learning_snapshot(
        self,
        entity_type: str,
        entity_id: str,
        principle_scores: Optional[Dict[str, Any]],
        rubric_version: Optional[str],
    ) -> None:
        if not self._enabled:
            return
        snapshot = LearningSnapshot(
            entity_type=entity_type,
            entity_id=entity_id,
            principle_scores=principle_scores,
            rubric_version=rubric_version,
            captured_at=_now(),
        )
        with self._session() as session:
            session.add(snapshot)

    def _insert_worker_event(self, session, worker_id: str, event_type: str, payload: Optional[Dict[str, Any]]) -> None:
        event = WorkerEvent(
            worker_id=worker_id,
            event_type=event_type,
            payload=payload,
            occurred_at=_now(),
        )
        session.add(event)
