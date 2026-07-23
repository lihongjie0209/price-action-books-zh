#!/usr/bin/env python3
"""Optimize chart figures with pyvips (libvips).

Requires system/libvips (see scripts/setup_vips_env.sh) and:
  uv sync   # or: uv pip install pyvips

Examples:
  uv run python scripts/optimize_images_vips.py
  uv run python scripts/optimize_images_vips.py books/trading-price-action-trends/assets/figures
  uv run python scripts/optimize_images_vips.py --format webp --quality 82
  uv run python scripts/optimize_images_vips.py --max-width 1600
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

# Prefer project-bundled libvips if present (micromamba/conda prefix)
_ROOT = Path(__file__).resolve().parents[1]
_VIPS_PREFIX = _ROOT / ".local" / "vips"
if _VIPS_PREFIX.is_dir():
    lib = str(_VIPS_PREFIX / "lib")
    os.environ["LD_LIBRARY_PATH"] = lib + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
    pc = str(_VIPS_PREFIX / "lib" / "pkgconfig")
    os.environ["PKG_CONFIG_PATH"] = pc + os.pathsep + os.environ.get("PKG_CONFIG_PATH", "")
    # Preload so pyvips/cffi finds libvips even if process started without LD_LIBRARY_PATH
    import ctypes

    for name in ("libvips.so.42", "libvips.so"):
        so = _VIPS_PREFIX / "lib" / name
        if so.exists():
            ctypes.CDLL(str(so), mode=ctypes.RTLD_GLOBAL)
            break

import pyvips  # noqa: E402

def collect_pngs(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        if p.is_file() and p.suffix.lower() == ".png":
            files.append(p)
        elif p.is_dir():
            figs = sorted(p.glob("fig_*.png"))
            files.extend(figs if figs else sorted(p.glob("*.png")))
    return files


def nearly_grayscale(image: pyvips.Image, sample_size: int = 64) -> bool:
    """Heuristic: downsample and check RGB channel similarity."""
    if image.bands < 3:
        return True
    # work on srgb without alpha for stats
    im = image
    if im.hasalpha():
        im = im.flatten(background=[255, 255, 255])
    if im.bands > 3:
        im = im.extract_band(0, n=3)
    # thumbnail for speed
    thumb = im.thumbnail_image(sample_size, height=sample_size, size="down")
    # avg |R-G| + |G-B|
    bands = [thumb.extract_band(i) for i in range(3)]
    d01 = (bands[0] - bands[1]).abs().avg()
    d12 = (bands[1] - bands[2]).abs().avg()
    d02 = (bands[0] - bands[2]).abs().avg()
    return (d01 + d12 + d02) / 3.0 < 6.0


def optimize_one(
    path: Path,
    *,
    fmt: str,
    quality: int,
    compression: int,
    max_width: int | None,
    force_grey: bool,
    keep_color: bool,
) -> tuple[int, int, str]:
    before = path.stat().st_size
    # copy_memory so we can pngsave multiple strategies without sequential re-read errors
    image = pyvips.Image.new_from_file(str(path)).copy_memory()

    if image.hasalpha():
        image = image.flatten(background=[255, 255, 255])

    if max_width and image.width > max_width:
        scale = max_width / float(image.width)
        image = image.resize(scale, kernel="lanczos3")

    to_grey = force_grey or (not keep_color and nearly_grayscale(image))
    if to_grey and image.bands >= 3:
        try:
            image = image.colourspace("b-w")
        except Exception:
            image = image.extract_band(1)

    # materialize pipeline once more after transforms
    image = image.copy_memory()

    with tempfile.TemporaryDirectory() as td:
        candidates: list[Path] = []

        if fmt == "webp":
            webp_path = Path(td) / "out.webp"
            image.webpsave(
                str(webp_path),
                Q=quality,
                strip=True,
                effort=5,
                min_size=True,
            )
            candidates.append(webp_path)
        else:
            # Strategy A: palette PNG (great for charts)
            p_pal = Path(td) / "palette.png"
            try:
                image.pngsave(
                    str(p_pal),
                    compression=compression,
                    strip=True,
                    interlace=False,
                    palette=True,
                    Q=min(100, max(50, quality)),
                )
                candidates.append(p_pal)
            except Exception:
                pass
            # Strategy B: plain greyscale/RGB PNG
            p_plain = Path(td) / "plain.png"
            image.pngsave(
                str(p_plain),
                compression=compression,
                strip=True,
                interlace=False,
            )
            candidates.append(p_plain)

        if not candidates:
            return before, before, str(path)

        best = min(candidates, key=lambda p: p.stat().st_size)
        after = best.stat().st_size
        if after < before:
            if fmt == "webp":
                dest = path.with_suffix(".webp")
                shutil.copy2(best, dest)
                return before, after, str(dest)
            shutil.copy2(best, path)
            return before, after, str(path)
        return before, before, str(path)

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Optimize figures with pyvips")
    ap.add_argument(
        "dirs",
        nargs="*",
        type=Path,
        help="PNG files or directories (default: books/*/assets/figures)",
    )
    ap.add_argument(
        "--format",
        choices=("png", "webp"),
        default="png",
        help="output format (default png, keeps markdown links)",
    )
    ap.add_argument("--quality", type=int, default=85, help="quant/webp quality 1-100")
    ap.add_argument("--compression", type=int, default=9, help="PNG zlib level 0-9")
    ap.add_argument("--max-width", type=int, default=0, help="downscale if wider than N")
    ap.add_argument("--force-grey", action="store_true", help="force greyscale")
    ap.add_argument("--keep-color", action="store_true", help="never auto greyscale")
    ap.add_argument(
        "--update-markdown",
        action="store_true",
        help="when --format webp, rewrite .png refs to .webp in en/zh chapters",
    )
    args = ap.parse_args(argv)

    root = _ROOT
    dirs = args.dirs
    if not dirs:
        dirs = list((root / "books").glob("*/assets/figures"))
    files = collect_pngs(dirs)
    if not files:
        print("No PNG files found", file=sys.stderr)
        return 1

    print(f"pyvips {pyvips.__version__} | libvips {pyvips.version(0)}.{pyvips.version(1)}.{pyvips.version(2)}")
    print(f"files={len(files)} format={args.format} quality={args.quality}")

    total_b = total_a = 0
    changed = 0
    webp_map: dict[str, str] = {}  # old png name -> webp name

    for path in files:
        b, a, outp = optimize_one(
            path,
            fmt=args.format,
            quality=args.quality,
            compression=args.compression,
            max_width=args.max_width or None,
            force_grey=args.force_grey,
            keep_color=args.keep_color,
        )
        total_b += b
        total_a += a
        pct = 100.0 * (1 - a / b) if b else 0
        flag = "✓" if a < b else "="
        print(f"{flag} {path.name}: {b/1024:.0f}KB -> {a/1024:.0f}KB ({pct:.1f}%)")
        if a < b:
            changed += 1
        if args.format == "webp" and outp.endswith(".webp"):
            webp_map[path.name] = Path(outp).name
            # remove original png if webp written and smaller
            if Path(outp).exists() and path.exists() and path.suffix.lower() == ".png":
                if Path(outp).stat().st_size < b:
                    path.unlink()

    print(
        f"TOTAL: {total_b/1e6:.2f}MB -> {total_a/1e6:.2f}MB "
        f"({100*(1-total_a/max(1,total_b)):.1f}% smaller), "
        f"shrunk={changed}/{len(files)}"
    )

    if args.update_markdown and webp_map:
        n = rewrite_markdown_webp(root, webp_map)
        print(f"Updated markdown references in {n} files")
    return 0


def rewrite_markdown_webp(root: Path, webp_map: dict[str, str]) -> int:
    n = 0
    for md in root.glob("books/*/en/chapters/*.md"):
        n += _rewrite_file(md, webp_map)
    for md in root.glob("books/*/zh/chapters/*.md"):
        n += _rewrite_file(md, webp_map)
    return n


def _rewrite_file(md: Path, webp_map: dict[str, str]) -> int:
    text = md.read_text(encoding="utf-8")
    orig = text
    for png, webp in webp_map.items():
        text = text.replace(png, webp)
    if text != orig:
        md.write_text(text, encoding="utf-8")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
