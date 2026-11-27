"""
Safety-net tests for `generate_mindmap.py` (lazy Matplotlib import + diagram rendering)
and `ingest_source_material.py` (offline modality detection + local Markdown ingestion).
Run with: python tests/test_mindmap_and_ingest.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

TESTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = TESTS_DIR.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import ingest_source_material as ism


def test_1_generate_mindmap_lazy_import() -> None:
    code = (
        f"import sys; sys.path.insert(0, {repr(str(SCRIPTS_DIR))}); "
        "import generate_mindmap; "
        "assert 'matplotlib' not in sys.modules, 'matplotlib eagerly loaded on import!'; "
        "print('LAZY_OK')"
    )
    res = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
        check=False,
    )
    assert res.returncode == 0, f"Subprocess failed: {res.stderr}\n{res.stdout}"
    assert "LAZY_OK" in res.stdout


def test_2_mindmap_landscape_and_a4_render() -> None:
    import generate_mindmap as gm

    with tempfile.TemporaryDirectory() as tmp:
        out_land = Path(tmp) / "landscape_smoke.png"
        fig, ax, theme = gm.setup_publication_canvas(dpi=120)
        gm.draw_macro_zone(ax, 3.0, 20.0, 42.0, 62.0, "主幹區塊一", theme, accent_key="primary")
        b1 = gm.draw_modern_card(
            ax, 5.0, 50.0, 38.0, "核心論點", ["• 測試條目一與避頭尾驗證。", "• 測試條目二。"], theme, accent_key="primary", top_y=76.0
        )
        b2 = gm.draw_modern_card(
            ax, 55.0, 50.0, 38.0, "落地機制", ["• 測試機制一。", "• 測試機制二。"], theme, accent_key="success", top_y=76.0
        )
        gm.draw_labeled_arrow(
            ax,
            gm.box_edge_point(b1, "right"),
            gm.box_edge_point(b2, "left"),
            label_text="驅動",
            theme=theme,
            accent_key="primary",
        )
        gm.draw_canvas_header_and_footer(ax, "知識圖譜冒煙測試", "副標題", "核心總結", "驗證雙欄排版與箭頭渲染。", theme=theme)
        gm.save_publication_figure(fig, str(out_land), theme=theme, dpi=120)
        assert out_land.is_file() and out_land.stat().st_size > 4096

        out_a4 = Path(tmp) / "a4_smoke.png"
        fig_a4, ax_a4, theme_a4 = gm.setup_a4_portrait_canvas(height_in=2.1, dpi=150)
        n1 = gm.draw_a4_node_box(ax_a4, 5.0, 20.0, 32.0, 60.0, "STEP 1", "輸入來源", ["原始文件"], theme=theme_a4)
        n2 = gm.draw_a4_node_box(ax_a4, 60.0, 20.0, 32.0, 60.0, "STEP 2", "圖譜輸出", ["300 DPI"], theme=theme_a4, accent_key="success")
        gm.draw_a4_arrow(ax_a4, (n1[0] + n1[2], 50.0), (n2[0], 50.0), label="轉換", theme=theme_a4)
        gm.save_a4_portrait_figure(fig_a4, str(out_a4), theme=theme_a4, dpi=150)
        assert out_a4.is_file() and out_a4.stat().st_size > 2048


def test_3_ingest_modality_and_local_markdown() -> None:
    assert ism.detect_input_modality("https://youtu.be/dQw4w9WgXcQ") == "youtube"
    assert ism.detect_input_modality("https://example.com/article") == "web_url"
    assert ism.detect_input_modality("report.pdf") == "pdf_file"
    assert ism.detect_input_modality("notes.docx") == "docx_file"
    assert ism.detect_input_modality("data.csv") == "csv_dataset"
    assert ism.detect_input_modality("article.md") == "text_or_md"
    assert ism.detect_input_modality("這是一段純文字輸入。") == "text_or_md"

    with tempfile.TemporaryDirectory() as tmp:
        src_md = Path(tmp) / "input.md"
        src_md.write_text("# 測試文章\n\n第一段研究摘要。\n", encoding="utf-8")
        out_md = Path(tmp) / "00_source_article.md"
        res = ism.ingest_to_source_markdown(str(src_md), output_md_path=str(out_md), title_override="自訂標題")
        assert res["ok"] is True
        assert out_md.is_file()
        content = out_md.read_text(encoding="utf-8")
        assert "自訂標題" in content and "第一段研究摘要" in content


def main() -> int:
    tests = [
        test_1_generate_mindmap_lazy_import,
        test_2_mindmap_landscape_and_a4_render,
        test_3_ingest_modality_and_local_markdown,
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
