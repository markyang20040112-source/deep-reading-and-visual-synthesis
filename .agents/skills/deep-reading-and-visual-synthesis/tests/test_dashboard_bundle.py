"""
Self-contained test suite for Format E `verify_dashboard_bundle` in `verify_visual_outputs.py`.
Run with: python tests/test_dashboard_bundle.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = TESTS_DIR.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from verify_visual_outputs import verify_dashboard_bundle


def _create_valid_bundle(root: Path) -> None:
    (root / "css").mkdir(parents=True, exist_ok=True)
    (root / "js").mkdir(parents=True, exist_ok=True)
    (root / "data").mkdir(parents=True, exist_ok=True)

    (root / "index.html").write_text(
        '<!DOCTYPE html><html><head><link rel="stylesheet" href="./css/style.css"></head>'
        '<body><script src="./js/gephi_palette.js"></script>'
        '<script src="./data/x_data.js"></script>'
        '<script src="./js/dashboard.js"></script></body></html>\n',
        encoding="utf-8",
    )
    (root / "css/style.css").write_text(
        ":root { --color-cat-1: #0284C7; }\n"
        ".kpi-value { font-variant-numeric: tabular-nums; }\n",
        encoding="utf-8",
    )
    (root / "js/gephi_palette.js").write_text("window.GephiPalette = {};\n", encoding="utf-8")
    (root / "js/dashboard.js").write_text("console.log('ready');\n", encoding="utf-8")
    (root / "data/x_data.js").write_text("window.DASHBOARD_DATA = [];\n", encoding="utf-8")
    (root / "data/x_data.json").write_text("[]\n", encoding="utf-8")
    (root / ".nojekyll").write_text("", encoding="utf-8")
    (root / "README.md").write_text("# Dashboard\n", encoding="utf-8")
    (root / ".gitignore").write_text(
        ".DS_Store\nThumbs.db\n.netlify/\n.wrangler/\n",
        encoding="utf-8",
    )


def test_1_valid_bundle_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "dash"
        _create_valid_bundle(d)
        res = verify_dashboard_bundle(str(d))
        assert res["passed"], f"Expected valid bundle to pass, got issues: {res['issues']}"
        assert res["issues"] == []


def test_2_missing_wrangler_in_gitignore_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "dash"
        _create_valid_bundle(d)
        (d / ".gitignore").write_text(".DS_Store\n.netlify/\n", encoding="utf-8")
        res = verify_dashboard_bundle(str(d))
        assert not res["passed"], "Expected bundle missing .wrangler/ to fail"
        assert any(".wrangler" in issue for issue in res["issues"]), (
            f"Expected .wrangler mention in issues, got: {res['issues']}"
        )


def test_3_nested_git_dir_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "dash"
        _create_valid_bundle(d)
        (d / ".git").mkdir()
        res = verify_dashboard_bundle(str(d))
        assert not res["passed"], "Expected bundle with .git directory to fail"
        assert any(".git" in issue and "git subtree split" in issue for issue in res["issues"]), (
            f"Expected updated nested .git guidance in issues, got: {res['issues']}"
        )


def main() -> int:
    tests = [
        test_1_valid_bundle_passes,
        test_2_missing_wrangler_in_gitignore_fails,
        test_3_nested_git_dir_fails,
    ]
    for fn in tests:
        fn()
        print(f"  [PASS] {fn.__name__}")
    print(f"All {len(tests)} dashboard bundle tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
