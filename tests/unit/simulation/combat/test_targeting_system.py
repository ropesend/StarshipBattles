"""
Tests for TargetingSystem - extracted targeting logic from ShipCombatEngine.

Follows TDD: Tests written first, then implementation.
"""
import pytest
import math
from unittest.mock import MagicMock

from game.core.math import Vector2


class TestTargetingSystemCreation:
    """Tests for TargetingSystem instantiation."""

    def test_targeting_system_can_be_created(self):
        """TargetingSystem can be instantiated."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()
        assert system is not None

    def test_targeting_system_has_required_methods(self):
        """TargetingSystem has all required public methods."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()
        assert hasattr(system, 'select_target')
        assert hasattr(system, 'find_valid_target')
        assert hasattr(system, 'calculate_firing_solution')
        assert hasattr(system, 'solve_lead')


class TestSolveLeadCalculation:
    """Tests for lead/interception calculation."""

    def test_solve_lead_stationary_target(self):
        """Lead calculation for stationary target returns direct time-to-target."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        # Shooter at origin, stationary
        pos = Vector2(0, 0)
        vel = Vector2(0, 0)

        # Target at (100, 0), stationary, projectile speed 10
        target_pos = Vector2(100, 0)
        target_vel = Vector2(0, 0)
        proj_speed = 10.0

        t = system.solve_lead(pos, vel, target_pos, target_vel, proj_speed)

        # Time should be distance / speed = 100 / 10 = 10
        assert abs(t - 10.0) < 0.1

    def test_solve_lead_moving_target(self):
        """Lead calculation for moving target returns intercept time."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        pos = Vector2(0, 0)
        vel = Vector2(0, 0)

        # Target moving right at 10 u/s at (100, 0)
        target_pos = Vector2(100, 0)
        target_vel = Vector2(10, 0)
        proj_speed = 20.0

        t = system.solve_lead(pos, vel, target_pos, target_vel, proj_speed)

        assert t > 0
        assert abs(t - 10.0) < 0.5

    def test_solve_lead_no_solution(self):
        """Lead calculation returns 0 when target cannot be intercepted."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        pos = Vector2(0, 0)
        vel = Vector2(0, 0)

        # Target moving away faster than projectile
        target_pos = Vector2(100, 0)
        target_vel = Vector2(100, 0)  # Moving away at 100 u/s
        proj_speed = 10.0  # Only 10 u/s

        t = system.solve_lead(pos, vel, target_pos, target_vel, proj_speed)

        assert t == 0

    def test_solve_lead_linear_case(self):
        """Lead calculation handles linear case (a == 0)."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        # Set up case where a = V.dot(V) - p_speed^2 = 0
        pos = Vector2(0, 0)
        vel = Vector2(0, 0)
        target_pos = Vector2(100, 0)
        target_vel = Vector2(10, 0)  # V = (10, 0), V.V = 100
        proj_speed = 10.0  # p_speed^2 = 100, so a = 0

        t = system.solve_lead(pos, vel, target_pos, target_vel, proj_speed)

        # Should still find a solution
        assert t >= 0


class TestTargetSelection:
    """Tests for target selection logic."""

    def test_select_target_returns_valid_enemy(self):
        """select_target returns an enemy ship from candidates."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        # Create ship mock
        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        # Create enemy candidate
        enemy = MagicMock()
        enemy.is_alive = True
        enemy.team_id = 1
        enemy.position = Vector2(100, 0)

        target = system.select_target(ship, [enemy])
        assert target is enemy

    def test_select_target_excludes_friendlies(self):
        """select_target does not return friendly ships."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        # Create friendly ship
        friendly = MagicMock()
        friendly.is_alive = True
        friendly.team_id = 0  # Same team

        target = system.select_target(ship, [friendly])
        assert target is None

    def test_select_target_excludes_dead_ships(self):
        """select_target does not return dead ships."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        # Create dead enemy
        dead_enemy = MagicMock()
        dead_enemy.is_alive = False
        dead_enemy.team_id = 1

        target = system.select_target(ship, [dead_enemy])
        assert target is None

    def test_select_target_returns_closest_enemy(self):
        """select_target returns the closest valid enemy."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        # Create multiple enemies at different distances
        far_enemy = MagicMock()
        far_enemy.is_alive = True
        far_enemy.team_id = 1
        far_enemy.position = Vector2(200, 0)

        close_enemy = MagicMock()
        close_enemy.is_alive = True
        close_enemy.team_id = 1
        close_enemy.position = Vector2(50, 0)

        target = system.select_target(ship, [far_enemy, close_enemy])
        assert target is close_enemy

    def test_select_target_empty_candidates(self):
        """select_target returns None for empty candidates list."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        target = system.select_target(ship, [])
        assert target is None


class TestFindValidTarget:
    """Tests for find_valid_target method."""

    def test_find_valid_target_returns_primary_when_valid(self):
        """find_valid_target returns primary target when valid."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.angle = 0

        primary = MagicMock()
        primary.is_alive = True
        primary.team_id = 1
        primary.position = Vector2(100, 0)
        primary.velocity = Vector2(0, 0)
        primary.type = 'ship'

        weapon = MagicMock()
        weapon.has_ability = lambda name: name in ['WeaponAbility', 'ProjectileWeaponAbility']
        weapon.has_pdc_ability = MagicMock(return_value=False)

        weapon_ab = MagicMock()
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        proj_ab = MagicMock()
        proj_ab.projectile_speed = 500

        weapon.get_ability = lambda name: weapon_ab if name == 'WeaponAbility' else proj_ab

        target = system.find_valid_target(ship, primary, [], weapon, weapon_ab)
        assert target is primary

    def test_find_valid_target_skips_dead_primary(self):
        """find_valid_target skips dead primary and checks secondaries."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.angle = 0

        dead_primary = MagicMock()
        dead_primary.is_alive = False
        dead_primary.team_id = 1

        secondary = MagicMock()
        secondary.is_alive = True
        secondary.team_id = 1
        secondary.position = Vector2(100, 0)
        secondary.velocity = Vector2(0, 0)
        secondary.type = 'ship'

        weapon = MagicMock()
        weapon.has_ability = lambda name: name in ['WeaponAbility', 'ProjectileWeaponAbility']
        weapon.has_pdc_ability = MagicMock(return_value=False)

        weapon_ab = MagicMock()
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        proj_ab = MagicMock()
        proj_ab.projectile_speed = 500

        weapon.get_ability = lambda name: weapon_ab if name == 'WeaponAbility' else proj_ab

        target = system.find_valid_target(ship, dead_primary, [secondary], weapon, weapon_ab)
        assert target is secondary

    def test_find_valid_target_non_pdc_skips_missiles(self):
        """find_valid_target non-PDC weapons skip missile targets."""
        from game.simulation.combat.targeting_system import TargetingSystem
        from game.core.constants import AttackType

        system = TargetingSystem()

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        missile = MagicMock()
        missile.is_alive = True
        missile.team_id = 1
        missile.type = AttackType.MISSILE

        weapon = MagicMock()
        weapon.has_pdc_ability = MagicMock(return_value=False)

        weapon_ab = MagicMock()

        target = system.find_valid_target(ship, missile, [], weapon, weapon_ab)
        assert target is None

    def test_find_valid_target_pdc_targets_missiles(self):
        """find_valid_target PDC weapons can target missiles."""
        from game.simulation.combat.targeting_system import TargetingSystem
        from game.core.constants import AttackType

        system = TargetingSystem()

        ship = MagicMock()
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.angle = 0

        missile = MagicMock()
        missile.is_alive = True
        missile.team_id = 1
        missile.position = Vector2(50, 0)
        missile.velocity = Vector2(0, 0)
        missile.type = AttackType.MISSILE

        weapon = MagicMock()
        weapon.has_ability = lambda name: name in ['WeaponAbility', 'ProjectileWeaponAbility']
        weapon.has_pdc_ability = MagicMock(return_value=True)

        weapon_ab = MagicMock()
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        proj_ab = MagicMock()
        proj_ab.projectile_speed = 500

        weapon.get_ability = lambda name: weapon_ab if name == 'WeaponAbility' else proj_ab

        target = system.find_valid_target(ship, missile, [], weapon, weapon_ab)
        assert target is missile


class TestFiringSolutionCalculation:
    """Tests for firing solution calculation."""

    def test_calculate_firing_solution_beam_weapon(self):
        """Firing solution for beam weapon aims directly at target."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        target = MagicMock()
        target.position = Vector2(100, 0)
        target.velocity = Vector2(0, 0)

        # Beam weapon component
        comp = MagicMock()
        comp.has_ability = lambda name: name in ['WeaponAbility', 'BeamWeaponAbility']

        aim_pos, aim_vec = system.calculate_firing_solution(ship, comp, target)

        assert aim_pos.x == 100
        assert aim_pos.y == 0
        assert aim_vec.x == 100
        assert aim_vec.y == 0

    def test_calculate_firing_solution_projectile_weapon(self):
        """Firing solution for projectile weapon leads the target."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        # Moving target
        target = MagicMock()
        target.position = Vector2(100, 0)
        target.velocity = Vector2(10, 0)  # Moving right

        # Projectile weapon component
        proj_ability = MagicMock()
        proj_ability.projectile_speed = 500

        comp = MagicMock()
        comp.has_ability = lambda name: name == 'ProjectileWeaponAbility'
        comp.get_ability = lambda name: proj_ability if name == 'ProjectileWeaponAbility' else None

        aim_pos, aim_vec = system.calculate_firing_solution(ship, comp, target)

        # Aim position should be ahead of current position (leading target)
        assert aim_pos.x >= target.position.x

    def test_calculate_firing_solution_seeker_weapon(self):
        """Firing solution for seeker weapon leads the target."""
        from game.simulation.combat.targeting_system import TargetingSystem

        system = TargetingSystem()

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)

        target = MagicMock()
        target.position = Vector2(100, 0)
        target.velocity = Vector2(5, 0)

        # Seeker weapon component
        seeker_ability = MagicMock()
        seeker_ability.projectile_speed = 300

        comp = MagicMock()
        comp.has_ability = lambda name: name == 'SeekerWeaponAbility'
        comp.get_ability = lambda name: seeker_ability if name == 'SeekerWeaponAbility' else None

        aim_pos, aim_vec = system.calculate_firing_solution(ship, comp, target)

        # Should have calculated a lead position
        assert aim_pos is not None
        assert aim_vec is not None
