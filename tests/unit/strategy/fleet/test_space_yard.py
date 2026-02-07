"""Tests for Fleet space yard capabilities (PROJ-67 Phase 1)."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.strategy.data.hex_math import HexCoord


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
    """Test cases for Fleet.has_space_shipyard property."""

    @pytest.fixture
    def make_ship_with_yard(self):
        """Factory for creating ship with fleet_space_yard component."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(name="Yard Ship", has_yard=True, is_combat_capable=True):
            mock = MagicMock(spec=ShipInstance)
            mock.name = name
            mock.is_combat_capable.return_value = is_combat_capable

            if has_yard:
                mock.design_data = {
                    'name': name,
                    'vehicle_type': 'Ship',
                    'layers': {
                        'core': [
                            {'id': 'fleet_space_yard', 'name': 'Fleet Space Yard'}
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

        assert basic_fleet.has_space_shipyard is False

    def test_fleet_with_yard_returns_true(self, basic_fleet, make_ship_with_yard):
        """Test fleet with yard ship returns True."""
        yard_ship = make_ship_with_yard(name="Construction Ship", has_yard=True)
        basic_fleet.ships.append(yard_ship)

        assert basic_fleet.has_space_shipyard is True

    def test_fleet_with_destroyed_yard_returns_false(self, basic_fleet, make_ship_with_yard):
        """Test fleet with destroyed yard ship returns False."""
        yard_ship = make_ship_with_yard(name="Construction Ship", has_yard=True, is_combat_capable=False)
        basic_fleet.ships.append(yard_ship)

        assert basic_fleet.has_space_shipyard is False

    def test_fleet_with_mixed_ships_finds_yard(self, basic_fleet, make_ship_with_yard, make_mock_ship):
        """Test fleet finds yard among multiple ships."""
        escort = make_mock_ship(name="Escort")
        yard_ship = make_ship_with_yard(name="Construction Ship", has_yard=True)
        tanker = make_mock_ship(name="Tanker")

        basic_fleet.ships.append(escort)
        basic_fleet.ships.append(yard_ship)
        basic_fleet.ships.append(tanker)

        assert basic_fleet.has_space_shipyard is True

    def test_empty_fleet_returns_false(self, basic_fleet):
        """Test empty fleet returns False."""
        assert basic_fleet.has_space_shipyard is False

    def test_fleet_with_ability_dict_format(self, basic_fleet):
        """Test fleet detects SpaceShipyard via abilities dict (test fixture format)."""
        mock = MagicMock()
        mock.is_combat_capable.return_value = True
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

        assert basic_fleet.has_space_shipyard is True


class TestFleetCanBuildType:
    """Test cases for Fleet.can_build_type() method."""

    @pytest.fixture
    def fleet_with_yard(self, basic_fleet, make_ship_with_yard):
        """Create a fleet with a space yard."""
        yard_ship = make_ship_with_yard(name="Construction Ship", has_yard=True)
        basic_fleet.ships.append(yard_ship)
        return basic_fleet

    @pytest.fixture
    def make_ship_with_yard(self):
        """Factory for creating ship with fleet_space_yard component."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(name="Yard Ship", has_yard=True, is_combat_capable=True):
            mock = MagicMock(spec=ShipInstance)
            mock.name = name
            mock.is_combat_capable.return_value = is_combat_capable

            if has_yard:
                mock.design_data = {
                    'name': name,
                    'vehicle_type': 'Ship',
                    'layers': {
                        'core': [
                            {'id': 'fleet_space_yard', 'name': 'Fleet Space Yard'}
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
        """Test fleet with yard can build ships."""
        assert fleet_with_yard.can_build_type("ship") is True
        assert fleet_with_yard.can_build_type("Ship") is True

    def test_fleet_with_yard_can_build_fighters(self, fleet_with_yard):
        """Test fleet with yard can build fighters."""
        assert fleet_with_yard.can_build_type("fighter") is True
        assert fleet_with_yard.can_build_type("Fighter") is True

    def test_fleet_with_yard_can_build_satellites(self, fleet_with_yard):
        """Test fleet with yard can build satellites."""
        assert fleet_with_yard.can_build_type("satellite") is True
        assert fleet_with_yard.can_build_type("Satellite") is True

    def test_fleet_without_yard_cannot_build(self, basic_fleet, make_mock_ship):
        """Test fleet without yard cannot build anything."""
        ship = make_mock_ship(name="Scout")
        basic_fleet.ships.append(ship)

        assert basic_fleet.can_build_type("ship") is False
        assert basic_fleet.can_build_type("fighter") is False
        assert basic_fleet.can_build_type("complex") is False

    def test_fleet_at_planet_can_build_complex(self, fleet_with_yard):
        """Test fleet at planet hex can build complexes."""
        # Mock galaxy with planet at fleet's location
        mock_galaxy = MagicMock()
        mock_planet = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]

        assert fleet_with_yard.can_build_type("complex", galaxy=mock_galaxy) is True
        mock_galaxy.get_planets_at_global_hex.assert_called_with(fleet_with_yard.location)

    def test_fleet_not_at_planet_cannot_build_complex(self, fleet_with_yard):
        """Test fleet NOT at planet hex cannot build complexes."""
        # Mock galaxy with no planet at fleet's location
        mock_galaxy = MagicMock()
        mock_galaxy.get_planets_at_global_hex.return_value = []

        assert fleet_with_yard.can_build_type("complex", galaxy=mock_galaxy) is False

    def test_complex_requires_galaxy_parameter(self, fleet_with_yard):
        """Test building complex without galaxy param returns False."""
        assert fleet_with_yard.can_build_type("complex") is False
        assert fleet_with_yard.can_build_type("complex", galaxy=None) is False

    def test_unknown_vehicle_type_returns_false(self, fleet_with_yard):
        """Test unknown vehicle type returns False."""
        assert fleet_with_yard.can_build_type("unknown") is False
        assert fleet_with_yard.can_build_type("spaceship") is False
