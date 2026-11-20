"""
ingest_source_material.py
Phase 1 Stage 0 Black-Box Source Ingestion & Normalization Engine.
Detects input modality (YouTube, web URL, local PDF, local DOCX, CSV, or raw text/Markdown)
and extracts clean, structured Markdown into `00_source_article.md`.

Provides:
- detect_input_modality(source_input: str) -> str
- ingest_url_to_markdown(url: str, output_md_path: Optional[str] = None, timeout: int = 20) -> dict
- ingest_youtube_transcript(url_or_id: str, output_md_path: Optional[str] = None, preferred_langs: tuple = ("zh-TW", "zh-Hant", "zh", "zh-Hans", "en")) -> dict
- ingest_local_document_to_markdown(file_path: str, output_md_path: Optional[str] = None) -> dict
- ingest_to_source_markdown(source_input: str, output_md_path: str, title_override: Optional[str] = None) -> dict
"""

import argparse
import json
import re
import sys
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import Request, urlopen

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

BLOCKED_PHRASES = (
    "just a moment...",
    "verify you are human",
    "cf-browser-verification",
    "attention required! | cloudflare",
    "enable javascript and cookies to continue",
    "access denied",
)

NOISE_XPATHS = (
    ".//script",
    ".//style",
    ".//noscript",
    ".//svg",
    ".//nav",
    ".//footer",
    ".//aside",
    ".//form",
    ".//*[contains(@class, 'sidebar')]",
    ".//*[contains(@class, 'cookie')]",
    ".//*[contains(@class, 'ads')]",
    ".//*[contains(@class, 'advertisement')]",
    ".//*[contains(@class, 'share-buttons')]",
    ".//*[contains(@class, 'related-posts')]",
)


def _extract_youtube_video_id(text: str) -> str | None:
    """Extract 11-character YouTube video ID from URL or raw ID string."""
    s = text.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    parsed = urlparse(s)
    host = parsed.netloc.lower()
    if not host:
        return None
    if "youtu.be" in host:
        cand = parsed.path.strip("/").split("/")[0]
        return cand if re.fullmatch(r"[A-Za-z0-9_-]{11}", cand) else None
    if "youtube.com" in host or "youtube-nocookie.com" in host:
        if parsed.path == "/watch":
            vid = parse_qs(parsed.query).get("v", [None])[0]
            return vid if vid and re.fullmatch(r"[A-Za-z0-9_-]{11}", vid) else None
        for prefix in ("/shorts/", "/embed/", "/live/", "/v/"):
            if parsed.path.startswith(prefix):
                cand = parsed.path[len(prefix):].split("/")[0]
                return cand if re.fullmatch(r"[A-Za-z0-9_-]{11}", cand) else None
    return None


def detect_input_modality(source_input: str) -> str:
    """
    Sniff input modality before Phase 1 routing.
    Returns one of: 'youtube', 'web_url', 'pdf_file', 'docx_file', 'csv_dataset', 'text_or_md'.
    """
    s = (source_input or "").strip()
    if not s:
        return "text_or_md"
    if "\n" not in s and len(s) < 512:
        if _extract_youtube_video_id(s):
            return "youtube"
        lower = s.lower()
        if lower.startswith(("http://", "https://")):
            return "web_url"
        p = Path(s)
        ext = p.suffix.lower()
        if ext == ".pdf":
            return "pdf_file"
        if ext in (".docx", ".doc"):
            return "docx_file"
        if ext in (".csv", ".tsv", ".xlsx", ".xls"):
            return "csv_dataset"
    return "text_or_md"


def _http_get_text(url: str, timeout: int = 20) -> tuple[int, str]:
    """Fetch URL body via `requests` if available, else standard library `urllib`."""
    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,text/markdown,text/plain;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    }
    try:
        import requests  # type: ignore

        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        resp.encoding = resp.apparent_encoding or resp.encoding or "utf-8"
        return resp.status_code, resp.text
    except ImportError:
        pass
    except Exception as exc:
        raise RuntimeError(f"HTTP request failed: {exc}") from exc

    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.status, raw.decode(charset, errors="replace")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return exc.code, body
    except URLError as exc:
        raise RuntimeError(f"URL open failed: {exc.reason}") from exc


def _clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _node_inline_text(el: Any) -> str:
    """Extract inline text with basic Markdown formatting for links, code, and emphasis."""
    parts: list[str] = []
    if el.text:
        parts.append(el.text)
    for child in el:
        tag = child.tag.lower() if isinstance(child.tag, str) else ""
        inner = _node_inline_text(child)
        if tag in ("strong", "b") and inner.strip():
            parts.append(f"**{inner.strip()}**")
        elif tag in ("em", "i") and inner.strip():
            parts.append(f"*{inner.strip()}*")
        elif tag == "code" and inner.strip():
            parts.append(f"`{inner.strip()}`")
        elif tag == "a" and inner.strip():
            href = (child.get("href") or "").strip()
            if href.startswith(("http://", "https://")):
                parts.append(f"[{inner.strip()}]({href})")
            else:
                parts.append(inner)
        elif tag == "br":
            parts.append("\n")
        else:
            parts.append(inner)
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def _table_to_markdown(table_el: Any) -> str:
    """Convert an HTML <table> element to a GitHub-flavored Markdown table."""
    rows: list[list[str]] = []
    for tr in table_el.xpath(".//tr"):
        cells = [_clean_whitespace(_node_inline_text(td)).replace("|", "\\|") for td in tr.xpath("./th|./td")]
        if any(cells):
            rows.append(cells)
    if not rows:
        return ""
    col_count = max(len(r) for r in rows)
    normalized = [r + [""] * (col_count - len(r)) for r in rows]
    lines = [
        "| " + " | ".join(normalized[0]) + " |",
        "| " + " | ".join(["---"] * col_count) + " |",
    ]
    for r in normalized[1:]:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


def _html_node_to_markdown(node: Any, blocks: list[str]) -> None:
    """Recursively convert block-level HTML elements to clean Markdown blocks."""
    tag = node.tag.lower() if isinstance(node.tag, str) else ""
    if not tag:
        return
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        txt = _clean_whitespace(_node_inline_text(node))
        if txt:
            blocks.append(f"{'#' * int(tag[1])} {txt}")
        return
    if tag == "p":
        txt = _clean_whitespace(_node_inline_text(node))
        if txt:
            blocks.append(txt)
        return
    if tag == "blockquote":
        txt = _clean_whitespace(" ".join(node.itertext()))
        if txt:
            blocks.append("\n".join(f"> {line}" for line in txt.splitlines() if line.strip()))
        return
    if tag == "pre":
        code = "".join(node.itertext()).strip("\n")
        if code.strip():
            blocks.append(f"```\n{code}\n```")
        return
    if tag in ("ul", "ol"):
        items: list[str] = []
        for idx, li in enumerate(node.xpath("./li"), start=1):
            txt = _clean_whitespace(_node_inline_text(li))
            if txt:
                prefix = f"{idx}." if tag == "ol" else "-"
                items.append(f"{prefix} {txt}")
        if items:
            blocks.append("\n".join(items))
        return
    if tag == "table":
        tbl = _table_to_markdown(node)
        if tbl:
            blocks.append(tbl)
        return
    for child in node:
        _html_node_to_markdown(child, blocks)


def _format_source_document(
    title: str,
    source_ref: str,
    modality_label: str,
    body_markdown: str,
    extra_notice: str | None = None,
) -> str:
    """Wrap extracted content with a uniform Phase 1 `00_source_article.md` header."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# {title.strip() or '未命名來源素材'}",
        "",
        f"- **原始來源**：{source_ref}",
        f"- **素材型態**：`{modality_label}`",
        f"- **自動擷取時間**：{ts}",
        "",
    ]
    if extra_notice:
        lines.extend([extra_notice.strip(), ""])
    lines.extend(["---", "", body_markdown.strip(), ""])
    return "\n".join(lines)


def _write_output_if_requested(content: str, output_md_path: str | None) -> str | None:
    if not output_md_path:
        return None
    out = Path(output_md_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return str(out.resolve())


def ingest_url_to_markdown(
    url: str,
    output_md_path: str | None = None,
    timeout: int = 20,
    title_override: str | None = None,
) -> dict[str, Any]:
    """
    Fetch a web page (with HackMD raw markdown fast-path) and convert main content to clean Markdown.
    Returns structured status dict; degrades gracefully on HTTP 401/403/429 or anti-bot walls.
    """
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        return {
            "ok": False,
            "status": "INVALID_URL",
            "modality": "web_url",
            "error": "僅支援 http:// 或 https:// 網址。",
        }

    # HackMD raw markdown fast-path
    if "hackmd.io" in parsed.netloc.lower() and not parsed.path.endswith("/download"):
        base_hackmd = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
        with suppress(RuntimeError, OSError, ValueError):
            st, md_raw = _http_get_text(f"{base_hackmd}/download", timeout=timeout)
            if st == 200 and md_raw.strip() and "<html" not in md_raw[:300].lower():
                first_h1 = re.search(r"(?m)^#\s+(.+)$", md_raw)
                title = title_override or (first_h1.group(1).strip() if first_h1 else base_hackmd.split("/")[-1])
                formatted = _format_source_document(title, url, "web_url (HackMD)", md_raw)
                written = _write_output_if_requested(formatted, output_md_path)
                return {
                    "ok": True,
                    "status": "OK",
                    "modality": "web_url",
                    "title": title,
                    "output_path": written,
                    "char_count": len(md_raw.strip()),
                    "markdown": formatted,
                }

    try:
        status_code, html_text = _http_get_text(url, timeout=timeout)
    except (RuntimeError, OSError, ValueError) as exc:
        return {
            "ok": False,
            "status": "FETCH_ERROR",
            "modality": "web_url",
            "error": f"網頁連線失敗：{exc}",
        }

    lower_html = html_text.lower()
    if status_code in (401, 403, 429) or any(phrase in lower_html for phrase in BLOCKED_PHRASES):
        return {
            "ok": False,
            "status": "BLOCKED_OR_TOO_SHORT",
            "modality": "web_url",
            "http_status": status_code,
            "error": "目標網頁受反爬蟲或登入牆保護，請直接複製貼上內文。",
        }
    if status_code >= 400:
        return {
            "ok": False,
            "status": "HTTP_ERROR",
            "modality": "web_url",
            "http_status": status_code,
            "error": f"目標網頁回傳錯誤狀態碼 HTTP {status_code}。",
        }

    # Optional trafilatura upgrade when installed
    title = title_override or ""
    body_md = ""
    with suppress(ImportError, RuntimeError, ValueError, OSError):
        import trafilatura  # type: ignore

        extracted = trafilatura.extract(
            html_text,
            output_format="markdown",
            include_tables=True,
            include_links=True,
            with_metadata=False,
        )
        if extracted and len(extracted.strip()) >= 120:
            body_md = extracted.strip()

    from lxml import etree
    from lxml import html as lxml_html

    try:
        doc = lxml_html.fromstring(html_text)
    except (etree.LxmlError, ValueError, TypeError) as exc:
        return {
            "ok": False,
            "status": "PARSE_ERROR",
            "modality": "web_url",
            "error": f"HTML 解析失敗：{exc}",
        }

    if not title:
        title_els = doc.xpath("//meta[@property='og:title']/@content | //title/text()")
        title = _clean_whitespace(title_els[0]) if title_els else parsed.netloc

    if not body_md:
        for xp in NOISE_XPATHS:
            for bad in doc.xpath(xp):
                parent = bad.getparent()
                if parent is not None:
                    parent.remove(bad)

        candidates = doc.xpath("//article | //*[@role='main'] | //main")
        root_node = None
        if candidates:
            root_node = max(candidates, key=lambda el: len(_clean_whitespace(" ".join(el.itertext()))))
        else:
            body_els = doc.xpath("//body")
            root_node = body_els[0] if body_els else doc

        blocks: list[str] = []
        _html_node_to_markdown(root_node, blocks)
        body_md = "\n\n".join(blocks).strip()
        if len(body_md) < 120:
            fallback_txt = "\n\n".join(
                _clean_whitespace(" ".join(p.itertext()))
                for p in root_node.xpath(".//p")
                if _clean_whitespace(" ".join(p.itertext()))
            )
            if len(fallback_txt) > len(body_md):
                body_md = fallback_txt

    if len(re.sub(r"\s+", "", body_md)) < 120:
        return {
            "ok": False,
            "status": "BLOCKED_OR_TOO_SHORT",
            "modality": "web_url",
            "error": "目標網頁受反爬蟲或登入牆保護，或正文過短（< 120 字），請直接複製貼上內文。",
        }

    formatted = _format_source_document(title, url, "web_url", body_md)
    written = _write_output_if_requested(formatted, output_md_path)
    return {
        "ok": True,
        "status": "OK",
        "modality": "web_url",
        "title": title,
        "output_path": written,
        "char_count": len(body_md),
        "markdown": formatted,
    }


def _fetch_youtube_oembed(video_id: str) -> tuple[str, str]:
    """Fetch video title and channel name via YouTube oEmbed without API keys."""
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    oembed_url = f"https://www.youtube.com/oembed?url={quote(watch_url, safe='')}&format=json"
    with suppress(RuntimeError, OSError, json.JSONDecodeError, ValueError):
        status, body = _http_get_text(oembed_url, timeout=10)
        if status == 200:
            data = json.loads(body)
            return str(data.get("title") or "").strip(), str(data.get("author_name") or "").strip()
    return f"YouTube 影片 ({video_id})", ""


def _select_youtube_transcript(transcript_list: Any, preferred_langs: tuple) -> Any:
    """Pick best transcript: manual preferred -> generated preferred -> first available."""
    from youtube_transcript_api._errors import YouTubeTranscriptApiException  # type: ignore

    with suppress(YouTubeTranscriptApiException, LookupError, AttributeError, ValueError):
        return transcript_list.find_manually_created_transcript(list(preferred_langs))
    with suppress(YouTubeTranscriptApiException, LookupError, AttributeError, ValueError):
        return transcript_list.find_generated_transcript(list(preferred_langs))
    for tr in transcript_list:
        return tr
    return None


def _aggregate_transcript_chunks(entries: list[Any], bucket_seconds: int = 60) -> str:
    """Aggregate short caption snippets into readable timestamped paragraphs."""
    paragraphs: list[str] = []
    bucket_start: float | None = None
    bucket_texts: list[str] = []

    def _flush() -> None:
        if bucket_start is None or not bucket_texts:
            return
        total_sec = int(bucket_start)
        mm, ss = divmod(total_sec, 60)
        hh, mm = divmod(mm, 60)
        stamp = f"{hh:02d}:{mm:02d}:{ss:02d}" if hh else f"{mm:02d}:{ss:02d}"
        joined = " ".join(bucket_texts)
        joined = re.sub(r"\s+", " ", joined).strip()
        if joined:
            paragraphs.append(f"**[{stamp}]** {joined}")

    for item in entries:
        text = item.get("text", "") if isinstance(item, dict) else getattr(item, "text", "")
        start = item.get("start", 0.0) if isinstance(item, dict) else getattr(item, "start", 0.0)
        cleaned = _clean_whitespace(str(text).replace("\n", " "))
        if not cleaned:
            continue
        if bucket_start is None:
            bucket_start = float(start)
        if float(start) - bucket_start >= bucket_seconds and bucket_texts:
            _flush()
            bucket_start = float(start)
            bucket_texts = [cleaned]
        else:
            bucket_texts.append(cleaned)

    _flush()
    return "\n\n".join(paragraphs)


def ingest_youtube_transcript(
    url_or_id: str,
    output_md_path: str | None = None,
    preferred_langs: tuple = ("zh-TW", "zh-Hant", "zh", "zh-Hans", "en"),
    title_override: str | None = None,
) -> dict[str, Any]:
    """
    Download YouTube captions/transcript into timestamped Markdown paragraphs.
    Supports both youtube-transcript-api >= 1.x instance methods and legacy classmethods.
    """
    video_id = _extract_youtube_video_id(url_or_id)
    if not video_id:
        return {
            "ok": False,
            "status": "INVALID_YOUTUBE_URL",
            "modality": "youtube",
            "error": "無法解析 YouTube 影片 ID。",
        }

    try:
        from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
        from youtube_transcript_api._errors import YouTubeTranscriptApiException  # type: ignore
    except ImportError:
        return {
            "ok": False,
            "status": "MISSING_DEPENDENCY",
            "modality": "youtube",
            "error": "尚未安裝 youtube-transcript-api，請執行 `python -m pip install youtube-transcript-api`。",
        }

    try:
        if hasattr(YouTubeTranscriptApi, "list_transcripts"):
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        else:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
        selected = _select_youtube_transcript(transcript_list, preferred_langs)
        if selected is None:
            return {
                "ok": False,
                "status": "NO_TRANSCRIPT",
                "modality": "youtube",
                "error": "此影片沒有任何可用的字幕軌道。",
            }
        raw_entries = list(selected.fetch())
        is_generated = bool(getattr(selected, "is_generated", False))
        lang_code = str(getattr(selected, "language_code", "unknown"))
    except (YouTubeTranscriptApiException, OSError, RuntimeError, ValueError, TypeError) as exc:
        return {
            "ok": False,
            "status": "TRANSCRIPT_FETCH_ERROR",
            "modality": "youtube",
            "error": f"YouTube 字幕擷取失敗：{exc}",
        }

    title, author = _fetch_youtube_oembed(video_id)
    final_title = title_override or (f"{title}（{author}）" if author else title)
    body_md = _aggregate_transcript_chunks(raw_entries, bucket_seconds=60)
    notice = None
    if is_generated:
        notice = (
            "> ⚠️ **【自動生成字幕校準提醒】**：本逐字稿由 YouTube 自動語音辨識生成"
            f"（語言代碼：`{lang_code}`），專有名詞或同音字可能存在誤差，於 Phase 1 蘇格拉底推演時請結合上下文脈絡判讀。"
        )
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    formatted = _format_source_document(
        final_title,
        watch_url,
        f"youtube (lang={lang_code}, auto_generated={is_generated})",
        body_md,
        extra_notice=notice,
    )
    written = _write_output_if_requested(formatted, output_md_path)
    return {
        "ok": True,
        "status": "OK",
        "modality": "youtube",
        "video_id": video_id,
        "title": final_title,
        "language_code": lang_code,
        "is_generated": is_generated,
        "output_path": written,
        "char_count": len(body_md),
        "markdown": formatted,
    }


def _docx_to_markdown(path: Path) -> str:
    """Convert .docx paragraphs (headings + body) and tables in document order to Markdown."""
    from docx import Document  # type: ignore
    from docx.opc.exceptions import OpcError  # type: ignore
    from docx.oxml.table import CT_Tbl  # type: ignore
    from docx.oxml.text.paragraph import CT_P  # type: ignore
    from docx.table import Table  # type: ignore
    from docx.text.paragraph import Paragraph  # type: ignore

    try:
        doc = Document(str(path))
    except OpcError as exc:
        raise RuntimeError(f"DOCX 檔案讀取失敗：{exc}") from exc
    blocks: list[str] = []

    for child in doc.element.body.iterchildren():
        if isinstance(child, CT_P):
            para = Paragraph(child, doc)
            text = _clean_whitespace(para.text)
            if not text:
                continue
            style_name = (para.style.name or "").lower() if para.style else ""
            m = re.search(r"heading\s*([1-6])", style_name)
            if m:
                blocks.append(f"{'#' * int(m.group(1))} {text}")
            elif "title" in style_name:
                blocks.append(f"# {text}")
            elif "list" in style_name:
                blocks.append(f"- {text}")
            else:
                blocks.append(text)
        elif isinstance(child, CT_Tbl):
            tbl = Table(child, doc)
            rows: list[list[str]] = []
            for row in tbl.rows:
                cells = [_clean_whitespace(c.text).replace("|", "\\|") for c in row.cells]
                if any(cells):
                    rows.append(cells)
            if rows:
                col_count = max(len(r) for r in rows)
                norm = [r + [""] * (col_count - len(r)) for r in rows]
                t_lines = [
                    "| " + " | ".join(norm[0]) + " |",
                    "| " + " | ".join(["---"] * col_count) + " |",
                ]
                for r in norm[1:]:
                    t_lines.append("| " + " | ".join(r) + " |")
                blocks.append("\n".join(t_lines))

    return "\n\n".join(blocks).strip()


def _pdf_to_markdown(path: Path) -> str:
    """Extract PDF into structured Markdown via pymupdf4llm, falling back to pymupdf."""
    with suppress(ImportError, RuntimeError, ValueError, OSError, TypeError):
        import pymupdf4llm  # type: ignore

        md_text = pymupdf4llm.to_markdown(str(path))
        if md_text and md_text.strip():
            return md_text.strip()

    import pymupdf  # type: ignore

    pages: list[str] = []
    with pymupdf.open(str(path)) as pdf:
        for idx, page in enumerate(pdf, start=1):
            txt = page.get_text("text").strip()
            if txt:
                pages.append(f"## Page {idx}\n\n{txt}")
    return "\n\n".join(pages).strip()


def ingest_local_document_to_markdown(
    file_path: str,
    output_md_path: str | None = None,
    title_override: str | None = None,
) -> dict[str, Any]:
    """Convert a local .pdf, .docx, .md, or .txt file into Phase 1 `00_source_article.md`."""
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        return {
            "ok": False,
            "status": "FILE_NOT_FOUND",
            "modality": "local_document",
            "error": f"找不到檔案：{file_path}",
        }

    ext = p.suffix.lower()
    title = title_override or p.stem
    try:
        if ext == ".pdf":
            modality = "pdf_file"
            body_md = _pdf_to_markdown(p)
        elif ext == ".docx":
            modality = "docx_file"
            body_md = _docx_to_markdown(p)
        elif ext in (".md", ".txt"):
            modality = "text_or_md"
            body_md = p.read_text(encoding="utf-8", errors="replace").strip()
        else:
            return {
                "ok": False,
                "status": "UNSUPPORTED_EXTENSION",
                "modality": ext,
                "error": f"不支援的本機文件格式 `{ext}`（支援 `.pdf`、`.docx`、`.md`、`.txt`）。",
            }
    except (OSError, RuntimeError, ValueError, TypeError, KeyError, AttributeError) as exc:
        return {
            "ok": False,
            "status": "DOCUMENT_PARSE_ERROR",
            "modality": ext,
            "error": f"文件解析失敗：{exc}",
        }

    if not body_md:
        return {
            "ok": False,
            "status": "EMPTY_DOCUMENT",
            "modality": modality,
            "error": "文件內容為空或為純掃描影像 PDF（無可選取文字）。",
        }

    formatted = _format_source_document(title, str(p), modality, body_md)
    written = _write_output_if_requested(formatted, output_md_path)
    return {
        "ok": True,
        "status": "OK",
        "modality": modality,
        "title": title,
        "output_path": written,
        "char_count": len(body_md),
        "markdown": formatted,
    }


def ingest_to_source_markdown(
    source_input: str,
    output_md_path: str,
    title_override: str | None = None,
) -> dict[str, Any]:
    """
    Unified Stage 0 dispatcher: detects modality and extracts clean Markdown into `output_md_path`.
    """
    modality = detect_input_modality(source_input)
    if modality == "youtube":
        return ingest_youtube_transcript(source_input, output_md_path=output_md_path, title_override=title_override)
    if modality == "web_url":
        return ingest_url_to_markdown(source_input, output_md_path=output_md_path, title_override=title_override)
    if modality in ("pdf_file", "docx_file"):
        return ingest_local_document_to_markdown(source_input, output_md_path=output_md_path, title_override=title_override)
    if modality == "csv_dataset":
        return {
            "ok": False,
            "status": "CSV_PASSTHROUGH",
            "modality": "csv_dataset",
            "error": "CSV / 試算表屬於 Mode 2 原始數據集，請原封不動存入 `data/<原檔名>.csv` 並走 `mode2_dataset_codebook_protocol.md`。",
        }

    # text_or_md: either a local .md/.txt file path or direct raw text
    cand = Path(source_input.strip())
    if "\n" not in source_input and len(source_input) < 512 and cand.exists() and cand.is_file():
        return ingest_local_document_to_markdown(str(cand), output_md_path=output_md_path, title_override=title_override)

    title = title_override or "使用者提供之原始文獻素材"
    formatted = _format_source_document(title, "Direct User Input", "text_or_md", source_input.strip())
    written = _write_output_if_requested(formatted, output_md_path)
    return {
        "ok": True,
        "status": "OK",
        "modality": "text_or_md",
        "title": title,
        "output_path": written,
        "char_count": len(source_input.strip()),
        "markdown": formatted,
    }


if __name__ == "__main__":
    with suppress(AttributeError, OSError, ValueError):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Stage 0 Black-Box Source Material Ingestor -> 00_source_article.md")
    parser.add_argument("--input", "-i", required=True, help="URL, YouTube link/ID, local .pdf/.docx/.md/.txt path, or text.")
    parser.add_argument("--output", "-o", required=True, help="Target path for 00_source_article.md.")
    parser.add_argument("--title", "-t", default=None, help="Optional title override.")
    args = parser.parse_args()

    res = ingest_to_source_markdown(args.input, args.output, title_override=args.title)
    summary = {k: v for k, v in res.items() if k != "markdown"}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not res.get("ok"):
        sys.exit(1)
