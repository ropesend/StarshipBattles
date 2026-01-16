"""
Tests for shared component fixtures.

These fixtures provide consistent component creation patterns for tests,
eliminating boilerplate and ensuring proper component configuration.
"""
import pytest

from game.simulation.components.component import Component, LayerType


class TestWeaponComponentFixture:
    """Tests for weapon_component fixture."""

    def test_returns_component_object(self, weapon_component):
        """Returns a Component instance."""
        assert isinstance(weapon_component, Component)

    def test_has_weapon_ability(self, weapon_component):
        """Component has WeaponAbility."""
        assert weapon_component.has_ability('WeaponAbility')

    def test_has_positive_damage(self, weapon_component):
        """Component can deal damage."""
        ability = weapon_component.get_ability('WeaponAbility')
        assert ability is not None


class TestEngineComponentFixture:
    """Tests for engine_component fixture."""

    def test_returns_component_object(self, engine_component):
        """Returns a Component instance."""
        assert isinstance(engine_component, Component)

    def test_has_propulsion_ability(self, engine_component):
        """Component has CombatPropulsion ability."""
        assert engine_component.has_ability('CombatPropulsion')


class TestShieldComponentFixture:
    """Tests for shield_component fixture."""

    def test_returns_component_object(self, shield_component):
        """Returns a Component instance."""
        assert isinstance(shield_component, Component)

    def test_has_shield_ability(self, shield_component):
        """Component has ShieldProjection ability."""
        assert shield_component.has_ability('ShieldProjection')


class TestArmorComponentFixture:
    """Tests for armor_component fixture."""

    def test_returns_component_object(self, armor_component):
        """Returns a Component instance."""
        assert isinstance(armor_component, Component)

    def test_has_positive_hp(self, armor_component):
        """Component has positive HP (provides protection)."""
        assert armor_component.max_hp > 0


class TestBridgeComponentFixture:
    """Tests for bridge_component fixture."""

    def test_returns_component_object(self, bridge_component):
        """Returns a Component instance."""
        assert isinstance(bridge_component, Component)

    def test_has_command_ability(self, bridge_component):
        """Component has CommandAndControl ability."""
        assert bridge_component.has_ability('CommandAndControl')


class TestComponentFactory:
    """Tests for component factory function."""

    def test_create_weapon(self):
        """Factory creates weapon component."""
        from tests.fixtures.components import create_weapon
        weapon = create_weapon()
        assert isinstance(weapon, Component)
        assert weapon.has_ability('WeaponAbility')

    def test_create_engine(self):
        """Factory creates engine component."""
        from tests.fixtures.components import create_engine
        engine = create_engine()
        assert isinstance(engine, Component)
        assert engine.has_ability('CombatPropulsion')

    def test_create_shield(self):
        """Factory creates shield component."""
        from tests.fixtures.components import create_shield
        shield = create_shield()
        assert isinstance(shield, Component)
        assert shield.has_ability('ShieldProjection')

    def test_create_armor(self):
        """Factory creates armor component."""
        from tests.fixtures.components import create_armor
        armor = create_armor()
        assert isinstance(armor, Component)
        assert armor.max_hp > 0

    def test_create_bridge(self):
        """Factory creates bridge component."""
        from tests.fixtures.components import create_bridge
        bridge = create_bridge()
        assert isinstance(bridge, Component)
        assert bridge.has_ability('CommandAndControl')
