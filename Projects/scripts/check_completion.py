#!/usr/bin/env python3
"""
Check if all tasks in refactor_plan.md are complete.
Returns exit code 0 if all complete, 1 if incomplete tasks remain.
"""

import sys
import re
from pathlib import Path


def check_completion(plan_file: Path) -> bool:
    """
    Check if all tasks in the plan file are complete.
    
    Args:
        plan_file: Path to refactor_plan.md
        
    Returns:
        True if all tasks complete, False otherwise
    """
    if not plan_file.exists():
        print(f"Error: Plan file not found: {plan_file}", file=sys.stderr)
        sys.exit(2)
    
    content = plan_file.read_text(encoding='utf-8')
    
    # Find all checkbox items in the Master Task List section
    # New format: - [ ] **PROJ-XX: Title**
    # Pattern matches: - [ ] or - [x] or - [~] (complete with issues)
    checkbox_pattern = r'^- \[([x~/ ])\]\s+\*\*PROJ-\d+:'
    
    # Extract Master Task List section (stops at next ## header, not ###)
    task_list_match = re.search(
        r'## Master Task List\s*\n(.*?)(?=\n## |\Z)',
        content,
        re.DOTALL
    )
    
    if not task_list_match:
        print("Error: Could not find Master Task List section", file=sys.stderr)
        sys.exit(2)
    
    task_list_section = task_list_match.group(1)
    
    # Find all project checkboxes
    checkboxes = re.findall(checkbox_pattern, task_list_section, re.MULTILINE)
    
    if not checkboxes:
        print("Warning: No project tasks found in Master Task List", file=sys.stderr)
        return True
    
    total_tasks = len(checkboxes)
    completed_tasks = sum(1 for status in checkboxes if status == 'x')
    completed_with_issues = sum(1 for status in checkboxes if status == '~')
    in_progress_tasks = sum(1 for status in checkboxes if status == '/')
    incomplete_tasks = sum(1 for status in checkboxes if status == ' ')
    
    print(f"Project Status:")
    print(f"  Total Projects: {total_tasks}")
    print(f"  Completed: {completed_tasks} [x]")
    print(f"  Completed (with issues): {completed_with_issues} [~]")
    print(f"  In Progress: {in_progress_tasks} [/]")
    print(f"  Not Started: {incomplete_tasks} [ ]")
    print()
    
    if incomplete_tasks > 0 or in_progress_tasks > 0:
        print(f"Status: {incomplete_tasks + in_progress_tasks} projects remaining")
        return False
    else:
        print("Status: All projects complete! ✓")
        if completed_with_issues > 0:
            print(f"Note: {completed_with_issues} project(s) completed with audit issues")
        return True


def main():
    if len(sys.argv) != 2:
        print("Usage: check_completion.py <plan_file>", file=sys.stderr)
        sys.exit(2)
    
    plan_file = Path(sys.argv[1])
    
    all_complete = check_completion(plan_file)
    
    sys.exit(0 if all_complete else 1)


if __name__ == "__main__":
    main()
