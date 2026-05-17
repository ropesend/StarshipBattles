"""PROJ-366 Phase 4 — Combat Lab fallback verification path.

A Combat Lab synthetic record has every ship's `instance_snapshot` as
None (no strategy ShipInstance is attached). The production fallback
adapter (`DesignOnlyMaterializer(load_combat_lab_design)` wrapped in a
closure that captures the bootstrap-time `registries`) is what allows
the coordinator to verify these records.

Two cases:
* PASS — coordinator wired with a fallback adapter (test analogue of
  the production Combat Lab adapter using `create_test_ship`) →
  sidecar PASSED.
* ERROR — coordinator wired with `fallback_ship_builder=None` →
  `replay_ship_builder` raises `ValueError("...no instance snapshot
  ... and no fallback_builder supplied")`; the coordinator's worker
  catches the exception and writes an ERROR sidecar with the
  diagnostic message.

Note: the test uses synthetic test fixtures rather than the actual
Combat Lab data path (which requires a registry-clear-and-reload cycle
via `combat_lab.runner.TestRunner.load_data_for_scenario`). The
production Combat Lab adapter shape is exercised in the real flow at
`game/app_bootstrap.py`'s `_replay_combat_lab_fallback` closure; this
test pins the fallback-routing contract specifically.
"""
from __future__ import annotations

import dataclasses
import time
from pathlib import Path

import pytest

from game.ai.ai_factory import AIControllerFactory
from game.core.registry import get_default_registry_provider
from game.simulation.battle_runner import run_battle
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.replay import (
    ReplayCaptureContext,
    reset_default_capture_sink,
    set_default_capture_sink,
)
from game.simulation.systems.battle_end_conditions import TickLimitCondition
from game.strategy.services.replay_store import ReplaySettings, ReplayStore
from game.strategy.services.replay_verification_coordinator import (
    ReplayVerificationCoordinator,
    shutdown_all_coordinators,
)
from game.strategy.services.replay_verification_sidecar import (
    VerificationStatus,
    read_verification_sidecar,
)
from game.strategy.systems.save_game_service import SaveGameService
from tests.fixtures.battle import make_minimal_spec
from tests.fixtures.ships import create_test_ship


def _wait_for_sidecar(sidecar_path: Path, timeout: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if sidecar_path.exists():
            return True
        time.sleep(0.1)
    return False


def _build_no_snapshot_record(fresh_registries):
    """Capture a battle to disk where the `ReplayCaptureContext` has no
    `ship_instance_lookup` — every ship's `instance_snapshot` will be
    None in the persisted record. This is the exact shape Combat Lab
    captures produce in production.
    """
    team0 = [
        create_test_ship(
            name="CLA", x=500, y=400, team_id=0,
            add_bridge=True, add_engine=True, add_weapons=2,
            registries=fresh_registries,
        )
    ]
    team1 = [
        create_test_ship(
            name="CLB", x=2000, y=400, team_id=1,
            add_bridge=True, add_engine=True, add_weapons=2,
            registries=fresh_registries,
        )
    ]
    spec = make_minimal_spec(
        {0: team0, 1: team1}, seed=42, max_ticks=40,
        telemetry_level=TelemetryLevel.NORMAL,
    )
    spec = dataclasses.replace(spec, end_condition=TickLimitCondition(max_ticks=40))

    ordered = list(team0) + list(team1)
    idx = [0]

    def builder(_ship_spec, _team_id):
        ship = ordered[idx[0]]
        idx[0] += 1
        return ship

    ctx = ReplayCaptureContext(
        sector_name="combat-lab",
        captured_at="2026-05-05T00:00:00Z",
        components_registry_hash="sha256:cl",
        # ship_instance_lookup left None → captured snapshots are all None.
    )
    run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=builder,
        capture_context=ctx,
    )


def _make_test_fallback(fresh_registries):
    """Test analogue of the production Combat Lab fallback adapter
    (`DesignOnlyMaterializer(load_combat_lab_design)` wrapped). Returns
    fresh test ships matching the captured spec's ship names + positions
    so verification produces a deterministic outcome.
    """
    def _fallback(ship_spec, team_id):
        return create_test_ship(
            name=ship_spec.name,
            x=ship_spec.position.x,
            y=ship_spec.position.y,
            team_id=team_id,
            add_bridge=True,
            add_engine=True,
            add_weapons=2,
            registries=fresh_registries,
        )
    return _fallback


@pytest.fixture
def replay_globals_cleanup():
    yield
    shutdown_all_coordinators(timeout=5.0)
    reset_default_capture_sink()
    SaveGameService.default().set_replay_store(None)


class TestCombatLabFallbackVerification:
    def test_no_snapshot_record_passes_when_fallback_wired(
        self,
        fresh_registries,
        tmp_path: Path,
        replay_globals_cleanup,
    ):
        """Record with `instance_snapshot=None` per ship + fallback adapter
        wired → sidecar PASSED.
        """
        save_root = tmp_path / "save"
        save_root.mkdir()

        settings = ReplaySettings(
            max_replays_per_save=10,
            verification_enabled=True,
            verification_queue_cap=4,
        )
        store = ReplayStore(settings=settings)
        store.set_save_root(save_root)
        set_default_capture_sink(store)
        SaveGameService.default().set_replay_store(store)

        provider = get_default_registry_provider()
        coordinator = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=AIControllerFactory(),
            registry_provider=provider,
            settings=settings,
            fallback_ship_builder=_make_test_fallback(fresh_registries),
        )
        coordinator.start()

        try:
            _build_no_snapshot_record(fresh_registries)
            assert coordinator.wait_for_idle(timeout=30.0)

            records = store.list()
            assert len(records) == 1
            replay_id = records[0].replay_id
            sidecar_path = save_root / "replays" / f"replay_{replay_id}.verification.json"
            assert _wait_for_sidecar(sidecar_path, timeout=30.0)
            sidecar = read_verification_sidecar(save_root / "replays", replay_id)
            assert sidecar is not None
            assert sidecar.status == VerificationStatus.PASSED.name, (
                f"expected PASSED with fallback wired; "
                f"got {sidecar.status} (error={sidecar.error}, diff={sidecar.diff})"
            )
        finally:
            coordinator.shutdown(timeout=5.0)

    def test_no_snapshot_record_errors_without_fallback(
        self,
        fresh_registries,
        tmp_path: Path,
        replay_globals_cleanup,
    ):
        """Record with `instance_snapshot=None` per ship + NO fallback
        wired → `replay_ship_builder` raises `ValueError` → coordinator
        catches the exception and writes an ERROR sidecar.
        """
        save_root = tmp_path / "save"
        save_root.mkdir()

        settings = ReplaySettings(
            max_replays_per_save=10,
            verification_enabled=True,
            verification_queue_cap=4,
        )
        store = ReplayStore(settings=settings)
        store.set_save_root(save_root)
        set_default_capture_sink(store)
        SaveGameService.default().set_replay_store(store)

        provider = get_default_registry_provider()
        coordinator = ReplayVerificationCoordinator(
            replay_store=store,
            ai_factory=AIControllerFactory(),
            registry_provider=provider,
            settings=settings,
            fallback_ship_builder=None,  # No fallback — verification must error.
        )
        coordinator.start()

        try:
            _build_no_snapshot_record(fresh_registries)
            assert coordinator.wait_for_idle(timeout=30.0)

            records = store.list()
            assert len(records) == 1
            replay_id = records[0].replay_id
            sidecar_path = save_root / "replays" / f"replay_{replay_id}.verification.json"
            assert _wait_for_sidecar(sidecar_path, timeout=30.0)
            sidecar = read_verification_sidecar(save_root / "replays", replay_id)
            assert sidecar is not None
            assert sidecar.status == VerificationStatus.ERROR.name, (
                f"expected ERROR with no fallback; got {sidecar.status}"
            )
            assert sidecar.error is not None
            # Diagnostic message from `replay_ship_builder._builder`'s
            # `ValueError("replay ship_builder: no instance snapshot for ... "
            # "and no fallback_builder supplied")`.
            msg = sidecar.error.get("message", "")
            assert "no instance snapshot" in msg or "fallback_builder" in msg, (
                f"unexpected error message: {sidecar.error}"
            )
        finally:
            coordinator.shutdown(timeout=5.0)
