#!/usr/bin/env python3
"""
Build cycle_plan.md for the complexity loop from a single project.

Unlike the continuous_loop version (which reads approval logs for multiple
projects), this creates a cycle_plan for exactly ONE project at a time.

Usage:
    python Projects/complexity_loop/populate_complexity_plan.py PROJ-200
    python Projects/complexity_loop/populate_complexity_plan.py PROJ-200 --output custom_plan.md
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.parent
ACTIVE_DIR = WORKSPACE / "Projects" / "active_projects"
DEFAULT_OUTPUT = WORKSPACE / "Projects" / "complexity_loop" / "cycle_plan.md"


def read_project_metadata(project_id: str) -> dict | None:
    """Read project title and phase count from plan.md."""
    plan_path = ACTIVE_DIR / project_id / "plan.md"
    if not plan_path.exists():
        return None

    content = plan_path.read_text(encoding="utf-8")

    # Extract title from first heading: # PROJ-XX: Title
    title_match = re.search(r"^# " + re.escape(project_id) + r":\s*(.+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Unknown"

    # Count phases from Quick Status table
    phase_matches = re.findall(
        r"\|\s*\d+\.\s*.+?\s*\|",
        content,
    )
    phase_count = len(phase_matches) if phase_matches else 1

    return {
        "id": project_id,
        "title": title,
        "phases": phase_count,
    }


def generate_cycle_plan(project: dict) -> str:
    """Generate cycle_plan.md content for a single project."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    pid = project["id"]
    title = project["title"]
    phases = project["phases"]

    lines = []

    # Header
    lines.extend([
        "# Complexity Loop - Cycle Plan",
        "",
        f"*Generated: {timestamp}*",
        "",
        "---",
        "",
    ])

    # Agent Context
    lines.extend([
        "## Agent Context",
        "",
        f"**Last Session:** {timestamp}",
        "**Last Completed:** Cycle plan generated",
        "**Current Status:** Ready to execute",
        f"**Current Project:** {pid}",
        "**Current Phase:** Phase 1",
        "**Test Status:** Not yet run",
        "**Active Blockers:** None",
        "",
        "**Handoff Notes:**",
        f"- Project {pid} created for complexity reduction",
        f"- {phases} phase(s) planned",
        "- Read project plan.md for full context",
        f"- Target context in findings/complexity_target.md",
        "",
        "---",
        "",
    ])

    # Master Task List
    lines.extend([
        "## Master Task List",
        "",
        f"- [ ] **{pid}: {title}**",
        f"  Phases: {phases}",
        f"  Plan: `Projects/active_projects/{pid}/plan.md`",
        "",
        "---",
        "",
    ])

    # Execution Log
    lines.extend([
        "## Execution Log",
        "",
        "| Timestamp | Project | Action | Status | Tests | Commit | Notes |",
        "|-----------|---------|--------|--------|-------|--------|-------|",
        f"| {timestamp} | {pid} | Plan generated | Ready | - | - | Automated complexity loop |",
        "",
        "---",
        "",
    ])

    # Instructions
    lines.extend([
        "## Instructions",
        "",
        "- Execute one phase per session, then exit",
        "- Update Agent Context and Execution Log before exiting",
        "- All tests must pass before committing",
        "- Audit runs automatically after all phases complete",
        "- Maximum 5 audit cycles per project before moving on",
        "- If the function is irreducibly complex, skip it",
        "- Follow all protocols in `Projects/protocols/`",
        "- Prioritize long-term maintainability over short-term convenience",
        "- Minimize technical debt in all decisions",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Build cycle_plan.md for complexity loop"
    )
    parser.add_argument(
        "project_id",
        help="Project ID (e.g., PROJ-200)",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Output file path (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    meta = read_project_metadata(args.project_id)
    if not meta:
        print(f"ERROR: Project not found: {args.project_id}", file=sys.stderr)
        sys.exit(1)

    print(f"Project: {meta['id']} - {meta['title']}")
    print(f"Phases: {meta['phases']}")

    content = generate_cycle_plan(meta)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    print(f"Generated: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
