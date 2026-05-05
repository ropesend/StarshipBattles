"""
Regression test for beam weapon hit tracking.

Beam weapons were incorrectly counting every shot as a hit because
shots_hit was incremented at fire time (weapon_firing_system.py)
rather than at accuracy-check time (collision.py).

This test verifies that shots_hit is only incremented when the
accuracy roll succeeds, not when the beam is fired.
"""

import pytest
from unittest.mock import MagicMock, patch
import random


class TestBeamHitTracking:
    """Verify beam weapons track hits correctly based on accuracy."""

    def test_beam_miss_does_not_increment_shots_hit(self, fresh_registries):
        """A beam that misses (fails accuracy roll) should not count as a hit."""
        from game.simulation.entities.ship import Ship
        from game.engine.collision import CollisionSystem

        # Create two ships
        attacker = Ship("Attacker", 0, 0, (255, 0, 0), team_id=0,
                       ship_class="Escort", registries=fresh_registries)
        target = Ship("Target", 5000, 0, (0, 0, 255), team_id=1,
                      ship_class="Escort", registries=fresh_registries)
        target.recalculate_stats()

        # Create a mock beam component with tracking
        beam_comp = MagicMock()
        beam_comp.shots_fired = 1  # Already fired
        beam_comp.shots_hit = 0    # No hits yet

        beam_ab = MagicMock()
        beam_ab.calculate_hit_chance.return_value = 0.0  # 0% chance = guaranteed miss
        beam_ab.get_damage.return_value = 100
        beam_comp.get_ability.return_value = beam_ab

        # Create beam attack
        from game.core.math import Vector2
        from game.simulation.combat.attack_contract import BeamResolution
        attack = BeamResolution(
            source=attacker,
            component=beam_comp,
            target=target,
            damage=100,
            range=10000,
            origin=Vector2(0, 0),
            direction=Vector2(1, 0),
            hit=True,
        )

        # Process the beam attack with a rigged RNG (always rolls > 0)
        collision = CollisionSystem(rng=random.Random(42))
        collision.process_beam_attack(attack, [])

        # shots_hit should NOT have been incremented (beam missed)
        assert beam_comp.shots_hit == 0, \
            f"Beam miss should not increment shots_hit, got {beam_comp.shots_hit}"

    def test_beam_hit_increments_shots_hit(self, fresh_registries):
        """A beam that hits (passes accuracy roll) should count as a hit."""
        from game.simulation.entities.ship import Ship
        from game.engine.collision import CollisionSystem

        attacker = Ship("Attacker", 0, 0, (255, 0, 0), team_id=0,
                       ship_class="Escort", registries=fresh_registries)
        target = Ship("Target", 100, 0, (0, 0, 255), team_id=1,
                      ship_class="Escort", registries=fresh_registries)
        target.recalculate_stats()

        beam_comp = MagicMock()
        beam_comp.shots_fired = 1
        beam_comp.shots_hit = 0

        beam_ab = MagicMock()
        beam_ab.calculate_hit_chance.return_value = 1.0  # 100% chance = guaranteed hit
        beam_ab.get_damage.return_value = 100
        beam_comp.get_ability.return_value = beam_ab

        from game.core.math import Vector2
        from game.simulation.combat.attack_contract import BeamResolution
        attack = BeamResolution(
            source=attacker,
            component=beam_comp,
            target=target,
            damage=100,
            range=10000,
            origin=Vector2(0, 0),
            direction=Vector2(1, 0),
            hit=True,
        )

        collision = CollisionSystem(rng=random.Random(42))
        collision.process_beam_attack(attack, [])

        assert beam_comp.shots_hit == 1, \
            f"Beam hit should increment shots_hit, got {beam_comp.shots_hit}"
