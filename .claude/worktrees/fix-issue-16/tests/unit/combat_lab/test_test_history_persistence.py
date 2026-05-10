"""
Tests for the sharded TestHistory store.

Each test_id has its own JSON shard under ``history_dir/{test_id}.json``.
Shards load lazily on first query and are written atomically via
``save_json`` (temp + rename). A single corrupt shard affects only that
test; others are unaffected. A one-shot migration splits any legacy
monolithic ``test_history.json`` into per-test shards.
"""

import json

from combat_lab.test_history import TestHistory


def _make_results(passed: bool = True, ticks: int = 100):
    return {
        'ticks_run': ticks,
        'has_validation_failures': not passed,
        'validation_summary': {'pass': 1 if passed else 0, 'fail': 0 if passed else 1, 'warn': 0},
        'validation_results': [],
    }


class TestHistoryRoundTrip:
    """Test that history survives save -> load cycle across shards."""

    def test_save_and_reload(self, tmp_path):
        """A run written by one TestHistory instance is read by another."""
        history_dir = str(tmp_path / "history")

        h1 = TestHistory(history_dir=history_dir)
        h1.add_run("TEST-001", _make_results(passed=True, ticks=500))

        h2 = TestHistory(history_dir=history_dir)
        runs = h2.get_runs("TEST-001")

        assert len(runs) == 1
        assert runs[0].passed is True
        assert runs[0].ticks_run == 500

    def test_multiple_tests_persist_as_separate_shards(self, tmp_path):
        """Each test_id writes to its own shard file."""
        history_dir = tmp_path / "history"

        h1 = TestHistory(history_dir=str(history_dir))
        for tid in ["A-001", "B-001", "C-001"]:
            h1.add_run(tid, _make_results())

        assert (history_dir / "A-001.json").exists()
        assert (history_dir / "B-001.json").exists()
        assert (history_dir / "C-001.json").exists()

        h2 = TestHistory(history_dir=str(history_dir))
        assert len(h2.get_runs("A-001")) == 1
        assert len(h2.get_runs("B-001")) == 1
        assert len(h2.get_runs("C-001")) == 1

    def test_multiple_runs_per_test_persist(self, tmp_path):
        """Multiple runs for the same test survive reload in order."""
        history_dir = str(tmp_path / "history")

        h1 = TestHistory(history_dir=history_dir)
        for i in range(5):
            h1.add_run("TEST-001", _make_results(passed=(i % 2 == 1), ticks=i * 100))

        h2 = TestHistory(history_dir=history_dir)
        runs = h2.get_runs("TEST-001")

        assert len(runs) == 5
        assert [r.ticks_run for r in runs] == [0, 100, 200, 300, 400]

    def test_max_runs_per_shard_enforced(self, tmp_path):
        """max_runs keeps only the newest N runs in a shard."""
        history_dir = str(tmp_path / "history")

        h = TestHistory(history_dir=history_dir, max_runs=3)
        for i in range(5):
            h.add_run("TEST-001", _make_results(ticks=i))

        runs = TestHistory(history_dir=history_dir, max_runs=3).get_runs("TEST-001")
        assert len(runs) == 3
        assert [r.ticks_run for r in runs] == [2, 3, 4]

    def test_failed_test_persists(self, tmp_path):
        """Failed run is persisted with passed=False."""
        history_dir = str(tmp_path / "history")

        h1 = TestHistory(history_dir=history_dir)
        h1.add_run("FAIL-001", {
            'ticks_run': 500,
            'has_validation_failures': True,
            'validation_summary': {'pass': 2, 'fail': 1, 'warn': 0},
            'validation_results': [
                {'name': 'Hit Rate', 'status': 'FAIL', 'phase': 'outcome'},
            ],
        })

        h2 = TestHistory(history_dir=history_dir)
        latest = h2.get_latest_run("FAIL-001")

        assert latest is not None
        assert latest.passed is False


class TestHistoryLazyLoad:
    """Test that shards are loaded only on demand."""

    def test_init_does_not_load_existing_shards(self, tmp_path):
        """Constructor does not eagerly read every shard on disk."""
        history_dir = tmp_path / "history"
        history_dir.mkdir()
        # Pre-populate a shard on disk
        (history_dir / "TEST-001.json").write_text(json.dumps([]))

        h = TestHistory(history_dir=str(history_dir))

        # Cache is empty until something queries TEST-001
        assert "TEST-001" not in h._loaded

        h.get_runs("TEST-001")

        assert "TEST-001" in h._loaded

    def test_nonexistent_test_returns_empty_list(self, tmp_path):
        """Querying a test_id with no shard returns an empty list."""
        h = TestHistory(history_dir=str(tmp_path / "history"))

        assert h.get_runs("NEVER-WRITTEN") == []
        assert h.get_latest_run("NEVER-WRITTEN") is None
        assert h.get_pass_rate("NEVER-WRITTEN") is None
        assert h.get_run_count("NEVER-WRITTEN") == 0


class TestHistoryCorruptShardRecovery:
    """Test that corrupt individual shards are handled gracefully."""

    def test_corrupt_shard_starts_fresh(self, tmp_path):
        """A corrupt shard yields an empty history for that test, not a crash."""
        history_dir = tmp_path / "history"
        history_dir.mkdir()
        (history_dir / "TEST-001.json").write_text('{"unclosed": ')

        h = TestHistory(history_dir=str(history_dir))

        assert h.get_runs("TEST-001") == []

    def test_corrupt_shard_backed_up(self, tmp_path):
        """A corrupt shard is copied to <test_id>.json.corrupt before reset."""
        history_dir = tmp_path / "history"
        history_dir.mkdir()
        corrupt_content = '{"unclosed": '
        (history_dir / "TEST-001.json").write_text(corrupt_content)

        h = TestHistory(history_dir=str(history_dir))
        h.get_runs("TEST-001")  # triggers lazy load + corruption detection

        backup = history_dir / "TEST-001.json.corrupt"
        assert backup.exists()
        assert backup.read_text() == corrupt_content

    def test_corrupt_shard_does_not_affect_other_shards(self, tmp_path):
        """Corruption in one shard leaves other tests' histories intact."""
        history_dir = tmp_path / "history"
        history_dir.mkdir()
        (history_dir / "BROKEN-001.json").write_text('INVALID JSON')
        good_runs = [{
            'timestamp': '2026-04-12T00:00:00',
            'ticks_run': 10,
            'passed': True,
            'metrics': {},
            'validation_summary': None,
            'validation_results': [],
            'initial_state_file': None,
            'final_state_file': None,
            'seed': None,
        }]
        (history_dir / "GOOD-001.json").write_text(json.dumps(good_runs))

        h = TestHistory(history_dir=str(history_dir))

        assert h.get_runs("BROKEN-001") == []
        assert len(h.get_runs("GOOD-001")) == 1

    def test_valid_data_after_corrupt_recovery(self, tmp_path):
        """After recovery the shard can be rewritten cleanly."""
        history_dir = tmp_path / "history"
        history_dir.mkdir()
        (history_dir / "TEST-001.json").write_text('INVALID JSON CONTENT')

        h = TestHistory(history_dir=str(history_dir))
        h.add_run("TEST-001", _make_results())

        h2 = TestHistory(history_dir=str(history_dir))
        assert len(h2.get_runs("TEST-001")) == 1


class TestHistoryInitialization:
    """Test that the TestHistory constructor sets up correctly."""

    def test_nonexistent_history_dir_is_created(self, tmp_path):
        """Constructor creates the shard directory if it does not exist."""
        history_dir = tmp_path / "nested" / "history"

        assert not history_dir.exists()

        TestHistory(history_dir=str(history_dir))

        assert history_dir.exists() and history_dir.is_dir()

    def test_empty_history_dir_yields_empty_cache(self, tmp_path):
        """Empty shard directory produces an empty in-memory cache."""
        h = TestHistory(history_dir=str(tmp_path / "history"))

        assert h.history == {}
        assert h._loaded == set()


class TestHistoryMigrationFromMonolith:
    """Test one-shot migration from the legacy monolithic test_history.json."""

    def test_legacy_file_is_split_into_shards(self, tmp_path):
        """A legacy test_history.json alongside the shard dir is migrated."""
        base_dir = tmp_path / "combat_lab"
        history_dir = base_dir / "test_history"
        legacy_file = base_dir / "test_history.json"
        base_dir.mkdir()

        legacy_file.write_text(json.dumps({
            "A-001": [{
                'timestamp': '2026-04-12T00:00:00',
                'ticks_run': 5,
                'passed': True,
                'metrics': {},
                'validation_summary': None,
                'validation_results': [],
                'initial_state_file': None,
                'final_state_file': None,
                'seed': None,
            }],
            "B-001": [],
        }))

        h = TestHistory(history_dir=str(history_dir))

        # Shard files were created
        assert (history_dir / "A-001.json").exists()
        assert (history_dir / "B-001.json").exists()
        # Legacy file was renamed so migration only runs once
        assert not legacy_file.exists()
        assert (base_dir / "test_history.json.migrated").exists()
        # Data is readable through the new API
        runs = h.get_runs("A-001")
        assert len(runs) == 1
        assert runs[0].ticks_run == 5
