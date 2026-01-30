#!/usr/bin/env python3
"""
Check the completion status of a specific project.

Returns the status of a project's phases and determines if audit should be triggered.
"""

import sys
import re
from pathlib import Path
from typing import Tuple, Optional


def check_project_status(project_id: str, projects_dir: Path) -> Tuple[str, dict]:
    """
    Check the status of a project's phases.
    
    Args:
        project_id: Project ID (e.g., "PROJ-45")
        projects_dir: Path to active_projects directory
        
    Returns:
        Tuple of (status, details) where status is:
        - "complete" - All phases complete, ready for audit
        - "in_progress" - Some phases complete, work remains
        - "not_started" - No phases complete yet
        - "not_found" - Project doesn't exist
        
        details dict contains:
        - total_phases: int
        - completed_phases: int
        - current_phase: int or None
        - phase_statuses: list of status strings
    """
    project_dir = projects_dir / project_id
    plan_file = project_dir / "plan.md"
    
    if not plan_file.exists():
        return "not_found", {"error": f"Project {project_id} not found"}
    
    content = plan_file.read_text(encoding='utf-8')
    
    # Find the Quick Status table
    # Format:
    # | Phase | Status | Checklist |
    # |-------|--------|-----------|
    # | 1. Foundation | Complete | [phase_1_checklist.md](...) |
    # | 2. Core Layer | In Progress | [phase_2_checklist.md](...) |
    
    table_pattern = r'\| Phase \| Status \| Checklist \|.*?\n\|.*?\|\n(.*?)(?=\n\n|\n##|\Z)'
    table_match = re.search(table_pattern, content, re.DOTALL)
    
    if not table_match:
        # Try alternative: look for phase checklist files
        return check_by_checklist_files(project_dir)
    
    table_content = table_match.group(1)
    
    # Parse phase rows
    # Format: | 1. Phase Name | Status | [link](...) |
    phase_pattern = r'\|\s*(\d+)\.\s+([^|]+?)\s*\|\s*([^|]+?)\s*\|'
    phases = re.findall(phase_pattern, table_content)
    
    if not phases:
        return check_by_checklist_files(project_dir)
    
    total_phases = len(phases)
    completed_phases = 0
    current_phase = None
    phase_statuses = []
    
    for phase_num, phase_name, status in phases:
        phase_num = int(phase_num)
        status = status.strip()
        phase_statuses.append(status)
        
        if status.lower() in ['complete', 'completed']:
            completed_phases += 1
        elif current_phase is None and status.lower() not in ['complete', 'completed', 'not started']:
            current_phase = phase_num
    
    # Determine overall status
    if completed_phases == 0:
        overall_status = "not_started"
    elif completed_phases == total_phases:
        overall_status = "complete"
    else:
        overall_status = "in_progress"
    
    details = {
        "total_phases": total_phases,
        "completed_phases": completed_phases,
        "current_phase": current_phase,
        "phase_statuses": phase_statuses
    }
    
    return overall_status, details


def check_by_checklist_files(project_dir: Path) -> Tuple[str, dict]:
    """
    Fallback: Check status by looking at phase checklist files.
    
    Counts how many phase_N_checklist.md files exist and checks their completion.
    """
    checklist_files = sorted(project_dir.glob("phase_*_checklist.md"))
    
    if not checklist_files:
        return "not_found", {"error": "No phase checklists found"}
    
    total_phases = len(checklist_files)
    completed_phases = 0
    current_phase = None
    
    for checklist_file in checklist_files:
        # Extract phase number from filename
        match = re.search(r'phase_(\d+)', checklist_file.name)
        if not match:
            continue
        
        phase_num = int(match.group(1))
        
        # Check if phase is complete by looking for "Status: Complete" in file
        content = checklist_file.read_text(encoding='utf-8')
        if re.search(r'\*\*Status:\*\*\s*(Complete|Completed)', content, re.IGNORECASE):
            completed_phases += 1
        elif current_phase is None:
            current_phase = phase_num
    
    # Determine overall status
    if completed_phases == 0:
        overall_status = "not_started"
    elif completed_phases == total_phases:
        overall_status = "complete"
    else:
        overall_status = "in_progress"
    
    details = {
        "total_phases": total_phases,
        "completed_phases": completed_phases,
        "current_phase": current_phase,
        "phase_statuses": ["unknown"] * total_phases
    }
    
    return overall_status, details


def main():
    if len(sys.argv) != 2:
        print("Usage: check_project_status.py <project_id>", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  check_project_status.py PROJ-45", file=sys.stderr)
        sys.exit(2)
    
    project_id = sys.argv[1]
    projects_dir = Path("Projects/active_projects")
    
    if not projects_dir.exists():
        print(f"Error: Projects directory not found: {projects_dir}", file=sys.stderr)
        sys.exit(2)
    
    status, details = check_project_status(project_id, projects_dir)
    
    if status == "not_found":
        print(f"Error: {details.get('error', 'Project not found')}", file=sys.stderr)
        sys.exit(1)
    
    # Print results
    print(f"Project: {project_id}")
    print(f"Status: {status}")
    print(f"Phases: {details['completed_phases']}/{details['total_phases']} complete")
    
    if details.get('current_phase'):
        print(f"Current Phase: {details['current_phase']}")
    
    # Exit codes:
    # 0 = complete (ready for audit)
    # 1 = in progress or not started
    # 2 = error
    sys.exit(0 if status == "complete" else 1)


if __name__ == "__main__":
    main()
