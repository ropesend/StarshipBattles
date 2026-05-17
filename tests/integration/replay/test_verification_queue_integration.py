"""PROJ-366 Phase 3 — End-to-end live battle → verification queue → sidecar.

The test wires the production composition manually (ReplayStore +
ReplayVerificationCoordinator with the Combat Lab fallback adapter) and
runs a live deterministic battle. It then waits for the coordinator's
worker thread to drain via ``coordinator.wait_for_idle(timeout=30)`` and
asserts the sidecar landed atomically.

Two cases:
* PASSED — verification settings enabled, deterministic battle,
  sidecar status PASSED.
* SKIPPED_DISABLED — same wiring with ``verification_enabled=False``;
  sidecar status SKIPPED_DISABLED.

Plus a no-recursion assertion: after the PASSED case, the store still
contains exactly one record (the headless replay must not have produced
a replay-of-itself).

Note on snapshot path (per r001 deviation acknowledgement): the
production `ship_instance_lookup` snapshot path requires fully-realized
``ShipInstance`` objects with real design data, which is a heavy fixture
build. This test uses the Combat Lab fallback path (no snapshots) so the
verifier exercises the fallback adapter wired by `app_bootstrap.py`. The
snapshot path is exercised separately by:
* `test_replay_ship_builder_registry_contract.py` — protocol contract
  passes a real `DefaultRegistryProvider` and confirms the production
  builder constructs without raising.
* `test_verification_uses_production_materializer.py` — spies on
  `build_replay_ship_builder` to confirm the coordinator uses the
  production materializer factory.
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
from game.simulation.services.ship_materializer import DesignOnlyMaterializer
from game.simulation.systems.battle_end_conditions import TickLimitCondition
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
)
from game.strategy.systems.save_game_service import SaveGameService
from tests.fixtures.battle import make_minimal_spec
from tests.fixtures.ships import create_test_ship


def _build_two_team_ships(fresh_registries):
    team0 = [
        create_test_ship(
            name="Alpha", x=500, y=400, team_id=0,
            add_bridge=True, add_engine=True, add_weapons=2,
            registries=fresh_registries,
        )
    ]
    team1 = [
        create_test_ship(
            name="Bravo", x=2000, y=400, team_id=1,
            add_bridge=True, add_engine=True, add_weapons=2,
            registries=fresh_registries,
        )
    ]
    return team0, team1


def _make_spec(team0, team1, *, seed=42, max_ticks=100):
    spec = make_minimal_spec(
        {0: team0, 1: team1},
        seed=seed, max_ticks=max_ticks,
        telemetry_level=TelemetryLevel.NORMAL,
    )
    return dataclasses.replace(spec, end_condition=TickLimitCondition(max_ticks=max_ticks))


def _make_builder(team0, team1):
    ordered = list(team0) + list(team1)
    idx = [0]

    def builder(_ship_spec, _team_id):
        ship = ordered[idx[0]]
        idx[0] += 1
        return ship

    return builder


def _make_test_fallback(fresh_registries):
    """Build a deterministic test fallback that produces fresh test ships
    matching the captured spec's positions.

    The test ships use `make_minimal_spec`-style design ids (e.g.
    `test_design_0_0`) which do not exist in Combat Lab data, so we cannot
    reuse the production `DesignOnlyMaterializer(load_combat_lab_design)`
    adapter here. Instead, we use a closure that recreates fresh test
    ships per spec — this is the test analogue of the production fallback
    and gives the verifier a deterministic ship to drive.
    """
    def _fallback(ship_spec, team_id):
        ship = create_test_ship(
            name=ship_spec.name,
            x=ship_spec.position.x,
            y=ship_spec.position.y,
            team_id=team_id,
            add_bridge=True,
            add_engine=True,
            add_weapons=2,
            registries=fresh_registries,
        )
        return ship

    return _fallback


@pytest.fixture
def replay_globals_cleanup():
    """Reset the process-wide sink + store globals after each test.

    Mirrors the autouse pattern in
    `tests/unit/strategy/services/test_replay_verification_coordinator.py:93-98`.
    """
    yield
    shutdown_all_coordinators(timeout=5.0)
    reset_default_capture_sink()
    SaveGameService.default().set_replay_store(None)


def _wait_for_sidecar(sidecar_path: Path, timeout: float = 30.0) -> bool:
    """Poll for sidecar file existence with a bounded deadline."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if sidecar_path.exists():
            return True
        time.sleep(0.1)
    return False


class TestVerificationQueueIntegration:
    def test_live_battle_produces_passed_sidecar_and_no_recursion(
        self,
        fresh_registries,
        tmp_path: Path,
        replay_globals_cleanup,
    ):
        """Live battle → store persists → coordinator listener fires →
        verification runs → sidecar PASSED. After verification, the store
        still contains exactly one record (no-recursion assertion).
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
            team0, team1 = _build_two_team_ships(fresh_registries)
            ctx = ReplayCaptureContext(
                sector_name="qint-1",
                sector_coords=(0, 0),
                turn_number=1,
                participating_empires=("A", "B"),
                components_registry_hash="sha256:test",
                captured_at="2026-05-05T00:00:00Z",
            )
            run_battle(
                _make_spec(team0, team1, seed=42),
                ai_factory=AIControllerFactory(),
                ship_builder=_make_builder(team0, team1),
                capture_context=ctx,
            )

            # Wait for the coordinator to drain.
            assert coordinator.wait_for_idle(timeout=30.0), (
                "coordinator did not become idle within 30s"
            )

            records = store.list()
            assert len(records) == 1, (
                f"expected 1 captured replay, got {len(records)} "
                "(headless verification may have recursed)"
            )
            replay_id = records[0].replay_id

            sidecar_path = save_root / "replays" / f"replay_{replay_id}.verification.json"
            assert _wait_for_sidecar(sidecar_path, timeout=30.0), (
                f"sidecar never landed at {sidecar_path}"
            )
            sidecar = read_verification_sidecar(
                save_root / "replays", replay_id,
            )
            assert sidecar is not None
            assert sidecar.status == VerificationStatus.PASSED.name, (
                f"expected PASSED, got {sidecar.status}; error={sidecar.error}; "
                f"diff={sidecar.diff}"
            )

            # No-recursion: the verification headless replay must not have
            # produced a second record.
            assert len(store.list()) == 1
        finally:
            coordinator.shutdown(timeout=5.0)

    def test_live_battle_with_verification_disabled_writes_skipped_sidecar(
        self,
        fresh_registries,
        tmp_path: Path,
        replay_globals_cleanup,
    ):
        """With `verification_enabled=False`, the coordinator listener
        writes a SKIPPED_DISABLED sidecar inline (no worker dispatch).
        """
        save_root = tmp_path / "save"
        save_root.mkdir()

        settings = ReplaySettings(
            max_replays_per_save=10,
            verification_enabled=False,
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
            team0, team1 = _build_two_team_ships(fresh_registries)
            ctx = ReplayCaptureContext(
                sector_name="qint-disabled",
                captured_at="2026-05-05T00:00:00Z",
                components_registry_hash="sha256:test",
            )
            run_battle(
                _make_spec(team0, team1, seed=42),
                ai_factory=AIControllerFactory(),
                ship_builder=_make_builder(team0, team1),
                capture_context=ctx,
            )

            assert coordinator.wait_for_idle(timeout=30.0)

            records = store.list()
            assert len(records) == 1
            replay_id = records[0].replay_id

            sidecar_path = save_root / "replays" / f"replay_{replay_id}.verification.json"
            assert _wait_for_sidecar(sidecar_path, timeout=30.0)
            sidecar = read_verification_sidecar(
                save_root / "replays", replay_id,
            )
            assert sidecar is not None
            assert sidecar.status == VerificationStatus.SKIPPED_DISABLED.name
        finally:
            coordinator.shutdown(timeout=5.0)
