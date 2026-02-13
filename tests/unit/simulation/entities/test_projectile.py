"""
Unit tests for Projectile entity.

Tests projectile initialization, validation, movement, damage, and guidance.
Covers all edge cases and validation exceptions.
"""
import pytest
from unittest.mock import MagicMock, patch
from game.core.math import Vector2
from game.core.constants import AttackType
from game.core.exceptions import ValidationException
from game.simulation.entities.projectile import Projectile


class TestProjectileInitialization:
    """Test Projectile creation and initialization."""

    @pytest.fixture
    def mock_owner(self):
        """Create a mock owner for projectiles."""
        owner = MagicMock()
        owner.team_id = 1
        return owner

    def test_projectile_creates_with_valid_params(self, mock_owner):
        """Projectile should initialize with all required parameters."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(100, 200),
            velocity=Vector2(10, 5),
            damage=50,
            range_val=1000,
            endurance=5.0,
            proj_type='projectile'
        )

        assert proj.damage == 50
        assert proj.max_range == 1000
        assert proj.endurance == 5.0
        assert proj.max_endurance == 5.0
        assert proj.type == AttackType.PROJECTILE
        assert proj.team_id == 1
        assert proj.is_alive is True
        assert proj.status == 'active'
        assert proj.distance_traveled == 0
        assert proj.position.x == 100
        assert proj.position.y == 200

    def test_projectile_inherits_team_from_owner(self, mock_owner):
        """Projectile should use owner's team_id."""
        mock_owner.team_id = 3
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type='projectile'
        )
        assert proj.team_id == 3

    def test_projectile_handles_owner_without_team(self):
        """Projectile should use -1 for owner without team_id."""
        owner = MagicMock(spec=[])  # No team_id attribute
        proj = Projectile(
            owner=owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type='projectile'
        )
        assert proj.team_id == -1

    def test_projectile_stores_source_weapon(self, mock_owner):
        """Projectile should store reference to source weapon."""
        weapon = MagicMock()
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type='projectile',
            source_weapon=weapon
        )
        assert proj.source_weapon is weapon

    def test_projectile_optional_kwargs(self, mock_owner):
        """Projectile should accept optional kwargs."""
        target = MagicMock()
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=200,
            target=target,
            hp=5,
            radius=10
        )

        assert proj.turn_rate == 90
        assert proj.max_speed == 200
        assert proj.target is target
        assert proj.hp == 5
        assert proj.max_hp == 5
        assert proj.radius == 10

    def test_projectile_default_kwargs(self, mock_owner):
        """Projectile should use defaults for optional kwargs."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type='projectile'
        )

        assert proj.turn_rate == 0
        assert proj.max_speed == 0
        assert proj.target is None
        assert proj.hp == 1
        assert proj.radius == 3


class TestProjectileTypeConversion:
    """Test projectile type handling."""

    @pytest.fixture
    def mock_owner(self):
        owner = MagicMock()
        owner.team_id = 1
        return owner

    def test_string_projectile_type_converted(self, mock_owner):
        """String 'projectile' should convert to AttackType.PROJECTILE."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type='projectile'
        )
        assert proj.type == AttackType.PROJECTILE

    def test_string_missile_type_converted(self, mock_owner):
        """String 'missile' should convert to AttackType.MISSILE."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type='missile'
        )
        assert proj.type == AttackType.MISSILE

    def test_string_beam_type_converted(self, mock_owner):
        """String 'beam' should convert to AttackType.BEAM."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type='beam'
        )
        assert proj.type == AttackType.BEAM

    def test_attacktype_enum_passed_directly(self, mock_owner):
        """AttackType enum should be used directly."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type=AttackType.MISSILE
        )
        assert proj.type == AttackType.MISSILE

    def test_unknown_string_type_raises_value_error(self, mock_owner):
        """Unknown type string raises ValueError."""
        with pytest.raises(ValueError, match="unknown_type"):
            Projectile(
                owner=mock_owner,
                position=Vector2(0, 0),
                velocity=Vector2(1, 0),
                damage=10,
                range_val=100,
                endurance=1.0,
                proj_type='unknown_type'
            )


class TestProjectileValidation:
    """Test projectile parameter validation."""

    @pytest.fixture
    def mock_owner(self):
        owner = MagicMock()
        owner.team_id = 1
        return owner

    def test_negative_damage_raises_validation_error(self, mock_owner):
        """Negative damage should raise ValidationException."""
        with pytest.raises(ValidationException) as exc_info:
            Projectile(
                owner=mock_owner,
                position=Vector2(0, 0),
                velocity=Vector2(1, 0),
                damage=-10,
                range_val=100,
                endurance=1.0,
                proj_type='projectile'
            )
        assert exc_info.value.code == "V003"
        assert "damage" in exc_info.value.context

    def test_none_damage_raises_validation_error(self, mock_owner):
        """None damage should raise ValidationException."""
        with pytest.raises(ValidationException) as exc_info:
            Projectile(
                owner=mock_owner,
                position=Vector2(0, 0),
                velocity=Vector2(1, 0),
                damage=None,
                range_val=100,
                endurance=1.0,
                proj_type='projectile'
            )
        assert exc_info.value.code == "V003"

    def test_zero_damage_allowed(self, mock_owner):
        """Zero damage should be allowed (for utility projectiles)."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=0,
            range_val=100,
            endurance=1.0,
            proj_type='projectile'
        )
        assert proj.damage == 0

    def test_zero_range_raises_validation_error(self, mock_owner):
        """Zero range should raise ValidationException."""
        with pytest.raises(ValidationException) as exc_info:
            Projectile(
                owner=mock_owner,
                position=Vector2(0, 0),
                velocity=Vector2(1, 0),
                damage=10,
                range_val=0,
                endurance=1.0,
                proj_type='projectile'
            )
        assert exc_info.value.code == "V003"
        assert "range" in exc_info.value.context

    def test_negative_range_raises_validation_error(self, mock_owner):
        """Negative range should raise ValidationException."""
        with pytest.raises(ValidationException) as exc_info:
            Projectile(
                owner=mock_owner,
                position=Vector2(0, 0),
                velocity=Vector2(1, 0),
                damage=10,
                range_val=-100,
                endurance=1.0,
                proj_type='projectile'
            )
        assert exc_info.value.code == "V003"

    def test_none_range_raises_validation_error(self, mock_owner):
        """None range should raise ValidationException."""
        with pytest.raises(ValidationException) as exc_info:
            Projectile(
                owner=mock_owner,
                position=Vector2(0, 0),
                velocity=Vector2(1, 0),
                damage=10,
                range_val=None,
                endurance=1.0,
                proj_type='projectile'
            )
        assert exc_info.value.code == "V003"

    def test_none_endurance_allowed(self, mock_owner):
        """None endurance should be allowed (range-limited projectiles)."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=None,
            proj_type='projectile'
        )
        assert proj.endurance is None

    def test_zero_endurance_raises_validation_error(self, mock_owner):
        """Zero endurance should raise ValidationException."""
        with pytest.raises(ValidationException) as exc_info:
            Projectile(
                owner=mock_owner,
                position=Vector2(0, 0),
                velocity=Vector2(1, 0),
                damage=10,
                range_val=100,
                endurance=0,
                proj_type='projectile'
            )
        assert exc_info.value.code == "V003"
        assert "endurance" in exc_info.value.context

    def test_negative_endurance_raises_validation_error(self, mock_owner):
        """Negative endurance should raise ValidationException."""
        with pytest.raises(ValidationException) as exc_info:
            Projectile(
                owner=mock_owner,
                position=Vector2(0, 0),
                velocity=Vector2(1, 0),
                damage=10,
                range_val=100,
                endurance=-1.0,
                proj_type='projectile'
            )
        assert exc_info.value.code == "V003"


class TestProjectileMovement:
    """Test projectile movement and position updates."""

    @pytest.fixture
    def mock_owner(self):
        owner = MagicMock()
        owner.team_id = 1
        return owner

    def test_update_moves_position_by_velocity(self, mock_owner):
        """Update should add velocity to position."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(100, 100),
            velocity=Vector2(10, 5),
            damage=10,
            range_val=10000,
            endurance=100.0,
            proj_type='projectile'
        )

        proj.update()

        assert proj.position.x == pytest.approx(110, abs=0.1)
        assert proj.position.y == pytest.approx(105, abs=0.1)

    def test_update_tracks_distance_traveled(self, mock_owner):
        """Update should accumulate distance_traveled."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(3, 4),  # Length = 5
            damage=10,
            range_val=10000,
            endurance=100.0,
            proj_type='projectile'
        )

        proj.update()
        assert proj.distance_traveled == pytest.approx(5, abs=0.1)

        proj.update()
        assert proj.distance_traveled == pytest.approx(10, abs=0.1)

    def test_dead_projectile_does_not_update(self, mock_owner):
        """Dead projectile should not move."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(10, 0),
            damage=10,
            range_val=1000,
            endurance=1.0,
            proj_type='projectile'
        )

        proj.is_alive = False
        initial_pos = Vector2(proj.position)
        proj.update()

        assert proj.position.x == initial_pos.x
        assert proj.position.y == initial_pos.y


class TestProjectileLifetime:
    """Test projectile lifetime limits (endurance and range)."""

    @pytest.fixture
    def mock_owner(self):
        owner = MagicMock()
        owner.team_id = 1
        return owner

    def test_range_limit_kills_projectile(self, mock_owner):
        """Projectile should die when exceeding max_range."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(100, 0),  # 100 per tick
            damage=10,
            range_val=250,
            endurance=100.0,  # Long endurance
            proj_type='projectile'
        )

        proj.update()  # 100 traveled
        assert proj.is_alive

        proj.update()  # 200 traveled
        assert proj.is_alive

        proj.update()  # 300 traveled > 250 max
        assert not proj.is_alive
        assert proj.status == 'miss'

    def test_endurance_depletes_over_time(self, mock_owner):
        """Endurance should decrease with each update."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100000,
            endurance=0.05,  # 5 ticks at 0.01 dt
            proj_type='projectile'
        )

        initial_endurance = proj.endurance
        proj.update()

        assert proj.endurance < initial_endurance

    def test_endurance_limit_kills_projectile(self, mock_owner):
        """Projectile should die when endurance reaches zero."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100000,
            endurance=0.02,  # 2 ticks
            proj_type='projectile'
        )

        proj.update()  # endurance ~0.01
        assert proj.is_alive

        proj.update()  # endurance ~0 or negative
        assert not proj.is_alive
        assert proj.status == 'miss'

    def test_none_endurance_ignores_time_limit(self, mock_owner):
        """Projectile with None endurance should not expire by time."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100000,
            endurance=None,
            proj_type='projectile'
        )

        for _ in range(100):
            proj.update()

        # Still alive (only range limit applies)
        assert proj.is_alive


class TestProjectileDamage:
    """Test projectile damage mechanics."""

    @pytest.fixture
    def mock_owner(self):
        owner = MagicMock()
        owner.team_id = 1
        return owner

    def test_take_damage_reduces_hp(self, mock_owner):
        """take_damage should reduce HP."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=1000,
            endurance=1.0,
            proj_type='missile',
            hp=10
        )

        proj.take_damage(3)
        assert proj.hp == 7
        assert proj.is_alive

    def test_lethal_damage_kills_projectile(self, mock_owner):
        """Lethal damage should kill projectile and set status."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=1000,
            endurance=1.0,
            proj_type='missile',
            hp=5
        )

        proj.take_damage(10)
        assert not proj.is_alive
        assert proj.status == 'destroyed'
        assert proj.hp == -5

    def test_exact_lethal_damage(self, mock_owner):
        """Exactly lethal damage should kill projectile."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=1000,
            endurance=1.0,
            proj_type='missile',
            hp=5
        )

        proj.take_damage(5)
        assert not proj.is_alive
        assert proj.status == 'destroyed'


class TestMissileGuidance:
    """Test guided missile tracking behavior."""

    @pytest.fixture
    def mock_owner(self):
        owner = MagicMock()
        owner.team_id = 1
        owner.combat_engine = MagicMock()
        owner.combat_engine.solve_lead.return_value = 0  # No lead
        return owner

    @pytest.fixture
    def mock_target(self):
        target = MagicMock()
        target.is_alive = True
        target.position = Vector2(1000, 0)
        target.velocity = Vector2(0, 0)
        return target

    def test_missile_turns_toward_target(self, mock_owner, mock_target):
        """Missile should turn velocity toward target."""
        # Missile starts pointing up, target is to the right
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(0, -100),  # Going up
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        initial_vel_x = proj.velocity.x

        # Update several times
        for _ in range(10):
            proj.update()

        # Should have turned right (positive x)
        assert proj.velocity.x > initial_vel_x

    def test_missile_ignores_dead_target(self, mock_owner, mock_target):
        """Missile should not track dead target."""
        mock_target.is_alive = False

        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        initial_vel = Vector2(proj.velocity)
        proj.update()

        # Velocity should be unchanged in direction
        assert proj.velocity.x == pytest.approx(initial_vel.x, abs=1)

    def test_missile_ignores_none_target(self, mock_owner):
        """Missile should not track None target."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(100, 0),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='missile',
            turn_rate=90,
            max_speed=100,
            target=None,
            hp=5
        )

        initial_vel = Vector2(proj.velocity)
        proj.update()

        # Should move but not turn
        assert proj.velocity.x == pytest.approx(initial_vel.x, abs=1)

    def test_non_missile_does_not_guide(self, mock_owner, mock_target):
        """Non-missile projectile should not use guidance."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(0, -100),
            damage=50,
            range_val=5000,
            endurance=10.0,
            proj_type='projectile',  # Not missile
            turn_rate=90,
            max_speed=100,
            target=mock_target,
            hp=5
        )

        initial_vel = Vector2(proj.velocity)
        proj.update()

        # Velocity direction unchanged (no guidance)
        assert proj.velocity.x == pytest.approx(initial_vel.x, abs=1)
        assert proj.velocity.y == pytest.approx(initial_vel.y, abs=1)


class TestProjectileFlags:
    """Test projectile flags and status tracking."""

    @pytest.fixture
    def mock_owner(self):
        owner = MagicMock()
        owner.team_id = 1
        return owner

    def test_is_derelict_flag(self, mock_owner):
        """Projectile should have is_derelict flag for filtering."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type='projectile'
        )
        assert proj.is_derelict is False

    def test_status_transitions(self, mock_owner):
        """Projectile status should track lifecycle."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type='projectile'
        )

        assert proj.status == 'active'

        # Can be manually set
        proj.status = 'hit'
        assert proj.status == 'hit'

    def test_last_turn_direction_tracking(self, mock_owner):
        """Missile should track turn direction for stability."""
        proj = Projectile(
            owner=mock_owner,
            position=Vector2(0, 0),
            velocity=Vector2(1, 0),
            damage=10,
            range_val=100,
            endurance=1.0,
            proj_type='missile'
        )

        assert proj.last_turn_direction == 0  # Initial
