#!/usr/bin/env bash
# Install libvips (conda-forge via micromamba) + uv venv with pyvips.
# Usage: bash scripts/setup_vips_env.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PREFIX="${ROOT}/.local/vips"
MAMBA_ROOT="${ROOT}/.mamba"
MM="${MAMBA_ROOT}/micromamba"

if [[ ! -x "$PREFIX/bin/vips" ]]; then
  echo "Installing libvips into ${PREFIX} ..."
  mkdir -p "$(dirname "$MM")"
  if [[ ! -x "$MM" ]]; then
    curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj -C "${MAMBA_ROOT}" bin/micromamba
    MM="${MAMBA_ROOT}/bin/micromamba"
  fi
  export MAMBA_ROOT_PREFIX="${MAMBA_ROOT}"
  "$MM" create -y -p "$PREFIX" -c conda-forge "libvips>=8.15" pkg-config
fi

export PKG_CONFIG_PATH="${PREFIX}/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
export LD_LIBRARY_PATH="${PREFIX}/lib:${LD_LIBRARY_PATH:-}"

cd "$ROOT"
if [[ ! -d .venv ]]; then
  uv venv .venv
fi
uv pip install -e . 2>/dev/null || uv pip install pyvips
echo "vips: $("$PREFIX/bin/vips" --version)"
LD_LIBRARY_PATH="${PREFIX}/lib" .venv/bin/python -c "import pyvips; print('pyvips', pyvips.__version__)"
echo "Done. Run: source scripts/env.sh && uv run python scripts/optimize_images_vips.py"
