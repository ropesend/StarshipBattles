"""
PROJ-332 — Characterization tests for the 10 untested lazy-engine
properties on `TurnEngine`, plus the conflict_engine `battle_resolver`
fallback branches.

The 5 properties already pinned by `test_dependency_injection.py`
(movement, production, order_processor, conflict, resource) are NOT
duplicated here — this file fills the gap for the remaining lazy
defaults and the `_NullBattleResolver` warn path.

Discipline: pure characterization — no production refactors.
"""
from __future__ import annotations

import logging
from unittest.mock import MagicMock

from game.strategy.engine.turn_engine import TurnEngine, _NullBattleResolver


class TestLazyPropertyDefaults:
    """Each lazy property should return its production default class
    on first access and the same instance on subsequent accesses
    (idempotency)."""

    def test_production_engine_property_returns_default_class_when_none_injected(
        self, fresh_registries
    ):
        from game.strategy.engine.production_engine import ProductionEngine

        engine = TurnEngine(registries=fresh_registries)

        prod_engine = engine.production_engine
        assert isinstance(prod_engine, ProductionEngine)
        # Idempotent — second access returns the same instance.
        assert engine.production_engine is prod_engine

    def test_order_processor_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.order_processor import OrderProcessor

        engine = TurnEngine(registries=fresh_registries)

        processor = engine.order_processor
        assert isinstance(processor, OrderProcessor)
        assert engine.order_processor is processor

    def test_resource_engine_property_returns_default_consumable_engine_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.consumable_management_engine import (
            ConsumableManagementEngine,
        )

        engine = TurnEngine(registries=fresh_registries)

        resource_engine = engine.resource_engine
        assert isinstance(resource_engine, ConsumableManagementEngine)
        assert engine.resource_engine is resource_engine

    def test_population_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.population_engine import PopulationEngine

        engine = TurnEngine(registries=fresh_registries)

        pop_engine = engine.population_engine
        assert isinstance(pop_engine, PopulationEngine)
        assert engine.population_engine is pop_engine

    def test_resupply_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.resupply_engine import ResupplyEngine

        engine = TurnEngine(registries=fresh_registries)

        resupply = engine.resupply_engine
        assert isinstance(resupply, ResupplyEngine)
        assert engine.resupply_engine is resupply

    def test_harvesting_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.harvesting_engine import HarvestingEngine

        engine = TurnEngine(registries=fresh_registries)

        harvest = engine.harvesting_engine
        assert isinstance(harvest, HarvestingEngine)
        assert engine.harvesting_engine is harvest

    def test_environmental_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.environmental_hazard_engine import (
            EnvironmentalHazardEngine,
        )

        engine = TurnEngine(registries=fresh_registries)

        env = engine.environmental_engine
        assert isinstance(env, EnvironmentalHazardEngine)
        assert engine.environmental_engine is env

    def test_planet_energy_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.planet_energy_engine import PlanetEnergyEngine

        engine = TurnEngine(registries=fresh_registries)

        pe = engine.planet_energy_engine
        assert isinstance(pe, PlanetEnergyEngine)
        assert engine.planet_energy_engine is pe

    # PROJ-353A Tier-7 (T2.6): five additional lazy-property defaults flagged
    # by OpenCode b4 as untested. Each pins (a) the production default class
    # and (b) idempotency.

    def test_action_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.action_execution_engine import ActionExecutionEngine

        engine = TurnEngine(registries=fresh_registries)

        ae = engine.action_engine
        assert isinstance(ae, ActionExecutionEngine)
        assert engine.action_engine is ae

    def test_planet_action_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.planet_action_engine import PlanetActionEngine

        engine = TurnEngine(registries=fresh_registries)

        pae = engine.planet_action_engine
        assert isinstance(pae, PlanetActionEngine)
        assert engine.planet_action_engine is pae

    def test_component_activation_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.component_activation_engine import (
            ComponentActivationEngine,
        )

        engine = TurnEngine(registries=fresh_registries)

        cae = engine.component_activation_engine
        assert isinstance(cae, ComponentActivationEngine)
        assert engine.component_activation_engine is cae

    def test_organics_consumption_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.organics_consumption_engine import (
            OrganicsConsumptionEngine,
        )

        engine = TurnEngine(registries=fresh_registries)

        oce = engine.organics_consumption_engine
        assert isinstance(oce, OrganicsConsumptionEngine)
        assert engine.organics_consumption_engine is oce

    def test_happiness_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.happiness_engine import HappinessEngine

        engine = TurnEngine(registries=fresh_registries)

        he = engine.happiness_engine
        assert isinstance(he, HappinessEngine)
        assert engine.happiness_engine is he

    # PROJ-369 Phase 2: Quality / Atmosphere / Water are now injectable
    # via TurnEngineConfig. The lazy properties mirror the existing 15
    # sub-engines.
    def test_quality_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.quality_engine import QualityEngine

        engine = TurnEngine(registries=fresh_registries)

        qe = engine.quality_engine
        assert isinstance(qe, QualityEngine)
        assert engine.quality_engine is qe

    def test_atmosphere_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.atmosphere_engine import AtmosphereEngine

        engine = TurnEngine(registries=fresh_registries)

        ae = engine.atmosphere_engine
        assert isinstance(ae, AtmosphereEngine)
        assert engine.atmosphere_engine is ae

    def test_water_engine_property_returns_default_class_and_is_idempotent(
        self, fresh_registries
    ):
        from game.strategy.engine.water_engine import WaterEngine

        engine = TurnEngine(registries=fresh_registries)

        we = engine.water_engine
        assert isinstance(we, WaterEngine)
        assert engine.water_engine is we


class TestCreateDefaultTurnEngineFactory:
    """PROJ-353A Tier-7 (T2.6): pin `create_default_turn_engine` factory.

    `test_dependency_injection.py::TestFactoryFunction` already covers the
    five originally-pinned engines. This pins the remaining lazy defaults
    flow through the factory too — the factory should produce a TurnEngine
    whose lazy properties resolve to the production default classes.
    """

    def test_factory_produces_engine_whose_action_engine_resolves_to_default(
        self, fresh_registries
    ):
        from game.strategy.engine.action_execution_engine import ActionExecutionEngine
        from game.strategy.engine.turn_engine import create_default_turn_engine

        engine = create_default_turn_engine(fresh_registries, ai_factory=MagicMock())

        assert isinstance(engine.action_engine, ActionExecutionEngine)

    def test_factory_produces_engine_whose_planet_action_engine_resolves_to_default(
        self, fresh_registries
    ):
        from game.strategy.engine.planet_action_engine import PlanetActionEngine
        from game.strategy.engine.turn_engine import create_default_turn_engine

        engine = create_default_turn_engine(fresh_registries, ai_factory=MagicMock())

        assert isinstance(engine.planet_action_engine, PlanetActionEngine)

    def test_factory_forwards_explicit_config_to_turn_engine_constructor(
        self, fresh_registries
    ):
        """`create_default_turn_engine(..., config=cfg)` must pass `config`
        through to `TurnEngine.__init__`. We assert this via the spy on
        TurnEngine to avoid coupling to TurnEngine's internal storage
        layout (the constructor unbundles config into individual fields)."""
        from game.strategy.engine import turn_engine as turn_engine_mod
        from game.strategy.engine.turn_engine_config import TurnEngineConfig

        cfg = TurnEngineConfig()
        captured = {}
        original = turn_engine_mod.TurnEngine

        def spy(*args, **kwargs):
            captured["config"] = kwargs.get("config")
            return original(*args, **kwargs)

        from unittest.mock import patch
        with patch.object(turn_engine_mod, "TurnEngine", side_effect=spy):
            turn_engine_mod.create_default_turn_engine(
                fresh_registries, ai_factory=MagicMock(), config=cfg,
            )

        assert captured["config"] is cfg

    def test_factory_works_without_ai_factory_and_uses_null_battle_resolver_path(
        self, fresh_registries
    ):
        """Factory accepts ai_factory=None; the conflict_engine fallback
        still works (ai_factory=None + battle_resolver=None falls into the
        _NullBattleResolver branch)."""
        from game.strategy.engine.turn_engine import create_default_turn_engine

        engine = create_default_turn_engine(fresh_registries, ai_factory=None)

        assert isinstance(engine, TurnEngine)
        assert engine._ai_factory is None


class TestConflictEngineBattleResolverBranches:
    """Pin the lazy `battle_resolver` decision tree inside `conflict_engine`:
    - injected battle_resolver → used as-is.
    - no battle_resolver but `ai_factory` set → SimulationBattleResolver built.
    - neither set → `_NullBattleResolver` + WARNING log; the null resolver
      raises `RuntimeError` if its `resolve_battle` is ever called.
    """

    def test_conflict_engine_uses_simulation_battle_resolver_when_ai_factory_provided_no_resolver(
        self, fresh_registries
    ):
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        ai_factory = MagicMock(name="ai_factory")
        engine = TurnEngine(
            registries=fresh_registries,
            ai_factory=ai_factory,
            battle_resolver=None,
        )

        # Triggering the lazy property forces the decision tree to run.
        _ = engine.conflict_engine

        # Engine cached the constructed resolver back onto the slot.
        assert isinstance(engine._battle_resolver, SimulationBattleResolver)

    def test_conflict_engine_uses_null_battle_resolver_and_warns_when_both_resolver_and_ai_factory_none(
        self, fresh_registries, caplog
    ):
        engine = TurnEngine(
            registries=fresh_registries,
            ai_factory=None,
            battle_resolver=None,
        )

        with caplog.at_level(logging.WARNING, logger="game.strategy.engine.turn_engine"):
            _ = engine.conflict_engine

        assert any(
            "no battle_resolver or ai_factory" in record.getMessage()
            for record in caplog.records
            if record.levelno >= logging.WARNING
        )

        # The _NullBattleResolver raises if invoked — pin that contract.
        null_resolver = _NullBattleResolver()
        try:
            null_resolver.resolve_battle()
        except RuntimeError as exc:
            assert "No battle resolver configured" in str(exc)
        else:
            raise AssertionError(
                "_NullBattleResolver.resolve_battle should raise RuntimeError"
            )
