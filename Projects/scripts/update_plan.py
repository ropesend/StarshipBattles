#!/usr/bin/env python3
"""
Helper script to update refactor_plan.md programmatically.
Can mark tasks complete, update agent context, and add execution log entries.
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Optional


class PlanUpdater:
    """Updates refactor_plan.md with task completion and context."""
    
    def __init__(self, plan_file: Path):
        self.plan_file = plan_file
        self.content = plan_file.read_text(encoding='utf-8')
    
    def mark_task_complete(self, project_id: str, phase_num: int) -> bool:
        """
        Mark a specific phase as complete.
        
        Args:
            project_id: e.g., "PROJ-45"
            phase_num: Phase number (1-based)
            
        Returns:
            True if task was found and marked, False otherwise
        """
        # Pattern to find the specific phase checkbox
        # Example: - [ ] Phase 1: Foundation - Exception Hierarchy & Error Codes
        pattern = rf'(### {project_id}:.*?)(- \[ \] Phase {phase_num}:.*?)$'
        
        def replace_checkbox(match):
            return match.group(1) + match.group(2).replace('[ ]', '[x]')
        
        new_content, count = re.subn(
            pattern,
            replace_checkbox,
            self.content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        if count > 0:
            self.content = new_content
            return True
        return False
    
    def update_agent_context(
        self,
        last_completed: str,
        status: str,
        test_status: str,
        blockers: str = "None",
        handoff_notes: Optional[str] = None
    ):
        """
        Update the Agent Context section.
        
        Args:
            last_completed: Description of last completed task
            status: Current status message
            test_status: Test suite status
            blockers: Any blockers (default "None")
            handoff_notes: Optional detailed handoff notes
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        context_section = f"""## Agent Context

**Last Session:** {timestamp}
**Last Completed:** {last_completed}
**Current Status:** {status}
**Test Status:** {test_status}
**Active Blockers:** {blockers}

**Handoff Notes:**
{handoff_notes if handoff_notes else "- No additional notes"}
"""
        
        # Replace the Agent Context section
        pattern = r'## Agent Context\n.*?(?=\n---\n## Master Task List)'
        self.content = re.sub(
            pattern,
            context_section,
            self.content,
            flags=re.DOTALL
        )
    
    def add_execution_log_entry(
        self,
        project_id: str,
        phase: str,
        status: str,
        test_result: str,
        commit_hash: Optional[str] = None
    ):
        """
        Add an entry to the Execution Log table.
        
        Args:
            project_id: e.g., "PROJ-45"
            phase: Phase description
            status: "Complete", "Failed", "In Progress"
            test_result: Test status
            commit_hash: Git commit hash (optional)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        commit = commit_hash[:8] if commit_hash else "-"
        
        # Find the execution log table
        log_pattern = r'(\| Timestamp \| Project \| Phase \| Status \| Tests \| Commit \|\n\|.*?\|\n)(.*?)(?=\n---|\Z)'
        
        new_entry = f"| {timestamp} | {project_id} | {phase} | {status} | {test_result} | {commit} |\n"
        
        def add_entry(match):
            header = match.group(1)
            existing_entries = match.group(2).strip()
            
            # If only placeholder row exists, replace it
            if existing_entries == "| - | - | - | - | - | - |":
                return header + new_entry
            else:
                return header + existing_entries + "\n" + new_entry
        
        self.content = re.sub(log_pattern, add_entry, self.content, flags=re.DOTALL)
    
    def save(self):
        """Save changes back to the plan file."""
        self.plan_file.write_text(self.content, encoding='utf-8')


def main():
    """CLI interface for updating the plan."""
    if len(sys.argv) < 2:
        print("Usage: update_plan.py <command> [args...]", file=sys.stderr)
        print("\nCommands:", file=sys.stderr)
        print("  mark-complete <plan_file> <project_id> <phase_num>", file=sys.stderr)
        print("  update-context <plan_file> <last_completed> <status> <test_status>", file=sys.stderr)
        print("  add-log <plan_file> <project_id> <phase> <status> <test_result>", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "mark-complete":
        if len(sys.argv) != 5:
            print("Usage: update_plan.py mark-complete <plan_file> <project_id> <phase_num>", file=sys.stderr)
            sys.exit(1)
        
        plan_file = Path(sys.argv[2])
        project_id = sys.argv[3]
        phase_num = int(sys.argv[4])
        
        updater = PlanUpdater(plan_file)
        if updater.mark_task_complete(project_id, phase_num):
            updater.save()
            print(f"Marked {project_id} Phase {phase_num} as complete")
        else:
            print(f"Could not find {project_id} Phase {phase_num}", file=sys.stderr)
            sys.exit(1)
    
    elif command == "update-context":
        if len(sys.argv) < 6:
            print("Usage: update_plan.py update-context <plan_file> <last_completed> <status> <test_status> [handoff_notes]", file=sys.stderr)
            sys.exit(1)
        
        plan_file = Path(sys.argv[2])
        last_completed = sys.argv[3]
        status = sys.argv[4]
        test_status = sys.argv[5]
        handoff_notes = sys.argv[6] if len(sys.argv) > 6 else None
        
        updater = PlanUpdater(plan_file)
        updater.update_agent_context(last_completed, status, test_status, handoff_notes=handoff_notes)
        updater.save()
        print("Updated agent context")
    
    elif command == "add-log":
        if len(sys.argv) != 7:
            print("Usage: update_plan.py add-log <plan_file> <project_id> <phase> <status> <test_result>", file=sys.stderr)
            sys.exit(1)
        
        plan_file = Path(sys.argv[2])
        project_id = sys.argv[3]
        phase = sys.argv[4]
        status = sys.argv[5]
        test_result = sys.argv[6]
        
        updater = PlanUpdater(plan_file)
        updater.add_execution_log_entry(project_id, phase, status, test_result)
        updater.save()
        print("Added execution log entry")
    
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
