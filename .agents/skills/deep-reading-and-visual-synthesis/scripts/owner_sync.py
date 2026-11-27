"""
owner_sync.py
Owner identity verification and private reading-session/config vault synchronization.
Note: `hcl_color_engine` is the public entry point.
"""

from typing import Dict, List, Optional

OWNER_GITHUB_ID = "markyang20040112-source"


OWNER_PRIVATE_REPO_URL = "https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis-Private-.git"


def ensure_owner_private_assets(
    pull_remote: bool = False,
    push_remote: bool = False,
    commit_msg: str = "chore(sync): sync owner sessions and private config",
) -> Dict[str, object]:
    """
    Sync owner private vault (`reading_sessions/` + `_owner_private_config/`) with the
    private GitHub repository and mirror `user_preferences.json` / `owner_styles/*.md`
    to `.agents/skills/deep-reading-and-visual-synthesis/config/` (ignored by the Public repo).
    """
    import shutil
    import subprocess
    from pathlib import Path

    skill_root = Path(__file__).resolve().parents[1]
    workspace_root = skill_root.parents[2] if len(skill_root.parents) >= 3 else skill_root.parent
    sessions_dir = workspace_root / "reading_sessions"
    private_cfg_dir = sessions_dir / "_owner_private_config"
    cfg_dir = skill_root / "config"

    actions: List[str] = []
    errors: List[str] = []

    def _run_git(args: List[str], cwd: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )

    cfg_dir.mkdir(parents=True, exist_ok=True)
    priv_prefs = private_cfg_dir / "user_preferences.json"
    cfg_prefs = cfg_dir / "user_preferences.json"
    priv_styles = private_cfg_dir / "owner_styles"
    cfg_styles = cfg_dir / "owner_styles"
    cfg_styles.mkdir(parents=True, exist_ok=True)

    def _restore_priv_to_cfg(overwrite: bool = False) -> None:
        if priv_prefs.exists() and (not cfg_prefs.exists() or (overwrite and cfg_prefs.read_bytes() != priv_prefs.read_bytes())):
            shutil.copy2(priv_prefs, cfg_prefs)
            actions.append("restored_user_preferences")
        if priv_styles.exists():
            for src_md in priv_styles.glob("*.md"):
                dst_md = cfg_styles / src_md.name
                if not dst_md.exists() or (overwrite and dst_md.read_bytes() != src_md.read_bytes()):
                    shutil.copy2(src_md, dst_md)
                    actions.append(f"restored_style:{src_md.name}")

    def _backup_cfg_to_priv(only_missing: bool = False) -> None:
        if cfg_prefs.exists():
            private_cfg_dir.mkdir(parents=True, exist_ok=True)
            if not priv_prefs.exists() or (not only_missing and cfg_prefs.read_bytes() != priv_prefs.read_bytes()):
                shutil.copy2(cfg_prefs, priv_prefs)
                actions.append("backed_up_user_preferences_to_vault")
        if cfg_styles.exists():
            priv_styles.mkdir(parents=True, exist_ok=True)
            for src_md in cfg_styles.glob("*.md"):
                dst_md = priv_styles / src_md.name
                if not dst_md.exists() or (not only_missing and src_md.read_bytes() != dst_md.read_bytes()):
                    shutil.copy2(src_md, dst_md)
                    actions.append(f"backed_up_style:{src_md.name}")

    def _init_or_clone_sessions_git(allow_checkout: bool = True) -> None:
        if (sessions_dir / ".git").exists():
            return
        if not sessions_dir.exists() or not any(sessions_dir.iterdir()):
            sessions_dir.parent.mkdir(parents=True, exist_ok=True)
            if sessions_dir.exists():
                sessions_dir.rmdir()
            res = _run_git(["clone", OWNER_PRIVATE_REPO_URL, str(sessions_dir)], workspace_root)
            if res.returncode == 0:
                actions.append("cloned_private_repo")
            else:
                errors.append(f"clone failed: {(res.stderr or res.stdout).strip()}")
        else:
            _run_git(["init"], sessions_dir)
            _run_git(["branch", "-M", "main"], sessions_dir)
            _run_git(["remote", "add", "origin", OWNER_PRIVATE_REPO_URL], sessions_dir)
            res_fetch = _run_git(["fetch", "origin", "main"], sessions_dir)
            if res_fetch.returncode == 0:
                _run_git(["reset", "--mixed", "origin/main"], sessions_dir)
                if allow_checkout:
                    _run_git(["checkout", "--", "."], sessions_dir)
                actions.append("initialized_and_pulled_private_repo")
            else:
                errors.append(f"fetch failed: {(res_fetch.stderr or res_fetch.stdout).strip()}")

    need_remote_bootstrap = not cfg_prefs.exists() and not priv_prefs.exists()

    if push_remote:
        # Sync/push workflow: backup local config/ -> vault FIRST, commit, then pull --rebase, then push.
        if pull_remote or need_remote_bootstrap:
            _init_or_clone_sessions_git(allow_checkout=False)
        _restore_priv_to_cfg(overwrite=False)
        _backup_cfg_to_priv(only_missing=False)

        if (sessions_dir / ".git").exists():
            _run_git(["add", "-A"], sessions_dir)
            st = _run_git(["status", "--porcelain"], sessions_dir)
            if (st.stdout or "").strip():
                c_res = _run_git(["commit", "-m", commit_msg], sessions_dir)
                if c_res.returncode == 0:
                    actions.append("committed_private_vault")
                else:
                    errors.append(f"commit failed: {(c_res.stderr or c_res.stdout).strip()}")

            if pull_remote:
                res_ls = _run_git(["ls-remote", "--heads", "origin", "main"], sessions_dir)
                if res_ls.returncode != 0:
                    errors.append(f"pull failed: {(res_ls.stderr or res_ls.stdout).strip()}")
                elif (res_ls.stdout or "").strip():
                    res_pull = _run_git(["pull", "--rebase", "--autostash", "origin", "main"], sessions_dir)
                    if res_pull.returncode == 0:
                        actions.append("pulled_private_repo")
                        _restore_priv_to_cfg(overwrite=True)
                    else:
                        errors.append(f"pull failed: {(res_pull.stderr or res_pull.stdout).strip()}")

            if not errors:
                p_res = _run_git(["push", "-u", "origin", "main"], sessions_dir)
                if p_res.returncode == 0:
                    actions.append("pushed_private_repo")
                else:
                    errors.append(f"push failed: {(p_res.stderr or p_res.stdout).strip()}")
    else:
        if pull_remote or need_remote_bootstrap:
            if not (sessions_dir / ".git").exists():
                _init_or_clone_sessions_git(allow_checkout=True)
            else:
                res_pull = _run_git(["pull", "--rebase", "--autostash", "origin", "main"], sessions_dir)
                if res_pull.returncode == 0:
                    actions.append("pulled_private_repo")
                else:
                    errors.append(f"pull failed: {(res_pull.stderr or res_pull.stdout).strip()}")

        if pull_remote:
            _restore_priv_to_cfg(overwrite=True)
            _backup_cfg_to_priv(only_missing=True)
        else:
            _restore_priv_to_cfg(overwrite=False)
            _backup_cfg_to_priv(only_missing=False)

    return {
        "ok": len(errors) == 0,
        "sessions_dir": str(sessions_dir),
        "private_cfg_dir": str(private_cfg_dir),
        "actions": actions,
        "errors": errors,
    }


def _detect_local_git_user(repo_dir: Optional[str] = None) -> str:
    """Detect current Git user identity via env override, git config user.name, or user.email."""
    import os
    import subprocess
    from pathlib import Path

    env_user = os.environ.get("DEEP_READING_GIT_USER")
    if env_user is not None:
        return env_user.strip()

    cwd = str(Path(repo_dir).resolve()) if repo_dir else str(Path(__file__).resolve().parents[1])
    for cmd in (["git", "config", "user.name"], ["git", "config", "user.email"]):
        try:
            res = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=3,
                check=False,
            )
            val = (res.stdout or "").strip()
            if val:
                if "@" in val:
                    val = val.split("@", 1)[0].strip()
                return val
        except Exception:
            continue
    return ""


def _detect_local_os_user() -> str:
    """Detect current OS login username for Git-less external user persistence."""
    import getpass
    import os
    env_override = os.environ.get("DEEP_READING_LOCAL_USER")
    if env_override is not None:
        return env_override.strip()
    try:
        return (getpass.getuser() or "").strip()
    except Exception:
        return (os.environ.get("USERNAME") or os.environ.get("USER") or "").strip()


def _is_gh_owner_authenticated() -> bool:
    """Return True if GitHub CLI (`gh`) is logged in as OWNER_GITHUB_ID."""
    import shutil
    import subprocess
    if not shutil.which("gh"):
        return False
    try:
        res = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=4,
            check=False,
        )
        return res.returncode == 0 and res.stdout.strip().lower() == OWNER_GITHUB_ID.lower()
    except Exception:
        return False


def check_user_identity_and_load_prefs(
    prefs_path: Optional[str] = None,
    override_git_user: Optional[str] = None,
    allow_workspace_fallback: bool = True,
    override_local_user: Optional[str] = None,
) -> Dict[str, object]:
    """
    Verify local Git / OS user identity and load `config/user_preferences.json`.
    - Owner Dual-Device Seamless Sync: Verified via local Git identity (`markyang20040112-source`),
      authenticated `gh` CLI login, or private home-directory marker `~/.deep_reading_owner_verified`
      (never by public repo files like `reading_sessions/` alone, preventing clone false-positives).
    - Strict External User Isolation: Strips and isolates all `owner_only: true` palettes and
      `available_owner_styles` for non-owners. Supports both Git-bound (`bound_git_user`) and
      Git-less local OS-bound (`bound_local_user`) persistence once onboarding is completed.
    """
    import copy
    import json
    from pathlib import Path

    skill_root = Path(__file__).resolve().parents[1]
    workspace_root = skill_root.parents[2] if len(skill_root.parents) >= 3 else skill_root.parent
    cfg_dir = skill_root / "config"
    target_prefs = Path(prefs_path).resolve() if prefs_path else (cfg_dir / "user_preferences.json")
    template_prefs = cfg_dir / "user_preferences.template.json"

    if target_prefs.exists():
        raw_prefs = json.loads(target_prefs.read_text(encoding="utf-8"))
    elif template_prefs.exists():
        raw_prefs = json.loads(template_prefs.read_text(encoding="utf-8"))
    else:
        raw_prefs = {}

    detected_user = (
        override_git_user.strip()
        if override_git_user is not None
        else _detect_local_git_user(str(workspace_root))
    )
    detected_local_user = (
        override_local_user.strip()
        if override_local_user is not None
        else _detect_local_os_user()
    )

    bound_user = str(raw_prefs.get("bound_git_user") or "").strip()
    bound_local_user = str(raw_prefs.get("bound_local_user") or "").strip()
    is_owner = False

    if detected_user.lower() == OWNER_GITHUB_ID.lower():
        is_owner = True
    elif not detected_user and allow_workspace_fallback and override_git_user is None:
        owner_marker = Path.home() / ".deep_reading_owner_verified"
        if owner_marker.exists() or _is_gh_owner_authenticated():
            is_owner = True

    if is_owner:
        if prefs_path is None and (not target_prefs.exists() or not (cfg_dir / "owner_styles").exists()):
            ensure_owner_private_assets(pull_remote=True)
            if target_prefs.exists():
                raw_prefs = json.loads(target_prefs.read_text(encoding="utf-8"))
        effective = copy.deepcopy(raw_prefs)
        effective["is_owner"] = True
        effective["isolated_external_user"] = False
        effective["detected_git_user"] = detected_user or OWNER_GITHUB_ID
        effective["detected_local_user"] = detected_local_user
        effective["onboarding_completed"] = True
        return effective

    # External user path: check if external user already completed onboarding (via Git OR local OS identity)
    git_matched = bool(
        detected_user
        and bound_user
        and detected_user.lower() == bound_user.lower()
        and bound_user.lower() != OWNER_GITHUB_ID.lower()
    )
    local_matched = bool(
        not detected_user
        and detected_local_user
        and bound_local_user
        and detected_local_user.lower() == bound_local_user.lower()
        and bound_user.lower() != OWNER_GITHUB_ID.lower()
    )

    if (git_matched or local_matched) and bool(raw_prefs.get("onboarding_completed", False)):
        effective = copy.deepcopy(raw_prefs)
        # Still ensure owner_only items remain isolated
        palettes = effective.get("color_sets", {}).get("chart_palettes", {})
        effective.setdefault("color_sets", {})["chart_palettes"] = {
            k: v for k, v in palettes.items() if not v.get("owner_only", False)
        }
        effective.setdefault("writing_styles", {})["available_owner_styles"] = []
        effective["is_owner"] = False
        effective["isolated_external_user"] = False
        effective["detected_git_user"] = detected_user
        effective["detected_local_user"] = detected_local_user
        return effective

    # External uninitialized user: strictly isolate all owner_only assets and force onboarding
    if template_prefs.exists():
        effective = json.loads(template_prefs.read_text(encoding="utf-8"))
    else:
        effective = copy.deepcopy(raw_prefs)

    palettes = effective.get("color_sets", {}).get("chart_palettes", {})
    effective.setdefault("color_sets", {})["chart_palettes"] = {
        k: v for k, v in palettes.items() if not v.get("owner_only", False)
    }
    effective["color_sets"]["active_chart_palette_id"] = None
    effective.setdefault("writing_styles", {})["available_owner_styles"] = []
    effective["writing_styles"]["active_style_id"] = None
    effective["bound_git_user"] = detected_user or None
    effective["bound_local_user"] = detected_local_user or None
    effective["is_owner"] = False
    effective["isolated_external_user"] = True
    effective["detected_git_user"] = detected_user
    effective["detected_local_user"] = detected_local_user
    effective["onboarding_completed"] = False
    return effective


def main() -> None:
    from color_core import GEPHI_QUALITATIVE_HEX

    import argparse
    import json
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="HCL Color Science Engine & Owner Private Vault Sync CLI."
    )
    parser.add_argument(
        "--restore-private",
        action="store_true",
        help="Pull owner Private repo into reading_sessions/ and restore user_preferences.json & owner_styles/.",
    )
    parser.add_argument(
        "--sync-private",
        action="store_true",
        help="Pull latest Private repo, sync local owner configs into _owner_private_config/, commit and push to Private repo.",
    )
    parser.add_argument(
        "--message",
        "-m",
        type=str,
        default="chore(sync): sync owner sessions and private config",
        help="Commit message used with --sync-private.",
    )
    args = parser.parse_args()

    if args.sync_private:
        res = ensure_owner_private_assets(pull_remote=True, push_remote=True, commit_msg=args.message)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res.get("ok") else 1)
    elif args.restore_private:
        res = ensure_owner_private_assets(pull_remote=True, push_remote=False)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0 if res.get("ok") else 1)
    else:
        prefs = check_user_identity_and_load_prefs()
        print(json.dumps({
            "is_owner": prefs.get("is_owner"),
            "detected_git_user": prefs.get("detected_git_user"),
            "active_qualitative_hex": GEPHI_QUALITATIVE_HEX,
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
