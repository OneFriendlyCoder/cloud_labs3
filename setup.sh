#!/usr/bin/env bash
# =============================================================================
# ShopEasy Lab Setup Script
# Lab 1: Amazon EBS — Persistent Block Storage
# =============================================================================
# Usage: bash setup.sh
# Run once on a fresh EC2 instance. Already-installed packages are skipped.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"
DATA_DIR="${SCRIPT_DIR}/data"

echo "======================================================"
echo "  ShopEasy Setup — Lab 1: Amazon EBS"
echo "======================================================"

# ── Helper: check if a deb package is installed ────────────────────────────
deb_installed() { dpkg -s "$1" &>/dev/null 2>&1; }

# ── Helper: check if an rpm package is installed ───────────────────────────
rpm_installed() { rpm -q "$1" &>/dev/null 2>&1; }

# ── 1. System packages ────────────────────────────────────────────────────────
echo ""
echo "▶ Checking system packages..."

if command -v apt-get &>/dev/null; then
    # ── Debian / Ubuntu / Amazon Linux 2023 (apt) ──────────────────────────
    NEED_UPDATE=false
    PKGS_TO_INSTALL=()

    for pkg in python3 python3-pip python3-venv; do
        if deb_installed "${pkg}"; then
            echo "  [skip] ${pkg} already installed"
        else
            echo "  [need] ${pkg}"
            PKGS_TO_INSTALL+=("${pkg}")
            NEED_UPDATE=true
        fi
    done

    # Also check the version-specific python3.x-venv package
    if command -v python3 &>/dev/null; then
        PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PY_VENV_PKG="python${PY_VER}-venv"
        if ! deb_installed "${PY_VENV_PKG}"; then
            if apt-cache show "${PY_VENV_PKG}" &>/dev/null; then
                echo "  [need] ${PY_VENV_PKG}"
                PKGS_TO_INSTALL+=("${PY_VENV_PKG}")
                NEED_UPDATE=true
            fi
        else
            echo "  [skip] ${PY_VENV_PKG} already installed"
        fi
    fi

    if [ "${#PKGS_TO_INSTALL[@]}" -gt 0 ]; then
        echo ""
        echo "  Installing: ${PKGS_TO_INSTALL[*]}"
        sudo apt-get update -q
        sudo apt-get install -y "${PKGS_TO_INSTALL[@]}"
    else
        echo "  All required apt packages are already installed."
    fi

elif command -v dnf &>/dev/null; then
    # ── Fedora / Amazon Linux 2023 (dnf) ──────────────────────────────────
    for pkg in python3 python3-pip; do
        if rpm_installed "${pkg}"; then
            echo "  [skip] ${pkg} already installed"
        else
            echo "  [need] ${pkg} — installing..."
            sudo dnf install -y "${pkg}"
        fi
    done

elif command -v yum &>/dev/null; then
    # ── Amazon Linux 2 / CentOS (yum) ─────────────────────────────────────
    for pkg in python3 python3-pip; do
        if rpm_installed "${pkg}"; then
            echo "  [skip] ${pkg} already installed"
        else
            echo "  [need] ${pkg} — installing..."
            sudo yum install -y "${pkg}"
        fi
    done

else
    echo "  ERROR: Unsupported package manager. Install python3, python3-pip, python3-venv manually."
    exit 1
fi

# ── 2. Verify Python ──────────────────────────────────────────────────────────
echo ""
echo "▶ Verifying Python..."
if ! command -v python3 &>/dev/null; then
    echo "  ERROR: python3 not found after install. Aborting."
    exit 1
fi
echo "  $(python3 --version)"

if ! python3 -m ensurepip --help &>/dev/null; then
    echo "  ERROR: ensurepip unavailable — cannot create virtual environments."
    echo "  Install the appropriate python3-venv package and retry."
    exit 1
fi

# ── 3. Virtual environment ────────────────────────────────────────────────────
echo ""
echo "▶ Virtual environment..."
if [ -d "${VENV_DIR}" ]; then
    echo "  [skip] venv already exists at ${VENV_DIR}"
else
    echo "  Creating venv at ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
    echo "  Done."
fi

source "${VENV_DIR}/bin/activate"

# ── 4. Python dependencies ────────────────────────────────────────────────────
echo ""
echo "▶ Installing Python dependencies..."
python -m pip install --quiet --upgrade pip
pip install --quiet -r "${SCRIPT_DIR}/requirements.txt"
echo "  All dependencies installed."

# ── 5. Data directory ─────────────────────────────────────────────────────────
echo ""
echo "▶ Data directory..."
if [ -d "${DATA_DIR}" ]; then
    echo "  [skip] ${DATA_DIR} already exists"
else
    mkdir -p "${DATA_DIR}"
    echo "  Created: ${DATA_DIR}"
fi

# ── 6. .env file ──────────────────────────────────────────────────────────────
echo ""
echo "▶ Environment config (.env)..."
if [ -f "${SCRIPT_DIR}/.env" ]; then
    echo "  [skip] .env already exists"
else
    echo "  Creating .env..."
    cat > "${SCRIPT_DIR}/.env" <<EOF
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
EOF
    echo "  Done."
fi

# ── Done ───────────────────────────────────────────────────────────────────────
echo ""
echo "======================================================"
echo "  Setup complete!"
echo "======================================================"
echo ""
echo "  Next steps:"
echo "    bash init.sh    — create database + seed products"
echo "    bash run.sh     — start the application"
echo ""