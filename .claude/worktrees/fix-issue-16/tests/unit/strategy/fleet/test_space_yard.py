"""Tests for Fleet space yard capabilities (PROJ-67 Phase 1)."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord


class TestFleetConstructionQueue:
    """Test cases for fleet construction_queue field."""

    def test_fleet_initializes_with_empty_construction_queue(self, basic_fleet):
        """Test fleet initializes with empty construction_queue."""
        assert hasattr(basic_fleet, 'construction_queue')
        assert basic_fleet.construction_queue == []

    def test_fleet_serialization_includes_construction_queue(self, make_ship_instance):
        """Test construction_queue is included in to_dict()."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.construction_queue = [
            {"design_id": "destroyer", "type": "ship", "turns_remaining": 5},
            {"design_id": "fighter_wing", "type": "fighter", "turns_remaining": 2},
        ]

        d = fleet.to_dict()

        assert 'construction_queue' in d
        assert len(d['construction_queue']) == 2
        assert d['construction_queue'][0]['design_id'] == 'destroyer'
        assert d['construction_queue'][1]['turns_remaining'] == 2

    def test_fleet_deserialization_restores_construction_queue(self):
        """Test construction_queue is restored from from_dict()."""
        d = {
            'id': 'f1',
            'owner_id': 0,
            'location': [0, 0],
            'speed': 5.0,
            'ships': [],
            'orders': [],
            'path': [],
            'construction_queue': [
                {"design_id": "cruiser", "type": "ship", "turns_remaining": 8}
            ],
        }

        fleet = Fleet.from_dict(d)

        assert len(fleet.construction_queue) == 1
        assert fleet.construction_queue[0]['design_id'] == 'cruiser'
        assert fleet.construction_queue[0]['turns_remaining'] == 8

    def test_fleet_deserialization_defaults_to_empty_queue(self):
        """Test from_dict() defaults to empty queue if not present."""
        d = {
            'id': 'f1',
            'owner_id': 0,
            'location': [0, 0],
            'speed': 5.0,
            'ships': [],
            'orders': [],
            'path': [],
        }

        fleet = Fleet.from_dict(d)

        assert fleet.construction_queue == []

    def test_construction_queue_roundtrip(self, make_ship_instance):
        """Test construction_queue survives serialization roundtrip."""
        original = Fleet("test", 0, HexCoord(0, 0))
        original.construction_queue = [
            {"design_id": "battleship", "type": "ship", "turns_remaining": 15}
        ]

        d = original.to_dict()
        d['location'] = [0, 0]  # Fix HexCoord serialization gap

        restored = Fleet.from_dict(d)

        assert restored.construction_queue == original.construction_queue


class TestFleetHasSpaceShipyard:
    """Test cases for Fleet.has_space_shipyard property.

    PROJ-211: Updated to set _registries on mocks for DI compliance.
    """

    @pytest.fixture
    def make_ship_with_yard(self, fresh_registries):
        """Factory for creating ship with space_shipyard component."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(name="Yard Ship", has_yard=True, is_combat_capable=True):
            mock = MagicMock(spec=ShipInstance)
            mock.name = name
            mock.is_combat_capable.return_value = is_combat_capable
            # PROJ-211: Set _registries for DI compliance
            mock._registries = fresh_registries

            if has_yard:
                mock.design_data = {
                    'name': name,
                    'vehicle_type': 'Ship',
                    'layers': {
                        'core': [
                            {'id': 'space_shipyard', 'name': 'Fleet Space Yard'}
                        ]
                    }
                }
            else:
                mock.design_data = {
                    'name': name,
                    'vehicle_type': 'Ship',
                    'layers': {
                        'core': [
                            {'id': 'reactor', 'name': 'Reactor'}
                        ]
                    }
                }
            return mock
        return _make

    def test_fleet_without_yard_returns_false(self, basic_fleet, make_mock_ship):
        """Test fleet without yard ship returns False."""
        ship = make_mock_ship(name="Scout")
        basic_fleet.ships.append(ship)

        assert basic_fleet.capabilities.has_space_shipyard is False

    def test_fleet_with_yard_returns_true(self, basic_fleet, make_ship_with_yard):
        """Test fleet with yard ship returns True."""
        yard_ship = make_ship_with_yard(name="Construction Ship", has_yard=True)
        basic_fleet.ships.append(yard_ship)

        assert basic_fleet.capabilities.has_space_shipyard is True

    def test_fleet_with_destroyed_yard_returns_false(self, basic_fleet, make_ship_with_yard):
        """Test fleet with destroyed yard ship returns False."""
        yard_ship = make_ship_with_yard(name="Construction Ship", has_yard=True, is_combat_capable=False)
        basic_fleet.ships.append(yard_ship)

        assert basic_fleet.capabilities.has_space_shipyard is False

    def test_fleet_with_mixed_ships_finds_yard(self, basic_fleet, make_ship_with_yard, make_mock_ship):
        """Test fleet finds yard among multiple ships."""
        escort = make_mock_ship(name="Escort")
        yard_ship = make_ship_with_yard(name="Construction Ship", has_yard=True)
        tanker = make_mock_ship(name="Tanker")

        basic_fleet.ships.append(escort)
        basic_fleet.ships.append(yard_ship)
        basic_fleet.ships.append(tanker)

        assert basic_fleet.capabilities.has_space_shipyard is True

    def test_empty_fleet_returns_false(self, basic_fleet):
        """Test empty fleet returns False."""
        assert basic_fleet.capabilities.has_space_shipyard is False

    def test_fleet_with_ability_dict_format(self, basic_fleet, fresh_registries):
        """Test fleet detects SpaceShipyard via abilities dict (test fixture format)."""
        mock = MagicMock()
        mock.is_combat_capable.return_value = True
        mock._registries = fresh_registries  # PROJ-211: DI compliance
        mock.design_data = {
            'name': 'Test Ship',
            'vehicle_type': 'Ship',
            'layers': {
                'core': [
                    {'id': 'custom', 'abilities': {'SpaceShipyard': {'construction_speed_bonus': 1.0}}}
                ]
            }
        }
        basic_fleet.ships.append(mock)

        assert basic_fleet.capabilities.has_space_shipyard is True


class TestFleetCanBuildType:
    """Test cases for Fleet.can_build_type() method.

    PROJ-211: Updated to set _registries on mocks for DI compliance.
    """

    @pytest.fixture
    def fleet_with_yard(self, basic_fleet, make_ship_with_yard):
        """Create a fleet with a space yard."""
        yard_ship = make_ship_with_yard(name="Construction Ship", has_yard=True)
        basic_fleet.ships.append(yard_ship)
        return basic_fleet

    @pytest.fixture
    def make_ship_with_yard(self, fresh_registries):
        """Factory for creating ship with space_shipyard component."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(name="Yard Ship", has_yard=True, is_combat_capable=True):
            mock = MagicMock(spec=ShipInstance)
            mock.name = name
            mock.is_combat_capable.return_value = is_combat_capable
            mock._registries = fresh_registries  # PROJ-211: DI compliance

            if has_yard:
                mock.design_data = {
                    'name': name,
                    'vehicle_type': 'Ship',
                    'layers': {
                        'core': [
                            {'id': 'space_shipyard', 'name': 'Fleet Space Yard'}
                        ]
                    }
                }
            else:
                mock.design_data = {
                    'name': name,
                    'vehicle_type': 'Ship',
                    'layers': {
                        'core': [
                            {'id': 'reactor', 'name': 'Reactor'}
                        ]
                    }
                }
            return mock
        return _make

    def test_fleet_with_yard_can_build_ships(self, fleet_with_yard):
        """Test fleet with yard can build ships (PROJ-210: via capabilities)."""
        assert fleet_with_yard.capabilities.can_build_type("ship") is True
        assert fleet_with_yard.capabilities.can_build_type("Ship") is True

    def test_fleet_with_yard_can_build_fighters(self, fleet_with_yard):
        """Test fleet with yard can build fighters (PROJ-210: via capabilities)."""
        assert fleet_with_yard.capabilities.can_build_type("fighter") is True
        assert fleet_with_yard.capabilities.can_build_type("Fighter") is True

    def test_fleet_with_yard_can_build_satellites(self, fleet_with_yard):
        """Test fleet with yard can build satellites (PROJ-210: via capabilities)."""
        assert fleet_with_yard.capabilities.can_build_type("satellite") is True
        assert fleet_with_yard.capabilities.can_build_type("Satellite") is True

    def test_fleet_without_yard_cannot_build(self, basic_fleet, make_mock_ship):
        """Test fleet without yard cannot build anything (PROJ-210: via capabilities)."""
        ship = make_mock_ship(name="Scout")
        basic_fleet.ships.append(ship)

        assert basic_fleet.capabilities.can_build_type("ship") is False
        assert basic_fleet.capabilities.can_build_type("fighter") is False
        assert basic_fleet.capabilities.can_build_type("complex") is False

    def test_fleet_at_planet_can_build_complex(self, fleet_with_yard):
        """Test fleet at planet hex can build complexes (PROJ-210: via capabilities)."""
        # Mock galaxy with planet at fleet's location
        mock_galaxy = MagicMock()
        mock_planet = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]

        assert fleet_with_yard.capabilities.can_build_type("complex", galaxy=mock_galaxy) is True
        mock_galaxy.get_planets_at_global_hex.assert_called_with(fleet_with_yard.location)

    def test_fleet_not_at_planet_cannot_build_complex(self, fleet_with_yard):
        """Test fleet NOT at planet hex cannot build complexes (PROJ-210: via capabilities)."""
        # Mock galaxy with no planet at fleet's location
        mock_galaxy = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = []

        assert fleet_with_yard.capabilities.can_build_type("complex", galaxy=mock_galaxy) is False

    def test_complex_requires_galaxy_parameter(self, fleet_with_yard):
        """Test building complex without galaxy param returns False (PROJ-210: via capabilities)."""
        assert fleet_with_yard.capabilities.can_build_type("complex") is False
        assert fleet_with_yard.capabilities.can_build_type("complex", galaxy=None) is False

    def test_unknown_vehicle_type_returns_false(self, fleet_with_yard):
        """Test unknown vehicle type returns False (PROJ-210: via capabilities)."""
        assert fleet_with_yard.capabilities.can_build_type("unknown") is False
        assert fleet_with_yard.capabilities.can_build_type("spaceship") is False


class TestFleetSpaceShipyardCount:
    """Test cases for Fleet.space_shipyard_count property (BUG-79).

    PROJ-211: Updated to set _registries on mocks for DI compliance.
    """

    @pytest.fixture
    def make_yard_ship(self, fresh_registries):
        """Factory for creating ships with configurable yard count."""
        def _make(name="Yard Ship", yard_count=1, is_combat_capable=True):
            mock = MagicMock()
            mock.name = name
            mock.is_combat_capable.return_value = is_combat_capable
            mock._registries = fresh_registries  # PROJ-211: DI compliance
            components = [{'id': 'space_shipyard'} for _ in range(yard_count)]
            components.append({'id': 'reactor'})  # Non-yard component
            mock.design_data = {
                'name': name,
                'vehicle_type': 'Ship',
                'layers': {'core': components}
            }
            return mock
        return _make

    def test_empty_fleet_has_zero_yards(self, basic_fleet):
        """Empty fleet has 0 space yards (PROJ-210: via capabilities)."""
        assert basic_fleet.capabilities.space_shipyard_count == 0

    def test_fleet_with_one_yard_counts_one(self, basic_fleet, make_yard_ship):
        """Fleet with one yard component counts 1 (PROJ-210: via capabilities)."""
        basic_fleet.ships.append(make_yard_ship(yard_count=1))
        assert basic_fleet.capabilities.space_shipyard_count == 1

    def test_fleet_with_two_yards_on_one_ship(self, basic_fleet, make_yard_ship):
        """Ship with 2 space_shipyard components counts 2 (BUG-79 core case, PROJ-210: via capabilities)."""
        basic_fleet.ships.append(make_yard_ship(yard_count=2))
        assert basic_fleet.capabilities.space_shipyard_count == 2

    def test_fleet_with_yards_across_multiple_ships(self, basic_fleet, make_yard_ship):
        """Yards across multiple ships are summed (PROJ-210: via capabilities)."""
        basic_fleet.ships.append(make_yard_ship(name="Ship A", yard_count=1))
        basic_fleet.ships.append(make_yard_ship(name="Ship B", yard_count=2))
        assert basic_fleet.capabilities.space_shipyard_count == 3

    def test_destroyed_ship_yards_not_counted(self, basic_fleet, make_yard_ship):
        """Yards on destroyed (non-combat-capable) ships are not counted (PROJ-210: via capabilities)."""
        basic_fleet.ships.append(make_yard_ship(yard_count=2, is_combat_capable=False))
        assert basic_fleet.capabilities.space_shipyard_count == 0
