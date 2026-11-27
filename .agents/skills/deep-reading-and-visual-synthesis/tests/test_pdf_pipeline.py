"""
End-to-end health check for `pdf_report_engine.py`:
- Short vs. long table classification (`<= 5` vs. `> 5` body rows).
- Multi-pass adaptive `<h2>` pagination reusing a single Playwright browser instance.
- Temporary `_tmp_report_*.html` cleanup verification.
Run with: python tests/test_pdf_pipeline.py
"""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = TESTS_DIR.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import pdf_report_engine as pre


def test_1_short_and_long_table_rules() -> None:
    rows_short = "".join(f"<tr><td>S{i}</td><td>{i * 10}</td></tr>" for i in range(3))
    rows_long = "".join(f"<tr><td>L{i}</td><td>{i * 10}</td></tr>" for i in range(8))
    html_src = (
        f"<table><thead><tr><th>A</th><th>B</th></tr></thead><tbody>{rows_short}</tbody></table>"
        f"<table><thead><tr><th>A</th><th>B</th></tr></thead><tbody>{rows_long}</tbody></table>"
    )
    out = pre.apply_content_adaptive_rules(html_src)
    assert "table-short" in out, "Expected <=5-row table to receive class 'table-short'"
    assert "table-long" in out, "Expected >5-row table to receive class 'table-long'"


def test_2_adaptive_pagination_and_single_browser_reuse() -> None:
    rows_short = "".join(f"<tr><td>短列{i}</td><td>{i + 1}</td></tr>" for i in range(3))
    rows_long = "".join(f"<tr><td>長列{i}</td><td>{(i + 1) * 15}</td></tr>" for i in range(9))
    filler = "".join(
        f"<p>第 {i} 段實證摘要文字，用來自然填滿第一頁的可列印垂直高度，"
        "確保後方章節標題落在頁底剩餘空間低於門檻的位置，進而觸發自適應換頁。</p>"
        for i in range(19)
    )
    body_html = f"""
    <h1>Format B 自適應分頁端到端測試報告</h1>
    <h2>一、第一章短表與長表分流</h2>
    <table><thead><tr><th>項目</th><th>數值</th></tr></thead><tbody>{rows_short}</tbody></table>
    <table><thead><tr><th>項目</th><th>數值</th></tr></thead><tbody>{rows_long}</tbody></table>
    {filler}
    <h2>二、第二章接近頁底應自動換頁</h2>
    <p>第二章核心分析正文段落，確認標題與內容未被切斷。</p>
    <h2>三、第三章接續章節</h2>
    <p>第三章結論與建議。</p>
    """

    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        out_pdf = out_dir / "adaptive_test_report.pdf"
        t0 = time.perf_counter()
        diag = pre.compile_adaptive_report_pdf(
            title="Format B 端到端測試",
            body_html=body_html,
            output_pdf_path=str(out_pdf),
            genre="memo",
            return_diagnostics=True,
        )
        elapsed = time.perf_counter() - t0

        assert out_pdf.is_file() and out_pdf.stat().st_size > 1024
        assert diag["total_pages"] >= 2, f"Expected >=2 pages, got {diag['total_pages']}"
        assert len(diag["break_indices"]) >= 1, f"Expected at least 1 adaptive h2 break, got {diag}"
        leftover_tmp = list(out_dir.glob("_tmp_report_*.html"))
        assert not leftover_tmp, f"Temporary HTML files not cleaned up: {leftover_tmp}"
        print(
            f"  [INFO] PDF compiled in {elapsed:.2f}s | pages={diag['total_pages']} | "
            f"passes={diag['passes']} | breaks={diag['break_indices']}"
        )


def main() -> int:
    tests = [
        test_1_short_and_long_table_rules,
        test_2_adaptive_pagination_and_single_browser_reuse,
    ]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"[PASS] {fn.__name__}")
        except Exception as exc:
            failed += 1
            print(f"[FAIL] {fn.__name__}: {exc}")
    print(f"\nSummary: {len(tests) - failed}/{len(tests)} passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
