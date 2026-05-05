"""PROJ-359 Phase 3.4: PDC weapon family handler.

PDC is a Beam-role weapon: it shares the firing-side `BeamResolution` shape
with the Beam family. The distinguishing semantics are:

1. PDC weapons are allowed to target enemy missiles (other beam-role weapons
   cannot).
2. The firing system injects enemy missiles from `context['projectiles']`
   into the candidate-target list when firing PDC weapons.
3. PDC weapons can only fire at target types listed in
   `pdc_valid_targets` on their `BeamWeaponAbility` (default
   `["MISSILE", "FIGHTER"]`).

Items 1 and 2 are reflected in `FAMILY_METADATA[WeaponFamily.PDC]` (see
`attack_contract.py`); the firing/targeting systems consult metadata rather
than the legacy `comp.has_pdc_ability()` string lookup. Item 3 stays on the
component (`pdc_valid_targets` is per-weapon configuration, not per-family
policy).
"""
from __future__ import annotations

from game.core.math import Vector2
from game.simulation.combat.attack_contract import (
    AttackRequest,
    AttackResolution,
    BeamResolution,
    WeaponFamily,
)
from game.simulation.combat.weapon_registry import WEAPON_REGISTRY


class PDCHandler:
    """PDC family handler — emits a BeamResolution identical in shape to the
    Beam family. The firing-time logic is the same; targeting-time filters
    diverge per `FAMILY_METADATA`."""

    def fire(self, request: AttackRequest) -> AttackResolution:
        ship = request.source
        comp = request.component
        weapon_ab = request.weapon_ability
        target = request.target
        aim_vec = request.aim_vec

        direction = aim_vec.normalize() if aim_vec.length() > 0 else Vector2(1, 0)
        return BeamResolution(
            source=ship,
            component=comp,
            target=target,
            damage=weapon_ab.damage,
            range=weapon_ab.range,
            origin=ship.position,
            direction=direction,
            hit=True,
        )


WEAPON_REGISTRY.register(WeaponFamily.PDC, PDCHandler())
