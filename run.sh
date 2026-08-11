#!/usr/bin/env bash
# =============================================================================
# ShopEasy — Application Runner
# Lab 1: Amazon EBS — Persistent Block Storage
# =============================================================================
# Usage:
#   bash run.sh          — start Flask dev server on port 5000
#   bash run.sh prod     — start with Gunicorn (production)
#   bash run.sh stop     — kill running server
#
# First time? Run these in order:
#   bash setup.sh        — install system deps + Python venv
#   bash init.sh         — create database and seed products
#   bash run.sh          — start the application
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"
MODE="${1:-dev}"

# ── Venv: create only if it doesn't already exist ────────────────────────────
if [ ! -d "${VENV_DIR}" ]; then
  echo "▶ Virtual environment not found — creating it now..."
  if ! command -v python3 &>/dev/null; then
    echo "  ERROR: python3 not found. Run: bash setup.sh"
    exit 1
  fi
  python3 -m venv "${VENV_DIR}"
  source "${VENV_DIR}/bin/activate"
  echo "▶ Installing Python dependencies..."
  pip install --quiet --upgrade pip
  pip install --quiet -r "${SCRIPT_DIR}/requirements.txt"
  echo "  Done."
else
  # venv already exists — activate and go
  source "${VENV_DIR}/bin/activate"
fi

cd "${SCRIPT_DIR}"

# ── Start / stop ──────────────────────────────────────────────────────────────
case "${MODE}" in
  dev|"")
    echo "Starting ShopEasy (Flask dev server) on http://0.0.0.0:5000"
    python3 app.py
    ;;
  prod)
    echo "Starting ShopEasy (Gunicorn) on http://0.0.0.0:5000"
    gunicorn \
      --bind 0.0.0.0:5000 \
      --workers 2 \
      --timeout 60 \
      --access-logfile - \
      "app:create_app()"
    ;;
  stop)
    pkill -f "python3 app.py" 2>/dev/null && echo "Flask stopped." || true
    pkill -f "gunicorn" 2>/dev/null && echo "Gunicorn stopped." || true
    ;;
  *)
    echo "Unknown mode: ${MODE}. Use dev, prod, or stop."
    exit 1
    ;;
esac

