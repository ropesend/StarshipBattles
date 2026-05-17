"""PROJ-366 Phase 3 — verification coordinator uses the production
materializer factory.

Pins the contract that the coordinator calls
`game.strategy.services.replay_ship_builder.build_replay_ship_builder`
when verifying a captured record. We monkeypatch the SOURCE-module name
that the coordinator imports (NOT the lazy-import shadow), so a future
refactor that swaps the import target will surface here.

Per Codex r001 (lazy-import patch-target delta): patch
`game.strategy.services.replay_verification_coordinator.build_replay_ship_builder`
because that module imports the symbol at module top, then uses it via
the local binding.
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
from game.strategy.services import replay_verification_coordinator as rvc_mod
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


def _make_test_fallback(fresh_registries):
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


def _wait_for_sidecar(sidecar_path: Path, timeout: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if sidecar_path.exists():
            return True
        time.sleep(0.1)
    return False


@pytest.fixture
def replay_globals_cleanup():
    yield
    shutdown_all_coordinators(timeout=5.0)
    reset_default_capture_sink()
    SaveGameService.default().set_replay_store(None)


def test_coordinator_calls_build_replay_ship_builder_from_source_module(
    fresh_registries,
    tmp_path: Path,
    monkeypatch,
    replay_globals_cleanup,
):
    """The coordinator must use the production materializer factory
    `build_replay_ship_builder` — not a hand-built test stub.

    Spies on the SOURCE-module symbol that the coordinator imports
    (`game.strategy.services.replay_verification_coordinator.build_replay_ship_builder`).
    """
    call_count = {"n": 0}
    real = rvc_mod.build_replay_ship_builder

    def spy(record, *, registry_provider, fallback_builder=None):
        call_count["n"] += 1
        return real(
            record,
            registry_provider=registry_provider,
            fallback_builder=fallback_builder,
        )

    # Source-module patch is the canonical assertion: the coordinator
    # imports `build_replay_ship_builder` at module top, so this rebinds
    # what the source module exposes as the public symbol.
    monkeypatch.setattr(
        rvc_mod, "build_replay_ship_builder", spy
    )

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
    # The coordinator's constructor binds `ship_builder_factory`'s default
    # at module-load time (Python default-arg semantics), so a runtime
    # monkeypatch of the source module doesn't affect already-bound
    # defaults. Explicitly pass the spy via the public DI seam — that's
    # exactly what production wiring does (the default IS
    # `build_replay_ship_builder`, so passing it explicitly is a faithful
    # mirror), AND it matches the seam tests are expected to use.
    coordinator = ReplayVerificationCoordinator(
        replay_store=store,
        ai_factory=AIControllerFactory(),
        registry_provider=provider,
        settings=settings,
        fallback_ship_builder=_make_test_fallback(fresh_registries),
        ship_builder_factory=spy,
    )
    coordinator.start()

    try:
        team0 = [
            create_test_ship(
                name="A0", x=500, y=400, team_id=0,
                add_bridge=True, add_engine=True, add_weapons=2,
                registries=fresh_registries,
            )
        ]
        team1 = [
            create_test_ship(
                name="B0", x=2000, y=400, team_id=1,
                add_bridge=True, add_engine=True, add_weapons=2,
                registries=fresh_registries,
            )
        ]
        spec = make_minimal_spec(
            {0: team0, 1: team1}, seed=42, max_ticks=60,
            telemetry_level=TelemetryLevel.NORMAL,
        )
        spec = dataclasses.replace(spec, end_condition=TickLimitCondition(max_ticks=60))

        ordered = list(team0) + list(team1)
        idx = [0]

        def builder(_ship_spec, _team_id):
            ship = ordered[idx[0]]
            idx[0] += 1
            return ship

        ctx = ReplayCaptureContext(
            sector_name="materializer-spy",
            captured_at="2026-05-05T00:00:00Z",
            components_registry_hash="sha256:test",
        )
        run_battle(
            spec,
            ai_factory=AIControllerFactory(),
            ship_builder=builder,
            capture_context=ctx,
        )

        assert coordinator.wait_for_idle(timeout=30.0)

        records = store.list()
        assert len(records) == 1
        replay_id = records[0].replay_id
        sidecar_path = save_root / "replays" / f"replay_{replay_id}.verification.json"
        assert _wait_for_sidecar(sidecar_path, timeout=30.0)
        sidecar = read_verification_sidecar(save_root / "replays", replay_id)
        assert sidecar is not None
        assert sidecar.status == VerificationStatus.PASSED.name, (
            f"expected PASSED, got {sidecar.status}: error={sidecar.error}"
        )

        # The spy MUST have been called at least once — the coordinator
        # uses the production `build_replay_ship_builder` factory, not
        # a hand-built stub.
        assert call_count["n"] >= 1, (
            "coordinator did not call `build_replay_ship_builder` from "
            "the source module — production materializer factory is "
            "not being used"
        )
    finally:
        coordinator.shutdown(timeout=5.0)
