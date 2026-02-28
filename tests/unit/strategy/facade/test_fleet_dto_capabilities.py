"""Tests for Fleet DTO capabilities field (PROJ-208 Phase 4)."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord
from game.strategy.facade.dto.fleet_dto import FleetInfo


class TestFleetInfoCapabilitiesField:
    """Test cases for FleetInfo capabilities DTO field.

    The capabilities field exposes fleet abilities to the UI layer without
    requiring direct domain object access.
    """

    @pytest.fixture
    def make_ship_with_ability(self, fresh_registries):
        """Factory for creating ship with specified ability."""
        def _make(name="Weapon Ship", ability_component='destroy_planet'):
            mock = MagicMock()
            mock.name = name
            mock.instance_id = f"inst_{name}"
            mock.design_id = "weapon_ship"
            mock.is_combat_capable.return_value = True
            mock.get_hp_percentage.return_value = 1.0
            mock.get_calculated_stats.return_value = {'mass': 5000}
            mock._registries = fresh_registries
            mock.design_data = {
                'name': name,
                'ship_class': 'Cruiser',
                'vehicle_type': 'Ship',
                'layers': {
                    'core': [{'id': ability_component, 'name': ability_component}]
                }
            }
            return mock
        return _make

    @pytest.fixture
    def make_regular_ship(self, fresh_registries):
        """Factory for creating regular ship without special abilities."""
        def _make(name="Scout"):
            mock = MagicMock()
            mock.name = name
            mock.instance_id = f"inst_{name}"
            mock.design_id = "scout"
            mock.is_combat_capable.return_value = True
            mock.get_hp_percentage.return_value = 1.0
            mock.get_calculated_stats.return_value = {'mass': 2000}
            mock._registries = fresh_registries
            mock.design_data = {
                'name': name,
                'ship_class': 'Scout',
                'vehicle_type': 'Ship',
                'layers': {'core': [{'id': 'engine'}]}
            }
            return mock
        return _make

    def test_fleet_info_has_capabilities_field(self):
        """Test FleetInfo has capabilities field."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        info = FleetInfo.from_fleet(fleet)

        assert hasattr(info, 'capabilities')

    def test_fleet_info_capabilities_is_tuple(self, make_regular_ship):
        """Test capabilities field is an immutable tuple."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_regular_ship())

        info = FleetInfo.from_fleet(fleet)

        assert isinstance(info.capabilities, tuple)

    def test_fleet_info_capabilities_empty_when_no_ships(self):
        """Test capabilities is empty when fleet has no ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        info = FleetInfo.from_fleet(fleet)

        assert info.capabilities == ()

    def test_fleet_info_capabilities_empty_when_no_special_abilities(self, make_regular_ship):
        """Test capabilities is empty when ships have no special abilities."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_regular_ship())

        info = FleetInfo.from_fleet(fleet)

        # Regular ship (engine only) has no superweapon abilities
        # Note: May have basic abilities like WarpJump but not DestroyPlanet etc.
        superweapon_abilities = {'DestroyPlanet', 'DestroyStar', 'OpenWarpPoint',
                                  'CloseWarpPoint', 'CreateDysonSphere', 'SelfDestruct'}
        actual_superweapons = set(info.capabilities) & superweapon_abilities
        assert actual_superweapons == set()

    def test_fleet_info_capabilities_includes_destroy_planet(self, make_ship_with_ability):
        """Test capabilities includes DestroyPlanet when ship has that ability."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        # planet_imploder is the component ID with DestroyPlanet ability
        fleet.ships.append(make_ship_with_ability("Death Star", "planet_imploder"))

        info = FleetInfo.from_fleet(fleet)

        assert 'DestroyPlanet' in info.capabilities

    def test_fleet_info_capabilities_includes_space_shipyard(self, make_ship_with_ability):
        """Test capabilities includes SpaceShipyard for fleet yard."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_ship_with_ability("Yard Ship", "fleet_space_yard"))

        info = FleetInfo.from_fleet(fleet)

        assert 'SpaceShipyard' in info.capabilities

    def test_fleet_info_capabilities_no_duplicates(self, make_ship_with_ability):
        """Test capabilities has no duplicates even with multiple ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        # Add two ships with same ability
        fleet.ships.append(make_ship_with_ability("Yard 1", "fleet_space_yard"))
        fleet.ships.append(make_ship_with_ability("Yard 2", "fleet_space_yard"))

        info = FleetInfo.from_fleet(fleet)

        # Should have SpaceShipyard only once
        count = sum(1 for c in info.capabilities if c == 'SpaceShipyard')
        assert count == 1

    def test_fleet_info_capabilities_is_immutable(self, make_ship_with_ability):
        """Test capabilities tuple cannot be modified."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        fleet.ships.append(make_ship_with_ability("Yard Ship", "fleet_space_yard"))

        info = FleetInfo.from_fleet(fleet)

        # Tuple should be immutable
        with pytest.raises(TypeError):
            info.capabilities[0] = "Modified"
