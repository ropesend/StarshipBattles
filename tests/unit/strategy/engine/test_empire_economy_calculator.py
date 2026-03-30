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
from game.strategy.data.planet import Planet, PlanetaryFacility
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance
PLANET_RESOURCE_NAMES = ["Metals", "Organics", "Vapors", "Radioactives", "Exotics"]


def _mock_colony(**kwargs):
    """Create a mock colony with construction_queue defaulting to empty."""
    colony = Mock(spec=Planet)
    colony.construction_queue = kwargs.pop('construction_queue', [])
    colony.facilities = kwargs.pop('facilities', [])
    colony.resources = kwargs.pop('resources', {})
    for k, v in kwargs.items():
        setattr(colony, k, v)
    return colony


def _mock_facility(**kwargs):
    """Create a mock facility with construction_queue defaulting to empty."""
    facility = Mock(spec=PlanetaryFacility)
    facility.construction_queue = kwargs.pop('construction_queue', [])
    for k, v in kwargs.items():
        setattr(facility, k, v)
    return facility


def _mock_fleet(**kwargs):
    """Create a mock fleet with construction_queue defaulting to empty."""
    fleet = Mock(spec=Fleet)
    fleet.construction_queue = kwargs.pop('construction_queue', [])
    for k, v in kwargs.items():
        setattr(fleet, k, v)
    return fleet


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
        assert snapshot.maintenance_expenses == {}
        assert snapshot.construction_expenses_ships == {}
        assert snapshot.construction_expenses_complexes == {}
        assert snapshot.total_expenses == {}
        assert snapshot.net_resources == {}
        assert snapshot.current_storage == {}
        assert snapshot.max_storage == {}


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
            assert snapshot.maintenance_expenses.get(res, 0.0) == 0.0
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
                                    'resource_type': 'Metals',
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
                              resources={'Metals': {'quality': 0.8, 'quantity': 1000}})

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Production = base_rate * quality = 10.0 * 0.8 = 8.0
        assert snapshot.colony_production['Metals'] == 8.0
        assert snapshot.total_production['Metals'] == 8.0

    def test_facility_maintenance_cost_is_5_percent(self, minimal_registries):
        """Facility maintenance is 5% of resource_cost."""
        facility = _mock_facility(
            is_operational=True,
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'expensive_building',
                            'abilities': {},
                            'resource_cost': {
                                'Metals': 100.0,
                                'Organics': 50.0
                            }
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

        # Maintenance = 5% of build cost
        assert snapshot.maintenance_expenses['Metals'] == 5.0  # 100 * 0.05
        assert snapshot.maintenance_expenses['Organics'] == 2.5  # 50 * 0.05

    def test_ship_maintenance_cost_is_5_percent(self, minimal_registries):
        """Ship maintenance is 5% of resource_cost."""
        ship = Mock(spec=ShipInstance)
        ship.design_data = {
            'layers': {
                'HULL': [
                    {
                        'id': 'hull_component',
                        'resource_cost': {'Metals': 200.0}
                    }
                ],
                'CORE': [
                    {
                        'id': 'core_component',
                        'resource_cost': {'Vapors': 80.0}
                    }
                ]
            }
        }

        fleet = _mock_fleet(ships=[ship])

        empire = Mock(spec=Empire)
        empire.colonies = []
        empire.fleets = [fleet]
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Total maintenance = 5% of total build cost
        assert snapshot.maintenance_expenses['Metals'] == 10.0  # 200 * 0.05
        assert snapshot.maintenance_expenses['Vapors'] == 4.0  # 80 * 0.05

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
                                    'resource_type': 'Metals',
                                    'base_harvest_rate': 10.0
                                }
                            },
                            'resource_cost': {'Metals': 40.0}  # 40 * 0.05 = 2.0 maintenance
                        }
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[facility],
                              resources={'Metals': {'quality': 1.0, 'quantity': 1000}})

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Production = 10.0 * 1.0 = 10.0
        # Maintenance = 40.0 * 0.05 = 2.0
        # Net = 10.0 - 2.0 = 8.0
        assert snapshot.total_production['Metals'] == 10.0
        assert snapshot.total_expenses['Metals'] == 2.0
        assert snapshot.net_resources['Metals'] == 8.0

    def test_current_storage_and_max_storage_copied_from_empire(self, minimal_registries):
        """current_storage and max_storage are copied from empire."""
        empire = Mock(spec=Empire)
        empire.colonies = []
        empire.fleets = []
        empire.resource_pool = {'Metals': 500.0, 'Organics': 300.0}
        empire.max_storage = {'Metals': 1000.0, 'Organics': 1000.0}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        assert snapshot.current_storage == {'Metals': 500.0, 'Organics': 300.0}
        assert snapshot.max_storage == {'Metals': 1000.0, 'Organics': 1000.0}

    def test_non_operational_facility_is_skipped(self, minimal_registries):
        """Non-operational facilities contribute neither production nor maintenance."""
        facility = _mock_facility(
            is_operational=False,
            design_data={
                'layers': {
                    'CORE': [
                        {
                            'id': 'expensive_harvester',
                            'abilities': {
                                'ResourceHarvester': {
                                    'resource_type': 'Metals',
                                    'base_harvest_rate': 100.0
                                }
                            },
                            'resource_cost': {'Metals': 1000.0}
                        }
                    ]
                }
            },
        )

        colony = _mock_colony(facilities=[facility],
                              resources={'Metals': {'quality': 1.0, 'quantity': 5000}})

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        # Both production and maintenance should be zero
        assert snapshot.colony_production['Metals'] == 0.0
        assert snapshot.maintenance_expenses['Metals'] == 0.0

    def test_dict_format_layer_with_components_key(self, minimal_registries):
        """Handles dict-format layer: {'components': [...]}."""
        facility = _mock_facility(
            is_operational=True,
            design_data={
                'layers': {
                    'CORE': {
                        'components': [
                            {
                                'id': 'building',
                                'resource_cost': {'Exotics': 60.0}
                            }
                        ]
                    }
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

        # Maintenance = 60 * 0.05 = 3.0
        assert snapshot.maintenance_expenses['Exotics'] == 3.0

    def test_list_format_layer_direct(self, minimal_registries):
        """Handles list-format layer: [component1, component2, ...]."""
        facility = _mock_facility(
            is_operational=True,
            design_data={
                'layers': {
                    'HULL': [
                        {
                            'id': 'building_a',
                            'resource_cost': {'Radioactives': 80.0}
                        },
                        {
                            'id': 'building_b',
                            'resource_cost': {'Radioactives': 20.0}
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

        # Total maintenance = (80 + 20) * 0.05 = 5.0
        assert snapshot.maintenance_expenses['Radioactives'] == 5.0

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
                                    'resource_type': 'Metals',
                                    'base_harvest_rate': 5.0
                                }
                            },
                            'resource_cost': {'Metals': 20.0}
                        }
                    ]
                }
            },
        )
        colony1 = _mock_colony(facilities=[facility1],
                               resources={'Metals': {'quality': 1.0, 'quantity': 1000}})

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
                                    'resource_type': 'Organics',
                                    'base_harvest_rate': 8.0
                                }
                            },
                            'resource_cost': {'Organics': 40.0}
                        }
                    ]
                }
            },
        )
        colony2 = _mock_colony(facilities=[facility2],
                               resources={'Organics': {'quality': 0.5, 'quantity': 1000}})

        # Fleet with ship
        ship = Mock(spec=ShipInstance)
        ship.design_data = {
            'layers': {
                'HULL': [{'id': 'hull', 'resource_cost': {'Vapors': 100.0}}]
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
        assert snapshot.colony_production['Metals'] == 5.0  # 5.0 * 1.0
        assert snapshot.colony_production['Organics'] == 4.0  # 8.0 * 0.5

        # Maintenance: facility1 + facility2 + ship
        assert snapshot.maintenance_expenses['Metals'] == 1.0  # 20 * 0.05
        assert snapshot.maintenance_expenses['Organics'] == 2.0  # 40 * 0.05
        assert snapshot.maintenance_expenses['Vapors'] == 5.0  # 100 * 0.05

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
                                    'resource_type': 'Exotics',
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
        assert snapshot.colony_production['Exotics'] == 0.0

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
                              resources={'Metals': {'quality': 0.8, 'quantity': 5000}})

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
                'resource_type': 'Metals',
                'base_harvest_rate': 100.0
            }
        }
        registries.components.get.return_value = comp_def

        calculator = EmpireEconomyCalculator(registries=registries)
        snapshot = calculator.calculate(empire)

        # Production = 100.0 * 0.8 = 80.0
        assert snapshot.colony_production['Metals'] == 80.0
        assert snapshot.total_production['Metals'] == 80.0

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
                              resources={'Metals': {'quality': 0.8, 'quantity': 5000}})

        empire = Mock(spec=Empire)
        empire.colonies = [colony]
        empire.fleets = []
        empire.resource_pool = {}
        empire.max_storage = {}

        # Empty registries - component lookup will fail, should gracefully return 0
        calculator = EmpireEconomyCalculator(registries=minimal_registries)
        snapshot = calculator.calculate(empire)

        assert snapshot.colony_production['Metals'] == 0.0


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
                    "total_cost": {"Metals": 500.0, "Organics": 200.0},
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
        assert snapshot.construction_expenses_complexes["Metals"] > 0
        assert snapshot.construction_expenses_ships["Metals"] == 0.0

    def test_facility_queue_ship_expenses(self, minimal_registries):
        """Shipyard facility queue items (ships) go to ships_expenses."""
        shipyard = _mock_facility(
            is_operational=True,
            is_shipyard=True,
            construction_queue=[
                {
                    "design_id": "escort",
                    "type": "ship",
                    "total_cost": {"Metals": 749.0},
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
                                    'production_rates': {"Metals": 3000.0, "Organics": 1000.0,
                                                         "Vapors": 500.0, "Radioactives": 500.0,
                                                         "Exotics": 200.0}
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
        assert snapshot.construction_expenses_ships["Metals"] == pytest.approx(749.0)
        assert snapshot.construction_expenses_complexes["Metals"] == 0.0

    def test_construction_expenses_included_in_total(self, minimal_registries):
        """Construction expenses are included in total_expenses and net_resources."""
        shipyard = _mock_facility(
            is_operational=True,
            is_shipyard=True,
            construction_queue=[
                {
                    "design_id": "escort",
                    "type": "ship",
                    "total_cost": {"Metals": 749.0},
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
                                    'production_rates': {"Metals": 3000.0, "Organics": 1000.0,
                                                         "Vapors": 500.0, "Radioactives": 500.0,
                                                         "Exotics": 200.0}
                                }
                            },
                            'resource_cost': {'Metals': 100.0}  # 5.0 maintenance
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

        # Total = maintenance (5.0) + construction ships (749.0)
        assert snapshot.total_expenses["Metals"] == pytest.approx(754.0)
        # Net = 0 production - 754 expenses
        assert snapshot.net_resources["Metals"] == pytest.approx(-754.0)

    def test_mixed_ship_and_complex_in_facility_queue(self, minimal_registries):
        """Facility queue with both ship and complex items splits correctly."""
        shipyard = _mock_facility(
            is_operational=True,
            is_shipyard=True,
            construction_queue=[
                {
                    "design_id": "escort",
                    "type": "ship",
                    "total_cost": {"Metals": 100.0},
                    "resources_consumed": {},
                },
                {
                    "design_id": "shipyard",
                    "type": "complex",
                    "total_cost": {"Metals": 200.0},
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
                                    'production_rates': {"Metals": 3000.0, "Organics": 1000.0,
                                                         "Vapors": 500.0, "Radioactives": 500.0,
                                                         "Exotics": 200.0}
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
        assert snapshot.construction_expenses_ships["Metals"] == pytest.approx(100.0)
        assert snapshot.construction_expenses_complexes["Metals"] == pytest.approx(200.0)

    def test_fighter_and_satellite_count_as_ships(self, minimal_registries):
        """Fighter and satellite types are categorized as ship expenses."""
        shipyard = _mock_facility(
            is_operational=True,
            is_shipyard=True,
            construction_queue=[
                {
                    "design_id": "interceptor",
                    "type": "fighter",
                    "total_cost": {"Metals": 50.0},
                    "resources_consumed": {},
                },
                {
                    "design_id": "platform",
                    "type": "satellite",
                    "total_cost": {"Metals": 75.0},
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
                                    'production_rates': {"Metals": 3000.0, "Organics": 1000.0,
                                                         "Vapors": 500.0, "Radioactives": 500.0,
                                                         "Exotics": 200.0}
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
        assert snapshot.construction_expenses_ships["Metals"] == pytest.approx(125.0)
        assert snapshot.construction_expenses_complexes["Metals"] == 0.0
