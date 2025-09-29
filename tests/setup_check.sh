#!/usr/bin/env bash
# Basic post-installation verification for evolutionAi
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "[check] virtual environment not found at $VENV_DIR" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

python -m compileall "$REPO_ROOT/local_engine" >/dev/null
uvicorn --version >/dev/null 2>&1

# smoke test: ensure assign_job payload is accepted (dry run)
python <<'PYCODE'
from local_engine.engine import AdaptiveAgentEngine
from local_engine.config_loader import load_connectivity_config

cfg = load_connectivity_config()
engine = AdaptiveAgentEngine(cfg)
job = engine.submit_job({
    "job_id": "setup-check",
    "objective": "sanity",
    "tadpole_count": 1,
    "requested_resources": {"compute_units": 2, "memory_mb": 256, "bandwidth_mbps": 100},
    "expected_duration_seconds": 1,
    "reward_signal": 0.1,
})
print("job", job.job_id, "queued")
PYCODE

echo "[check] setup verification succeeded"
