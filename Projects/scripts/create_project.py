#!/usr/bin/env python3
"""
Create a new project with the correct directory structure.

Usage:
    python create_project.py "My Feature Title"
    python create_project.py "My Feature Title" --id PROJ-10
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import ACTIVE_DIR
from utils.index_manager import get_next_project_id, add_project_to_index


# Templates with embedded reminder banners
PLAN_TEMPLATE = '''# {project_id}: {title}

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py {project_id}` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py {project_id} [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. TBD | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** {date}
**Active Phase:** Planning
**Last Action:** Project created
**Next Action:** Define project scope and phases
**Blockers:** None

## Overview
[2-3 sentence description of what this project accomplishes]

## Goals
- [Goal 1]
- [Goal 2]

## Scope
**In:** [What's included]
**Out:** [What's explicitly excluded]

## Key Files
| Component | File Path |
|-----------|-----------|
| [Name] | `path/to/file.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
'''

DESIGN_TEMPLATE = '''# {project_id}: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis
[Findings from Phase A code review - what was discovered about the codebase]

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture
[Key architecture points relevant to implementation]

### Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

### Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

### Opportunities Discovered
- [Opportunity 1]

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
'''

DECISIONS_TEMPLATE = '''# {project_id}: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| {date} | Project initialized | Starting point for {title} |
'''

MANIFEST_TEMPLATE = '''# {project_id} File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| path/to/file.py | Production | [What changes] |
| tests/path/to/test_file.py | Test | [New or modified] |
'''

PHASE_TEMPLATE = '''# Phase {phase_num}: {phase_name}

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py {project_id} {phase_num}`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** [What this phase accomplishes]

---

## Tasks

### Task {phase_num}.1: [Task Name] [Simple/Medium/Complex]
**File:** `path/to/file.py`
**Tests:** `pytest tests/path/`

- [ ] Subtask with specific action
- [ ] Another subtask
- [ ] Verify: [what to check]

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
'''


def create_project(title: str, project_id: str = None) -> str:
    """Create a new project with directory structure.

    Returns the project ID.
    """
    # Get project ID
    if project_id is None:
        project_id = get_next_project_id()

    date = datetime.now().strftime("%Y-%m-%d")
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"\n{'=' * 50}")
    print(f"Creating New Project: {project_id}")
    print('=' * 50)

    # Create project directory
    project_dir = ACTIVE_DIR / project_id
    findings_dir = project_dir / "findings"

    # Safety check: fail if directory already exists (prevents overwrites)
    if project_dir.exists():
        print(f"\n[ERROR] Directory already exists: {project_dir}")
        print("        This suggests the index is out of sync with the filesystem.")
        print("        Run: python Projects/scripts/sync_index.py --fix")
        print("        Or manually remove the directory if it's orphaned.")
        sys.exit(1)

    print(f"\nSTEP 1: Create directory structure")
    project_dir.mkdir(parents=True, exist_ok=False)
    findings_dir.mkdir(exist_ok=True)
    print(f"  Created: {project_dir}")
    print(f"  Created: {findings_dir}")

    # Create plan.md
    print(f"\nSTEP 2: Create project files")
    plan_content = PLAN_TEMPLATE.format(
        project_id=project_id,
        title=title,
        date=date_time,
    )
    (project_dir / "plan.md").write_text(plan_content, encoding='utf-8')
    print(f"  Created: plan.md")

    # Create design.md
    design_content = DESIGN_TEMPLATE.format(project_id=project_id)
    (project_dir / "design.md").write_text(design_content, encoding='utf-8')
    print(f"  Created: design.md")

    # Create decisions.md
    decisions_content = DECISIONS_TEMPLATE.format(
        project_id=project_id,
        title=title,
        date=date,
    )
    (project_dir / "decisions.md").write_text(decisions_content, encoding='utf-8')
    print(f"  Created: decisions.md")

    # Create initial phase checklist
    phase_content = PHASE_TEMPLATE.format(
        project_id=project_id,
        phase_num=1,
        phase_name="TBD",
    )
    (project_dir / "phase_1_checklist.md").write_text(phase_content, encoding='utf-8')
    print(f"  Created: phase_1_checklist.md")

    # Create manifest.md (for parallel execution)
    manifest_content = MANIFEST_TEMPLATE.format(project_id=project_id)
    (project_dir / "manifest.md").write_text(manifest_content, encoding='utf-8')
    print(f"  Created: manifest.md")

    # Update projects_index.md
    print(f"\nSTEP 3: Update projects_index.md")
    try:
        add_project_to_index(project_id, title, "Planning")
        print(f"  Added {project_id} to index")
    except Exception as e:
        print(f"  [WARN] Could not update index: {e}")
        print(f"         Please add manually to projects_index.md")

    print(f"\n{'=' * 50}")
    print(f"PROJECT CREATED")
    print(f"  ID: {project_id}")
    print(f"  Directory: {project_dir}")
    print(f"\nNext step: Run 'Start Project' prompt to begin planning.")
    print('=' * 50)

    return project_id


def main():
    parser = argparse.ArgumentParser(
        description='Create a new project with directory structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python create_project.py "Add Dark Mode Support"
    python create_project.py "Refactor Auth System" --id PROJ-15
        """
    )
    parser.add_argument('title', help='Project title')
    parser.add_argument('--id', dest='project_id',
                        help='Specific project ID (default: auto-assign)')

    args = parser.parse_args()

    project_id = create_project(args.title, args.project_id)
    sys.exit(0)


if __name__ == '__main__':
    main()
