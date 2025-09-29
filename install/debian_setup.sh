#!/usr/bin/env bash
# Debian bootstrap script for evolutionAi
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"
PYTHON_BIN="python3"
PIP_BIN=""

log() {
  printf "[setup] %s\n" "$1"
}

ensure_prereqs() {
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    log "python3 is required. Install with: sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip"
    exit 1
  fi
}

create_venv() {
  if [ ! -d "$VENV_DIR" ]; then
    log "Creating virtual environment at $VENV_DIR"
    "$PYTHON_BIN" -m venv "$VENV_DIR"
  else
    log "Virtual environment already exists at $VENV_DIR"
  fi
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
  PIP_BIN="$(command -v pip)"
}

upgrade_tooling() {
  log "Upgrading pip/setuptools/wheel"
  "$PIP_BIN" install --upgrade pip setuptools wheel
}

install_requirements() {
  log "Installing Python requirements"
  "$PIP_BIN" install -r "$REPO_ROOT/requirements.txt"
}

run_sanity_checks() {
  log "Running sanity checks"
  "$PYTHON_BIN" -m compileall "$REPO_ROOT/local_engine"
  uvicorn --version >/dev/null 2>&1 || {
    log "Uvicorn not found after installation"
    exit 1
  }
  log "Sanity checks passed"
}

ensure_prereqs
create_venv
upgrade_tooling
install_requirements
run_sanity_checks

log "Setup complete. Activate the venv with: source $VENV_DIR/bin/activate"
