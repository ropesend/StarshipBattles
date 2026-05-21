"""PROJ-471 Task 1.2 regression tests.

The ShipCombatEngine subsystems (TargetingSystem / DamageCalculator /
WeaponFiringSystem) were previously CLASS-level attributes shared across every
ship instance and leaking across battles and tests. They are now per-instance,
optionally sourced from a per-battle ``CombatSubsystems`` bundle owned by the
BattleEngine. These tests pin two invariants:

1. Two standalone ShipCombatEngine instances must have DISTINCT subsystems
   (no class-level shared state -> no cross-battle / cross-test leakage).
2. When a ``CombatSubsystems`` bundle is injected, the engine uses exactly
   that bundle's subsystems (this is how the per-battle seeded DamageCalculator
   reaches every ship -- determinism is preserved).
"""

from unittest.mock import MagicMock

from game.simulation.entities.ship_combat_engine import ShipCombatEngine


class TestSubsystemsArePerInstance:
    def test_two_engines_have_distinct_subsystems(self):
        """No class-level sharing: each engine owns its own subsystems."""
        engine_a = ShipCombatEngine(MagicMock())
        engine_b = ShipCombatEngine(MagicMock())

        assert engine_a._targeting_system is not engine_b._targeting_system
        assert engine_a._damage_calculator is not engine_b._damage_calculator
        assert engine_a._weapon_firing_system is not engine_b._weapon_firing_system

    def test_no_class_level_subsystem_state_leaks(self):
        """Constructing an engine must not populate class attributes."""
        # Whatever the class declares, constructing instances must not turn the
        # class attribute into a populated shared object.
        ShipCombatEngine(MagicMock())
        assert ShipCombatEngine.__dict__.get("_targeting_system") is None
        assert ShipCombatEngine.__dict__.get("_damage_calculator") is None
        assert ShipCombatEngine.__dict__.get("_weapon_firing_system") is None


class TestSubsystemsBundleInjection:
    def test_injected_bundle_subsystems_are_used(self):
        """Injecting a CombatSubsystems bundle threads its subsystems in."""
        from game.simulation.combat.combat_subsystems import CombatSubsystems
        from game.simulation.combat.targeting_system import TargetingSystem
        from game.simulation.combat.damage_calculator import DamageCalculator
        from game.simulation.combat.weapon_firing_system import WeaponFiringSystem

        targeting = TargetingSystem()
        damage = DamageCalculator()
        firing = WeaponFiringSystem(targeting)
        bundle = CombatSubsystems(
            targeting_system=targeting,
            damage_calculator=damage,
            weapon_firing_system=firing,
        )

        engine = ShipCombatEngine(MagicMock(), subsystems=bundle)

        assert engine._targeting_system is targeting
        assert engine._damage_calculator is damage
        assert engine._weapon_firing_system is firing

    def test_two_engines_sharing_a_bundle_share_subsystems(self):
        """All ships in one battle share the engine-owned bundle (determinism)."""
        from game.simulation.combat.combat_subsystems import CombatSubsystems

        bundle = CombatSubsystems.create_default()
        engine_a = ShipCombatEngine(MagicMock(), subsystems=bundle)
        engine_b = ShipCombatEngine(MagicMock(), subsystems=bundle)

        assert engine_a._damage_calculator is engine_b._damage_calculator
        assert engine_a._targeting_system is engine_b._targeting_system

    def test_bundle_carries_seeded_damage_calculator(self):
        """The bundle's DamageCalculator preserves the injected (seeded) RNG."""
        import random
        from game.simulation.combat.combat_subsystems import CombatSubsystems
        from game.simulation.combat.damage_calculator import DamageCalculator

        seeded_rng = random.Random(12345)
        damage = DamageCalculator(rng=seeded_rng)
        bundle = CombatSubsystems.create_default(damage_calculator=damage)

        engine = ShipCombatEngine(MagicMock(), subsystems=bundle)
        assert engine._damage_calculator.rng is seeded_rng
