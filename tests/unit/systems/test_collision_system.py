from unittest.mock import MagicMock, patch
from pygame.math import Vector2

from game.engine.collision import CollisionSystem


class TestCollisionSystem:
    def test_beam_weapon_raycasting(self):
        """
        Unit test process_beam_attack with hardcoded vectors.
        Verify hit detection math: direct hit, near miss, range limits.
        """
        collision_system = CollisionSystem()

        # Setup source and target
        source_pos = Vector2(0, 0)

        # Mocking generic object for Target since we don't want to rely on Ship class complexities
        target = MagicMock()
        target.position = Vector2(200, 0)
        target.radius = 20
        target.is_alive = True

        # Mock ability for hit chance (always hit) and damage formula
        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 10  # Return static damage value

        # Mock component that returns the mock ability
        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability

        recent_beams = []

        # Case 1: Direct Hit
        attack_hit = {
            'origin': source_pos,
            'direction': Vector2(1, 0),  # Directly at target (200, 0)
            'range': 300,
            'target': target,
            'damage': 10,
            'component': mock_component
        }

        with patch('random.random', return_value=0.0):
            collision_system.process_beam_attack(attack_hit, recent_beams)
            target.combat_engine.take_damage.assert_called_with(10)

        # Verify beam recorded
        assert len(recent_beams) == 1

        # Case 2: Near Miss
        target.reset_mock()
        aim_vec = Vector2(200, 21).normalize()

        attack_miss = {
            'origin': source_pos,
            'direction': aim_vec,
            'range': 300,
            'target': target,
            'damage': 10,
            'component': mock_component
        }

        with patch('random.random', return_value=0.0):
            collision_system.process_beam_attack(attack_miss, recent_beams)
            target.combat_engine.take_damage.assert_not_called()

        # Case 3: Range Limits
        target.reset_mock()
        attack_range = {
            'origin': source_pos,
            'direction': Vector2(1, 0),
            'range': 150,
            'target': target,
            'damage': 10,
            'component': mock_component
        }

        with patch('random.random', return_value=0.0):
            collision_system.process_beam_attack(attack_range, recent_beams)
            target.combat_engine.take_damage.assert_not_called()

    def test_ramming_logic(self):
        """
        test process_ramming.
        """
        collision_system = CollisionSystem()

        # Mock Ships
        rammer = MagicMock()
        rammer.name = "Rammer"
        rammer.position = Vector2(0, 0)
        rammer.radius = 10
        rammer.ai_strategy = 'kamikaze'
        rammer.is_alive = True
        rammer.hp = 50

        target = MagicMock()
        target.name = "Target"
        target.position = Vector2(15, 0)  # Colliding
        target.radius = 10
        target.is_alive = True
        target.hp = 100

        rammer.current_target = target

        ships = [rammer, target]

        logger = MagicMock()

        # Case A: Rammer HP (50) < Target HP (100)
        collision_system.process_ramming(ships, logger)

        rammer.combat_engine.take_damage.assert_called_with(50 + 9999)
        target.combat_engine.take_damage.assert_called_with(25.0)  # 50 * 0.5

        # Case B: Rammer HP (100) > Target HP (50)
        rammer.reset_mock()
        target.reset_mock()
        rammer.hp = 100
        target.hp = 50

        collision_system.process_ramming(ships, logger)

        target.combat_engine.take_damage.assert_called_with(50 + 9999)
        rammer.combat_engine.take_damage.assert_called_with(25.0)

    def test_beam_weapon_zero_direction_vector(self):
        """Test edge case: zero-length direction vector (a == 0)."""
        collision_system = CollisionSystem()
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.radius = 20
        target.is_alive = True
        target.total_defense_score = 0

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 10

        mock_component = MagicMock()
        mock_component.get_ability.return_value = mock_ability
        recent_beams = []

        # Zero direction vector - this means a=0 in the quadratic
        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(0, 0),  # Zero-length direction
            'range': 300,
            'target': target,
            'component': mock_component
        }

        # With zero direction, discriminant calculation still works,
        # but t=0 means hit at origin. Code sets t1=t2=0 when a=0.
        # This should not cause damage since t=0 doesn't fall in valid range properly
        collision_system.process_beam_attack(attack, recent_beams)
        assert len(recent_beams) == 1

    def test_beam_weapon_tangent_hit(self):
        """Test edge case: discriminant == 0 (tangent hit)."""
        collision_system = CollisionSystem()
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
        target.combat_engine.take_damage.assert_called_with(15)

    def test_beam_weapon_dead_target(self):
        """Test edge case: dead target should not be hit."""
        collision_system = CollisionSystem()
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.radius = 20
        target.is_alive = False  # Dead

        mock_component = MagicMock()
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

        # Beam still recorded but goes to max range
        assert len(recent_beams) == 1
        assert recent_beams[0]['end'] == Vector2(300, 0)

    def test_beam_weapon_no_target(self):
        """Test edge case: no target (just fires into space)."""
        collision_system = CollisionSystem()
        mock_component = MagicMock()
        recent_beams = []

        attack = {
            'origin': Vector2(0, 0),
            'direction': Vector2(1, 0),
            'range': 500,
            'target': None,  # No target
            'component': mock_component
        }

        collision_system.process_beam_attack(attack, recent_beams)

        # Beam just goes to max range
        assert len(recent_beams) == 1
        assert recent_beams[0]['end'] == Vector2(500, 0)

    def test_beam_weapon_target_behind_origin(self):
        """Test edge case: target behind ray origin (negative t values)."""
        collision_system = CollisionSystem()
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

    def test_beam_weapon_origin_inside_target(self):
        """Test edge case: ray origin inside target sphere."""
        collision_system = CollisionSystem()
        target = MagicMock()
        target.position = Vector2(0, 0)  # Same as origin
        target.radius = 50  # Origin is inside
        target.is_alive = True
        target.total_defense_score = 0

        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 20

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

        with patch('random.random', return_value=0.0):
            collision_system.process_beam_attack(attack, recent_beams)

        # Ray exits sphere, t2 is valid - should hit
        target.combat_engine.take_damage.assert_called_with(20)

    def test_ramming_mutual_destruction(self):
        """Test edge case: equal HP results in mutual destruction."""
        collision_system = CollisionSystem()

        rammer = MagicMock()
        rammer.name = "Rammer"
        rammer.position = Vector2(0, 0)
        rammer.radius = 10
        rammer.ai_strategy = 'kamikaze'
        rammer.is_alive = True
        rammer.hp = 50

        target = MagicMock()
        target.name = "Target"
        target.position = Vector2(15, 0)  # Colliding
        target.radius = 10
        target.is_alive = True
        target.hp = 50  # Same HP

        rammer.current_target = target
        ships = [rammer, target]
        logger = MagicMock()

        collision_system.process_ramming(ships, logger)

        # Both should be destroyed
        rammer.combat_engine.take_damage.assert_called_with(50 + 9999)
        target.combat_engine.take_damage.assert_called_with(50 + 9999)
        logger.log.assert_called_with("Ramming: Mutual destruction!")

    def test_ramming_no_logger(self):
        """Test ramming works without logger."""
        collision_system = CollisionSystem()

        rammer = MagicMock()
        rammer.name = "Rammer"
        rammer.position = Vector2(0, 0)
        rammer.radius = 10
        rammer.ai_strategy = 'kamikaze'
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

    def test_ramming_non_kamikaze_ship(self):
        """Test that non-kamikaze ships don't ram."""
        collision_system = CollisionSystem()

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.radius = 10
        ship.ai_strategy = 'aggressive'  # Not kamikaze
        ship.is_alive = True
        ship.hp = 50

        target = MagicMock()
        target.position = Vector2(15, 0)
        target.radius = 10
        target.is_alive = True

        ship.current_target = target
        ships = [ship, target]

        collision_system.process_ramming(ships)

        # Neither should be damaged
        ship.combat_engine.take_damage.assert_not_called()
        target.combat_engine.take_damage.assert_not_called()

    def test_ramming_no_current_target(self):
        """Test kamikaze ship with no target doesn't crash."""
        collision_system = CollisionSystem()

        rammer = MagicMock()
        rammer.position = Vector2(0, 0)
        rammer.radius = 10
        rammer.ai_strategy = 'kamikaze'
        rammer.is_alive = True
        rammer.current_target = None  # No target

        ships = [rammer]

        # Should not raise
        collision_system.process_ramming(ships)
        rammer.combat_engine.take_damage.assert_not_called()
