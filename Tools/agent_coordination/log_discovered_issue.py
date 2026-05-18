#!/usr/bin/env python3
"""Append one cross-task discovered-issue entry to the shared log.

The log lives at `AgentCoordination/discovered_issues/log.jsonl` and is the
inbox for issues that any agent (claude, codex, ocode, gemini) notices while
working on something else. See `AgentCoordination/discovered_issues/README.md`
for the full schema and triage workflow.

This helper is the only sanctioned writer. Hand-editing the log is discouraged
because the helper enforces:

  * file existence and line-in-range
  * snippet capture (so the entry survives line drift)
  * deterministic, monotonic per-day `id` generation
  * canonical UTC ISO8601 timestamp
  * one JSON object per line (no trailing comma, no pretty-printing)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_AGENTS = ("claude", "codex", "ocode", "gemini")
ALLOWED_CATEGORIES = (
    "bug",
    "security",
    "perf",
    "test-gap",
    "dead-code",
    "doc",
    "convention",
    "tech-debt",
)
ALLOWED_SEVERITIES = ("low", "medium", "high")

LOG_RELATIVE = Path("AgentCoordination") / "discovered_issues" / "log.jsonl"


def _utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _discover_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(8):
        if (cur / "AGENTS.md").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise SystemExit(
        f"Could not locate repo root (AGENTS.md) starting from {start}"
    )


def _normalize_repo_path(repo_root: Path, file_arg: str) -> Path:
    p = Path(file_arg)
    if p.is_absolute():
        try:
            rel = p.resolve().relative_to(repo_root)
        except ValueError as exc:
            raise SystemExit(
                f"--file {file_arg!r} is outside repo root {repo_root}"
            ) from exc
        return rel
    return Path(*p.parts)


def _read_snippet(abs_file: Path, line: int) -> str:
    text = abs_file.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if not 1 <= line <= len(lines):
        raise SystemExit(
            f"--line {line} out of range for {abs_file} ({len(lines)} lines)"
        )
    lo = max(1, line - 1)
    hi = min(len(lines), line + 1)
    return "\n".join(lines[lo - 1 : hi])


def _next_id(log_path: Path, today: str) -> str:
    prefix = f"DI-{today}-"
    highest = 0
    if log_path.exists():
        with log_path.open("r", encoding="utf-8") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    entry = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                eid = entry.get("id", "")
                if isinstance(eid, str) and eid.startswith(prefix):
                    try:
                        highest = max(highest, int(eid[len(prefix) :]))
                    except ValueError:
                        continue
    return f"{prefix}{highest + 1:03d}"


def _build_entry(
    *,
    agent: str,
    source_task: str,
    file_rel: Path,
    line: int,
    snippet: str,
    symbol: str | None,
    category: str,
    severity: str,
    description: str,
    suggested_action: str | None,
    entry_id: str,
    timestamp: str,
) -> dict[str, object]:
    entry: dict[str, object] = {
        "id": entry_id,
        "discovered_at": timestamp,
        "agent": agent,
        "source_task": source_task,
        "file": file_rel.as_posix(),
        "line": line,
        "code_snippet": snippet,
        "category": category,
        "severity": severity,
        "description": description,
    }
    if symbol:
        entry["symbol"] = symbol
    if suggested_action:
        entry["suggested_action"] = suggested_action
    return entry


def _append_entry(log_path: Path, entry: dict[str, object]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False, sort_keys=True)

    needs_leading_newline = False
    if log_path.exists() and log_path.stat().st_size > 0:
        with log_path.open("rb") as peek:
            peek.seek(-1, 2)
            if peek.read(1) != b"\n":
                needs_leading_newline = True

    with log_path.open("a", encoding="utf-8", newline="\n") as fh:
        if needs_leading_newline:
            fh.write("\n")
        fh.write(line + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Record one discovered issue in the shared log."
    )
    parser.add_argument("--agent", required=True, choices=ALLOWED_AGENTS)
    parser.add_argument(
        "--source-task",
        required=True,
        help="What the agent was working on when this was discovered.",
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Repo-relative or absolute path to the file containing the issue.",
    )
    parser.add_argument("--line", required=True, type=int)
    parser.add_argument("--category", required=True, choices=ALLOWED_CATEGORIES)
    parser.add_argument(
        "--severity", default="medium", choices=ALLOWED_SEVERITIES
    )
    parser.add_argument(
        "--description",
        required=True,
        help="What is wrong. Be specific enough that the entry is durable.",
    )
    parser.add_argument(
        "--suggested-action",
        default=None,
        help="Optional fix recommendation.",
    )
    parser.add_argument(
        "--symbol",
        default=None,
        help="Optional enclosing function/class name for fallback locating.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Override auto-discovery of the repo root (testing).",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=None,
        help="Override the log file location (testing).",
    )
    args = parser.parse_args(argv)

    repo_root = (
        args.repo_root.resolve() if args.repo_root else _discover_repo_root(Path.cwd())
    )
    file_rel = _normalize_repo_path(repo_root, args.file)
    abs_file = repo_root / file_rel
    if not abs_file.is_file():
        raise SystemExit(f"--file does not exist: {abs_file}")

    if args.line < 1:
        raise SystemExit(f"--line must be >= 1 (got {args.line})")

    snippet = _read_snippet(abs_file, args.line)

    log_path = args.log_path.resolve() if args.log_path else (repo_root / LOG_RELATIVE)
    timestamp = _utc_timestamp()
    today = timestamp[:10]  # YYYY-MM-DD
    entry_id = _next_id(log_path, today)

    entry = _build_entry(
        agent=args.agent,
        source_task=args.source_task,
        file_rel=file_rel,
        line=args.line,
        snippet=snippet,
        symbol=args.symbol,
        category=args.category,
        severity=args.severity,
        description=args.description,
        suggested_action=args.suggested_action,
        entry_id=entry_id,
        timestamp=timestamp,
    )
    _append_entry(log_path, entry)
    print(entry_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
