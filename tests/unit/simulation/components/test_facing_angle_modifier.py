"""
Regression test for facing angle modifier on weapons.

The facing_angle modifier was not being applied to weapon abilities because
the recalculate() method had a guard that prevented the update.

This test verifies that:
1. A weapon with facing_angle modifier has the correct facing on the ability
2. The facing angle affects firing arc checks
"""

import pytest


class TestFacingAngleModifier:
    """Verify facing angle modifier applies to weapon abilities."""

    def test_facing_angle_modifier_applies_to_weapon(self, fresh_registries):
        """A weapon with facing_angle=180 modifier should face backwards."""
        from game.simulation.components.component import create_component

        laser = create_component('laser_cannon', registries=fresh_registries)
        laser.add_modifier('facing', 180.0)
        laser.recalculate_stats()

        beam_ab = laser.get_ability('BeamWeaponAbility')
        assert beam_ab is not None, "Laser should have BeamWeaponAbility"
        assert beam_ab.facing_angle == 180.0, \
            f"Expected facing_angle=180, got {beam_ab.facing_angle}"

    def test_facing_angle_zero_by_default(self, fresh_registries):
        """A weapon without facing modifier should face forward (0)."""
        from game.simulation.components.component import create_component

        laser = create_component('laser_cannon', registries=fresh_registries)
        laser.recalculate_stats()

        beam_ab = laser.get_ability('BeamWeaponAbility')
        assert beam_ab.facing_angle == 0.0, \
            f"Expected default facing_angle=0, got {beam_ab.facing_angle}"

    def test_facing_angle_on_ship_weapon(self, fresh_registries):
        """A weapon on a ship with facing modifier should have correct facing."""
        from game.simulation.entities.ship import Ship

        design = {
            'name': 'Test', 'ship_class': 'Escort', 'vehicle_type': 'Ship',
            'theme_id': 'Federation', 'team_id': 0, 'color': [255, 255, 255],
            'ai_strategy': 'standard_ranged',
            'layers': {
                'CORE': [{'id': 'bridge'}],
                'OUTER': [
                    {'id': 'laser_cannon', 'modifiers': [
                        {'id': 'facing', 'value': 180.0}
                    ]},
                ],
            },
            'resources': {'fuel': 0, 'energy': 0, 'ammo': 0},
        }

        ship = Ship.from_dict(design, registries=fresh_registries)
        ship.recalculate_stats()

        # Find the laser cannon and check its facing
        for lt, ld in ship.layers.items():
            for comp in ld.components:
                beam_ab = comp.get_ability('BeamWeaponAbility')
                if beam_ab:
                    assert beam_ab.facing_angle == 180.0, \
                        f"Expected facing=180 on {comp.name}, got {beam_ab.facing_angle}"
                    return

        pytest.fail("No BeamWeaponAbility found on ship")

    def test_facing_affects_firing_arc_check(self, fresh_registries):
        """A weapon facing 180° should NOT fire at targets in front."""
        from game.simulation.components.component import create_component
        from game.core.math import Vector2

        laser = create_component('laser_cannon', registries=fresh_registries)
        # Set facing to 180° (rear)
        laser.add_modifier('facing', 180.0)
        laser.recalculate_stats()

        beam_ab = laser.get_ability('BeamWeaponAbility')

        ship_pos = Vector2(0, 0)

        # Ship facing 0° (right), target directly ahead at (100, 0)
        # Weapon faces 180° (left), arc=1° — target at 0° is outside arc
        can_fire_forward = beam_ab.check_firing_solution(
            ship_pos=ship_pos,
            ship_angle=0.0,
            target_pos=Vector2(100, 0),  # directly ahead
        )
        assert not can_fire_forward, \
            "Weapon facing 180° should not fire at targets directly ahead"

        # Target directly behind at (-100, 0) — should be IN arc
        can_fire_rear = beam_ab.check_firing_solution(
            ship_pos=ship_pos,
            ship_angle=0.0,
            target_pos=Vector2(-100, 0),  # directly behind
        )
        assert can_fire_rear, \
            "Weapon facing 180° should fire at targets directly behind"
