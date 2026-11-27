"""
Self-contained test suite for `color_registry.py`, Phase A wiring in `hcl_color_engine.py`,
`gephi_palette.js` entity color support, and `verify_visual_outputs.verify_color_registry`.
Run with: python tests/test_color_registry.py
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
from color_registry import (
    REGISTRY_FILENAME,
    CategoryColorRegistry,
    RegistryFullError,
    clear_active_registry,
    use_session_registry,
)
from verify_visual_outputs import verify_color_registry


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


def test_1_order_independence() -> None:
    snap = _snapshot_palette()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            reg_path = Path(tmp) / REGISTRY_FILENAME
            r1 = CategoryColorRegistry(reg_path)
            m1 = r1.assign(["台北", "台中", "高雄"], source="fig01")

            r2 = CategoryColorRegistry(reg_path)
            m2 = r2.assign(["高雄", "台北", "台中"], source="fig02")

            for city in ("台北", "台中", "高雄"):
                assert m1[city] == m2[city], f"{city} color drifted: {m1[city]} != {m2[city]}"
            assert len({m1["台北"], m1["台中"], m1["高雄"]}) == 3
    finally:
        _restore_palette(snap)


def test_2_na_and_other_do_not_consume_slots() -> None:
    snap = _snapshot_palette()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            reg = CategoryColorRegistry(Path(tmp) / REGISTRY_FILENAME)
            m = reg.assign([None, "NA", "其他", "其他項目合計", "台北", "台中"])
            assert m["NA"] == hce.GEPHI_DISCRETE_NEUTRALS["na_missing"]
            assert m["其他"] == hce.GEPHI_DISCRETE_NEUTRALS["other_aggregated"]
            assert m["其他項目合計"] == hce.GEPHI_DISCRETE_NEUTRALS["other_aggregated"]
            assert m["台北"] == hce.GEPHI_QUALITATIVE_HEX[0]
            assert m["台中"] == hce.GEPHI_QUALITATIVE_HEX[1]
            # Slots 2 and 3 must still be free
            m2 = reg.assign(["高雄", "台南"])
            assert m2["高雄"] == hce.GEPHI_QUALITATIVE_HEX[2]
            assert m2["台南"] == hce.GEPHI_QUALITATIVE_HEX[3]
    finally:
        _restore_palette(snap)


def test_3_fifth_entity_overflow() -> None:
    snap = _snapshot_palette()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            reg = CategoryColorRegistry(Path(tmp) / REGISTRY_FILENAME)
            reg.assign(["台北", "台中", "高雄", "台南"])
            raised = False
            try:
                reg.assign(["桃園"])
            except RegistryFullError as exc:
                raised = True
                assert isinstance(exc, ValueError)
            assert raised, "Expected RegistryFullError on 5th entity"

            m_other = reg.assign(["桃園"], overflow="other")
            assert m_other["桃園"] == hce.GEPHI_DISCRETE_NEUTRALS["other_aggregated"]
            assert reg.hex_for("桃園") is None
    finally:
        _restore_palette(snap)


def test_4_aliases_nfkc_and_pin_conflicts() -> None:
    snap = _snapshot_palette()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            reg = CategoryColorRegistry(Path(tmp) / REGISTRY_FILENAME)
            reg.assign(["台北"])
            reg.add_alias("臺北", "台北")
            m = reg.assign(["臺北"])
            assert m["臺北"] == reg.hex_for("台北")

            assert reg.normalize_key("ＡＢＣ") == reg.normalize_key("abc") == "abc"
            m_abc = reg.assign(["ＡＢＣ"])
            assert reg.hex_for("abc") == m_abc["ＡＢＣ"]

            # Pinning "高雄" to slot 0 (owned by "台北") must raise ValueError
            pin_failed = False
            try:
                reg.pin("高雄", 0)
            except ValueError:
                pin_failed = True
            assert pin_failed, "Expected ValueError when pinning to occupied slot"

            pinned_hex = reg.pin("高雄", 3)
            assert pinned_hex == hce.GEPHI_QUALITATIVE_HEX[3]
            assert reg.hex_for("高雄") == hce.GEPHI_QUALITATIVE_HEX[3]
    finally:
        _restore_palette(snap)


def test_5_palette_switch_preserves_slot_and_updates_hex() -> None:
    snap = _snapshot_palette()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            reg = CategoryColorRegistry(Path(tmp) / REGISTRY_FILENAME)
            reg.assign(["台北", "台中"])
            old_tp = reg.hex_for("台北")
            old_tc = reg.hex_for("台中")
            assert old_tp == hce.GEPHI_QUALITATIVE_HEX[0]
            assert old_tc == hce.GEPHI_QUALITATIVE_HEX[1]

            new_pal = hce.build_palette_from_primary_hexes(
                ["#112233", "#445566", "#778899", "#AABBCC"]
            )
            hce.activate_chart_palette(new_pal)

            assert reg.hex_for("台北") == "#112233"
            assert reg.hex_for("台中") == "#445566"
            assert reg.tint_for("台北") == hce.GEPHI_LIGHT_BADGE_TINTS[0]
    finally:
        _restore_palette(snap)


def test_6_bind_qualitative_colors_integration_and_fallback() -> None:
    snap = _snapshot_palette()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            use_session_registry(tmp)
            b1 = hce.bind_qualitative_colors(["台北", "台中", "高雄"])
            b2 = hce.bind_qualitative_colors(["高雄", "台北", "台中"])
            for k in ("台北", "台中", "高雄"):
                assert b1[k] == b2[k]

            clear_active_registry()
            # Without active registry, order-of-appearance governs assignment again
            u1 = hce.bind_qualitative_colors(["台北", "台中", "高雄"])
            u2 = hce.bind_qualitative_colors(["高雄", "台北", "台中"])
            assert u1["台北"] == hce.GEPHI_QUALITATIVE_HEX[0]
            assert u2["高雄"] == hce.GEPHI_QUALITATIVE_HEX[0]
    finally:
        _restore_palette(snap)


def test_7_export_js_and_verify_color_registry() -> None:
    snap = _snapshot_palette()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            s_dir = Path(tmp)
            reg = use_session_registry(s_dir)
            reg.assign(["台北", "台中"])
            reg.add_alias("臺北", "台北")

            js_out = s_dir / "02_outputs" / "dashboard" / "js" / "gephi_palette.js"
            hce.export_gephi_palette_js(str(js_out))
            js_text = js_out.read_text(encoding="utf-8")
            assert reg.hex_for("台北") in js_text
            assert '"台北"' in js_text
            assert '"臺北": "台北"' in js_text

            ok_rep = verify_color_registry(str(s_dir))
            assert ok_rep["passed"], f"Expected verify_color_registry to pass, got {ok_rep}"

            # Tamper with JS entityColors hex -> verification must fail
            tp_hex = reg.hex_for("台北")
            tampered = js_text.replace(f'"台北": "{tp_hex}"', '"台北": "#000001"', 1)
            assert tampered != js_text, "Expected entityColors replacement to modify JS text"
            js_out.write_text(tampered, encoding="utf-8")
            bad_rep = verify_color_registry(str(s_dir))
            assert not bad_rep["passed"], "Expected verify_color_registry to fail after JS edit"
    finally:
        _restore_palette(snap)


def test_8_plot_smoke_tests() -> None:
    snap = _snapshot_palette()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            reg = use_session_registry(tmp)
            # Pin specific slots so defaults [0]/[1] wouldn't accidentally match
            reg.pin("台北", 2)
            reg.pin("高雄", 3)
            reg.pin("台中", 1)

            # 1) plot_dumbbell
            fig, ax = plt.subplots(figsize=(8, 4))
            res_db = hce.plot_dumbbell(
                ax,
                ["A", "B"],
                [10.0, 20.0],
                [18.0, 28.0],
                label_start="台北",
                label_end="高雄",
            )
            c_start_actual = mcolors.to_hex(res_db["scatter_start"].get_facecolors()[0]).upper()
            c_end_actual = mcolors.to_hex(res_db["scatter_end"].get_facecolors()[0]).upper()
            assert c_start_actual == reg.hex_for("台北").upper()
            assert c_end_actual == reg.hex_for("高雄").upper()
            plt.close(fig)

            # 2) plot_marimekko (partially registered sub_labels)
            fig, ax = plt.subplots(figsize=(8, 4))
            res_mk = hce.plot_marimekko(
                ax,
                ["區1", "區2"],
                [60.0, 40.0],
                [[40.0, 60.0], [50.0, 50.0]],
                ["台北", "未登記子類"],
            )
            first_patch_hex = mcolors.to_hex(res_mk["patches"][0].get_facecolor()).upper()
            second_patch_hex = mcolors.to_hex(res_mk["patches"][1].get_facecolor()).upper()
            assert first_patch_hex == reg.hex_for("台北").upper()
            assert second_patch_hex != first_patch_hex
            # Unregistered label must NOT have been added to the registry
            assert reg.hex_for("未登記子類") is None
            plt.close(fig)

            # 3) plot_cleveland_dot
            fig, ax = plt.subplots(figsize=(8, 4))
            res_cd = hce.plot_cleveland_dot(
                ax,
                ["未登記中位", "台北", "台中"],
                [50.0, 10.0, 90.0],
                top_n=1,
                bottom_n=1,
            )
            facecolors = [mcolors.to_hex(c).upper() for c in res_cd["scatter"].get_facecolors()]
            # Sorted ascending: 台北 (10), 未登記中位 (50), 台中 (90)
            assert facecolors[0] == reg.hex_for("台北").upper()
            assert facecolors[1] == "#94A3B8"
            assert facecolors[2] == reg.hex_for("台中").upper()
            assert reg.hex_for("未登記中位") is None
            plt.close(fig)
    finally:
        _restore_palette(snap)


def main() -> int:
    tests = [
        test_1_order_independence,
        test_2_na_and_other_do_not_consume_slots,
        test_3_fifth_entity_overflow,
        test_4_aliases_nfkc_and_pin_conflicts,
        test_5_palette_switch_preserves_slot_and_updates_hex,
        test_6_bind_qualitative_colors_integration_and_fallback,
        test_7_export_js_and_verify_color_registry,
        test_8_plot_smoke_tests,
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
