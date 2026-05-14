"""
Tests for EmpireEconomyCalculator.

PROJ-99 Phase 1: Verifies production aggregation, maintenance calculation,
and economic snapshot generation.
PROJ-191 Phase 3: Updated mocks to use spec= for type safety.
FEAT-06: Added construction expense tests, updated mocks with construction_queue.
"""

import pytest
from unittest.mock import Mock

from game.strategy.engine.empire_economy_calculator import (
    EmpireEconomyCalculator,
    EmpireEconomySnapshot,
)
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance
PLANET_RESOURCE_NAMES = ["metals", "organics", "vapors", "radioactives", "exotics"]


def _mock_colony(**kwargs):
    """Create a mock colony with construction_queue defaulting to empty."""
    colony = Mock(spec=Planet)
    colony.construction_queue = kwargs.pop('construction_queue', [])
    colony.facilities = kwargs.pop('facilities', [])
    colony.deposits = kwargs.pop('resources', {})
    # FEAT-17: explicit default — Mock(spec=Planet) auto-creates a truthy
    # Mock for every attr, so we must pin this to False.
    colony.construction_queue_paused = kwargs.pop('construction_queue_paused', False)
    for k, v in kwargs.items():
        setattr(colony, k, v)
    return colony


def _mock_facility(**kwargs):
    """Create a mock facility with construction_queue defaulting to empty."""
    facility = Mock(spec=PlanetaryFacility)
    facility.construction_queue = kwargs.pop('construction_queue', [])
    facility.construction_queue_paused = kwargs.pop('construction_queue_paused', False)
    for k, v in kwargs.items():
        setattr(facility, k, v)
    return facility


def _mock_fleet(**kwargs):
    """Create a mock fleet with construction_queue defaulting to empty."""
    fleet = Mock(spec=Fleet)
    fleet.construction_queue = kwargs.pop('construction_queue', [])
    fleet.construction_queue_paused = kwargs.pop('construction_queue_paused', False)
    for k, v in kwargs.items():
        setattr(fleet, k, v)
    return fleet


@pytest.fixture
def _mock_race_registry():
    """Stub race registry used by upkeep / harvest tests.

    `.get_race(*) -> None` so the projector's harvest + yard paths
    (which consult habitability via `race_registry.get_race`)
    short-circuit cleanly to 1.0. Upkeep projection does NOT consult
    `race_registry` at all — this fixture exists only because the
    projector constructor requires one.
    """
    stub = Mock()
    stub.get_race.return_value = None
    return stub


class TestEmpireEconomySnapshot:
    """Tests for EmpireEconomySnapshot dataclass."""

    def test_empty_snapshot_defaults_to_empty_dicts(self):
        """Snapshot can be instantiated with no args and all fields default to empty dict."""
        snapshot = EmpireEconomySnapshot()

        assert snapshot.colony_production == {}
        assert snapshot.ship_production == {}
        assert snapshot.trade_production == {}
        assert snapshot.tribute_production == {}
        assert snapshot.mining_production == {}
        assert snapshot.total_production == {}
        assert snapshot.tribute_expenses == {}
        assert snapshot.construction_expenses_ships == {}
        assert snapshot.construction_expenses_complexes == {}
        assert snapshot.total_expenses == {}
        assert snapshot.net_resources == {}
        assert snapshot.current_storage == {}
        assert snapshot.max_storage == {}
        assert snapshot.total_population_upkeep == {}


class TestEmpireEconomyCalculator:
    """Tests for EmpireEconomyCalculator."""

    def test_empty_empire_returns_zeros(self, minimal_registries):
        """Empty empire (no colonies, no fleets) returns 0.0 for each resource."""
        empire = Mock(spec=Empire)
        empire.colonies = []
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        for res in PLANET_RESOURCE_NAMES:
            assert snapshot.colony_production.get(res, 0.0) == 0.0
            assert snapshot.total_production.get(res, 0.0) == 0.0
            assert snapshot.total_expenses.get(res, 0.0) == 0.0
            assert snapshot.net_resources[res] == 0.0

    def test_single_colony_with_resource_harvester(self, minimal_registries):
        """Single colony with one facility having ResourceHarvester returns correct production."""
        facility = _mock_facility(
            is_operational=True,
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'metals_harvester',
                            'abilities': {
                                'ResourceHarvester': {
                                    'resource_type': 'metals',
                                    'base_harvest_rate': 10.0
                                }
                            },
                            'resource_cost': {}
                        }
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[facility],
                              resources={'metals': {'quality': 0.8, 'quantity': 1000}})

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Production = base_rate * quality = 10.0 * 0.8 = 8.0
        assert snapshot.colony_production['metals'] == 8.0
        assert snapshot.total_production['metals'] == 8.0

    def test_net_resources_equals_production_minus_expenses(self, minimal_registries):
        """net_resources = total_production - total_expenses."""
        facility = _mock_facility(
            is_operational=True,
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'harvester',
                            'abilities': {
                                'ResourceHarvester': {
                                    'resource_type': 'metals',
                                    'base_harvest_rate': 10.0
                                }
                            },
                            'resource_cost': {}
                        }
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[facility],
                              resources={'metals': {'quality': 1.0, 'quantity': 1000}})

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Production = 10.0 * 1.0 = 10.0
        # No maintenance expenses
        # Net = 10.0 - 0.0 = 10.0
        assert snapshot.total_production['metals'] == 10.0
        assert snapshot.total_expenses['metals'] == 0.0
        assert snapshot.net_resources['metals'] == 10.0

    def test_current_storage_and_max_storage_copied_from_empire(self, minimal_registries):
        """current_storage and max_storage are copied from empire."""
        empire = Mock(spec=Empire)
        empire.colonies = []
        empire.fleets = []
        empire.resource_pool = {'metals': 500.0, 'organics': 300.0}
        empire.max_storage = {'metals': 1000.0, 'organics': 1000.0}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        assert snapshot.current_storage == {'metals': 500.0, 'organics': 300.0}
        assert snapshot.max_storage == {'metals': 1000.0, 'organics': 1000.0}

    def test_non_operational_facility_is_skipped(self, minimal_registries):
        """Non-operational facilities contribute no production."""
        facility = _mock_facility(
            is_operational=False,
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'expensive_harvester',
                            'abilities': {
                                'ResourceHarvester': {
                                    'resource_type': 'metals',
                                    'base_harvest_rate': 100.0
                                }
                            },
                            'resource_cost': {'metals': 1000.0}
                        }
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[facility],
                              resources={'metals': {'quality': 1.0, 'quantity': 5000}})

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Production should be zero
        assert snapshot.colony_production['metals'] == 0.0

    def test_multiple_colonies_and_fleets_aggregate(self, minimal_registries):
        """Multiple colonies and fleets aggregate correctly."""
        # Colony 1: Metals production
        facility1 = _mock_facility(
            is_operational=True,
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'harvester1',
                            'abilities': {
                                'ResourceHarvester': {
                                    'resource_type': 'metals',
                                    'base_harvest_rate': 5.0
                                }
                            },
                            'resource_cost': {'metals': 20.0}
                        }
                    ]
                }
            },
        )
        colony1 = _mock_colony(facilities=[facility1],
                               resources={'metals': {'quality': 1.0, 'quantity': 1000}})

        # Colony 2: Organics production
        facility2 = _mock_facility(
            is_operational=True,
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'harvester2',
                            'abilities': {
                                'ResourceHarvester': {
                                    'resource_type': 'organics',
                                    'base_harvest_rate': 8.0
                                }
                            },
                            'resource_cost': {'organics': 40.0}
                        }
                    ]
                }
            },
        )
        colony2 = _mock_colony(facilities=[facility2],
                               resources={'organics': {'quality': 0.5, 'quantity': 1000}})

        # Fleet with ship
        ship = Mock(spec=ShipInstance)
        ship.design_data = {
            'layers': {
                'HULL': [{'id': 'hull', 'resource_cost': {'vapors': 100.0}}]
            }
        }
        fleet = _mock_fleet(ships=[ship])

        empire = Mock(spec=Empire)
        empire.colonies = [colony1, colony2]
        empire.fleets = [fleet]
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Productions
        assert snapshot.colony_production['metals'] == 5.0  # 5.0 * 1.0
        assert snapshot.colony_production['organics'] == 4.0  # 8.0 * 0.5

    def test_missing_resource_quality_defaults_to_zero(self, minimal_registries):
        """If colony lacks a resource entry, quality defaults to 0.0 (no production)."""
        facility = _mock_facility(
            is_operational=True,
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'harvester',
                            'abilities': {
                                'ResourceHarvester': {
                                    'resource_type': 'exotics',
                                    'base_harvest_rate': 50.0
                                }
                            },
                            'resource_cost': {}
                        }
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[facility])

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # No production because no quality
        assert snapshot.colony_production['exotics'] == 0.0

    def test_placeholder_sources_are_zero(self, minimal_registries):
        """Placeholder production sources (ship, trade, tribute, mining) are zero."""
        empire = Mock(spec=Empire)
        empire.colonies = []
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        for res in PLANET_RESOURCE_NAMES:
            assert snapshot.ship_production[res] == 0.0
            assert snapshot.trade_production[res] == 0.0
            assert snapshot.tribute_production[res] == 0.0
            assert snapshot.mining_production[res] == 0.0
            assert snapshot.tribute_expenses[res] == 0.0
            assert snapshot.construction_expenses_ships[res] == 0.0
            assert snapshot.construction_expenses_complexes[res] == 0.0

    def test_registry_fallback_for_colony_production(self):
        """Components without inline abilities resolve via registry lookup (BUG-87).

        Real facility designs store components as {"id": "metal_harvester", "modifiers": [...]}
        without inline abilities. The calculator must fall back to registry lookup.
        """
        facility = _mock_facility(
            is_operational=True,
            design_data={
                'layers': {
                    'OUTER': [
                        {
                            'id': 'metal_harvester',
                            'modifiers': [{'id': 'simple_size_mount', 'value': 1.0}]
                        }
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[facility],
                              resources={'metals': {'quality': 0.8, 'quantity': 5000}})

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        # Mock registry with component definition
        registries = Mock()
        comp_def = Mock()
        comp_def.abilities = {
            'ResourceHarvester': {
                'resource_type': 'metals',
                'base_harvest_rate': 100.0
            }
        }
        registries.components.get.return_value = comp_def

        calculator = EmpireEconomyCalculator(registries=registries)
        snapshot = calculator.calculate(empire)

        # Production = 100.0 * 0.8 = 80.0
        assert snapshot.colony_production['metals'] == 80.0
        assert snapshot.total_production['metals'] == 80.0

    def test_registry_lookup_not_found_returns_zero(self, minimal_registries):
        """Components not found in registry produce nothing (BUG-87)."""
        facility = _mock_facility(
            is_operational=True,
            design_data={
                'layers': {
                    'OUTER': [
                        {'id': 'metal_harvester', 'modifiers': []}
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[facility],
                              resources={'metals': {'quality': 0.8, 'quantity': 5000}})

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        # Empty registries - component lookup will fail, should gracefully return 0
        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        assert snapshot.colony_production['metals'] == 0.0


class TestConstructionExpenses:
    """Tests for construction expense aggregation (FEAT-06)."""

    def test_empty_queues_return_zero(self, minimal_registries):
        """Colonies and fleets with empty queues produce zero expenses."""
        colony = _mock_colony(facilities=[])

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        for res in PLANET_RESOURCE_NAMES:
            assert snapshot.construction_expenses_ships[res] == 0.0
            assert snapshot.construction_expenses_complexes[res] == 0.0

    def test_planet_base_queue_complex_expenses(self, minimal_registries):
        """Planet base queue items (complexes) go to complexes_expenses."""
        colony = _mock_colony(
            facilities=[],
            construction_queue=[
                {
                    "design_id": "shipyard",
                    "type": "complex",
                    "total_cost": {"metals": 500.0, "organics": 200.0},
                    "resources_consumed": {},
                }
            ],
        )

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Base queue uses planetary_yard rates; exact values depend on production_rates.json
        # but complexes_expenses should be nonzero and ships should be zero
        assert snapshot.construction_expenses_complexes["metals"] > 0
        assert snapshot.construction_expenses_ships["metals"] == 0.0

    def test_facility_queue_ship_expenses(self, minimal_registries):
        """Shipyard facility queue items (ships) go to ships_expenses."""
        shipyard = _mock_facility(
            is_operational=True,
            is_shipyard=True,
            construction_queue=[
                {
                    "design_id": "escort",
                    "type": "ship",
                    "total_cost": {"metals": 749.0},
                    "resources_consumed": {},
                }
            ],
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'space_shipyard',
                            'abilities': {
                                'SpaceShipyard': {
                                    'construction_speed_bonus': 1.0,
                                    'production_rates': {"metals": 3000.0, "organics": 1000.0,
                                                         "vapors": 500.0, "radioactives": 500.0,
                                                         "exotics": 200.0}
                                }
                            },
                            'resource_cost': {}
                        }
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[shipyard])

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Ship costing 749 metals with 3000 rate completes within turn
        assert snapshot.construction_expenses_ships["metals"] == pytest.approx(749.0)
        assert snapshot.construction_expenses_complexes["metals"] == 0.0

    def test_construction_expenses_included_in_total(self, minimal_registries):
        """Construction expenses are included in total_expenses and net_resources."""
        shipyard = _mock_facility(
            is_operational=True,
            is_shipyard=True,
            construction_queue=[
                {
                    "design_id": "escort",
                    "type": "ship",
                    "total_cost": {"metals": 749.0},
                    "resources_consumed": {},
                }
            ],
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'space_shipyard',
                            'abilities': {
                                'SpaceShipyard': {
                                    'construction_speed_bonus': 1.0,
                                    'production_rates': {"metals": 3000.0, "organics": 1000.0,
                                                         "vapors": 500.0, "radioactives": 500.0,
                                                         "exotics": 200.0}
                                }
                            },
                            'resource_cost': {'metals': 100.0}
                        }
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[shipyard])

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Total = construction ships (749.0) only (no maintenance)
        assert snapshot.total_expenses["metals"] == pytest.approx(749.0)
        # Net = 0 production - 749 expenses
        assert snapshot.net_resources["metals"] == pytest.approx(-749.0)

    def test_mixed_ship_and_complex_in_facility_queue(self, minimal_registries):
        """Facility queue with both ship and complex items splits correctly."""
        shipyard = _mock_facility(
            is_operational=True,
            is_shipyard=True,
            construction_queue=[
                {
                    "design_id": "escort",
                    "type": "ship",
                    "total_cost": {"metals": 100.0},
                    "resources_consumed": {},
                },
                {
                    "design_id": "shipyard",
                    "type": "complex",
                    "total_cost": {"metals": 200.0},
                    "resources_consumed": {},
                },
            ],
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'space_shipyard',
                            'abilities': {
                                'SpaceShipyard': {
                                    'construction_speed_bonus': 1.0,
                                    'production_rates': {"metals": 3000.0, "organics": 1000.0,
                                                         "vapors": 500.0, "radioactives": 500.0,
                                                         "exotics": 200.0}
                                }
                            },
                            'resource_cost': {}
                        }
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[shipyard])

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Both items complete within turn (300 total vs 3000 rate)
        assert snapshot.construction_expenses_ships["metals"] == pytest.approx(100.0)
        assert snapshot.construction_expenses_complexes["metals"] == pytest.approx(200.0)

    def test_fighter_and_satellite_count_as_ships(self, minimal_registries):
        """Fighter and satellite types are categorized as ship expenses."""
        shipyard = _mock_facility(
            is_operational=True,
            is_shipyard=True,
            construction_queue=[
                {
                    "design_id": "interceptor",
                    "type": "fighter",
                    "total_cost": {"metals": 50.0},
                    "resources_consumed": {},
                },
                {
                    "design_id": "platform",
                    "type": "satellite",
                    "total_cost": {"metals": 75.0},
                    "resources_consumed": {},
                },
            ],
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'space_shipyard',
                            'abilities': {
                                'SpaceShipyard': {
                                    'construction_speed_bonus': 1.0,
                                    'production_rates': {"metals": 3000.0, "organics": 1000.0,
                                                         "vapors": 500.0, "radioactives": 500.0,
                                                         "exotics": 200.0}
                                }
                            },
                            'resource_cost': {}
                        }
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[shipyard])

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Both fighter and satellite count as ships
        assert snapshot.construction_expenses_ships["metals"] == pytest.approx(125.0)
        assert snapshot.construction_expenses_complexes["metals"] == 0.0


class TestConstructionExpensesPausedQueues:
    """FEAT-17 — paused queues contribute zero to Treasury aggregation."""

    def test_paused_planet_base_queue_excluded(self, minimal_registries):
        """A paused planet base queue must not show up in complex expenses."""
        colony = _mock_colony(
            facilities=[],
            construction_queue_paused=True,
            construction_queue=[
                {
                    "design_id": "shipyard",
                    "type": "complex",
                    "total_cost": {"metals": 500.0, "organics": 200.0},
                    "resources_consumed": {},
                }
            ],
        )

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        for res in PLANET_RESOURCE_NAMES:
            assert snapshot.construction_expenses_complexes[res] == 0.0
            assert snapshot.construction_expenses_ships[res] == 0.0

    def test_paused_facility_queue_excluded_others_still_count(self, minimal_registries):
        """Paused shipyard contributes 0; unpaused shipyard still drains."""
        paused_yard = _mock_facility(
            is_operational=True,
            is_shipyard=True,
            construction_queue_paused=True,
            construction_queue=[
                {
                    "design_id": "ship_a",
                    "type": "ship",
                    "total_cost": {"metals": 749.0},
                    "resources_consumed": {},
                }
            ],
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'space_shipyard',
                            'abilities': {
                                'SpaceShipyard': {
                                    'construction_speed_bonus': 1.0,
                                    'production_rates': {"metals": 3000.0, "organics": 1000.0,
                                                         "vapors": 500.0, "radioactives": 500.0,
                                                         "exotics": 200.0},
                                }
                            },
                            'resource_cost': {},
                        }
                    ]
                }
            },
        )
        active_yard = _mock_facility(
            is_operational=True,
            is_shipyard=True,
            construction_queue_paused=False,
            construction_queue=[
                {
                    "design_id": "ship_b",
                    "type": "ship",
                    "total_cost": {"metals": 749.0},
                    "resources_consumed": {},
                }
            ],
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'space_shipyard',
                            'abilities': {
                                'SpaceShipyard': {
                                    'construction_speed_bonus': 1.0,
                                    'production_rates': {"metals": 3000.0, "organics": 1000.0,
                                                         "vapors": 500.0, "radioactives": 500.0,
                                                         "exotics": 200.0},
                                }
                            },
                            'resource_cost': {},
                        }
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[paused_yard, active_yard])
        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Only the active yard's 749-metal ship counts.
        assert snapshot.construction_expenses_ships["metals"] == pytest.approx(749.0)
        assert snapshot.construction_expenses_complexes["metals"] == 0.0


# ---------------------------------------------------------------------------
# PROJ-290 Phase 1: empire-wide multi-resource population upkeep aggregation
# ---------------------------------------------------------------------------

class TestPopulationUpkeepAggregation:
    """`EmpireEconomySnapshot.total_population_upkeep` sums every declared
    `EconomyConfig.population_consumption` resource across every empire
    colony's populations. Mirrors `PlanetEconomyProjector._project_upkeep`
    per-colony, then adds across colonies.

    Per-turn upkeep formula (matches `OrganicsConsumptionEngine`):
        `pop.count * cfg.food_allocation * per_pop_rate`

    Empty dict when the empire has no populations at all — the treasury
    panel hides the row in that case.
    """

    @pytest.fixture
    def three_resource_economy(self):
        """Shipped `data/economy.json` baseline: organics 0.001, metals
        0.0001, radioactives 0.00001 per pop per turn."""
        from game.strategy.config.economy_config import EconomyConfig
        return EconomyConfig(population_consumption={
            "organics": 0.001,
            "metals": 0.0001,
            "radioactives": 0.00001,
        })

    def _colony_with_populations(self, populations):
        """Build a real Planet so `get_species_config` lazy-creates
        `ColonySpeciesConfig` entries with the default `food_allocation=1.0`."""
        from game.core.hex_math import HexCoord
        from game.strategy.data.planet import Planet, PlanetType
        return Planet(
            name="TestColony",
            location=HexCoord(0, 0),
            orbit_distance=3,
            mass=5.97e24, radius=6.371e6, surface_area=5.1e14, density=5515.0,
            surface_gravity=9.81, surface_pressure=101325.0, surface_temperature=288.0,
            surface_water=0.71, tectonic_activity=0.3, magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL, populations=populations, stockpile={},
            owner_id=1,
        )

    def test_empire_with_no_colonies_has_empty_upkeep(
        self, minimal_registries, three_resource_economy, _mock_race_registry,
    ):
        empire = Mock(spec=Empire)
        empire.colonies = []
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(
            registries=minimal_registries,
            economy_config=three_resource_economy,
            race_registry=_mock_race_registry,
        )
        snapshot = calculator.calculate(empire)

        assert snapshot.total_population_upkeep == {}

    def test_empire_colonies_with_no_populations_has_empty_upkeep(
        self, minimal_registries, three_resource_economy, _mock_race_registry,
    ):
        """No populations → projector loops zero times → `total_population_upkeep`
        stays `{}`. Treasury row hides itself in this state."""
        colony = self._colony_with_populations(populations=[])

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(
            registries=minimal_registries,
            economy_config=three_resource_economy,
            race_registry=_mock_race_registry,
        )
        snapshot = calculator.calculate(empire)

        assert snapshot.total_population_upkeep == {}

    def test_single_colony_single_species_uses_economy_rates(
        self, minimal_registries, three_resource_economy, _mock_race_registry,
    ):
        """1000 humans on one colony, allocation=1.0 (default):
            organics:      1000 * 1.0 * 0.001   = 1.0
            metals:        1000 * 1.0 * 0.0001  = 0.1
            radioactives:  1000 * 1.0 * 0.00001 = 0.01
        """
        from game.strategy.data.species_population import SpeciesPopulation

        colony = self._colony_with_populations(populations=[
            SpeciesPopulation(race_id="human", count=1000, happiness=0.5),
        ])

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(
            registries=minimal_registries,
            economy_config=three_resource_economy,
            race_registry=_mock_race_registry,
        )
        snapshot = calculator.calculate(empire)

        assert snapshot.total_population_upkeep["organics"] == pytest.approx(1.0)
        assert snapshot.total_population_upkeep["metals"] == pytest.approx(0.1)
        assert snapshot.total_population_upkeep["radioactives"] == pytest.approx(0.01)

    def test_multi_colony_upkeep_sums_per_resource(
        self, minimal_registries, three_resource_economy, _mock_race_registry,
    ):
        """Two colonies with 500 humans each should produce the same
        total as one colony with 1000 humans."""
        from game.strategy.data.species_population import SpeciesPopulation

        colony_a = self._colony_with_populations(populations=[
            SpeciesPopulation(race_id="human", count=500, happiness=0.5),
        ])
        colony_b = self._colony_with_populations(populations=[
            SpeciesPopulation(race_id="human", count=500, happiness=0.5),
        ])

        empire = Mock(spec=Empire)
        empire.colonies = [colony_a, colony_b]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(
            registries=minimal_registries,
            economy_config=three_resource_economy,
            race_registry=_mock_race_registry,
        )
        snapshot = calculator.calculate(empire)

        assert snapshot.total_population_upkeep["organics"] == pytest.approx(1.0)
        assert snapshot.total_population_upkeep["metals"] == pytest.approx(0.1)
        assert snapshot.total_population_upkeep["radioactives"] == pytest.approx(0.01)

    def test_multi_species_colony_upkeep_aggregates_per_resource(
        self, minimal_registries, three_resource_economy, _mock_race_registry,
    ):
        """Humans + Voidari on the same colony: upkeep per resource sums
        both species' contributions."""
        from game.strategy.data.species_population import SpeciesPopulation

        colony = self._colony_with_populations(populations=[
            SpeciesPopulation(race_id="human", count=1000, happiness=0.5),
            SpeciesPopulation(race_id="voidari", count=500, happiness=0.5),
        ])

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(
            registries=minimal_registries,
            economy_config=three_resource_economy,
            race_registry=_mock_race_registry,
        )
        snapshot = calculator.calculate(empire)

        # Humans: 1000 * 1.0 * rate; Voidari: 500 * 1.0 * rate.
        # Sum: 1500 * rate.
        assert snapshot.total_population_upkeep["organics"] == pytest.approx(1.5)
        assert snapshot.total_population_upkeep["metals"] == pytest.approx(0.15)
        assert snapshot.total_population_upkeep["radioactives"] == pytest.approx(0.015)

    def test_food_allocation_scales_upkeep_linearly(
        self, minimal_registries, three_resource_economy, _mock_race_registry,
    ):
        """Doubling `food_allocation` doubles every declared resource's
        upkeep for that species — scaling is per-species, not per-colony."""
        from game.strategy.data.species_population import SpeciesPopulation

        colony = self._colony_with_populations(populations=[
            SpeciesPopulation(race_id="human", count=1000, happiness=0.5),
        ])
        # Double the humans' allocation.
        colony.get_species_config("human").food_allocation = 2.0

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(
            registries=minimal_registries,
            economy_config=three_resource_economy,
            race_registry=_mock_race_registry,
        )
        snapshot = calculator.calculate(empire)

        # Each entry doubles relative to `test_single_colony_single_species_uses_economy_rates`.
        assert snapshot.total_population_upkeep["organics"] == pytest.approx(2.0)
        assert snapshot.total_population_upkeep["metals"] == pytest.approx(0.2)
        assert snapshot.total_population_upkeep["radioactives"] == pytest.approx(0.02)

    def test_calculator_without_economy_deps_produces_empty_upkeep(
        self, minimal_registries,
    ):
        """Backward compat: existing callers that only pass `registries=`
        still work; the new `total_population_upkeep` field is populated
        as an empty dict (the treasury row hides in that state)."""
        from game.strategy.data.species_population import SpeciesPopulation

        colony = self._colony_with_populations(populations=[
            SpeciesPopulation(race_id="human", count=1000, happiness=0.5),
        ])

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        # No economy_config / race_registry — legacy construction.
        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        assert snapshot.total_population_upkeep == {}


# ---------------------------------------------------------------------------
# PROJ-291 Phase 1 (C1): Treasury Total must include population upkeep.
# Audit found the upkeep term was computed correctly into
# `total_population_upkeep` but silently dropped from the `total_expenses`
# summation, so the Treasury panel's "Total" row showed an inconsistent
# number relative to its visible "Population Upkeep" row.
# ---------------------------------------------------------------------------

class TestTreasuryTotalIncludesUpkeep:
    """`EmpireEconomySnapshot.total_expenses[r]` must be the sum of every
    expense category INCLUDING `total_population_upkeep[r]`. Pins the C1
    contract at the unit level; `tests/integration/strategy/test_treasury_panel_e2e.py`
    pins it at the render level."""

    @pytest.fixture
    def two_resource_economy(self):
        from game.strategy.config.economy_config import EconomyConfig
        return EconomyConfig(population_consumption={
            "organics": 0.001,
            "metals": 0.0001,
        })

    def _colony_with_populations(self, populations):
        from game.core.hex_math import HexCoord
        from game.strategy.data.planet import Planet, PlanetType
        return Planet(
            name="TestColony",
            location=HexCoord(0, 0),
            orbit_distance=3,
            mass=5.97e24, radius=6.371e6, surface_area=5.1e14, density=5515.0,
            surface_gravity=9.81, surface_pressure=101325.0, surface_temperature=288.0,
            surface_water=0.71, tectonic_activity=0.3, magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL, populations=populations, stockpile={},
            owner_id=1,
        )

    def test_total_expenses_includes_population_upkeep_per_resource(
        self, minimal_registries, two_resource_economy, _mock_race_registry,
    ):
        """Two colonies x two species (humans + voidari, 1000 each) with
        non-zero `population_consumption` produce non-zero upkeep. The
        per-resource `total_expenses[r]` must equal the sum of every
        expense category — tributes + ships + complexes + upkeep — for
        EVERY planetary resource. Fails on the pre-fix code because the
        upkeep term is absent from the summation at lines 147-150 of
        `empire_economy_calculator.py`."""
        from game.strategy.data.species_population import SpeciesPopulation
        from game.strategy.engine.empire_economy_calculator import _get_planetary_ids

        populations = [
            SpeciesPopulation(race_id="human", count=1000, happiness=0.5),
            SpeciesPopulation(race_id="voidari", count=1000, happiness=0.5),
        ]
        colony_a = self._colony_with_populations(populations=populations)
        colony_b = self._colony_with_populations(populations=populations)

        empire = Mock(spec=Empire)
        empire.colonies = [colony_a, colony_b]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(
            registries=minimal_registries,
            economy_config=two_resource_economy,
            race_registry=_mock_race_registry,
        )
        snapshot = calculator.calculate(empire)

        # Sanity: the upkeep dict actually has non-zero values, otherwise
        # the test below would pass even with the bug present.
        assert snapshot.total_population_upkeep.get("organics", 0.0) > 0.0
        assert snapshot.total_population_upkeep.get("metals", 0.0) > 0.0

        for r in _get_planetary_ids():
            expected = (
                snapshot.tribute_expenses.get(r, 0.0)
                + snapshot.construction_expenses_ships.get(r, 0.0)
                + snapshot.construction_expenses_complexes.get(r, 0.0)
                + snapshot.total_population_upkeep.get(r, 0.0)
            )
            assert snapshot.total_expenses[r] == pytest.approx(expected), (
                f"total_expenses[{r}] should include population upkeep: "
                f"{snapshot.total_expenses[r]} != {expected}"
            )

    def test_net_resources_reflects_upkeep_in_total(
        self, minimal_registries, two_resource_economy, _mock_race_registry,
    ):
        """`net_resources[r] == total_production[r] - total_expenses[r]` is
        the existing contract; combined with Test 1 this means net is
        also lower by the upkeep amount. With the bug present, net is
        overstated by exactly the per-resource upkeep value."""
        from game.strategy.data.species_population import SpeciesPopulation
        from game.strategy.engine.empire_economy_calculator import _get_planetary_ids

        colony = self._colony_with_populations(populations=[
            SpeciesPopulation(race_id="human", count=1000, happiness=0.5),
        ])

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(
            registries=minimal_registries,
            economy_config=two_resource_economy,
            race_registry=_mock_race_registry,
        )
        snapshot = calculator.calculate(empire)

        for r in _get_planetary_ids():
            expected_net = snapshot.total_production.get(r, 0.0) - (
                snapshot.tribute_expenses.get(r, 0.0)
                + snapshot.construction_expenses_ships.get(r, 0.0)
                + snapshot.construction_expenses_complexes.get(r, 0.0)
                + snapshot.total_population_upkeep.get(r, 0.0)
            )
            assert snapshot.net_resources[r] == pytest.approx(expected_net), (
                f"net_resources[{r}] should reflect upkeep drain: "
                f"{snapshot.net_resources[r]} != {expected_net}"
            )
