"""PROJ-306: DI contract tests for `run_battle` and `BattleController.start_from_spec`.

This module pins the post-PROJ-306 contract:

1. The private `_default_ship_builder_from_context()` helper has been
   DELETED. Importing it raises `ImportError`.
2. A new public helper `build_context_ship_builder(registry_provider)`
   exists in its place. It REQUIRES a `registry_provider` argument —
   no global lookup.
3. `run_battle(spec, ai_factory=...)` with neither `ship_builder` nor
   `registry_provider` raises `RuntimeError` with explicit guidance.
   No global lookup is performed from inside `game/simulation/`.
4. `run_battle(spec, ai_factory=..., registry_provider=p)` works — pulls
   the materializer from `ApplicationContext` and assembles
   `GameRegistries` from the explicit provider.
5. `BattleController.start_from_spec` mirrors the same contract.

Per `docs/02_PATTERNS.md` §3 ("Simulation Code Must NOT Use Global
Lookup", PROJ-252), `get_default_registry_provider()` must never be
called from inside `game/simulation/`. This test file is the regression
guard for that rule on the two surviving fallback sites that PROJ-306
eliminates.
"""
from __future__ import annotations

import pytest

from game.ai.ai_factory import AIControllerFactory
from game.simulation.battle_outcome import BattleOutcome
from game.simulation.battle_runner import run_battle
from game.simulation.battle_spec import BattleSpec, ShipSpec
from game.simulation.combat.modifier_stack import ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.entities.ship import Ship
from game.simulation.systems.battle_end_conditions import TickLimitCondition

# Helpers shared with test_battle_runner.py via conftest.
# (Consolidated in PROJ-322 Task 1.5 / HLP-002.)
from tests.unit.simulation.conftest import _make_ship_spec, _make_team


def _minimal_spec() -> BattleSpec:
    return BattleSpec(
        seed=7,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=2),
        absolute_max_ticks=10,
        teams=(
            _make_team(0, (_make_ship_spec("s0", 0.0, 0.0),)),
            _make_team(1, (_make_ship_spec("s1", 500.0, 0.0),)),
        ),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )


@pytest.fixture
def ship_builder(fresh_registries):
    """Minimal ship builder — same shape as test_battle_runner.py's fixture."""

    def _build(ship_spec: ShipSpec, team_id: int) -> Ship:
        ship = Ship(
            name=ship_spec.name,
            x=ship_spec.position.x,
            y=ship_spec.position.y,
            color=(200, 100, 50),
            team_id=team_id,
            ship_class="Escort",
            theme_id=ship_spec.theme_id,
            registries=fresh_registries,
        )
        ship.instance_id = ship_spec.instance_id
        return ship

    return _build


# ---------------------------------------------------------------------------
# Contract tests
# ---------------------------------------------------------------------------


class TestPrivateFallbackIsGone:
    """The private `_default_ship_builder_from_context` is DELETED."""

    def test_private_fallback_cannot_be_imported(self):
        """`from game.simulation.battle_runner import
        _default_ship_builder_from_context` must raise ImportError."""
        with pytest.raises(ImportError):
            from game.simulation.battle_runner import (  # noqa: F401
                _default_ship_builder_from_context,
            )


class TestPublicHelperContract:
    """`build_context_ship_builder(registry_provider)` is the public
    successor. It REQUIRES the provider argument — no internal global
    lookup."""

    def test_public_helper_exists_and_requires_provider(self):
        from game.simulation.battle_runner import build_context_ship_builder

        # Cannot be called without a registry_provider — raises TypeError.
        with pytest.raises(TypeError):
            build_context_ship_builder()  # type: ignore[call-arg]

    def test_public_helper_returns_callable(self, fresh_registries):
        from game.core.registry import get_default_registry_provider
        from game.simulation.battle_runner import build_context_ship_builder

        provider = get_default_registry_provider()
        builder = build_context_ship_builder(registry_provider=provider)
        assert callable(builder)

    def test_returned_builder_calls_materializer_with_ship_spec_team_id_and_registries(
        self, fresh_registries,
    ):
        """PROJ-353A Tier-7 (T2.11): rewrite of the PROJ-321-deleted
        `test_start_battle_ship_builder_calls_to_ship_with_position_and_team_id`.

        The original deleted test did a source-text scan
        (`assert "to_ship(registries=registries)" not in app.py`) — a
        fragile, trivially-bypassed pin. PROJ-321 deleted it; per Stream 2
        the task should have been REWRITE not DELETE. Behavioral coverage
        in `test_battle_runner.py::test_materialize_spec_ships_passes_team_id_to_builder`
        and `test_ship_materializer.py::test_instance_backed_calls_to_ship_with_position_and_team_id`
        partly fills the gap, but the production `_ship_builder` closure
        (now `build_context_ship_builder`) was not directly pinned. This
        test closes that gap.

        It asserts the closure produced by `build_context_ship_builder`
        forwards `(ship_spec, team_id, registries)` to the registered
        materializer — the failure mode the deleted test was guarding
        against (`to_ship(registries=registries)` missing position +
        team_id) is now caught by a behavioral assertion on the closure
        rather than by a string scan.
        """
        from unittest.mock import MagicMock

        from game.core.registry import get_default_registry_provider
        from game.simulation.battle_runner import build_context_ship_builder
        from game.simulation.services import ship_materializer as mat_mod

        # Capture invocations on a stub materializer so we can assert
        # what the closure forwarded.
        captured: list = []
        fake_ship = MagicMock(name="fake_ship")

        class _StubMaterializer:
            def materialize(self, ship_spec, team_id, registries):
                captured.append((ship_spec, team_id, registries))
                return fake_ship

        original_get = mat_mod.get_default_ship_materializer
        mat_mod.get_default_ship_materializer = lambda: _StubMaterializer()
        try:
            provider = get_default_registry_provider()
            builder = build_context_ship_builder(registry_provider=provider)

            ship_spec = _make_ship_spec("recovered", 1.0, 2.0)
            result = builder(ship_spec, 7)
        finally:
            mat_mod.get_default_ship_materializer = original_get

        assert result is fake_ship
        assert len(captured) == 1
        forwarded_spec, forwarded_team_id, forwarded_registries = captured[0]
        assert forwarded_spec is ship_spec
        assert forwarded_team_id == 7
        # The registries bundle was assembled from the explicit provider
        # — not pulled via a global lookup inside simulation.
        assert forwarded_registries is not None
        # Sanity: the bundle has the catalog field PROJ-306 added.
        assert hasattr(forwarded_registries, "resource_catalog")


class TestRunBattleRequiresProviderWhenNoBuilder:
    """`run_battle(spec, ai_factory=...)` with neither `ship_builder` nor
    `registry_provider` MUST raise `RuntimeError`. No silent global lookup."""

    def test_raises_when_neither_builder_nor_provider(self):
        # PROJ-466 (Phase 4 Task 4.2): the missing-dependency error is now
        # ValidationException(MISSING_DEPENDENCY) — assert the exact type and
        # code so a regression to a generic builtin (RuntimeError/TypeError)
        # fails loudly.
        from game.core.error_codes import ErrorCode
        from game.core.exceptions import ValidationException

        spec = _minimal_spec()
        with pytest.raises(ValidationException) as ei:
            run_battle(
                spec,
                ai_factory=AIControllerFactory(),
                # No ship_builder.
                # No registry_provider.
            )
        assert ei.value.code == ErrorCode.MISSING_DEPENDENCY.value

    def test_works_when_registry_provider_is_passed(self, ship_builder):
        """Smoke: providing a registry_provider lets run_battle succeed
        without a ship_builder. The context materializer is invoked with
        the explicit provider's GameRegistries bundle."""
        from game.core.registry import get_default_registry_provider
        from game.simulation.services import ship_materializer as mat_mod

        # Spy materializer adapts the test ship_builder fixture.
        invocations = []

        class SpyMaterializer:
            def materialize(self, ship_spec, team_id, registries):
                invocations.append(ship_spec.instance_id)
                return ship_builder(ship_spec, team_id)

        original = mat_mod._default_ship_materializer
        try:
            mat_mod._default_ship_materializer = SpyMaterializer()
            spec = _minimal_spec()
            outcome = run_battle(
                spec,
                ai_factory=AIControllerFactory(),
                registry_provider=get_default_registry_provider(),
            )
        finally:
            mat_mod._default_ship_materializer = original

        assert isinstance(outcome, BattleOutcome)
        assert set(invocations) == {"s0", "s1"}

    def test_explicit_ship_builder_still_takes_priority(self, ship_builder):
        """When `ship_builder` is explicit, registry_provider is unused."""
        spec = _minimal_spec()
        outcome = run_battle(
            spec,
            ai_factory=AIControllerFactory(),
            ship_builder=ship_builder,
            # No registry_provider — but should not be needed.
        )
        assert isinstance(outcome, BattleOutcome)


class TestSimulationLayerHasNoGlobalLookup:
    """Static guard: `get_default_registry_provider` is NOT called from
    `game/simulation/` after PROJ-306. This is the regression check —
    if a future change re-introduces the global lookup, this test fires.

    Implementation note: rather than runtime-monkeypatching, we walk the
    Simulation source tree and fail if any line references the symbol.
    Comments and docstrings are allowed.
    """

    def test_no_simulation_call_to_get_default_registry_provider(self):
        import ast
        from pathlib import Path

        sim_root = Path(__file__).parents[3] / "game" / "simulation"
        assert sim_root.is_dir(), f"Expected {sim_root} to exist"

        # AST-based scan — definitively catches imports + call expressions
        # while ignoring docstrings, comments, and string literals.
        offending: list = []
        symbol = "get_default_registry_provider"

        for py in sim_root.rglob("*.py"):
            try:
                tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                # Catch `from game.core.registry import get_default_registry_provider`
                if isinstance(node, ast.ImportFrom):
                    if node.module and "game.core.registry" in node.module:
                        for alias in node.names:
                            if alias.name == symbol:
                                offending.append(
                                    f"{py}:{node.lineno}: import {symbol}"
                                )
                # Catch `get_default_registry_provider(...)` calls
                elif isinstance(node, ast.Call):
                    func = node.func
                    name = None
                    if isinstance(func, ast.Name):
                        name = func.id
                    elif isinstance(func, ast.Attribute):
                        name = func.attr
                    if name == symbol:
                        offending.append(
                            f"{py}:{node.lineno}: call {symbol}(...)"
                        )

        assert not offending, (
            "Simulation-layer global lookup of get_default_registry_provider:\n"
            + "\n".join(offending)
        )
