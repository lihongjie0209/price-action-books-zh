#!/usr/bin/env python3
"""Optimize chart PNGs: grayscale/palette + oxipng."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OXIPNG = ROOT / "scripts" / "oxipng"
if not OXIPNG.exists():
    which = shutil.which("oxipng")
    OXIPNG = Path(which) if which else None


def is_nearly_gray(im: Image.Image, sample: int = 2500, thr: float = 10.0) -> bool:
    rgb = im.convert("RGB")
    w, h = rgb.size
    step = max(1, (w * h) // sample)
    data = list(rgb.getdata())
    diffs = []
    for i in range(0, len(data), step):
        r, g, b = data[i]
        diffs.append((abs(r - g) + abs(g - b) + abs(r - b)) / 3.0)
    return (sum(diffs) / max(1, len(diffs))) < thr


def optimize_one(path: Path) -> tuple[int, int]:
    before = path.stat().st_size
    im = Image.open(path)
    im.load()

    if im.mode in ("RGBA", "LA"):
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im.convert("RGBA"))
        im = bg.convert("RGB")
    elif im.mode == "P":
        im = im.convert("RGB")
    elif im.mode not in ("RGB", "L"):
        im = im.convert("RGB")

    if im.mode == "L" or is_nearly_gray(im):
        out = im.convert("L")
    else:
        out = im.convert("RGB").quantize(colors=64, method=Image.Quantize.MEDIANCUT)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "out.png"
        out.save(tmp, format="PNG", optimize=True, compress_level=9)
        if OXIPNG and Path(OXIPNG).exists():
            subprocess.run(
                [str(OXIPNG), "-o", "4", "--strip", "safe", str(tmp)],
                check=False,
                capture_output=True,
            )
        after = tmp.stat().st_size
        if after < before:
            shutil.copy2(tmp, path)
            return before, after
        return before, before


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="*", type=Path)
    args = ap.parse_args()
    dirs = args.dirs or list((ROOT / "books").glob("*/assets/figures"))
    files: list[Path] = []
    for d in dirs:
        if d.is_file() and d.suffix.lower() == ".png":
            files.append(d)
        elif d.is_dir():
            figs = sorted(d.glob("fig_*.png"))
            files.extend(figs if figs else sorted(d.glob("*.png")))
    if not files:
        print("No PNG files", file=sys.stderr)
        return 1
    tb = ta = 0
    for p in files:
        b, a = optimize_one(p)
        tb += b
        ta += a
        print(f"{p.name}: {b/1024:.0f}KB -> {a/1024:.0f}KB ({100*(1-a/b):.1f}%)")
    print(f"TOTAL: {tb/1e6:.2f}MB -> {ta/1e6:.2f}MB ({100*(1-ta/tb):.1f}% reduction), n={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
