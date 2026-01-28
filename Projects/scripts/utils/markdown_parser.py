"""Utilities for parsing project markdown files."""
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

from .config import ACTIVE_DIR


@dataclass
class Task:
    """Represents a single task within a phase."""
    id: str
    name: str
    complexity: str
    file_path: Optional[str] = None
    tests: Optional[str] = None
    subtasks: List[Tuple[bool, str]] = field(default_factory=list)  # (checked, text)
    notes: Optional[str] = None


@dataclass
class Phase:
    """Represents a project phase."""
    number: int
    name: str
    status: str
    objective: Optional[str] = None
    tasks: List[Task] = field(default_factory=list)


@dataclass
class CurrentState:
    """Represents the Current State section."""
    last_updated: Optional[str] = None
    active_phase: Optional[str] = None
    last_action: Optional[str] = None
    next_action: Optional[str] = None
    blockers: Optional[str] = None
    context: Optional[str] = None


@dataclass
class ProjectData:
    """Complete parsed project data."""
    project_id: str
    title: str
    content: str
    phases: List[Phase] = field(default_factory=list)
    current_state: Optional[CurrentState] = None
    decisions: List[Dict[str, str]] = field(default_factory=list)


def get_project_path(project_id: str) -> Path:
    """Get the path to a project file or directory."""
    # Check for new directory structure first
    dir_path = ACTIVE_DIR / project_id
    if dir_path.is_dir():
        return dir_path / "plan.md"

    # Fall back to old flat file structure
    file_path = ACTIVE_DIR / f"{project_id}.md"
    if file_path.exists():
        return file_path

    raise FileNotFoundError(f"Project not found: {project_id}")


def parse_project_file(project_id: str) -> ProjectData:
    """Parse a project file into structured data."""
    filepath = get_project_path(project_id)
    content = filepath.read_text(encoding='utf-8')

    # Extract title
    title_match = re.search(r'^# (?:PROJ-\d+:\s*)?(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else project_id

    # Parse phases
    phases = get_phases(content)

    # Parse current state
    current_state = get_current_state(content)

    return ProjectData(
        project_id=project_id,
        title=title,
        content=content,
        phases=phases,
        current_state=current_state,
    )


def get_phases(content: str) -> List[Phase]:
    """Extract all phases from project content."""
    phases = []

    # Handle both old format (### Phase N:) and new format (in separate files)
    # Pattern for phases in main file: ### Phase N: Name [Complexity]
    phase_pattern = r'###\s*Phase\s*(\d+):\s*([^\[\n]+?)(?:\s*\[([^\]]+)\])?\s*\n'

    # Split content by phase headers
    phase_matches = list(re.finditer(phase_pattern, content))

    for i, match in enumerate(phase_matches):
        phase_num = int(match.group(1))
        phase_name = match.group(2).strip()

        # Get the content for this phase (up to next phase or end)
        start_pos = match.end()
        end_pos = phase_matches[i + 1].start() if i + 1 < len(phase_matches) else len(content)
        phase_content = content[start_pos:end_pos]

        # Extract status
        status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', phase_content)
        status = status_match.group(1).strip() if status_match else "Unknown"
        # Clean up status markers like checkmarks
        status = re.sub(r'[✅🔄⏸️]', '', status).strip()

        # Extract objective
        obj_match = re.search(r'\*\*Objective:\*\*\s*(.+?)(?:\n|$)', phase_content)
        objective = obj_match.group(1).strip() if obj_match else None

        # Extract tasks
        tasks = extract_tasks(phase_content, phase_num)

        phases.append(Phase(
            number=phase_num,
            name=phase_name,
            status=status,
            objective=objective,
            tasks=tasks,
        ))

    return phases


def extract_tasks(phase_content: str, phase_num: int) -> List[Task]:
    """Extract tasks from a phase section."""
    tasks = []

    # Pattern: #### Task X.Y: Name [Complexity]
    task_pattern = r'####\s*Task\s*(\d+\.\d+):\s*([^\[\n]+?)(?:\s*\[([^\]]+)\])?\s*\n'

    task_matches = list(re.finditer(task_pattern, phase_content))

    for i, match in enumerate(task_matches):
        task_id = match.group(1)
        task_name = match.group(2).strip()
        complexity = match.group(3).strip() if match.group(3) else "Unknown"

        # Get task content
        start_pos = match.end()
        end_pos = task_matches[i + 1].start() if i + 1 < len(task_matches) else len(phase_content)
        task_content = phase_content[start_pos:end_pos]

        # Extract file path
        file_match = re.search(r'\*\*File:\*\*\s*`([^`]+)`', task_content)
        file_path = file_match.group(1) if file_match else None

        # Extract tests
        tests_match = re.search(r'\*\*Tests:\*\*\s*(.+?)(?:\n|$)', task_content)
        tests = tests_match.group(1).strip() if tests_match else None

        # Extract subtasks (checkboxes)
        subtasks = []
        checkbox_pattern = r'-\s*\[([ xX])\]\s*(.+?)(?=\n-\s*\[|\n\*\*|\n####|\n###|\n---|\Z)'
        for cb_match in re.finditer(checkbox_pattern, task_content, re.DOTALL):
            checked = cb_match.group(1).lower() == 'x'
            text = cb_match.group(2).strip().split('\n')[0]  # First line only
            subtasks.append((checked, text))

        # Extract notes
        notes_match = re.search(r'\*\*Notes:\*\*\s*(.+?)(?=\n####|\n###|\n---|\Z)', task_content, re.DOTALL)
        notes = notes_match.group(1).strip() if notes_match else None
        if notes and notes in ['', '[Empty]', 'None', '[Filled during implementation]']:
            notes = None

        tasks.append(Task(
            id=task_id,
            name=task_name,
            complexity=complexity,
            file_path=file_path,
            tests=tests,
            subtasks=subtasks,
            notes=notes,
        ))

    return tasks


def get_current_state(content: str) -> Optional[CurrentState]:
    """Extract Current State section from content."""
    state_match = re.search(
        r'##\s*Current State\s*\n(.+?)(?=\n##\s|\Z)',
        content,
        re.DOTALL
    )

    if not state_match:
        return None

    section_text = state_match.group(1)

    def extract_field(pattern: str) -> Optional[str]:
        match = re.search(pattern, section_text)
        return match.group(1).strip() if match else None

    return CurrentState(
        last_updated=extract_field(r'\*\*Last Updated:\*\*\s*(.+?)(?:\n|$)'),
        active_phase=extract_field(r'\*\*(?:Current Phase|Active Phase):\*\*\s*(.+?)(?:\n|$)'),
        last_action=extract_field(r'\*\*Last (?:Agent )?Action:\*\*\s*(.+?)(?:\n|$)'),
        next_action=extract_field(r'\*\*Next Action:\*\*\s*(.+?)(?:\n|$)'),
        blockers=extract_field(r'\*\*Blockers:\*\*\s*(.+?)(?:\n|$)'),
        context=extract_field(r'\*\*Context for Next Agent:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)'),
    )


def count_checkboxes(content: str) -> Tuple[int, int]:
    """Count checked and total checkboxes in content.

    Returns:
        Tuple of (checked_count, total_count)
    """
    checked = len(re.findall(r'-\s*\[[xX]\]', content))
    unchecked = len(re.findall(r'-\s*\[\s\]', content))
    return checked, checked + unchecked


def find_incomplete_tasks(project_data: ProjectData) -> List[Tuple[Phase, Task, List[str]]]:
    """Find all tasks with unchecked subtasks.

    Returns:
        List of (phase, task, unchecked_subtask_texts)
    """
    incomplete = []

    for phase in project_data.phases:
        for task in phase.tasks:
            unchecked = [text for checked, text in task.subtasks if not checked]
            if unchecked:
                incomplete.append((phase, task, unchecked))

    return incomplete


def update_section(content: str, section_name: str, new_content: str) -> str:
    """Update a section in markdown content.

    Args:
        content: Full markdown content
        section_name: Name of section (e.g., "Current State")
        new_content: New content for the section (without the ## header)

    Returns:
        Updated content
    """
    pattern = rf'(##\s*{re.escape(section_name)}\s*\n)(.+?)(?=\n##\s|\Z)'
    replacement = rf'\1{new_content}\n'

    updated, count = re.subn(pattern, replacement, content, flags=re.DOTALL)

    if count == 0:
        raise ValueError(f"Section not found: {section_name}")

    return updated


def parse_phase_file(filepath: Path) -> Phase:
    """Parse a standalone phase checklist file."""
    content = filepath.read_text(encoding='utf-8')

    # Extract phase number from filename (phase_1_checklist.md -> 1)
    num_match = re.search(r'phase_(\d+)', filepath.stem)
    phase_num = int(num_match.group(1)) if num_match else 0

    # Extract title: # Phase X: Name
    title_match = re.search(r'^#\s*Phase\s*\d+:\s*(.+)$', content, re.MULTILINE)
    phase_name = title_match.group(1).strip() if title_match else "Unknown"

    # Extract status
    status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', content)
    status = status_match.group(1).strip() if status_match else "Unknown"

    # Extract objective
    obj_match = re.search(r'\*\*Objective:\*\*\s*(.+?)(?:\n|$)', content)
    objective = obj_match.group(1).strip() if obj_match else None

    # Extract tasks
    tasks = extract_tasks(content, phase_num)

    return Phase(
        number=phase_num,
        name=phase_name,
        status=status,
        objective=objective,
        tasks=tasks,
    )


def extract_sub_project_reference(phase: Phase) -> Optional[str]:
    """Extract the sub-project ID from an extracted phase.

    Looks for patterns like:
    - "Extracted to PROJ-42"
    - "**Extracted To:** PROJ-42"
    - "-> PROJ-42"

    Args:
        phase: The Phase object to check

    Returns:
        The sub-project ID (e.g., "PROJ-42") or None if not found
    """
    patterns = [
        r'Extracted\s+[Tt]o[:\s]+\**(PROJ-\d+)',
        r'->\s*(PROJ-\d+)',
        r'\*\*Sub-Project:\*\*\s*\[?(PROJ-\d+)',
        r'\*\*Extracted To:\*\*\s*(PROJ-\d+)',
    ]
    # Search in status and objective
    search_text = phase.status + " " + (phase.objective or "")
    for pattern in patterns:
        match = re.search(pattern, search_text)
        if match:
            return match.group(1)
    return None


def find_extracted_phases(project_data: ProjectData) -> List[Tuple[int, str]]:
    """Find all extracted phases and their sub-project references.

    Args:
        project_data: The parsed project data

    Returns:
        List of (phase_num, sub_project_id) tuples
    """
    extracted = []
    for phase in project_data.phases:
        if "extracted" in phase.status.lower():
            sub_id = extract_sub_project_reference(phase)
            if sub_id:
                extracted.append((phase.number, sub_id))
    return extracted
