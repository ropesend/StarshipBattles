#!/usr/bin/env python3
"""
Trim the Execution Log in cycle_plan.md to prevent context window overflow.

Keeps the table header and the most recent N rows, archiving older rows
into a separate file. Also strips completed project entries from the
Master Task List (projects marked [x] or [~]).

Usage:
    python Projects/continuous_loop/trim_execution_log.py
    python Projects/continuous_loop/trim_execution_log.py --keep 20
    python Projects/continuous_loop/trim_execution_log.py --plan-file continuous_loop/cycle_plan.md
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.parent
DEFAULT_PLAN = WORKSPACE / "Projects" / "continuous_loop" / "cycle_plan.md"
DEFAULT_ARCHIVE = WORKSPACE / "Projects" / "continuous_loop" / "cycle_execution_archive.md"
DEFAULT_KEEP = 20


def trim_execution_log(plan_path: Path, keep: int, archive_path: Path) -> dict:
    """Trim execution log rows and completed projects from cycle_plan.md.

    Returns dict with counts of what was trimmed.
    """
    if not plan_path.exists():
        print(f"ERROR: Plan file not found: {plan_path}", file=sys.stderr)
        sys.exit(1)

    content = plan_path.read_text(encoding="utf-8")
    stats = {"log_rows_archived": 0, "projects_stripped": 0, "original_size": len(content)}

    # ── Trim Execution Log ──
    # Find the execution log table: header line, separator line, then data rows
    log_section = re.search(
        r"(## Execution Log\s*\n)"
        r"(\| Timestamp .+\n)"    # header row
        r"(\|[-| ]+\n)"           # separator row
        r"((?:\| .+\n)*)",        # data rows (0 or more)
        content,
    )

    if log_section:
        section_heading = log_section.group(1)
        header_row = log_section.group(2)
        separator_row = log_section.group(3)
        data_rows_text = log_section.group(4)

        data_rows = [line for line in data_rows_text.splitlines() if line.strip()]
        total_rows = len(data_rows)

        if total_rows > keep:
            rows_to_archive = data_rows[: total_rows - keep]
            rows_to_keep = data_rows[total_rows - keep :]
            stats["log_rows_archived"] = len(rows_to_archive)

            # Append archived rows to archive file
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            with open(archive_path, "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n## Archived {timestamp} ({len(rows_to_archive)} rows)\n\n")
                f.write(header_row)
                f.write(separator_row)
                for row in rows_to_archive:
                    f.write(row + "\n")

            # Rebuild the section with only the kept rows
            kept_text = "\n".join(rows_to_keep) + "\n" if rows_to_keep else ""
            new_section = section_heading + header_row + separator_row + kept_text
            content = content[: log_section.start()] + new_section + content[log_section.end() :]

    # ── Strip completed projects from Master Task List ──
    # Remove entire project blocks that are marked [x] or [~]
    # Pattern: "- [x] **PROJ-..." followed by indented lines and "---"
    completed_pattern = re.compile(
        r"- \[[xX~]\] \*\*PROJ-\d+:.+?\n"  # checkbox line
        r"(?:  .+\n)*"                       # indented detail lines
        r"(?:\n---\n)?",                     # optional separator
    )

    completed_matches = list(completed_pattern.finditer(content))
    if completed_matches:
        stats["projects_stripped"] = len(completed_matches)
        # Remove in reverse order to preserve positions
        for m in reversed(completed_matches):
            content = content[: m.start()] + content[m.end() :]

    # Write back
    plan_path.write_text(content, encoding="utf-8")
    stats["final_size"] = len(content)
    stats["size_reduction"] = stats["original_size"] - stats["final_size"]

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Trim execution log in cycle_plan.md to prevent context overflow"
    )
    parser.add_argument(
        "--plan-file",
        default=str(DEFAULT_PLAN),
        help=f"Path to cycle_plan.md (default: {DEFAULT_PLAN})",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=DEFAULT_KEEP,
        help=f"Number of recent log rows to keep (default: {DEFAULT_KEEP})",
    )
    parser.add_argument(
        "--archive",
        default=str(DEFAULT_ARCHIVE),
        help=f"Archive file for trimmed rows (default: {DEFAULT_ARCHIVE})",
    )
    args = parser.parse_args()

    plan_path = Path(args.plan_file)
    archive_path = Path(args.archive)

    stats = trim_execution_log(plan_path, args.keep, archive_path)

    if stats["log_rows_archived"] > 0 or stats["projects_stripped"] > 0:
        print(
            f"Trimmed: {stats['log_rows_archived']} log rows archived, "
            f"{stats['projects_stripped']} completed projects stripped, "
            f"size reduced by {stats['size_reduction']} bytes"
        )
    else:
        print("No trimming needed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
