#!/usr/bin/env python3
"""Aggregate per-install skill usage counters into a single summary.

Reads `AgentCoordination/generated/skill_usage/by_install/*.json` and writes
`AgentCoordination/generated/skill_usage/summary.json`. The summary is the
artifact a human reviews to identify rarely-used skills as cleanup candidates.

Per the plan: counters are advisory only. This tool never deletes anything.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    _here = Path(__file__).resolve()
    for _ in range(6):
        if (_here.parent / "AGENTS.md").exists():
            sys.path.insert(0, str(_here.parent))
            break
        _here = _here.parent

SCHEMA_VERSION = 1


def _aggregate(by_install_dir: Path) -> dict[str, object]:
    skills: dict[str, dict[str, object]] = {}
    if by_install_dir.is_dir():
        for path in sorted(by_install_dir.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                print(f"warning: skipping malformed {path.name}: {exc}", file=sys.stderr)
                continue
            install_id = payload.get("install_id") if isinstance(payload, dict) else None
            install_skills = payload.get("skills") if isinstance(payload, dict) else None
            if not isinstance(install_id, str) or not isinstance(install_skills, dict):
                print(f"warning: skipping malformed {path.name}: missing install_id or skills", file=sys.stderr)
                continue
            for skill_name, entry in install_skills.items():
                if not isinstance(entry, dict):
                    continue
                count = int(entry.get("count", 0))
                summary_entry = skills.setdefault(skill_name, {
                    "total_count": 0,
                    "by_install": {},
                    "last_used": "",
                })
                summary_entry["total_count"] = int(summary_entry["total_count"]) + count  # type: ignore[arg-type]
                by_install: dict[str, int] = summary_entry["by_install"]  # type: ignore[assignment]
                by_install[install_id] = by_install.get(install_id, 0) + count
                last_used = entry.get("last_used", "")
                if isinstance(last_used, str) and last_used > str(summary_entry.get("last_used", "")):
                    summary_entry["last_used"] = last_used
    return {
        "schema_version": SCHEMA_VERSION,
        "skills": skills,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate skill usage counters into summary.json")
    parser.add_argument("--repo-root", type=Path, default=None)
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve() if args.repo_root else Path.cwd()
    by_install = repo_root / "AgentCoordination" / "generated" / "skill_usage" / "by_install"
    summary = _aggregate(by_install)
    summary_path = repo_root / "AgentCoordination" / "generated" / "skill_usage" / "summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
