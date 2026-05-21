"""CombatSubsystems -- per-battle bundle of ship-combat subsystems (PROJ-471).

Historically ``ShipCombatEngine`` held its ``TargetingSystem`` /
``DamageCalculator`` / ``WeaponFiringSystem`` as **class-level** attributes,
shared across every ship instance and leaking across battles and tests
(state-isolation bug, PROJ-471 Task 1.2).

The subsystems are nonetheless genuinely *shared within a single battle*: the
seeded ``DamageCalculator(rng=engine.rng)`` must reach every ship so damage
distribution is deterministic, the ram/mine resolvers borrow that same
calculator, and one bus-wired ``WeaponFiringSystem`` services all ships.

This bundle makes that sharing explicit and per-battle instead of per-class:
``BattleEngine`` owns one ``CombatSubsystems`` per ``start()`` and injects it
into each ship's ``ShipCombatEngine``. Standalone ``ShipCombatEngine``
construction (tests, non-battle paths) gets its own fresh per-instance bundle,
so no state leaks between instances.
"""
from __future__ import annotations

from dataclasses import dataclass
import random

from game.simulation.combat.targeting_system import TargetingSystem
from game.simulation.combat.damage_calculator import DamageCalculator
from game.simulation.combat.weapon_firing_system import WeaponFiringSystem


@dataclass
class CombatSubsystems:
    """The three stateless-ish combat subsystems shared within one battle."""

    targeting_system: TargetingSystem
    damage_calculator: DamageCalculator
    weapon_firing_system: WeaponFiringSystem

    @classmethod
    def create_default(
        cls,
        *,
        rng: random.Random | None = None,
        damage_calculator: DamageCalculator | None = None,
        event_bus: object | None = None,
    ) -> "CombatSubsystems":
        """Build a fresh bundle.

        Args:
            rng: Seeded RNG threaded into a new ``DamageCalculator`` when
                ``damage_calculator`` is not supplied. ``None`` -> the
                ``DamageCalculator`` default (unseeded) RNG.
            damage_calculator: Pre-built (already-seeded) calculator to adopt
                verbatim. Takes precedence over ``rng``.
            event_bus: Optional session ``EventBus`` wired into the
                ``WeaponFiringSystem``.
        """
        targeting = TargetingSystem()
        if damage_calculator is None:
            damage_calculator = DamageCalculator(rng=rng)
        firing = WeaponFiringSystem(targeting, event_bus=event_bus)
        return cls(
            targeting_system=targeting,
            damage_calculator=damage_calculator,
            weapon_firing_system=firing,
        )
