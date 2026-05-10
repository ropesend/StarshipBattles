# Project management utilities
from .markdown_parser import (
    parse_project_file,
    get_phases,
    get_current_state,
    count_checkboxes,
    find_incomplete_tasks,
    update_section,
)
from .index_manager import (
    read_projects_index,
    get_next_project_id,
    update_project_status_in_index,
    add_project_to_index,
    archive_project_in_index,
)
from .config import PROJECTS_DIR, ACTIVE_DIR, ARCHIVED_DIR, SCRIPTS_DIR
