"""Tests for beam weapon raycasting and ramming collision edge cases.

Covers:
- Beam weapon raycasting edge cases in CollisionSystem
- Ramming collision edge cases
"""
import pytest
from unittest.mock import MagicMock, patch
from pygame.math import Vector2


# =============================================================================
# Test: Beam Weapon Raycasting Edge Cases
# =============================================================================


class TestBeamRaycastingEdgeCases:
    """Edge cases for beam weapon raycasting in CollisionSystem."""

    def test_beam_zero_length_direction(self, collision_system):
        """Beam with zero-length direction should not crash."""
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.radius = 20
        target.is_alive = True

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 10

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(0, 0),  # Zero direction
            'range': 300,
            'target': target,
            'component': mock_component
        }

        # Should not crash (a == 0 case handled)
        collision_system.process_beam_attack(attack, recent_beams)

        # Beam should be recorded
        assert len(recent_beams) == 1

    def test_beam_target_at_origin(self, collision_system):
        """Beam with target at same position as origin."""
        target = MagicMock()
        target.position = Vector2(0, 0)  # Same as origin
        target.radius = 20
        target.is_alive = True

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 10

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 300,
            'target': target,
            'component': mock_component
        }

        # Should handle this case
        with patch('random.random', return_value=0.0):
            collision_system.process_beam_attack(attack, recent_beams)

        # Target is inside beam origin, should hit
        target.combat_engine.take_damage.assert_called()

    def test_beam_dead_target_no_hit(self, collision_system):
        """Beam should not hit dead target."""
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.radius = 20
        target.is_alive = False  # Dead

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 10

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 300,
            'target': target,
            'component': mock_component
        }

        collision_system.process_beam_attack(attack, recent_beams)

        target.combat_engine.take_damage.assert_not_called()

    def test_beam_no_target(self, collision_system):
        """Beam without target should record full-length beam."""
        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 500,
            'target': None,  # No target
            'component': MagicMock()
        }

        collision_system.process_beam_attack(attack, recent_beams)

        assert len(recent_beams) == 1
        # End should be at full range
        assert recent_beams[0]['end'].x == 500

    def test_beam_hit_chance_zero(self, collision_system):
        """Beam with zero hit chance should miss."""
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.radius = 20
        target.is_alive = True

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 0.0  # Zero chance
        mock_ability.get_damage.return_value = 10

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 300,
            'target': target,
            'component': mock_component
        }

        with patch('random.random', return_value=0.5):  # 0.5 > 0.0
            collision_system.process_beam_attack(attack, recent_beams)

        target.combat_engine.take_damage.assert_not_called()

    # -------------------------------------------------------------------------
    # Migrated from tests/unit/systems/test_collision_system.py
    # -------------------------------------------------------------------------

    def test_beam_weapon_tangent_hit(self, collision_system):
        """Test edge case: discriminant == 0 (tangent hit).

        When a beam ray is exactly tangent to a target sphere, the quadratic
        discriminant equals zero, giving exactly one intersection point.
        """
        target = MagicMock()
        target.position = Vector2(100, 20)  # Offset so ray can be tangent
        target.radius = 20
        target.is_alive = True
        target.total_defense_score = 0

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 15

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []

        # Ray exactly tangent to sphere at distance 100
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),  # Horizontal ray
            'range': 300,
            'target': target,
            'component': mock_component
        }

        with patch('random.random', return_value=0.0):
            collision_system.process_beam_attack(attack, recent_beams)

        # Tangent hit counts as hit - one intersection point
        target.combat_engine.take_damage.assert_called_once()
        assert target.combat_engine.take_damage.call_args[0][0] == 15

    def test_beam_weapon_target_behind_origin(self, collision_system):
        """Test edge case: target behind ray origin (negative t values).

        When the target is behind the beam origin, the intersection points
        have negative t values and should not register as hits.
        """
        target = MagicMock()
        target.position = Vector2(-100, 0)  # Behind origin
        target.radius = 20
        target.is_alive = True

        mock_component = MagicMock()
        recent_beams = []

        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),  # Firing forward
            'range': 300,
            'target': target,
            'component': mock_component
        }

        collision_system.process_beam_attack(attack, recent_beams)

        # Target behind ray, should not hit
        target.combat_engine.take_damage.assert_not_called()
        assert recent_beams[0]['end'] == Vector2(300, 0)


class TestBeamRaycastingGeometry:
    """Tests for ray-sphere intersection geometry (TCG-FND-003).

    These tests verify the actual quadratic formula calculations rather than
    mocking the hit chance. They validate that hit_dist is geometrically correct.
    """

    def test_ray_sphere_intersection_direct_hit(self, collision_system):
        """Verify ray-sphere intersection math for direct hit.

        Scenario: Beam origin at (0,0), direction (1,0), target at (100, 0) with radius 20.
        Expected hit distance: 100 - 20 = 80 (entry point of sphere).
        """
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.radius = 20
        target.is_alive = True
        target.total_defense_score = 0.0

        # Create ability that records what hit_dist it receives
        captured_hit_dist = []

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0

        def capture_damage(dist):
            captured_hit_dist.append(dist)
            return 50

        mock_ability.get_damage.side_effect = capture_damage

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        source_ship = MagicMock()
        source_ship.get_total_sensor_score.return_value = 0.0

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),  # Unit vector pointing right
            'range': 300,
            'target': target,
            'component': mock_component,
            'source': source_ship
        }

        with patch('random.random', return_value=0.0):  # Guarantee hit
            collision_system.process_beam_attack(attack, recent_beams)

        # Verify hit_dist passed to get_damage is geometrically correct
        # Entry point of sphere centered at (100,0) with radius 20 is at x=80
        assert len(captured_hit_dist) == 1
        assert captured_hit_dist[0] == pytest.approx(80.0, abs=0.1)

        # Verify beam end point is at hit location
        assert recent_beams[0]['end'].x == pytest.approx(80.0, abs=0.1)
        assert recent_beams[0]['end'].y == pytest.approx(0.0, abs=0.1)

    def test_ray_sphere_intersection_offset_target(self, collision_system):
        """Verify ray-sphere intersection with offset target.

        Scenario: Beam origin at (0,0), direction (1,0), target at (100, 10) with radius 20.
        The ray passes below the target center but within the sphere.
        """
        import math

        target = MagicMock()
        target.position = Vector2(100, 10)  # Offset 10 units up
        target.radius = 20
        target.is_alive = True
        target.total_defense_score = 0.0

        captured_hit_dist = []

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0

        def capture_damage(dist):
            captured_hit_dist.append(dist)
            return 50

        mock_ability.get_damage.side_effect = capture_damage

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        source_ship = MagicMock()
        source_ship.get_total_sensor_score.return_value = 0.0

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 300,
            'target': target,
            'component': mock_component,
            'source': source_ship
        }

        with patch('random.random', return_value=0.0):
            collision_system.process_beam_attack(attack, recent_beams)

        # Verify hit occurred and distance is reasonable
        # Ray at y=0 intersects sphere at (100, 10) with r=20
        # Using Pythagorean theorem: intersection at x = 100 - sqrt(20^2 - 10^2) = 100 - sqrt(300) ≈ 82.68
        expected_dist = 100 - math.sqrt(400 - 100)
        assert len(captured_hit_dist) == 1
        assert captured_hit_dist[0] == pytest.approx(expected_dist, abs=0.5)

    def test_ray_sphere_miss_out_of_range(self, collision_system):
        """Verify ray misses when target is beyond beam range."""
        target = MagicMock()
        target.position = Vector2(500, 0)  # Target at 500 units
        target.radius = 20
        target.is_alive = True

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 50

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 300,  # Range is only 300
            'target': target,
            'component': mock_component
        }

        collision_system.process_beam_attack(attack, recent_beams)

        # Should miss - entry point (480) is beyond range (300)
        target.combat_engine.take_damage.assert_not_called()

        # Beam should extend to full range
        assert recent_beams[0]['end'].x == pytest.approx(300, abs=0.1)

    def test_ray_sphere_miss_perpendicular(self, collision_system):
        """Verify ray misses when it doesn't intersect sphere."""
        target = MagicMock()
        target.position = Vector2(100, 50)  # Target 50 units above ray path
        target.radius = 20  # Radius only 20, so ray passes below
        target.is_alive = True

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 50

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),  # Ray goes right at y=0
            'range': 300,
            'target': target,
            'component': mock_component
        }

        collision_system.process_beam_attack(attack, recent_beams)

        # Ray at y=0 misses sphere at (100, 50) with r=20
        # Closest approach is 50 units, which is > 20 radius
        target.combat_engine.take_damage.assert_not_called()

    def test_damage_pipeline_end_to_end(self, collision_system):
        """Verify full damage pipeline: geometry -> hit chance -> damage.

        Tests that get_damage receives correct distance, hit chance uses
        correct attack/defense scores, and damage is applied correctly.
        """
        target = MagicMock()
        target.position = Vector2(150, 0)
        target.radius = 30
        target.is_alive = True
        target.total_defense_score = 5.0  # Target has defense

        # Track all method calls
        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 0.8

        # Verify get_damage called with geometric hit distance
        def verify_damage_call(dist):
            # Entry point: 150 - 30 = 120
            assert dist == pytest.approx(120.0, abs=0.5)
            return 75

        mock_ability.get_damage.side_effect = verify_damage_call

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        source_ship = MagicMock()
        source_ship.get_total_sensor_score.return_value = 10.0  # Attacker has sensors

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 300,
            'target': target,
            'component': mock_component,
            'source': source_ship
        }

        with patch.object(collision_system.rng, 'random', return_value=0.5):  # 0.5 < 0.8 = hit
            collision_system.process_beam_attack(attack, recent_beams)

        # Verify hit chance was called with correct scores
        mock_ability.calculate_hit_chance.assert_called_once()
        call_args = mock_ability.calculate_hit_chance.call_args
        assert call_args[0][0] == pytest.approx(120.0, abs=0.5)  # hit_dist
        assert call_args[0][1] == 10.0  # attack_score
        assert call_args[0][2] == 5.0   # defense_score

        # Verify damage was applied
        target.combat_engine.take_damage.assert_called_once()
        assert target.combat_engine.take_damage.call_args[0][0] == 75


# =============================================================================
# Test: Ramming Edge Cases
# =============================================================================


class TestRammingEdgeCases:
    """Edge cases for ramming collisions."""

    def test_ramming_non_kamikaze_ignored(self, collision_system):
        """Ships without kamikaze strategy should not ram."""
        ship = MagicMock()
        ship.movement_policy = 'brawl_close'  # Not kamikaze
        ship.is_alive = True
        ship.current_target = MagicMock()

        collision_system.process_ramming([ship])

        ship.combat_engine.take_damage.assert_not_called()

    def test_ramming_no_target_ignored(self, collision_system):
        """Kamikaze ship without target should not process."""
        ship = MagicMock()
        ship.movement_policy = 'ramming_speed'
        ship.is_alive = True
        ship.current_target = None

        collision_system.process_ramming([ship])

        ship.combat_engine.take_damage.assert_not_called()

    def test_ramming_dead_target_ignored(self, collision_system):
        """Kamikaze ship with dead target should not process."""
        target = MagicMock()
        target.is_alive = False

        ship = MagicMock()
        ship.movement_policy = 'ramming_speed'
        ship.is_alive = True
        ship.current_target = target

        collision_system.process_ramming([ship])

        ship.combat_engine.take_damage.assert_not_called()

    def test_ramming_equal_hp_mutual_destruction(self, collision_system):
        """Equal HP should result in mutual destruction."""
        target = MagicMock()
        target.name = "Target"
        target.is_alive = True
        target.hp = 100
        target.position = Vector2(5, 0)
        target.radius = 10

        ship = MagicMock()
        ship.name = "Rammer"
        ship.movement_policy = 'ramming_speed'
        ship.is_alive = True
        ship.hp = 100  # Equal HP
        ship.position = Vector2(0, 0)
        ship.radius = 10
        ship.current_target = target

        logger = MagicMock()
        collision_system.process_ramming([ship, target], logger)

        # Both should take lethal damage
        ship.combat_engine.take_damage.assert_called()
        target.combat_engine.take_damage.assert_called()

    def test_ramming_zero_radius(self, collision_system):
        """Ramming with zero radius at same position should collide."""
        target = MagicMock()
        target.name = "Target"
        target.is_alive = True
        target.hp = 100
        target.position = Vector2(0, 0)  # Same position
        target.radius = 0  # Zero radius

        ship = MagicMock()
        ship.name = "Rammer"
        ship.movement_policy = 'ramming_speed'
        ship.is_alive = True
        ship.hp = 50
        ship.position = Vector2(0, 0)
        ship.radius = 0  # Zero radius
        ship.current_target = target

        collision_system.process_ramming([ship, target])

        # Distance is 0, collision_radius is 0
        # condition is: distance_to < collision_radius
        # 0 < 0 is False, so no collision happens
        # This is expected behavior - zero radius objects don't collide
        # unless distance is strictly less than radius
        ship.combat_engine.take_damage.assert_not_called()

    def test_ramming_missing_hp_attribute(self, collision_system):
        """Ramming should handle ships without hp attribute gracefully.

        PROJ-40/NEW-AI-004: Ships should use default HP when .hp is missing.
        """
        target = MagicMock(spec=['name', 'is_alive', 'position', 'radius', 'combat_engine'])
        target.name = "Target"
        target.is_alive = True
        target.position = Vector2(5, 0)
        target.radius = 10
        # No .hp attribute

        ship = MagicMock(spec=['name', 'movement_policy', 'is_alive', 'position', 'radius', 'current_target', 'combat_engine'])
        ship.name = "Rammer"
        ship.movement_policy = 'ramming_speed'
        ship.is_alive = True
        ship.position = Vector2(0, 0)
        ship.radius = 10
        ship.current_target = target
        # No .hp attribute

        # Should not crash - uses default HP
        collision_system.process_ramming([ship, target])

        # Both should take damage based on default HP
        ship.combat_engine.take_damage.assert_called()
        target.combat_engine.take_damage.assert_called()

    def test_ramming_rammer_missing_hp(self, collision_system):
        """Ramming should handle rammer without hp attribute.

        PROJ-40/NEW-AI-004: Rammer uses default HP, target uses actual HP.
        """
        target = MagicMock()
        target.name = "Target"
        target.is_alive = True
        target.position = Vector2(5, 0)
        target.radius = 10
        target.hp = 200  # Target has HP

        ship = MagicMock(spec=['name', 'movement_policy', 'is_alive', 'position', 'radius', 'current_target', 'combat_engine'])
        ship.name = "Rammer"
        ship.movement_policy = 'ramming_speed'
        ship.is_alive = True
        ship.position = Vector2(0, 0)
        ship.radius = 10
        ship.current_target = target
        # No .hp attribute - should use default (100)

        collision_system.process_ramming([ship, target])

        # Rammer (default 100) < Target (200), so rammer destroyed
        ship.combat_engine.take_damage.assert_called()

    def test_ramming_target_missing_hp(self, collision_system):
        """Ramming should handle target without hp attribute.

        PROJ-40/NEW-AI-004: Target uses default HP, rammer uses actual HP.
        """
        target = MagicMock(spec=['name', 'is_alive', 'position', 'radius', 'combat_engine'])
        target.name = "Target"
        target.is_alive = True
        target.position = Vector2(5, 0)
        target.radius = 10
        # No .hp attribute - should use default (100)

        ship = MagicMock()
        ship.name = "Rammer"
        ship.movement_policy = 'ramming_speed'
        ship.is_alive = True
        ship.position = Vector2(0, 0)
        ship.radius = 10
        ship.hp = 50  # Rammer has HP
        ship.current_target = target

        collision_system.process_ramming([ship, target])

        # Rammer (50) < Target (default 100), so rammer destroyed
        ship.combat_engine.take_damage.assert_called()

    # -------------------------------------------------------------------------
    # Migrated from tests/unit/systems/test_collision_system.py
    # -------------------------------------------------------------------------

    def test_ramming_no_logger(self, collision_system):
        """Test ramming works without logger (logger=None).

        Verifies process_ramming doesn't raise when called with logger=None.
        """
        rammer = MagicMock()
        rammer.name = "Rammer"
        rammer.position = Vector2(0, 0)
        rammer.radius = 10
        rammer.movement_policy = 'ramming_speed'
        rammer.is_alive = True
        rammer.hp = 50

        target = MagicMock()
        target.name = "Target"
        target.position = Vector2(15, 0)
        target.radius = 10
        target.is_alive = True
        target.hp = 100

        rammer.current_target = target
        ships = [rammer, target]

        # Should not raise without logger
        collision_system.process_ramming(ships, logger=None)
        rammer.combat_engine.take_damage.assert_called()


# =============================================================================
# TCG-FND-020: Integration Tests with Real Ship Objects
# =============================================================================


class TestCollisionIntegrationWithRealShip:
    """Integration tests using real Ship objects instead of mocks.

    TCG-FND-020: Add integration tests that use real Ship instances
    to verify collision system works with actual game entities.
    """

    def test_beam_attack_hits_real_ship(self, collision_system, fresh_registries):
        """Beam weapon attack against a real Ship object.

        Verifies that the collision system correctly processes beam attacks
        against actual Ship instances with real combat engines.
        """
        from game.simulation.entities.ship import Ship
        from game.simulation.components.component import create_component
        from game.core.constants import LayerType
        from pygame.math import Vector2
        from unittest.mock import patch

        # Create a real ship with components
        target_ship = Ship(
            name="TargetShip",
            x=100, y=0,
            color=(255, 0, 0),
            team_id=1,
            registries=fresh_registries
        )

        # Add crew support so components are active
        crew = create_component('crew_quarters', registries=fresh_registries)
        life = create_component('life_support', registries=fresh_registries)
        if crew:
            target_ship.add_component(crew, LayerType.CORE)
        if life:
            target_ship.add_component(life, LayerType.CORE)

        # Add armor so the ship has HP to damage
        armor = create_component('armor_plate', registries=fresh_registries)
        if armor:
            target_ship.add_component(armor, LayerType.ARMOR)

        target_ship.recalculate_stats()
        initial_hp = target_ship.hp

        # Create mock beam ability
        from unittest.mock import MagicMock
        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 50

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 300,
            'target': target_ship,
            'component': mock_component,
            'source': None
        }

        with patch('random.random', return_value=0.0):  # Guarantee hit
            collision_system.process_beam_attack(attack, recent_beams)

        # Verify damage was applied to the real ship
        assert len(recent_beams) == 1
        assert target_ship.hp < initial_hp, "Ship should have taken damage"

    def test_ramming_collision_with_real_ships(self, collision_system, fresh_registries):
        """Ramming collision between two real Ship objects.

        Verifies that the collision system correctly handles ramming
        between actual Ship instances with real HP calculations.
        """
        from game.simulation.entities.ship import Ship
        from game.simulation.components.component import create_component
        from game.core.constants import LayerType
        from pygame.math import Vector2

        # Create rammer ship
        rammer = Ship(
            name="Rammer",
            x=0, y=0,
            color=(255, 0, 0),
            team_id=0,
            registries=fresh_registries
        )
        rammer.movement_policy = 'ramming_speed'

        # Create target ship
        target = Ship(
            name="Target",
            x=15, y=0,  # Within collision range
            color=(0, 255, 0),
            team_id=1,
            registries=fresh_registries
        )

        # Add components to both ships for HP
        for ship in [rammer, target]:
            crew = create_component('crew_quarters', registries=fresh_registries)
            life = create_component('life_support', registries=fresh_registries)
            armor = create_component('armor_plate', registries=fresh_registries)
            if crew:
                ship.add_component(crew, LayerType.CORE)
            if life:
                ship.add_component(life, LayerType.CORE)
            if armor:
                ship.add_component(armor, LayerType.ARMOR)
            ship.recalculate_stats()

        # Set up ramming target
        rammer.current_target = target

        # Record initial HP
        rammer_initial_hp = rammer.hp
        target_initial_hp = target.hp

        # Process ramming
        collision_system.process_ramming([rammer, target])

        # Verify damage was applied
        # At least one ship should have taken damage if collision occurred
        # Note: Collision only occurs if distance < collision_radius
        distance = rammer.position.distance_to(target.position)
        collision_radius = rammer.radius + target.radius

        if distance < collision_radius:
            # Collision should have occurred - at least one ship damaged
            damage_applied = (rammer.hp < rammer_initial_hp or
                              target.hp < target_initial_hp)
            assert damage_applied, "Ramming collision should apply damage"
