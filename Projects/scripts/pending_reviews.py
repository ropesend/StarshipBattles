#!/usr/bin/env python3
"""03c: list pending/in-progress/completed reviews for a project.

Walks AgentCoordination/opencodereview/{pending,in_progress,completed}_review_requests/
and filters by project_id (matched against the request body's `Project_id`
or by parsing the title).

Usage:
    python Projects/scripts/pending_reviews.py PROJ-XX
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

PROJECT_ROOT = SCRIPTS_DIR.parent.parent
DAEMON_DIR = PROJECT_ROOT / "AgentCoordination" / "opencodereview"
PENDING = DAEMON_DIR / "pending_review_requests"
IN_PROGRESS = DAEMON_DIR / "in_progress_review_requests"
COMPLETED = DAEMON_DIR / "completed_review_requests"


def _matches_project(content: str, project_id: str) -> bool:
    # Match either explicit "project_id: PROJ-XX" coverage line or title containing PROJ-XX.
    if re.search(rf"\*\*project_id:\*\*\s*{re.escape(project_id)}\b", content):
        return True
    if re.search(rf"# Review Request:.*\b{re.escape(project_id)}\b", content):
        return True
    return False


def _summarize(req_path: Path, project_id: str, bucket: str) -> str | None:
    try:
        content = req_path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not _matches_project(content, project_id):
        return None
    fields = []
    fields.append(f"[{bucket}] {req_path.stem}")
    m = re.search(r"\*\*focus_phase:\*\*\s*(\S+)", content)
    if m:
        fields.append(f"focus={m.group(1)}")
    m = re.search(r"\*\*coverage_set:\*\*\s*(.+)", content)
    if m:
        fields.append(f"coverage=[{m.group(1).strip()}]")
    m = re.search(r"\*\*Status:\*\*\s*(\S+)", content)
    if m:
        fields.append(f"status={m.group(1)}")
    return "  " + "  ".join(fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="03c pending/in-flight reviews for a project")
    parser.add_argument("project_id")
    args = parser.parse_args()

    print(f"# Reviews for {args.project_id}")
    found = False
    for bucket, d in (("pending", PENDING), ("in_progress", IN_PROGRESS), ("completed", COMPLETED)):
        if not d.exists():
            continue
        for req in sorted(d.glob("req_*.md")):
            line = _summarize(req, args.project_id, bucket)
            if line:
                print(line)
                found = True
    if not found:
        print("  (none)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
