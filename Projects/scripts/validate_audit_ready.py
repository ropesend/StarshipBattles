#!/usr/bin/env python3
"""
Validate that a project is ready for audit.

Usage:
    python validate_audit_ready.py PROJ-08
    python validate_audit_ready.py PROJ-08 --run-tests  # Also run pytest
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.markdown_parser import parse_project_file, find_incomplete_tasks, find_extracted_phases
from utils.index_manager import get_project_entry, is_project_archived, project_exists


class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passes: List[str] = []

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


def _validate_03c_audit_gate(project_id: str, result: "ValidationResult") -> None:
    """Apply the 03c rigorous final audit gate (Projects/protocols/03c).

    Hard-fails if ANY of:
      1. A finding has status `open` or `addressed_pending_review`.
      2. A `deferred_until_phase` finding's target phase is at or before the
         latest clean coverage and unresolved.
      3. The latest clean review's `coverage_set` does not include all
         non-skipped phases.
      4. The project branch tip SHA differs from the audited SHA.

    No-op for legacy projects without `phase_state.json`.
    """
    state_path = (
        Path(__file__).resolve().parent.parent / "active_projects" / project_id / "phase_state.json"
    )
    if not state_path.exists():
        return  # legacy project, no 03c gate applies

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from phase_workflow import state as state_mod
    except ImportError:
        result.errors.append(
            "03c gate: cannot import phase_workflow.state — "
            "Projects/scripts/phase_workflow/ is missing or broken"
        )
        return

    try:
        s = state_mod.load_state(state_path)
    except (ValueError, OSError) as e:
        result.errors.append(f"03c gate: cannot load phase_state.json: {e}")
        return

    # Rule 1: no open or addressed-pending findings.
    blocking_statuses = {"open", "addressed_pending_review"}
    blocking = [
        (fid, f["status"], f.get("summary", ""))
        for fid, f in s["findings"].items()
        if f["status"] in blocking_statuses
    ]
    if blocking:
        for fid, status, summary in blocking[:5]:
            result.errors.append(
                f"03c gate: finding {fid} status={status} ({summary[:80]})"
            )
        if len(blocking) > 5:
            result.errors.append(f"03c gate: ... and {len(blocking) - 5} more open findings")

    # Identify latest clean review.
    clean_reviews = [
        r for r in s["reviews"].values()
        if r["result_status"] == "completed_clean" and r.get("superseded_by") is None
    ]
    latest_clean = (
        max(clean_reviews, key=lambda r: r["review_sequence"]) if clean_reviews else None
    )

    # Rule 2: deferred-until-phase target reached but unresolved.
    if latest_clean:
        latest_coverage = set(latest_clean["coverage_set"])
        for fid, f in s["findings"].items():
            if f["status"] != "deferred_until_phase":
                continue
            target = f.get("deferred_until_phase")
            if target and target in latest_coverage:
                result.errors.append(
                    f"03c gate: finding {fid} deferred to {target} (now covered) but unresolved"
                )
    else:
        result.errors.append("03c gate: no clean cumulative review on record")

    # Rule 3: every non-skipped phase covered by the latest clean review.
    if latest_clean:
        non_skipped = {
            pid for pid, p in s["phases"].items()
            if p["status"] != "scrapped"
        }
        latest_coverage = set(latest_clean["coverage_set"])
        missing = sorted(non_skipped - latest_coverage)
        if missing:
            result.errors.append(
                f"03c gate: phases never in a clean review: {', '.join(missing)}"
            )

    # Rule 4: project tip SHA matches audited SHA.
    if latest_clean:
        # We don't shell out to git here; phase_complete records merge SHAs.
        # Latest committed phase merge_sha should equal the latest clean review's tip.
        committed_phases = [
            p for p in s["phases"].values()
            if p.get("merged_into_project_at_sha")
        ]
        if committed_phases:
            latest_merge_sha = max(
                committed_phases,
                key=lambda p: p.get("merged_into_project_at_sha", ""),
            )["merged_into_project_at_sha"]
            if latest_merge_sha and latest_merge_sha != latest_clean["project_tip_sha"]:
                result.errors.append(
                    f"03c gate: project tip ({latest_merge_sha[:8]}) differs from "
                    f"latest clean review SHA ({latest_clean['project_tip_sha'][:8]}); "
                    f"unreviewed work on project branch"
                )

    if not blocking and latest_clean and not result.errors:
        result.passes.append(
            f"03c gate: clean. Latest review={latest_clean['review_sequence']} "
            f"covers {len(latest_clean['coverage_set'])} phases at "
            f"SHA {latest_clean['project_tip_sha'][:8]}"
        )


def validate_audit_ready(project_id: str, run_tests: bool = False) -> ValidationResult:
    """Validate that a project is ready for audit."""
    result = ValidationResult()

    try:
        project_data = parse_project_file(project_id)
    except FileNotFoundError as e:
        result.errors.append(str(e))
        return result

    # 03c rigorous audit gate (no-op for legacy projects).
    _validate_03c_audit_gate(project_id, result)

    # Check 1: All phases complete or deferred
    for phase in project_data.phases:
        status_lower = phase.status.lower()
        if "complete" in status_lower:
            result.passes.append(f"Phase {phase.number}: {phase.status}")
        elif "extracted" in status_lower:
            # Extracted phases are acceptable - will be checked separately
            result.passes.append(f"Phase {phase.number}: {phase.status} (extracted)")
        elif "deferred" in status_lower or "skipped" in status_lower:
            result.warnings.append(f"Phase {phase.number}: {phase.status} (acceptable)")
        elif "not started" in status_lower:
            result.errors.append(f"Phase {phase.number}: {phase.status} - not started")
        else:
            result.errors.append(f"Phase {phase.number}: {phase.status} - not complete")

    # Check 1.5: Extracted phase sub-project dependencies
    extracted_phases = find_extracted_phases(project_data)
    for phase_num, sub_project_id in extracted_phases:
        if not project_exists(sub_project_id):
            result.errors.append(
                f"Phase {phase_num}: Sub-project {sub_project_id} NOT FOUND - critical error"
            )
        elif is_project_archived(sub_project_id):
            result.passes.append(
                f"Phase {phase_num}: Sub-project {sub_project_id} is ARCHIVED (auto-complete ready)"
            )
        else:
            result.warnings.append(
                f"Phase {phase_num}: Sub-project {sub_project_id} still ACTIVE (phase pending)"
            )

    # Check 2: All tasks complete
    incomplete = find_incomplete_tasks(project_data)
    if incomplete:
        total_incomplete = len(incomplete)
        result.errors.append(f"{total_incomplete} tasks have incomplete subtasks:")
        for phase, task, unchecked in incomplete[:5]:  # Show first 5
            result.errors.append(f"  Phase {phase.number} > Task {task.id}: {len(unchecked)} unchecked")
        if total_incomplete > 5:
            result.errors.append(f"  ... and {total_incomplete - 5} more")
    else:
        total_tasks = sum(len(phase.tasks) for phase in project_data.phases)
        result.passes.append(f"All {total_tasks} tasks complete")

    # Check 3: No blockers
    if project_data.current_state:
        blockers = project_data.current_state.blockers
        if blockers and blockers.lower() not in ['none', 'no', '']:
            result.errors.append(f"Blockers reported: {blockers}")
        else:
            result.passes.append("No blockers reported")

    # Check 4: Project status in index
    entry = get_project_entry(project_id)
    if entry:
        if entry.status == "Awaiting Verification":
            result.passes.append(f"Index status: {entry.status}")
        elif entry.status == "In Progress":
            result.warnings.append(f"Index status is '{entry.status}', expected 'Awaiting Verification'")
        else:
            result.warnings.append(f"Index status: {entry.status}")

    # Check 5: Run tests if requested
    # NOTE: Audit ALWAYS runs full test suite (no --testmon)
    # This ensures complete verification regardless of testmon state
    if run_tests:
        print("\nRunning pytest (FULL SUITE - no testmon)...")
        try:
            proc = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if proc.returncode == 0:
                result.passes.append("All tests passed")
            else:
                result.errors.append(f"Tests failed (exit code {proc.returncode})")
                # Show last few lines of output
                lines = proc.stdout.split('\n')[-10:]
                for line in lines:
                    if line.strip():
                        result.errors.append(f"  {line}")
        except subprocess.TimeoutExpired:
            result.errors.append("Tests timed out after 5 minutes")
        except FileNotFoundError:
            result.warnings.append("pytest not found - skipping test run")

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Validate project is ready for audit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python validate_audit_ready.py PROJ-08
    python validate_audit_ready.py PROJ-08 --run-tests
        """
    )
    parser.add_argument('project_id', help='Project ID (e.g., PROJ-08)')
    parser.add_argument('--run-tests', action='store_true',
                        help='Also run pytest to verify tests pass')

    args = parser.parse_args()

    print(f"\n{'=' * 50}")
    print(f"Audit Readiness Check: {args.project_id}")
    print('=' * 50)

    result = validate_audit_ready(args.project_id, args.run_tests)

    print("\nCHECKING: Phase completion")
    for msg in [m for m in result.passes if 'Phase' in m]:
        print(f"  [PASS] {msg}")
    for msg in [m for m in result.warnings if 'Phase' in m]:
        print(f"  [WARN] {msg}")
    for msg in [m for m in result.errors if 'Phase' in m]:
        print(f"  [FAIL] {msg}")

    print("\nCHECKING: Task completion")
    for msg in [m for m in result.passes if 'task' in m.lower()]:
        print(f"  [PASS] {msg}")
    for msg in [m for m in result.errors if 'task' in m.lower()]:
        print(f"  [FAIL] {msg}")

    print("\nCHECKING: Blockers and status")
    for msg in result.passes:
        if 'Phase' not in msg and 'task' not in msg.lower() and 'test' not in msg.lower():
            print(f"  [PASS] {msg}")
    for msg in result.warnings:
        if 'Phase' not in msg:
            print(f"  [WARN] {msg}")
    for msg in result.errors:
        if 'Phase' not in msg and 'task' not in msg.lower() and 'test' not in msg.lower():
            print(f"  [FAIL] {msg}")

    if args.run_tests:
        print("\nCHECKING: Tests")
        for msg in [m for m in result.passes if 'test' in m.lower()]:
            print(f"  [PASS] {msg}")
        for msg in [m for m in result.errors if 'test' in m.lower()]:
            print(f"  [FAIL] {msg}")

    print(f"\n{'=' * 50}")
    print(f"RESULT: {'PASSED' if result.passed else 'FAILED'}")
    if result.passed:
        print("Project is ready for audit.")
    else:
        print(f"{len(result.errors)} errors, {len(result.warnings)} warnings")
        print("Fix errors before proceeding with audit.")
    print('=' * 50)

    sys.exit(0 if result.passed else 1)


if __name__ == '__main__':
    main()
