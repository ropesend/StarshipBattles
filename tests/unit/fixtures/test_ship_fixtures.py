"""
Tests for shared ship fixtures.

These fixtures provide consistent ship creation patterns for tests,
eliminating boilerplate and ensuring test isolation.
"""
import pytest
from pathlib import Path

from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component, LayerType


class TestEmptyShipFixture:
    """Tests for empty_ship fixture."""

    def test_returns_ship_object(self, empty_ship):
        """Returns a Ship instance."""
        assert isinstance(empty_ship, Ship)

    def test_has_name(self, empty_ship):
        """Ship has a name."""
        assert empty_ship.name is not None
        assert len(empty_ship.name) > 0

    def test_has_hull_only(self, empty_ship):
        """Ship has only the auto-equipped hull component."""
        components = empty_ship.get_all_components()
        # Hull is auto-equipped by Ship.__init__
        assert len(components) == 1
        assert components[0].layer_assigned == LayerType.HULL

    def test_has_layers_structure(self, empty_ship):
        """Ship has the layers dict structure."""
        assert hasattr(empty_ship, 'layers')
        assert isinstance(empty_ship.layers, dict)


class TestBasicShipFixture:
    """Tests for basic_ship fixture."""

    def test_returns_ship_object(self, basic_ship):
        """Returns a Ship instance."""
        assert isinstance(basic_ship, Ship)

    def test_has_bridge(self, basic_ship):
        """Ship has a bridge (CommandAndControl ability)."""
        bridges = basic_ship.get_components_by_ability('CommandAndControl')
        assert len(bridges) >= 1

    def test_has_engine(self, basic_ship):
        """Ship has an engine (CombatPropulsion ability)."""
        engines = basic_ship.get_components_by_ability('CombatPropulsion')
        assert len(engines) >= 1

    def test_has_recalculated_stats(self, basic_ship):
        """Ship has recalculated stats."""
        # Should have max_hp set from components
        assert basic_ship.max_hp > 0


class TestArmedShipFixture:
    """Tests for armed_ship fixture."""

    def test_returns_ship_object(self, armed_ship):
        """Returns a Ship instance."""
        assert isinstance(armed_ship, Ship)

    def test_has_weapons(self, armed_ship):
        """Ship has at least one weapon."""
        weapons = armed_ship.get_components_by_ability('WeaponAbility')
        assert len(weapons) >= 1

    def test_has_bridge_and_engine(self, armed_ship):
        """Ship has bridge and engine (basic requirements)."""
        bridges = armed_ship.get_components_by_ability('CommandAndControl')
        engines = armed_ship.get_components_by_ability('CombatPropulsion')
        assert len(bridges) >= 1
        assert len(engines) >= 1

    def test_components_span_multiple_layers(self, armed_ship):
        """Components are in multiple layers."""
        layers_with_comps = set()
        for layer_type, comp in armed_ship.iter_components():
            layers_with_comps.add(layer_type)
        # Should have at least HULL, CORE, OUTER, ARMOR
        # HULL: auto-equipped hull
        # CORE: bridge
        # OUTER: engine, shield, weapons
        # ARMOR: armor plate
        assert len(layers_with_comps) >= 3


class TestShieldedShipFixture:
    """Tests for shielded_ship fixture."""

    def test_returns_ship_object(self, shielded_ship):
        """Returns a Ship instance."""
        assert isinstance(shielded_ship, Ship)

    def test_has_shield(self, shielded_ship):
        """Ship has at least one shield generator."""
        shields = shielded_ship.get_components_by_ability('ShieldProjection')
        assert len(shields) >= 1

    def test_has_basic_components(self, shielded_ship):
        """Ship has basic components (bridge, engine)."""
        bridges = shielded_ship.get_components_by_ability('CommandAndControl')
        engines = shielded_ship.get_components_by_ability('CombatPropulsion')
        assert len(bridges) >= 1
        assert len(engines) >= 1


class TestFullyEquippedShipFixture:
    """Tests for fully_equipped_ship fixture."""

    def test_returns_ship_object(self, fully_equipped_ship):
        """Returns a Ship instance."""
        assert isinstance(fully_equipped_ship, Ship)

    def test_has_weapons(self, fully_equipped_ship):
        """Ship has weapons."""
        weapons = fully_equipped_ship.get_components_by_ability('WeaponAbility')
        assert len(weapons) >= 1

    def test_has_shields(self, fully_equipped_ship):
        """Ship has shields."""
        shields = fully_equipped_ship.get_components_by_ability('ShieldProjection')
        assert len(shields) >= 1

    def test_has_bridge_and_engine(self, fully_equipped_ship):
        """Ship has bridge and engine."""
        bridges = fully_equipped_ship.get_components_by_ability('CommandAndControl')
        engines = fully_equipped_ship.get_components_by_ability('CombatPropulsion')
        assert len(bridges) >= 1
        assert len(engines) >= 1


class TestShipFixtureIsolation:
    """Tests that ship fixtures are properly isolated."""

    def test_empty_ship_is_fresh(self, empty_ship):
        """Each test gets a fresh empty_ship instance."""
        # Modify the ship
        empty_ship.name = "Modified"
        empty_ship.current_hp = 1
        # (Next test will verify it's fresh)

    def test_empty_ship_is_unmodified(self, empty_ship):
        """Empty ship is not affected by previous test."""
        assert empty_ship.name != "Modified"

    def test_basic_ship_is_fresh(self, basic_ship):
        """Each test gets a fresh basic_ship instance."""
        # Damage a component
        components = basic_ship.get_all_components()
        if components:
            components[0].current_hp = 0

    def test_basic_ship_is_unmodified(self, basic_ship):
        """Basic ship is not affected by previous test."""
        components = basic_ship.get_all_components()
        for comp in components:
            # All components should be at full HP
            assert comp.current_hp == comp.max_hp


class TestShipFactory:
    """Tests for the ship factory function."""

    def test_create_test_ship_returns_ship(self):
        """create_test_ship returns a Ship instance."""
        from tests.fixtures.ships import create_test_ship
        ship = create_test_ship()
        assert isinstance(ship, Ship)

    def test_create_test_ship_with_custom_name(self):
        """create_test_ship accepts custom name."""
        from tests.fixtures.ships import create_test_ship
        ship = create_test_ship(name="CustomName")
        assert ship.name == "CustomName"

    def test_create_test_ship_with_position(self):
        """create_test_ship accepts position."""
        from tests.fixtures.ships import create_test_ship
        ship = create_test_ship(x=100, y=200)
        assert ship.position.x == 100
        assert ship.position.y == 200

    def test_create_test_ship_with_team_id(self):
        """create_test_ship accepts team_id."""
        from tests.fixtures.ships import create_test_ship
        ship = create_test_ship(team_id=1)
        assert ship.team_id == 1
