# Installation Guide — Linux

Tested on Ubuntu 22.04 LTS. Adapt as needed for other distributions.

## Prerequisites
- Python 3.10+
- `pip` and optional virtual environment tool (`venv` or `pipenv`)
- `ngrok` account and agent (optional, for external access)

## Setup Steps
1. **Clone the repository (once repo is initialised):**
   ```bash
   git clone https://github.com/<org>/evolveAi.git
   cd evolveAi
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt  # generate this as dependencies are formalised
   pip install pyyaml
   ```
4. **Export required environment variables:**
   ```bash
   export ADAPTIVE_CAPABILITY_SECRET="<32+ character secret>"
   export NGROK_AUTHTOKEN="<token>"      # optional
   export NGROK_WEBHOOK_SECRET="<secret>" # optional
   ```
5. **Run the local engine:**
   ```bash
   python -m local_engine.main --host 127.0.0.1 --port 8080
   ```
6. **(Optional) Expose the service via ngrok:**
   ```bash
   ngrok http 8080 --hostname=<reserved-subdomain>.ngrok.app
   ```

## Verification
- `curl http://127.0.0.1:8080/healthz`
- `curl http://127.0.0.1:8080/metrics`
- `curl -X POST http://127.0.0.1:8080/commands \
    -H "Content-Type: application/json" \
    -H "X-Timestamp: $(date +%s)" \
    -H "X-Capability-Token: <generated token>" \
    -d '{"action":"heartbeat"}'`

Consult `local_engine/README.md` for command payload examples and token generation snippets.
