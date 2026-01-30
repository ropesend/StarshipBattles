#!/usr/bin/env python3
"""
Helper script to update refactor_plan.md programmatically.
Can update project status ([], [/], [x], [~]), update agent context, and add execution log entries.
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
    
    def update_project_status(self, project_id: str, status_char: str) -> bool:
        """
        Update the checkbox status for a specific project.
        
        Args:
            project_id: e.g., "PROJ-45"
            status_char: One of ' ', '/', 'x', '~'
            
        Returns:
            True if project was found and updated, False otherwise
        """
        if status_char not in [' ', '/', 'x', '~', 'X']:
            print(f"Error: Invalid status character '{status_char}'. Must be ' ', '/', 'x', or '~'", file=sys.stderr)
            return False
            
        status_char = status_char.lower()
        
        # Pattern to find the project line
        # Example: - [ ] **PROJ-45: Title**
        # capture group 1: start of line up to brackets
        # capture group 2: content inside brackets
        # capture group 3: rest of line including project ID
        pattern = rf'^(- \[)(.)(\] \*\*{project_id}:)'
        
        def replace_status(match):
            return match.group(1) + status_char + match.group(3)
        
        new_content, count = re.subn(
            pattern,
            replace_status,
            self.content,
            flags=re.MULTILINE
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
        
        # Ensure handoff notes are properly formatted (list items)
        notes_formatted = handoff_notes if handoff_notes else "- No additional notes"
        
        context_section = f"""## Agent Context

**Last Session:** {timestamp}
**Last Completed:** {last_completed}
**Current Status:** {status}
**Test Status:** {test_status}
**Active Blockers:** {blockers}

**Handoff Notes:**
{notes_formatted}
"""
        
        # Replace the Agent Context section
        # Look for ## Agent Context followed by content, up to the next horizontal rule or header
        pattern = r'## Agent Context\n.*?(?=\n---|\n## )'
        
        new_content, count = re.subn(
            pattern,
            context_section,
            self.content,
            flags=re.DOTALL
        )
        
        if count > 0:
            self.content = new_content
        else:
            print("Warning: Could not locate Agent Context section to update", file=sys.stderr)
    
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
        
        # Find the execution log table header and content
        log_pattern = r'(\| Timestamp \| Project \| .*?\|\n\|.*?\|\n)(.*?)(?=\n---|\Z)'
        
        # Format: | Timestamp | Project | Action | Status | Tests | Commit | Notes |
        new_entry = f"| {timestamp} | {project_id} | {phase} | {status} | {test_result} | {commit} | - |"
        
        def add_entry(match):
            header = match.group(1)
            existing_entries = match.group(2).strip()
            
            # If only placeholder row exists (|- | - | ...), replace it
            if "- | -" in existing_entries and len(existing_entries.split('\n')) <= 1:
                 return header + new_entry + "\n"
            else:
                return header + existing_entries + "\n" + new_entry + "\n"
        
        self.content = re.sub(log_pattern, add_entry, self.content, flags=re.DOTALL)
    
    def save(self):
        """Save changes back to the plan file."""
        self.plan_file.write_text(self.content, encoding='utf-8')


def main():
    """CLI interface for updating the plan."""
    if len(sys.argv) < 2:
        print("Usage: update_plan.py <command> [args...]", file=sys.stderr)
        print("\nCommands:", file=sys.stderr)
        print("  update-project <plan_file> <project_id> <status_char>", file=sys.stderr)
        print("  update-context <plan_file> <last_completed> <status> <test_status> [handoff_notes]", file=sys.stderr)
        print("  add-log <plan_file> <project_id> <phase> <status> <test_result> [commit_hash]", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "update-project":
        if len(sys.argv) != 5:
            print("Usage: update_plan.py update-project <plan_file> <project_id> <status_char>", file=sys.stderr)
            print("Status chars: ' ' (reset), '/' (in progress), 'x' (complete), '~' (skipped)", file=sys.stderr)
            sys.exit(1)
        
        plan_file = Path(sys.argv[2])
        project_id = sys.argv[3]
        status_char = sys.argv[4]
        
        updater = PlanUpdater(plan_file)
        if updater.update_project_status(project_id, status_char):
            updater.save()
            print(f"Updated {project_id} status to [{status_char}]")
        else:
            print(f"Could not find project {project_id}", file=sys.stderr)
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
        if len(sys.argv) < 7:
            print("Usage: update_plan.py add-log <plan_file> <project_id> <phase> <status> <test_result> [commit_hash]", file=sys.stderr)
            sys.exit(1)
        
        plan_file = Path(sys.argv[2])
        project_id = sys.argv[3]
        phase = sys.argv[4]
        status = sys.argv[5]
        test_result = sys.argv[6]
        commit_hash = sys.argv[7] if len(sys.argv) > 7 else None
        
        updater = PlanUpdater(plan_file)
        updater.add_execution_log_entry(project_id, phase, status, test_result, commit_hash)
        updater.save()
        print("Added execution log entry")
    
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
