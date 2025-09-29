# AdaptiveAgent Local Engine

This package provides a minimal HTTP control-plane that mirrors the connectivity and orchestration documents supplied to the AdaptiveAgent Custom GPT. It exposes:

- `GET /healthz` – returns a heartbeat payload derived from `custom_gpt/connectivity_config.yaml`.
- `GET /metrics` – lists active workers and recent telemetry.
- `POST /commands` – accepts JSON commands (`spawn`, `retire`, `status`, `heartbeat`, `optimize`, `revise_egg`) and mutates in-memory worker state.
- Rubric-aware composite scoring built from `dynamic_rubric_system.txt` keeps every worker aligned with the active principles.
- HMAC-backed capability tokens enforce the zero-trust contract described in `security_authentication_framework.txt`.
- `revise_egg` synthesizes repository metadata via `tadpole_metadata_judgement_system.txt` before new tadpoles spawn.

## Quick Start

```bash
python -m local_engine.main --host 127.0.0.1 --port 8080
```

Before starting the server, export a shared secret for capability tokens:

```bash
export ADAPTIVE_CAPABILITY_SECRET="<32+ character secret>"
```

To expose the API externally, follow the ngrok guidance in `custom_gpt/connectivity_config.yaml`. Ensure `NGROK_AUTHTOKEN`, `NGROK_PUBLIC_URL`, and `NGROK_WEBHOOK_SECRET` are exported before starting the tunnel.

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

All `POST /commands` requests must include an `X-Timestamp` header (Unix time seconds) and an `X-Capability-Token` header. Generate tokens with:

```python
from local_engine.capabilities import CapabilityValidator

secret = "<same value as ADAPTIVE_CAPABILITY_SECRET>"
timestamp = 1700000000.0
token = CapabilityValidator.build_token(secret, timestamp, action="spawn")
```

Outputs include the worker state plus any generated metadata. Extend `dispatch_command` in `local_engine/program.py` to support additional actions that your Custom GPT recommends.
