"""
Unit tests for ProjectileManager.

Tests cover:
- Projectile creation and tracking
- Update/tick behavior
- Collision detection (static and dynamic)
- Missile interception
- Edge cases (empty lists, boundary conditions, cleanup)
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from game.core.math import Vector2
from game.core.constants import AttackType
from game.simulation.projectile_manager import ProjectileManager


# ============================================================================
# Helper Classes
# ============================================================================

class DummyProjectile:
    """Minimal projectile class for missile interception tests.

    Needed because isinstance check in _check_missile_interception
    requires both projectiles to be the same Python type.
    """
    def __init__(self, **kwargs):
        self.type = kwargs.get('type', AttackType.PROJECTILE)
        self.position = kwargs.get('position', Vector2(0, 0))
        self.velocity = kwargs.get('velocity', Vector2(0, 0))
        self.radius = kwargs.get('radius', 5)
        self.damage = kwargs.get('damage', 10)
        self.is_alive = True
        self.team_id = kwargs.get('team_id', 0)
        self.target = kwargs.get('target', None)
        self.source_weapon = None
        self.status = 'active'
        self.distance_traveled = kwargs.get('distance_traveled', 0)

    def update(self):
        self.position = self.position + self.velocity

    def take_damage(self, amount):
        self.is_alive = False


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def manager():
    """Create a fresh ProjectileManager."""
    return ProjectileManager()


@pytest.fixture
def mock_grid():
    """Create a mock SpatialGrid."""
    grid = MagicMock()
    grid.query_radius.return_value = []
    return grid


@pytest.fixture
def mock_projectile():
    """Create a basic mock projectile."""
    proj = MagicMock()
    proj.position = Vector2(0, 0)
    proj.velocity = Vector2(10, 0)
    proj.is_alive = True
    proj.team_id = 0
    proj.type = AttackType.PROJECTILE
    proj.damage = 20
    proj.distance_traveled = 0
    proj.source_weapon = None
    proj.target = None
    proj.status = 'active'
    proj.radius = 3
    return proj


@pytest.fixture
def mock_ship():
    """Create a basic mock ship."""
    ship = MagicMock()
    ship.position = Vector2(100, 0)
    ship.velocity = Vector2(0, 0)
    ship.radius = 10
    ship.is_alive = True
    ship.team_id = 1  # Different team from projectile
    ship.name = "TestShip"
    return ship


# ============================================================================
# Basic Management Tests
# ============================================================================

class TestProjectileManagerCreation:
    """Tests for ProjectileManager instantiation."""

    def test_can_create_manager(self):
        """ProjectileManager can be instantiated."""
        manager = ProjectileManager()
        assert manager is not None

    def test_starts_with_empty_projectile_list(self):
        """New manager has no projectiles."""
        manager = ProjectileManager()
        assert manager.get_active_projectiles() == []


class TestAddProjectile:
    """Tests for adding projectiles."""

    def test_add_single_projectile(self, manager, mock_projectile):
        """Can add a projectile to the manager."""
        manager.add_projectile(mock_projectile)
        assert len(manager.get_active_projectiles()) == 1
        assert mock_projectile in manager.get_active_projectiles()

    def test_add_multiple_projectiles(self, manager):
        """Can add multiple projectiles."""
        proj1 = MagicMock()
        proj2 = MagicMock()
        proj3 = MagicMock()

        manager.add_projectile(proj1)
        manager.add_projectile(proj2)
        manager.add_projectile(proj3)

        assert len(manager.get_active_projectiles()) == 3

    def test_projectiles_maintain_order(self, manager):
        """Projectiles are stored in the order they were added."""
        projs = [MagicMock() for _ in range(5)]
        for p in projs:
            manager.add_projectile(p)

        active = manager.get_active_projectiles()
        for i, p in enumerate(projs):
            assert active[i] is p


class TestClearProjectiles:
    """Tests for clearing projectiles."""

    def test_clear_removes_all_projectiles(self, manager, mock_projectile):
        """clear() removes all projectiles."""
        manager.add_projectile(mock_projectile)
        manager.add_projectile(MagicMock())
        assert len(manager.get_active_projectiles()) == 2

        manager.clear()
        assert manager.get_active_projectiles() == []

    def test_clear_on_empty_manager(self, manager):
        """clear() on empty manager does not raise."""
        manager.clear()  # Should not raise
        assert manager.get_active_projectiles() == []


# ============================================================================
# Update/Tick Tests
# ============================================================================

class TestUpdateBasics:
    """Tests for basic update behavior."""

    def test_update_calls_projectile_update(self, manager, mock_projectile, mock_grid):
        """update() calls each projectile's update method."""
        manager.add_projectile(mock_projectile)
        manager.update(mock_grid)
        mock_projectile.update.assert_called_once()

    def test_update_calls_grid_query(self, manager, mock_projectile, mock_grid):
        """update() queries the spatial grid for nearby ships."""
        manager.add_projectile(mock_projectile)
        manager.update(mock_grid)
        mock_grid.query_radius.assert_called()

    def test_update_with_empty_list(self, manager, mock_grid):
        """update() with no projectiles does not raise."""
        manager.update(mock_grid)  # Should not raise

    def test_dead_projectiles_removed_after_update(self, manager, mock_grid):
        """Projectiles that become dead during update are removed."""
        proj = MagicMock()
        proj.position = Vector2(0, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.target = None

        # Simulate projectile dying during update
        def die_on_update():
            proj.is_alive = False
        proj.update.side_effect = die_on_update

        manager.add_projectile(proj)
        manager.update(mock_grid)

        assert len(manager.get_active_projectiles()) == 0

    def test_multiple_projectiles_updated(self, manager, mock_grid):
        """All projectiles receive update calls."""
        projs = []
        for _ in range(5):
            p = MagicMock()
            p.position = Vector2(0, 0)
            p.velocity = Vector2(1, 0)
            p.is_alive = True
            p.team_id = 0
            p.type = AttackType.PROJECTILE
            p.target = None
            projs.append(p)
            manager.add_projectile(p)

        manager.update(mock_grid)

        for p in projs:
            p.update.assert_called_once()


class TestProjectileRemoval:
    """Tests for projectile removal during update."""

    def test_some_projectiles_removed_some_remain(self, manager, mock_grid):
        """Dead projectiles are removed, alive ones remain."""
        alive_proj = MagicMock()
        alive_proj.position = Vector2(0, 0)
        alive_proj.velocity = Vector2(1, 0)
        alive_proj.is_alive = True
        alive_proj.team_id = 0
        alive_proj.type = AttackType.PROJECTILE
        alive_proj.target = None

        dead_proj = MagicMock()
        dead_proj.position = Vector2(100, 100)
        dead_proj.velocity = Vector2(1, 0)
        dead_proj.is_alive = True
        dead_proj.team_id = 0
        dead_proj.type = AttackType.PROJECTILE
        dead_proj.target = None

        def die():
            dead_proj.is_alive = False
        dead_proj.update.side_effect = die

        manager.add_projectile(alive_proj)
        manager.add_projectile(dead_proj)
        manager.update(mock_grid)

        active = manager.get_active_projectiles()
        assert len(active) == 1
        assert alive_proj in active
        assert dead_proj not in active

    def test_all_projectiles_removed_when_all_die(self, manager, mock_grid):
        """All projectiles are removed when they all die."""
        projs = []
        for i in range(3):
            p = MagicMock()
            p.position = Vector2(i * 10, 0)
            p.velocity = Vector2(1, 0)
            p.is_alive = True
            p.team_id = 0
            p.type = AttackType.PROJECTILE
            p.target = None
            p.update.side_effect = lambda p=p: setattr(p, 'is_alive', False)
            projs.append(p)
            manager.add_projectile(p)

        manager.update(mock_grid)
        assert manager.get_active_projectiles() == []


# ============================================================================
# Ship Collision Tests
# ============================================================================

class TestShipCollisions:
    """Tests for projectile-ship collisions."""

    def test_projectile_hits_enemy_ship(self, manager, mock_projectile, mock_ship, mock_grid):
        """Projectile collides with enemy ship and applies damage."""
        # Position projectile close to ship
        mock_projectile.position = Vector2(95, 0)
        mock_projectile.velocity = Vector2(10, 0)
        mock_ship.position = Vector2(100, 0)

        mock_grid.query_radius.return_value = [mock_ship]
        manager.add_projectile(mock_projectile)
        manager.update(mock_grid)

        # Verify damage was applied
        mock_ship.combat_engine.take_damage.assert_called_with(20)
        # Verify projectile is marked as hit
        assert mock_projectile.is_alive is False
        assert mock_projectile.status == 'hit'

    def test_projectile_ignores_friendly_ship(self, manager, mock_projectile, mock_ship, mock_grid):
        """Projectile does not hit ships on same team."""
        mock_projectile.position = Vector2(95, 0)
        mock_projectile.velocity = Vector2(10, 0)
        mock_ship.team_id = 0  # Same team as projectile
        mock_ship.position = Vector2(100, 0)

        mock_grid.query_radius.return_value = [mock_ship]
        manager.add_projectile(mock_projectile)
        manager.update(mock_grid)

        # No damage should be applied
        mock_ship.combat_engine.take_damage.assert_not_called()
        # Projectile still alive
        assert mock_projectile.is_alive is True

    def test_projectile_ignores_dead_ship(self, manager, mock_projectile, mock_ship, mock_grid):
        """Projectile does not hit dead ships."""
        mock_projectile.position = Vector2(95, 0)
        mock_projectile.velocity = Vector2(10, 0)
        mock_ship.is_alive = False
        mock_ship.position = Vector2(100, 0)

        mock_grid.query_radius.return_value = [mock_ship]
        manager.add_projectile(mock_projectile)
        manager.update(mock_grid)

        mock_ship.combat_engine.take_damage.assert_not_called()

    def test_collision_with_stationary_ship(self, manager, mock_grid):
        """Projectile hits stationary ship (static collision)."""
        proj = MagicMock()
        proj.position = Vector2(5, 0)  # Very close to ship
        proj.velocity = Vector2(0, 0)  # Not moving
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 15
        proj.distance_traveled = 10
        proj.source_weapon = None
        proj.target = None

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)
        ship.radius = 10
        ship.is_alive = True
        ship.team_id = 1
        ship.name = "StaticShip"

        mock_grid.query_radius.return_value = [ship]
        manager.add_projectile(proj)
        manager.update(mock_grid)

        ship.combat_engine.take_damage.assert_called_with(15)

    def test_collision_with_moving_ship(self, manager, mock_grid):
        """Projectile hits moving ship (dynamic collision)."""
        # Collision detection uses swept collision:
        # p_start = p_pos - p_vel (projectile start position this frame)
        # For projectile at (110, 0) with velocity (20, 0):
        #   p_start = (90, 0), p_end = (110, 0)
        # Ship at (100, 0) with velocity (0, 0):
        #   s_prev = (100, 0), s_curr = (100, 0)
        # The projectile sweeps from 90 to 110 and ship is at 100 with radius 10
        # So there should definitely be a collision
        proj = MagicMock()
        proj.position = Vector2(110, 0)  # Current position after moving
        proj.velocity = Vector2(20, 0)   # Velocity this frame
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 25
        proj.distance_traveled = 50
        proj.source_weapon = None
        proj.target = None

        ship = MagicMock()
        ship.position = Vector2(100, 0)  # Ship at 100
        ship.velocity = Vector2(0, 0)
        ship.radius = 10
        ship.is_alive = True
        ship.team_id = 1
        ship.name = "TargetShip"

        mock_grid.query_radius.return_value = [ship]
        manager.add_projectile(proj)
        manager.update(mock_grid)

        ship.combat_engine.take_damage.assert_called_with(25)

    def test_miss_when_outside_collision_radius(self, manager, mock_grid):
        """Projectile misses ship when outside collision radius."""
        proj = MagicMock()
        proj.position = Vector2(0, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.target = None

        ship = MagicMock()
        ship.position = Vector2(500, 500)  # Far away
        ship.velocity = Vector2(0, 0)
        ship.radius = 10
        ship.is_alive = True
        ship.team_id = 1

        mock_grid.query_radius.return_value = [ship]
        manager.add_projectile(proj)
        manager.update(mock_grid)

        ship.combat_engine.take_damage.assert_not_called()


class TestDamageCalculation:
    """Tests for damage calculation during hits."""

    def test_uses_static_damage_without_weapon(self, manager, mock_projectile, mock_ship, mock_grid):
        """Uses projectile's static damage when no source weapon."""
        mock_projectile.position = Vector2(95, 0)
        mock_projectile.velocity = Vector2(10, 0)
        mock_projectile.damage = 42
        mock_projectile.source_weapon = None
        mock_ship.position = Vector2(100, 0)

        mock_grid.query_radius.return_value = [mock_ship]
        manager.add_projectile(mock_projectile)
        manager.update(mock_grid)

        mock_ship.combat_engine.take_damage.assert_called_with(42)

    def test_uses_weapon_damage_formula_when_available(self, manager, mock_ship, mock_grid):
        """Uses weapon ability's get_damage when available."""
        proj = MagicMock()
        proj.position = Vector2(95, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 20  # Static damage (should be ignored)
        proj.distance_traveled = 100
        proj.target = None

        # Setup source weapon with WeaponAbility
        weapon = MagicMock()
        weapon_ability = MagicMock()
        weapon_ability.get_damage.return_value = 35  # Distance-based damage
        weapon.get_ability.return_value = weapon_ability
        proj.source_weapon = weapon

        mock_ship.position = Vector2(100, 0)
        mock_grid.query_radius.return_value = [mock_ship]

        manager.add_projectile(proj)
        manager.update(mock_grid)

        # Should call weapon ability's get_damage with distance
        weapon_ability.get_damage.assert_called_with(100)
        mock_ship.combat_engine.take_damage.assert_called_with(35)

    def test_weapon_hit_counter_incremented(self, manager, mock_ship, mock_grid):
        """Source weapon's shots_hit counter is incremented on hit."""
        proj = MagicMock()
        proj.position = Vector2(95, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 20
        proj.distance_traveled = 10
        proj.target = None

        weapon = MagicMock()
        weapon.shots_hit = 0
        weapon.get_ability.return_value = None
        proj.source_weapon = weapon

        mock_ship.position = Vector2(100, 0)
        mock_grid.query_radius.return_value = [mock_ship]

        manager.add_projectile(proj)
        manager.update(mock_grid)

        assert weapon.shots_hit == 1


# ============================================================================
# Missile Interception Tests
# ============================================================================

class TestMissileInterception:
    """Tests for missile-vs-missile interception."""

    def test_missile_intercepts_target_missile(self, manager, mock_grid):
        """Interceptor missile destroys target missile."""
        # Must use real class instances (not MagicMock) because
        # _check_missile_interception uses isinstance(p.target, type(p))
        target_missile = DummyProjectile(
            type=AttackType.MISSILE,
            position=Vector2(60, 0),  # Close to interceptor
            velocity=Vector2(0, 0),
            radius=5,
            team_id=1
        )

        interceptor = DummyProjectile(
            type=AttackType.MISSILE,
            position=Vector2(50, 0),
            velocity=Vector2(10, 0),
            radius=5,
            damage=50,
            team_id=0,
            target=target_missile
        )

        manager.add_projectile(interceptor)
        manager.add_projectile(target_missile)

        # Patch take_damage to verify it was called
        with patch.object(target_missile, 'take_damage') as mock_take_damage:
            manager.update(mock_grid)
            mock_take_damage.assert_called_with(50)

    def test_non_missile_does_not_intercept(self, manager, mock_grid):
        """Non-missile projectiles do not intercept other projectiles."""
        target_missile = MagicMock()
        target_missile.position = Vector2(55, 0)
        target_missile.velocity = Vector2(0, 0)
        target_missile.is_alive = True
        target_missile.team_id = 1
        target_missile.radius = 5

        projectile = MagicMock()
        projectile.position = Vector2(50, 0)
        projectile.velocity = Vector2(10, 0)
        projectile.is_alive = True
        projectile.team_id = 0
        projectile.type = AttackType.PROJECTILE  # Not a missile
        projectile.damage = 50
        projectile.target = target_missile
        projectile.source_weapon = None

        manager.add_projectile(projectile)
        manager.update(mock_grid)

        # No interception should occur
        target_missile.take_damage.assert_not_called()

    def test_no_interception_if_target_dead(self, manager, mock_grid):
        """Missile does not intercept already-dead target."""
        target_missile = MagicMock()
        target_missile.position = Vector2(55, 0)
        target_missile.velocity = Vector2(0, 0)
        target_missile.is_alive = False  # Already dead
        target_missile.team_id = 1
        target_missile.radius = 5
        target_missile.type = AttackType.MISSILE

        interceptor = MagicMock()
        interceptor.position = Vector2(50, 0)
        interceptor.velocity = Vector2(10, 0)
        interceptor.is_alive = True
        interceptor.team_id = 0
        interceptor.type = AttackType.MISSILE
        interceptor.damage = 50
        interceptor.radius = 5
        interceptor.target = target_missile
        interceptor.source_weapon = None

        type(target_missile).__name__ = type(interceptor).__name__

        manager.add_projectile(interceptor)
        manager.update(mock_grid)

        target_missile.take_damage.assert_not_called()

    def test_no_interception_if_target_out_of_range(self, manager, mock_grid):
        """Missile does not intercept target that's too far away."""
        target_missile = MagicMock()
        target_missile.position = Vector2(1000, 0)  # Far away
        target_missile.velocity = Vector2(0, 0)
        target_missile.is_alive = True
        target_missile.team_id = 1
        target_missile.radius = 5
        target_missile.type = AttackType.MISSILE

        interceptor = MagicMock()
        interceptor.position = Vector2(50, 0)
        interceptor.velocity = Vector2(10, 0)
        interceptor.is_alive = True
        interceptor.team_id = 0
        interceptor.type = AttackType.MISSILE
        interceptor.damage = 50
        interceptor.radius = 5
        interceptor.target = target_missile
        interceptor.source_weapon = None

        type(target_missile).__name__ = type(interceptor).__name__

        manager.add_projectile(interceptor)
        manager.update(mock_grid)

        target_missile.take_damage.assert_not_called()

    def test_intercepted_missile_marked_destroyed(self, manager, mock_grid):
        """Intercepted missile that dies is marked as destroyed."""
        # Must use real class instances for isinstance check in _check_missile_interception
        target_missile = DummyProjectile(
            type=AttackType.MISSILE,
            position=Vector2(60, 0),
            velocity=Vector2(0, 0),
            radius=5,
            team_id=1
        )

        interceptor = DummyProjectile(
            type=AttackType.MISSILE,
            position=Vector2(50, 0),
            velocity=Vector2(10, 0),
            radius=5,
            damage=50,
            team_id=0,
            target=target_missile
        )

        manager.add_projectile(interceptor)
        manager.add_projectile(target_missile)
        manager.update(mock_grid)

        # DummyProjectile.take_damage sets is_alive=False,
        # which should trigger status='destroyed' in _check_missile_interception
        assert target_missile.status == 'destroyed'


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_zero_velocity_projectile(self, manager, mock_grid):
        """Projectile with zero velocity still processes."""
        proj = MagicMock()
        proj.position = Vector2(0, 0)
        proj.velocity = Vector2(0, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.target = None

        manager.add_projectile(proj)
        manager.update(mock_grid)

        proj.update.assert_called_once()

    def test_negative_velocity_projectile(self, manager, mock_grid):
        """Projectile with negative velocity (moving backwards)."""
        proj = MagicMock()
        proj.position = Vector2(100, 100)
        proj.velocity = Vector2(-10, -10)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.target = None

        manager.add_projectile(proj)
        manager.update(mock_grid)

        proj.update.assert_called_once()

    def test_very_large_velocity(self, manager, mock_grid):
        """Projectile with very large velocity."""
        proj = MagicMock()
        proj.position = Vector2(0, 0)
        proj.velocity = Vector2(10000, 10000)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.target = None

        manager.add_projectile(proj)
        manager.update(mock_grid)  # Should not raise

    def test_projectile_and_ship_same_velocity(self, manager, mock_grid):
        """Projectile and ship moving at same velocity (relative rest)."""
        proj = MagicMock()
        proj.position = Vector2(5, 0)
        proj.velocity = Vector2(50, 0)  # Moving right at 50
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 10
        proj.distance_traveled = 5
        proj.source_weapon = None
        proj.target = None

        ship = MagicMock()
        ship.position = Vector2(10, 0)
        ship.velocity = Vector2(50, 0)  # Also moving right at 50
        ship.radius = 10
        ship.is_alive = True
        ship.team_id = 1
        ship.name = "ParallelShip"

        mock_grid.query_radius.return_value = [ship]
        manager.add_projectile(proj)
        manager.update(mock_grid)

        # Static collision check should apply (rel vel = 0)
        # Distance is 5 which is less than radius + tolerance
        ship.combat_engine.take_damage.assert_called()

    def test_multiple_ships_in_range_hits_first(self, manager, mock_grid):
        """When multiple ships in range, only first is hit."""
        proj = MagicMock()
        proj.position = Vector2(95, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 20
        proj.distance_traveled = 50
        proj.source_weapon = None
        proj.target = None

        ship1 = MagicMock()
        ship1.position = Vector2(100, 0)
        ship1.velocity = Vector2(0, 0)
        ship1.radius = 10
        ship1.is_alive = True
        ship1.team_id = 1
        ship1.name = "Ship1"

        ship2 = MagicMock()
        ship2.position = Vector2(100, 5)
        ship2.velocity = Vector2(0, 0)
        ship2.radius = 10
        ship2.is_alive = True
        ship2.team_id = 1
        ship2.name = "Ship2"

        mock_grid.query_radius.return_value = [ship1, ship2]
        manager.add_projectile(proj)
        manager.update(mock_grid)

        # First ship should be hit
        ship1.combat_engine.take_damage.assert_called_once()
        # Second ship should not be hit (projectile already used)
        ship2.combat_engine.take_damage.assert_not_called()

    def test_rapid_add_and_clear(self, manager):
        """Rapid add and clear operations work correctly."""
        for _ in range(100):
            manager.add_projectile(MagicMock())
        assert len(manager.get_active_projectiles()) == 100

        manager.clear()
        assert len(manager.get_active_projectiles()) == 0

        for _ in range(50):
            manager.add_projectile(MagicMock())
        assert len(manager.get_active_projectiles()) == 50

    def test_update_with_large_projectile_count(self, manager, mock_grid):
        """Update handles many projectiles efficiently."""
        projs = []
        for i in range(100):
            p = MagicMock()
            p.position = Vector2(i * 10, 0)
            p.velocity = Vector2(1, 0)
            p.is_alive = True
            p.team_id = 0
            p.type = AttackType.PROJECTILE
            p.target = None
            projs.append(p)
            manager.add_projectile(p)

        manager.update(mock_grid)

        # All should have been updated
        for p in projs:
            p.update.assert_called_once()


class TestQueryBuffer:
    """Tests related to spatial query buffer."""

    def test_query_radius_uses_velocity_plus_buffer(self, manager, mock_grid):
        """Query radius is based on projectile velocity plus buffer."""
        proj = MagicMock()
        proj.position = Vector2(0, 0)
        proj.velocity = Vector2(100, 0)  # Speed of 100
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.target = None

        manager.add_projectile(proj)
        manager.update(mock_grid)

        # Verify query was made with appropriate radius
        call_args = mock_grid.query_radius.call_args
        assert call_args is not None
        # The radius should be velocity.length() + buffer (100 + 100 = 200 typically)
        pos, radius = call_args[0]
        assert radius >= 100  # At least velocity magnitude


# ============================================================================
# Record Hit Tests
# ============================================================================

class TestRecordHit:
    """Tests for _record_hit behavior."""

    def test_hit_sets_is_alive_false(self, manager, mock_ship, mock_grid):
        """Projectile is marked dead after hit."""
        proj = MagicMock()
        proj.position = Vector2(95, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 20
        proj.distance_traveled = 10
        proj.source_weapon = None
        proj.target = None

        mock_ship.position = Vector2(100, 0)
        mock_grid.query_radius.return_value = [mock_ship]

        manager.add_projectile(proj)
        manager.update(mock_grid)

        assert proj.is_alive is False

    def test_hit_sets_status_to_hit(self, manager, mock_ship, mock_grid):
        """Projectile status is 'hit' after collision."""
        proj = MagicMock()
        proj.position = Vector2(95, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 20
        proj.distance_traveled = 10
        proj.source_weapon = None
        proj.target = None
        proj.status = 'active'

        mock_ship.position = Vector2(100, 0)
        mock_grid.query_radius.return_value = [mock_ship]

        manager.add_projectile(proj)
        manager.update(mock_grid)

        assert proj.status == 'hit'

    def test_no_weapon_stats_update_when_no_source(self, manager, mock_ship, mock_grid):
        """No crash when projectile has no source weapon."""
        proj = MagicMock()
        proj.position = Vector2(95, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 20
        proj.distance_traveled = 10
        proj.source_weapon = None
        proj.target = None

        mock_ship.position = Vector2(100, 0)
        mock_grid.query_radius.return_value = [mock_ship]

        manager.add_projectile(proj)
        # Should not raise
        manager.update(mock_grid)


# ============================================================================
# Additional Edge Case Tests (PROJ-118 Phase 2)
# ============================================================================

class TestProjectileManagerAdditionalEdgeCases:
    """Additional edge case tests for ProjectileManager."""

    def test_weapon_ability_returns_none(self, manager, mock_ship, mock_grid):
        """Handles weapon.get_ability returning None for WeaponAbility."""
        proj = MagicMock()
        proj.position = Vector2(95, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 25  # Should use static damage
        proj.distance_traveled = 50
        proj.target = None

        # Weapon exists but get_ability returns None
        weapon = MagicMock()
        weapon.get_ability.return_value = None
        weapon.shots_hit = 0
        proj.source_weapon = weapon

        mock_ship.position = Vector2(100, 0)
        mock_grid.query_radius.return_value = [mock_ship]

        manager.add_projectile(proj)
        manager.update(mock_grid)

        # Should fall back to static damage
        mock_ship.combat_engine.take_damage.assert_called_with(25)
        assert weapon.shots_hit == 1

    def test_weapon_ability_without_get_damage_method(self, manager, mock_ship, mock_grid):
        """Handles weapon ability without get_damage method (uses static damage)."""
        proj = MagicMock()
        proj.position = Vector2(95, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 30
        proj.distance_traveled = 50
        proj.target = None

        # Weapon ability exists but lacks get_damage method
        weapon = MagicMock()
        weapon_ability = MagicMock(spec=[])  # Empty spec = no get_damage
        del weapon_ability.get_damage  # Ensure no get_damage attr
        weapon.get_ability.return_value = weapon_ability
        weapon.shots_hit = 0
        proj.source_weapon = weapon

        mock_ship.position = Vector2(100, 0)
        mock_grid.query_radius.return_value = [mock_ship]

        manager.add_projectile(proj)
        manager.update(mock_grid)

        # Should use static damage since ability lacks get_damage
        mock_ship.combat_engine.take_damage.assert_called_with(30)

    def test_missile_with_none_target(self, manager, mock_grid):
        """Missile projectile with None target does not crash."""
        proj = MagicMock()
        proj.position = Vector2(0, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.MISSILE
        proj.target = None  # No target
        proj.damage = 50
        proj.radius = 5

        manager.add_projectile(proj)
        # Should not raise
        manager.update(mock_grid)

        # Projectile should still be alive (no interception)
        assert proj.is_alive is True

    def test_projectile_missing_target_attribute(self, manager, mock_grid):
        """Projectile without target attribute does not crash."""
        proj = MagicMock()
        proj.position = Vector2(0, 0)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        # Explicitly remove target attribute
        del proj.target

        manager.add_projectile(proj)
        # Should not raise
        manager.update(mock_grid)

    def test_concurrent_removal_of_adjacent_projectiles(self, manager, mock_grid):
        """Multiple adjacent projectiles dying in same update are handled correctly."""
        projs = []
        for i in range(5):
            p = MagicMock()
            p.position = Vector2(i * 5, 0)
            p.velocity = Vector2(1, 0)
            p.is_alive = True
            p.team_id = 0
            p.type = AttackType.PROJECTILE
            p.target = None
            # All die during update
            p.update.side_effect = lambda p=p: setattr(p, 'is_alive', False)
            projs.append(p)
            manager.add_projectile(p)

        manager.update(mock_grid)

        # All should be removed
        assert manager.get_active_projectiles() == []

    def test_projectile_velocity_diagonal(self, manager, mock_ship, mock_grid):
        """Projectile moving diagonally can hit ship."""
        proj = MagicMock()
        # Diagonal approach to (100, 100) from (90, 90)
        proj.position = Vector2(100, 100)
        proj.velocity = Vector2(10, 10)
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 15
        proj.distance_traveled = 14.14  # sqrt(10^2 + 10^2)
        proj.source_weapon = None
        proj.target = None

        mock_ship.position = Vector2(95, 95)
        mock_ship.velocity = Vector2(0, 0)
        mock_ship.radius = 15
        mock_ship.is_alive = True
        mock_ship.team_id = 1
        mock_ship.name = "DiagonalTarget"

        mock_grid.query_radius.return_value = [mock_ship]
        manager.add_projectile(proj)
        manager.update(mock_grid)

        # Should hit the ship
        mock_ship.combat_engine.take_damage.assert_called_with(15)

    def test_get_active_projectiles_returns_copy_safe_list(self, manager):
        """get_active_projectiles() returns internal list reference."""
        proj1 = MagicMock()
        proj2 = MagicMock()
        manager.add_projectile(proj1)
        manager.add_projectile(proj2)

        active = manager.get_active_projectiles()

        # Verify it's the actual list (not a copy)
        assert active is manager.projectiles
        assert len(active) == 2

    def test_projectile_just_inside_collision_radius_hits(self, manager, mock_grid):
        """Projectile clearly inside collision radius hits ship."""
        from game.core.config import BattleConfig

        proj = MagicMock()
        ship_radius = 10
        tolerance = BattleConfig.PROJECTILE_HIT_TOLERANCE
        # Position projectile clearly within collision range
        # Collision radius = ship_radius + tolerance = 15
        # Place projectile at distance 5 (well within 15)
        proj.position = Vector2(5, 0)
        proj.velocity = Vector2(0, 0)  # Stationary
        proj.is_alive = True
        proj.team_id = 0
        proj.type = AttackType.PROJECTILE
        proj.damage = 5
        proj.distance_traveled = 0
        proj.source_weapon = None
        proj.target = None

        ship = MagicMock()
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)
        ship.radius = ship_radius
        ship.is_alive = True
        ship.team_id = 1
        ship.name = "TargetShip"

        mock_grid.query_radius.return_value = [ship]
        manager.add_projectile(proj)
        manager.update(mock_grid)

        # Should hit since clearly within collision radius
        ship.combat_engine.take_damage.assert_called()

    def test_interceptor_missile_is_removed_after_interception(self, manager, mock_grid):
        """Interceptor missile is removed after successful interception."""
        target_missile = DummyProjectile(
            type=AttackType.MISSILE,
            position=Vector2(60, 0),
            velocity=Vector2(0, 0),
            radius=5,
            team_id=1
        )

        interceptor = DummyProjectile(
            type=AttackType.MISSILE,
            position=Vector2(50, 0),
            velocity=Vector2(10, 0),
            radius=5,
            damage=50,
            team_id=0,
            target=target_missile
        )

        manager.add_projectile(interceptor)
        manager.add_projectile(target_missile)
        manager.update(mock_grid)

        # Both should be removed (interceptor hit, target destroyed)
        active = manager.get_active_projectiles()
        assert interceptor not in active


# ============================================================================
# Batch Update Tests (PROJ-120 Task 1.16)
# ============================================================================

class TestBatchUpdateMultipleHits:
    """Tests for multiple projectiles hitting different ships in same update."""

    def test_multiple_projectiles_hit_different_ships(self, manager, mock_grid):
        """Multiple projectiles can hit different ships in the same update cycle."""
        # Create two ships
        ship1 = MagicMock()
        ship1.position = Vector2(100, 0)
        ship1.velocity = Vector2(0, 0)
        ship1.radius = 10
        ship1.is_alive = True
        ship1.team_id = 1
        ship1.name = "Ship1"

        ship2 = MagicMock()
        ship2.position = Vector2(200, 0)
        ship2.velocity = Vector2(0, 0)
        ship2.radius = 10
        ship2.is_alive = True
        ship2.team_id = 1
        ship2.name = "Ship2"

        # Create two projectiles targeting different areas
        proj1 = MagicMock()
        proj1.position = Vector2(95, 0)
        proj1.velocity = Vector2(10, 0)
        proj1.is_alive = True
        proj1.team_id = 0
        proj1.type = AttackType.PROJECTILE
        proj1.damage = 20
        proj1.distance_traveled = 50
        proj1.source_weapon = None
        proj1.target = None

        proj2 = MagicMock()
        proj2.position = Vector2(195, 0)
        proj2.velocity = Vector2(10, 0)
        proj2.is_alive = True
        proj2.team_id = 0
        proj2.type = AttackType.PROJECTILE
        proj2.damage = 30
        proj2.distance_traveled = 50
        proj2.source_weapon = None
        proj2.target = None

        # Setup grid to return appropriate ships for each query
        def query_side_effect(pos, radius):
            # Return ships near the queried position
            if pos.x < 150:
                return [ship1]
            else:
                return [ship2]

        mock_grid.query_radius.side_effect = query_side_effect

        manager.add_projectile(proj1)
        manager.add_projectile(proj2)
        manager.update(mock_grid)

        # Both ships should receive damage
        ship1.combat_engine.take_damage.assert_called_with(20)
        ship2.combat_engine.take_damage.assert_called_with(30)
        # Both projectiles should be marked hit
        assert proj1.is_alive is False
        assert proj2.is_alive is False

    def test_multiple_projectiles_hit_same_ship(self, manager, mock_grid):
        """Multiple projectiles can hit the same ship in the same update."""
        ship = MagicMock()
        ship.position = Vector2(100, 0)
        ship.velocity = Vector2(0, 0)
        ship.radius = 20  # Large radius to hit both
        ship.is_alive = True
        ship.team_id = 1
        ship.name = "BigShip"

        # Create projectiles approaching from different angles
        proj1 = MagicMock()
        proj1.position = Vector2(95, 5)
        proj1.velocity = Vector2(10, 0)
        proj1.is_alive = True
        proj1.team_id = 0
        proj1.type = AttackType.PROJECTILE
        proj1.damage = 15
        proj1.distance_traveled = 25
        proj1.source_weapon = None
        proj1.target = None

        proj2 = MagicMock()
        proj2.position = Vector2(95, -5)
        proj2.velocity = Vector2(10, 0)
        proj2.is_alive = True
        proj2.team_id = 0
        proj2.type = AttackType.PROJECTILE
        proj2.damage = 25
        proj2.distance_traveled = 25
        proj2.source_weapon = None
        proj2.target = None

        mock_grid.query_radius.return_value = [ship]

        manager.add_projectile(proj1)
        manager.add_projectile(proj2)
        manager.update(mock_grid)

        # Ship should receive damage twice
        assert ship.combat_engine.take_damage.call_count == 2
        # Verify both damage values were applied
        calls = [call[0][0] for call in ship.combat_engine.take_damage.call_args_list]
        assert 15 in calls
        assert 25 in calls


class TestBatchMarkAndSweepRemoval:
    """Tests for the in-place mark-and-sweep removal algorithm."""

    def test_alternating_alive_dead_projectiles(self, manager, mock_grid):
        """Alternating pattern of alive/dead projectiles is handled correctly."""
        projs = []
        for i in range(10):
            p = MagicMock()
            p.position = Vector2(i * 100, 0)  # Spread out
            p.velocity = Vector2(1, 0)
            p.is_alive = True
            p.team_id = 0
            p.type = AttackType.PROJECTILE
            p.target = None

            # Every other projectile dies
            if i % 2 == 0:
                p.update.side_effect = lambda p=p: setattr(p, 'is_alive', False)
            projs.append(p)
            manager.add_projectile(p)

        manager.update(mock_grid)

        # Should have exactly 5 alive (odd indices)
        active = manager.get_active_projectiles()
        assert len(active) == 5
        for i, p in enumerate(projs):
            if i % 2 == 1:
                assert p in active
            else:
                assert p not in active

    def test_first_half_dead_second_half_alive(self, manager, mock_grid):
        """First half of projectiles die, second half survive."""
        alive_projs = []
        dead_projs = []

        for i in range(10):
            p = MagicMock()
            p.position = Vector2(i * 100, 0)
            p.velocity = Vector2(1, 0)
            p.is_alive = True
            p.team_id = 0
            p.type = AttackType.PROJECTILE
            p.target = None

            if i < 5:
                p.update.side_effect = lambda p=p: setattr(p, 'is_alive', False)
                dead_projs.append(p)
            else:
                alive_projs.append(p)
            manager.add_projectile(p)

        manager.update(mock_grid)

        active = manager.get_active_projectiles()
        assert len(active) == 5
        for p in alive_projs:
            assert p in active
        for p in dead_projs:
            assert p not in active

    def test_only_first_survives(self, manager, mock_grid):
        """Only the first projectile survives, rest die."""
        first = MagicMock()
        first.position = Vector2(0, 0)
        first.velocity = Vector2(1, 0)
        first.is_alive = True
        first.team_id = 0
        first.type = AttackType.PROJECTILE
        first.target = None
        manager.add_projectile(first)

        for i in range(9):
            p = MagicMock()
            p.position = Vector2((i + 1) * 100, 0)
            p.velocity = Vector2(1, 0)
            p.is_alive = True
            p.team_id = 0
            p.type = AttackType.PROJECTILE
            p.target = None
            p.update.side_effect = lambda p=p: setattr(p, 'is_alive', False)
            manager.add_projectile(p)

        manager.update(mock_grid)

        active = manager.get_active_projectiles()
        assert len(active) == 1
        assert first in active

    def test_only_last_survives(self, manager, mock_grid):
        """Only the last projectile survives, rest die."""
        projs = []
        for i in range(10):
            p = MagicMock()
            p.position = Vector2(i * 100, 0)
            p.velocity = Vector2(1, 0)
            p.is_alive = True
            p.team_id = 0
            p.type = AttackType.PROJECTILE
            p.target = None

            if i < 9:
                p.update.side_effect = lambda p=p: setattr(p, 'is_alive', False)
            projs.append(p)
            manager.add_projectile(p)

        manager.update(mock_grid)

        active = manager.get_active_projectiles()
        assert len(active) == 1
        assert projs[9] in active

    def test_removal_preserves_relative_order(self, manager, mock_grid):
        """Surviving projectiles maintain their relative order."""
        survivors = []
        for i in range(10):
            p = MagicMock()
            p.position = Vector2(i * 100, 0)
            p.velocity = Vector2(1, 0)
            p.is_alive = True
            p.team_id = 0
            p.type = AttackType.PROJECTILE
            p.target = None
            p.order_id = i  # Track original order

            # Keep indices 1, 4, 7
            if i in [1, 4, 7]:
                survivors.append(p)
            else:
                p.update.side_effect = lambda p=p: setattr(p, 'is_alive', False)
            manager.add_projectile(p)

        manager.update(mock_grid)

        active = manager.get_active_projectiles()
        assert len(active) == 3
        # Verify order is preserved
        assert active[0].order_id == 1
        assert active[1].order_id == 4
        assert active[2].order_id == 7


class TestBatchUpdateLargeScale:
    """Tests for batch updates with large numbers of projectiles."""

    def test_batch_update_100_projectiles_half_die(self, manager, mock_grid):
        """100 projectiles with half dying is handled efficiently."""
        projs = []
        for i in range(100):
            p = MagicMock()
            p.position = Vector2(i * 10, 0)
            p.velocity = Vector2(1, 0)
            p.is_alive = True
            p.team_id = 0
            p.type = AttackType.PROJECTILE
            p.target = None

            if i % 2 == 0:
                p.update.side_effect = lambda p=p: setattr(p, 'is_alive', False)
            projs.append(p)
            manager.add_projectile(p)

        manager.update(mock_grid)

        assert len(manager.get_active_projectiles()) == 50

    def test_batch_update_all_survive(self, manager, mock_grid):
        """100 projectiles all surviving is handled."""
        for i in range(100):
            p = MagicMock()
            p.position = Vector2(i * 10, 0)
            p.velocity = Vector2(1, 0)
            p.is_alive = True
            p.team_id = 0
            p.type = AttackType.PROJECTILE
            p.target = None
            manager.add_projectile(p)

        manager.update(mock_grid)

        assert len(manager.get_active_projectiles()) == 100

    def test_batch_removal_no_stale_references(self, manager, mock_grid):
        """After batch removal, list has no gaps or stale references."""
        projs = []
        for i in range(20):
            p = MagicMock()
            p.position = Vector2(i * 50, 0)
            p.velocity = Vector2(5, 0)
            p.is_alive = True
            p.team_id = 0
            p.type = AttackType.PROJECTILE
            p.target = None
            p.name = f"proj_{i}"

            # Kill random pattern
            if i in [0, 3, 7, 11, 15, 19]:
                p.update.side_effect = lambda p=p: setattr(p, 'is_alive', False)
            else:
                projs.append(p)
            manager.add_projectile(p)

        manager.update(mock_grid)

        active = manager.get_active_projectiles()
        # Should have exactly 14 survivors
        assert len(active) == 14
        # All should be alive
        for p in active:
            assert p.is_alive is True
        # List should be contiguous (no None gaps)
        for i, p in enumerate(active):
            assert active[i] is not None


class TestBatchUpdateWithHitsAndDeaths:
    """Tests combining hits and natural deaths in same update."""

    def test_mixed_hit_and_expire_removal(self, manager, mock_grid):
        """Projectiles removed by both hit and expiration in same update."""
        ship = MagicMock()
        ship.position = Vector2(100, 0)
        ship.velocity = Vector2(0, 0)
        ship.radius = 10
        ship.is_alive = True
        ship.team_id = 1
        ship.name = "Target"

        # Projectile that will hit
        hitting = MagicMock()
        hitting.position = Vector2(95, 0)
        hitting.velocity = Vector2(10, 0)
        hitting.is_alive = True
        hitting.team_id = 0
        hitting.type = AttackType.PROJECTILE
        hitting.damage = 20
        hitting.distance_traveled = 50
        hitting.source_weapon = None
        hitting.target = None

        # Projectile that expires naturally
        expiring = MagicMock()
        expiring.position = Vector2(500, 500)  # Far from ship
        expiring.velocity = Vector2(1, 0)
        expiring.is_alive = True
        expiring.team_id = 0
        expiring.type = AttackType.PROJECTILE
        expiring.target = None
        expiring.update.side_effect = lambda: setattr(expiring, 'is_alive', False)

        # Projectile that survives
        surviving = MagicMock()
        surviving.position = Vector2(1000, 1000)  # Far from ship
        surviving.velocity = Vector2(1, 0)
        surviving.is_alive = True
        surviving.team_id = 0
        surviving.type = AttackType.PROJECTILE
        surviving.target = None

        def query_side_effect(pos, radius):
            if pos.x < 150:
                return [ship]
            return []

        mock_grid.query_radius.side_effect = query_side_effect

        manager.add_projectile(hitting)
        manager.add_projectile(expiring)
        manager.add_projectile(surviving)
        manager.update(mock_grid)

        active = manager.get_active_projectiles()
        assert len(active) == 1
        assert surviving in active
        assert hitting not in active
        assert expiring not in active

    def test_projectile_hit_then_another_checked_but_misses(self, manager, mock_grid):
        """First projectile hits ship, second is checked but misses."""
        ship = MagicMock()
        ship.position = Vector2(100, 0)
        ship.velocity = Vector2(0, 0)
        ship.radius = 10
        ship.is_alive = True
        ship.team_id = 1
        ship.name = "Target"

        # First projectile hits
        proj1 = MagicMock()
        proj1.position = Vector2(95, 0)
        proj1.velocity = Vector2(10, 0)
        proj1.is_alive = True
        proj1.team_id = 0
        proj1.type = AttackType.PROJECTILE
        proj1.damage = 20
        proj1.distance_traveled = 10
        proj1.source_weapon = None
        proj1.target = None

        # Second projectile misses (far from ship)
        proj2 = MagicMock()
        proj2.position = Vector2(300, 0)
        proj2.velocity = Vector2(10, 0)
        proj2.is_alive = True
        proj2.team_id = 0
        proj2.type = AttackType.PROJECTILE
        proj2.target = None

        def query_side_effect(pos, radius):
            # Ship only near first projectile
            if pos.x < 150:
                return [ship]
            return []

        mock_grid.query_radius.side_effect = query_side_effect

        manager.add_projectile(proj1)
        manager.add_projectile(proj2)
        manager.update(mock_grid)

        # First hit, second survives
        ship.combat_engine.take_damage.assert_called_once_with(20)
        active = manager.get_active_projectiles()
        assert len(active) == 1
        assert proj2 in active
