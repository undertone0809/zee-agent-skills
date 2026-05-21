#!/usr/bin/env python3
"""
flomo local/API helper.

Commands:
- query
- summarize
- export-monthly
- tags
- create
- edit
"""

from __future__ import annotations

import argparse
import html
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional


TOKEN_RE = re.compile(r'access_token":"([^"]+)')
TAG_RE = re.compile(r"(?<!\w)#([^\s#]+)")
MEMO_URL_ID_RE = re.compile(r"[?&]memo_id=([A-Za-z0-9_-]+)")
TRAILING_TAG_PUNCT = ".,;:!?，。！？；：、）)]】》」』"

BASE_URL = "https://flomoapp.com/api/v1"
API_SECRET = "dbbc3dd73364b4084c3a69346e0ce2b2"
APP_VERSION = "5.26.12"
PLATFORM = "mac"
TZ = "8:0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="flomo local/API helper")
    sub = parser.add_subparsers(dest="command", required=True)

    query = sub.add_parser("query", help="Query memos by keyword, tag, or time range")
    query.add_argument("--keyword")
    query.add_argument("--tag")
    query.add_argument("--days", type=int)
    query.add_argument("--start-date")
    query.add_argument("--end-date")
    query.add_argument("--limit", type=int, default=20)
    query.add_argument("--format", choices=["json", "markdown"], default="json")

    summarize = sub.add_parser("summarize", help="Summarize recent memo themes")
    summarize.add_argument("--days", type=int, default=30)
    summarize.add_argument("--limit", type=int, default=50)

    export = sub.add_parser("export-monthly", help="Export monthly markdown and tag stats")
    export.add_argument(
        "--output-dir",
        default=str(Path.home() / "download" / "flomo-markdown-export-monthly"),
    )

    tags = sub.add_parser("tags", help="Inspect existing flomo tags and their frequencies")
    tags.add_argument("--query", help="Case-insensitive substring filter on tag names")
    tags.add_argument("--prefix", help="Filter tags by exact prefix such as area/ai/agent")
    tags.add_argument("--days", type=int, help="Restrict stats to recent memos only")
    tags.add_argument("--limit", type=int, default=50)
    tags.add_argument("--min-total-count", type=int, default=1, help="Only show tags whose total_count is at least this value")
    tags.add_argument("--roots-only", action="store_true", help="Only show root tags (depth 1)")
    tags.add_argument("--format", choices=["json", "markdown"], default="json")

    create = sub.add_parser("create", help="Create a new memo")
    create.add_argument("--content", help="Memo content as plain text unless --html is set")
    create.add_argument("--html", action="store_true", help="Treat --content or stdin as raw HTML")
    create.add_argument("--stdin", action="store_true", help="Read memo content from stdin")
    create.add_argument("--source", default="web")

    edit = sub.add_parser("edit", help="Edit an existing memo by slug or flomo memo URL")
    edit_target = edit.add_mutually_exclusive_group(required=True)
    edit_target.add_argument("--slug", help="Memo slug to edit")
    edit_target.add_argument("--url", help="flomo memo URL containing memo_id")
    edit.add_argument("--content", help="Updated memo content as plain text unless --html is set")
    edit.add_argument("--html", action="store_true", help="Treat --content or stdin as raw HTML")
    edit.add_argument("--stdin", action="store_true", help="Read updated memo content from stdin")
    edit.add_argument("--source", help="Override memo source; defaults to the existing memo source")

    return parser.parse_args()


def local_storage_dir() -> Path:
    return (
        Path.home()
        / "Library/Containers/com.flomoapp.m/Data/Library/Application Support/flomo/Local Storage/leveldb"
    )


def find_access_token() -> str:
    storage = local_storage_dir()
    if not storage.exists():
        raise RuntimeError(f"flomo local storage not found: {storage}")
    for path in sorted(storage.iterdir()):
        if path.suffix not in {".ldb", ".log"} or not path.is_file():
            continue
        text = path.read_bytes().decode("latin1", errors="ignore")
        match = TOKEN_RE.search(text)
        if match:
            return match.group(1)
    raise RuntimeError("Could not find flomo access token in local storage")


def sign_params(params: Dict[str, object]) -> str:
    pieces: List[str] = []
    for key in sorted(params.keys()):
        value = params[key]
        if value is None:
            continue
        if value == "" and value != 0:
            continue
        if isinstance(value, list):
            for item in sorted(value, key=lambda item: str(item)):
                pieces.append(f"{key}[]={item}")
            continue
        pieces.append(f"{key}={value}")
    payload = "&".join(pieces) + API_SECRET
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def api_request(method: str, path: str, extra_params: Optional[Dict[str, object]] = None) -> dict:
    token = find_access_token()
    params: Dict[str, object] = {
        "timestamp": int(datetime.now().timestamp()),
        "api_key": "flomo_web",
        "app_version": APP_VERSION,
        "platform": PLATFORM,
        "webp": "1",
    }
    if extra_params:
        params.update(extra_params)
    params["sign"] = sign_params(params)
    upper_method = method.upper()
    body: Optional[bytes] = None
    url = f"{BASE_URL}{path}"
    if upper_method == "GET":
        url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"
    else:
        body = json.dumps(params).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method=upper_method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "platform": "Mac",
            "device-model": "Mac",
            "device-id": "codex-skill",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("code") != 0:
        raise RuntimeError(f"flomo API error: {data}")
    return data["data"]


def api_get(path: str, extra_params: Optional[Dict[str, object]] = None) -> dict:
    return api_request("GET", path, extra_params)


def api_put(path: str, extra_params: Optional[Dict[str, object]] = None) -> dict:
    return api_request("PUT", path, extra_params)


def fetch_me() -> dict:
    return api_get("/user/me")


def fetch_all_memos() -> List[dict]:
    limit = 200
    latest_updated_at = 0
    latest_slug = ""
    all_memos: List[dict] = []

    for _ in range(50):
        params: Dict[str, object] = {
            "limit": limit,
            "latest_updated_at": latest_updated_at,
            "tz": TZ,
        }
        if latest_slug:
            params["latest_slug"] = latest_slug
        chunk = api_get("/memo/updated/", params)
        all_memos.extend(chunk)
        if len(chunk) < limit:
            break
        last = chunk[-1]
        latest_updated_at = int(datetime.strptime(last["updated_at"], "%Y-%m-%d %H:%M:%S").timestamp())
        latest_slug = last["slug"]

    unique = {memo["slug"]: memo for memo in all_memos}
    return sorted(
        [memo for memo in unique.values() if not memo.get("deleted_at")],
        key=lambda memo: memo["created_at"],
    )


def fetch_memo_by_slug(slug: str) -> dict:
    limit = 200
    latest_updated_at = 0
    latest_slug = ""

    for _ in range(50):
        params: Dict[str, object] = {
            "limit": limit,
            "latest_updated_at": latest_updated_at,
            "tz": TZ,
        }
        if latest_slug:
            params["latest_slug"] = latest_slug
        chunk = api_get("/memo/updated/", params)
        for memo in chunk:
            if memo.get("slug") == slug:
                if memo.get("deleted_at"):
                    raise RuntimeError(f"Memo is deleted: {slug}")
                return memo
        if len(chunk) < limit:
            break
        last = chunk[-1]
        latest_updated_at = int(datetime.strptime(last["updated_at"], "%Y-%m-%d %H:%M:%S").timestamp())
        latest_slug = last["slug"]

    raise RuntimeError(f"Memo not found by slug: {slug}")


def extract_memo_slug(raw_value: str) -> str:
    value = raw_value.strip()
    if not value:
        raise RuntimeError("Memo slug or URL cannot be empty")
    match = MEMO_URL_ID_RE.search(value)
    if match:
        return match.group(1)
    if "flomoapp.com" in value and "memo_id=" in value:
        raise RuntimeError(f"Could not parse memo_id from URL: {value}")
    return value


def memo_web_url(slug: str) -> str:
    return f"https://v.flomoapp.com/mine/?memo_id={slug}"


def html_to_markdown(html: str) -> str:
    replacements = [
        (r"<br\s*/?>", "\n"),
        (r"<hr\s*/?>", "\n\n---\n\n"),
        (r"</p>\s*<p>", "\n\n"),
        (r"<p>", ""),
        (r"</p>", ""),
        (r"<li>\s*<p>", "- "),
        (r"</p>\s*</li>", "\n"),
        (r"<li>", "- "),
        (r"</li>", "\n"),
        (r"<ul>|</ul>|<ol>|</ol>", "\n"),
        (r"<strong>(.*?)</strong>", r"**\1**"),
        (r"<em>(.*?)</em>", r"*\1*"),
        (r"<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", r"[\2](\1)"),
        (r"<[^>]+>", ""),
    ]
    out = html
    for pattern, repl in replacements:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE | re.DOTALL)
    out = (
        out.replace("&nbsp;", " ")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("\r", "")
    )
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


def extract_tags(text: str) -> List[str]:
    seen = set()
    tags: List[str] = []
    for raw in TAG_RE.findall(text):
        tag = raw.strip().rstrip(TRAILING_TAG_PUNCT).strip("/")
        if not tag or tag in seen:
            continue
        seen.add(tag)
        tags.append(tag)
    return tags


def add_derived_fields(memo: dict) -> dict:
    markdown = html_to_markdown(memo.get("content", ""))
    return {
        **memo,
        "markdown": markdown,
        "tags": extract_tags(markdown),
    }


def date_in_range(memo: dict, start_date: Optional[str], end_date: Optional[str]) -> bool:
    created = memo["created_at"][:10]
    if start_date and created < start_date:
        return False
    if end_date and created > end_date:
        return False
    return True


def filter_memos(
    memos: Iterable[dict],
    keyword: Optional[str],
    tag: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
) -> List[dict]:
    keyword_lower = keyword.lower() if keyword else None
    filtered = []
    for memo in memos:
        if not date_in_range(memo, start_date, end_date):
            continue
        if tag and tag not in memo["tags"]:
            continue
        if keyword_lower:
            haystack = f"{memo['markdown']}\n{' '.join(memo['tags'])}".lower()
            if keyword_lower not in haystack:
                continue
        filtered.append(memo)
    return filtered


def snippet(text: str, max_len: int = 120) -> str:
    collapsed = " ".join(text.split())
    return collapsed if len(collapsed) <= max_len else collapsed[: max_len - 1] + "…"


def command_query(args: argparse.Namespace) -> int:
    memos = [add_derived_fields(m) for m in fetch_all_memos()]
    start_date = args.start_date
    end_date = args.end_date
    if args.days:
        start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
    hits = filter_memos(memos, args.keyword, args.tag, start_date, end_date)[: args.limit]

    if args.format == "json":
        payload = [
            {
                "created_at": memo["created_at"],
                "slug": memo["slug"],
                "url": memo_web_url(memo["slug"]),
                "tags": memo["tags"],
                "snippet": snippet(memo["markdown"]),
            }
            for memo in hits
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    lines = ["# flomo query", ""]
    for memo in hits:
        lines.extend(
            [
                f"## {memo['created_at']}",
                "",
                snippet(memo["markdown"], 240),
                "",
                f"- url: {memo_web_url(memo['slug'])}",
                f"- slug: {memo['slug']}",
                f"- tags: {', '.join(memo['tags']) if memo['tags'] else '(none)'}",
                "",
            ]
        )
    print("\n".join(lines))
    return 0


def command_summarize(args: argparse.Namespace) -> int:
    memos = [add_derived_fields(m) for m in fetch_all_memos()]
    start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    recent = filter_memos(memos, None, None, start_date, end_date)

    tag_counter: Counter[str] = Counter()
    for memo in recent:
        for tag in memo["tags"]:
            tag_counter[tag] += 1

    lines = [
        "# flomo recent summary",
        "",
        f"- days: {args.days}",
        f"- memo_count: {len(recent)}",
        "",
        "## Top tags",
        "",
    ]
    for tag, count in tag_counter.most_common(15):
        lines.append(f"- {tag}: {count}")

    lines.extend(["", "## Supporting memos", ""])
    for memo in recent[: args.limit]:
        lines.extend([f"- {memo['created_at']} | {snippet(memo['markdown'], 160)}"])

    print("\n".join(lines))
    return 0


def command_tags(args: argparse.Namespace) -> int:
    memos = [add_derived_fields(m) for m in fetch_all_memos()]
    if args.days:
        start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        memos = filter_memos(memos, None, None, start_date, end_date)

    tag_stats = build_tag_stats(memos, "flomo-user")
    rows = tag_stats["flat_tags"]

    if args.roots_only:
        rows = [row for row in rows if row["depth"] == 1]
    if args.prefix:
        prefix = args.prefix.strip().strip("/")
        rows = [row for row in rows if row["tag"].startswith(prefix)]
    if args.query:
        query = args.query.casefold()
        rows = [row for row in rows if query in row["tag"].casefold()]
    rows = [row for row in rows if row["total_count"] >= args.min_total_count]

    rows = rows[: args.limit]

    if args.format == "json":
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    lines = ["# flomo tags", ""]
    if args.days:
        lines.append(f"- days: {args.days}")
    if args.query:
        lines.append(f"- query: {args.query}")
    if args.prefix:
        lines.append(f"- prefix: {args.prefix.strip().strip('/')}")
    if args.roots_only:
        lines.append("- roots_only: true")
    if args.min_total_count > 1:
        lines.append(f"- min_total_count: {args.min_total_count}")
    lines.extend(["", "| tag | depth | parent | direct_count | total_count |", "|---|---:|---|---:|---:|"])
    for row in rows:
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
    print("\n".join(lines))
    return 0


def plain_text_to_html(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        raise RuntimeError("Memo content cannot be empty")
    blocks = re.split(r"\n{2,}", text)
    paragraphs = []
    for block in blocks:
        escaped = html.escape(block, quote=False).replace("\n", "<br/>")
        paragraphs.append(f"<p>{escaped}</p>")
    return "".join(paragraphs)


def resolve_raw_content(args: argparse.Namespace, action_name: str) -> str:
    if args.stdin:
        raw_content = sys.stdin.read()
    elif args.content is not None:
        raw_content = args.content
    else:
        raise RuntimeError(f"{action_name} requires --content or --stdin")

    if not raw_content.strip():
        raise RuntimeError("Memo content cannot be empty")
    return raw_content


def memo_file_ids(memo: dict) -> List[object]:
    return [file["id"] for file in memo.get("files", []) if "id" in file]


def command_create(args: argparse.Namespace) -> int:
    raw_content = resolve_raw_content(args, "create")

    content = raw_content if args.html else plain_text_to_html(raw_content)
    created = api_put(
        "/memo",
        {
            "content": content,
            "created_at": int(datetime.now().timestamp()),
            "source": args.source,
            "file_ids": [],
            "tz": TZ,
        },
    )
    print(json.dumps(add_derived_fields(created), ensure_ascii=False, indent=2))
    return 0


def command_edit(args: argparse.Namespace) -> int:
    raw_content = resolve_raw_content(args, "edit")
    slug = extract_memo_slug(args.slug or args.url)
    existing = fetch_memo_by_slug(slug)
    content = raw_content if args.html else plain_text_to_html(raw_content)
    updated = api_put(
        f"/memo/{slug}",
        {
            "content": content,
            "local_updated_at": int(datetime.now().timestamp()),
            "source": args.source or existing.get("source") or "web",
            "file_ids": memo_file_ids(existing),
            "tz": TZ,
            "pin": existing.get("pin", 0),
        },
    )
    print(json.dumps(add_derived_fields(updated), ensure_ascii=False, indent=2))
    return 0


def build_tag_stats(memos: List[dict], user: str) -> dict:
    direct_counter: Counter[str] = Counter()
    for memo in memos:
        for tag in memo["tags"]:
            direct_counter[tag] += 1

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

    for tag, count in direct_counter.items():
        parts = tag.split("/")
        for i in range(1, len(parts) + 1):
            get_node("/".join(parts[:i]))
        get_node(tag)["direct_count"] = count

    roots: Dict[str, dict] = {}
    for full_tag, node in node_map.items():
        if node["parent"]:
            node_map[node["parent"]]["children"][node["name"]] = node
        else:
            roots[node["name"]] = node

    def finalize(node: dict) -> int:
        total = node["direct_count"]
        children = list(node["children"].values())
        for child in children:
            total += finalize(child)
        children.sort(key=lambda c: (-c["total_count"], c["name"]))
        node["children"] = children
        node["total_count"] = total
        return total

    root_list = list(roots.values())
    for root in root_list:
        finalize(root)
    root_list.sort(key=lambda c: (-c["total_count"], c["name"]))

    flat_tags = [
        {
            "tag": node["full_tag"],
            "depth": node["depth"],
            "parent": node["parent"],
            "direct_count": node["direct_count"],
            "total_count": node["total_count"],
        }
        for node in node_map.values()
    ]
    flat_tags.sort(key=lambda item: (-item["total_count"], item["tag"]))

    def to_tree_node(node: dict) -> dict:
        return {
            "name": node["name"],
            "full_tag": node["full_tag"],
            "direct_count": node["direct_count"],
            "total_count": node["total_count"],
            "children": [to_tree_node(child) for child in node["children"]],
        }

    return {
        "meta": {
            "user": user,
            "memo_total_count": len(memos),
            "memo_filtered_count": len(memos),
            "start_date": memos[0]["created_at"][:10] if memos else "",
            "end_date": memos[-1]["created_at"][:10] if memos else "",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "flat_tags": flat_tags,
        "tree": [to_tree_node(root) for root in root_list],
    }


def md_escape_cell(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\n", " ")


def render_tag_tree_markdown(nodes: List[dict], indent: int = 0) -> List[str]:
    lines: List[str] = []
    pad = "  " * indent
    for node in nodes:
        lines.append(
            f"{pad}- `{node['full_tag']}` (direct: {node['direct_count']}, total: {node['total_count']})"
        )
        if node.get("children"):
            lines.extend(render_tag_tree_markdown(node["children"], indent + 1))
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


def command_export_monthly(args: argparse.Namespace) -> int:
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    me = fetch_me()
    memos = [add_derived_fields(m) for m in fetch_all_memos()]
    by_month: Dict[str, List[dict]] = {}

    for memo in memos:
        month = memo["created_at"][:7]
        by_month.setdefault(month, []).append(memo)

    for month, items in sorted(by_month.items()):
        lines = [f"# {month}", ""]
        current_date = ""
        for memo in items:
            memo_date = memo["created_at"][:10]
            memo_time = memo["created_at"][11:19]
            if memo_date != current_date:
                current_date = memo_date
                lines.extend([f"## {memo_date}", ""])
            lines.extend([f"### {memo_time}", "", memo["markdown"], "", f"- created_at: `{memo['created_at']}`"])
            if memo.get("files"):
                lines.append(f"- files: {len(memo['files'])}")
            lines.append("")
        (out_dir / f"{month}.md").write_text("\n".join(lines), encoding="utf-8")

    tag_stats = build_tag_stats(memos, me.get("name", "flomo用户"))
    (out_dir / "tag-stats.md").write_text(render_tag_stats_markdown(tag_stats), encoding="utf-8")

    readme = [
        "# flomo Monthly Markdown Export",
        "",
        f"- generated_at: {datetime.now().isoformat(timespec='seconds')}",
        f"- active_memos_exported: {len(memos)}",
        f"- month_files: {len(by_month)}",
        "- tag_stats_md: tag-stats.md",
        "",
    ]
    (out_dir / "README.md").write_text("\n".join(readme), encoding="utf-8")
    print(
        json.dumps(
            {
                "output_dir": str(out_dir),
                "active_memos_exported": len(memos),
                "month_files": len(by_month),
                "tag_stats_md": str(out_dir / "tag-stats.md"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "query":
        return command_query(args)
    if args.command == "summarize":
        return command_summarize(args)
    if args.command == "export-monthly":
        return command_export_monthly(args)
    if args.command == "tags":
        return command_tags(args)
    if args.command == "create":
        return command_create(args)
    if args.command == "edit":
        return command_edit(args)
    raise RuntimeError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
