"""PROJ-359 Phase 3.1: Beam weapon family handler.

Owns the firing-side construction of a `BeamResolution` for a Beam weapon.
The PDC role is registered separately (`families/pdc.py`) because its
firing/targeting semantics diverge — even though both use a
`BeamWeaponAbility` underneath.
"""
from __future__ import annotations

from game.simulation.combat.attack_contract import (
    AttackRequest,
    AttackResolution,
    WeaponFamily,
)
from game.simulation.combat.families._beam_common import build_beam_resolution
from game.simulation.combat.weapon_registry import WEAPON_REGISTRY


class BeamHandler:
    """Beam weapon family handler.

    Constructs a `BeamResolution` whose field set mirrors the legacy beam
    dict 1:1. PROJ-359 audit (MAJ-002): construction is delegated to
    `_beam_common.build_beam_resolution` so this handler and `PDCHandler`
    cannot drift apart.
    """

    def fire(self, request: AttackRequest) -> AttackResolution:
        return build_beam_resolution(request)


WEAPON_REGISTRY.register(WeaponFamily.BEAM, BeamHandler())
