"""
Safety-net test suite for the tree-structured Markdown architecture of
`deep-reading-and-visual-synthesis`.

Verifies:
1. Structural completeness of `shared/` and all 5 `formats/format_*` branches,
   and complete removal of obsolete `phase2_output/`.
2. Zero broken relative Markdown links across all active skill `.md` files and
   root `README.md`.
3. Zero stale references to removed `phase2_output/` / `layer2_advisor_` /
   `layer3_advisor_` / legacy spec filenames in active docs.
4. Strict UTF-8 byte-size redlines for trunk files (`SKILL.md`, `shared/router.md`,
   `shared/blueprint_template.md`, `shared/style_and_color_core.md`).
5. Core architectural invariants (trunk+branch blueprint, hybrid overrides,
   Subagent isolation + sequential fallback, self-sufficient diagram boundaries).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

TESTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = TESTS_DIR.parent
REPO_ROOT = SKILL_ROOT.parents[2]
ROOT_README = REPO_ROOT / "README.md"

MD_TOKEN_RE = re.compile(
    r"```.*?```"                                                # fenced code block (ignore)
    r"|`[^`\n]+`"                                               # inline literal code span (ignore)
    r"|!?\[(?:`[^`\n]+`|[^\]])*\]\(((?:[^()\s]|(?:\([^()\s]*\)))+(?:\s+\"[^\"]*\")?)\)",  # real markdown link/image (supports balanced parens in URL)
    re.DOTALL,
)

BACKTICK_SKILL_PATH_RE = re.compile(
    r"`((?:\.\./)?(?:formats/|format_[a-e]_|shared/|phase1_reading/|setup/|scripts/)[A-Za-z0-9_./-]+\.(?:md|py|js|json))`"
)

STALE_TOKENS = [
    "phase2_output/",
    "phase2_output_router.md",
    "layer2_advisor_",
    "layer3_advisor_",
    "visual_cognition_principles.md",
    "visual_diagram_matplotlib_spec.md",
    "document_report_spec.md",
    "medium_column_spec.md",
    "presentation_slide_spec.md",
    "quantitative_chart_spec.md",
    "data_dashboard_spec.md",
    "chart_family1_ranking_and_deviation.md",
    "chart_family2_trend_and_comparison.md",
    "chart_family3_composition_and_flow.md",
    "distribution_and_density_chart_spec.md",
    "chart_family5_multivariate_and_spatial.md",
    "Phase 2 三層決策",
    "Phase 2 三層生成藍圖",
    "Layer 3 Armory",
    "render_html_svg_to_png",
]

SIZE_REDLINES = {
    "SKILL.md": 8 * 1024,
    "shared/router.md": 8 * 1024,
    "shared/blueprint_template.md": 6 * 1024,
    "shared/style_and_color_core.md": 8 * 1024,
}


def _collect_active_md_files() -> list[Path]:
    md_files: list[Path] = []
    for p in sorted(SKILL_ROOT.rglob("*.md")):
        rel_parts = p.relative_to(SKILL_ROOT).parts
        # Exclude gitignored / user-local private style profiles
        if len(rel_parts) >= 2 and rel_parts[0] == "config" and rel_parts[1] in ("owner_styles", "user_styles"):
            continue
        md_files.append(p)
    if ROOT_README.exists():
        md_files.append(ROOT_README)
    return md_files


def _extract_markdown_link_targets(text: str) -> list[str]:
    targets: list[str] = []
    for match in MD_TOKEN_RE.finditer(text):
        raw = match.group(1)
        if raw is not None:
            targets.append(raw.strip())
    return targets


def test_1_structural_completeness() -> None:
    obsolete = SKILL_ROOT / "phase2_output"
    assert not obsolete.exists(), f"Obsolete directory still exists: {obsolete}"

    required_paths = [
        "SKILL.md",
        "THEORY_ARCHIVE.md",
        # Thin trunk shared/
        "shared/router.md",
        "shared/blueprint_template.md",
        "shared/style_and_color_core.md",
        "shared/visual_cognition_core.md",
        "shared/editorial_narrative_spec.md",
        "shared/creative_armory/INDEX.md",
        "shared/creative_armory/cases/01_texture_and_container/glass_liquid_bars.md",
        "shared/creative_armory/cases/01_texture_and_container/masked_texture_wedges.md",
        "shared/creative_armory/cases/01_texture_and_container/sprite_coord_scatter.md",
        "shared/creative_armory/cases/02_structural_geometry/.gitkeep",
        "shared/creative_armory/cases/03_spatial_and_thematic/diagram_spatial_metaphors.md",
        "shared/creative_armory/cases/03_spatial_and_thematic/thematic_palette_frame.md",
        # Format A
        "formats/format_a_diagram/01_plan.md",
        "formats/format_a_diagram/02_build.md",
        "formats/format_a_diagram/03_qa.md",
        # Format B
        "formats/format_b_document/01_plan.md",
        "formats/format_b_document/02_build_pdf.md",
        "formats/format_b_document/02_build_medium.md",
        "formats/format_b_document/03_qa.md",
        # Format C
        "formats/format_c_slides/01_plan.md",
        "formats/format_c_slides/02_build.md",
        "formats/format_c_slides/03_qa.md",
        # Format D + 5 families
        "formats/format_d_charts/01_plan.md",
        "formats/format_d_charts/02_build_core.md",
        "formats/format_d_charts/03_qa.md",
        "formats/format_d_charts/families/family1_ranking_and_deviation.md",
        "formats/format_d_charts/families/family2_trend_and_comparison.md",
        "formats/format_d_charts/families/family3_composition_and_flow.md",
        "formats/format_d_charts/families/family4_distribution_and_density.md",
        "formats/format_d_charts/families/family5_multivariate_and_spatial.md",
        # Format E
        "formats/format_e_dashboard/01_plan.md",
        "formats/format_e_dashboard/02_build.md",
        "formats/format_e_dashboard/03_qa.md",
    ]

    missing: list[str] = []
    empty: list[str] = []
    for rel in required_paths:
        p = SKILL_ROOT / rel
        if not p.is_file():
            missing.append(rel)
        elif p.stat().st_size == 0:
            empty.append(rel)

    assert not missing, f"Missing required architecture files: {missing}"
    assert not empty, f"Empty required architecture files: {empty}"


def test_2_zero_broken_relative_links() -> None:
    # Sanity-check link extractor distinguishes real links with code labels & balanced parens vs. inline code examples
    sample = "See [`real.md`](./real.md), [paren](dir/foo_(bar).md) and literal `![example](./fake.png)` plus [other](dir/b.md)."
    assert _extract_markdown_link_targets(sample) == ["./real.md", "dir/foo_(bar).md", "dir/b.md"]

    md_files = _collect_active_md_files()
    assert len(md_files) >= 30, f"Expected >= 30 active markdown files, found {len(md_files)}"

    broken: list[str] = []
    checked_links = 0
    for md_path in md_files:
        text = md_path.read_text(encoding="utf-8")
        for raw_target in _extract_markdown_link_targets(text):
            if not raw_target:
                continue
            # Strip optional markdown link title: path "title"
            target = raw_target.split()[0].strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "file://", "#")):
                continue
            if "<" in target or ">" in target:
                continue
            # Drop URL fragment (#section)
            rel_part = unquote(target.split("#", 1)[0])
            if not rel_part:
                continue
            checked_links += 1
            resolved = (md_path.parent / rel_part).resolve()
            if not resolved.exists():
                display_src = md_path.relative_to(REPO_ROOT)
                broken.append(f"{display_src} -> {raw_target} (resolved: {resolved})")

        # Also validate explicit backtick skill-internal file paths (catches truncated prefixes like `format_b_document/...`)
        stripped_fences = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for m in BACKTICK_SKILL_PATH_RE.finditer(stripped_fences):
            cand = m.group(1)
            if "*" in cand or "<" in cand:
                continue
            if not ((md_path.parent / cand).exists() or (SKILL_ROOT / cand).exists()):
                display_src = md_path.relative_to(REPO_ROOT)
                broken.append(f"{display_src} -> backtick `{cand}` does not resolve from file dir or SKILL_ROOT")

    assert checked_links >= 80, f"Expected >= 80 relative links checked, got {checked_links}"
    assert not broken, "Broken relative Markdown links or backtick paths found:\n  " + "\n  ".join(broken)


def test_3_zero_stale_references() -> None:
    md_files = _collect_active_md_files()
    script_files = [
        p
        for p in sorted((SKILL_ROOT / "scripts").rglob("*"))
        if p.is_file() and p.suffix in (".py", ".js") and "__pycache__" not in p.parts
    ]
    targets = md_files + script_files

    hits: list[str] = []
    for path in targets:
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for token in STALE_TOKENS:
                if token in line:
                    rel = path.relative_to(REPO_ROOT)
                    hits.append(f"{rel}:L{line_no} contains stale token '{token}'")

    assert not hits, "Stale legacy path or workflow references found:\n  " + "\n  ".join(hits)


def test_4_trunk_size_redlines() -> None:
    violations: list[str] = []
    for rel, max_bytes in SIZE_REDLINES.items():
        p = SKILL_ROOT / rel
        raw = p.read_bytes()
        size = len(raw)
        crlf_size = len(raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        if size > max_bytes or crlf_size > max_bytes:
            violations.append(f"{rel}: raw={size} B / crlf={crlf_size} B > limit {max_bytes} B")
    assert not violations, "Size redlines exceeded:\n  " + "\n  ".join(violations)


def test_5_architectural_invariants() -> None:
    router_text = (SKILL_ROOT / "shared" / "router.md").read_text(encoding="utf-8")
    assert "Subagent" in router_text, "shared/router.md must document Subagent isolation"
    assert "sequential_confirm" in router_text, "shared/router.md must document sequential fallback"
    assert "setup_a4_portrait_canvas" in router_text, "shared/router.md must document Format B A4 portrait self-sufficiency"
    assert "render_svg_to_png_300dpi" in router_text, "shared/router.md must document Format C Mode 3 Tier 3 SVG API"
    assert "02c_slide_spec_lock.json" in router_text, "shared/router.md Subagent packet must include 02c_slide_spec_lock.json for Format C"
    assert "formats/format_d_charts/02_build_core.md" in router_text, "shared/router.md Subagent packet must include Format D SSOT for Format E"
    assert "*_slide.png" in router_text, "shared/router.md Subagent packet must pass upstream Format D charts to Format B/C"

    p1_guide = (SKILL_ROOT / "phase1_reading" / "phase1_socratic_reading_guide.md").read_text(encoding="utf-8")
    assert "SKILL.md`](../SKILL.md) 第三節" not in p1_guide, "phase1_socratic_reading_guide.md must not reference removed SKILL.md section 3"

    bp_text = (SKILL_ROOT / "shared" / "blueprint_template.md").read_text(encoding="utf-8")
    for heading in (
        "## 0. 主幹全域錨點",
        "## Format D 分枝藍圖",
        "## Format A 分枝藍圖",
        "## Format B 分枝藍圖",
        "## Format C 分枝藍圖",
        "## Format E 分枝藍圖",
    ):
        assert heading in bp_text, f"shared/blueprint_template.md missing section: {heading}"

    style_core = (SKILL_ROOT / "shared" / "style_and_color_core.md").read_text(encoding="utf-8")
    format_c_plan = (SKILL_ROOT / "formats" / "format_c_slides" / "01_plan.md").read_text(encoding="utf-8")
    format_b_plan = (SKILL_ROOT / "formats" / "format_b_document" / "01_plan.md").read_text(encoding="utf-8")

    assert "Topic Art Direction DNA 卡（Format C 模式 3）" in format_c_plan, (
        "Format C Mode 3 DNA card must reside in formats/format_c_slides/01_plan.md"
    )
    assert "Topic Art Direction DNA 卡（Format C 模式 3）" not in style_core, (
        "Format C Mode 3 DNA card must be moved out of shared/style_and_color_core.md"
    )
    assert "clreq_kaiti" in format_b_plan and "modern_sans" in format_b_plan, (
        "Format B PDF font choice must reside in formats/format_b_document/01_plan.md"
    )


def main() -> int:
    tests = [
        test_1_structural_completeness,
        test_2_zero_broken_relative_links,
        test_3_zero_stale_references,
        test_4_trunk_size_redlines,
        test_5_architectural_invariants,
    ]
    passed = 0
    for fn in tests:
        try:
            fn()
            print(f"[PASS] {fn.__name__}")
            passed += 1
        except Exception as exc:
            print(f"[FAIL] {fn.__name__}: {exc}")
    print(f"\nSummary: {passed}/{len(tests)} passed.")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    raise SystemExit(main())
