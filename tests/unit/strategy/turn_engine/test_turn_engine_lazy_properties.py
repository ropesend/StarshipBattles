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

from unittest.mock import MagicMock

from tests.fixtures.turn_engine import build_test_turn_engine


class TestEagerDefaultEngines:
    """Each sub-engine property should expose the production default
    class when the engine is built via the canonical
    ``TurnEngineConfig.create_default(...)`` path.

    PROJ-369 Phase 3: eager construction replaces lazy fallback init.
    Idempotency is trivial (passthrough) so we still verify the
    property returns the same instance across accesses.
    """

    def test_movement_engine_default(self, fresh_registries):
        from game.strategy.engine.fleet_movement_engine import FleetMovementEngine

        engine = build_test_turn_engine(fresh_registries)
        assert isinstance(engine.movement_engine, FleetMovementEngine)
        assert engine.movement_engine is engine.movement_engine

    def test_production_engine_default(self, fresh_registries):
        from game.strategy.engine.production_engine import ProductionEngine

        engine = build_test_turn_engine(fresh_registries)
        prod = engine.production_engine
        assert isinstance(prod, ProductionEngine)
        assert engine.production_engine is prod

    def test_order_processor_default(self, fresh_registries):
        from game.strategy.engine.order_processor import OrderProcessor

        engine = build_test_turn_engine(fresh_registries)
        op = engine.order_processor
        assert isinstance(op, OrderProcessor)
        assert engine.order_processor is op

    def test_resource_engine_default(self, fresh_registries):
        from game.strategy.engine.consumable_management_engine import (
            ConsumableManagementEngine,
        )

        engine = build_test_turn_engine(fresh_registries)
        re = engine.resource_engine
        assert isinstance(re, ConsumableManagementEngine)
        assert engine.resource_engine is re

    def test_population_engine_default(self, fresh_registries):
        from game.strategy.engine.population_engine import PopulationEngine

        engine = build_test_turn_engine(fresh_registries)
        pe = engine.population_engine
        assert isinstance(pe, PopulationEngine)
        assert engine.population_engine is pe

    def test_resupply_engine_default(self, fresh_registries):
        from game.strategy.engine.resupply_engine import ResupplyEngine

        engine = build_test_turn_engine(fresh_registries)
        rse = engine.resupply_engine
        assert isinstance(rse, ResupplyEngine)
        assert engine.resupply_engine is rse

    def test_harvesting_engine_default(self, fresh_registries):
        from game.strategy.engine.harvesting_engine import HarvestingEngine

        engine = build_test_turn_engine(fresh_registries)
        he = engine.harvesting_engine
        assert isinstance(he, HarvestingEngine)
        assert engine.harvesting_engine is he

    def test_environmental_engine_default(self, fresh_registries):
        from game.strategy.engine.environmental_hazard_engine import (
            EnvironmentalHazardEngine,
        )

        engine = build_test_turn_engine(fresh_registries)
        ee = engine.environmental_engine
        assert isinstance(ee, EnvironmentalHazardEngine)
        assert engine.environmental_engine is ee

    def test_planet_energy_engine_default(self, fresh_registries):
        from game.strategy.engine.planet_energy_engine import PlanetEnergyEngine

        engine = build_test_turn_engine(fresh_registries)
        pee = engine.planet_energy_engine
        assert isinstance(pee, PlanetEnergyEngine)
        assert engine.planet_energy_engine is pee

    def test_action_engine_default(self, fresh_registries):
        from game.strategy.engine.action_execution_engine import (
            ActionExecutionEngine,
        )

        engine = build_test_turn_engine(fresh_registries)
        ae = engine.action_engine
        assert isinstance(ae, ActionExecutionEngine)
        assert engine.action_engine is ae

    def test_planet_action_engine_default(self, fresh_registries):
        from game.strategy.engine.planet_action_engine import PlanetActionEngine

        engine = build_test_turn_engine(fresh_registries)
        pae = engine.planet_action_engine
        assert isinstance(pae, PlanetActionEngine)
        assert engine.planet_action_engine is pae

    def test_component_activation_engine_default(self, fresh_registries):
        from game.strategy.engine.component_activation_engine import (
            ComponentActivationEngine,
        )

        engine = build_test_turn_engine(fresh_registries)
        cae = engine.component_activation_engine
        assert isinstance(cae, ComponentActivationEngine)
        assert engine.component_activation_engine is cae

    def test_organics_consumption_engine_default(self, fresh_registries):
        from game.strategy.engine.organics_consumption_engine import (
            OrganicsConsumptionEngine,
        )

        engine = build_test_turn_engine(fresh_registries)
        oce = engine.organics_consumption_engine
        assert isinstance(oce, OrganicsConsumptionEngine)
        assert engine.organics_consumption_engine is oce

    def test_happiness_engine_default(self, fresh_registries):
        from game.strategy.engine.happiness_engine import HappinessEngine

        engine = build_test_turn_engine(fresh_registries)
        he = engine.happiness_engine
        assert isinstance(he, HappinessEngine)
        assert engine.happiness_engine is he

    def test_quality_engine_default(self, fresh_registries):
        from game.strategy.engine.quality_engine import QualityEngine

        engine = build_test_turn_engine(fresh_registries)
        qe = engine.quality_engine
        assert isinstance(qe, QualityEngine)
        assert engine.quality_engine is qe

    def test_atmosphere_engine_default(self, fresh_registries):
        from game.strategy.engine.atmosphere_engine import AtmosphereEngine

        engine = build_test_turn_engine(fresh_registries)
        ae = engine.atmosphere_engine
        assert isinstance(ae, AtmosphereEngine)
        assert engine.atmosphere_engine is ae

    def test_water_engine_default(self, fresh_registries):
        from game.strategy.engine.water_engine import WaterEngine

        engine = build_test_turn_engine(fresh_registries)
        we = engine.water_engine
        assert isinstance(we, WaterEngine)
        assert engine.water_engine is we


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

    def test_conflict_engine_resolver_guard_present_at_dispatch_site(
        self, fresh_registries
    ):
        """PROJ-369 Phase 3: ``_NullBattleResolver`` deleted. The
        absent-resolver case is now guarded at the dispatch site
        inside ``ConflictResolutionEngine._resolve_combat_at_hex``
        (just before ``self._battle_resolver.resolve_battle(...)``).

        Non-combat ticks (no actual battle) do not raise — only the
        attempt to dispatch a battle does. We verify the guard is
        present by inspecting the engine source for the explicit
        ``ValueError`` and the ``battle_resolver`` reference.
        """
        import inspect
        from game.strategy.engine import conflict_resolution_engine

        src = inspect.getsource(
            conflict_resolution_engine.ConflictResolutionEngine._resolve_combat_at_hex
        )
        assert "self._battle_resolver is None" in src, (
            "PROJ-369 Phase 3 guard missing from _resolve_combat_at_hex: "
            "expected an explicit `self._battle_resolver is None` check "
            "before the resolver call site."
        )
        assert "ValueError" in src
        assert "battle_resolver" in src

        # Production wiring sanity: with ai_factory=None, the engine's
        # bound resolver is None.
        engine = build_test_turn_engine(
            fresh_registries, ai_factory=None,
        )
        assert engine.conflict_engine._battle_resolver is None


class TestPlanetModifierEffectEngineLazyProperty:
    """PROJ-428 Phase 1: planet-modifier engine lives on TurnEngine.

    The registry module must not import PlanetModifierEffectEngine; the
    construction site moves to a lazy property on TurnEngine, accessed
    through a resolver lambda on the descriptor.
    """

    def test_registry_module_does_not_import_planet_modifier_effect_engine(self):
        """AST guard: turn_phase_registry must not import the engine."""
        import ast
        from pathlib import Path

        from game.strategy.engine import turn_phase_registry as _reg

        src = Path(_reg.__file__).read_text(encoding="utf-8")
        tree = ast.parse(src)
        offenders: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if "planet_modifier_effect_engine" in module:
                    offenders.append(f"from {module} import ...")
                for alias in node.names:
                    if alias.name == "PlanetModifierEffectEngine":
                        offenders.append(f"from {module} import {alias.name}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if "planet_modifier_effect_engine" in alias.name:
                        offenders.append(f"import {alias.name}")
        assert not offenders, (
            f"turn_phase_registry must not import PlanetModifierEffectEngine "
            f"(found: {offenders}). PROJ-428 Phase 1 moves construction to "
            f"TurnEngine.planet_modifier_effect_engine."
        )

    def test_planet_modifier_effect_engine_property_returns_cached_instance(
        self, fresh_registries
    ):
        """The lazy property must construct once and cache."""
        from game.strategy.engine.planet_modifier_effect_engine import (
            PlanetModifierEffectEngine,
        )

        engine = build_test_turn_engine(fresh_registries)
        first = engine.planet_modifier_effect_engine
        second = engine.planet_modifier_effect_engine
        assert isinstance(first, PlanetModifierEffectEngine)
        assert first is second


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
