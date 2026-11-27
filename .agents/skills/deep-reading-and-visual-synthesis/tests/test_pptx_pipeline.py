"""
End-to-end safety-net test suite for Format C (`pptx_slide_engine` + `verify_visual_outputs`):
- Full 5-family, 13-refined-layout deterministic pipeline (`Step 4A` -> `render_deck_from_spec` -> `check_copy_fidelity`).
- `verify_pptx_structure(..., spec_lock_path=...)` zero Hard Error verification.
- Option C contact sheet (`4x4`) + HD `2x2` QA grids + `cleanup_preview_artifacts`.
- DISCAS typography scale, Pillow/Kinsoku text measurement, and sequence guardrail checks.
Run with: python tests/test_pptx_pipeline.py
"""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

TESTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = TESTS_DIR.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from PIL import Image, ImageDraw
from pptx import Presentation

import pptx_slide_engine as pse
import verify_visual_outputs as vvo


def _make_sample_chart_png(out_path: Path) -> Path:
    """Create a crisp 1600x900 PNG (>= 150 PPI when placed in F5-A visual box)."""
    img = Image.new("RGB", (1600, 900), (248, 250, 252))
    draw = ImageDraw.Draw(img)
    bars = [
        (180, 560, 340, 780, (59, 130, 246)),
        (460, 420, 620, 780, (13, 148, 136)),
        (740, 300, 900, 780, (245, 158, 11)),
        (1020, 200, 1180, 780, (99, 102, 241)),
    ]
    draw.line([(120, 780), (1440, 780)], fill=(100, 116, 139), width=4)
    for x0, y0, x1, y1, col in bars:
        draw.rectangle([x0, y0, x1, y1], fill=col)
    img.save(str(out_path), format="PNG")
    return out_path


def _build_full_13_layout_spec(chart_png_path: Path) -> dict[str, object]:
    """Build a 14-slide spec covering all 5 families and all 13 refined layouts (`F1-A`..`F5-C`)."""
    slides = [
        # 1. F1-A Opening Bookend
        {
            "layout": {"family_id": "F1-A"},
            "copy": {
                "badge_text": "EXECUTIVE BRIEFING",
                "headline": "全五大家族十三版型端到端驗證簡報",
                "subtitle": "涵蓋 DISCAS 字級地板、唯讀文案鎖與方案 C 結構檢查",
                "kpi_cards": [
                    {"value": "13", "label": "精煉版型數"},
                    {"value": "100%", "label": "文案保真率"},
                ],
                "speaker_notes": "開場說明本簡報用於驗證五大家族十三種版型與確定性渲染管線。",
                "key_numbers": ["13", "100%"],
            },
        },
        # 2. F1-B Section Divider
        {
            "layout": {"family_id": "F1-B"},
            "copy": {
                "section_num": "01",
                "section_title": "結構並列與脈絡展開",
                "subtitle": "測試無框並列欄、瑞士網格橫列與便當盒配置",
                "speaker_notes": "過場頁引出第一幕：三種結構展開版型。",
            },
        },
        # 3. F2-A Parallel Minimal Columns (unboxed)
        {
            "layout": {"family_id": "F2-A", "variant": "minimal_column", "spotlight_idx": 0},
            "copy": {
                "chapter_pill": "核心支柱",
                "headline": "三層解耦設計同時顧及可讀性、保真度與維護效率",
                "items": [
                    {
                        "title": "視距字級鎖定",
                        "subtitle": "DISCAS 地板",
                        "bullets": [
                            {"lead": "實體基準字級", "body": "筆電預讀維持 13.5pt，絕不跌破 12pt 底線。"},
                            {"lead": "先調幾何再動字", "body": "優先微調寬高比例，保留閱讀呼吸感。"},
                        ],
                    },
                    {
                        "title": "文案唯讀凍結",
                        "subtitle": "Step 3 契約",
                        "bullets": [
                            {"lead": "前後快照比對", "body": "渲染前後驗證 JSON 快照，嚴禁擅改數字。"},
                            {"lead": "關鍵數值校驗", "body": "自動核對百分比與金額 100% 一致。"},
                        ],
                    },
                    {
                        "title": "三階視覺品管",
                        "subtitle": "方案 C 檢查",
                        "bullets": [
                            {"lead": "零 Token 掃描", "body": "程式化攔截穿框、撞邊與 Zone 2/3 重疊。"},
                            {"lead": "分頁局部重繪", "body": "只重算異常頁，兼顧速度與品質。"},
                        ],
                    },
                ],
                "speaker_notes": "分別說明視距字級、文案唯讀與三階視覺品管三大支柱。",
                "key_numbers": ["13.5pt", "12pt", "100%"],
            },
        },
        # 4. F1-C Hero Stat (big_number)
        {
            "layout": {"family_id": "F1-C", "variant": "big_number"},
            "copy": {
                "chapter_pill": "衝擊指標",
                "headline": "去方塊排版將無效框架壓低至四成以下",
                "stat_value": "<= 40%",
                "stat_label": "帶方塊卡片頁佔比上限",
                "context_points": [
                    {"lead": "釋放畫布留白", "body": "移除重複套盒後，主要內容垂直可用空間增加約 18%。"},
                    {"lead": "聚焦視覺動線", "body": "全頁最多鎖定 1 個聚光燈主角，次要訊息退居淺灰。"},
                ],
                "speaker_notes": "強調去方塊比例控制在 40% 以內可顯著降低視覺疲勞。",
                "key_numbers": ["40%", "18%"],
            },
        },
        # 5. F2-B Editorial Split Rows
        {
            "layout": {"family_id": "F2-B", "spotlight_idx": 1},
            "copy": {
                "chapter_pill": "瑞士網格",
                "headline": "左標右展橫列清楚區隔階段責任與驗收門檻",
                "rows": [
                    {"title": "Step 3 凍結", "body": "定稿文案鎖入 spec lock，禁止後續流程刪改原意。"},
                    {"title": "Step 4A 對齊", "body": "先輸出純文字配置對齊表確認版型與配圖對應。"},
                    {"title": "Step 4B 渲染", "body": "由引擎確定性產出投影片並即時執行保真檢核。"},
                ],
                "speaker_notes": "透過左標右展說明 Step 3 到 Step 4B 的明確責任分工。",
            },
        },
        # 6. F3-A Process Steps (fine_track, 3 steps)
        {
            "layout": {"family_id": "F3-A", "variant": "fine_track", "spotlight_idx": 1},
            "copy": {
                "chapter_pill": "執行管線",
                "headline": "三步確定性管線確保每次重新渲染結果完全一致",
                "steps": [
                    {"title": "步驟一：讀取規格", "body": "解析四區 JSON 結構並初始化統一設計 Token。"},
                    {"title": "步驟二：幾何排版", "body": "依 Pillow 實測繁中字寬配置 TOP 自然堆疊高度。"},
                    {"title": "步驟三：自動體檢", "body": "核驗邊界、字級與關鍵數值無誤後交付成檔。"},
                ],
                "speaker_notes": "說明三步驟確定性管線如何消除人工調版的不穩定。",
            },
        },
        # 7. F2-C Bento Grid
        {
            "layout": {"family_id": "F2-C", "spotlight_idx": 0},
            "copy": {
                "chapter_pill": "主輔配置",
                "headline": "不對稱便當盒網格同時呈現核心結論與兩項支撐證據",
                "primary_block": {
                    "title": "核心結論：單一議題聚焦",
                    "body": "每頁只講清楚一個核心主張，透過主副比例拉開資訊主從層次，避免平均分配版面。",
                },
                "secondary_blocks": [
                    {"title": "輔助證據一", "body": "維持行距 1.3 倍與足夠內距，降低長段落壓迫感。"},
                    {"title": "輔助證據二", "body": "搭配可選 Zone 3 結論橫幅收斂全頁要旨。"},
                ],
                "zone3_takeaway": "主輔比例明確時，讀者可在 3 秒內鎖定本頁核心。",
                "speaker_notes": "展示不對稱便當盒版型的視覺主從效果。",
                "key_numbers": ["1.3", "3"],
            },
        },
        # 8. F4-A Quadrant Matrix (borderless)
        {
            "layout": {"family_id": "F4-A", "borderless": True, "spotlight_idx": 1},
            "copy": {
                "chapter_pill": "二維決策",
                "headline": "雙軸四象限依實作成本與維護效益區分重構優先順序",
                "x_axis_label": "重構效益（低 → 高）",
                "y_axis_label": "實作風險（低 → 高）",
                "quadrants": [
                    {"title": "高風險低效益", "body": "暫緩全面改寫舊專案腳本，維持門面相容即可。"},
                    {"title": "高風險高效益", "body": "拆分大型簡報引擎前先建端到端回歸安全網。"},
                    {"title": "低風險低效益", "body": "純風格微調留待後續按需修訂，不搶排程。"},
                    {"title": "低風險高效益", "body": "優先落地跨圖配色登記表與單瀏覽器重用。"},
                ],
                "speaker_notes": "用四象限矩陣說明為何先建測試安全網再拆大型引擎。",
            },
        },
        # 9. F3-B Clean Mechanism (horizontal_chain)
        {
            "layout": {"family_id": "F3-B", "topology": "horizontal_chain"},
            "copy": {
                "chapter_pill": "因果機制",
                "headline": "類別鎖色機制確保跨圖、跨簡報與網頁維持同一語義色碼",
                "nodes": [
                    {"title": "登記表鎖色", "body": "02_color_registry.json"},
                    {"title": "靜態圖查表", "body": "Format D 唯讀對齊"},
                    {"title": "跨格式嵌入", "body": "Format C / E 一致"},
                ],
                "callouts": [
                    {"lead": "順序無關", "body": "同一實體在不同排序圖表中維持固定色槽。"},
                    {"lead": "設計分離", "body": "簡報純裝飾配色不強制綁定資料登記表。"},
                ],
                "callout_heading": "機制亮點",
                "speaker_notes": "說明資料鎖色與簡報視覺設計之間的邊界。",
            },
        },
        # 10. F5-A Visual Callout (right)
        {
            "layout": {"family_id": "F5-A", "callout_position": "right", "visual_asset": str(chart_png_path), "spotlight_idx": 0},
            "copy": {
                "chapter_pill": "圖表佐證",
                "headline": "高解析度統計圖搭配右側無框導讀兼顧數據誠實與說服力",
                "visual_caption": "圖 1：測試四類別指標比較（1600x900 模擬高解析統計圖）",
                "callout_heading": "圖表解讀要點",
                "callouts": [
                    {"lead": "1:1 高解析貼圖", "body": "維持實效 PPI 高於 150，確保投影放大字跡銳利。"},
                    {"lead": "無框導讀對齊", "body": "右側以豎色條與層級字體替代厚重方框。"},
                ],
                "speaker_notes": "說明圖表頁採用右側無框導讀避免圖旁疊加方塊。",
                "key_numbers": ["150"],
            },
        },
        # 11. F4-B Comparison Table
        {
            "layout": {"family_id": "F4-B", "spotlight_col": 2},
            "copy": {
                "chapter_pill": "方案比較",
                "headline": "資料夾套件門面相容方案兼顧結構整潔與零改寫成本",
                "headers": ["評估維度", "單一巨型檔案", "套件＋相容門面"],
                "rows": [
                    ["舊腳本相容度", "高", "100% 相容"],
                    ["模組邊界清晰度", "低（9,000+ 行）", "高（職責分層）"],
                    ["改版型回歸風險", "高", "低（分層測試）"],
                ],
                "speaker_notes": "透過三線比較表對比單檔與套件門面方案的維護差異。",
                "key_numbers": ["100%"],
            },
        },
        # 12. F5-B KPI Strip
        {
            "layout": {"family_id": "F5-B", "spotlight_idx": 0},
            "copy": {
                "chapter_pill": "成果總覽",
                "headline": "三項量化驗收指標全面達標且零阻塞級錯誤",
                "kpi_items": [
                    {"value": "13", "label": "覆蓋版型數"},
                    {"value": "0", "label": "Hard Error 數"},
                    {"value": "100%", "label": "數字保真度"},
                ],
                "insight_blocks": [
                    {"title": "版型切換節奏", "body": "相鄰頁全面異構且無單一家族超過四成門檻。"},
                    {"title": "幾何防撞保護", "body": "Zone 2 與 Zone 3 保留安全間距，無跨區重疊。"},
                ],
                "speaker_notes": "總覽本次簡報安全網驗證的三大核心量化指標。",
                "key_numbers": ["13", "0", "100%"],
            },
        },
        # 13. F5-C Focal Anatomy (with native OMML equation)
        {
            "layout": {"family_id": "F5-C", "mode": "left_right", "use_omml": True},
            "copy": {
                "chapter_pill": "視距公式",
                "headline": "DISCAS 視距公式由觀看距離與畫面高度反推最小字級地板",
                "focal_title": "DISCAS 最小字級公式",
                "focal_formula": "min_pt = max(12.0, 3.18 * D / H)",
                "focal_note": "D 為最遠觀眾距離（m），H 為畫面高度（m）",
                "items": [
                    {"lead": "近距筆電閱讀", "body": "D/H <= 3.5 時鎖定 12.0pt 硬底線，常設 13.5pt 正文。"},
                    {"lead": "大場投影演講", "body": "D/H >= 7.0 時自動拉升至 20pt 以上，防止遠距糊字。"},
                ],
                "speaker_notes": "解剖 DISCAS 公式各項物理參數與對應場景字級。",
                "key_numbers": ["12.0", "3.18", "13.5", "20"],
            },
        },
        # 14. F1-A Closing Bookend
        {
            "layout": {"family_id": "F1-A"},
            "copy": {
                "badge_text": "SUMMARY",
                "headline": "全自動安全網就位，支援高信心重構與持續迭代",
                "subtitle": "感謝審閱・五大家族十三版型驗證通過",
                "speaker_notes": "結尾總結安全網建立完成，準備進入模組分家與長期維護階段。",
            },
        },
    ]
    return {
        "schema_version": "1.0",
        "deck_meta": {
            "title": "Format C 全版型驗證簡報",
            "viewing_context": "筆電近看預讀",
            "distance_m": 2.0,
            "screen_height_m": 0.6,
            "min_font_pt": 12.0,
        },
        "design_tokens": {
            "min_font_pt": 12.0,
            "target_body_pt": 13.5,
            "doc_theme_id": "swiss_editorial",
        },
        "slides": slides,
    }


def test_1_step4a_preview_and_deterministic_render() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        chart_png = _make_sample_chart_png(tmp_dir / "sample_chart.png")
        spec = _build_full_13_layout_spec(chart_png)
        spec_snapshot = copy.deepcopy(spec)

        preview_md = pse.export_step4a_alignment_preview(spec)
        for code in ("F1-A", "F1-B", "F1-C", "F2-A", "F2-B", "F2-C", "F3-A", "F3-B", "F4-A", "F4-B", "F5-A", "F5-B", "F5-C"):
            assert code in preview_md, f"Missing {code} in Step 4A alignment preview"

        out_pptx = tmp_dir / "test_full_13_layouts.pptx"
        rendered_path = pse.render_deck_from_spec(
            spec,
            out_pptx,
            validate_sequence=True,
            require_bookends=True,
            strict_fidelity=True,
        )
        assert Path(rendered_path).is_file() and Path(rendered_path).stat().st_size > 20000
        assert spec == spec_snapshot, "Input spec dictionary mutated during render!"

        prs = Presentation(rendered_path)
        assert len(prs.slides) == 14, f"Expected 14 slides, got {len(prs.slides)}"

        fidelity = pse.check_copy_fidelity(spec, rendered_path)
        assert fidelity["passed"], f"Copy fidelity failed: {fidelity}"


def test_2_verify_pptx_structure_zero_hard_errors() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        chart_png = _make_sample_chart_png(tmp_dir / "sample_chart.png")
        spec = _build_full_13_layout_spec(chart_png)
        spec_path = tmp_dir / "02c_slide_spec_lock.json"
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")

        out_pptx = tmp_dir / "verify_deck.pptx"
        pse.render_deck_from_spec(spec, out_pptx, validate_sequence=True, strict_fidelity=True)

        report = vvo.verify_pptx_structure(
            str(out_pptx),
            min_font_pt=12.0,
            profile="reading",
            spec_lock_path=spec_path,
        )
        print(f"  [INFO] {report['stats_line']}")
        if report.get("errors"):
            print("  [INFO] Errors:", report["errors"])
        assert report["passed"], f"verify_pptx_structure failed with errors: {report['errors']}"


def test_3_option_c_contact_sheet_and_qa_grids() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        pngs: list[str] = []
        for idx in range(1, 7):
            p = tmp_dir / f"slide_{idx:02d}.png"
            img = Image.new("RGB", (640, 360), (241, 245, 249))
            ImageDraw.Draw(img).rectangle([40, 40, 600, 320], outline=(59, 130, 246), width=4)
            img.save(str(p), format="PNG")
            pngs.append(str(p))

        sheet_path = Path(vvo.build_pptx_contact_sheet(pngs, str(tmp_dir / "_qa_contact_test.png")))
        assert sheet_path.is_file()
        with Image.open(sheet_path) as im:
            assert im.size[0] > 0 and im.size[1] > 0

        grids = vvo.build_pptx_qa_grids(pngs, str(tmp_dir), prefix="test")
        assert len(grids) == 2, f"Expected 2 2x2 grids for 6 slides, got {len(grids)}"
        for g in grids:
            assert Path(g).is_file()

        removed = vvo.cleanup_preview_artifacts(str(tmp_dir))
        assert len(removed) >= 9, f"Expected >=9 cleaned artifacts, got {len(removed)}"
        leftovers = list(tmp_dir.glob("_qa_*")) + list(tmp_dir.glob("slide_*.png"))
        assert not leftovers, f"Leftover preview artifacts after cleanup: {leftovers}"


def test_4_layout_helpers_and_tokens() -> None:
    assert pse.calc_min_font_pt_from_distance(8.0, 1.5) >= 16.0
    scale = pse.resolve_typography_scale(14.0)
    assert scale["body"] == 14.0 and scale["headline"] >= 14.0 * 1.35

    tokens = pse.build_slide_design_tokens(min_font_pt=12.0, target_body_pt=13.5)
    assert tokens["target_body_pt"] == 13.5

    layout = pse.measure_text_layout("繁體中文測試斷行與行數計算。", 4.0, 14.0)
    assert len(layout["lines"]) >= 1 and layout["safe_height_in"] > 0

    dup_failed = False
    try:
        pse.validate_layout_sequence(["F1-A", "F2-A", "F2-A", "F1-A"], require_bookends=True, min_distinct=2)
    except ValueError:
        dup_failed = True
    assert dup_failed, "Expected ValueError on duplicate consecutive layout codes"


def main() -> int:
    tests = [
        test_1_step4a_preview_and_deterministic_render,
        test_2_verify_pptx_structure_zero_hard_errors,
        test_3_option_c_contact_sheet_and_qa_grids,
        test_4_layout_helpers_and_tokens,
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
