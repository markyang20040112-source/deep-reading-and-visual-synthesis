"""
Unified test runner for all developer safety-net test suites under `tests/`.
Run with: python tests/run_all.py
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent

SUITES = [
    "test_color_registry.py",
    "test_charts_regression.py",
    "test_pdf_pipeline.py",
    "test_mindmap_and_ingest.py",
    "test_pptx_pipeline.py",
    "test_dashboard_bundle.py",
    "test_md_architecture.py",
]


def main() -> int:
    results: list[tuple[str, bool, float]] = []
    t_total_start = time.perf_counter()

    for name in SUITES:
        path = TESTS_DIR / name
        print(f"=== Running {name} ===")
        t0 = time.perf_counter()
        proc = subprocess.run([sys.executable, str(path)], check=False)
        dt = time.perf_counter() - t0
        ok = proc.returncode == 0
        results.append((name, ok, dt))
        print()

    total_dt = time.perf_counter() - t_total_start
    passed = sum(1 for _, ok, _ in results if ok)
    print("================ TEST SUITE SUMMARY ================")
    for name, ok, dt in results:
        tag = "PASS" if ok else "FAIL"
        print(f"  [{tag}] {name:<30s} ({dt:.2f}s)")
    print(f"Total: {passed}/{len(results)} suites passed in {total_dt:.2f}s.")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
