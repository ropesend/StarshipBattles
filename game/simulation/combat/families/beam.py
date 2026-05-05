"""PROJ-359 Phase 3.1: Beam weapon family handler.

Owns the firing-side construction of a `BeamResolution` for a Beam weapon.
The PDC role is registered separately (`families/pdc.py`) because its
firing/targeting semantics diverge — even though both use a
`BeamWeaponAbility` underneath.
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


class BeamHandler:
    """Beam weapon family handler.

    Constructs a `BeamResolution` whose field set mirrors the legacy beam
    dict 1:1. The engine layer (`game/engine/collision.py`) still consumes
    a dict in Phase 3; the firing system adapts the resolution to the dict
    shape at the dispatch boundary. Phase 4 collapses that adapter.
    """

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


WEAPON_REGISTRY.register(WeaponFamily.BEAM, BeamHandler())
