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

    def test_resolve_when_store_has_no_replay_dir_returns_missing(self):
        class _NoReplayDirStore:
            replay_dir = None

            def load_or_error(self, replay_id: str):
                raise AssertionError("load_or_error should not be called")

        resolver = ReplayResolver(
            _NoReplayDirStore(),
            current_components_registry_hash="sha256:current",
        )

        result = resolver.resolve("not-mounted")

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


# PROJ-354B Phase 3.2: ReplayResolver surfaces sidecar verification status.
class TestReplayResolverSidecarStatus:
    def test_no_sidecar_yields_none(self, store: ReplayStore):
        store.persist(_make_record("plain"))
        resolver = ReplayResolver(
            store, current_components_registry_hash="sha256:current"
        )
        result = resolver.resolve("plain")
        assert result.found is True
        assert result.verification_status is None

    def test_passed_sidecar_surfaced(self, store: ReplayStore):
        from game.strategy.services.replay_verification_sidecar import (
            REPLAY_VERIFICATION_SCHEMA_VERSION,
            VerificationSidecar,
            VerificationSource,
            VerificationStatus,
            write_verification_sidecar,
        )
        store.persist(_make_record("good"))
        rd = store.save_root / "replays"  # type: ignore[union-attr]
        write_verification_sidecar(
            rd,
            VerificationSidecar(
                replay_id="good",
                schema_version=REPLAY_VERIFICATION_SCHEMA_VERSION,
                status=VerificationStatus.PASSED.name,
                source=VerificationSource.BACKGROUND.name,
                verified_at="2026-05-04T00:00:00+00:00",
                duration_ms=10,
                diff=None,
                error=None,
            ),
        )
        resolver = ReplayResolver(
            store, current_components_registry_hash="sha256:current"
        )
        result = resolver.resolve("good")
        assert result.found is True
        assert result.verification_status == "PASSED"

    def test_failed_sidecar_surfaced(self, store: ReplayStore):
        from game.strategy.services.replay_verification_sidecar import (
            REPLAY_VERIFICATION_SCHEMA_VERSION,
            VerificationSidecar,
            VerificationSource,
            VerificationStatus,
            write_verification_sidecar,
        )
        store.persist(_make_record("bad"))
        rd = store.save_root / "replays"  # type: ignore[union-attr]
        write_verification_sidecar(
            rd,
            VerificationSidecar(
                replay_id="bad",
                schema_version=REPLAY_VERIFICATION_SCHEMA_VERSION,
                status=VerificationStatus.FAILED.name,
                source=VerificationSource.BACKGROUND.name,
                verified_at="2026-05-04T00:00:00+00:00",
                duration_ms=15,
                diff=[{"path": ["x"], "expected": 1, "actual": 2}],
                error=None,
            ),
        )
        resolver = ReplayResolver(
            store, current_components_registry_hash="sha256:current"
        )
        result = resolver.resolve("bad")
        assert result.verification_status == "FAILED"

    def test_corrupt_sidecar_yields_none(self, store: ReplayStore):
        from game.strategy.services.replay_verification_sidecar import (
            sidecar_path_for_replay,
        )
        store.persist(_make_record("c1"))
        rd = store.save_root / "replays"  # type: ignore[union-attr]
        sidecar_path_for_replay(rd, "c1").write_text("{not valid")
        resolver = ReplayResolver(
            store, current_components_registry_hash="sha256:current"
        )
        result = resolver.resolve("c1")
        assert result.found is True  # replay still loadable
        assert result.verification_status is None  # sidecar unreadable
