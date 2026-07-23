# shellcheck shell=bash
# Usage: source scripts/env.sh
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export VIPS_PREFIX="${ROOT}/.local/vips"
export PATH="${VIPS_PREFIX}/bin:${ROOT}/.venv/bin:${PATH}"
export LD_LIBRARY_PATH="${VIPS_PREFIX}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PKG_CONFIG_PATH="${VIPS_PREFIX}/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
