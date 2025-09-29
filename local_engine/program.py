"""Command handler that maps CustomGPT instructions to engine actions."""
from __future__ import annotations

from typing import Any, Dict

from .engine import AdaptiveAgentEngine


def dispatch_command(engine: AdaptiveAgentEngine, command: Dict[str, Any]) -> Dict[str, Any]:
    """Route a control-plane command to the engine.

    Expected payload structure::
        {
            "action": "spawn" | "retire" | "status" | "heartbeat",
            "args": {...}
        }
    """

    action = command.get("action")
    args = command.get("args", {})

    if action == "spawn":
        record = engine.spawn_worker(args)
        return {"status": "ok", "worker_id": record.worker_id, "state": record.status}
    if action == "retire":
        worker_id = args.get("worker_id")
        if not worker_id:
            raise ValueError("retire action requires args.worker_id")
        record = engine.retire_worker(worker_id, reason=args.get("reason"))
        return {"status": "ok", "worker_id": record.worker_id, "state": record.status}
    if action == "status":
        worker_id = args.get("worker_id")
        if not worker_id:
            raise ValueError("status action requires args.worker_id")
        record = engine.record_status(worker_id, args.get("state", "unknown"), args.get("metadata"))
        return {"status": "ok", "worker_id": record.worker_id, "state": record.status}
    if action == "heartbeat":
        return {"status": "ok", "heartbeat": engine.heartbeat()}
    if action == "optimize":
        cycle = args.get("cycle")
        if not cycle:
            raise ValueError("optimize action requires args.cycle")
        entry = engine.trigger_cycle(cycle, initiator=args.get("initiator"), metadata=args.get("metadata"))
        return {"status": "ok", "cycle": entry}
    if action == "revise_egg":
        revision = engine.revise_egg()
        return {"status": "ok", "revision": revision}
    if action == "assign_job":
        job = engine.submit_job(args)
        return {"status": "ok", "job": engine.get_job_snapshot(job.job_id)}
    if action == "job_status":
        job_id = args.get("job_id")
        if not job_id:
            raise ValueError("job_status action requires args.job_id")
        return {"status": "ok", "job": engine.get_job_snapshot(job_id)}
    if action == "list_jobs":
        return {"status": "ok", "jobs": engine.list_jobs()}
    if action == "assign_worker":
        worker = engine.assign_worker(args)
        return {"status": "ok", "worker": engine.get_worker_snapshot(worker.worker_id)}
    if action == "worker_status":
        worker_id = args.get("worker_id")
        if not worker_id:
            raise ValueError("worker_status action requires args.worker_id")
        return {"status": "ok", "worker": engine.get_worker_snapshot(worker_id)}
    if action == "list_workers":
        return {"status": "ok", "workers": engine.list_workers()}

    raise ValueError(f"Unsupported action: {action}")
