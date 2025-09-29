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
   pip install -r requirements.txt
   ```
4. **Set environment variables securely (PowerShell):**
   ```powershell
   Copy-Item .env.example .env
   notepad .env
   Get-Content .env | ForEach-Object {
     if ($_ -and $_ -notlike '#*') {
       $pair = $_.Split('=')
       $name = $pair[0]
       $value = $pair[1]
       Set-Item -Path Env:$name -Value $value
     }
   }
   ```
5. **Run the local engine with Uvicorn:**
   ```powershell
   uvicorn local_engine.asgi:app --host 127.0.0.1 --port 8080
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
