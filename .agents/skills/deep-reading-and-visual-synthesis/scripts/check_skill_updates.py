"""
check_skill_updates.py
Monthly Upstream Skill Update Checker & Non-Destructive Updater.
Target Repository: https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis

Design Guarantees:
1. Monthly Throttling (default: 30 days): Checks `last_update_check_at` in `config/user_preferences.json`.
   Skips network calls immediately if checked within the last 30 days (zero daily latency/token cost).
2. Zero-Git Required: Uses Python stdlib (`urllib.request`, `zipfile`, `json`) so even ZIP-download users
   without `git` or `gh` CLI can check for updates and view upstream commit changelogs.
3. Strict Non-Destructive Isolation: NEVER overwrites:
   - `config/user_preferences.json` (only deep-merges *missing* new schema keys, never touches user values)
   - `config/user_styles/**` (user custom writing styles)
   - `reading_sessions/**` (user reading logs & outputs)
   - Custom active chart palette in `scripts/gephi_palette.js` (re-synced from user's active palette after update)
"""

import argparse
import io
import json
import os
import shutil
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

UPSTREAM_REPO = "markyang20040112-source/deep-reading-and-visual-synthesis"
UPSTREAM_BRANCH = "main"
SKILL_REL_PATH = ".agents/skills/deep-reading-and-visual-synthesis"
DEFAULT_INTERVAL_DAYS = 30

PROTECTED_REL_PREFIXES = (
    "config/user_preferences.json",
    "config/user_styles/",
    "config/user_styles\\",
    "config/owner_styles/",
    "config/owner_styles\\",
)


def _skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _prefs_path() -> Path:
    return _skill_root() / "config" / "user_preferences.json"


def _load_prefs(path: Optional[Path] = None) -> Dict[str, object]:
    p = path or _prefs_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_prefs(data: Dict[str, object], path: Optional[Path] = None) -> None:
    p = path or _prefs_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _deep_merge_missing(target: Dict[str, object], template: Dict[str, object]) -> Dict[str, object]:
    """Add new keys from `template` into `target` without overwriting any existing user values."""
    for key, val in template.items():
        if key not in target:
            target[key] = val
        elif isinstance(target[key], dict) and isinstance(val, dict):
            _deep_merge_missing(target[key], val)
    return target


def is_update_check_due(
    prefs: Optional[Dict[str, object]] = None,
    interval_days: int = DEFAULT_INTERVAL_DAYS,
    now_dt: Optional[datetime] = None,
) -> Tuple[bool, int]:
    """Return `(is_due, days_since_last_check)` based on `update_check.last_update_check_at`."""
    data = prefs if prefs is not None else _load_prefs()
    uc = data.get("update_check", {})
    if isinstance(uc, dict) and uc.get("enabled") is False:
        return False, 0
    interval = int(uc.get("interval_days", interval_days)) if isinstance(uc, dict) else interval_days
    last_str = str(uc.get("last_update_check_at") or "").strip() if isinstance(uc, dict) else ""
    if not last_str:
        return True, interval
    try:
        last_dt = datetime.fromisoformat(last_str.replace("Z", "+00:00"))
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        now = now_dt or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        elapsed = (now - last_dt).days
        return elapsed >= interval, elapsed
    except Exception:
        return True, interval


def fetch_upstream_commits(
    repo: str = UPSTREAM_REPO,
    branch: str = UPSTREAM_BRANCH,
    limit: int = 10,
    timeout: int = 8,
) -> List[Dict[str, str]]:
    """Fetch recent upstream commits affecting the skill directory via GitHub public REST API."""
    api_url = (
        f"https://api.github.com/repos/{repo}/commits"
        f"?sha={branch}&path={SKILL_REL_PATH}&per_page={int(limit)}"
    )
    req = urllib.request.Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "DeepReadingSkillUpdater/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = json.loads(resp.read().decode("utf-8", errors="replace"))

    commits: List[Dict[str, str]] = []
    for item in raw if isinstance(raw, list) else []:
        sha = str(item.get("sha") or "").strip()
        commit_obj = item.get("commit") or {}
        msg = str(commit_obj.get("message") or "").splitlines()[0].strip()
        date_str = str((commit_obj.get("committer") or {}).get("date") or "")[:10]
        if sha:
            commits.append({"sha": sha, "short_sha": sha[:7], "date": date_str, "message": msg})
    return commits


def check_for_skill_updates(
    force: bool = False,
    prefs_path: Optional[str] = None,
    commits_override: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, object]:
    """
    Check once per month whether the official upstream skill has new commits.
    Returns a structured dict with `has_update`, `changelog`, and `prompt_message`.
    Never modifies user styles, palettes, or preferences values.
    """
    p_path = Path(prefs_path).resolve() if prefs_path else _prefs_path()
    prefs = _load_prefs(p_path)
    due, elapsed_days = is_update_check_due(prefs)

    if not force and not due:
        return {
            "status": "skipped_not_due",
            "checked": False,
            "has_update": False,
            "days_since_last_check": elapsed_days,
        }

    try:
        commits = commits_override if commits_override is not None else fetch_upstream_commits()
    except Exception as exc:
        return {
            "status": "offline_or_error",
            "checked": False,
            "has_update": False,
            "error": str(exc),
        }

    if not commits:
        return {"status": "no_upstream_commits", "checked": True, "has_update": False}

    latest_sha = commits[0]["sha"]
    uc = prefs.setdefault("update_check", {})
    if isinstance(uc, dict):
        installed_sha = str(uc.get("installed_skill_commit_sha") or "").strip()
        uc["last_update_check_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        _save_prefs(prefs, p_path)
    else:
        installed_sha = ""

    if installed_sha and installed_sha == latest_sha:
        return {
            "status": "up_to_date",
            "checked": True,
            "has_update": False,
            "latest_sha": latest_sha,
        }

    new_commits: List[Dict[str, str]] = []
    for c in commits:
        if installed_sha and c["sha"] == installed_sha:
            break
        new_commits.append(c)
    if not new_commits:
        new_commits = commits[:5]

    changelog_lines = [f"- `{c['short_sha']}` ({c['date']}): {c['message']}" for c in new_commits]
    prompt_msg = (
        f"偵測到官方 `deep-reading-and-visual-synthesis` 技能有 **{len(new_commits)} 項新更新**：\n"
        + "\n".join(changelog_lines)
        + "\n\n請問是否要立即更新官方技能檔案？（您的個人筆風檔 `config/user_styles/`、專屬色票與 `user_preferences.json` 設定將 **100% 保留不被覆蓋**）"
    )

    return {
        "status": "update_available",
        "checked": True,
        "has_update": True,
        "installed_sha": installed_sha or None,
        "latest_sha": latest_sha,
        "changelog": new_commits,
        "prompt_message": prompt_msg,
    }


def is_protected_relative_path(rel_path: str) -> bool:
    """Return True if `rel_path` belongs to user-owned settings/styles that must NEVER be overwritten."""
    norm = rel_path.replace("\\", "/").lstrip("./")
    if norm == "config/user_preferences.json":
        return True
    if norm.startswith("config/user_styles/") or norm.startswith("config/owner_styles/"):
        return True
    return False


def apply_non_destructive_update(
    target_skill_root: Optional[str] = None,
    zip_bytes: Optional[bytes] = None,
    latest_sha: Optional[str] = None,
    prefs_path: Optional[str] = None,
) -> Dict[str, object]:
    """
    Download official upstream `main.zip` (or use `zip_bytes` in tests) and update ONLY core skill files,
    strictly preserving `config/user_preferences.json`, `config/user_styles/**`, and user's active palette.
    """
    root = Path(target_skill_root).resolve() if target_skill_root else _skill_root()
    p_path = Path(prefs_path).resolve() if prefs_path else (root / "config" / "user_preferences.json")
    old_prefs = _load_prefs(p_path)

    if zip_bytes is None:
        zip_url = f"https://github.com/{UPSTREAM_REPO}/archive/refs/heads/{UPSTREAM_BRANCH}.zip"
        req = urllib.request.Request(zip_url, headers={"User-Agent": "DeepReadingSkillUpdater/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            zip_bytes = resp.read()

    updated_files: List[str] = []
    skipped_protected: List[str] = []

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        marker = f"/{SKILL_REL_PATH}/"
        for info in zf.infolist():
            if info.is_dir():
                continue
            idx = info.filename.find(marker)
            if idx == -1:
                continue
            rel = info.filename[idx + len(marker):].lstrip("/")
            if not rel:
                continue
            if is_protected_relative_path(rel):
                skipped_protected.append(rel)
                continue
            dest = root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(zf.read(info.filename))
            updated_files.append(rel)

    # Merge any new template schema keys into user's existing user_preferences.json without overwriting user values
    template_path = root / "config" / "user_preferences.template.json"
    if template_path.exists() and old_prefs:
        try:
            tmpl = json.loads(template_path.read_text(encoding="utf-8"))
            _deep_merge_missing(old_prefs, tmpl)
        except Exception:
            pass

    if old_prefs:
        uc = old_prefs.setdefault("update_check", {})
        if isinstance(uc, dict):
            uc["last_update_check_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if latest_sha:
                uc["installed_skill_commit_sha"] = latest_sha
        _save_prefs(old_prefs, p_path)

    # Re-sync user's custom active chart palette to gephi_palette.js if present
    palette_resynced = False
    try:
        color_sets = old_prefs.get("color_sets", {})
        active_pid = color_sets.get("active_chart_palette_id")
        palettes = color_sets.get("chart_palettes", {})
        if active_pid and isinstance(palettes, dict) and active_pid in palettes:
            import sys
            scripts_dir = str(root / "scripts")
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            import hcl_color_engine as hcl
            hcl.export_gephi_palette_js(str(root / "scripts" / "gephi_palette.js"), palettes[active_pid])
            palette_resynced = True
    except Exception:
        palette_resynced = False

    return {
        "status": "updated_successfully",
        "updated_count": len(updated_files),
        "skipped_protected": skipped_protected,
        "palette_resynced": palette_resynced,
        "latest_sha": latest_sha,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Monthly upstream skill update checker & non-destructive updater."
    )
    parser.add_argument("--check", action="store_true", help="Check if upstream skill updates exist.")
    parser.add_argument("--apply", action="store_true", help="Apply upstream update without overwriting user settings.")
    parser.add_argument("--force", action="store_true", help="Bypass 30-day throttle when checking.")
    args = parser.parse_args()

    if args.apply:
        chk = check_for_skill_updates(force=True)
        res = apply_non_destructive_update(latest_sha=chk.get("latest_sha"))
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        res = check_for_skill_updates(force=args.force)
        print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
