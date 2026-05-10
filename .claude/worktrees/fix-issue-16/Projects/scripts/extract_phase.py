#!/usr/bin/env python3
"""
Extract a phase from an existing project into its own independent project.

This script handles the mechanics of extracting a phase that has grown too
large or complex into its own multi-phase project. The extracted phase is
replaced with a dependency reference, and the new project follows the full
"Start Project" workflow.

Usage:
    python extract_phase.py PROJ-08 3                    # Extract Phase 3
    python extract_phase.py PROJ-08 3 --dry-run          # Preview without changes
    python extract_phase.py PROJ-08 3 --title "Custom"   # Custom title for new project
    python extract_phase.py PROJ-08 3 --reason "Too complex"  # Document reason
"""

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import ACTIVE_DIR, ARCHIVED_DIR
from utils.index_manager import get_next_project_id, add_project_to_index
from utils.markdown_parser import parse_phase_file, Phase
from create_project import create_project


class ExtractionStage(Enum):
    """Stages of extraction for rollback purposes."""
    VALIDATION = 1
    NEW_PROJECT_CREATED = 2
    CONTEXT_FILE_WRITTEN = 3
    ORIGINAL_PHASE_UPDATED = 4
    ORIGINAL_PLAN_UPDATED = 5
    DECISIONS_LOGGED = 6
    COMPLETE = 7


@dataclass
class ExtractResult:
    """Result of an extraction operation."""
    success: bool
    new_project_id: Optional[str]
    source_project_id: str
    phase_num: int
    errors: List[str]
    warnings: List[str]


# Template for extraction context file in new project
EXTRACTION_CONTEXT_TEMPLATE = '''# Extraction Context

This project was created by extracting Phase {phase_num} from {source_project_id}.

**Extraction Date:** {date}
**Reason:** {reason}

---

## Original Phase Information

**Original Objective:** {objective}

**Original Tasks:**
{original_tasks}

---

## Notes for Planning

This context is provided as reference only. The new project should be planned
fresh using the "Start Project" prompt - it is not constrained by the original
phase structure. The original tasks may be reorganized, expanded, or refined
based on proper analysis.

Use `Start Project` prompt to begin planning this project.
'''

# Template for extracted phase checklist (replaces original)
EXTRACTED_PHASE_TEMPLATE = '''# Phase {phase_num}: {phase_name}

> **THIS PHASE HAS BEEN EXTRACTED**
> This phase is being developed as an independent project.
> It will auto-complete when the sub-project is archived (checked during audit).

**Status:** Extracted
**Extracted To:** {new_project_id}
**Extraction Date:** {date}
**Original Objective:** {objective}

---

## Extraction Notice

This phase has been extracted to a standalone project for independent development.

**Sub-Project:** [{new_project_id}](../../{new_project_id}/plan.md)
**Reason:** {reason}

### Completion Behavior
This phase will auto-complete when {new_project_id} is archived. The Audit protocol
(Protocol 04) will check sub-project status during audit cycles.

---

## Original Tasks (Archived for Reference)

The following tasks were part of this phase before extraction. They are preserved
here for historical reference only.

{original_tasks}
'''


def get_phase_checklist_path(project_id: str, phase_num: int) -> Path:
    """Get the path to a phase checklist file."""
    project_dir = ACTIVE_DIR / project_id
    return project_dir / f"phase_{phase_num}_checklist.md"


def get_plan_path(project_id: str) -> Path:
    """Get the path to a project's plan.md file."""
    project_dir = ACTIVE_DIR / project_id
    return project_dir / "plan.md"


def get_decisions_path(project_id: str) -> Path:
    """Get the path to a project's decisions.md file."""
    project_dir = ACTIVE_DIR / project_id
    return project_dir / "decisions.md"


def validate_extraction(source_project_id: str, phase_num: int) -> List[str]:
    """Validate that extraction can proceed.

    Returns a list of error messages (empty if valid).
    """
    errors = []

    # Check source project exists
    project_dir = ACTIVE_DIR / source_project_id
    if not project_dir.exists():
        errors.append(f"Source project not found: {source_project_id}")
        return errors

    # Check phase checklist exists
    phase_path = get_phase_checklist_path(source_project_id, phase_num)
    if not phase_path.exists():
        errors.append(f"Phase checklist not found: {phase_path.name}")
        return errors

    # Parse the phase and check status
    phase = parse_phase_file(phase_path)
    status_lower = phase.status.lower()

    if "extracted" in status_lower:
        errors.append(f"Phase {phase_num} is already extracted")
    elif status_lower == "complete":
        errors.append(f"Phase {phase_num} is already complete - cannot extract")

    return errors


def format_tasks_for_archive(phase: Phase) -> str:
    """Format phase tasks for archival in the extracted phase file."""
    lines = []
    for task in phase.tasks:
        lines.append(f"### Task {task.id}: {task.name} [{task.complexity}]")
        if task.file_path:
            lines.append(f"**File:** `{task.file_path}`")
        if task.tests:
            lines.append(f"**Tests:** {task.tests}")
        lines.append("")
        for checked, text in task.subtasks:
            marker = "[x]" if checked else "[ ]"
            lines.append(f"- {marker} {text}")
        if task.notes:
            lines.append(f"\n**Notes:** {task.notes}")
        lines.append("")
    return "\n".join(lines)


def update_plan_quick_status(plan_content: str, phase_num: int, new_project_id: str) -> str:
    """Update the Quick Status table to show the phase as extracted."""
    # Pattern to match the phase row in Quick Status table
    # Format: | N. Phase Name | Status | [link](file) |
    pattern = rf'(\|\s*{phase_num}\.\s*[^|]+\|)\s*[^|]+\s*(\|[^|]+\|)'
    replacement = rf'\1 **Extracted** \2 -> {new_project_id} |'

    updated, count = re.subn(pattern, replacement, plan_content)

    if count == 0:
        # Try alternate format without the phase number prefix
        pattern2 = rf'(\|[^|]*phase[^|]*{phase_num}[^|]*\|)\s*[^|]+\s*(\|[^|]+\|)'
        updated, count = re.subn(pattern2, replacement, plan_content, flags=re.IGNORECASE)

    return updated


def add_decisions_entry(decisions_content: str, entry: str) -> str:
    """Add an entry to the decisions log table."""
    # Find the table and add after the header row
    # Pattern: | Date | Decision | Rationale |
    # followed by |------|----------|-----------|
    pattern = r'(\|[^\n]*Date[^\n]*\|\n\|[-| ]+\|\n)'

    match = re.search(pattern, decisions_content)
    if match:
        insert_pos = match.end()
        return decisions_content[:insert_pos] + entry + "\n" + decisions_content[insert_pos:]
    else:
        # Append to end if table not found
        return decisions_content + f"\n{entry}\n"


def extract_phase(
    source_project_id: str,
    phase_num: int,
    dry_run: bool = False,
    custom_title: Optional[str] = None,
    reason: str = "Phase complexity exceeded single-phase scope"
) -> ExtractResult:
    """Extract a phase from a project into its own independent project.

    Args:
        source_project_id: The source project ID (e.g., "PROJ-08")
        phase_num: The phase number to extract
        dry_run: If True, preview changes without making them
        custom_title: Optional custom title for the new project
        reason: Reason for extraction (documented in both projects)

    Returns:
        ExtractResult with success status and details
    """
    errors = []
    warnings = []
    new_project_id = None
    stage = ExtractionStage.VALIDATION
    date = datetime.now().strftime("%Y-%m-%d")
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"\n{'=' * 60}")
    print(f"{'[DRY RUN] ' if dry_run else ''}Extracting Phase {phase_num} from {source_project_id}")
    print('=' * 60)

    # === STAGE 1: Validation ===
    print(f"\nSTEP 1: Validating extraction request...")

    validation_errors = validate_extraction(source_project_id, phase_num)
    if validation_errors:
        for err in validation_errors:
            print(f"  [ERROR] {err}")
        return ExtractResult(
            success=False,
            new_project_id=None,
            source_project_id=source_project_id,
            phase_num=phase_num,
            errors=validation_errors,
            warnings=[]
        )

    # Load the phase
    phase_path = get_phase_checklist_path(source_project_id, phase_num)
    phase = parse_phase_file(phase_path)
    print(f"  Phase: {phase.name}")
    print(f"  Status: {phase.status}")
    print(f"  Tasks: {len(phase.tasks)}")

    # Generate title for new project
    if custom_title:
        new_title = custom_title
    else:
        new_title = f"{phase.name} (from {source_project_id})"

    print(f"  New project title: {new_title}")
    print("  Validation PASSED")

    if dry_run:
        # Preview what would happen
        preview_project_id = get_next_project_id()
        print(f"\n[DRY RUN] Would create new project: {preview_project_id}")
        print(f"[DRY RUN] Would update: {phase_path.name}")
        print(f"[DRY RUN] Would update: plan.md Quick Status table")
        print(f"[DRY RUN] Would add decisions.md entries to both projects")
        print(f"\n{'=' * 60}")
        print("[DRY RUN] No changes made")
        print('=' * 60)

        return ExtractResult(
            success=True,
            new_project_id=preview_project_id,
            source_project_id=source_project_id,
            phase_num=phase_num,
            errors=[],
            warnings=["Dry run - no changes made"]
        )

    try:
        # === STAGE 2: Create new project ===
        print(f"\nSTEP 2: Creating new project...")
        new_project_id = create_project(new_title)
        stage = ExtractionStage.NEW_PROJECT_CREATED
        print(f"  Created: {new_project_id}")

        # === STAGE 3: Write extraction context file ===
        print(f"\nSTEP 3: Writing extraction context...")
        new_project_dir = ACTIVE_DIR / new_project_id
        findings_dir = new_project_dir / "findings"
        findings_dir.mkdir(exist_ok=True)

        original_tasks = format_tasks_for_archive(phase)
        context_content = EXTRACTION_CONTEXT_TEMPLATE.format(
            phase_num=phase_num,
            source_project_id=source_project_id,
            date=date_time,
            reason=reason,
            objective=phase.objective or "Not specified",
            original_tasks=original_tasks
        )

        context_path = findings_dir / "extraction_context.md"
        context_path.write_text(context_content, encoding='utf-8')
        stage = ExtractionStage.CONTEXT_FILE_WRITTEN
        print(f"  Created: {context_path.relative_to(ACTIVE_DIR.parent)}")

        # === STAGE 4: Update original phase checklist ===
        print(f"\nSTEP 4: Updating original phase checklist...")

        extracted_content = EXTRACTED_PHASE_TEMPLATE.format(
            phase_num=phase_num,
            phase_name=phase.name,
            new_project_id=new_project_id,
            date=date_time,
            objective=phase.objective or "Not specified",
            reason=reason,
            original_tasks=original_tasks
        )

        phase_path.write_text(extracted_content, encoding='utf-8')
        stage = ExtractionStage.ORIGINAL_PHASE_UPDATED
        print(f"  Updated: {phase_path.name}")

        # === STAGE 5: Update original plan.md ===
        print(f"\nSTEP 5: Updating original plan.md...")

        plan_path = get_plan_path(source_project_id)
        plan_content = plan_path.read_text(encoding='utf-8')
        updated_plan = update_plan_quick_status(plan_content, phase_num, new_project_id)

        if updated_plan != plan_content:
            plan_path.write_text(updated_plan, encoding='utf-8')
            print(f"  Updated Quick Status table")
        else:
            warnings.append("Could not update Quick Status table - manual update may be needed")
            print(f"  [WARN] Could not find phase row in Quick Status table")

        stage = ExtractionStage.ORIGINAL_PLAN_UPDATED

        # === STAGE 6: Update decisions.md in both projects ===
        print(f"\nSTEP 6: Updating decisions logs...")

        # Source project decisions
        source_decisions_path = get_decisions_path(source_project_id)
        if source_decisions_path.exists():
            source_decisions = source_decisions_path.read_text(encoding='utf-8')
            source_entry = f"| {date} | Extracted Phase {phase_num} to {new_project_id} | {reason}. Original objective: \"{phase.objective or 'Not specified'}\". |"
            updated_source_decisions = add_decisions_entry(source_decisions, source_entry)
            source_decisions_path.write_text(updated_source_decisions, encoding='utf-8')
            print(f"  Updated: {source_project_id}/decisions.md")

        # New project decisions
        new_decisions_path = get_decisions_path(new_project_id)
        if new_decisions_path.exists():
            new_decisions = new_decisions_path.read_text(encoding='utf-8')
            new_entry = f"| {date} | Project originated from {source_project_id} Phase {phase_num} extraction | {reason}. See findings/extraction_context.md for original phase content. |"
            updated_new_decisions = add_decisions_entry(new_decisions, new_entry)
            new_decisions_path.write_text(updated_new_decisions, encoding='utf-8')
            print(f"  Updated: {new_project_id}/decisions.md")

        stage = ExtractionStage.COMPLETE

        print(f"\n{'=' * 60}")
        print("EXTRACTION COMPLETE")
        print(f"  Source: {source_project_id} Phase {phase_num}")
        print(f"  New Project: {new_project_id}")
        print(f"\nNext steps:")
        print(f"  1. Run 'Start Project' prompt on {new_project_id}")
        print(f"  2. Continue work on {source_project_id} (other phases)")
        print(f"  3. Phase {phase_num} will auto-complete when {new_project_id} is archived")
        print('=' * 60)

        return ExtractResult(
            success=True,
            new_project_id=new_project_id,
            source_project_id=source_project_id,
            phase_num=phase_num,
            errors=[],
            warnings=warnings
        )

    except Exception as e:
        errors.append(str(e))
        print(f"\n[ERROR] Extraction failed: {e}")

        # Rollback if we created the new project
        if stage >= ExtractionStage.NEW_PROJECT_CREATED and new_project_id:
            print(f"\nRolling back: Removing {new_project_id}...")
            try:
                import shutil
                new_project_dir = ACTIVE_DIR / new_project_id
                if new_project_dir.exists():
                    shutil.rmtree(new_project_dir)
                    print(f"  Removed: {new_project_dir}")
            except Exception as rollback_error:
                print(f"  [WARN] Rollback failed: {rollback_error}")
                errors.append(f"Rollback failed: {rollback_error}")

        return ExtractResult(
            success=False,
            new_project_id=None,
            source_project_id=source_project_id,
            phase_num=phase_num,
            errors=errors,
            warnings=warnings
        )


def main():
    parser = argparse.ArgumentParser(
        description='Extract a phase from a project into its own independent project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python extract_phase.py PROJ-08 3
    python extract_phase.py PROJ-08 3 --dry-run
    python extract_phase.py PROJ-08 3 --title "Authentication System"
    python extract_phase.py PROJ-08 3 --reason "Phase requires parallel development"
        """
    )
    parser.add_argument('project_id', help='Source project ID (e.g., PROJ-08)')
    parser.add_argument('phase_num', type=int, help='Phase number to extract')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview changes without making them')
    parser.add_argument('--title', dest='custom_title',
                        help='Custom title for the new project')
    parser.add_argument('--reason', default='Phase complexity exceeded single-phase scope',
                        help='Reason for extraction (documented in both projects)')

    args = parser.parse_args()

    result = extract_phase(
        source_project_id=args.project_id,
        phase_num=args.phase_num,
        dry_run=args.dry_run,
        custom_title=args.custom_title,
        reason=args.reason
    )

    sys.exit(0 if result.success else 1)


if __name__ == '__main__':
    main()
