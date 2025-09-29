# Installation Guide — Windows 11

## Prerequisites
- Windows 11 (22H2 or later)
- Python 3.10+ from the Microsoft Store or python.org
- PowerShell 7+
- (Optional) Windows Subsystem for Linux (WSL2) for parity with Linux commands
- ngrok agent (optional)

## Setup Steps (PowerShell)
1. **Clone the repository (once GitHub is initialised):**
   ```powershell
   git clone https://github.com/<org>/evolveAi.git
   Set-Location evolveAi
   ```
2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. **Install dependencies:**
   ```powershell
   pip install pyyaml
   ```
4. **Set environment variables:**
   ```powershell
   $env:ADAPTIVE_CAPABILITY_SECRET = "<32+ character secret>"
   $env:NGROK_AUTHTOKEN = "<token>"          # optional
   $env:NGROK_WEBHOOK_SECRET = "<secret>"    # optional
   ```
5. **Run the local engine:**
   ```powershell
   python -m local_engine.main --host 127.0.0.1 --port 8080
   ```
6. **(Optional) ngrok tunnel:**
   ```powershell
   ngrok http 8080 --hostname <reserved-subdomain>.ngrok.app
   ```

## Verification
```powershell
Invoke-RestMethod http://127.0.0.1:8080/healthz
Invoke-RestMethod http://127.0.0.1:8080/metrics
```

To generate capability tokens, open Python in PowerShell and use the helper in `local_engine.capabilities`.
