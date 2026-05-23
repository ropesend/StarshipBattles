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

        # PROJ-359 Phase 4: beam dispatch returns BeamResolution (typed)
        assert len(attacks) == 1
        assert attacks[0].type == AttackType.BEAM
        assert attacks[0].source is ship
        assert attacks[0].target is target
        assert attacks[0].damage == 50


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

        # PROJ-359 Phase 3.2: Projectile family handler now lives in
        # families/projectile.py — patch its Projectile import.
        with patch('game.simulation.combat.families.projectile.Projectile') as mock_proj:
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
        weapon_ab.facing_angle = 0  # PROJ-190: Now on ability, not component
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        seeker_ab = MagicMock()
        seeker_ab.projectile_speed = 300
        seeker_ab.damage = 100
        seeker_ab.endurance = 100
        seeker_ab.turn_rate = 5
        seeker_ab.projectile_hp = 3

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

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        with patch('game.simulation.combat.families.seeker.Projectile') as mock_proj:
            mock_proj.return_value = MagicMock()
            attacks = system.fire_weapons(ship)

            assert len(attacks) == 1
            # Verify missile parameters
            call_kwargs = mock_proj.call_args[1]
            assert call_kwargs['proj_type'] == AttackType.MISSILE


# PROJ-FMS-C audit Fix 1: ``TestHangarLaunch`` removed. The legacy
# ``VehicleLaunch`` weapon-firing auto-launch path has been deleted in
# favor of the explicit :meth:`BattleEngine.launch_fighters_in_battle`
# action surface, driven by
# :class:`game.ai.carrier_controller.CarrierAIController` or a player UI
# action. See ``tests/unit/ai/test_carrier_controller.py`` and
# ``tests/integration/test_fms_c_launch_in_battle_e2e.py``.


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


# =============================================================================
# PROJ-120 Task 1.6: Additional WeaponFiringSystem Tests
# =============================================================================


class TestMultipleWeaponsFiring:
    """Tests for ships with multiple weapons firing simultaneously."""

    def test_multiple_beam_weapons_all_fire(self):
        """Ship with multiple beam weapons fires all of them."""
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

        def create_beam_weapon(damage):
            weapon_ab = MagicMock()
            weapon_ab.can_fire = MagicMock(return_value=True)
            weapon_ab.fire = MagicMock(return_value=True)
            weapon_ab.damage = damage
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
            return weapon

        # Create 3 beam weapons with different damage
        weapons = [
            (LayerType.OUTER, create_beam_weapon(50)),
            (LayerType.OUTER, create_beam_weapon(75)),
            (LayerType.INNER, create_beam_weapon(100)),
        ]
        ship.iter_components = MagicMock(return_value=weapons)

        attacks = system.fire_weapons(ship)

        # All 3 weapons should fire (PROJ-359 Phase 4: BeamResolution typed)
        assert len(attacks) == 3
        assert all(a.type == AttackType.BEAM for a in attacks)

    def test_multiple_projectile_weapons_all_fire(self):
        """Ship with multiple projectile weapons fires all of them."""
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

        def create_proj_weapon():
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
            return weapon

        weapons = [
            (LayerType.OUTER, create_proj_weapon()),
            (LayerType.OUTER, create_proj_weapon()),
        ]
        ship.iter_components = MagicMock(return_value=weapons)

        # PROJ-359 Phase 3.2: Projectile family in families/projectile.py
        with patch('game.simulation.combat.families.projectile.Projectile') as mock_proj:
            mock_proj.return_value = MagicMock()
            attacks = system.fire_weapons(ship)

            # Both weapons should fire
            assert len(attacks) == 2
            assert mock_proj.call_count == 2

    def test_mixed_weapon_types_all_fire(self):
        """Ship with mixed beam and projectile weapons fires all."""
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

        # Beam weapon
        beam_weapon_ab = MagicMock()
        beam_weapon_ab.can_fire = MagicMock(return_value=True)
        beam_weapon_ab.fire = MagicMock(return_value=True)
        beam_weapon_ab.damage = 50
        beam_weapon_ab.range = 500
        beam_weapon_ab.check_firing_solution = MagicMock(return_value=True)
        beam_ab = MagicMock()

        beam_weapon = MagicMock()
        beam_weapon.is_active = True
        beam_weapon.has_ability = lambda name: name in ['WeaponAbility', 'BeamWeaponAbility']
        beam_weapon.get_ability = lambda name: beam_weapon_ab if name == 'WeaponAbility' else beam_ab
        beam_weapon.can_afford_activation = MagicMock(return_value=True)
        beam_weapon.has_pdc_ability = MagicMock(return_value=False)
        beam_weapon.shots_fired = 0
        beam_weapon.shots_hit = 0

        # Projectile weapon
        proj_weapon_ab = MagicMock()
        proj_weapon_ab.can_fire = MagicMock(return_value=True)
        proj_weapon_ab.fire = MagicMock(return_value=True)
        proj_weapon_ab.damage = 25
        proj_weapon_ab.range = 1000
        proj_weapon_ab.check_firing_solution = MagicMock(return_value=True)
        proj_ab = MagicMock()
        proj_ab.projectile_speed = 500
        proj_ab.damage = 25
        proj_ab.range = 1000

        proj_weapon = MagicMock()
        proj_weapon.is_active = True
        proj_weapon.has_ability = lambda name: name in ['WeaponAbility', 'ProjectileWeaponAbility']
        proj_weapon.get_ability = lambda name: proj_weapon_ab if name == 'WeaponAbility' else proj_ab
        proj_weapon.can_afford_activation = MagicMock(return_value=True)
        proj_weapon.has_pdc_ability = MagicMock(return_value=False)
        proj_weapon.shots_fired = 0

        weapons = [
            (LayerType.OUTER, beam_weapon),
            (LayerType.INNER, proj_weapon),
        ]
        ship.iter_components = MagicMock(return_value=weapons)

        # PROJ-359 Phase 3.2: Projectile family in families/projectile.py
        with patch('game.simulation.combat.families.projectile.Projectile') as mock_proj:
            mock_proj.return_value = MagicMock()
            attacks = system.fire_weapons(ship)

            # Both should fire
            assert len(attacks) == 2
            # PROJ-359 Phase 4: beam attacks are BeamResolution objects
            from game.simulation.combat.attack_contract import BeamResolution
            beam_attacks = [a for a in attacks if isinstance(a, BeamResolution)]
            assert len(beam_attacks) == 1


class TestInactiveWeapons:
    """Tests for inactive weapon handling."""

    def test_inactive_weapon_not_fired(self):
        """Inactive weapon is skipped during fire_weapons."""
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

        # Non-operational weapon (inactive)
        weapon_ab = MagicMock()
        weapon_ab.can_fire = MagicMock(return_value=True)

        weapon = MagicMock()
        weapon.is_active = False  # INACTIVE
        weapon.is_operational = False  # NON-OPERATIONAL (checked by fire_weapons)
        weapon.has_ability = lambda name: name == 'WeaponAbility'
        weapon.get_ability = lambda name: weapon_ab

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        attacks = system.fire_weapons(ship)

        # No attacks since weapon is inactive
        assert attacks == []

    def test_some_weapons_inactive_others_fire(self):
        """Only active weapons fire, inactive ones are skipped."""
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

        def create_weapon(is_active):
            weapon_ab = MagicMock()
            weapon_ab.can_fire = MagicMock(return_value=True)
            weapon_ab.fire = MagicMock(return_value=True)
            weapon_ab.damage = 50
            weapon_ab.range = 500
            weapon_ab.check_firing_solution = MagicMock(return_value=True)
            beam_ab = MagicMock()

            weapon = MagicMock()
            weapon.is_active = is_active
            weapon.is_operational = is_active  # fire_weapons checks is_operational
            weapon.has_ability = lambda name: name in ['WeaponAbility', 'BeamWeaponAbility']
            weapon.get_ability = lambda name: weapon_ab if name == 'WeaponAbility' else beam_ab
            weapon.can_afford_activation = MagicMock(return_value=True)
            weapon.has_pdc_ability = MagicMock(return_value=False)
            weapon.shots_fired = 0
            weapon.shots_hit = 0
            return weapon

        weapons = [
            (LayerType.OUTER, create_weapon(is_active=True)),
            (LayerType.OUTER, create_weapon(is_active=False)),  # Inactive
            (LayerType.INNER, create_weapon(is_active=True)),
        ]
        ship.iter_components = MagicMock(return_value=weapons)

        attacks = system.fire_weapons(ship)

        # Only 2 active weapons fire
        assert len(attacks) == 2


class TestPointDefenseWeapons:
    """Tests for Point Defense (PDC) weapon behavior."""

    def test_pdc_weapon_cannot_fire_at_regular_ships(self):
        """PDC weapons should NOT fire at regular ship targets (only missiles/fighters)."""
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

        # Regular ship target (not a fighter)
        target = MagicMock()
        target.is_alive = True
        target.team_id = 1
        target.position = Vector2(100, 0)
        target.velocity = Vector2(0, 0)
        target.type = 'ship'
        target.ship_class = 'Frigate'  # Regular ship, not Fighter
        ship.current_target = target

        # PDC weapon (beam type)
        weapon_ab = MagicMock()
        weapon_ab.can_fire = MagicMock(return_value=True)
        weapon_ab.fire = MagicMock(return_value=True)
        weapon_ab.damage = 10
        weapon_ab.range = 200
        weapon_ab.check_firing_solution = MagicMock(return_value=True)
        beam_ab = MagicMock()

        pdc_weapon = MagicMock()
        pdc_weapon.is_active = True
        pdc_weapon.is_operational = True
        pdc_weapon.has_ability = lambda name: name in ['WeaponAbility', 'BeamWeaponAbility']
        pdc_weapon.get_ability = lambda name: weapon_ab if name == 'WeaponAbility' else beam_ab
        pdc_weapon.can_afford_activation = MagicMock(return_value=True)
        pdc_weapon.has_pdc_ability = MagicMock(return_value=True)  # PDC
        pdc_weapon.shots_fired = 0
        pdc_weapon.shots_hit = 0

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, pdc_weapon)])

        attacks = system.fire_weapons(ship)

        # PDC should NOT fire at regular ships
        assert len(attacks) == 0

    def test_pdc_context_adds_only_alive_enemy_missiles_to_candidates(self):
        """PDC missile context ignores friendly, dead, and non-missile projectiles."""
        from game.simulation.combat.attack_contract import WeaponFamily
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem

        targeting = MagicMock()
        selected_target = MagicMock()
        targeting.find_valid_target.return_value = selected_target
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.team_id = 7
        ship.current_target = None
        ship.max_targets = 1
        ship.secondary_targets = []

        def projectile(is_alive, team_id, attack_type):
            item = MagicMock()
            item.is_alive = is_alive
            item.team_id = team_id
            item.type = attack_type
            return item

        valid_enemy_missile = projectile(True, 3, AttackType.MISSILE)
        friendly_missile = projectile(True, 7, AttackType.MISSILE)
        dead_enemy_missile = projectile(False, 3, AttackType.MISSILE)
        enemy_non_missile = projectile(True, 3, AttackType.PROJECTILE)
        context = {
            'projectiles': [
                friendly_missile,
                valid_enemy_missile,
                dead_enemy_missile,
                enemy_non_missile,
            ]
        }

        with patch(
            'game.simulation.combat.weapon_firing_system.detect_family',
            return_value=WeaponFamily.PDC,
        ):
            result = system._find_valid_target(ship, MagicMock(), MagicMock(), context)

        assert result is selected_target
        targeting.find_valid_target.assert_called_once()
        # PROJ-479 Task 3.27: prefer kwargs over positional .args[N] indexing
        # so a refactor that reorders positional params doesn't silently
        # mis-extract the wrong argument.
        call_args = targeting.find_valid_target.call_args
        if "secondary_targets" in call_args.kwargs:
            secondary_targets = call_args.kwargs["secondary_targets"]
        else:
            secondary_targets = call_args.args[2]
        assert secondary_targets == [valid_enemy_missile]


class TestWeaponFireFails:
    """Tests for weapon fire failure scenarios."""

    def test_weapon_fire_returns_false(self):
        """When weapon.fire() returns False, no attack is created."""
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
        weapon_ab.fire = MagicMock(return_value=False)  # Fire fails
        weapon_ab.damage = 50
        weapon_ab.range = 500
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        weapon = MagicMock()
        weapon.is_active = True
        weapon.has_ability = lambda name: name == 'WeaponAbility'
        weapon.get_ability = lambda name: weapon_ab
        weapon.can_afford_activation = MagicMock(return_value=True)
        weapon.has_pdc_ability = MagicMock(return_value=False)

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        attacks = system.fire_weapons(ship)

        assert attacks == []

    def test_noattack_dispatch_resolution_returns_no_attacks(self):
        """NoAttack keeps the firing path typed without leaking a result."""
        from game.simulation.combat.attack_contract import NoAttack, WeaponFamily
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem

        targeting = MagicMock()
        target = MagicMock()
        targeting.find_valid_target.return_value = target
        targeting.calculate_firing_solution.return_value = (
            Vector2(100, 0),
            Vector2(1, 0),
        )
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.team_id = 0
        ship.current_target = target
        ship.total_shots_fired = 0
        ship.max_targets = 1
        ship.secondary_targets = []

        weapon_ab = MagicMock()
        weapon_ab.can_fire.return_value = True
        weapon_ab.fire.return_value = True

        weapon = MagicMock()
        weapon.is_operational = True
        weapon.has_ability = lambda name: name == 'WeaponAbility'
        weapon.get_ability = lambda name: weapon_ab if name == 'WeaponAbility' else None
        weapon.can_afford_activation.return_value = True
        weapon.shots_fired = 0

        ship.iter_components.return_value = [(LayerType.OUTER, weapon)]

        with patch(
            'game.simulation.combat.weapon_firing_system.detect_family',
            return_value=WeaponFamily.BEAM,
        ), patch(
            'game.simulation.combat.weapon_firing_system.WEAPON_REGISTRY.dispatch',
            return_value=NoAttack("out of arc"),
        ) as dispatch:
            attacks = system.fire_weapons(ship)

        assert attacks == []
        assert ship.total_shots_fired == 1
        assert weapon.shots_fired == 1
        dispatch.assert_called_once()
        request = dispatch.call_args.args[0]
        assert request.family is WeaponFamily.BEAM
        assert request.target is target


class TestWeaponShotTracking:
    """Tests for shot tracking statistics."""

    def test_total_shots_fired_incremented(self):
        """Ship's total_shots_fired is incremented on successful fire."""
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

        system.fire_weapons(ship)

        assert ship.total_shots_fired == 1

    def test_component_shots_fired_incremented(self):
        """Component's shots_fired is incremented on successful fire."""
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

        system.fire_weapons(ship)

        assert weapon.shots_fired == 1

    def test_beam_shots_hit_not_incremented_at_fire_time(self):
        """Beam weapon's shots_hit is NOT incremented at fire time (tracked in collision.py)."""
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

        system.fire_weapons(ship)

        # shots_hit is NOT incremented at fire time — only after accuracy check in collision.py
        assert weapon.shots_hit == 0


# PROJ-FMS-C audit Fix 1: ``TestHangarLaunchEdgeCases`` removed alongside
# ``TestHangarLaunch``. The legacy auto-launch path has been deleted.


class TestSecondaryTargets:
    """Tests for secondary target handling."""

    def test_secondary_targets_passed_to_targeting_system(self):
        """Secondary targets are passed to targeting system for consideration."""
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
        from game.simulation.combat.targeting_system import TargetingSystem

        targeting = MagicMock(spec=TargetingSystem)
        system = WeaponFiringSystem(targeting)

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.team_id = 0
        ship.position = Vector2(0, 0)
        ship.velocity = Vector2(0, 0)
        ship.angle = 0
        ship.total_shots_fired = 0
        ship.max_targets = 3  # Can target multiple

        # Primary target
        primary = MagicMock()
        primary.is_alive = True
        primary.team_id = 1
        primary.position = Vector2(100, 0)
        primary.velocity = Vector2(0, 0)
        primary.type = 'ship'
        ship.current_target = primary

        # Secondary targets
        secondary1 = MagicMock()
        secondary1.is_alive = True
        secondary1.team_id = 1
        secondary2 = MagicMock()
        secondary2.is_alive = True
        secondary2.team_id = 1
        ship.secondary_targets = [secondary1, secondary2]

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

        # Make targeting return a target
        targeting.find_valid_target = MagicMock(return_value=primary)
        targeting.calculate_firing_solution = MagicMock(
            return_value=(Vector2(100, 0), Vector2(100, 0))
        )

        attacks = system.fire_weapons(ship)

        # Verify secondary_targets was passed to find_valid_target
        targeting.find_valid_target.assert_called()
        call_args = targeting.find_valid_target.call_args
        # Third positional arg should be secondary_targets list
        assert call_args[0][2] == [secondary1, secondary2]


class TestSeekerProjectileCreation:
    """Tests for seeker/missile projectile creation details."""

    def test_seeker_projectile_has_turn_rate(self):
        """Seeker projectile is created with turn_rate parameter."""
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
        weapon_ab.facing_angle = 0  # PROJ-190: Now on ability, not component
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        seeker_ab = MagicMock()
        seeker_ab.projectile_speed = 300
        seeker_ab.damage = 100
        seeker_ab.endurance = 100
        seeker_ab.turn_rate = 15  # Specific turn rate
        seeker_ab.projectile_hp = 5  # HP of seeker missile

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

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        with patch('game.simulation.combat.families.seeker.Projectile') as mock_proj:
            mock_proj.return_value = MagicMock()
            system.fire_weapons(ship)

            call_kwargs = mock_proj.call_args[1]
            assert call_kwargs['turn_rate'] == 15
            assert call_kwargs['hp'] == 5

    def test_seeker_target_in_arc_uses_aim_vector(self):
        """Seeker launches toward aim vector when target is in arc."""
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
        ship.angle = 0  # Facing right
        ship.total_shots_fired = 0
        ship.max_targets = 1
        ship.secondary_targets = []

        # Target directly ahead (in arc)
        target = MagicMock()
        target.is_alive = True
        target.team_id = 1
        target.position = Vector2(100, 0)  # Directly ahead
        target.velocity = Vector2(0, 0)
        target.type = 'ship'
        ship.current_target = target

        weapon_ab = MagicMock()
        weapon_ab.can_fire = MagicMock(return_value=True)
        weapon_ab.fire = MagicMock(return_value=True)
        weapon_ab.damage = 100
        weapon_ab.range = 2000
        weapon_ab.firing_arc = 90  # 45 degrees each side
        weapon_ab.facing_angle = 0  # PROJ-190: Now on ability, not component
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        seeker_ab = MagicMock()
        seeker_ab.projectile_speed = 300
        seeker_ab.damage = 100
        seeker_ab.endurance = 100
        seeker_ab.turn_rate = 5
        seeker_ab.projectile_hp = 1

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

        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        with patch('game.simulation.combat.families.seeker.Projectile') as mock_proj:
            mock_proj.return_value = MagicMock()
            system.fire_weapons(ship)

            # Verify projectile was created
            assert mock_proj.called
