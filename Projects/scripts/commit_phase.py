#!/usr/bin/env python3
"""
Helper script to create standardized git commits for completed phases.
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional


def run_git_command(args: list[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
    """
    Run a git command and return the result.
    
    Args:
        args: Git command arguments (e.g., ['status', '--short'])
        cwd: Working directory (default: current directory)
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ['git'] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Git command timed out"
    except Exception as e:
        return 1, "", str(e)


def check_git_status(repo_path: Path) -> bool:
    """
    Check if there are uncommitted changes.
    
    Returns:
        True if there are changes to commit, False otherwise
    """
    exit_code, stdout, _ = run_git_command(['status', '--short'], cwd=repo_path)
    return exit_code == 0 and bool(stdout.strip())


def commit_phase(
    repo_path: Path,
    project_id: str,
    phase_num: int,
    phase_name: str,
    test_status: str = "All tests passing"
) -> bool:
    """
    Create a git commit for a completed phase.
    
    Args:
        repo_path: Path to git repository
        project_id: e.g., "PROJ-45"
        phase_num: Phase number
        phase_name: Short description of phase
        test_status: Test result summary
        
    Returns:
        True if commit successful, False otherwise
    """
    # Check if there are changes to commit
    if not check_git_status(repo_path):
        print("No changes to commit")
        return False
    
    # Stage all changes
    exit_code, _, stderr = run_git_command(['add', '-A'], cwd=repo_path)
    if exit_code != 0:
        print(f"Error staging changes: {stderr}", file=sys.stderr)
        return False
    
    # Create commit message
    commit_message = f"""[{project_id}] Phase {phase_num}: {phase_name} - Automated

Test Status: {test_status}

This commit was created automatically by the stateless refactor loop.
"""
    
    # Commit
    exit_code, stdout, stderr = run_git_command(
        ['commit', '-m', commit_message],
        cwd=repo_path
    )
    
    if exit_code != 0:
        print(f"Error creating commit: {stderr}", file=sys.stderr)
        return False
    
    print(f"Commit created: [{project_id}] Phase {phase_num}: {phase_name}")
    
    # Get commit hash
    exit_code, commit_hash, _ = run_git_command(
        ['rev-parse', 'HEAD'],
        cwd=repo_path
    )
    
    if exit_code == 0:
        print(f"Commit hash: {commit_hash.strip()[:8]}")
    
    return True


def main():
    """CLI interface for committing phases."""
    if len(sys.argv) < 5:
        print("Usage: commit_phase.py <repo_path> <project_id> <phase_num> <phase_name> [test_status]", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print('  commit_phase.py . PROJ-45 1 "Exception Hierarchy" "5199 passed"', file=sys.stderr)
        sys.exit(1)
    
    repo_path = Path(sys.argv[1])
    project_id = sys.argv[2]
    phase_num = int(sys.argv[3])
    phase_name = sys.argv[4]
    test_status = sys.argv[5] if len(sys.argv) > 5 else "All tests passing"
    
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)
    
    if not (repo_path / '.git').exists():
        print(f"Error: Not a git repository: {repo_path}", file=sys.stderr)
        sys.exit(1)
    
    success = commit_phase(repo_path, project_id, phase_num, phase_name, test_status)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
