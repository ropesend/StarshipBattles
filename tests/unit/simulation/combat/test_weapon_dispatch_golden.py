"""
PROJ-359 Phase 1: Golden / Characterization Tests for Weapon Dispatch.

Locks current per-family dispatch outcomes for Beam, Projectile, Seeker, and
PDC weapons before the typed-contract refactor begins. These tests pin the
*exact* observable shape of each family's emitted attack and the downstream
hit-application contract (collision for beam, projectile manager for
projectile/seeker, projectile manager + collision for PDC).

Strict TDD invariants:
- These tests must PASS on current main (pre-refactor)
- They must continue to PASS bit-for-bit through Phase 2 (contract introduced)
- They guard each Phase 3 family migration
- After Phase 4 (legacy deletion), they may need shape adaptations only if the
  contract goal explicitly converges shapes (per plan §Goals)

Author: PROJ-359 Phase 1
"""
from __future__ import annotations

import math
import random
from unittest.mock import MagicMock, patch

import pytest

from game.core.constants import AttackType, LayerType, SimulationConstants
from game.core.math import Vector2
from game.engine.collision import CollisionSystem
from game.simulation.combat.targeting_system import TargetingSystem
from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
from game.simulation.entities.projectile import Projectile
from game.simulation.projectile_manager import ProjectileManager


# ---------------------------------------------------------------------------
# Fixtures: deterministic ships and weapons
# ---------------------------------------------------------------------------


def _make_ship(team_id: int = 0, position: tuple[float, float] = (0.0, 0.0)) -> MagicMock:
    ship = MagicMock()
    ship.is_alive = True
    ship.is_derelict = False
    ship.team_id = team_id
    ship.position = Vector2(*position)
    ship.velocity = Vector2(0.0, 0.0)
    ship.angle = 0.0
    ship.total_shots_fired = 0
    ship.max_targets = 1
    ship.secondary_targets = []
    ship.current_target = None
    ship.iter_components = MagicMock(return_value=[])
    return ship


def _make_weapon_component(
    *,
    family_abilities: list[str],
    weapon_ab: MagicMock,
    family_ab: MagicMock | None = None,
    is_pdc: bool = False,
) -> MagicMock:
    """Build a MagicMock weapon component that reports ownership of the named
    abilities plus 'WeaponAbility'. `family_ab` is returned for any non-Weapon
    ability lookup (Beam/Projectile/Seeker)."""
    ability_set = set(family_abilities) | {'WeaponAbility'}

    weapon = MagicMock()
    weapon.is_active = True
    weapon.is_operational = True
    weapon.has_ability = lambda name: name in ability_set
    weapon.has_pdc_ability = MagicMock(return_value=is_pdc)
    weapon.can_afford_activation = MagicMock(return_value=True)
    weapon.shots_fired = 0
    weapon.shots_hit = 0

    def _get_ability(name: str):
        if name == 'WeaponAbility':
            return weapon_ab
        if family_ab is not None and name in family_abilities:
            return family_ab
        return None

    weapon.get_ability = _get_ability
    return weapon


# ---------------------------------------------------------------------------
# Beam family
# ---------------------------------------------------------------------------


class TestBeamGolden:
    """Golden snapshot for the Beam dispatch path."""

    def test_beam_attack_has_exact_resolution_shape(self):
        """Beam dispatch returns a BeamResolution with these exact field values.

        PROJ-359 Phase 4: original Phase 1 golden test asserted on a dict
        shape. Phase 4 deleted the dict carrier; this test now asserts on
        the typed BeamResolution attributes (same field names and values
        since the resolution was designed as a 1:1 typed mirror)."""
        from game.simulation.combat.attack_contract import BeamResolution

        targeting = TargetingSystem()
        firing = WeaponFiringSystem(targeting)

        ship = _make_ship()
        target = _make_ship(team_id=1, position=(100.0, 0.0))
        target.type = 'ship'
        ship.current_target = target

        weapon_ab = MagicMock()
        weapon_ab.can_fire = MagicMock(return_value=True)
        weapon_ab.fire = MagicMock(return_value=True)
        weapon_ab.damage = 50
        weapon_ab.range = 500
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        beam_ab = MagicMock()

        weapon = _make_weapon_component(
            family_abilities=['BeamWeaponAbility'],
            weapon_ab=weapon_ab,
            family_ab=beam_ab,
            is_pdc=False,
        )
        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        attacks = firing.fire_weapons(ship)

        assert len(attacks) == 1
        attack = attacks[0]
        assert isinstance(attack, BeamResolution)
        assert attack.type is AttackType.BEAM
        assert attack.source is ship
        assert attack.target is target
        assert attack.damage == 50
        assert attack.range == 500
        assert attack.origin == ship.position
        assert attack.component is weapon
        assert attack.hit is True
        # Direction is unit vector toward target (target is at +x of source)
        assert attack.direction.x == pytest.approx(1.0)
        assert attack.direction.y == pytest.approx(0.0)

    def test_beam_collision_telemetry_chain(self):
        """End-to-end: beam attack -> collision -> damage applied with
        DamageContext(damage_type='beam'). Locks the engine-layer contract.

        PROJ-359 Phase 4: input is now BeamResolution, not dict."""
        from game.simulation.combat.attack_contract import BeamResolution

        rng = random.Random(0)
        # Force rng.random() to return 0.0 so any non-zero hit chance hits
        rng.random = lambda: 0.0
        cs = CollisionSystem(rng=rng)

        target = MagicMock()
        target.is_alive = True
        target.position = Vector2(100.0, 0.0)
        target.radius = 10.0
        target.total_defense_score = 0.0
        target.fleet_defense_bonus = None
        target.combat_engine = MagicMock()

        beam_ab = MagicMock()
        beam_ab.calculate_hit_chance = MagicMock(return_value=0.99)
        beam_ab.get_damage = MagicMock(return_value=42.0)

        beam_comp = MagicMock()
        beam_comp.get_ability = lambda name: beam_ab if name == 'BeamWeaponAbility' else None
        beam_comp.shots_hit = 0

        source = MagicMock()
        source.get_total_sensor_score = MagicMock(return_value=0.0)
        source.fleet_attack_bonus = None

        attack = BeamResolution(
            source=source,
            component=beam_comp,
            target=target,
            damage=42.0,
            range=500.0,
            origin=Vector2(0.0, 0.0),
            direction=Vector2(1.0, 0.0),
            hit=True,
        )
        recent: list[dict] = []
        cs.process_beam_attack(attack, recent)

        # Hit was rolled and applied
        target.combat_engine.take_damage.assert_called_once()
        call = target.combat_engine.take_damage.call_args
        assert call.args[0] == 42.0
        ctx = call.kwargs['context']
        assert ctx.damage_type == 'beam'
        assert ctx.attacker is source
        assert ctx.source_weapon is beam_comp
        # shots_hit incremented exactly once
        assert beam_comp.shots_hit == 1
        # Visualization side-effect captured
        assert len(recent) == 1
        assert set(recent[0].keys()) == {'start', 'end', 'color'}


# ---------------------------------------------------------------------------
# Projectile family
# ---------------------------------------------------------------------------


class TestProjectileGolden:
    """Golden snapshot for the Projectile dispatch path."""

    def test_projectile_attack_creates_projectile_with_pinned_fields(self):
        targeting = TargetingSystem()
        firing = WeaponFiringSystem(targeting)

        ship = _make_ship()
        target = _make_ship(team_id=1, position=(100.0, 0.0))
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

        weapon = _make_weapon_component(
            family_abilities=['ProjectileWeaponAbility'],
            weapon_ab=weapon_ab,
            family_ab=proj_ab,
        )
        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        # PROJ-359 Phase 3.2: Projectile family is now in families/projectile.py.
        # Patch both possible call sites so this test stays valid before & after
        # the migration (the test pins the constructor kwargs, which are
        # unchanged regardless of which module instantiates the projectile).
        with patch('game.simulation.combat.families.projectile.Projectile') as mock_proj:
            sentinel = MagicMock()
            mock_proj.return_value = sentinel
            attacks = firing.fire_weapons(ship)

            assert len(attacks) == 1
            assert attacks[0] is sentinel

            # Constructor kwargs (golden)
            mock_proj.assert_called_once()
            kwargs = mock_proj.call_args.kwargs
            assert kwargs['owner'] is ship
            assert kwargs['damage'] == 25
            assert kwargs['range_val'] == 1000
            assert kwargs['endurance'] is None
            assert kwargs['proj_type'] is AttackType.PROJECTILE
            assert kwargs['source_weapon'] is weapon
            assert kwargs['target'] is target
            # Velocity = unit_aim * (speed/SCALE) + ship.velocity
            expected_speed = 500 / SimulationConstants.PROJECTILE_SPEED_SCALE
            assert kwargs['velocity'].x == pytest.approx(expected_speed)
            assert kwargs['velocity'].y == pytest.approx(0.0)

    def test_projectile_hit_application_telemetry(self):
        """Projectile hit on a ship goes through ProjectileManager._apply_hit
        with damage_type='projectile' DamageContext. Pinned for refactor."""
        pm = ProjectileManager()

        owner = _make_ship()
        target_ship = _make_ship(team_id=1, position=(50.0, 0.0))
        target_ship.combat_engine = MagicMock()

        weapon_ab = MagicMock()
        weapon_ab.get_damage = MagicMock(return_value=33.0)
        source_weapon = MagicMock()
        source_weapon.get_ability = lambda name: weapon_ab if name == 'WeaponAbility' else None

        # Bypass Projectile.__init__ (validation) — assemble a stand-in object
        p = MagicMock(spec=Projectile)
        p.distance_traveled = 100.0
        p.damage = 33.0
        p.owner = owner
        p.source_weapon = source_weapon

        pm._apply_hit(p, target_ship)

        target_ship.combat_engine.take_damage.assert_called_once()
        call = target_ship.combat_engine.take_damage.call_args
        assert call.args[0] == 33.0
        ctx = call.kwargs['context']
        assert ctx.damage_type == 'projectile'
        assert ctx.attacker is owner
        assert ctx.source_weapon is source_weapon


# ---------------------------------------------------------------------------
# Seeker / Missile family
# ---------------------------------------------------------------------------


class TestSeekerGolden:
    """Golden snapshot for the Seeker / Missile dispatch path."""

    def test_seeker_attack_creates_missile_with_pinned_fields(self):
        targeting = TargetingSystem()
        firing = WeaponFiringSystem(targeting)

        ship = _make_ship()
        target = _make_ship(team_id=1, position=(100.0, 0.0))
        target.type = 'ship'
        ship.current_target = target

        weapon_ab = MagicMock()
        weapon_ab.can_fire = MagicMock(return_value=True)
        weapon_ab.fire = MagicMock(return_value=True)
        weapon_ab.damage = 100
        weapon_ab.range = 2000
        weapon_ab.firing_arc = 90
        weapon_ab.facing_angle = 0
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        seeker_ab = MagicMock()
        seeker_ab.projectile_speed = 300
        seeker_ab.projectile_damage = 100
        seeker_ab.endurance = 100
        seeker_ab.turn_rate = 5
        seeker_ab.projectile_hp = 3
        seeker_ab.to_hit_defense = 0.5
        # Used by find_valid_target range gating
        seeker_ab.endurance = 100

        weapon = _make_weapon_component(
            family_abilities=['SeekerWeaponAbility'],
            weapon_ab=weapon_ab,
            family_ab=seeker_ab,
        )
        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        # PROJ-359 Phase 3.3: Seeker family in families/seeker.py
        with patch('game.simulation.combat.families.seeker.Projectile') as mock_proj:
            sentinel = MagicMock()
            mock_proj.return_value = sentinel
            attacks = firing.fire_weapons(ship)

            assert len(attacks) == 1
            mock_proj.assert_called_once()
            kwargs = mock_proj.call_args.kwargs
            assert kwargs['owner'] is ship
            assert kwargs['damage'] == 100  # seeker_ab.projectile_damage
            assert kwargs['proj_type'] is AttackType.MISSILE
            assert kwargs['turn_rate'] == 5
            assert kwargs['target'] is target
            assert kwargs['hp'] == 3
            assert kwargs['to_hit_defense'] == 0.5
            assert kwargs['endurance'] == 100
            assert kwargs['source_weapon'] is weapon
            # range_val = projectile_speed * endurance
            assert kwargs['range_val'] == 300 * 100
            # max_speed = projectile_speed / SCALE
            expected_speed = 300 / SimulationConstants.PROJECTILE_SPEED_SCALE
            assert kwargs['max_speed'] == pytest.approx(expected_speed)


# ---------------------------------------------------------------------------
# PDC family — distinguishing scenario: PDC firing on enemy missile
# ---------------------------------------------------------------------------


class TestPDCGolden:
    """Golden snapshot for the PDC dispatch path (PDC-vs-missile)."""

    def test_pdc_targets_enemy_missile_from_context(self):
        """A PDC weapon scans context['projectiles'] for enemy missiles and
        produces a beam attack against the missile. Pins the dispatch shape."""
        targeting = TargetingSystem()
        firing = WeaponFiringSystem(targeting)

        ship = _make_ship()
        ship.current_target = None  # no primary target

        # Enemy missile in context
        enemy_missile = MagicMock()
        enemy_missile.is_alive = True
        enemy_missile.team_id = 1
        enemy_missile.type = AttackType.MISSILE
        enemy_missile.position = Vector2(50.0, 0.0)
        enemy_missile.velocity = Vector2(0.0, 0.0)

        weapon_ab = MagicMock()
        weapon_ab.can_fire = MagicMock(return_value=True)
        weapon_ab.fire = MagicMock(return_value=True)
        weapon_ab.damage = 5
        weapon_ab.range = 200
        weapon_ab.check_firing_solution = MagicMock(return_value=True)
        weapon_ab.pdc_valid_targets = ["MISSILE", "FIGHTER"]

        beam_ab = MagicMock()
        beam_ab.pdc_valid_targets = ["MISSILE", "FIGHTER"]

        weapon = _make_weapon_component(
            family_abilities=['BeamWeaponAbility'],
            weapon_ab=weapon_ab,
            family_ab=beam_ab,
            is_pdc=True,
        )
        ship.iter_components = MagicMock(return_value=[(LayerType.OUTER, weapon)])

        attacks = firing.fire_weapons(ship, context={'projectiles': [enemy_missile]})

        assert len(attacks) == 1
        attack = attacks[0]
        # PROJ-359 Phase 4: PDC dispatch now produces a BeamResolution (typed)
        # rather than a dict.
        from game.simulation.combat.attack_contract import BeamResolution
        assert isinstance(attack, BeamResolution)
        assert attack.type is AttackType.BEAM
        assert attack.target is enemy_missile
        assert attack.component is weapon
        assert attack.hit is True

    def test_pdc_collision_against_missile_uses_take_damage(self):
        """Beam against a Projectile (missile) target uses target.take_damage
        (not combat_engine.take_damage) — pinned engine-layer behavior."""
        rng = random.Random(0)
        rng.random = lambda: 0.0
        cs = CollisionSystem(rng=rng)

        # Missile target — has take_damage but no combat_engine
        missile = MagicMock(spec=['is_alive', 'position', 'radius', 'total_defense_score',
                                  'fleet_defense_bonus', 'take_damage'])
        missile.is_alive = True
        missile.position = Vector2(50.0, 0.0)
        missile.radius = 3.0
        missile.total_defense_score = 0.0
        missile.fleet_defense_bonus = None

        beam_ab = MagicMock()
        beam_ab.calculate_hit_chance = MagicMock(return_value=0.99)
        beam_ab.get_damage = MagicMock(return_value=5.0)

        beam_comp = MagicMock()
        beam_comp.get_ability = lambda name: beam_ab if name == 'BeamWeaponAbility' else None
        beam_comp.shots_hit = 0

        source = MagicMock()
        source.get_total_sensor_score = MagicMock(return_value=0.0)
        source.fleet_attack_bonus = None

        from game.simulation.combat.attack_contract import BeamResolution
        attack = BeamResolution(
            source=source,
            component=beam_comp,
            target=missile,
            damage=5.0,
            range=200.0,
            origin=Vector2(0.0, 0.0),
            direction=Vector2(1.0, 0.0),
            hit=True,
        )
        cs.process_beam_attack(attack, [])

        # Missile path: target.take_damage(damage), NOT combat_engine.take_damage
        missile.take_damage.assert_called_once_with(5.0)
        assert beam_comp.shots_hit == 1


# ---------------------------------------------------------------------------
# Targeting golden — PDC vs non-PDC restrictions
# ---------------------------------------------------------------------------


class TestTargetingGolden:
    """Golden snapshot for targeting filter rules per family."""

    def test_non_pdc_cannot_target_missiles(self):
        targeting = TargetingSystem()
        ship = _make_ship()

        missile = MagicMock()
        missile.is_alive = True
        missile.team_id = 1
        missile.type = AttackType.MISSILE
        missile.position = Vector2(50.0, 0.0)
        missile.velocity = Vector2(0.0, 0.0)

        weapon_ab = MagicMock()
        weapon_ab.check_firing_solution = MagicMock(return_value=True)

        beam_ab = MagicMock()
        beam_ab.pdc_valid_targets = ["MISSILE", "FIGHTER"]

        weapon = _make_weapon_component(
            family_abilities=['BeamWeaponAbility'],
            weapon_ab=weapon_ab,
            family_ab=beam_ab,
            is_pdc=False,  # NON-PDC
        )

        result = targeting.find_valid_target(ship, None, [missile], weapon, weapon_ab)
        assert result is None  # Non-PDC weapons cannot target missiles

    def test_pdc_targets_only_missile_or_fighter_types(self):
        targeting = TargetingSystem()
        ship = _make_ship()

        # A non-missile non-fighter ship (vehicle_type='destroyer')
        ship_target = MagicMock()
        ship_target.is_alive = True
        ship_target.team_id = 1
        ship_target.type = 'ship'
        ship_target.position = Vector2(50.0, 0.0)
        ship_target.velocity = Vector2(0.0, 0.0)
        ship_target.vehicle_type = 'destroyer'

        weapon_ab = MagicMock()
        weapon_ab.check_firing_solution = MagicMock(return_value=True)
        weapon_ab.pdc_valid_targets = ["MISSILE", "FIGHTER"]

        beam_ab = MagicMock()
        beam_ab.pdc_valid_targets = ["MISSILE", "FIGHTER"]

        weapon = _make_weapon_component(
            family_abilities=['BeamWeaponAbility'],
            weapon_ab=weapon_ab,
            family_ab=beam_ab,
            is_pdc=True,
        )

        result = targeting.find_valid_target(ship, None, [ship_target], weapon, weapon_ab)
        assert result is None  # destroyer not in pdc_valid_targets

    def test_seeker_uses_endurance_range_gate(self):
        """Seeker targeting checks `projectile_speed * endurance * SEEKER_MAX_RANGE_MULTIPLIER`
        rather than `weapon_ab.check_firing_solution`."""
        targeting = TargetingSystem()
        ship = _make_ship()

        target = _make_ship(team_id=1, position=(50.0, 0.0))

        weapon_ab = MagicMock()
        # Make sure check_firing_solution is NOT what gates seeker
        weapon_ab.check_firing_solution = MagicMock(return_value=False)

        seeker_ab = MagicMock()
        seeker_ab.projectile_speed = 300
        seeker_ab.endurance = 100  # 300 * 100 * mult >> 50

        weapon = _make_weapon_component(
            family_abilities=['SeekerWeaponAbility'],
            weapon_ab=weapon_ab,
            family_ab=seeker_ab,
        )

        result = targeting.find_valid_target(ship, target, [], weapon, weapon_ab)
        assert result is target  # Seeker accepts based on its own range gate
