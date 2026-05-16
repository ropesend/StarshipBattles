"""PROJ-FMS-A Phase 4: vehicle-class ``signature_bonus`` -> ``total_defense_score``.

Verifies that a mine with class-level signature_bonus=3 gets that bonus
included in its total defense score, and ships (default 0) don't change.
"""
from __future__ import annotations

import pytest

from game.simulation.entities.ship import Ship


class TestSignatureBonusWiring:
    def test_mine_class_has_signature_bonus(self, fresh_registries):
        ship = Ship(
            "TestMine", 0, 0, (255, 255, 255),
            ship_class="Mine (Medium)",
            registries=fresh_registries,
        )
        ship.recalculate_stats()
        # vehicleclasses.json sets signature_bonus=3 for all mine tiers.
        assert ship.signature_bonus == pytest.approx(3.0)
        # Total defense score must include it (size + maneuver + ecm +
        # signature). For an empty mine (no components), maneuver/ecm
        # contribute negligibly; signature_bonus is on top of the base.
        # Just assert the bonus flowed through into the total.
        # The exact value depends on size_score for a tiny radius; we
        # compare the same class with and without bonus by writing the
        # signature_bonus through the registry.

    def test_ship_default_signature_bonus_is_zero(self, fresh_registries):
        ship = Ship(
            "TestCruiser", 0, 0, (255, 255, 255),
            ship_class="Cruiser",
            registries=fresh_registries,
        )
        ship.recalculate_stats()
        assert ship.signature_bonus == pytest.approx(0.0)

    def test_mine_defense_score_includes_bonus(self, fresh_registries):
        """Mutating the registry's signature_bonus changes total_defense_score
        by the same delta — proves the wiring."""
        ship_a = Ship(
            "MineA", 0, 0, (255, 255, 255),
            ship_class="Mine (Medium)",
            registries=fresh_registries,
        )
        ship_a.recalculate_stats()
        score_a = ship_a.total_defense_score

        # Mutate the registry copy, rebuild a fresh ship of the same class.
        fresh_registries.vehicle_classes["Mine (Medium)"]["signature_bonus"] = 10.0
        ship_b = Ship(
            "MineB", 0, 0, (255, 255, 255),
            ship_class="Mine (Medium)",
            registries=fresh_registries,
        )
        ship_b.recalculate_stats()
        score_b = ship_b.total_defense_score

        # Delta in total_defense_score must equal delta in signature_bonus
        # (10 - 3 = 7) — proves the bonus was the only changing term.
        assert score_b - score_a == pytest.approx(7.0)
