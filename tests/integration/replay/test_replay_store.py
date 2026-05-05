"""PROJ-312 Phase 4 — ReplayStore + lifecycle tests.

Covers:
    * persist → load → list happy path with atomic write
    * Ring-buffer eviction is write-then-evict
    * Settings fallback on missing replay_settings.json
    * Schema-version mismatch silently skipped
    * Corrupt file silently skipped
    * SaveGameService lifecycle hooks (set_save_root / clear_save_root /
      cascade-with-rmtree)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from game.simulation.replay import (
    REPLAY_SCHEMA_VERSION,
    ReplayCaptureContext,
    ReplayOutcome,
    ReplayRecord,
    ReplaySpec,
)
from game.strategy.services.replay_store import (
    ReplaySettings,
    ReplayStore,
    load_replay_settings,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_minimal_battle_spec():
    """Reuse the spec helper from the serialization tests by lazy import."""
    from tests.unit.simulation.replay.test_serialization import (
        _make_minimal_battle_spec,
    )
    return _make_minimal_battle_spec()


def _make_minimal_outcome():
    from tests.unit.simulation.replay.test_serialization import (
        _make_minimal_outcome,
    )
    return _make_minimal_outcome()


def _make_record(replay_id: str = "r-1", *, captured_at: str = "2026-04-27T00:00:00Z") -> ReplayRecord:
    spec = _make_minimal_battle_spec()
    outcome = _make_minimal_outcome()
    return ReplayRecord(
        schema_version=REPLAY_SCHEMA_VERSION,
        replay_id=replay_id,
        captured_at=captured_at,
        sector_name="test",
        sector_coords=(0, 0),
        turn_number=1,
        participating_empires=("A", "B"),
        components_registry_hash="sha256:test",
        spec=ReplaySpec.from_battle_spec(spec),
        outcome=ReplayOutcome.from_battle_outcome(outcome),
    )


@pytest.fixture
def store(tmp_path: Path) -> ReplayStore:
    save_root = tmp_path / "save_a"
    save_root.mkdir()
    s = ReplayStore(settings=ReplaySettings(max_replays_per_save=3))
    s.set_save_root(save_root)
    return s


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


class TestReplaySettings:
    def test_load_returns_defaults_when_missing(self, tmp_path: Path):
        path = tmp_path / "missing.json"
        settings = load_replay_settings(path=path)
        assert settings.max_replays_per_save == 50

    def test_load_parses_real_file(self, tmp_path: Path):
        path = tmp_path / "replay_settings.json"
        path.write_text(json.dumps({"max_replays_per_save": 12}))
        settings = load_replay_settings(path=path)
        assert settings.max_replays_per_save == 12

    def test_load_clamps_to_minimum_one(self, tmp_path: Path):
        path = tmp_path / "replay_settings.json"
        path.write_text(json.dumps({"max_replays_per_save": 0}))
        settings = load_replay_settings(path=path)
        assert settings.max_replays_per_save >= 1

    def test_load_falls_back_on_malformed_json(self, tmp_path: Path):
        path = tmp_path / "replay_settings.json"
        path.write_text("{not valid json")
        settings = load_replay_settings(path=path)
        assert settings.max_replays_per_save == 50

    # PROJ-354B Phase 1.1: verification settings
    def test_verification_defaults_when_missing(self, tmp_path: Path):
        path = tmp_path / "missing.json"
        settings = load_replay_settings(path=path)
        assert settings.verification_enabled is True
        assert settings.verification_queue_cap == 16

    def test_verification_overrides_via_json(self, tmp_path: Path):
        path = tmp_path / "replay_settings.json"
        path.write_text(json.dumps({
            "max_replays_per_save": 12,
            "verification_enabled": False,
            "verification_queue_cap": 4,
        }))
        settings = load_replay_settings(path=path)
        assert settings.verification_enabled is False
        assert settings.verification_queue_cap == 4

    def test_verification_queue_cap_clamped_to_minimum_one(self, tmp_path: Path):
        path = tmp_path / "replay_settings.json"
        path.write_text(json.dumps({"verification_queue_cap": 0}))
        settings = load_replay_settings(path=path)
        assert settings.verification_queue_cap == 1

    def test_verification_queue_cap_invalid_falls_back_to_default(
        self, tmp_path: Path
    ):
        path = tmp_path / "replay_settings.json"
        path.write_text(json.dumps({"verification_queue_cap": "not-an-int"}))
        settings = load_replay_settings(path=path)
        assert settings.verification_queue_cap == 16

    def test_verification_enabled_falsy_value_coerced(self, tmp_path: Path):
        path = tmp_path / "replay_settings.json"
        path.write_text(json.dumps({"verification_enabled": 0}))
        settings = load_replay_settings(path=path)
        assert settings.verification_enabled is False

    def test_malformed_json_keeps_verification_defaults(self, tmp_path: Path):
        path = tmp_path / "replay_settings.json"
        path.write_text("{not valid json")
        settings = load_replay_settings(path=path)
        assert settings.verification_enabled is True
        assert settings.verification_queue_cap == 16


# ---------------------------------------------------------------------------
# ReplayStore — persistence + ring buffer
# ---------------------------------------------------------------------------


class TestReplayStorePersistence:
    def test_persist_writes_a_replay_file(self, store: ReplayStore):
        path = store.persist(_make_record("first"))
        assert path is not None
        assert path.exists()
        assert path.name.startswith("replay_") and path.name.endswith(".json")

    def test_persist_returns_none_when_no_save_root(self, tmp_path: Path):
        unbound = ReplayStore()
        assert unbound.persist(_make_record("x")) is None

    def test_load_round_trips(self, store: ReplayStore):
        store.persist(_make_record("foo"))
        loaded = store.load("foo")
        assert loaded is not None
        assert loaded.replay_id == "foo"

    def test_list_sorted_newest_first(self, store: ReplayStore):
        store.persist(_make_record("old", captured_at="2026-04-25T00:00:00Z"))
        store.persist(_make_record("new", captured_at="2026-04-27T00:00:00Z"))
        ids = [r.replay_id for r in store.list()]
        assert ids == ["new", "old"]

    def test_delete_removes_file(self, store: ReplayStore):
        store.persist(_make_record("doomed"))
        assert store.delete("doomed") is True
        assert store.load("doomed") is None

    def test_delete_returns_false_for_missing(self, store: ReplayStore):
        assert store.delete("never-existed") is False


class TestReplayStoreRingBuffer:
    def test_evicts_excess_after_write(self, store: ReplayStore):
        # cap=3 (fixture). Persist 5 records with monotonic captured_at.
        for i in range(5):
            store.persist(_make_record(f"r{i}", captured_at=f"2026-04-27T00:00:0{i}Z"))
        kept = {r.replay_id for r in store.list()}
        assert len(kept) == 3

    def test_writes_before_evicting(self, tmp_path: Path):
        """If the eviction step ran first and the new write then failed,
        the user would lose a replay. Verify the new file lands first."""
        save_root = tmp_path / "save"
        save_root.mkdir()
        seen_files_during_write: list = []

        def fake_writer(path_str: str, data: Dict[str, Any]) -> None:
            # During the write call, list whatever's already in the dir.
            seen_files_during_write.append(
                sorted(p.name for p in (save_root / "replays").glob("*.json"))
            )
            # Actually persist (so the rest of the test can read it back).
            (save_root / "replays").mkdir(exist_ok=True)
            from pathlib import Path as _P
            p = _P(path_str)
            p.write_text(json.dumps(data))

        s = ReplayStore(
            settings=ReplaySettings(max_replays_per_save=2),
            json_writer=fake_writer,
        )
        s.set_save_root(save_root)
        s.persist(_make_record("a", captured_at="2026-04-27T00:00:01Z"))
        s.persist(_make_record("b", captured_at="2026-04-27T00:00:02Z"))
        s.persist(_make_record("c", captured_at="2026-04-27T00:00:03Z"))
        # On the 3rd persist, when fake_writer was invoked, the dir held
        # the previous 2 (no eviction yet). Eviction runs *after*.
        assert len(seen_files_during_write[-1]) == 2


class TestReplayStoreGracefulDegradation:
    def test_corrupt_file_skipped_in_list(self, store: ReplayStore):
        store.persist(_make_record("ok"))
        # Create a corrupt sibling.
        rd = store.save_root / "replays"  # type: ignore[union-attr]
        (rd / "replay_corrupt.json").write_text("{not valid")
        ids = [r.replay_id for r in store.list()]
        assert ids == ["ok"]

    def test_schema_mismatch_skipped(self, store: ReplayStore):
        # Write a record with wrong schema version directly.
        rec = _make_record("future")
        from dataclasses import replace
        bad = replace(rec, schema_version="0.0.1-stale")
        rd = store.save_root / "replays"  # type: ignore[union-attr]
        (rd / "replay_future.json").write_text(json.dumps(bad.to_dict()))
        ids = [r.replay_id for r in store.list()]
        assert "future" not in ids

    def test_load_returns_none_for_schema_mismatch(self, store: ReplayStore):
        from dataclasses import replace
        rec = replace(_make_record("future"), schema_version="0.0.1-stale")
        rd = store.save_root / "replays"  # type: ignore[union-attr]
        (rd / "replay_future.json").write_text(json.dumps(rec.to_dict()))
        assert store.load("future") is None


# ---------------------------------------------------------------------------
# IReplayCaptureSink path
# ---------------------------------------------------------------------------


class TestReplayStoreAsCaptureSink:
    def test_started_then_ended_persists_record(self, store: ReplayStore):
        spec = ReplaySpec.from_battle_spec(_make_minimal_battle_spec())
        outcome = ReplayOutcome.from_battle_outcome(_make_minimal_outcome())
        ctx = ReplayCaptureContext(
            sector_name="alpha",
            sector_coords=(2, 3),
            turn_number=7,
            participating_empires=("A", "B"),
            components_registry_hash="sha256:abc",
            captured_at="2026-04-27T12:00:00Z",
        )
        replay_id = store.on_battle_started(spec, context=ctx)
        assert replay_id  # non-empty
        store.on_battle_ended(replay_id, outcome)
        loaded = store.load(replay_id)
        assert loaded is not None
        assert loaded.sector_name == "alpha"
        assert loaded.sector_coords == (2, 3)
        assert loaded.turn_number == 7

    def test_started_returns_empty_when_no_save_root(self):
        s = ReplayStore()  # no save root
        spec = ReplaySpec.from_battle_spec(_make_minimal_battle_spec())
        ctx = ReplayCaptureContext()
        assert s.on_battle_started(spec, context=ctx) == ""

    def test_ended_without_matching_start_is_a_noop(self, store: ReplayStore):
        outcome = ReplayOutcome.from_battle_outcome(_make_minimal_outcome())
        # Should not raise.
        store.on_battle_ended("never-started", outcome)


# ---------------------------------------------------------------------------
# SaveGameService lifecycle hooks
# ---------------------------------------------------------------------------


class TestSaveGameServiceHooks:
    """Verify the module-level set_replay_store / hook helpers."""

    def setup_method(self):
        from game.strategy.systems import save_game_service
        save_game_service.set_replay_store(None)

    def teardown_method(self):
        from game.strategy.systems import save_game_service
        save_game_service.set_replay_store(None)

    def test_set_replay_store_is_called_by_save_path(self, tmp_path: Path):
        """The module-level _notify_replay_store_save_or_load should call
        set_save_root on a registered store."""
        from game.strategy.systems import save_game_service

        recorded = []

        class _Spy:
            def set_save_root(self, p):
                recorded.append(("set", p))

            def clear_save_root(self):
                recorded.append(("clear",))

        save_game_service.set_replay_store(_Spy())
        save_game_service._notify_replay_store_save_or_load(str(tmp_path))
        assert recorded[0][0] == "set"

    def test_clear_called_after_delete(self):
        from game.strategy.systems import save_game_service

        recorded = []

        class _Spy:
            def set_save_root(self, p):
                recorded.append(("set", p))

            def clear_save_root(self):
                recorded.append(("clear",))

        save_game_service.set_replay_store(_Spy())
        save_game_service._notify_replay_store_save_deleted()
        assert recorded == [("clear",)]

    def test_hooks_tolerate_missing_store(self):
        """When no store is registered, the helpers are silent no-ops."""
        from game.strategy.systems import save_game_service
        # Should not raise.
        save_game_service._notify_replay_store_save_or_load("/nope")
        save_game_service._notify_replay_store_save_deleted()
