#!/usr/bin/env python3
"""Inspect and prune the shared discovered-issues log.

Reads `AgentCoordination/discovered_issues/log.jsonl` and, for each entry,
verifies the recorded snippet against the current state of the file. The
result tells a triage agent (or the user) whether the issue is likely still
valid, has drifted to a new line, or appears to have been resolved.

Usage:

  # Inspect all open entries (default action).
  python Tools/agent_coordination/triage_discovered_issues.py

  # Filter:
  python Tools/agent_coordination/triage_discovered_issues.py --agent claude
  python Tools/agent_coordination/triage_discovered_issues.py --category bug
  python Tools/agent_coordination/triage_discovered_issues.py --severity high

  # Machine-readable output (one JSON object per line, including verdict).
  python Tools/agent_coordination/triage_discovered_issues.py --format jsonl

  # Prune (delete) one or more entries by id. Git history preserves them.
  python Tools/agent_coordination/triage_discovered_issues.py --prune DI-2026-05-18-001 DI-2026-05-18-002

Verdict vocabulary (per entry):
  * match-exact      file:line still shows the snippet
  * match-drifted    snippet found within +/- DRIFT_WINDOW lines
  * match-elsewhere  snippet found, but far from original line
  * snippet-gone     file exists, snippet not found anywhere -> likely fixed
  * file-gone        file no longer exists -> almost certainly resolved
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

DRIFT_WINDOW = 25
LOG_RELATIVE = Path("AgentCoordination") / "discovered_issues" / "log.jsonl"

VERDICT_MATCH_EXACT = "match-exact"
VERDICT_MATCH_DRIFTED = "match-drifted"
VERDICT_MATCH_ELSEWHERE = "match-elsewhere"
VERDICT_SNIPPET_GONE = "snippet-gone"
VERDICT_FILE_GONE = "file-gone"


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


def _load_entries(log_path: Path) -> list[dict[str, object]]:
    if not log_path.exists():
        return []
    entries: list[dict[str, object]] = []
    with log_path.open("r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            stripped = raw.strip()
            if not stripped:
                continue
            try:
                entries.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise SystemExit(
                    f"Malformed JSONL at {log_path}:{lineno}: {exc.msg}"
                ) from exc
    return entries


@dataclass(frozen=True)
class Verdict:
    code: str
    current_line: int | None
    detail: str


def _find_snippet(file_text: str, snippet: str) -> list[int]:
    """Return 1-indexed start lines where `snippet` matches `file_text` exactly."""
    if not snippet:
        return []
    file_lines = file_text.splitlines()
    snip_lines = snippet.splitlines()
    if not snip_lines or len(snip_lines) > len(file_lines):
        return []
    hits: list[int] = []
    n = len(snip_lines)
    for i in range(len(file_lines) - n + 1):
        if file_lines[i : i + n] == snip_lines:
            hits.append(i + 1)
    return hits


def _verdict_for(entry: dict[str, object], repo_root: Path) -> Verdict:
    file_rel = entry.get("file")
    line = entry.get("line")
    snippet = entry.get("code_snippet", "")
    if not isinstance(file_rel, str) or not isinstance(line, int):
        return Verdict(VERDICT_SNIPPET_GONE, None, "malformed entry")

    abs_file = (repo_root / file_rel).resolve()
    if not abs_file.is_file():
        return Verdict(VERDICT_FILE_GONE, None, f"{file_rel} not present")

    text = abs_file.read_text(encoding="utf-8", errors="replace")
    if not isinstance(snippet, str):
        return Verdict(VERDICT_SNIPPET_GONE, None, "snippet missing from entry")

    # Snippet was captured as line-1 .. line+1, so the snippet's first line
    # corresponds to original (line - 1) in the file when fully captured. We
    # normalize by searching for the whole snippet and reporting the *middle*
    # line of the match as the new line number.
    hits = _find_snippet(text, snippet)
    if not hits:
        return Verdict(VERDICT_SNIPPET_GONE, None, "snippet not found in file")

    snip_n = len(snippet.splitlines())
    # The "middle line" approximates the original target line (line-1 + offset).
    def _mid(start_line: int) -> int:
        return start_line + (snip_n // 2)

    mids = [_mid(h) for h in hits]
    # Prefer the closest hit to the recorded line.
    closest = min(mids, key=lambda m: abs(m - line))
    distance = abs(closest - line)
    if distance == 0:
        return Verdict(VERDICT_MATCH_EXACT, closest, "line and snippet agree")
    if distance <= DRIFT_WINDOW:
        return Verdict(
            VERDICT_MATCH_DRIFTED,
            closest,
            f"snippet at line {closest} (drifted {distance} from {line})",
        )
    return Verdict(
        VERDICT_MATCH_ELSEWHERE,
        closest,
        f"snippet at line {closest}, far from recorded line {line}",
    )


def _filter(
    entries: list[dict[str, object]],
    *,
    agent: str | None,
    category: str | None,
    severity: str | None,
    ids: set[str] | None,
) -> list[dict[str, object]]:
    out = []
    for e in entries:
        if agent and e.get("agent") != agent:
            continue
        if category and e.get("category") != category:
            continue
        if severity and e.get("severity") != severity:
            continue
        if ids is not None and e.get("id") not in ids:
            continue
        out.append(e)
    return out


def _print_human(
    entries: list[dict[str, object]],
    verdicts: list[Verdict],
    stream: object,
) -> None:
    if not entries:
        print("(no entries)", file=stream)
        return
    for entry, verdict in zip(entries, verdicts):
        print(
            f"{entry.get('id')}  [{verdict.code}]  "
            f"{entry.get('category')}/{entry.get('severity')}  "
            f"{entry.get('file')}:{entry.get('line')}",
            file=stream,
        )
        if verdict.current_line and verdict.current_line != entry.get("line"):
            print(f"    -> now at line {verdict.current_line}", file=stream)
        print(f"    agent={entry.get('agent')}  source={entry.get('source_task')}", file=stream)
        desc = str(entry.get("description", "")).replace("\n", " ")
        if len(desc) > 200:
            desc = desc[:197] + "..."
        print(f"    {desc}", file=stream)
        if verdict.detail:
            print(f"    ({verdict.detail})", file=stream)


def _prune(log_path: Path, ids_to_remove: set[str]) -> tuple[int, list[str]]:
    entries = _load_entries(log_path)
    keep: list[dict[str, object]] = []
    removed: list[str] = []
    for e in entries:
        eid = e.get("id")
        if isinstance(eid, str) and eid in ids_to_remove:
            removed.append(eid)
            continue
        keep.append(e)

    tmp = log_path.with_suffix(log_path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as fh:
        for e in keep:
            fh.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(log_path)
    return len(removed), removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect or prune the discovered-issues log."
    )
    parser.add_argument(
        "--repo-root", type=Path, default=None, help="Override repo-root discovery."
    )
    parser.add_argument(
        "--log-path", type=Path, default=None, help="Override the log file location."
    )
    parser.add_argument("--agent", default=None)
    parser.add_argument("--category", default=None)
    parser.add_argument("--severity", default=None)
    parser.add_argument(
        "--id",
        action="append",
        default=None,
        help="Restrict to specific entry id(s); repeatable.",
    )
    parser.add_argument(
        "--format",
        choices=("human", "jsonl"),
        default="human",
        help="Output format for the inspection report.",
    )
    parser.add_argument(
        "--prune",
        nargs="+",
        default=None,
        metavar="ID",
        help="Delete the listed entries from the log and exit.",
    )
    args = parser.parse_args(argv)

    repo_root = (
        args.repo_root.resolve() if args.repo_root else _discover_repo_root(Path.cwd())
    )
    log_path = args.log_path.resolve() if args.log_path else (repo_root / LOG_RELATIVE)

    if args.prune:
        removed_count, removed_ids = _prune(log_path, set(args.prune))
        missing = sorted(set(args.prune) - set(removed_ids))
        print(f"pruned {removed_count} entr{'y' if removed_count == 1 else 'ies'}")
        for rid in removed_ids:
            print(f"  - {rid}")
        if missing:
            print(f"not found: {', '.join(missing)}", file=sys.stderr)
            return 1
        return 0

    entries = _load_entries(log_path)
    filtered = _filter(
        entries,
        agent=args.agent,
        category=args.category,
        severity=args.severity,
        ids=set(args.id) if args.id else None,
    )
    verdicts = [_verdict_for(e, repo_root) for e in filtered]

    if args.format == "jsonl":
        for e, v in zip(filtered, verdicts):
            payload = dict(e)
            payload["_verdict"] = v.code
            payload["_verdict_detail"] = v.detail
            if v.current_line is not None:
                payload["_current_line"] = v.current_line
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        _print_human(filtered, verdicts, sys.stdout)
        print(f"\n{len(filtered)} entr{'y' if len(filtered) == 1 else 'ies'} shown.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
