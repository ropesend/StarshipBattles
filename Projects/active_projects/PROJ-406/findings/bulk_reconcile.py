"""PROJ-406 bookkeeping helper: bulk-tick task checkboxes & set phase Status.

Idempotent — running twice is a no-op.

Usage:
    python Projects/active_projects/PROJ-406/findings/bulk_reconcile.py <file> [--note "text"] [--leave-task TASK_ID ...]

Behavior:
- Sets `**Status:** Not Started` -> `**Status:** Complete` at the top of the file.
- Ticks every `- [ ]` to `- [x]`.
- If --leave-task is given, leaves the boxes inside those task subsections unticked.
- If --note is given, appends a one-line note paragraph just under the file H1.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def reconcile(path: Path, leave_tasks: list[str], note: str | None) -> None:
    text = path.read_text(encoding="utf-8")

    # 1. Status -> Complete (case-insensitive).
    text = re.sub(
        r"^\*\*Status:\*\*\s*Not Started\s*$",
        "**Status:** Complete",
        text,
        flags=re.MULTILINE,
    )

    # 2. Tick checkboxes globally, then re-untick any inside `### Task X.Y` we want to leave.
    text = text.replace("- [ ]", "- [x]")

    if leave_tasks:
        lines = text.splitlines(keepends=True)
        leave_set = set(leave_tasks)
        in_leave_task = False
        for i, line in enumerate(lines):
            m = re.match(r"^### Task (\S+):", line)
            if m:
                in_leave_task = m.group(1) in leave_set
                continue
            # Stop on next major heading.
            if line.startswith("### ") or line.startswith("---"):
                in_leave_task = False
            if in_leave_task:
                lines[i] = line.replace("- [x]", "- [ ]")
        text = "".join(lines)

    if note:
        # Insert note immediately after first H1.
        text = re.sub(
            r"(^# [^\n]+\n)",
            r"\1\n> **PROJ-406 reconciliation note:** " + note + "\n",
            text,
            count=1,
            flags=re.MULTILINE,
        )

    path.write_text(text, encoding="utf-8")
    print(f"Reconciled {path}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("path", type=Path)
    p.add_argument("--leave-task", action="append", default=[])
    p.add_argument("--note", default=None)
    args = p.parse_args()
    reconcile(args.path, args.leave_task, args.note)


if __name__ == "__main__":
    main()
