#!/usr/bin/env python3
"""Record one skill invocation in the per-checkout usage log.

Per the final coordination plan: counters are advisory only. They identify
cleanup candidates and never authorize automatic deletion.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    _here = Path(__file__).resolve()
    for _ in range(6):
        if (_here.parent / "AGENTS.md").exists():
            sys.path.insert(0, str(_here.parent))
            break
        _here = _here.parent

from Tools.agent_coordination.summarize_skill_usage import write_summary  # noqa: E402

SCHEMA_VERSION = 1
ALLOWED_AGENTS = ("claude", "anti", "ocode", "codex")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ensure_install_id(repo_root: Path) -> str:
    path = repo_root / "AgentCoordination" / "local" / "install_id.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("install_id"), str) and data["install_id"]:
                return data["install_id"]
        except (json.JSONDecodeError, OSError):
            pass
    install_id = uuid.uuid4().hex
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"install_id": install_id, "created_at": _utc_timestamp()}, indent=2) + "\n",
        encoding="utf-8",
    )
    return install_id


def _record_usage(repo_root: Path, install_id: str, agent: str, skill: str) -> None:
    by_install = repo_root / "AgentCoordination" / "generated" / "skill_usage" / "by_install"
    by_install.mkdir(parents=True, exist_ok=True)
    file_path = by_install / f"{install_id}.json"

    payload: dict[str, object]
    if file_path.exists():
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            payload = {}
    else:
        payload = {}

    if not isinstance(payload, dict) or payload.get("install_id") != install_id:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "install_id": install_id,
            "skills": {},
        }

    payload.setdefault("schema_version", SCHEMA_VERSION)
    payload.setdefault("skills", {})
    skills = payload["skills"]
    if not isinstance(skills, dict):
        skills = {}
        payload["skills"] = skills

    entry = skills.get(skill)
    if not isinstance(entry, dict):
        entry = {"count": 0, "last_used": "", "agents": {}}
    entry["count"] = int(entry.get("count", 0)) + 1
    entry["last_used"] = _utc_timestamp()
    agents = entry.get("agents")
    if not isinstance(agents, dict):
        agents = {}
    agents[agent] = int(agents.get(agent, 0)) + 1
    entry["agents"] = agents
    skills[skill] = entry

    file_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record one skill invocation")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--agent", required=True, help="Agent system: claude / anti / ocode / codex")
    parser.add_argument("--skill", required=True, help="Skill name (must match Agent Skills regex)")
    args = parser.parse_args(argv)

    if args.agent not in ALLOWED_AGENTS:
        print(f"Unknown agent {args.agent!r}; allowed: {ALLOWED_AGENTS}", file=sys.stderr)
        return 2
    if not SKILL_NAME_RE.fullmatch(args.skill):
        print(f"Invalid skill name {args.skill!r}; must match ^[a-z0-9]+(-[a-z0-9]+)*$", file=sys.stderr)
        return 2

    repo_root = args.repo_root.resolve() if args.repo_root else Path.cwd()
    install_id = _ensure_install_id(repo_root)
    _record_usage(repo_root, install_id, args.agent, args.skill)
    write_summary(repo_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
