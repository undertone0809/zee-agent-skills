#!/usr/bin/env python3
"""
Convert flomo memos from local desktop auth/API into grouped Markdown files and tag statistics.

Default output is decompressed Markdown files (no ZIP).

Behavior: this script only supports local/API source and will fail fast on read errors.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
except Exception as exc:  # pragma: no cover
    print(
        "ERROR: BeautifulSoup4 (bs4) is required to run this script. "
        "Install it with: pip install beautifulsoup4",
        file=sys.stderr,
    )
    raise


INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
MULTI_UNDERSCORE_RE = re.compile(r"_+")
TAG_RE = re.compile(r"(?<!\w)#([^\s#]+)")
TRAILING_TAG_PUNCT = ".,;:!?，。！？；：、）)]】》」』"
DEFAULT_CHAR_LIMIT = 500_000
LOCAL_API_MODULE = None


@dataclass
class Attachment:
    kind: str  # image | audio | file
    rel_src: str
    url: Optional[str] = None


@dataclass
class Memo:
    time_str: str
    timestamp: datetime
    content_html: str
    plain_text: str
    attachments: List[Attachment] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class ParseResult:
    user: str
    memos: List[Memo]
    warnings: List[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert flomo local/API data into grouped Markdown files and tag statistics."
    )
    parser.add_argument("--output-dir", help="Output directory for markdown files")
    parser.add_argument("--start-date", help="Filter start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="Filter end date (YYYY-MM-DD)")
    parser.add_argument(
        "--split",
        choices=["year", "halfYear", "quarter", "month"],
        default="month",
        help="Split granularity (default: month)",
    )
    parser.add_argument(
        "--name-template",
        default="{{user}}_{{range}}",
        help="Output filename template (supports {{user}} and {{range}})",
    )
    parser.add_argument(
        "--word-limit",
        type=int,
        default=DEFAULT_CHAR_LIMIT,
        help="Character count threshold per output file (kept as word-limit for compatibility)",
    )
    parser.add_argument(
        "--preview-only",
        action="store_true",
        help="Parse/filter/group/stat only. Do not write markdown files or copy assets.",
    )
    parser.add_argument(
        "--asset-mode",
        choices=["placeholder", "ignore", "copy"],
        default="placeholder",
        help="How to handle memo attachments (default: placeholder)",
    )
    parser.add_argument("--summary-json", help="Optional path to write summary JSON")
    return parser.parse_args()


def load_local_api_module():
    global LOCAL_API_MODULE
    if LOCAL_API_MODULE is not None:
        return LOCAL_API_MODULE

    skills_root = Path(__file__).resolve().parents[2]
    module_path = skills_root / "flomo-local-api" / "scripts" / "flomo_local_api.py"
    if not module_path.exists():
        raise RuntimeError(f"flomo local api helper not found: {module_path}")

    spec = importlib.util.spec_from_file_location("flomo_local_api_for_nblm", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load flomo local api helper: {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    LOCAL_API_MODULE = module
    return module


def parse_datetime(value: str) -> Optional[datetime]:
    value = value.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    # Fallback for minor format drift
    normalized = value.replace("/", "-")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def normalize_plain_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def extract_tags_from_text(text: str) -> List[str]:
    seen = set()
    tags: List[str] = []
    for raw in TAG_RE.findall(text):
        tag = raw.strip().rstrip(TRAILING_TAG_PUNCT)
        tag = tag.strip("/")
        if not tag:
            continue
        if tag not in seen:
            seen.add(tag)
            tags.append(tag)
    return tags


def collect_local_attachments(files: Sequence[dict]) -> List[Attachment]:
    attachments: List[Attachment] = []
    seen: set[Tuple[str, str]] = set()

    for file_item in files:
        rel_src = str(file_item.get("path") or "").strip()
        url = str(file_item.get("url") or "").strip() or None
        ref = rel_src or (url or "")
        if not ref:
            continue

        kind_raw = str(file_item.get("type") or "").strip().lower()
        kind = kind_raw if kind_raw in {"image", "audio"} else "file"
        key = (kind, ref)
        if key in seen:
            continue
        seen.add(key)
        attachments.append(Attachment(kind=kind, rel_src=ref, url=url))

    return attachments

def parse_local_flomo_api() -> ParseResult:
    try:
        local_api = load_local_api_module()
    except Exception as exc:
        raise RuntimeError("Failed to initialize local flomo API. No cached export fallback is supported.") from exc

    warnings: List[str] = []
    try:
        me = local_api.fetch_me()
    except Exception as exc:
        raise RuntimeError("Failed to read flomo user info from local API.") from exc

    user = me.get("name", "flomo用户") or "flomo用户"
    if not user.strip():
        raise RuntimeError("Failed to read flomo user name from local API response.")

    memos: List[Memo] = []
    try:
        raw_memos = local_api.fetch_all_memos()
    except Exception as exc:
        raise RuntimeError("Failed to fetch memo list from flomo local API.") from exc

    for idx, raw_memo in enumerate(raw_memos, start=1):
        time_str = str(raw_memo.get("created_at") or "").strip()
        dt = parse_datetime(time_str)
        if dt is None:
            warnings.append(f"Skipped memo #{idx}: invalid created_at '{time_str}'")
            continue

        content_html = str(raw_memo.get("content") or "")
        plain_text = normalize_plain_text(html_to_markdown(content_html)) if content_html else ""
        attachments = collect_local_attachments(raw_memo.get("files") or [])
        tags = extract_tags_from_text(plain_text)

        memos.append(
            Memo(
                time_str=time_str,
                timestamp=dt,
                content_html=content_html,
                plain_text=plain_text,
                attachments=attachments,
                tags=tags,
            )
        )

    memos.sort(key=lambda m: m.timestamp)
    return ParseResult(user=user, memos=memos, warnings=warnings)


def parse_filter_date(value: Optional[str], end_of_day: bool = False) -> Optional[datetime]:
    if not value:
        return None
    try:
        d = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date '{value}', expected YYYY-MM-DD")
    return datetime.combine(d, time.max if end_of_day else time.min)


def get_range_suffix(dt: datetime, range_type: str) -> str:
    y = dt.year
    m = dt.month
    if range_type == "year":
        return f"{y}年"
    if range_type == "month":
        return f"{y}-{m:02d}"
    if range_type == "quarter":
        return f"{y}-Q{((m - 1) // 3) + 1}"
    if range_type == "halfYear":
        return f"{y}-上半年" if m <= 6 else f"{y}-下半年"
    return "export"


def render_inline_children(tag: Tag) -> str:
    parts: List[str] = []
    for child in tag.children:
        parts.append(render_inline_node(child))
    return "".join(parts)


def render_inline_node(node) -> str:
    if isinstance(node, NavigableString):
        return str(node)
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    if name == "br":
        return "\n"
    if name in {"strong", "b"}:
        text = render_inline_children(node).strip()
        return f"**{text}**" if text else ""
    if name in {"em", "i"}:
        text = render_inline_children(node).strip()
        return f"*{text}*" if text else ""
    if name == "code":
        text = render_inline_children(node).strip()
        return f"`{text}`" if text else ""
    if name == "a":
        text = render_inline_children(node).strip() or (node.get("href") or "").strip()
        href = (node.get("href") or "").strip()
        if href:
            return f"[{text}]({href})"
        return text
    # Fallback: inline render descendants
    return render_inline_children(node)


def render_block_children(parent: Tag, indent: int = 0) -> List[str]:
    lines: List[str] = []
    for child in parent.children:
        lines.extend(render_block_node(child, indent=indent))
    return lines


def normalize_block_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse excessive blank lines created by nested parsing
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def render_list_item(li: Tag, ordered: bool, index: int, indent: int) -> List[str]:
    prefix = f"{index}. " if ordered else "- "
    pad = "  " * indent
    child_lines: List[str] = []
    direct_text_parts: List[str] = []

    for child in li.children:
        if isinstance(child, NavigableString):
            direct_text_parts.append(str(child))
            continue
        if not isinstance(child, Tag):
            continue
        if child.name.lower() in {"ul", "ol"}:
            if direct_text_parts:
                text = normalize_block_text("".join(direct_text_parts))
                if text:
                    child_lines.append(f"{pad}{prefix}{text}")
                direct_text_parts = []
            nested_lines = render_block_node(child, indent=indent + 1)
            child_lines.extend(nested_lines)
        elif child.name.lower() == "p":
            text = normalize_block_text(render_inline_children(child))
            if text:
                if not child_lines:
                    child_lines.append(f"{pad}{prefix}{text}")
                else:
                    child_lines.append(f"{pad}  {text}")
        else:
            direct_text_parts.append(render_inline_node(child))

    if direct_text_parts:
        text = normalize_block_text("".join(direct_text_parts))
        if text:
            if not child_lines:
                child_lines.append(f"{pad}{prefix}{text}")
            else:
                child_lines.append(f"{pad}  {text}")

    if not child_lines:
        child_lines.append(f"{pad}{prefix}")
    return child_lines


def render_block_node(node, indent: int = 0) -> List[str]:
    if isinstance(node, NavigableString):
        text = normalize_block_text(str(node))
        return [text] if text else []
    if not isinstance(node, Tag):
        return []

    name = node.name.lower()
    if name in {"p", "div"}:
        text = normalize_block_text(render_inline_children(node))
        return [text] if text else []
    if name == "br":
        return [""]
    if name == "ul":
        lines: List[str] = []
        idx = 0
        for li in node.find_all("li", recursive=False):
            idx += 1
            lines.extend(render_list_item(li, ordered=False, index=idx, indent=indent))
        return lines
    if name == "ol":
        lines = []
        for idx, li in enumerate(node.find_all("li", recursive=False), start=1):
            lines.extend(render_list_item(li, ordered=True, index=idx, indent=indent))
        return lines
    if name == "blockquote":
        content = "\n".join(render_block_children(node, indent=indent)).strip()
        if not content:
            return []
        return [f"> {line}" if line else ">" for line in content.splitlines()]
    if name == "pre":
        code = node.get_text("", strip=False).rstrip("\n")
        return ["```", code, "```"] if code else []
    if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        level = int(name[1])
        text = normalize_block_text(render_inline_children(node))
        return [f"{'#' * level} {text}"] if text else []
    # Fallback: flatten descendants
    return render_block_children(node, indent=indent)


def html_to_markdown(html_fragment: str) -> str:
    soup = BeautifulSoup(html_fragment, "html.parser")
    lines = render_block_children(soup)
    out: List[str] = []
    prev_blank = True
    for line in lines:
        line = line.rstrip()
        if not line:
            if not prev_blank:
                out.append("")
            prev_blank = True
            continue
        out.append(line)
        prev_blank = False
    return "\n".join(out).strip()


def sanitize_filename_base(name: str) -> str:
    name = INVALID_FILENAME_CHARS.sub("_", name)
    name = name.strip().rstrip(".")
    name = MULTI_UNDERSCORE_RE.sub("_", name)
    return name


def ensure_md_extension(name: str) -> str:
    return name if name.lower().endswith(".md") else f"{name}.md"


def build_logical_filename(user: str, dt: datetime, range_type: str, template: str) -> str:
    rendered = template.replace("{{user}}", user).replace("{{range}}", get_range_suffix(dt, range_type))
    rendered = rendered.strip()
    rendered = ensure_md_extension(rendered) if rendered else ""
    return rendered


def fallback_filename(dt: datetime, range_type: str) -> str:
    suffix = sanitize_filename_base(get_range_suffix(dt, range_type))
    if suffix:
        return f"flomo_export_{suffix}.md"
    return "flomo_export.md"


def dedupe_filename(target_name: str, used: set[str]) -> str:
    if target_name not in used:
        used.add(target_name)
        return target_name
    stem, ext = os.path.splitext(target_name)
    i = 2
    while True:
        candidate = f"{stem}_{i}{ext}"
        if candidate not in used:
            used.add(candidate)
            return candidate
        i += 1


def is_remote_ref(value: str) -> bool:
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme in {"http", "https"}


def attachment_dest_rel_path(att: Attachment, index: int) -> Path:
    raw_ref = att.rel_src or (att.url or "")
    if is_remote_ref(raw_ref):
        raw_ref = urllib.parse.urlparse(raw_ref).path
    raw_ref = raw_ref.lstrip("/")
    if not raw_ref:
        raw_ref = f"attachment_{index}"
    return Path("assets") / raw_ref


def download_attachment(url: str, dest_path: Path) -> None:
    with urllib.request.urlopen(url) as resp:
        dest_path.write_bytes(resp.read())


def render_attachment_lines(
    attachments: Sequence[Attachment],
    asset_mode: str,
    output_dir: Optional[Path],
    copy_manifest: Dict[str, str],
) -> List[str]:
    if asset_mode == "ignore" or not attachments:
        return []

    lines: List[str] = []
    if asset_mode == "placeholder":
        lines.append("附件:")
        for att in attachments:
            label = "图片" if att.kind == "image" else "音频" if att.kind == "audio" else "文件"
            lines.append(f"- {label}: {att.rel_src}")
        return lines

    # copy mode
    if output_dir is None:
        return []
    lines.append("附件:")
    for idx, att in enumerate(attachments, start=1):
        dest_rel = attachment_dest_rel_path(att, idx)
        dest_path = output_dir / dest_rel
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        remote_url = att.url or (att.rel_src if is_remote_ref(att.rel_src) else "")
        if remote_url:
            try:
                if not dest_path.exists():
                    download_attachment(remote_url, dest_path)
            except Exception as exc:
                lines.append(f"- 缺失附件 ({att.kind}): {att.rel_src} ({exc})")
                continue
        else:
            lines.append(f"- 缺失附件 ({att.kind}): {att.rel_src}")
            continue

        copy_key = att.rel_src or (att.url or dest_rel.as_posix())
        copy_manifest[copy_key] = dest_rel.as_posix()
        rel_ref = dest_rel.as_posix()
        if att.kind == "image":
            lines.append(f"![]({rel_ref})")
        elif att.kind == "audio":
            lines.append(f"- 音频: [打开附件]({rel_ref})")
        else:
            lines.append(f"- 文件: [打开附件]({rel_ref})")
    return lines


def build_markdown_for_memo(
    memo: Memo,
    asset_mode: str,
    output_dir: Optional[Path],
    copy_manifest: Dict[str, str],
) -> str:
    body = html_to_markdown(memo.content_html)
    sections = [f"### {memo.time_str}", "", body if body else ""]
    attachment_lines = render_attachment_lines(
        memo.attachments,
        asset_mode,
        output_dir,
        copy_manifest,
    )
    if attachment_lines:
        if sections[-1] != "":
            sections.append("")
        sections.extend(attachment_lines)
    sections.extend(["", "---", ""])
    return "\n".join(sections)


def filter_memos(memos: Sequence[Memo], start_dt: Optional[datetime], end_dt: Optional[datetime]) -> List[Memo]:
    filtered = []
    for memo in memos:
        if start_dt and memo.timestamp < start_dt:
            continue
        if end_dt and memo.timestamp > end_dt:
            continue
        filtered.append(memo)
    return filtered


def build_grouped_data(
    memos: Sequence[Memo],
    user: str,
    range_type: str,
    template: str,
    char_limit: int,
) -> Tuple[List[dict], Dict[str, List[Memo]]]:
    groups: Dict[str, List[Memo]] = defaultdict(list)
    for memo in memos:
        logical = build_logical_filename(user, memo.timestamp, range_type, template)
        if not logical:
            logical = fallback_filename(memo.timestamp, range_type)
        groups[logical].append(memo)

    used_names: set[str] = set()
    summaries: List[dict] = []
    renamed_groups: Dict[str, List[Memo]] = {}

    for logical_name in sorted(groups.keys()):
        sample_memo = groups[logical_name][0]
        stem, ext = os.path.splitext(logical_name)
        clean_stem = sanitize_filename_base(stem)
        if not clean_stem:
            clean_name = fallback_filename(sample_memo.timestamp, range_type)
        else:
            clean_name = f"{clean_stem}{ext or '.md'}"
        actual_name = dedupe_filename(clean_name, used_names)
        renamed_groups[actual_name] = groups[logical_name]

        char_count = sum(len(m.plain_text) for m in groups[logical_name])
        summaries.append(
            {
                "logical_name": logical_name,
                "actual_name": actual_name,
                "memo_count": len(groups[logical_name]),
                "char_count": char_count,
                "over_limit": char_count > char_limit,
            }
        )

    return summaries, renamed_groups


def build_tag_stats(memos: Sequence[Memo], user: str, total_memos: int, date_span: Tuple[Optional[str], Optional[str]]) -> dict:
    direct_counter = Counter()
    for memo in memos:
        for tag in memo.tags:
            direct_counter[tag] += 1

    # Build tree node map
    node_map: Dict[str, dict] = {}

    def get_node(full_tag: str) -> dict:
        if full_tag not in node_map:
            parts = full_tag.split("/")
            node_map[full_tag] = {
                "name": parts[-1],
                "full_tag": full_tag,
                "direct_count": 0,
                "total_count": 0,
                "children": {},
                "parent": "/".join(parts[:-1]) if len(parts) > 1 else None,
                "depth": len(parts),
            }
        return node_map[full_tag]

    # Create nodes for direct tags and ancestors
    for tag, count in direct_counter.items():
        parts = tag.split("/")
        for i in range(1, len(parts) + 1):
            ancestor = "/".join(parts[:i])
            get_node(ancestor)
        get_node(tag)["direct_count"] = count

    # Link tree
    roots: Dict[str, dict] = {}
    for full_tag, node in node_map.items():
        parent = node["parent"]
        if parent:
            parent_node = node_map[parent]
            parent_node["children"][node["name"]] = node
        else:
            roots[node["name"]] = node

    def finalize(node: dict) -> int:
        total = node["direct_count"]
        child_items = list(node["children"].items())
        finalized_children = []
        for child_name, child in child_items:
            total += finalize(child)
            finalized_children.append(child)
        finalized_children.sort(key=lambda c: (-c["total_count"], c["name"]))
        node["children"] = finalized_children
        node["total_count"] = total
        return total

    root_list = list(roots.values())
    for root in root_list:
        finalize(root)
    root_list.sort(key=lambda c: (-c["total_count"], c["name"]))

    flat_tags = []
    for full_tag, node in node_map.items():
        flat_tags.append(
            {
                "tag": full_tag,
                "depth": node["depth"],
                "parent": node["parent"],
                "direct_count": node["direct_count"],
                "total_count": node["total_count"],
            }
        )
    flat_tags.sort(key=lambda item: (-item["total_count"], item["tag"]))

    # Strip helper keys from tree output
    def to_tree_node(node: dict) -> dict:
        return {
            "name": node["name"],
            "full_tag": node["full_tag"],
            "direct_count": node["direct_count"],
            "total_count": node["total_count"],
            "children": [to_tree_node(child) for child in node["children"]],
        }

    start_date, end_date = date_span
    return {
        "meta": {
            "user": user,
            "memo_total_count": total_memos,
            "memo_filtered_count": len(memos),
            "start_date": start_date,
            "end_date": end_date,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "flat_tags": flat_tags,
        "tree": [to_tree_node(root) for root in root_list],
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def md_escape_cell(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\n", " ")


def render_tag_tree_markdown(nodes: Sequence[dict], indent: int = 0) -> List[str]:
    lines: List[str] = []
    pad = "  " * indent
    for node in nodes:
        lines.append(
            f"{pad}- `{node['full_tag']}` (direct: {node['direct_count']}, total: {node['total_count']})"
        )
        children = node.get("children", [])
        if children:
            lines.extend(render_tag_tree_markdown(children, indent=indent + 1))
    return lines


def render_tag_stats_markdown(tag_stats: dict) -> str:
    meta = tag_stats.get("meta", {})
    flat_tags = tag_stats.get("flat_tags", [])
    tree = tag_stats.get("tree", [])

    lines: List[str] = []
    lines.append("# Tag Stats")
    lines.append("")
    lines.append("## Meta")
    lines.append("")
    lines.append(f"- User: `{meta.get('user', '')}`")
    lines.append(f"- Memo total count: {meta.get('memo_total_count', 0)}")
    lines.append(f"- Memo filtered count: {meta.get('memo_filtered_count', 0)}")
    lines.append(f"- Date range: {meta.get('start_date', '')} to {meta.get('end_date', '')}")
    lines.append(f"- Generated at: {meta.get('generated_at', '')}")
    lines.append("")
    lines.append("## Flat Tags (sorted by total_count desc)")
    lines.append("")
    lines.append("| tag | depth | parent | direct_count | total_count |")
    lines.append("|---|---:|---|---:|---:|")
    for row in flat_tags:
        lines.append(
            "| "
            + " | ".join(
                [
                    md_escape_cell(row.get("tag", "")),
                    md_escape_cell(row.get("depth", "")),
                    md_escape_cell(row.get("parent", "")),
                    md_escape_cell(row.get("direct_count", "")),
                    md_escape_cell(row.get("total_count", "")),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## Tag Tree")
    lines.append("")
    if tree:
        lines.extend(render_tag_tree_markdown(tree))
    else:
        lines.append("- (no tags)")
    lines.append("")
    return "\n".join(lines)


def default_output_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = Path.home() / "download"
    return base / f"nblm_export_{stamp}"


def summarize_for_stdout(summary: dict) -> None:
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> int:
    args = parse_args()

    try:
        parsed = parse_local_flomo_api()
    except Exception as exc:
        print("ERROR: flomo local/API read failed. This skill does not fall back to cached exports.", file=sys.stderr)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not parsed.memos:
        print("ERROR: No valid memos parsed from the selected flomo source.", file=sys.stderr)
        return 1

    try:
        start_dt = parse_filter_date(args.start_date, end_of_day=False)
        end_dt = parse_filter_date(args.end_date, end_of_day=True)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    all_start = parsed.memos[0].timestamp.strftime("%Y-%m-%d")
    all_end = parsed.memos[-1].timestamp.strftime("%Y-%m-%d")
    if start_dt is None:
        start_dt = datetime.combine(parsed.memos[0].timestamp.date(), time.min)
    if end_dt is None:
        end_dt = datetime.combine(parsed.memos[-1].timestamp.date(), time.max)

    filtered = filter_memos(parsed.memos, start_dt, end_dt)
    group_summaries, grouped_memos = build_grouped_data(
        filtered, parsed.user, args.split, args.name_template, args.word_limit
    )

    tag_stats = build_tag_stats(
        filtered,
        user=parsed.user,
        total_memos=len(parsed.memos),
        date_span=(start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")),
    )

    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else default_output_dir()
    wrote_files = []
    copy_manifest: Dict[str, str] = {}

    if not args.preview_only:
        output_dir.mkdir(parents=True, exist_ok=True)
        for actual_name, memos in grouped_memos.items():
            md_path = output_dir / actual_name
            chunks = [
                build_markdown_for_memo(
                    memo,
                    asset_mode=args.asset_mode,
                    output_dir=output_dir,
                    copy_manifest=copy_manifest,
                )
                for memo in memos
            ]
            md_path.write_text("".join(chunks), encoding="utf-8")
            wrote_files.append(str(md_path))
        tag_stats_path = output_dir / "tag-stats.md"
        write_text(tag_stats_path, render_tag_stats_markdown(tag_stats))
    else:
        tag_stats_path = None

    warnings = list(parsed.warnings)
    if not filtered:
        warnings.append("No memos matched the selected date range.")

    summary = {
        "input": {
            "source": "local",
            "mode": "preview" if args.preview_only else "export",
        },
        "config": {
            "split": args.split,
            "name_template": args.name_template,
            "asset_mode": args.asset_mode,
            "word_limit": args.word_limit,
            "word_limit_semantics": "character_count_threshold",
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "end_date": end_dt.strftime("%Y-%m-%d"),
            "preview_only": args.preview_only,
        },
        "stats": {
            "user": parsed.user,
            "memo_total_count": len(parsed.memos),
            "memo_filtered_count": len(filtered),
            "source_date_span": {"start": all_start, "end": all_end},
            "group_count": len(group_summaries),
            "warnings_count": len(warnings),
        },
        "groups": group_summaries,
        "outputs": {
            "output_dir": None if args.preview_only else str(output_dir),
            "markdown_files": [] if args.preview_only else wrote_files,
            "tag_stats_md": None if args.preview_only else str(tag_stats_path),
            "copied_assets": copy_manifest,
        },
        "warnings": warnings,
    }

    if args.summary_json:
        summary_path = Path(args.summary_json).expanduser().resolve()
        write_json(summary_path, summary)
        summary["outputs"]["summary_json"] = str(summary_path)
    else:
        summary["outputs"]["summary_json"] = None

    summarize_for_stdout(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
