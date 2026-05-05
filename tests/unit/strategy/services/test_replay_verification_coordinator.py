"""PROJ-354B Phase 4 — ReplayVerificationCoordinator tests.

The coordinator is a single-worker FIFO queue that subscribes to
``ReplayStore``'s post-persist listener and runs each captured replay
through the verifier headlessly. It mirrors the
``LLMBackgroundCall`` threading pattern (lock + cancel/done events +
module-level concurrency tracking + ``shutdown_all_calls``-style
shutdown).

These tests exercise the coordinator without needing a real battle
runner: they inject a stub ``run_replay_headless`` via constructor
arg and assert the resulting sidecars on disk.
"""
from __future__ import annotations

import threading
import time
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List

import pytest

from game.simulation.replay import REPLAY_SCHEMA_VERSION, ReplayOutcome, ReplayRecord, ReplaySpec
from game.strategy.services.replay_store import (
    ReplaySettings,
    ReplayStore,
)
from game.strategy.services.replay_verification_coordinator import (
    ReplayVerificationCoordinator,
    shutdown_all_coordinators,
)
from game.strategy.services.replay_verification_sidecar import (
    VerificationStatus,
    read_verification_sidecar,
    sidecar_path_for_replay,
)


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------


def _make_record(replay_id: str = "r1") -> ReplayRecord:
    from tests.unit.simulation.replay.test_serialization import (
        _make_minimal_battle_spec,
        _make_minimal_outcome,
    )
    spec = _make_minimal_battle_spec()
    outcome = _make_minimal_outcome()
    return ReplayRecord(
        schema_version=REPLAY_SCHEMA_VERSION,
        replay_id=replay_id,
        captured_at="2026-05-04T00:00:00Z",
        sector_name="test",
        sector_coords=(0, 0),
        turn_number=1,
        participating_empires=("A", "B"),
        components_registry_hash="sha256:t",
        spec=ReplaySpec.from_battle_spec(spec),
        outcome=ReplayOutcome.from_battle_outcome(outcome),
    )


@pytest.fixture
def store(tmp_path: Path) -> ReplayStore:
    save_root = tmp_path / "save"
    save_root.mkdir()
    s = ReplayStore(settings=ReplaySettings(max_replays_per_save=50))
    s.set_save_root(save_root)
    return s


def _identity_replay_runner(record, **_kwargs):
    """Stub run_replay_headless that just returns the captured outcome
    untouched. The verifier will see equality and pass."""
    return record.outcome.to_battle_outcome()


def _divergent_replay_runner(record, **_kwargs):
    """Stub that mutates one field of the captured outcome so the
    verifier emits a FAILED diff."""
    outcome = record.outcome.to_battle_outcome()
    return replace(outcome, duration_ticks=outcome.duration_ticks + 1)


def _raising_replay_runner(record, **_kwargs):
    raise RuntimeError("simulated headless failure")


@pytest.fixture(autouse=True)
def _shutdown_all_coordinators_after_test():
    """Defensively shut down any stray coordinators a test forgot to
    join, so a misbehaving test cannot leak threads into the next."""
    yield
    shutdown_all_coordinators(timeout=5.0)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCoordinatorBasics:
    def test_passes_when_outcome_matches(self, store: ReplayStore):
        record = _make_record("pass-1")
        coord = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=object(),
            registry_provider=object(),
            settings=store._settings,
            replay_runner=_identity_replay_runner,
            ship_builder_factory=lambda *a, **k: None,
        )
        coord.start()
        try:
            store.persist(record)
            assert coord.wait_for_idle(timeout=5.0)
        finally:
            coord.shutdown(timeout=5.0)

        rd = store.save_root / "replays"  # type: ignore[union-attr]
        sidecar = read_verification_sidecar(rd, "pass-1")
        assert sidecar is not None
        assert sidecar.status == VerificationStatus.PASSED.name
        assert sidecar.error is None
        assert sidecar.diff is None

    def test_fails_when_outcome_diverges(self, store: ReplayStore):
        record = _make_record("fail-1")
        coord = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=object(),
            registry_provider=object(),
            settings=store._settings,
            replay_runner=_divergent_replay_runner,
            ship_builder_factory=lambda *a, **k: None,
        )
        coord.start()
        try:
            store.persist(record)
            assert coord.wait_for_idle(timeout=5.0)
        finally:
            coord.shutdown(timeout=5.0)

        rd = store.save_root / "replays"  # type: ignore[union-attr]
        sidecar = read_verification_sidecar(rd, "fail-1")
        assert sidecar is not None
        assert sidecar.status == VerificationStatus.FAILED.name
        assert sidecar.diff is not None
        assert len(sidecar.diff) >= 1


class TestCoordinatorToggle:
    def test_disabled_setting_writes_skipped_sidecar(
        self, store: ReplayStore
    ):
        # Override to disabled
        store._settings = ReplaySettings(
            max_replays_per_save=50,
            verification_enabled=False,
            verification_queue_cap=16,
        )
        record = _make_record("disabled-1")
        coord = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=object(),
            registry_provider=object(),
            settings=store._settings,
            replay_runner=_identity_replay_runner,
            ship_builder_factory=lambda *a, **k: None,
        )
        coord.start()
        try:
            store.persist(record)
            assert coord.wait_for_idle(timeout=5.0)
        finally:
            coord.shutdown(timeout=5.0)

        rd = store.save_root / "replays"  # type: ignore[union-attr]
        sidecar = read_verification_sidecar(rd, "disabled-1")
        assert sidecar is not None
        assert sidecar.status == VerificationStatus.SKIPPED_DISABLED.name


class TestCoordinatorQueueCap:
    def test_queue_full_writes_skipped_queue_full_sidecar(
        self, store: ReplayStore
    ):
        store._settings = ReplaySettings(
            max_replays_per_save=50,
            verification_enabled=True,
            verification_queue_cap=2,
        )
        # Block the worker on a barrier so we can fill the queue.
        gate = threading.Event()
        runs: List[str] = []

        def slow_runner(record, **_kwargs):
            gate.wait(timeout=10.0)
            runs.append(record.replay_id)
            return record.outcome.to_battle_outcome()

        coord = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=object(),
            registry_provider=object(),
            settings=store._settings,
            replay_runner=slow_runner,
            ship_builder_factory=lambda *a, **k: None,
        )
        coord.start()
        try:
            # First record kicks the worker; it blocks on the gate.
            store.persist(_make_record("a"))
            # Wait for worker to actually pick it up.
            timeout = time.monotonic() + 2.0
            while time.monotonic() < timeout:
                if coord._is_worker_busy():
                    break
                time.sleep(0.01)
            # Fill the queue (cap=2 → two more enqueue OK, third overflows).
            store.persist(_make_record("b"))
            store.persist(_make_record("c"))
            store.persist(_make_record("d"))  # overflow

            # Release the gate so the worker drains.
            gate.set()
            assert coord.wait_for_idle(timeout=5.0)
        finally:
            gate.set()
            coord.shutdown(timeout=5.0)

        rd = store.save_root / "replays"  # type: ignore[union-attr]
        statuses = {
            rid: (
                read_verification_sidecar(rd, rid).status
                if read_verification_sidecar(rd, rid) is not None
                else None
            )
            for rid in ["a", "b", "c", "d"]
        }
        # 'd' should be skipped; the others should have passed.
        assert statuses["d"] == VerificationStatus.SKIPPED_QUEUE_FULL.name
        assert statuses["a"] == VerificationStatus.PASSED.name
        assert statuses["b"] == VerificationStatus.PASSED.name
        assert statuses["c"] == VerificationStatus.PASSED.name


class TestCoordinatorErrorIsolation:
    def test_runner_exception_writes_error_sidecar(self, store: ReplayStore):
        record = _make_record("err-1")
        coord = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=object(),
            registry_provider=object(),
            settings=store._settings,
            replay_runner=_raising_replay_runner,
            ship_builder_factory=lambda *a, **k: None,
        )
        coord.start()
        try:
            store.persist(record)
            assert coord.wait_for_idle(timeout=5.0)
        finally:
            coord.shutdown(timeout=5.0)

        rd = store.save_root / "replays"  # type: ignore[union-attr]
        sidecar = read_verification_sidecar(rd, "err-1")
        assert sidecar is not None
        assert sidecar.status == VerificationStatus.ERROR.name
        assert sidecar.error is not None
        assert sidecar.error["type"] == "RuntimeError"

    def test_runner_exception_does_not_block_subsequent_records(
        self, store: ReplayStore
    ):
        seen: List[str] = []

        def runner(record, **_kwargs):
            seen.append(record.replay_id)
            if record.replay_id == "boom":
                raise RuntimeError("kaboom")
            return record.outcome.to_battle_outcome()

        coord = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=object(),
            registry_provider=object(),
            settings=store._settings,
            replay_runner=runner,
            ship_builder_factory=lambda *a, **k: None,
        )
        coord.start()
        try:
            store.persist(_make_record("boom"))
            store.persist(_make_record("ok"))
            assert coord.wait_for_idle(timeout=5.0)
        finally:
            coord.shutdown(timeout=5.0)

        rd = store.save_root / "replays"  # type: ignore[union-attr]
        boom = read_verification_sidecar(rd, "boom")
        ok = read_verification_sidecar(rd, "ok")
        assert boom is not None and boom.status == VerificationStatus.ERROR.name
        assert ok is not None and ok.status == VerificationStatus.PASSED.name


class TestCoordinatorShutdown:
    def test_shutdown_joins_worker(self, store: ReplayStore):
        coord = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=object(),
            registry_provider=object(),
            settings=store._settings,
            replay_runner=_identity_replay_runner,
            ship_builder_factory=lambda *a, **k: None,
        )
        coord.start()
        store.persist(_make_record("s1"))
        coord.shutdown(timeout=5.0)
        # After shutdown, worker thread should not be alive.
        thread = coord._worker
        assert thread is None or not thread.is_alive()

    def test_shutdown_idempotent(self, store: ReplayStore):
        coord = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=object(),
            registry_provider=object(),
            settings=store._settings,
            replay_runner=_identity_replay_runner,
            ship_builder_factory=lambda *a, **k: None,
        )
        coord.start()
        coord.shutdown(timeout=5.0)
        # Second call must not raise.
        coord.shutdown(timeout=5.0)

    def test_post_shutdown_persist_does_not_enqueue(self, store: ReplayStore):
        seen: List[str] = []

        def runner(record, **_kwargs):
            seen.append(record.replay_id)
            return record.outcome.to_battle_outcome()

        coord = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=object(),
            registry_provider=object(),
            settings=store._settings,
            replay_runner=runner,
            ship_builder_factory=lambda *a, **k: None,
        )
        coord.start()
        coord.shutdown(timeout=5.0)
        store.persist(_make_record("after-shutdown"))
        # Listener should have been removed, so no run.
        time.sleep(0.1)  # tiny grace
        assert "after-shutdown" not in seen


class TestNoRecursion:
    def test_verification_does_not_create_new_replay_records(
        self, store: ReplayStore, tmp_path: Path
    ):
        # The runner stub is `_identity_replay_runner` which calls
        # `record.outcome.to_battle_outcome()` — purely a dict roundtrip,
        # NOT a real `run_battle` call. But the contract is:
        # `run_replay_headless` passes `capture_context=None` to
        # `run_battle`, which prevents capture. We assert that no NEW
        # replay records appear in the dir after verification of the
        # original.
        record = _make_record("orig-1")
        coord = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=object(),
            registry_provider=object(),
            settings=store._settings,
            replay_runner=_identity_replay_runner,
            ship_builder_factory=lambda *a, **k: None,
        )
        coord.start()
        try:
            store.persist(record)
            assert coord.wait_for_idle(timeout=5.0)
        finally:
            coord.shutdown(timeout=5.0)

        rd = store.save_root / "replays"  # type: ignore[union-attr]
        # Count true replay record files (not sidecars).
        replay_files = [
            p for p in rd.glob("replay_*.json")
            if not p.name.endswith(".verification.json")
        ]
        # Only the original record exists; no recursive captures.
        assert len(replay_files) == 1
        assert replay_files[0].name == "replay_orig-1.json"


class TestSerialExecution:
    def test_single_worker_serializes_records(self, store: ReplayStore):
        active = [0]
        max_concurrent = [0]
        lock = threading.Lock()
        completed: List[str] = []

        def runner(record, **_kwargs):
            with lock:
                active[0] += 1
                if active[0] > max_concurrent[0]:
                    max_concurrent[0] = active[0]
            time.sleep(0.05)
            with lock:
                active[0] -= 1
            completed.append(record.replay_id)
            return record.outcome.to_battle_outcome()

        coord = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=object(),
            registry_provider=object(),
            settings=store._settings,
            replay_runner=runner,
            ship_builder_factory=lambda *a, **k: None,
        )
        coord.start()
        try:
            for i in range(5):
                store.persist(_make_record(f"s{i}"))
            assert coord.wait_for_idle(timeout=10.0)
        finally:
            coord.shutdown(timeout=5.0)

        assert max_concurrent[0] == 1
        assert len(completed) == 5
