#!/usr/bin/env python3
"""Back-fill rewrite for legacy unprefixed slash commands left in current docs.

The original prefix renamer rewrote references inside skill directories,
adapter docs, opencode.json, and protocols. It did not reach the broader
README/manifest/ticket scope. This one-shot script rewrites those leftover
`/proj-start`, `$proj-start`, `/audit-shrink`, etc. invocations to their
post-rename forms using the historical migration map.

Idempotent: rerunning produces no changes once everything is already
prefixed.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    _here = Path(__file__).resolve()
    for _ in range(6):
        if (_here.parent / "AGENTS.md").exists():
            sys.path.insert(0, str(_here.parent))
            break
        _here = _here.parent

from Tools.agent_coordination.validate_agent_surfaces import (  # noqa: E402
    LEGACY_SCAN_EXCLUDE_DIRS,
    LEGACY_SCAN_GLOBS,
    LEGACY_SCAN_TARGETS,
)

# Historical migration map. Keys are the pre-rename names; values are the
# post-rename names. For skills that existed in both Claude and Antigravity,
# user-facing READMEs almost always meant the Claude version, so default to
# the `claude-` prefix. Antigravity-only skills (originally only in
# `.agent/skills/`) get `anti-`. The single OpenCode skill gets `ocode-`.
HISTORICAL_RENAME_MAP: dict[str, str] = {
    # Antigravity-only originals
    "proj-close": "anti-proj-close",
    "proj-sequential": "anti-proj-sequential",
    "debug-sequential": "anti-debug-sequential",
    "deep-dive-sequential": "anti-deep-dive-sequential",
    # OpenCode original
    "audit-shrink": "ocode-audit-shrink",
    # Claude-only originals
    "proj-parallel": "claude-proj-parallel",
    "debug-parallel": "claude-debug-parallel",
    "deep-dive-parallel": "claude-deep-dive-parallel",
    # Shared (existed in both Claude and Antigravity); README context = Claude
    "analysis-complexity": "claude-analysis-complexity",
    "analysis-dead-code": "claude-analysis-dead-code",
    "analysis-sweep": "claude-analysis-sweep",
    "fix-crash": "claude-fix-crash",
    "loc": "claude-loc",
    "proj-add-to-plan": "claude-proj-add-to-plan",
    "proj-archive": "claude-proj-archive",
    "proj-audit": "claude-proj-audit",
    "proj-continue": "claude-proj-continue",
    "proj-extract-phase": "claude-proj-extract-phase",
    "proj-manage-plan": "claude-proj-manage-plan",
    "proj-reset-baseline": "claude-proj-reset-baseline",
    "proj-review": "claude-proj-review",
    "proj-revise": "claude-proj-revise",
    "proj-start": "claude-proj-start",
    "qa-feedback": "claude-qa-feedback",
    "qa-triage": "claude-qa-triage",
    "ticket-add": "claude-ticket-add",
    "ticket-answer": "claude-ticket-answer",
    "ticket-batch-close": "claude-ticket-batch-close",
    "ticket-close": "claude-ticket-close",
    "ticket-continue": "claude-ticket-continue",
    "ticket-deep-dive": "claude-ticket-deep-dive",
    "ticket-next": "claude-ticket-next",
    "ticket-reject": "claude-ticket-reject",
    "ticket-update": "claude-ticket-update",
    "ticket-work": "claude-ticket-work",
    "triage-to-proj": "claude-triage-to-proj",
    "validate-designs": "claude-validate-designs",
}


def _build_pattern() -> re.Pattern[str]:
    # Sort longest-first so e.g. `proj-extract-phase` matches before `proj-`.
    sorted_old = sorted(HISTORICAL_RENAME_MAP.keys(), key=len, reverse=True)
    alt = "|".join(re.escape(name) for name in sorted_old)
    return re.compile(rf"(?P<sigil>(?<![A-Za-z0-9_-])[/$])(?P<name>{alt})\b")


def _scan_files(repo_root: Path) -> list[Path]:
    candidates: set[Path] = set()
    for rel in LEGACY_SCAN_TARGETS:
        path = repo_root / rel
        if path.is_file():
            candidates.add(path)
    for pattern in LEGACY_SCAN_GLOBS:
        for path in repo_root.glob(pattern):
            if path.is_file():
                candidates.add(path)
    for surface in (".claude/skills", ".agent/skills", ".agents/skills", ".opencode/skills"):
        d = repo_root / surface
        if d.is_dir():
            for skill_md in d.rglob("SKILL.md"):
                candidates.add(skill_md)
    out: list[Path] = []
    for path in candidates:
        rel = path.relative_to(repo_root).as_posix()
        if any(rel.startswith(prefix + "/") or rel == prefix for prefix in LEGACY_SCAN_EXCLUDE_DIRS):
            continue
        out.append(path)
    return sorted(out, key=lambda p: p.as_posix())


def rewrite_file(path: Path, pattern: re.Pattern[str]) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return 0
    count = 0

    def _replace(match: re.Match[str]) -> str:
        nonlocal count
        sigil = match.group("sigil")
        old_name = match.group("name")
        new_name = HISTORICAL_RENAME_MAP[old_name]
        count += 1
        return f"{sigil}{new_name}"

    new_text = pattern.sub(_replace, text)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Back-fill legacy unprefixed slash commands in current docs")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be rewritten without modifying files.")
    args = parser.parse_args(argv)

    if args.repo_root is None:
        repo_root = Path.cwd()
    else:
        repo_root = args.repo_root.resolve()

    pattern = _build_pattern()
    total_rewrites = 0
    files_changed: list[str] = []
    for path in _scan_files(repo_root):
        if args.dry_run:
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            matches = pattern.findall(text)
            if matches:
                rel = path.relative_to(repo_root).as_posix()
                files_changed.append(f"{rel}: {len(matches)}")
                total_rewrites += len(matches)
        else:
            count = rewrite_file(path, pattern)
            if count:
                rel = path.relative_to(repo_root).as_posix()
                files_changed.append(f"{rel}: {count}")
                total_rewrites += count

    if args.dry_run:
        print("Dry-run; would rewrite:")
    else:
        print("Rewrites applied:")
    for line in files_changed:
        print(f"  {line}")
    print(f"Total: {total_rewrites}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
