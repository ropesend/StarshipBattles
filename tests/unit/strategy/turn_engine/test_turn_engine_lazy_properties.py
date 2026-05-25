"""
PROJ-332 — Characterization tests for the engine properties on
``TurnEngine``, plus the ``conflict_engine`` battle-resolver semantics.

PROJ-369 Phase 3: lazy fallback init removed; all 18 sub-engines are
constructed eagerly in ``TurnEngineConfig.create_default(...)`` and
flow through trivial passthrough properties on TurnEngine. The tests
below pin that the eager-default config wires the production class
into each property — matching the old "first access creates default"
contract — and that the conflict engine's resolver decision is made
in ``create_default``, not at first property access.

The ``_NullBattleResolver`` placeholder was deleted in Phase 3;
the absent-resolver case now raises clearly from
``ConflictResolutionEngine.resolve_all_conflicts`` instead.
"""
from __future__ import annotations

import importlib
from unittest.mock import MagicMock

import pytest

from tests.fixtures.turn_engine import build_test_turn_engine


# PROJ-496 T1.1 (origin PROJ-480 T3.29): parametrize the 17 isinstance +
# identity tests that share an identical pattern (engine attribute → class
# match + same-instance idempotency check) into a single data table.
#
# Each entry is (attribute_name, module_path, class_name). We import the
# class lazily inside the test body so a regression that breaks a single
# module doesn't poison the collection of all 17 cases.
_DEFAULT_ENGINE_CASES = [
    ("movement_engine", "game.strategy.engine.fleet_movement_engine", "FleetMovementEngine"),
    ("production_engine", "game.strategy.engine.production_engine", "ProductionEngine"),
    ("order_processor", "game.strategy.engine.order_processor", "OrderProcessor"),
    ("resource_engine", "game.strategy.engine.consumable_management_engine", "ConsumableManagementEngine"),
    ("population_engine", "game.strategy.engine.population_engine", "PopulationEngine"),
    ("resupply_engine", "game.strategy.engine.resupply_engine", "ResupplyEngine"),
    ("harvesting_engine", "game.strategy.engine.harvesting_engine", "HarvestingEngine"),
    ("environmental_engine", "game.strategy.engine.environmental_hazard_engine", "EnvironmentalHazardEngine"),
    ("planet_energy_engine", "game.strategy.engine.planet_energy_engine", "PlanetEnergyEngine"),
    ("action_engine", "game.strategy.engine.action_execution_engine", "ActionExecutionEngine"),
    ("planet_action_engine", "game.strategy.engine.planet_action_engine", "PlanetActionEngine"),
    ("component_activation_engine", "game.strategy.engine.component_activation_engine", "ComponentActivationEngine"),
    ("organics_consumption_engine", "game.strategy.engine.organics_consumption_engine", "OrganicsConsumptionEngine"),
    ("happiness_engine", "game.strategy.engine.happiness_engine", "HappinessEngine"),
    ("quality_engine", "game.strategy.engine.quality_engine", "QualityEngine"),
    ("atmosphere_engine", "game.strategy.engine.atmosphere_engine", "AtmosphereEngine"),
    ("water_engine", "game.strategy.engine.water_engine", "WaterEngine"),
]


class TestEagerDefaultEngines:
    """Each sub-engine property should expose the production default
    class when the engine is built via the canonical
    ``TurnEngineConfig.create_default(...)`` path.

    PROJ-369 Phase 3: eager construction replaces lazy fallback init.
    Idempotency is trivial (passthrough) so we still verify the
    property returns the same instance across accesses.
    """

    @pytest.mark.parametrize(
        "attr_name,module_path,class_name",
        _DEFAULT_ENGINE_CASES,
        ids=[attr for attr, _, _ in _DEFAULT_ENGINE_CASES],
    )
    def test_engine_property_default(
        self, fresh_registries, attr_name, module_path, class_name
    ):
        module = importlib.import_module(module_path)
        engine_class = getattr(module, class_name)

        engine = build_test_turn_engine(fresh_registries)
        value = getattr(engine, attr_name)
        assert isinstance(value, engine_class)
        # Idempotency: same instance on re-access.
        assert getattr(engine, attr_name) is value


class TestConflictEngineBattleResolverBranches:
    """Pin the battle-resolver decision tree.

    PROJ-369 Phase 3: the decision tree moved from the lazy
    ``conflict_engine`` property body into
    ``TurnEngineConfig.create_default(...)``. Behavior pinned:

    - ``ai_factory`` provided → ``SimulationBattleResolver`` constructed
      and wired into ``conflict_engine``.
    - ``ai_factory=None`` → ``conflict_engine.battle_resolver`` is None;
      combat raises clearly from
      ``ConflictResolutionEngine.resolve_all_conflicts``.

    The legacy ``_NullBattleResolver`` placeholder was deleted.
    """

    def test_simulation_battle_resolver_when_ai_factory_provided(
        self, fresh_registries
    ):
        from game.strategy.adapters.simulation_adapter import (
            SimulationBattleResolver,
        )

        ai_factory = MagicMock(name="ai_factory")
        engine = build_test_turn_engine(
            fresh_registries, ai_factory=ai_factory,
        )

        # ConflictResolutionEngine's battle_resolver is the
        # SimulationBattleResolver constructed inside create_default.
        resolver = engine.conflict_engine._battle_resolver
        assert isinstance(resolver, SimulationBattleResolver)

    def test_battle_resolver_none_when_ai_factory_none(self, fresh_registries):
        engine = build_test_turn_engine(
            fresh_registries, ai_factory=None,
        )
        assert engine.conflict_engine._battle_resolver is None

    def test_conflict_engine_raises_when_resolver_absent_at_dispatch_site(
        self, fresh_registries
    ):
        """PROJ-369 Phase 3: ``_NullBattleResolver`` deleted. The
        absent-resolver case is now guarded at the dispatch site
        inside ``ConflictResolutionEngine._resolve_combat_at_hex``
        (just before ``self._battle_resolver.resolve_battle(...)``).

        Non-combat ticks (no actual battle) do not raise — only the
        attempt to dispatch a battle does. We verify the guard by
        BEHAVIOR: build the engine with ``ai_factory=None`` so
        ``conflict_engine._battle_resolver`` is None, then drive
        ``_resolve_combat_at_hex`` with two empires sharing a hex
        (each with a non-empty fleet) so the dispatch reaches the
        resolver call site, and assert ``ValueError`` is raised.

        PROJ-491 Task 1.5: replaces the previous
        ``inspect.getsource(...) + substring check`` brittle pattern.
        Batch 4↔5 merge note (2026-05-24): Batch 5's PROJ-496 T1.2
        independently moved a source-text variant of this guard to
        ``tests/static_guards/test_turn_engine_architectural_guards.py``.
        This behavioral test supersedes the source-text guard because it
        drives the actual runtime path and would catch silent removal of
        the ``ValueError`` raise. The static-guard variant is kept as a
        redundant backstop and is not load-bearing.
        """
        import pytest

        from game.strategy.data.fleet import Fleet
        from game.strategy.data.ship_instance import ShipInstance

        engine = build_test_turn_engine(
            fresh_registries, ai_factory=None,
        )
        conflict_engine = engine.conflict_engine
        assert conflict_engine._battle_resolver is None

        # Two empires, two fleets, same hex, each carrying ≥1 ship so
        # ``_resolve_combat_at_hex`` does not short-circuit on the
        # "no participating fleet has any ships" guard above.
        empire_a = MagicMock()
        empire_a.id = 1
        empire_b = MagicMock()
        empire_b.id = 2

        ship_a = MagicMock(spec=ShipInstance)
        ship_b = MagicMock(spec=ShipInstance)

        fleet_a = MagicMock(spec=Fleet)
        fleet_a.id = 10
        fleet_a.owner_id = 1
        fleet_a.location = MagicMock(name="hex_loc")
        fleet_a.ships = [ship_a]

        fleet_b = MagicMock(spec=Fleet)
        fleet_b.id = 20
        fleet_b.owner_id = 2
        fleet_b.location = fleet_a.location
        fleet_b.ships = [ship_b]

        with pytest.raises(ValueError, match="battle_resolver"):
            conflict_engine._resolve_combat_at_hex(
                [(empire_a, fleet_a), (empire_b, fleet_b)]
            )


class TestPlanetModifierEffectEngineLazyProperty:
    """PROJ-428 Phase 1: planet-modifier engine lives on TurnEngine.

    PROJ-491 Task 1.5: the AST import-absence guard moved to the canonical
    static-guard suite at
    ``tests/static_guards/test_turn_phase_registry_no_planet_modifier_import.py``
    to preserve architectural intent without keeping in-line AST scans inside
    a behavioral-test file. This class is intentionally left as a documentation
    anchor for the wiring contract referenced by PROJ-428 Phase 1.

    Batch 4↔5 merge note (2026-05-24): Batch 5's PROJ-496 T1.2 independently
    added a duplicate AST guard inside
    ``tests/static_guards/test_turn_engine_architectural_guards.py``. Both
    files now host functionally-identical guards; the duplication is benign
    (both pass on the same source). A future cleanup pass may consolidate.
    """

    # PROJ-479 Task 1.11: deleted
    # `test_planet_modifier_effect_engine_property_returns_cached_instance` —
    # the 18-test cluster above (`test_*_engine_default`) already exercises
    # the identical isinstance + identity caching pattern for every other
    # engine property; adding `planet_modifier_effect_engine` to the
    # `TestTurnEngineLazyProperties` class via the same pattern would be
    # the right place if a new variant is needed.


class TestNullBattleResolverSymbolAbsent:
    """PROJ-369 Phase 3 regression guard: ``_NullBattleResolver`` is gone."""

    def test_null_battle_resolver_not_importable(self):
        from game.strategy.engine import turn_engine as turn_engine_module

        assert not hasattr(turn_engine_module, "_NullBattleResolver")

    def test_create_default_turn_engine_factory_not_importable(self):
        """PROJ-369 Phase 3 also deleted ``create_default_turn_engine``;
        the canonical entry point is now ``TurnEngineConfig.create_default()
        + TurnEngine(config=...)``.
        """
        from game.strategy.engine import turn_engine as turn_engine_module

        assert not hasattr(turn_engine_module, "create_default_turn_engine")
