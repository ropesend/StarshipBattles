#!/usr/bin/env python3
"""
Trigger an audit for a completed project.

This script is called automatically when all phases of a project are complete.
It updates the refactor_plan.md to indicate audit is needed.
"""

import sys
import re
from pathlib import Path
from datetime import datetime


def trigger_audit(plan_file: Path, project_id: str) -> bool:
    """
    Update refactor_plan.md to trigger audit for a project.
    
    Args:
        plan_file: Path to refactor_plan.md
        project_id: Project ID (e.g., "PROJ-45")
        
    Returns:
        True if successful, False otherwise
    """
    if not plan_file.exists():
        print(f"Error: Plan file not found: {plan_file}", file=sys.stderr)
        return False
    
    content = plan_file.read_text(encoding='utf-8')
    
    # Find the project entry in Master Task List
    # Format:
    # - [ ] **PROJ-XX: Title**
    #   - **Phases:** N | **Status:** Ready | **Priority:** High
    #   - **Plan:** [link](...)
    #   - **Audit:** Not Started | **Cycles:** 0/5
    
    # Pattern to find project and its audit status line
    project_pattern = rf'(- \[ \] \*\*{project_id}:.*?\n(?:.*?\n)*?)(  - \*\*Audit:\*\*) ([^\n]+)'
    
    match = re.search(project_pattern, content, re.MULTILINE)
    
    if not match:
        print(f"Error: Could not find project {project_id} in plan", file=sys.stderr)
        return False
    
    # Update audit status to "Ready for Audit"
    new_content = re.sub(
        project_pattern,
        r'\1\2 Ready for Audit | **Cycles:** 0/5',
        content,
        count=1
    )
    
    # Also update Agent Context to indicate audit is needed
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    context_pattern = r'(## Agent Context\n\n)(.*?)(\n\n---)'
    
    def update_context(match):
        header = match.group(1)
        old_context = match.group(2)
        footer = match.group(3)
        
        new_context = f"""**Last Session:** {timestamp}
**Last Completed:** All phases of {project_id}
**Current Status:** Audit required for {project_id}
**Current Project:** {project_id}
**Current Phase:** Audit (Cycle 1)
**Test Status:** All tests passing
**Active Blockers:** None

**Handoff Notes:**
- All phases of {project_id} are complete
- Audit must be run using Protocol 04
- Follow Protocol 08 for audit integration
- Maximum 5 audit cycles allowed
- If audit passes, mark project complete and move to next
- If audit fails, add fix phases and continue"""
        
        return header + new_context + footer
    
    new_content = re.sub(context_pattern, update_context, new_content, flags=re.DOTALL)
    
    # Write updated content
    plan_file.write_text(new_content, encoding='utf-8')
    
    print(f"Audit triggered for {project_id}")
    print(f"Status updated in {plan_file}")
    
    return True


def main():
    if len(sys.argv) != 2:
        print("Usage: trigger_audit.py <project_id>", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  trigger_audit.py PROJ-45", file=sys.stderr)
        sys.exit(2)
    
    project_id = sys.argv[1]
    plan_file = Path("Projects/refactor_loop/refactor_plan.md")
    
    success = trigger_audit(plan_file, project_id)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
