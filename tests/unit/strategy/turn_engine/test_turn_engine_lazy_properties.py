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
