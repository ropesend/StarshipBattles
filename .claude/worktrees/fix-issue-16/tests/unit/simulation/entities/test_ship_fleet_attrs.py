"""
Tests for fleet bonus attributes declared on Ship.

PROJ-243 Phase 1: Verify that fleet_attack_bonus and fleet_defense_bonus
are declared in Ship.__init__ with default 0.0, eliminating the undeclared
attribute risk when FleetAuraManager has not yet run.
"""
import pytest

from game.simulation.entities.ship import Ship


class TestFleetBonusAttributeDeclaration:
    """Verify fleet bonus attributes exist on freshly constructed ships."""

    def test_fleet_attack_bonus_default_is_zero(self, fresh_registries):
        """A freshly constructed Ship has fleet_attack_bonus == 0.0."""
        ship = Ship(
            name="TestShip",
            x=0, y=0,
            color=(255, 255, 255),
            registries=fresh_registries,
        )
        assert ship.fleet_attack_bonus == 0.0

    def test_fleet_defense_bonus_default_is_zero(self, fresh_registries):
        """A freshly constructed Ship has fleet_defense_bonus == 0.0."""
        ship = Ship(
            name="TestShip",
            x=0, y=0,
            color=(255, 255, 255),
            registries=fresh_registries,
        )
        assert ship.fleet_defense_bonus == 0.0

    def test_fleet_attack_bonus_can_be_set_and_read(self, fresh_registries):
        """fleet_attack_bonus can be set to a float and read back."""
        ship = Ship(
            name="TestShip",
            x=0, y=0,
            color=(255, 255, 255),
            registries=fresh_registries,
        )
        ship.fleet_attack_bonus = 3.5
        assert ship.fleet_attack_bonus == 3.5

    def test_fleet_defense_bonus_can_be_set_and_read(self, fresh_registries):
        """fleet_defense_bonus can be set to a float and read back."""
        ship = Ship(
            name="TestShip",
            x=0, y=0,
            color=(255, 255, 255),
            registries=fresh_registries,
        )
        ship.fleet_defense_bonus = 2.7
        assert ship.fleet_defense_bonus == 2.7
