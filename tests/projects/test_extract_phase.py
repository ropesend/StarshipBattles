"""Tests for phase extraction functionality."""
import pytest
import shutil
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add Projects scripts to path
PROJECTS_SCRIPTS = Path(__file__).parent.parent.parent / "Projects" / "scripts"
sys.path.insert(0, str(PROJECTS_SCRIPTS))

from utils.config import ACTIVE_DIR, ARCHIVED_DIR, VALID_PHASE_STATUSES
from utils.markdown_parser import (
    Phase, Task, ProjectData, CurrentState,
    extract_sub_project_reference, find_extracted_phases
)
from utils.index_manager import is_project_archived, project_exists


class TestValidPhaseStatuses:
    """Test that VALID_PHASE_STATUSES includes extraction statuses."""

    def test_extracted_status_exists(self):
        """Extracted should be a valid phase status."""
        assert "Extracted" in VALID_PHASE_STATUSES

    def test_extracted_complete_status_exists(self):
        """Extracted (Complete) should be a valid phase status."""
        assert "Extracted (Complete)" in VALID_PHASE_STATUSES


class TestExtractSubProjectReference:
    """Tests for extract_sub_project_reference function."""

    def test_extracts_from_status_with_to(self):
        """Should extract project ID from 'Extracted to PROJ-XX' status."""
        phase = Phase(
            number=3,
            name="Test Phase",
            status="Extracted to PROJ-42",
            objective="Test objective"
        )
        result = extract_sub_project_reference(phase)
        assert result == "PROJ-42"

    def test_extracts_from_status_with_arrow(self):
        """Should extract project ID from '-> PROJ-XX' format."""
        phase = Phase(
            number=3,
            name="Test Phase",
            status="Extracted -> PROJ-15",
            objective="Test objective"
        )
        result = extract_sub_project_reference(phase)
        assert result == "PROJ-15"

    def test_extracts_from_objective(self):
        """Should extract project ID from objective if not in status."""
        phase = Phase(
            number=3,
            name="Test Phase",
            status="Extracted",
            objective="**Extracted To:** PROJ-99"
        )
        result = extract_sub_project_reference(phase)
        assert result == "PROJ-99"

    def test_returns_none_when_not_found(self):
        """Should return None if no sub-project reference found."""
        phase = Phase(
            number=3,
            name="Test Phase",
            status="In Progress",
            objective="Working on tasks"
        )
        result = extract_sub_project_reference(phase)
        assert result is None

    def test_handles_complete_status(self):
        """Should extract from Extracted (Complete) status."""
        phase = Phase(
            number=3,
            name="Test Phase",
            status="Extracted (Complete) -> PROJ-07",
            objective="Done"
        )
        result = extract_sub_project_reference(phase)
        assert result == "PROJ-07"


class TestFindExtractedPhases:
    """Tests for find_extracted_phases function."""

    def test_finds_single_extracted_phase(self):
        """Should find a single extracted phase."""
        project_data = ProjectData(
            project_id="PROJ-01",
            title="Test Project",
            content="",
            phases=[
                Phase(number=1, name="Phase 1", status="Complete"),
                Phase(number=2, name="Phase 2", status="Extracted to PROJ-50"),
                Phase(number=3, name="Phase 3", status="Not Started"),
            ]
        )
        result = find_extracted_phases(project_data)
        assert len(result) == 1
        assert result[0] == (2, "PROJ-50")

    def test_finds_multiple_extracted_phases(self):
        """Should find multiple extracted phases."""
        project_data = ProjectData(
            project_id="PROJ-01",
            title="Test Project",
            content="",
            phases=[
                Phase(number=1, name="Phase 1", status="Extracted to PROJ-10"),
                Phase(number=2, name="Phase 2", status="Extracted -> PROJ-11"),
                Phase(number=3, name="Phase 3", status="Complete"),
            ]
        )
        result = find_extracted_phases(project_data)
        assert len(result) == 2
        assert (1, "PROJ-10") in result
        assert (2, "PROJ-11") in result

    def test_returns_empty_when_no_extracted_phases(self):
        """Should return empty list when no extracted phases."""
        project_data = ProjectData(
            project_id="PROJ-01",
            title="Test Project",
            content="",
            phases=[
                Phase(number=1, name="Phase 1", status="Complete"),
                Phase(number=2, name="Phase 2", status="In Progress"),
            ]
        )
        result = find_extracted_phases(project_data)
        assert len(result) == 0

    def test_skips_extracted_without_reference(self):
        """Should skip extracted phases without valid sub-project reference."""
        project_data = ProjectData(
            project_id="PROJ-01",
            title="Test Project",
            content="",
            phases=[
                Phase(number=1, name="Phase 1", status="Extracted"),  # No reference
                Phase(number=2, name="Phase 2", status="Extracted to PROJ-20"),
            ]
        )
        result = find_extracted_phases(project_data)
        # Only finds the one with a valid reference
        assert len(result) == 1
        assert result[0] == (2, "PROJ-20")


class TestIsProjectArchived:
    """Tests for is_project_archived function."""

    def test_returns_false_for_nonexistent_project(self):
        """Should return False for projects that don't exist."""
        result = is_project_archived("PROJ-99999")
        assert result is False

    def test_detects_archived_directory(self, tmp_path, monkeypatch):
        """Should detect archived project directory."""
        # Create fake archived directory
        archived_dir = tmp_path / "archived_projects"
        archived_dir.mkdir()
        (archived_dir / "PROJ-TEST").mkdir()

        # Patch ARCHIVED_DIR
        monkeypatch.setattr("utils.index_manager.ARCHIVED_DIR", archived_dir)

        result = is_project_archived("PROJ-TEST")
        assert result is True

    def test_detects_archived_file(self, tmp_path, monkeypatch):
        """Should detect archived project file (old format)."""
        archived_dir = tmp_path / "archived_projects"
        archived_dir.mkdir()
        (archived_dir / "PROJ-TEST.md").write_text("# Test")

        monkeypatch.setattr("utils.index_manager.ARCHIVED_DIR", archived_dir)

        result = is_project_archived("PROJ-TEST")
        assert result is True


class TestProjectExists:
    """Tests for project_exists function."""

    def test_returns_false_for_nonexistent_project(self):
        """Should return False for projects that don't exist."""
        result = project_exists("PROJ-99999")
        assert result is False

    def test_detects_active_directory(self, tmp_path, monkeypatch):
        """Should detect active project directory."""
        active_dir = tmp_path / "active_projects"
        active_dir.mkdir()
        (active_dir / "PROJ-TEST").mkdir()

        monkeypatch.setattr("utils.index_manager.ACTIVE_DIR", active_dir)
        monkeypatch.setattr("utils.index_manager.ARCHIVED_DIR", tmp_path / "archived")

        result = project_exists("PROJ-TEST")
        assert result is True

    def test_detects_archived_project(self, tmp_path, monkeypatch):
        """Should detect project in archived directory."""
        active_dir = tmp_path / "active_projects"
        active_dir.mkdir()
        archived_dir = tmp_path / "archived_projects"
        archived_dir.mkdir()
        (archived_dir / "PROJ-TEST").mkdir()

        monkeypatch.setattr("utils.index_manager.ACTIVE_DIR", active_dir)
        monkeypatch.setattr("utils.index_manager.ARCHIVED_DIR", archived_dir)

        result = project_exists("PROJ-TEST")
        assert result is True


class TestExtractPhaseScript:
    """Integration tests for the extract_phase.py script."""

    @pytest.fixture
    def mock_project_structure(self, tmp_path, monkeypatch):
        """Create a mock project structure for testing."""
        # Create directories
        active_dir = tmp_path / "active_projects"
        archived_dir = tmp_path / "archived_projects"
        active_dir.mkdir()
        archived_dir.mkdir()

        # Create a test project
        project_dir = active_dir / "PROJ-TEST"
        project_dir.mkdir()
        (project_dir / "findings").mkdir()

        # Create plan.md
        plan_content = """# PROJ-TEST: Test Project

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Setup | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Implementation | In Progress | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-01-28
**Active Phase:** Phase 2
"""
        (project_dir / "plan.md").write_text(plan_content)

        # Create decisions.md
        decisions_content = """# PROJ-TEST: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-28 | Project initialized | Starting point |
"""
        (project_dir / "decisions.md").write_text(decisions_content)

        # Create phase checklist
        phase_content = """# Phase 2: Implementation

**Status:** In Progress
**Objective:** Implement the feature

## Tasks

### Task 2.1: Write code [Medium]
**File:** `src/main.py`
**Tests:** `pytest tests/`

- [ ] Write function
- [ ] Add tests
- [ ] Document

**Notes:**
"""
        (project_dir / "phase_2_checklist.md").write_text(phase_content)

        # Create index file
        index_content = """# Projects Index

Next Project ID: PROJ-02

## Active Projects
| ID | Title | Status | Started | Last Updated |
|-----|-------|--------|---------|--------------|
| PROJ-TEST | Test Project | In Progress | 2026-01-28 | 2026-01-28 |

## Archived Projects
| ID | Title | Status | Started | Completed |
|-----|-------|--------|---------|-----------|
"""
        (tmp_path / "projects_index.md").write_text(index_content)

        # Patch the config
        monkeypatch.setattr("utils.config.ACTIVE_DIR", active_dir)
        monkeypatch.setattr("utils.config.ARCHIVED_DIR", archived_dir)
        monkeypatch.setattr("utils.config.INDEX_FILE", tmp_path / "projects_index.md")

        return {
            "tmp_path": tmp_path,
            "active_dir": active_dir,
            "archived_dir": archived_dir,
            "project_dir": project_dir,
        }

    def test_validate_extraction_success(self, mock_project_structure):
        """Should pass validation for valid extraction request."""
        from extract_phase import validate_extraction

        errors = validate_extraction("PROJ-TEST", 2)
        assert len(errors) == 0

    def test_validate_extraction_nonexistent_project(self, mock_project_structure):
        """Should fail validation for non-existent project."""
        from extract_phase import validate_extraction

        errors = validate_extraction("PROJ-FAKE", 1)
        assert len(errors) > 0
        assert "not found" in errors[0].lower()

    def test_validate_extraction_nonexistent_phase(self, mock_project_structure):
        """Should fail validation for non-existent phase."""
        from extract_phase import validate_extraction

        errors = validate_extraction("PROJ-TEST", 99)
        assert len(errors) > 0
        assert "not found" in errors[0].lower()

    def test_format_tasks_for_archive(self, mock_project_structure):
        """Should format tasks correctly for archival."""
        from extract_phase import format_tasks_for_archive

        phase = Phase(
            number=2,
            name="Test Phase",
            status="In Progress",
            tasks=[
                Task(
                    id="2.1",
                    name="Test Task",
                    complexity="Medium",
                    file_path="src/main.py",
                    tests="pytest tests/",
                    subtasks=[(False, "Do something"), (True, "Done thing")],
                    notes="Some notes"
                )
            ]
        )

        result = format_tasks_for_archive(phase)
        assert "Task 2.1" in result
        assert "Test Task" in result
        assert "[Medium]" in result
        assert "[ ] Do something" in result
        assert "[x] Done thing" in result
        assert "Some notes" in result

    def test_update_plan_quick_status(self, mock_project_structure):
        """Should update Quick Status table correctly."""
        from extract_phase import update_plan_quick_status

        plan_content = """# Project

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Setup | Complete | [file](file) |
| 2. Impl | In Progress | [file](file) |
"""
        updated = update_plan_quick_status(plan_content, 2, "PROJ-NEW")
        assert "**Extracted**" in updated
        assert "PROJ-NEW" in updated

    def test_add_decisions_entry(self, mock_project_structure):
        """Should add entry to decisions log table."""
        from extract_phase import add_decisions_entry

        decisions_content = """# Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-01 | Old decision | Reason |
"""
        entry = "| 2026-01-28 | New decision | New reason |"
        updated = add_decisions_entry(decisions_content, entry)

        assert "New decision" in updated
        assert "Old decision" in updated
        # New entry should appear after header
        assert updated.index("New decision") < updated.index("Old decision")


class TestValidatePhaseWithExtracted:
    """Test validate_phase.py handling of extracted phases."""

    def test_validate_phase_extracted_with_active_subproject(self, tmp_path, monkeypatch):
        """Should pass validation for extracted phase with active sub-project."""
        # This tests the integration between validate_phase and extraction
        # The actual test would require setting up the full project structure
        pass  # Placeholder for integration test

    def test_validate_phase_extracted_with_archived_subproject(self, tmp_path, monkeypatch):
        """Should pass and suggest auto-complete for archived sub-project."""
        pass  # Placeholder for integration test


class TestValidateAuditReadyWithExtracted:
    """Test validate_audit_ready.py handling of extracted phases."""

    def test_audit_ready_with_extracted_phases(self, tmp_path, monkeypatch):
        """Should include extracted phase checks in audit validation."""
        pass  # Placeholder for integration test

    def test_audit_ready_warns_active_subproject(self, tmp_path, monkeypatch):
        """Should warn when sub-project is still active."""
        pass  # Placeholder for integration test

    def test_audit_ready_errors_missing_subproject(self, tmp_path, monkeypatch):
        """Should error when sub-project reference is invalid."""
        pass  # Placeholder for integration test
