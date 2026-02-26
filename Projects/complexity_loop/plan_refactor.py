#!/usr/bin/env python3
"""
Generate a refactoring project for the most complex function.

Runs the complexity audit, selects the worst target, creates a PROJ-XX
project, and outputs the project ID. The actual detailed plan is generated
by a Claude agent (ANALYSIS_WORKER.md) — this script just scaffolds the
project and writes initial context.

Usage:
    python Projects/complexity_loop/plan_refactor.py
    python Projects/complexity_loop/plan_refactor.py --threshold 20
    python Projects/complexity_loop/plan_refactor.py --dry-run
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.parent

# Add project scripts to path for create_project
sys.path.insert(0, str(WORKSPACE / "Projects" / "scripts"))
from create_project import create_project


def run_audit(threshold: int) -> dict:
    """Run the complexity audit and return parsed JSON results."""
    cmd = [
        sys.executable,
        str(WORKSPACE / "Projects" / "complexity_loop" / "run_complexity_audit.py"),
        "--threshold", str(threshold),
        "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE))
    if result.returncode != 0:
        print(f"ERROR: Audit failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    return json.loads(result.stdout)


def generate_target_context(target: dict, all_findings: list[dict]) -> str:
    """Build the context document for the analysis agent.

    This goes into the project's findings/ directory so the analysis
    and review agents have full context about the target.
    """
    # Find other complex functions in the same file
    same_file = [f for f in all_findings if f["file"] == target["file"]]
    same_file.sort(key=lambda x: x["cc"], reverse=True)

    lines = [
        f"# Complexity Reduction Target",
        f"",
        f"## Primary Target",
        f"- **File:** `{target['file']}`",
        f"- **Function:** `{target['function']}`",
        f"- **Line:** {target['line']}",
        f"- **Cyclomatic Complexity:** {target['cc']} (grade {target['grade']})",
        f"- **Type:** {target['type']}",
    ]

    if target.get("class_name"):
        lines.append(f"- **Class:** `{target['class_name']}`")

    if target.get("length"):
        lines.append(f"- **Length:** ~{target['length']} lines")

    lines.extend([
        f"",
        f"## Goal",
        f"Reduce the cyclomatic complexity of `{target['function']}` to below 20.",
        f"If the function cannot be reduced below 20 without compromising",
        f"readability or correctness, document why and add to the skip list.",
        f"",
        f"## Other Complex Functions in Same File",
    ])

    if len(same_file) > 1:
        lines.append(f"| Function | Line | CC | Grade |")
        lines.append(f"|----------|------|----|-------|")
        for f in same_file:
            marker = " **<-- TARGET**" if f["function"] == target["function"] else ""
            cn = f"{f['class_name']}." if f.get("class_name") else ""
            lines.append(
                f"| `{cn}{f['function']}` | {f['line']} | {f['cc']} | {f['grade']} |{marker}"
            )
    else:
        lines.append("No other complex functions in this file.")

    lines.extend([
        f"",
        f"## Constraints",
        f"- All existing tests must continue to pass",
        f"- No behavioral changes — pure refactoring",
        f"- Prefer extracting helper methods over restructuring",
        f"- If the function is irreducibly complex, skip it rather than break it",
        f"- Document all decisions in decisions.md",
    ])

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Generate a refactoring project for the most complex function"
    )
    parser.add_argument(
        "--threshold", type=int, default=20,
        help="CC threshold (default: 20)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be created without creating it",
    )
    args = parser.parse_args()

    # Run audit
    audit = run_audit(args.threshold)

    if not audit["results"]:
        print("ALL CLEAR: No functions above threshold. Nothing to refactor.")
        print(f"  Threshold: {args.threshold}")
        print(f"  Skipped: {audit['skipped']}")
        sys.exit(2)  # Exit code 2 = nothing to do (success condition)

    target = audit["results"][0]

    class_prefix = f"{target['class_name']}." if target.get("class_name") else ""
    title = f"Reduce complexity: {class_prefix}{target['function']} (CC {target['cc']})"
    short_file = target["file"].replace("game/", "")

    print(f"Target: {target['file']}:{target['line']}")
    print(f"  Function: {class_prefix}{target['function']}")
    print(f"  CC: {target['cc']} (grade {target['grade']})")
    print(f"  Remaining above threshold: {len(audit['results'])}")

    if args.dry_run:
        print(f"\n[DRY RUN] Would create project: \"{title}\"")
        return 0

    # Create the project
    project_id = create_project(title)

    # Write target context into findings/
    project_dir = WORKSPACE / "Projects" / "active_projects" / project_id
    findings_dir = project_dir / "findings"
    findings_dir.mkdir(exist_ok=True)

    context_file = findings_dir / "complexity_target.md"
    context_file.write_text(
        generate_target_context(target, audit["results"]),
        encoding="utf-8",
    )

    # Also write the raw audit data for the analysis agent
    audit_data_file = findings_dir / "audit_data.json"
    audit_data_file.write_text(
        json.dumps({
            "target": target,
            "threshold": args.threshold,
            "total_above_threshold": audit["total_above_threshold"],
            "same_file_findings": [
                f for f in audit["results"] if f["file"] == target["file"]
            ],
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nProject created: {project_id}")
    print(f"  Context: {context_file}")
    print(f"  Audit data: {audit_data_file}")

    # Output just the project ID on the last line for script parsing
    print(f"\nPROJECT_ID={project_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
