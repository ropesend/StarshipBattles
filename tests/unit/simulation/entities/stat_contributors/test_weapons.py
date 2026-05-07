"""
Unit tests for the weapons / targeting stat contributor.

The contributor stores ``ship.baseline_to_hit_offense`` and returns the ECM
score so the calculator can compose ``total_defense_score``. We patch
``get_ability_total`` to drive contributor logic without setting up a full
ability registry.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.simulation.entities.stat_contributors import weapons


class TestAggregateTargetingScores:
    def test_returns_ecm_score_and_stores_offense(self):
        ship = MagicMock()

        with patch(
            "game.simulation.entities.stat_contributors.weapons.get_ability_total"
        ) as mock_total:
            mock_total.side_effect = lambda pool, name: {
                "ToHitDefenseModifier": 1.5,
                "ToHitAttackModifier": 0.75,
            }[name]
            ecm = weapons.aggregate_targeting_scores(ship, [MagicMock()])

        assert ecm == 1.5
        assert ship.baseline_to_hit_offense == 0.75

    def test_bool_payload_coerced_to_zero(self):
        """Legacy guard: get_ability_total may return False when no contributor."""
        ship = MagicMock()

        with patch(
            "game.simulation.entities.stat_contributors.weapons.get_ability_total"
        ) as mock_total:
            mock_total.return_value = False
            ecm = weapons.aggregate_targeting_scores(ship, [])

        assert ecm == 0.0
        assert ship.baseline_to_hit_offense == 0.0

    def test_zero_returned_passes_through_unchanged(self):
        ship = MagicMock()

        with patch(
            "game.simulation.entities.stat_contributors.weapons.get_ability_total"
        ) as mock_total:
            mock_total.return_value = 0.0
            ecm = weapons.aggregate_targeting_scores(ship, [])

        assert ecm == 0.0
        assert ship.baseline_to_hit_offense == 0.0
