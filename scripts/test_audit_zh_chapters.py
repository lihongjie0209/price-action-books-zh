#!/usr/bin/env python3
"""Unit tests for scripts/audit_zh_chapters.py (real shipped functions)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import audit_zh_chapters as audit  # noqa: E402


class TestMidbreakDetectFix(unittest.TestCase):
    def test_detect_mid_sentence_across_page_marker(self):
        text = (
            "## 标题\n\n"
            "他们会把它看作\n\n"
            "<!-- PDF page 160 -->\n\n"
            "潜在耗竭缺口。若市场回落。\n"
        )
        issues = audit.detect_midbreaks_in_text(text, "sample.md")
        self.assertEqual(len(issues), 1)
        self.assertIn("看作", issues[0]["left_tail"])
        self.assertIn("潜在", issues[0]["right_head"])

    def test_fix_joins_and_inlines_page_marker(self):
        text = (
            "## 标题\n\n"
            "他们会把它看作\n\n"
            "<!-- PDF page 160 -->\n\n"
            "潜在耗竭缺口。若市场回落。\n"
        )
        fixed, n = audit.fix_midbreaks_in_text(text)
        self.assertGreaterEqual(n, 1)
        self.assertEqual(len(audit.detect_midbreaks_in_text(fixed, "x")), 0)
        self.assertIn("<!-- PDF page 160 -->", fixed)
        # no blank-line split between 看作 and 潜在
        self.assertRegex(fixed, r"看作\s*<!-- PDF page 160 -->\s*潜在")

    def test_complete_sentence_not_joined(self):
        text = (
            "这是完整一句。\n\n"
            "<!-- PDF page 10 -->\n\n"
            "这是下一句开始。\n"
        )
        fixed, n = audit.fix_midbreaks_in_text(text)
        self.assertEqual(n, 0)
        self.assertEqual(len(audit.detect_midbreaks_in_text(fixed, "x")), 0)
        # page comment remains a separate block
        self.assertIn("<!-- PDF page 10 -->", fixed)

    def test_real_ranges_gaps_chapter_zero_midbreaks(self):
        path = (
            REPO
            / "books"
            / "trading-price-action-trading-ranges"
            / "zh"
            / "chapters"
            / "13-ch06-gaps.md"
        )
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        issues = audit.detect_midbreaks_in_text(text, str(path))
        self.assertEqual(issues, [], msg=f"residual midbreaks: {issues[:3]}")


class TestFigureResolve(unittest.TestCase):
    def test_figure_refs_resolve_for_all_books(self):
        # Drive cmd_figures on real tree; must exit 0
        code = audit.cmd_figures(None, None)
        self.assertEqual(code, 0)

    def test_remapped_reversals_charts_are_landscape(self):
        fig = REPO / "books" / "trading-price-action-reversals" / "assets" / "figures"
        for name in ("fig_4_14.webp", "fig_20_2.webp", "fig_24_12.webp"):
            p = fig / name
            self.assertTrue(p.is_file(), name)
            try:
                from PIL import Image
            except ImportError:
                self.skipTest("Pillow not available")
            with Image.open(p) as im:
                w, h = im.size
            self.assertGreaterEqual(w, h, f"{name} should be chart-like landscape, got {w}x{h}")


if __name__ == "__main__":
    unittest.main()
