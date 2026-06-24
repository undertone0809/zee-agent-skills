#!/usr/bin/env python3
"""Generate a local Codex usage insights report.

The script is intentionally read-only. It scans common Codex history surfaces,
normalizes recent session records, extracts lightweight sanitized evidence, and
writes Markdown/JSON artifacts for a human or agent to refine.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECRET_PATTERNS = [
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"(?i)(api[_-]?key\s*[=:]\s*)[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"(?i)(token\s*[=:]\s*)[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"(?i)(password\s*[=:]\s*)\S+"),
    re.compile(r"(?i)(cookie\s*[=:]\s*)\S+"),
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
]


@dataclass
class SessionRecord:
    session_id: str
    path: str
    created_at: str | None = None
    updated_at: str | None = None
    cwd: str | None = None
    first_user_message: str | None = None
    user_messages: int = 0
    assistant_messages: int = 0
    tool_calls: int = 0
    tools: dict[str, int] | None = None
    git_branch: str | None = None
    parent_id: str | None = None
    source: str = "jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME") or "~/.codex")
    parser.add_argument("--limit", type=int, default=30, help="Maximum sessions to analyze.")
    parser.add_argument("--scan-multiplier", type=int, default=8, help="JSONL candidates to inspect per requested session.")
    parser.add_argument("--cwd", help="Only include sessions with this cwd prefix.")
    parser.add_argument("--since", help="Only include sessions on or after YYYY-MM-DD.")
    parser.add_argument("--out", default="/tmp/codex-insights", help="Output directory.")
    parser.add_argument("--include-archived", action="store_true", default=True)
    return parser.parse_args()


def sanitize(value: str | None, max_len: int = 500) -> str | None:
    if value is None:
        return None
    text = value.replace("\x00", "")
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(lambda m: m.group(1) + "[REDACTED]" if m.groups() else "[REDACTED]", text)
    text = re.sub(r"[A-Za-z0-9_+=-]{80,}", "[REDACTED_LONG_SECRET]", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        return text[: max_len - 1] + "..."
    return text


def iso_from_ms(value: Any) -> str | None:
    try:
        if value is None:
            return None
        return datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc).isoformat()
    except Exception:
        return None


def parse_json_line(line: str) -> dict[str, Any] | None:
    try:
        value = json.loads(line)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        return None


def iter_jsonl_files(codex_home: Path, include_archived: bool) -> list[Path]:
    files: list[Path] = []
    for pattern in ["sessions/**/*.jsonl", "session_index.jsonl"]:
        files.extend(codex_home.glob(pattern))
    if include_archived:
        files.extend(codex_home.glob("archived_sessions/**/*.jsonl"))
    return sorted(set(files), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)


def extract_text_from_content(content: Any) -> str | None:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif item.get("type") == "input_text" and isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif isinstance(item.get("content"), str):
                    parts.append(item["content"])
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts) if parts else None
    return None


def event_role(event: dict[str, Any]) -> str | None:
    if isinstance(event.get("message"), dict):
        return event["message"].get("role")
    if isinstance(event.get("payload"), dict):
        payload = event["payload"]
        if isinstance(payload.get("role"), str):
            return payload.get("role")
        if isinstance(payload.get("message"), dict):
            return payload["message"].get("role")
    if event.get("type") in {"user", "assistant"}:
        return event.get("type")
    return None


def event_content(event: dict[str, Any]) -> str | None:
    message = event.get("message")
    if isinstance(message, dict):
        return extract_text_from_content(message.get("content"))
    payload = event.get("payload")
    if isinstance(payload, dict):
        if "content" in payload:
            return extract_text_from_content(payload.get("content"))
        msg = payload.get("message")
        if isinstance(msg, dict):
            return extract_text_from_content(msg.get("content"))
    return extract_text_from_content(event.get("content"))


def event_tool_names(event: dict[str, Any]) -> list[str]:
    names: list[str] = []
    candidates = [event]
    if isinstance(event.get("message"), dict):
        candidates.append(event["message"])
    if isinstance(event.get("payload"), dict):
        candidates.append(event["payload"])
    for candidate in candidates:
        if candidate.get("type") in {"function_call", "tool_use"} and isinstance(candidate.get("name"), str):
            names.append(candidate["name"])
        name = candidate.get("name") or candidate.get("tool_name")
        if isinstance(name, str) and ("tool" in str(candidate.get("type", "")).lower() or candidate.get("tool_call_id")):
            names.append(name)
        content = candidate.get("content")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") in {"tool_use", "function_call"}:
                    item_name = item.get("name") or item.get("tool_name")
                    if isinstance(item_name, str):
                        names.append(item_name)
    return names


def parse_session_jsonl(path: Path) -> SessionRecord | None:
    user_messages = 0
    assistant_messages = 0
    tools: Counter[str] = Counter()
    first_user_message: str | None = None
    session_id = path.stem.replace("rollout-", "")
    cwd: str | None = None
    git_branch: str | None = None
    parent_id: str | None = None
    created_values: list[str] = []

    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                event = parse_json_line(line)
                if not event:
                    continue
                if event.get("type") == "session_meta" and isinstance(event.get("payload"), dict):
                    payload = event["payload"]
                    session_id = str(payload.get("id") or session_id)
                    cwd = cwd or payload.get("cwd")
                    git = payload.get("git")
                    if isinstance(git, dict):
                        git_branch = git_branch or git.get("branch")
                session_id = str(event.get("sessionId") or event.get("session_id") or event.get("thread_id") or session_id)
                cwd = cwd or event.get("cwd")
                git_branch = git_branch or event.get("gitBranch") or event.get("git_branch")
                parent_id = parent_id or event.get("parentUuid") or event.get("parent_uuid") or event.get("parentId")
                timestamp = event.get("timestamp") or event.get("created_at") or event.get("createdAt")
                if isinstance(timestamp, str):
                    created_values.append(timestamp)
                role = event_role(event)
                if role == "user":
                    user_messages += 1
                    content = event_content(event)
                    if first_user_message is None and content and "<environment_context>" not in content:
                        first_user_message = sanitize(content, 700)
                elif role == "assistant":
                    assistant_messages += 1
                for name in event_tool_names(event):
                    tools[name] += 1
    except OSError:
        return None

    stat = path.stat()
    created_at = min(created_values) if created_values else datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat()
    updated_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    if user_messages == 0 and assistant_messages == 0 and not first_user_message:
        return None
    return SessionRecord(
        session_id=session_id,
        path=str(path),
        created_at=created_at,
        updated_at=updated_at,
        cwd=cwd,
        first_user_message=first_user_message,
        user_messages=user_messages,
        assistant_messages=assistant_messages,
        tool_calls=sum(tools.values()),
        tools=dict(tools),
        git_branch=git_branch,
        parent_id=parent_id,
    )


def read_sqlite_records(codex_home: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for db_path in sorted(codex_home.glob("state_*.sqlite")):
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
        except sqlite3.Error:
            continue
        try:
            tables = {
                row["name"]
                for row in conn.execute("select name from sqlite_master where type='table'")
                if row["name"]
            }
            for table in ["threads", "sessions", "conversation_threads"]:
                if table not in tables:
                    continue
                columns = [row["name"] for row in conn.execute(f"pragma table_info({table})")]
                select_cols = [c for c in ["id", "session_id", "thread_id", "cwd", "created_at_ms", "created_at", "updated_at_ms", "first_user_message", "parent_id"] if c in columns]
                if not select_cols:
                    continue
                query = f"select {', '.join(select_cols)} from {table}"
                for row in conn.execute(query):
                    data = dict(row)
                    sid = data.get("session_id") or data.get("thread_id") or data.get("id")
                    if sid:
                        records[str(sid)] = data | {"sqlite_path": str(db_path), "sqlite_table": table}
        except sqlite3.Error:
            pass
        finally:
            conn.close()
    return records


def merge_sqlite(records: list[SessionRecord], sqlite_records: dict[str, dict[str, Any]]) -> None:
    for record in records:
        data = sqlite_records.get(record.session_id)
        if not data:
            continue
        record.source = record.source + "+sqlite"
        record.cwd = record.cwd or data.get("cwd")
        record.first_user_message = record.first_user_message or sanitize(data.get("first_user_message"), 700)
        record.parent_id = record.parent_id or data.get("parent_id")
        record.created_at = record.created_at or iso_from_ms(data.get("created_at_ms")) or data.get("created_at")
        record.updated_at = record.updated_at or iso_from_ms(data.get("updated_at_ms"))


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def filter_records(records: list[SessionRecord], cwd: str | None, since: str | None) -> list[SessionRecord]:
    since_dt = None
    if since:
        since_dt = datetime.fromisoformat(since).replace(tzinfo=timezone.utc)
    filtered: list[SessionRecord] = []
    for record in records:
        if cwd and not ((record.cwd or "").startswith(cwd)):
            continue
        if since_dt:
            created = parse_dt(record.created_at) or parse_dt(record.updated_at)
            if not created or created < since_dt:
                continue
        filtered.append(record)
    return filtered


def classify_prompt(text: str | None) -> list[str]:
    if not text:
        return ["unknown"]
    lowered = text.lower()
    labels: list[str] = []
    checks = [
        ("review", ["review", "审查", "代码审查", "pr ", "diff"]),
        ("debug", ["bug", "error", "失败", "报错", "debug", "修复", "fix"]),
        ("skill", ["skill", "技能", "conversation-to-skill", "skill-creator"]),
        ("research", ["research", "查", "搜索", "调研", "latest", "最新"]),
        ("docs", ["doc", "readme", "文档", "proposal", "方案"]),
        ("git", ["commit", "push", "merge", "rebase", "branch"]),
        ("frontend", ["ui", "页面", "frontend", "playwright", "screenshot"]),
        ("automation", ["automation", "定时", "每天", "schedule", "monitor"]),
    ]
    for label, needles in checks:
        if any(needle in lowered for needle in needles):
            labels.append(label)
    return labels or ["implementation"]


def root_workflow_count(records: list[SessionRecord]) -> tuple[int, dict[str, list[str]]]:
    children: dict[str, list[str]] = defaultdict(list)
    ids = {r.session_id for r in records}
    roots = set(ids)
    for record in records:
        if record.parent_id and record.parent_id in ids:
            roots.discard(record.session_id)
            children[record.parent_id].append(record.session_id)
    return len(roots), dict(children)


def generate_report(records: list[SessionRecord], source_meta: dict[str, Any], out_dir: Path) -> str:
    cwd_counts = Counter(r.cwd or "unknown" for r in records)
    label_counts: Counter[str] = Counter()
    tool_counts: Counter[str] = Counter()
    for record in records:
        label_counts.update(classify_prompt(record.first_user_message))
        tool_counts.update(record.tools or {})
    root_count, child_map = root_workflow_count(records)

    lines = [
        "# Codex Insights",
        "",
        f"Data window: latest {len(records)} matching sessions",
        f"Sources: `{source_meta['codex_home']}`",
        f"Analyzed: {len(records)} raw sessions, {root_count} root workflows if parent metadata is available",
        "",
        "## Current Fact",
        "",
        f"- JSONL files found: {source_meta['jsonl_files_found']}",
        f"- JSONL files scanned: {source_meta['jsonl_files_scanned']}",
        f"- SQLite records found: {source_meta['sqlite_records_found']}",
        f"- Output directory: `{out_dir}`",
        "",
        "## Usage Patterns",
        "",
    ]
    if label_counts:
        lines.append("- Task families: " + ", ".join(f"{k} ({v})" for k, v in label_counts.most_common(8)))
    if cwd_counts:
        lines.append("- Top workspaces: " + ", ".join(f"`{k}` ({v})" for k, v in cwd_counts.most_common(5)))
    if tool_counts:
        lines.append("- Top tools: " + ", ".join(f"`{k}` ({v})" for k, v in tool_counts.most_common(8)))
    if child_map:
        lines.append(f"- Fanout detected: {sum(len(v) for v in child_map.values())} child sessions under {len(child_map)} parents")
    lines.extend(["", "## Friction Points", ""])
    heavy = [r for r in records if r.user_messages >= 8 or r.tool_calls >= 20]
    if heavy:
        lines.append(f"- {len(heavy)} sessions look high-friction by message/tool volume; inspect evidence before drawing conclusions.")
    else:
        lines.append("- No high-volume friction pattern was obvious from lightweight counters.")
    unknown = [r for r in records if not r.first_user_message]
    if unknown:
        lines.append(f"- {len(unknown)} sessions lack a readable first user message; report coverage may be incomplete.")
    lines.extend(["", "## Workflow Opportunities", ""])
    if label_counts.get("skill", 0) >= 2:
        lines.append("- `skill-optimization`: repeated skill work appears in the cohort; inspect whether existing skill instructions or evals need updates.")
    if label_counts.get("automation", 0) >= 2:
        lines.append("- `automation`: repeated scheduled/monitoring language appears; check whether this should become a durable automation.")
    if label_counts.get("review", 0) >= 3:
        lines.append("- `skill-optimization`: review-heavy usage may warrant tighter reviewer instructions or reusable grading scripts.")
    if not any(label_counts.get(k, 0) >= n for k, n in [("skill", 2), ("automation", 2), ("review", 3)]):
        lines.append("- `no-op`: no clear new-skill signal from counters alone. Use the evidence list for qualitative judgment.")
    lines.extend(["", "## Evidence", ""])
    for idx, record in enumerate(records[:12], 1):
        created = record.created_at or record.updated_at or "unknown time"
        lines.append(f"{idx}. `{record.session_id}` `{created}` `{record.cwd or 'unknown cwd'}`")
        if record.first_user_message:
            lines.append(f"   - {record.first_user_message}")
        lines.append(f"   - path: `{record.path}`")
    lines.extend([
        "",
        "Artifacts:",
        f"- `{out_dir / 'report.md'}`",
        f"- `{out_dir / 'summary.json'}`",
        f"- `{out_dir / 'sessions.json'}`",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    codex_home = Path(args.codex_home).expanduser()
    out_dir = Path(args.out).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    jsonl_files = iter_jsonl_files(codex_home, args.include_archived)
    scan_limit = max(args.limit * args.scan_multiplier, args.limit)
    candidate_files = []
    records: list[SessionRecord] = []
    for path in jsonl_files:
        if len(candidate_files) >= scan_limit and len(records) >= args.limit:
            break
        candidate_files.append(path)
        record = parse_session_jsonl(path)
        if record:
            records.append(record)
    sqlite_records = read_sqlite_records(codex_home)
    merge_sqlite(records, sqlite_records)
    records = filter_records(records, args.cwd, args.since)
    records.sort(key=lambda r: parse_dt(r.created_at) or parse_dt(r.updated_at) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    records = records[: args.limit]

    source_meta = {
        "codex_home": str(codex_home),
        "jsonl_files_found": len(jsonl_files),
        "jsonl_files_scanned": len(candidate_files),
        "sqlite_records_found": len(sqlite_records),
        "limit": args.limit,
        "cwd_filter": args.cwd,
        "since": args.since,
    }
    summary = {
        "source_meta": source_meta,
        "analyzed_sessions": len(records),
        "top_cwds": Counter(r.cwd or "unknown" for r in records).most_common(),
        "task_families": Counter(label for r in records for label in classify_prompt(r.first_user_message)).most_common(),
        "tool_counts": Counter(tool for r in records for tool, count in (r.tools or {}).items() for _ in range(count)).most_common(),
    }
    (out_dir / "sessions.json").write_text(json.dumps([asdict(r) for r in records], ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    report = generate_report(records, source_meta, out_dir)
    (out_dir / "report.md").write_text(report, encoding="utf-8")
    print(out_dir / "report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
