"""
report_skill_feedback.py
Cross-User Skill Evolution & Feedback Auto-Reporter (3-Channel Engine).
Locked Target Repository: https://github.com/markyang20040112-source/deep-reading-and-visual-synthesis

Provides Three-Channel Reporting for `_pending_skill_inspirations.md` during Step E1 / Step E3:
- Channel A (Authenticated CLI): Detects authenticated `gh` CLI (`gh auth status`) and creates an issue directly via
  `gh issue create --repo markyang20040112-source/deep-reading-and-visual-synthesis`.
- Channel B (Anonymous Google Apps Script Webhook): Sends a structured JSON POST to the author's deployed
  Apps Script Web App endpoint (exposes zero GitHub tokens and zero author email addresses in the repo),
  which automatically creates the GitHub Issue and notifies the author privately.
- Channel C (Zero-Auth Browser Fallback): Generates a URL-encoded pre-filled GitHub Issue creation link
  and optionally opens it in the user's default web browser if both Channel A and B are unavailable.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

UPSTREAM_REPO = "markyang20040112-source/deep-reading-and-visual-synthesis"
UPSTREAM_ISSUES_NEW_URL = f"https://github.com/{UPSTREAM_REPO}/issues/new"
DEFAULT_FEEDBACK_WEBHOOK_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwmiB6apvEF6Cqfg0ydxvut98XerhQXAdwukwgP4mnY_pSz3HnJYyjOfNKa5k1oLLJW-A/exec"
)

CATEGORY_CODES: Dict[str, str] = {
    "FR-FLOW": "引導流程與互動",
    "FR-VIS": "視覺設計與圖表排版",
    "FR-STYLE": "筆風與色彩引擎",
    "FR-CODE": "底層引擎與工程除錯",
    "FR-DOC": "技能文件與結構",
    "FR-BUG": "異常與防呆缺口",
}


def _load_webhook_url_from_prefs() -> str:
    """Read feedback_webhook_url from config/user_preferences.json (or template), falling back to default."""
    env_url = os.environ.get("DEEP_READING_FEEDBACK_WEBHOOK")
    if env_url is not None and env_url.strip():
        return env_url.strip()
    cfg_dir = Path(__file__).resolve().parents[1] / "config"
    for fname in ("user_preferences.json", "user_preferences.template.json"):
        fpath = cfg_dir / fname
        if fpath.exists():
            try:
                data = json.loads(fpath.read_text(encoding="utf-8"))
                url = str(data.get("git_and_feedback", {}).get("feedback_webhook_url") or "").strip()
                if url:
                    return url
            except Exception:
                pass
    return DEFAULT_FEEDBACK_WEBHOOK_URL


def is_gh_cli_authenticated() -> bool:
    """Return True if GitHub CLI (`gh`) is installed and logged in."""
    if not shutil.which("gh"):
        return False
    try:
        res = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
        )
        return res.returncode == 0
    except Exception:
        return False


def _get_git_credential_github_token() -> Optional[str]:
    """Retrieve local Git Credential Manager OAuth token for github.com if available (non-interactive)."""
    if not shutil.which("git"):
        return None
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    try:
        res = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=4,
            env=env,
            check=False,
        )
        if res.returncode != 0:
            return None
        creds = dict(
            line.split("=", 1)
            for line in (res.stdout or "").splitlines()
            if "=" in line
        )
        token = creds.get("password", "").strip()
        return token or None
    except Exception:
        return None


def _submit_via_github_rest_api(
    token: str,
    repo: str,
    title: str,
    body: str,
    labels: Optional[List[str]] = None,
    timeout: int = 15,
) -> Dict[str, object]:
    """Create a GitHub Issue directly via GitHub REST API using local Git credential token."""
    clean_repo = str(repo or UPSTREAM_REPO).strip().strip("/")
    api_url = f"https://api.github.com/repos/{clean_repo}/issues"
    payload_dict: Dict[str, object] = {"title": title, "body": body}
    if labels:
        payload_dict["labels"] = [str(l).strip() for l in labels if str(l).strip()]
    payload = json.dumps(payload_dict).encode("utf-8")
    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "DeepReadingFeedbackReporter/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw_resp = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw_resp or "{}")


def build_prefilled_issue_url(
    title: str,
    body: str,
    labels: Optional[List[str]] = None,
    repo: str = UPSTREAM_REPO,
) -> str:
    """Construct a pre-filled GitHub Issue URL with safe length truncation for browser compatibility."""
    clean_repo = str(repo or UPSTREAM_REPO).strip().strip("/")
    base_url = f"https://github.com/{clean_repo}/issues/new"
    safe_body = str(body or "").strip()
    if len(safe_body) > 6000:
        safe_body = safe_body[:5950] + "\n\n...(truncated for URL length limit)..."

    params: Dict[str, str] = {
        "title": str(title or "[FR-FLOW] Empirical Skill Inspiration").strip(),
        "body": safe_body,
    }
    if labels:
        params["labels"] = ",".join(str(l).strip() for l in labels if str(l).strip())

    return f"{base_url}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"


def _detect_local_git_user() -> str:
    """Detect local Git user name (or DEEP_READING_GIT_USER override) for environment tagging."""
    env_override = os.environ.get("DEEP_READING_GIT_USER")
    if env_override is not None:
        return env_override.strip()
    try:
        res = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return ""


def normalize_category_code(category_code: str = "FR-FLOW", raw_text: str = "") -> str:
    """Resolve and validate a canonical `[FR-*]` category code."""
    c = str(category_code or "").strip().upper()
    if c in CATEGORY_CODES:
        return c
    low = (raw_text or "").lower()
    if any(k in low for k in ("bug", "error", "traceback", "exception", "失敗", "報錯")):
        return "FR-BUG"
    if any(k in low for k in ("palette", "hex", "cielab", "筆風", "slot", "style", "色票")):
        return "FR-STYLE"
    if any(k in low for k in ("chart", "plot", "kde", "pptx", "pdf", "mindmap", "圖表", "排版")):
        return "FR-VIS"
    if any(k in low for k in ("script", ".py", ".js", "pip", "install", "環境", "套件")):
        return "FR-CODE"
    if any(k in low for k in ("spec", "skill.md", "doc", "文件", "說明")):
        return "FR-DOC"
    return "FR-FLOW"


def _extract_first_summary(raw_text: str, max_len: int = 36) -> str:
    """Extract a clean one-line summary from raw inspiration markdown."""
    for line in str(raw_text or "").splitlines():
        s = re.sub(r"^[#>*\-\d.\s`]+", "", line).strip()
        if s:
            if "|" in s:
                parts = [p.strip() for p in s.split("|") if p.strip()]
                s = parts[-1] if parts else s
            return s[:max_len] + ("..." if len(s) > max_len else "")
    return "實證優化靈感回報"


def format_issue_title(
    summary: Optional[str] = None,
    category_code: str = "FR-FLOW",
    raw_inspirations_text: str = "",
    reporter_git_user: str = "",
) -> str:
    """Build a strictly coded issue title: `[FR-<CODE>] <Summary> (<env>)`."""
    code = normalize_category_code(category_code, raw_inspirations_text)
    core = (summary or "").strip() or _extract_first_summary(raw_inspirations_text)
    user_tag = reporter_git_user.strip() or _detect_local_git_user() or "external-user"
    return f"[{code}] {core} ({user_tag})"


def format_issue_markdown_body(
    raw_inspirations_text: str,
    reporter_git_user: str = "",
    category_code: str = "FR-FLOW",
    target_files: str = "（見下方內容）",
    summary: Optional[str] = None,
) -> str:
    """Wrap raw `_pending_skill_inspirations.md` content into a structured, scannable Issue Markdown body."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    user_tag = reporter_git_user.strip() or _detect_local_git_user() or "anonymous-skill-user"
    code = normalize_category_code(category_code, raw_inspirations_text)
    code_desc = CATEGORY_CODES.get(code, "引導流程與互動")
    core = (summary or "").strip() or _extract_first_summary(raw_inspirations_text)

    return (
        f"## [{code}] {core}\n\n"
        "| 欄位 | 內容 |\n"
        "| :--- | :--- |\n"
        f"| **類別代號** | `{code}`（{code_desc}） |\n"
        f"| **影響檔案** | `{target_files}` |\n"
        f"| **回報環境識別** | `{user_tag}` |\n"
        f"| **回報時間** | `{timestamp}` |\n"
        f"| **目標上游倉庫** | `https://github.com/{UPSTREAM_REPO}` |\n\n"
        "---\n\n"
        "### 1. 觀察到的痛點與捕獲靈感清單（Observed Pain Point & Inspirations）\n\n"
        f"{raw_inspirations_text.strip()}\n\n"
        "### 2. 建議處置（Suggested Next Action）\n\n"
        "- [ ] 查證實證文獻或技術可行性並評估納入下個版本。\n"
    )


def _submit_via_webhook(
    webhook_url: str,
    category_code: str,
    title: str,
    body: str,
    timeout: int = 15,
) -> Dict[str, object]:
    """POST structured feedback JSON to the author's Google Apps Script Web App."""
    payload = json.dumps({
        "skill_id": "deep-reading-and-visual-synthesis",
        "category_code": category_code,
        "title": title,
        "body": body,
    }).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw_resp = resp.read().decode("utf-8", errors="replace")
    parsed = json.loads(raw_resp or "{}")
    if not parsed.get("ok"):
        raise RuntimeError(parsed.get("error") or "Webhook returned ok=false")
    return parsed


def report_inspirations_to_github_issue(
    inspirations_path_or_text: str,
    title: Optional[str] = None,
    labels: Optional[List[str]] = None,
    open_browser_fallback: bool = True,
    dry_run: bool = False,
    repo: str = UPSTREAM_REPO,
    reporter_git_user: str = "",
    category_code: str = "FR-FLOW",
    summary: Optional[str] = None,
    target_files: str = "（見下方內容）",
    webhook_url: Optional[str] = None,
    preferred_channel: str = "auto",
) -> Dict[str, object]:
    """
    Submit skill optimization inspirations to `markyang20040112-source/deep-reading-and-visual-synthesis` Issues.
    1. Reads `_pending_skill_inspirations.md` (if path exists) or treats input as raw Markdown text.
    2. Formats a standardized `[FR-*]` title and structured Markdown body.
    3. Channel A: `gh issue create` (if `gh` CLI is authenticated) or direct GitHub REST API via local
       `git credential fill` OAuth token (when `git` is logged into GitHub).
    4. Channel B: Anonymous Google Apps Script Webhook POST (zero-auth, hides author email & token).
    5. Channel C: Pre-filled GitHub Issue URL + `webbrowser.open` fallback.
    """
    p = Path(inspirations_path_or_text) if "\n" not in inspirations_path_or_text and len(inspirations_path_or_text) < 260 else None
    if p is not None and p.exists() and p.is_file():
        raw_text = p.read_text(encoding="utf-8")
    else:
        raw_text = str(inspirations_path_or_text or "").strip()

    if not raw_text:
        raise ValueError("Inspiration content is empty; nothing to report.")

    resolved_code = normalize_category_code(category_code, raw_text)
    issue_title = title or format_issue_title(
        summary=summary,
        category_code=resolved_code,
        raw_inspirations_text=raw_text,
        reporter_git_user=reporter_git_user,
    )
    issue_body = format_issue_markdown_body(
        raw_text,
        reporter_git_user=reporter_git_user,
        category_code=resolved_code,
        target_files=target_files,
        summary=summary,
    )
    resolved_webhook = webhook_url if webhook_url is not None else _load_webhook_url_from_prefs()
    effective_labels = (
        [str(l).strip() for l in labels if str(l).strip()]
        if labels is not None
        else ["skill-feedback", resolved_code]
    )
    prefilled_url = build_prefilled_issue_url(issue_title, issue_body, labels=effective_labels, repo=repo)
    ch_mode = str(preferred_channel or "auto").strip().lower()

    if dry_run:
        return {
            "status": "dry_run",
            "channel": "none",
            "repo": repo,
            "category_code": resolved_code,
            "labels": effective_labels,
            "title": issue_title,
            "webhook_configured": bool(resolved_webhook),
            "prefilled_url": prefilled_url,
            "body_preview": issue_body[:600],
        }

    # Channel A: Authenticated GitHub CLI (`gh issue create`) OR Local Git Credential Manager OAuth token
    if ch_mode in ("auto", "a", "channel_a"):
        if is_gh_cli_authenticated():
            cmd = [
                "gh", "issue", "create",
                "--repo", repo,
                "--title", issue_title,
                "--body", issue_body,
            ]
            try:
                res = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=20,
                    check=False,
                )
                if res.returncode == 0:
                    created_url = (res.stdout or "").strip().splitlines()[-1].strip()
                    return {
                        "status": "created_via_gh_cli",
                        "channel": "Channel_A_gh_cli",
                        "auth_method": "gh_cli",
                        "repo": repo,
                        "category_code": resolved_code,
                        "title": issue_title,
                        "issue_url": created_url,
                        "prefilled_url": prefilled_url,
                    }
            except Exception:
                pass

        git_token = _get_git_credential_github_token()
        if git_token:
            try:
                gh_res = _submit_via_github_rest_api(
                    git_token,
                    repo=repo,
                    title=issue_title,
                    body=issue_body,
                    labels=effective_labels,
                )
                created_url = str(gh_res.get("html_url") or "").strip()
                if created_url:
                    return {
                        "status": "created_via_gh_cli",
                        "channel": "Channel_A_gh_cli",
                        "auth_method": "git_credential_manager",
                        "repo": repo,
                        "category_code": resolved_code,
                        "labels": effective_labels,
                        "title": issue_title,
                        "issue_number": gh_res.get("number"),
                        "issue_url": created_url,
                        "prefilled_url": prefilled_url,
                    }
            except Exception:
                pass

    # Channel B: Anonymous Google Apps Script Webhook (zero-auth, hides email & token)
    webhook_error = None
    if ch_mode in ("auto", "b", "channel_b") and resolved_webhook:
        try:
            wh_res = _submit_via_webhook(
                resolved_webhook,
                category_code=resolved_code,
                title=issue_title,
                body=issue_body,
            )
            return {
                "status": "created_via_webhook",
                "channel": "Channel_B_apps_script_webhook",
                "repo": repo,
                "category_code": resolved_code,
                "title": issue_title,
                "issue_number": wh_res.get("issue_number"),
                "issue_url": wh_res.get("issue_url"),
            }
        except Exception as wh_err:
            webhook_error = str(wh_err)

    # Channel C: Pre-filled GitHub Issue URL + Browser launch fallback
    browser_opened = False
    if open_browser_fallback:
        try:
            browser_opened = bool(webbrowser.open(prefilled_url))
        except Exception:
            browser_opened = False

    result: Dict[str, object] = {
        "status": "fallback_prefilled_url",
        "channel": "Channel_C_browser_url",
        "repo": repo,
        "category_code": resolved_code,
        "title": issue_title,
        "browser_opened": browser_opened,
        "prefilled_url": prefilled_url,
    }
    if webhook_error:
        result["webhook_error"] = webhook_error
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report skill optimization inspirations to markyang20040112-source/deep-reading-and-visual-synthesis GitHub Issues."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="reading_sessions/_pending_skill_inspirations.md",
        help="Path to _pending_skill_inspirations.md or raw markdown string.",
    )
    parser.add_argument("--title", default=None, help="Custom GitHub Issue title.")
    parser.add_argument(
        "--category",
        default="FR-FLOW",
        choices=list(CATEGORY_CODES.keys()),
        help="Structured category code for the issue title.",
    )
    parser.add_argument("--summary", default=None, help="Short one-line summary for [FR-*] title.")
    parser.add_argument("--files", default="（見下方內容）", help="Affected skill files.")
    parser.add_argument(
        "--channel",
        default="auto",
        choices=["auto", "a", "b", "c"],
        help="Preferred reporting channel: auto (A->B->C), a (Channel A), b (Channel B), c (Channel C).",
    )
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-open browser on Channel C fallback.")
    parser.add_argument("--dry-run", action="store_true", help="Preview formatted title/body without sending.")
    args = parser.parse_args()

    result = report_inspirations_to_github_issue(
        args.input,
        title=args.title,
        open_browser_fallback=not args.no_browser,
        dry_run=args.dry_run,
        category_code=args.category,
        summary=args.summary,
        target_files=args.files,
        preferred_channel=args.channel,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
