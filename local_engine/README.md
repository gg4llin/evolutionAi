# AdaptiveAgent Local Engine

This package provides a minimal HTTP control-plane that mirrors the connectivity and orchestration documents supplied to the AdaptiveAgent Custom GPT. It exposes:

- `GET /healthz` – returns a heartbeat payload derived from `custom_gpt/connectivity_config.yaml`.
- `GET /metrics` – lists active workers and recent telemetry.
- `POST /commands` – accepts JSON commands (`spawn`, `retire`, `status`, `heartbeat`, `optimize`, `revise_egg`, `assign_job`, `job_status`, `list_jobs`, `assign_worker`, `worker_status`, `list_workers`) and mutates in-memory state.
- Rubric-aware composite scoring built from `dynamic_rubric_system.txt` keeps every worker aligned with the active principles.
- HMAC-backed capability tokens enforce the zero-trust contract described in `security_authentication_framework.txt`.
- `revise_egg` synthesizes repository metadata via `tadpole_metadata_judgement_system.txt` before new tadpoles spawn.
- `assign_job`, `job_status`, and `list_jobs` drive the task orchestration workflow described in `task_orchestration_system.txt`.
- `assign_worker`, `worker_status`, and `list_workers` create quest workers, track improvements, and manage tool discovery as defined in `worker_orchestration_system.txt`.

## Quick Start

1. Copy the sample environment file and populate secrets (keep `.env` out of version control):
   ```bash
   cp .env.example .env
   # edit .env
   export $(grep -v '^#' .env | xargs)
   ```
2. Start the ASGI server with Uvicorn (recommended):
   ```bash
   uvicorn local_engine.asgi:app --host 127.0.0.1 --port 8080
   ```
   The legacy fallback remains available via `python -m local_engine.main --host 127.0.0.1 --port 8080`.

To expose the API externally, follow the ngrok guidance in `custom_gpt/connectivity_config.yaml`. Ensure `NGROK_AUTHTOKEN`, `NGROK_PUBLIC_URL`, and `NGROK_WEBHOOK_SECRET` live in the environment or your secrets manager.

## Command Payloads

```json
{"action": "spawn", "args": {"trigger": "stagnation_detected"}}
```

```json
{
  "action": "status",
  "args": {
    "worker_id": "<uuid>",
    "state": "active",
    "metadata": {
      "metrics": {
        "execution_time": 0.7,
        "resource_utilization": 0.8,
        "task_completion_rate": 0.95
      }
    }
  }
}
```

```json
{"action": "optimize", "args": {"cycle": "micro_cycle", "initiator": "adaptive_agent_gpt"}}
```

```json
{"action": "revise_egg"}
```

```json
{"action": "retire", "args": {"worker_id": "<uuid>", "reason": "scale_down"}}
```

```json
{
  "action": "assign_job",
  "args": {
    "job_id": "job-001",
    "objective": "process_dataset",
    "tadpole_count": 3,
    "requested_resources": {
      "compute_units": 12,
      "memory_mb": 2048,
      "bandwidth_mbps": 600
    },
    "expected_duration_seconds": 30,
    "reward_signal": 1.25
  }
}
```

```json
{"action": "assign_worker", "args": {"worker_id": "worker-alpha", "state": "scaffolding"}}
```

```json
{"action": "worker_status", "args": {"worker_id": "worker-alpha"}}
```

Follow-on commands:
- `{"action": "job_status", "args": {"job_id": "job-001"}}`
- `{"action": "list_jobs"}`
- `{"action": "worker_status", "args": {"worker_id": "worker-alpha"}}`
- `{"action": "list_workers"}`

All `POST /commands` requests must include an `X-Timestamp` header (Unix time seconds) and an `X-Capability-Token` header. Generate tokens with:

```python
from local_engine.capabilities import CapabilityValidator

secret = "<same value as ADAPTIVE_CAPABILITY_SECRET>"
timestamp = 1700000000.0
token = CapabilityValidator.build_token(secret, timestamp, action="spawn")
```

Outputs include the worker state plus any generated metadata. Extend `dispatch_command` in `local_engine/program.py` to support additional actions that your Custom GPT recommends.
