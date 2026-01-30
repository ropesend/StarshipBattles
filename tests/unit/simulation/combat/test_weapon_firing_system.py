"""
Tests for WeaponFiringSystem - extracted weapon firing logic from ShipCombatEngine.

Follows TDD: Tests written first, then implementation.
"""
import pytest
import math
from unittest.mock import MagicMock, patch

from game.core.math import Vector2
from game.core.constants import AttackType, LayerType


class TestWeaponFiringSystemCreation:
    """Tests for WeaponFiringSystem instantiation."""

    def test_weapon_firing_system_can_be_created(self):
        """WeaponFiringSystem can be instantiated."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = TargetingSystem()
        system = WeaponFiringSystem(targeting)
        assert system is not None

    def test_weapon_firing_system_has_required_methods(self):
        """WeaponFiringSystem has all required public methods."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = TargetingSystem()
        system = WeaponFiringSystem(targeting)
        assert hasattr(system, 'fire_weapons')


class TestFireWeaponsBasic:
    """Basic tests for fire_weapons method."""

    def test_fire_weapons_returns_empty_when_dead(self):
        """fire_weapons returns empty list when ship is dead."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = TargetingSystem()
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.is_alive = False
        ship.is_derelict = False

        attacks = system.fire_weapons(ship)
        assert attacks == []

    def test_fire_weapons_returns_empty_when_derelict(self):
        """fire_weapons returns empty list when ship is derelict."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = TargetingSystem()
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = True

        attacks = system.fire_weapons(ship)
        assert attacks == []

    def test_fire_weapons_returns_empty_when_no_weapons(self):
        """fire_weapons returns empty list when ship has no weapons."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = TargetingSystem()
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.iter_components = MagicMock(return_value=[])

        attacks = system.fire_weapons(ship)
        assert attacks == []


class TestBeamWeaponFiring:
    """Tests for beam weapon firing."""

    def test_beam_weapon_creates_beam_attack(self):
        """Beam weapon creates beam attack when fired."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = TargetingSystem()
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)
        ship.angle = 0
        ship.total_shots_fired = 0
        ship.max_targets = 1
        ship.secondary_targets = []

        # Target
        target = MagicMock()
        target.is_alive = True
        target.team_id = 1
        target.position = Vector2(100, 0)
        target.velocity = Vector2(0, 0)
        target.type = 'ship'
        ship.current_target = target

        # Beam weapon
        weapon_ab = MagicMock()
        weapon_ab.can_fire = MagicMock(return_value=True)
        weapon_ab.fire = MagicMock(return_value=True)
        weapon_ab.damage = 50
        weapon_ab.range = 500
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        beam_ab = MagicMock()

        weapon = MagicMock()
        weapon.is_active = True
        weapon.has_ability = lambda name: name in ['WeaponAbility', 'BeamWeaponAbility']
        weapon.get_ability = lambda name: weapon_ab if name == 'WeaponAbility' else beam_ab
        weapon.can_afford_activation = MagicMock(return_value=True)
        weapon.has_pdc_ability = MagicMock(return_value=False)
        weapon.shots_fired = 0
        weapon.shots_hit = 0

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        attacks = system.fire_weapons(ship)

        assert len(attacks) == 1
        assert attacks[0]['type'] == AttackType.BEAM
        assert attacks[0]['source'] is ship
        assert attacks[0]['target'] is target
        assert attacks[0]['damage'] == 50


class TestProjectileWeaponFiring:
    """Tests for projectile weapon firing."""

    def test_projectile_weapon_creates_projectile(self):
        """Projectile weapon creates projectile when fired."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = TargetingSystem()
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)
        ship.angle = 0
        ship.total_shots_fired = 0
        ship.max_targets = 1
        ship.secondary_targets = []

        target = MagicMock()
        target.is_alive = True
        target.team_id = 1
        target.position = Vector2(100, 0)
        target.velocity = Vector2(0, 0)
        target.type = 'ship'
        ship.current_target = target

        weapon_ab = MagicMock()
        weapon_ab.can_fire = MagicMock(return_value=True)
        weapon_ab.fire = MagicMock(return_value=True)
        weapon_ab.damage = 25
        weapon_ab.range = 1000
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        proj_ab = MagicMock()
        proj_ab.projectile_speed = 500
        proj_ab.damage = 25
        proj_ab.range = 1000

        weapon = MagicMock()
        weapon.is_active = True
        weapon.has_ability = lambda name: name in ['WeaponAbility', 'ProjectileWeaponAbility']
        weapon.get_ability = lambda name: weapon_ab if name == 'WeaponAbility' else proj_ab
        weapon.can_afford_activation = MagicMock(return_value=True)
        weapon.has_pdc_ability = MagicMock(return_value=False)
        weapon.shots_fired = 0

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        with patch('game.simulation.combat.weapon_firing_system.Projectile') as mock_proj:
            mock_proj.return_value = MagicMock()
            attacks = system.fire_weapons(ship)

            assert len(attacks) == 1
            mock_proj.assert_called_once()


class TestSeekerWeaponFiring:
    """Tests for seeker/missile weapon firing."""

    def test_seeker_weapon_creates_missile(self):
        """Seeker weapon creates missile projectile when fired."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = TargetingSystem()
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)
        ship.angle = 0
        ship.total_shots_fired = 0
        ship.max_targets = 1
        ship.secondary_targets = []

        target = MagicMock()
        target.is_alive = True
        target.team_id = 1
        target.position = Vector2(100, 0)
        target.velocity = Vector2(0, 0)
        target.type = 'ship'
        ship.current_target = target

        weapon_ab = MagicMock()
        weapon_ab.can_fire = MagicMock(return_value=True)
        weapon_ab.fire = MagicMock(return_value=True)
        weapon_ab.damage = 100
        weapon_ab.range = 2000
        weapon_ab.firing_arc = 90
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        seeker_ab = MagicMock()
        seeker_ab.projectile_speed = 300
        seeker_ab.damage = 100
        seeker_ab.endurance = 100
        seeker_ab.turn_rate = 5
        seeker_ab.missile_hp = 3

        weapon = MagicMock()
        weapon.is_active = True
        weapon.has_ability = lambda name: name in ['WeaponAbility', 'SeekerWeaponAbility']
        weapon.get_ability = lambda name: {
            'WeaponAbility': weapon_ab,
            'SeekerWeaponAbility': seeker_ab,
        }.get(name)
        weapon.can_afford_activation = MagicMock(return_value=True)
        weapon.has_pdc_ability = MagicMock(return_value=False)
        weapon.shots_fired = 0
        weapon.facing_angle = 0

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        with patch('game.simulation.combat.weapon_firing_system.Projectile') as mock_proj:
            mock_proj.return_value = MagicMock()
            attacks = system.fire_weapons(ship)

            assert len(attacks) == 1
            # Verify missile parameters
            call_kwargs = mock_proj.call_args[1]
            assert call_kwargs['proj_type'] == AttackType.MISSILE


class TestHangarLaunch:
    """Tests for hangar vehicle launch."""

    def test_hangar_creates_launch_attack(self):
        """Hangar component creates launch attack when ready."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = TargetingSystem()
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.team_id = 0
        ship.position = Vector2(0, 0)

        target = MagicMock()
        target.is_alive = True
        target.team_id = 1
        ship.current_target = target

        vl_ability = MagicMock()
        vl_ability.try_launch = MagicMock(return_value=True)
        vl_ability.fighter_class = 'interceptor'

        hangar = MagicMock()
        hangar.is_active = True
        hangar.has_ability = lambda name: name == 'VehicleLaunch'
        hangar.get_ability = lambda name: vl_ability if name == 'VehicleLaunch' else None

        ship.iter_components = MagicMock(return_value=[(LayerType.INNER, hangar)])

        attacks = system.fire_weapons(ship)

        assert len(attacks) == 1
        assert attacks[0]['type'] == AttackType.LAUNCH
        assert attacks[0]['fighter_class'] == 'interceptor'


class TestWeaponFiringConditions:
    """Tests for weapon firing conditions."""

    def test_weapon_not_fired_when_cannot_afford_activation(self):
        """Weapon not fired when can_afford_activation returns False."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = TargetingSystem()
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.iter_components = MagicMock(return_value=[])

        weapon_ab = MagicMock()

        weapon = MagicMock()
        weapon.is_active = True
        weapon.has_ability = lambda name: name == 'WeaponAbility'
        weapon.get_ability = lambda name: weapon_ab
        weapon.can_afford_activation = MagicMock(return_value=False)

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        attacks = system.fire_weapons(ship)

        assert attacks == []

    def test_weapon_not_fired_when_on_cooldown(self):
        """Weapon not fired when can_fire returns False."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = TargetingSystem()
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = False

        weapon_ab = MagicMock()
        weapon_ab.can_fire = MagicMock(return_value=False)

        weapon = MagicMock()
        weapon.is_active = True
        weapon.has_ability = lambda name: name == 'WeaponAbility'
        weapon.get_ability = lambda name: weapon_ab
        weapon.can_afford_activation = MagicMock(return_value=True)

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        attacks = system.fire_weapons(ship)

        assert attacks == []

    def test_weapon_not_fired_when_no_valid_target(self):
        """Weapon not fired when no valid target exists."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = TargetingSystem()
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.team_id = 0
        ship.current_target = None
        ship.secondary_targets = []
        ship.max_targets = 1

        weapon_ab = MagicMock()
        weapon_ab.can_fire = MagicMock(return_value=True)

        weapon = MagicMock()
        weapon.is_active = True
        weapon.has_ability = lambda name: name == 'WeaponAbility'
        weapon.get_ability = lambda name: weapon_ab
        weapon.can_afford_activation = MagicMock(return_value=True)
        weapon.has_pdc_ability = MagicMock(return_value=False)

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        attacks = system.fire_weapons(ship)

        assert attacks == []
