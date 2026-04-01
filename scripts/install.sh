#!/bin/bash
# Install aio-search CLI and download ontology file into CLAUDE_PLUGIN_DATA.
# Runs at SessionStart; skips if already up to date.
set -e

VENV="${CLAUDE_PLUGIN_DATA}/.venv"
MARKER="${CLAUDE_PLUGIN_DATA}/pyproject.toml.installed"
OWL="${CLAUDE_PLUGIN_DATA}/aio-full.owl"

# --- Install Python deps if pyproject.toml changed or venv missing ---
if ! diff -q "${CLAUDE_PLUGIN_ROOT}/pyproject.toml" "${MARKER}" >/dev/null 2>&1 || \
   [ ! -f "${VENV}/bin/aio-search" ]; then
  echo "[aio-search] Installing CLI dependencies..." >&2
  UV_PROJECT_ENVIRONMENT="${VENV}" uv sync --project "${CLAUDE_PLUGIN_ROOT}" >&2
  cp "${CLAUDE_PLUGIN_ROOT}/pyproject.toml" "${MARKER}"
  echo "[aio-search] CLI installed." >&2
fi

# --- Symlink binary to ~/.local/bin so it's on PATH from any directory ---
LOCAL_BIN="${HOME}/.local/bin"
mkdir -p "${LOCAL_BIN}"
ln -sf "${VENV}/bin/aio-search" "${LOCAL_BIN}/aio-search"

# --- Download ontology file if missing ---
if [ ! -f "${OWL}" ]; then
  echo "[aio-search] Downloading aio-full.owl (~5 MB)..." >&2
  curl -fsSL \
    "https://raw.githubusercontent.com/berkeleybop/artificial-intelligence-ontology/main/aio-full.owl" \
    -o "${OWL}" >&2
  echo "[aio-search] Ontology downloaded." >&2
fi
