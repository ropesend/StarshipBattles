"""
Tests for sub-engine per-tick input validation.

PROJ-251 Phase 6: Validates that engines raise ValidationException
with clear messages when preconditions are violated.

PROJ-480 Task 1.10: 12+ near-identical engine validation classes
consolidated into parametrized cases. Each engine declares an
``engine_factory`` (callable taking fresh_registries) and a
``mutate`` function applied to a baseline empire/fleet to produce
the raise-case. The failure modes are preserved per-engine via
distinct parametrize ids and distinct mutate callables — collapsing
to a single "any field None raises" would lose semantic coverage.
"""
from typing import Callable
from unittest.mock import MagicMock

import pytest

from game.core.exceptions import ValidationException


# ---------------------------------------------------------------------------
# Empire / fleet fixtures (shared with the engine matrix below)
# ---------------------------------------------------------------------------

def _empire(fleets=None, colonies=None):
    e = MagicMock()
    e.id = 0
    e.fleets = fleets or []
    e.colonies = colonies or []
    e.resource_pool = {}
    return e


def _fleet(location=None, ships=None, orders=None):
    f = MagicMock()
    f.id = "fleet-1"
    f.location = location if location is not None else MagicMock()
    f.ships = ships if ships is not None else []
    f.orders = orders if orders is not None else []
    return f


# ---------------------------------------------------------------------------
# Per-engine factories — each returns an engine *and* a callable that
# performs the validation on the supplied empires (because OrderProcessor
# validates via a handler, not directly).
# ---------------------------------------------------------------------------

def _factory_harvesting(fresh_registries):
    from game.strategy.engine.harvesting_engine import HarvestingEngine
    e = HarvestingEngine(registries=fresh_registries)
    return e, e._validate_tick_inputs


def _factory_consumable(fresh_registries):
    from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine
    e = ConsumableManagementEngine(registries=fresh_registries)
    return e, e._validate_tick_inputs


def _factory_resupply(fresh_registries):
    from game.strategy.engine.resupply_engine import ResupplyEngine
    e = ResupplyEngine(registries=fresh_registries)
    return e, e._validate_tick_inputs


def _factory_planet_energy(fresh_registries):
    from game.strategy.engine.planet_energy_engine import PlanetEnergyEngine
    e = PlanetEnergyEngine(registries=fresh_registries)
    return e, e._validate_tick_inputs


def _factory_production(fresh_registries):
    from game.strategy.engine.production_engine import ProductionEngine
    e = ProductionEngine(registries=fresh_registries)
    return e, e._validate_tick_inputs


def _factory_env_hazard(fresh_registries):
    from game.strategy.engine.environmental_hazard_engine import EnvironmentalHazardEngine
    e = EnvironmentalHazardEngine()
    return e, e._validate_tick_inputs


def _factory_order_processor(fresh_registries):
    # PROJ-368 Phase 4: _validate_tick_inputs lives on JoinFleetHandler.
    from game.strategy.data.order_types import OrderType
    from game.strategy.engine.order_processor import OrderProcessor
    e = OrderProcessor()
    handler = e._handler_registry.get(OrderType.JOIN_FLEET)
    return e, handler._validate_tick_inputs


def _factory_action_execution(fresh_registries):
    from game.strategy.engine.action_execution_engine import ActionExecutionEngine
    e = ActionExecutionEngine(order_processor=MagicMock())
    return e, e._validate_tick_inputs


def _factory_planet_action(fresh_registries):
    from game.strategy.engine.planet_action_engine import PlanetActionEngine
    e = PlanetActionEngine()
    return e, e._validate_tick_inputs


def _factory_component_activation(fresh_registries):
    from game.strategy.engine.component_activation_engine import ComponentActivationEngine
    e = ComponentActivationEngine()
    return e, e._validate_tick_inputs


def _factory_fleet_movement(fresh_registries):
    from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
    e = FleetMovementEngine()
    return e, e._validate_tick_inputs


def _factory_conflict_resolution(fresh_registries):
    from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
    e = ConflictResolutionEngine(battle_resolver=MagicMock(), registries=fresh_registries)
    return e, e._validate_tick_inputs


def _factory_population(fresh_registries):
    from game.strategy.engine.population_engine import PopulationEngine
    e = PopulationEngine()
    return e, e._validate_tick_inputs


def _factory_quality(fresh_registries):
    from game.strategy.engine.quality_engine import QualityEngine
    e = QualityEngine()
    return e, e._validate_tick_inputs


def _factory_atmosphere(fresh_registries):
    from game.strategy.engine.atmosphere_engine import AtmosphereEngine
    e = AtmosphereEngine()
    return e, e._validate_tick_inputs


# ---------------------------------------------------------------------------
# Valid-empires baseline: each engine receives the empire shape that
# exercises its validation path (some need a fleet; OrderProcessor needs
# a fleet on the empire for the JoinFleetHandler validator).
# ---------------------------------------------------------------------------

def _baseline_fleetless():
    return [_empire()]


def _baseline_with_fleet():
    return [_empire(fleets=[_fleet()])]


# ---------------------------------------------------------------------------
# Raise-case mutators: distinct per failure mode. Each returns the empires
# list to pass to the validator.
# ---------------------------------------------------------------------------

def _mutate_colony_none():
    return [_empire(colonies=[None])]


def _mutate_fleet_none_location():
    fleet = _fleet()
    fleet.location = None
    return [_empire(fleets=[fleet])]


def _mutate_fleet_none_ships():
    fleet = _fleet()
    fleet.ships = None
    return [_empire(fleets=[fleet])]


def _mutate_fleet_none_orders():
    fleet = _fleet()
    fleet.orders = None
    return [_empire(fleets=[fleet])]


def _mutate_resource_pool_none():
    emp = _empire()
    emp.resource_pool = None
    return [emp]


# ---------------------------------------------------------------------------
# Matrix: (engine_id, factory, baseline_builder, raise_case_builder)
# Each row preserves a distinct (engine x failure-mode) pairing from the
# original 14 hand-rolled classes.
# ---------------------------------------------------------------------------

ENGINE_CASES: list[tuple[str, Callable, Callable, Callable]] = [
    ("HarvestingEngine_colony_none",
        _factory_harvesting, _baseline_fleetless, _mutate_colony_none),
    ("ConsumableManagementEngine_fleet_none_ships",
        _factory_consumable, _baseline_with_fleet, _mutate_fleet_none_ships),
    ("ResupplyEngine_colony_none",
        _factory_resupply, _baseline_fleetless, _mutate_colony_none),
    ("PlanetEnergyEngine_colony_none",
        _factory_planet_energy, _baseline_fleetless, _mutate_colony_none),
    ("ProductionEngine_resource_pool_none",
        _factory_production, _baseline_fleetless, _mutate_resource_pool_none),
    ("EnvironmentalHazardEngine_fleet_none_location",
        _factory_env_hazard, _baseline_fleetless, _mutate_fleet_none_location),
    ("OrderProcessor_fleet_none_orders",
        _factory_order_processor, _baseline_with_fleet, _mutate_fleet_none_orders),
    ("ActionExecutionEngine_fleet_none_location",
        _factory_action_execution, _baseline_fleetless, _mutate_fleet_none_location),
    ("PlanetActionEngine_colony_none",
        _factory_planet_action, _baseline_fleetless, _mutate_colony_none),
    ("ComponentActivationEngine_colony_none",
        _factory_component_activation, _baseline_fleetless, _mutate_colony_none),
    ("FleetMovementEngine_fleet_none_location",
        _factory_fleet_movement, _baseline_fleetless, _mutate_fleet_none_location),
    ("ConflictResolutionEngine_fleet_none_location",
        _factory_conflict_resolution, _baseline_fleetless, _mutate_fleet_none_location),
    ("PopulationEngine_colony_none",
        _factory_population, _baseline_fleetless, _mutate_colony_none),
    ("QualityEngine_colony_none",
        _factory_quality, _baseline_fleetless, _mutate_colony_none),
    ("AtmosphereEngine_colony_none",
        _factory_atmosphere, _baseline_fleetless, _mutate_colony_none),
]


@pytest.mark.parametrize(
    "engine_id, factory, baseline, raise_case",
    ENGINE_CASES,
    ids=[row[0] for row in ENGINE_CASES],
)
class TestEngineValidationMatrix:
    """Per-engine validation parametrize matrix.

    Each parametrize id pins one engine-class + one failure mode so the
    distinct contracts that the original 14 classes documented remain
    individually addressable on failure.
    """

    def test_valid_empires_pass(self, fresh_registries, engine_id, factory, baseline, raise_case):
        _engine, validate = factory(fresh_registries)
        validate(baseline())

    def test_invalid_input_raises(self, fresh_registries, engine_id, factory, baseline, raise_case):
        _engine, validate = factory(fresh_registries)
        with pytest.raises(ValidationException):
            validate(raise_case())
