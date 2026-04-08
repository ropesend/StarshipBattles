"""
Tests for TestHistory persistence — saving, loading, and corrupt file recovery.

Validates that test run history survives between sessions and handles
corrupt/truncated JSON files gracefully.
"""

import json
import os
from pathlib import Path

from combat_lab.test_history import TestHistory


class TestHistoryRoundTrip:
    """Test that history survives save → load cycle."""

    def test_save_and_reload(self, tmp_path):
        """Data saved by one TestHistory instance is loaded by another."""
        history_file = str(tmp_path / "history.json")

        # Session 1: add a run
        h1 = TestHistory(history_file=history_file)
        h1.add_run("TEST-001", {
            'ticks_run': 500,
            'has_validation_failures': False,
            'validation_summary': {'pass': 3, 'fail': 0, 'warn': 0},
            'validation_results': [{'name': 'Check1', 'status': 'PASS'}],
        })

        # Session 2: fresh load from same file
        h2 = TestHistory(history_file=history_file)

        runs = h2.get_runs("TEST-001")
        assert len(runs) == 1
        assert runs[0].passed is True
        assert runs[0].ticks_run == 500

    def test_multiple_tests_persist(self, tmp_path):
        """Multiple test IDs all survive reload."""
        history_file = str(tmp_path / "history.json")

        h1 = TestHistory(history_file=history_file)
        for tid in ["A-001", "B-001", "C-001"]:
            h1.add_run(tid, {
                'ticks_run': 100,
                'has_validation_failures': False,
                'validation_summary': {'pass': 1, 'fail': 0, 'warn': 0},
                'validation_results': [],
            })

        h2 = TestHistory(history_file=history_file)
        assert len(h2.get_runs("A-001")) == 1
        assert len(h2.get_runs("B-001")) == 1
        assert len(h2.get_runs("C-001")) == 1

    def test_multiple_runs_per_test_persist(self, tmp_path):
        """Multiple runs for the same test survive reload."""
        history_file = str(tmp_path / "history.json")

        h1 = TestHistory(history_file=history_file)
        for i in range(5):
            h1.add_run("TEST-001", {
                'ticks_run': i * 100,
                'has_validation_failures': (i % 2 == 0),
                'validation_summary': {'pass': 1, 'fail': 0, 'warn': 0},
                'validation_results': [],
            })

        h2 = TestHistory(history_file=history_file)
        runs = h2.get_runs("TEST-001")
        assert len(runs) == 5

    def test_failed_test_persists(self, tmp_path):
        """Failed test results are persisted and loaded correctly."""
        history_file = str(tmp_path / "history.json")

        h1 = TestHistory(history_file=history_file)
        h1.add_run("FAIL-001", {
            'ticks_run': 500,
            'has_validation_failures': True,
            'validation_summary': {'pass': 2, 'fail': 1, 'warn': 0},
            'validation_results': [
                {'name': 'Hit Rate', 'status': 'FAIL', 'phase': 'outcome'},
            ],
        })

        h2 = TestHistory(history_file=history_file)
        latest = h2.get_latest_run("FAIL-001")
        assert latest is not None
        assert latest.passed is False


class TestHistoryCorruptFileRecovery:
    """Test that corrupt/truncated JSON files are handled gracefully."""

    def test_truncated_json_starts_fresh(self, tmp_path):
        """Truncated JSON file results in empty history, not a crash."""
        history_file = tmp_path / "history.json"
        history_file.write_text('{"TEST-001": [{"passed": ')  # truncated

        h = TestHistory(history_file=str(history_file))

        assert h.get_runs("TEST-001") == []

    def test_corrupt_json_creates_backup(self, tmp_path):
        """Corrupt file is backed up before starting fresh."""
        history_file = tmp_path / "history.json"
        corrupt_content = '{"TEST-001": [{"passed": '
        history_file.write_text(corrupt_content)

        TestHistory(history_file=str(history_file))

        backup = tmp_path / "history.json.corrupt"
        assert backup.exists()
        assert backup.read_text() == corrupt_content

    def test_empty_file_starts_fresh(self, tmp_path):
        """Empty file results in empty history."""
        history_file = tmp_path / "history.json"
        history_file.write_text('')

        h = TestHistory(history_file=str(history_file))

        assert len(h.history) == 0

    def test_valid_data_after_corrupt_recovery(self, tmp_path):
        """After recovering from corrupt file, new saves work correctly."""
        history_file = tmp_path / "history.json"
        history_file.write_text('INVALID JSON CONTENT')

        h = TestHistory(history_file=str(history_file))
        h.add_run("RECOVERED-001", {
            'ticks_run': 100,
            'has_validation_failures': False,
            'validation_summary': {'pass': 1, 'fail': 0, 'warn': 0},
            'validation_results': [],
        })

        # Reload and verify the new data persisted
        h2 = TestHistory(history_file=str(history_file))
        assert len(h2.get_runs("RECOVERED-001")) == 1

    def test_nonexistent_file_creates_new(self, tmp_path):
        """Non-existent history file starts fresh without error."""
        history_file = str(tmp_path / "nonexistent" / "history.json")

        h = TestHistory(history_file=history_file)

        assert len(h.history) == 0
