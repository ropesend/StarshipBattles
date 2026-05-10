"""PROJ-312 Phase 6 — ReplayResolver graceful-degradation tests.

The resolver wraps ReplayStore with a UI-friendly result type so the
Event Log button can render "missing" / "corrupt" / "version drift" /
"registry drift" affordances without raising.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from game.simulation.replay import REPLAY_SCHEMA_VERSION
from game.strategy.services.replay_resolver import ReplayLookup, ReplayResolver
from game.strategy.services.replay_store import ReplaySettings, ReplayStore


def _make_record(replay_id: str, *, components_hash: str = "sha256:current"):
    from tests.integration.replay.test_replay_store import _make_record as _factory
    rec = _factory(replay_id)
    from dataclasses import replace
    return replace(rec, components_registry_hash=components_hash)


@pytest.fixture
def store(tmp_path: Path) -> ReplayStore:
    save_root = tmp_path / "save"
    save_root.mkdir()
    s = ReplayStore(settings=ReplaySettings(max_replays_per_save=10))
    s.set_save_root(save_root)
    return s


class TestReplayResolver:
    def test_resolve_missing_id_returns_missing(self, store: ReplayStore):
        resolver = ReplayResolver(store, current_components_registry_hash="sha256:current")
        assert resolver.resolve("").found is False
        assert resolver.resolve("").reason == "missing"

    def test_resolve_unknown_replay_returns_missing(self, store: ReplayStore):
        resolver = ReplayResolver(store, current_components_registry_hash="sha256:current")
        result = resolver.resolve("does-not-exist")
        assert result.found is False
        assert result.reason == "missing"

    def test_resolve_healthy_replay_returns_found(self, store: ReplayStore):
        store.persist(_make_record("ok", components_hash="sha256:current"))
        resolver = ReplayResolver(store, current_components_registry_hash="sha256:current")
        result = resolver.resolve("ok")
        assert result.found is True
        assert result.record is not None
        assert result.registry_drift is False

    def test_resolve_corrupt_file_returns_corrupt(self, store: ReplayStore):
        rd = store.save_root / "replays"  # type: ignore[union-attr]
        rd.mkdir(exist_ok=True)
        (rd / "replay_garbage.json").write_text("{not valid")
        resolver = ReplayResolver(store, current_components_registry_hash="sha256:current")
        result = resolver.resolve("garbage")
        assert result.found is False
        assert result.reason == "corrupt"

    def test_resolve_version_mismatch_returns_version_drift(self, store: ReplayStore):
        from dataclasses import replace
        rec = replace(_make_record("future"), schema_version="0.0.0-stale")
        rd = store.save_root / "replays"  # type: ignore[union-attr]
        rd.mkdir(exist_ok=True)
        (rd / "replay_future.json").write_text(json.dumps(rec.to_dict()))
        resolver = ReplayResolver(store, current_components_registry_hash="sha256:current")
        result = resolver.resolve("future")
        assert result.found is False
        assert result.reason == "version_drift"

    def test_resolve_flags_registry_drift(self, store: ReplayStore):
        store.persist(_make_record("drifted", components_hash="sha256:OLD"))
        resolver = ReplayResolver(store, current_components_registry_hash="sha256:NEW")
        result = resolver.resolve("drifted")
        assert result.found is True  # still loadable
        assert result.registry_drift is True

    def test_no_drift_when_either_hash_is_empty(self, store: ReplayStore):
        """Defensive: if either side has an empty/unknown hash, don't
        flag drift — neither is authoritative."""
        store.persist(_make_record("untracked", components_hash=""))
        resolver = ReplayResolver(store, current_components_registry_hash="sha256:current")
        result = resolver.resolve("untracked")
        assert result.found is True
        assert result.registry_drift is False

    def test_from_registries_factory(self, fresh_registries, store: ReplayStore):
        resolver = ReplayResolver.from_registries(store, fresh_registries)
        # The resolver took the live hash; resolving a missing replay still
        # returns gracefully.
        assert resolver.resolve("nope").reason == "missing"
