#!/usr/bin/env python3
"""Claude Code skill-usage hook adapter.

Reads hook input JSON from stdin, extracts the skill name from either
`UserPromptExpansion` (`command_name`) or `PreToolUse` for the Skill tool
(`tool_input`), and calls `log_skill_usage.py` with `--agent claude` and
the skill name. Tracks ALL skills (prefixed `claude-*` and builtins like
`loop`, `simplify`, `review`, `security-review`, etc.).

Designed to be invoked from `.claude/settings.json` `hooks.UserPromptExpansion`
and `hooks.PreToolUse` (matcher: `Skill`). Failures are silent — a usage hook
must never block a real prompt or tool invocation.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _resolve_repo_root() -> Path:
    """Find the repo root containing AGENTS.md, walking up from this file."""
    current = Path(__file__).resolve().parent
    for _ in range(8):
        if (current / "AGENTS.md").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    # Fallback: use cwd. Hooks always run with cwd at the repo root.
    return Path.cwd()


def _extract_skill_name(payload: dict[str, object]) -> str | None:
    # UserPromptExpansion: skill name is in `command_name`.
    command_name = payload.get("command_name")
    if isinstance(command_name, str) and command_name:
        return command_name
    # PreToolUse for the Skill tool: name lives under `tool_input`.
    tool_name = payload.get("tool_name")
    if tool_name == "Skill":
        tool_input = payload.get("tool_input")
        if isinstance(tool_input, dict):
            for key in ("skill", "skill_name", "name"):
                value = tool_input.get(key)
                if isinstance(value, str) and value:
                    return value
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0

    skill_name = _extract_skill_name(payload)
    if not skill_name or not SKILL_NAME_RE.fullmatch(skill_name):
        return 0

    repo_root = _resolve_repo_root()
    log_script = repo_root / "Tools" / "agent_coordination" / "log_skill_usage.py"
    if not log_script.exists():
        return 0

    try:
        subprocess.run(
            [
                sys.executable,
                str(log_script),
                "--repo-root",
                str(repo_root),
                "--agent",
                "claude",
                "--skill",
                skill_name,
            ],
            cwd=str(repo_root),
            check=False,
            capture_output=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        # Hook must never raise; usage logging is advisory.
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
