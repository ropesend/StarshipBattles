"""
Tests for fleet bonus attributes declared on Ship.

PROJ-243 Phase 1: Verify that fleet_attack_bonus and fleet_defense_bonus
are declared in Ship.__init__ with default 0.0, eliminating the undeclared
attribute risk when FleetAuraManager has not yet run.
"""
import pytest

from game.simulation.entities.ship import Ship


class TestFleetBonusAttributeDeclaration:
    """Verify fleet bonus attributes exist on freshly constructed ships.

    PROJ-495 T3.7: the four original tests covered (default + set/read) ×
    (fleet_attack_bonus, fleet_defense_bonus). Parametrized on
    ``attr_name`` (× the default test) and ``(attr_name, new_value)``
    (× the set/read test).
    """

    @pytest.mark.parametrize(
        "attr_name",
        ["fleet_attack_bonus", "fleet_defense_bonus"],
    )
    def test_fleet_bonus_default_is_zero(self, fresh_registries, attr_name: str) -> None:
        """A freshly constructed Ship has the fleet bonus attr defaulted to 0.0."""
        ship = Ship(
            name="TestShip",
            x=0, y=0,
            color=(255, 255, 255),
            registries=fresh_registries,
        )
        assert getattr(ship, attr_name) == 0.0

    @pytest.mark.parametrize(
        "attr_name,new_value",
        [
            ("fleet_attack_bonus", 3.5),
            ("fleet_defense_bonus", 2.7),
        ],
    )
    def test_fleet_bonus_can_be_set_and_read(
        self, fresh_registries, attr_name: str, new_value: float
    ) -> None:
        """A fleet bonus attr can be set to a float and read back."""
        ship = Ship(
            name="TestShip",
            x=0, y=0,
            color=(255, 255, 255),
            registries=fresh_registries,
        )
        setattr(ship, attr_name, new_value)
        assert getattr(ship, attr_name) == new_value
