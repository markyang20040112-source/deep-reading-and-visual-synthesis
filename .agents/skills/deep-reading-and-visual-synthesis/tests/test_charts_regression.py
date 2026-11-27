"""
Regression & zero-collision test suite for all chart families, `setup_chart_canvas`,
Family 2/5 APIs, `plot_dumbbell` refactor invariants, and read-only entity color lookup.
Run with: python tests/test_charts_regression.py
"""

from __future__ import annotations

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

import matplotlib

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

import hcl_color_engine as hce
from color_registry import clear_active_registry, use_session_registry
from verify_visual_outputs import check_matplotlib_text_collisions


def _snapshot_palette() -> dict:
    return {
        "qualitative_4": list(hce.GEPHI_QUALITATIVE_HEX),
        "light_badge_tints_4": list(hce.GEPHI_LIGHT_BADGE_TINTS),
        "sequential_scales": {k: list(v) for k, v in hce.GEPHI_SEQUENTIAL_SCALES.items()},
        "diverging_9": list(hce.GEPHI_DIVERGING_SCALE),
        "discrete_neutrals": dict(hce.GEPHI_DISCRETE_NEUTRALS),
    }


def _restore_palette(snap: dict) -> None:
    hce.activate_chart_palette(snap)
    clear_active_registry()


def test_1_setup_chart_canvas_variants() -> None:
    fig_v, ax_v = hce.setup_chart_canvas("vertical")
    assert tuple(round(x, 2) for x in fig_v.get_size_inches()) == (12.0, 6.4)
    plt.close(fig_v)

    fig_h, ax_h = hce.setup_chart_canvas("horizontal")
    assert tuple(round(x, 2) for x in fig_h.get_size_inches()) == (12.8, 6.7)
    plt.close(fig_h)

    fig_s, ax_s = hce.setup_chart_canvas("vertical", slide_mode=True)
    assert tuple(round(x, 2) for x in fig_s.get_size_inches()) == (9.6, 5.2)
    plt.close(fig_s)

    raised = False
    try:
        hce.setup_chart_canvas("diagonal")
    except ValueError:
        raised = True
    assert raised, "Expected ValueError on unsupported orientation"


def test_2_existing_charts_and_components_smoke() -> None:
    # Covers all 14 existing chart/component functions
    fig, ax = hce.setup_chart_canvas("horizontal")
    res_cd = hce.plot_cleveland_dot(ax, ["甲市", "乙市", "丙市", "丁市"], [18.0, 42.0, 29.0, 71.0])
    assert res_cd["scatter"] is not None
    coll_cd = check_matplotlib_text_collisions(fig, print_report=False)
    assert coll_cd["passed"], f"Cleveland collision: {coll_cd['issues']}"
    plt.close(fig)

    for directed in (False, True):
        fig, ax = hce.setup_chart_canvas("horizontal")
        res_db = hce.plot_dumbbell(ax, ["北部", "中部", "南部"], [20.0, 35.0, 15.0], [32.0, 30.0, 29.0], directed=directed)
        assert res_db["scatter_start"] is not None
        coll_db = check_matplotlib_text_collisions(fig, print_report=False)
        assert not coll_db["overlaps"], f"Dumbbell(directed={directed}) overlaps: {coll_db['overlaps']}"
        if directed:
            assert coll_db["passed"], f"Dumbbell(directed=True) collision: {coll_db['issues']}"
        plt.close(fig)

    cases = [
        lambda ax, fig: hce.plot_slope_chart(ax, ["A", "B", "C"], [40.0, 55.0, 30.0], [60.0, 48.0, 42.0]),
        lambda ax, fig: hce.plot_bullet(ax, ["指標一", "指標二"], [78.0, 62.0], [80.0, 75.0], bands=[[50, 75, 100], [45, 70, 100]]),
        lambda ax, fig: hce.plot_marimekko(ax, ["區1", "區2", "區3"], [50.0, 30.0, 20.0], [[40.0, 60.0], [70.0, 30.0], [55.0, 45.0]], ["子A", "子B"]),
        lambda ax, fig: hce.plot_waterfall(ax, ["期初", "新增", "流失", "期末"], [100.0, 35.0, -18.0, 117.0], is_total_flags=[True, False, False, True]),
        lambda ax, fig: hce.plot_clipped_kde(ax, [1.2, 2.5, 3.1, 4.0, 5.2, 6.8, 7.1, 8.5, 9.0, 11.4]),
        lambda ax, fig: (ax.plot([0, 10], [0, 10]), hce.add_halo_vline(ax, 5.0), hce.annotate_floor_extreme(ax, 1.0, 0.0, "低點"), hce.add_editorial_footer(fig, ["資料來源：測試資料集", "註：測試底註"])),
        lambda ax, fig: (ax.plot([0, 10], [0, 10]), hce.add_badge_vline(ax, 5.0, "基準線 5.0")),
        lambda ax, fig: (ax.plot([0, 10], [0, 10]), hce.add_regime_shading_and_events(ax, regimes=[{"start": 2, "end": 5, "label": "試行期"}], events=[{"x": 6, "y": 6, "label": "改制"}])),
        lambda ax, fig: (ax.plot([0, 10], [0, 10]), hce.add_inset_leaderboard(ax, ["項目A", "項目B", "項目C"], [88.0, 64.0, 41.0], title="排行")),
        lambda ax, fig: hce.plot_liquid_container_bars(ax, ["杯一", "杯二", "杯三"], [180.0, 320.0, 450.0], max_capacity=500.0),
        lambda ax, fig: hce.plot_masked_texture_wedge(ax, 64.5, texture_img_path=None, title="比例", subtitle="測試"),
        lambda ax, fig: hce.plot_sprite_scatter(ax, [1.0, 2.0, 3.0], [10.0, 25.0, 18.0], sprite_img_path=None, labels=["a", "b", "c"]),
    ]
    for fn in cases:
        fig, ax = hce.setup_chart_canvas("vertical")
        fn(ax, fig)
        fig.canvas.draw()
        plt.close(fig)


def test_3_family2_and_family5_zero_collision() -> None:
    # 1) plot_scissors_line (with uneven years & close endpoints)
    fig, ax = hce.setup_chart_canvas("vertical")
    res_sc = hce.plot_scissors_line(
        ax,
        [2018, 2019, 2021, 2024, 2025],
        [82.0, 88.0, 74.0, 91.0, 95.0],
        [45.0, 52.0, 60.0, 84.0, 92.0],
        label_a="出國人次",
        label_b="來臺人次",
    )
    assert res_sc["line_a"] is not None and res_sc["fill"] is not None
    coll_sc = check_matplotlib_text_collisions(fig, print_report=False)
    assert coll_sc["passed"], f"Scissors line collision: {coll_sc['issues']}"
    plt.close(fig)

    # 2) plot_paired_dual_bar
    fig, ax = hce.setup_chart_canvas("vertical")
    res_pd = hce.plot_paired_dual_bar(
        ax,
        ["製造業", "金融業", "零售業", "醫療業"],
        [88.0, 92.0, 81.0, 76.0],
        [24.0, 31.0, 19.0, 14.0],
        label_a="AI 樂觀預期",
        label_b="實際核心投產",
    )
    assert res_pd["bars_a"] is not None and res_pd["bars_b"] is not None
    coll_pd = check_matplotlib_text_collisions(fig, print_report=False)
    assert coll_pd["passed"], f"Paired dual bar collision: {coll_pd['issues']}"
    plt.close(fig)

    # 3) plot_quadrant_bubble
    fig, ax = hce.setup_chart_canvas("vertical")
    res_qb = hce.plot_quadrant_bubble(
        ax,
        [15.0, 28.0, 42.0, 65.0, 78.0, 33.0, 52.0, 85.0],
        [22.0, 68.0, 44.0, 82.0, 35.0, 18.0, 61.0, 90.0],
        size_vals=[120, 450, 300, 980, 620, 200, 510, 1200],
        labels=["甲區", "乙區", "丙區", "丁區", "戊區", "己區", "庚區", "辛區"],
        categories=["台北", "台中", "高雄", "台北", "台中", "高雄", "台北", "台南"],
        quadrant_labels=("高潛力觀察", "雙高領航區", "低基期觀望", "高量低成長"),
        size_unit="億",
    )
    assert res_qb["scatter"] is not None
    coll_qb = check_matplotlib_text_collisions(fig, print_report=False)
    assert coll_qb["passed"], f"Quadrant bubble collision: {coll_qb['issues']}"
    plt.close(fig)


def test_4_family2_and_family5_readonly_registry_lock() -> None:
    snap = _snapshot_palette()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            reg = use_session_registry(tmp)
            reg.pin("台北", 2)
            reg.pin("高雄", 3)

            # Scissors line lookup
            fig, ax = hce.setup_chart_canvas("vertical")
            res_sc = hce.plot_scissors_line(
                ax, [2020, 2021, 2022], [10, 20, 30], [15, 25, 35], label_a="台北", label_b="高雄"
            )
            assert mcolors.to_hex(res_sc["line_a"].get_color()).upper() == reg.hex_for("台北").upper()
            assert mcolors.to_hex(res_sc["line_b"].get_color()).upper() == reg.hex_for("高雄").upper()
            plt.close(fig)

            # Paired dual bar lookup
            fig, ax = hce.setup_chart_canvas("vertical")
            res_pd = hce.plot_paired_dual_bar(
                ax, ["指標1", "指標2"], [40, 60], [30, 50], label_a="台北", label_b="未登記對照"
            )
            assert mcolors.to_hex(res_pd["bars_a"].patches[0].get_facecolor()).upper() == reg.hex_for("台北").upper()
            assert reg.hex_for("未登記對照") is None
            plt.close(fig)

            # Quadrant bubble lookup
            fig, ax = hce.setup_chart_canvas("vertical")
            res_qb = hce.plot_quadrant_bubble(
                ax, [10, 20, 30], [20, 40, 60], categories=["台北", "高雄", "未登記城市"], annotate_top_k=0
            )
            assert res_qb["category_colors"]["台北"].upper() == reg.hex_for("台北").upper()
            assert res_qb["category_colors"]["高雄"].upper() == reg.hex_for("高雄").upper()
            assert reg.hex_for("未登記城市") is None
            plt.close(fig)
    finally:
        _restore_palette(snap)


def main() -> int:
    tests = [
        test_1_setup_chart_canvas_variants,
        test_2_existing_charts_and_components_smoke,
        test_3_family2_and_family5_zero_collision,
        test_4_family2_and_family5_readonly_registry_lock,
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
