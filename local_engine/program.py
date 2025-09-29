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

    raise ValueError(f"Unsupported action: {action}")
