#!/usr/bin/env python3
"""Fast prefix-compliance check for agent skill surfaces.

Runs against the inventory's surface map and fails when a skill on a known
surface does not begin with the expected prefix or the reserved `shared-`
cross-agent prefix.

Designed to run in pre-commit hooks and CI before the full validator is
available.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    _here = Path(__file__).resolve()
    for _ in range(6):
        if (_here.parent / "AGENTS.md").exists():
            sys.path.insert(0, str(_here.parent))
            break
        _here = _here.parent

from Tools.agent_coordination.inventory_agent_surfaces import SURFACES, _find_project_root  # noqa: E402

SHARED_PREFIX = "shared-"


def run(repo_root: Path) -> tuple[int, list[dict[str, str]]]:
    """Return (exit_code, findings)."""
    findings: list[dict[str, str]] = []
    resolved = repo_root.resolve()
    for config in SURFACES:
        surface_path = str(config["surface_path"])
        expected_prefix = str(config["expected_prefix"])
        surface_dir = resolved / surface_path
        if not surface_dir.is_dir():
            continue
        for skill_dir in sorted(surface_dir.iterdir(), key=lambda p: p.name):
            if not skill_dir.is_dir():
                continue
            if not (skill_dir / "SKILL.md").exists():
                continue
            name = skill_dir.name
            if name.startswith(expected_prefix) or name.startswith(SHARED_PREFIX):
                continue
            findings.append({
                "surface_path": surface_path,
                "skill_name": name,
                "expected_prefix": expected_prefix,
            })
    return (1 if findings else 0), findings


def _format_findings(findings: list[dict[str, str]]) -> str:
    if not findings:
        return "Prefix check OK: every skill has its expected prefix.\n"
    lines = ["Prefix check FAILED:"]
    for finding in findings:
        lines.append(
            f"  [{finding['surface_path']}] {finding['skill_name']!r} "
            f"is missing required prefix {finding['expected_prefix']!r}"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check that every skill has its expected agent prefix")
    parser.add_argument("--repo-root", type=Path, default=None)
    args = parser.parse_args(argv)
    repo_root = args.repo_root or _find_project_root()
    rc, findings = run(repo_root)
    print(_format_findings(findings), end="")
    return rc


if __name__ == "__main__":
    sys.exit(main())
