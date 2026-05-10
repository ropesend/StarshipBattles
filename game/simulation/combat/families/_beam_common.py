"""PROJ-359: Shared construction helper for beam-shaped resolutions.

Both the BEAM and PDC family handlers emit a `BeamResolution` with the same
field set — they are both Beam-role weapons (PDC is a Beam-role weapon with
the 'pdc' tag and missile-targeting privileges). The targeting/firing
divergence between them is encoded in `FAMILY_METADATA`, not in the firing-
side resolution shape.

PROJ-359 audit (MAJ-002): the two handlers previously held byte-identical
`.fire()` bodies with no shared base. If `BeamResolution` gains a field both
handlers must update in lockstep — easy to miss. This helper centralises the
construction so adding a field is a one-place edit, and the two handlers stay
in sync by construction.
"""
from __future__ import annotations

from game.core.math import Vector2
from game.simulation.combat.attack_contract import AttackRequest, BeamResolution


def build_beam_resolution(request: AttackRequest) -> BeamResolution:
    """Build the canonical `BeamResolution` for a beam-role family.

    Used by both `BeamHandler` and `PDCHandler`. The resolution shape is
    identical for both families; per-family divergence is consumed elsewhere
    (targeting filters, missile-context injection) via `FAMILY_METADATA`.
    """
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
