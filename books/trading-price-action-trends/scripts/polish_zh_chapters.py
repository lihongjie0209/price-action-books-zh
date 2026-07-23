#!/usr/bin/env python3
"""Re-merge thin chapters from zh/chunks and strip residual PDF running headers.

Handles:
- ALL-CAPS single-line English running headers
- Title Case multi-line English chapter titles (e.g. "Bar Basics:" / "Signal Bars," ...)
- Short Chinese running headers after <!-- PDF page N --> markers
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZH_CH = ROOT / "zh" / "chapters"
ZH_CK = ROOT / "zh" / "chunks"

# ALL-CAPS single-line patterns
ALLCAPS_PATTERNS = [
    r"(?m)^SIGNAL BARS: OTHER TYPES\s*$",
    r"(?m)^SIGNAL BARS: REVERSAL BARS\s*$",
    r"(?m)^BAR BASICS:.*$",
    r"(?m)^REVERSAL DAY\s*$",
    r"(?m)^TREND RESUMPTION DAY\s*$",
    r"(?m)^STAIRS: BROAD CHANNEL TRENDS?\s*$",
    r"(?m)^TRENDING TRADING RANGE DAYS\s*$",
    r"(?m)^TREND FROM THE OPEN AND SMALL PULLBACK TRENDS\s*$",
    r"(?m)^SPIKE AND CHANNEL TREND\s*$",
    r"(?m)^EXAMPLE OF HOW TO TRADE A TREND\s*$",
    r"(?m)^SIGNS OF STRENGTH IN A TREND\s*$",
    r"(?m)^P\s*A\s*R\s*T\s+[IVXLC\d\s]+$",
    r"(?m)^C\s*H\s*A\s*P\s*T\s*E\s*R\s+[\d\s]+$",
    r"(?m)^CHAPTER\s+\d+\s*$",
    r"(?m)^PRICE ACTION\s*$",
    r"(?m)^TRENDS\s*$",
    r"(?m)^COMMON TREND PATTERNS\s*$",
    r"(?m)^TREND LINES AND CHANNELS\s*$",
    r"(?m)^LIST OF TERMS USED IN THIS BOOK\s*$",
    r"(?m)^THE SPECTRUM OF PRICE ACTION\s*$",
    r"(?m)^BREAKOUTS, TRADING RANGES, TESTS, AND REVERSALS\s*$",
    r"(?m)^TREND BARS, DOJI BARS, AND CLIMAXES\s*$",
    r"(?m)^OUTSIDE BARS\s*$",
    r"(?m)^THE IMPORTANCE OF THE CLOSE OF THE BAR\s*$",
    r"(?m)^EXCHANGE-TRADED FUNDS AND INVERSE CHARTS\s*$",
    r"(?m)^SECOND ENTRIES\s*$",
    r"(?m)^LATE AND MISSED ENTRIES\s*$",
    r"(?m)^PATTERN EVOLUTION\s*$",
    r"(?m)^TREND LINES\s*$",
    r"(?m)^TREND CHANNEL LINES\s*$",
    r"(?m)^CHANNELS\s*$",
    r"(?m)^MICRO CHANNELS\s*$",
    r"(?m)^HORIZONTAL LINES:.*$",
    r"(?m)^TWO LEGS\s*$",
    r"(?m)^FIGURE\s+\d.*$",
    r"<!--\s*MERGE_MARK\s*-->",
]

# Title Case multi-line decorative titles (line sequences)
KNOWN_MULTILINE_TITLES = [
    ["Bar Basics:", "Signal Bars,", "Entry Bars,", "Setups, and", "Candle Patterns"],
    ["Trend", "Resumption Day"],
    ["Stairs: Broad", "Channel Trend"],
    ["Trading", "Price", "Action"],
    ["Trend Bars,", "Doji Bars,", "and Climaxes"],
    ["Breakouts,", "Trading Ranges,", "Tests, and", "Reversals"],
    ["Signal Bars:", "Reversal Bars"],
    ["Signal Bars:", "Other Types"],
    ["The Importance", "of the Close of", "the Bar"],
    ["Exchange-Traded", "Funds and", "Inverse Charts"],
    ["Late and", "Missed Entries"],
    ["Horizontal Lines:", "Swing Points and", "Other Key", "Price Levels"],
    ["Example of How", "to Trade a Trend"],
    ["Signs of Strength", "in a Trend"],
    ["Spike and Channel", "Trend"],
    ["Trending Trading", "Range Days"],
    ["Trend from the Open", "and Small", "Pullback Trends"],
    ["The Spectrum of", "Price Action:", "Extreme Trends", "to Extreme", "Trading Ranges"],
    ["List of Terms", "Used in This Book"],
]

TITLE_CASE_LINE = re.compile(r"^[A-Z][A-Za-z0-9 ,:\-\'/&()]+$")

CN_RUNNERS = {
    "价格行为",
    "趋势线与通道",
    "常见趋势形态",
    "趋势",
    "目录",
    "本书所用术语表",
    "导论",
    "信号K线：其他类型",
    "反转日",
    "趋势恢复日",
}


def merge_stem(stem: str) -> None:
    parts = sorted(
        ZH_CK.glob(f"{stem}.part*.md"),
        key=lambda p: int(re.search(r"part(\d+)", p.name).group(1)),
    )
    if not parts:
        print(f"no chunks for {stem}", file=sys.stderr)
        return
    merged = "\n\n".join(p.read_text(encoding="utf-8").strip() for p in parts) + "\n"
    out = ZH_CH / f"{stem}.md"
    out.write_text(merged, encoding="utf-8")
    print(f"merged {stem} -> {out.stat().st_size} bytes")


def strip_multiline_titles(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        matched = False
        for title_lines in KNOWN_MULTILINE_TITLES:
            n = len(title_lines)
            if i + n <= len(lines):
                window = [lines[i + k].strip() for k in range(n)]
                if window == title_lines:
                    i += n
                    matched = True
                    break
        if not matched:
            out.append(lines[i])
            i += 1
    return out


def strip_after_page_markers(lines: list[str]) -> list[str]:
    """After <!-- PDF page N -->, drop EN Title Case title lines and CN running headers."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        out.append(lines[i])
        if re.match(r"<!-- PDF page \d+", lines[i].strip()):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                out.append(lines[j])
                j += 1
            # drop CN runner
            if j < len(lines) and lines[j].strip() in CN_RUNNERS:
                j += 1
            # drop consecutive Title Case EN lines
            while j < len(lines):
                t = lines[j].strip()
                if not t:
                    break
                if re.search(r"[\u4e00-\u9fff]", t) or t.startswith("<!--") or t.startswith("#"):
                    break
                if TITLE_CASE_LINE.match(t) and 3 <= len(t) < 80:
                    j += 1
                    continue
                break
            i = j
            continue
        i += 1
    return out


def strip_allcaps_regex(text: str) -> str:
    for pat in ALLCAPS_PATTERNS:
        text = re.sub(pat, "", text)
    return text


def polish_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    lines = strip_multiline_titles(lines)
    lines = strip_after_page_markers(lines)
    text = "\n".join(lines)
    text = strip_allcaps_regex(text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    if not text.endswith("\n"):
        text += "\n"
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def strip_all() -> None:
    n = 0
    for p in sorted(ZH_CH.glob("*.md")):
        if polish_file(p):
            print(f"stripped {p.name}")
            n += 1
    print(f"polished {n} files")


def assert_no_flagged_residuals() -> None:
    """Regression checks for skeptic-flagged Title Case multi-line titles."""
    checks = {
        "09-ch04-bar-basics-signal-bars-entry-bars-setups-and-candle-patterns.md": [
            "Bar Basics:",
            "Signal Bars,",
            "Entry Bars,",
            "Setups, and",
            "Candle Patterns",
        ],
        "33-ch25-trend-resumption-day.md": [
            "Resumption Day",
        ],
        "34-ch26-stairs-broad-channel-trend.md": [
            "Stairs: Broad",
            "Channel Trend",
        ],
    }
    errors = []
    for name, frags in checks.items():
        p = ZH_CH / name
        t = p.read_text(encoding="utf-8")
        # ignore HTML comments
        body_lines = [
            ln.strip()
            for ln in t.splitlines()
            if ln.strip() and not ln.strip().startswith("<!--") and not ln.strip().startswith("#")
        ]
        for frag in frags:
            if any(ln == frag for ln in body_lines):
                errors.append(f"{name}: residual body line {frag!r}")
    if errors:
        print("FAIL residual title fragments:")
        for e in errors:
            print(" -", e)
        raise SystemExit(1)
    print("PASS residual Title Case checks")


if __name__ == "__main__":
    if "--merge-intro" in sys.argv:
        merge_stem("04-introduction")
    strip_all()
    assert_no_flagged_residuals()
