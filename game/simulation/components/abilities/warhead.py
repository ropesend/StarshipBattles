"""Mine warheads and laserheads — explosive and beam payloads.

Originally PROJ-FMS-A Phase 2 also defined ``RamTargetAbility`` here as
a marker for kamikaze-capable designs. That gate was removed by the
QA 2026-05-16 Obs 1b ramming redesign — ramming is now a universal
tactical action driven by ``RamTargetResolver.set_ram_target(...)``
rather than an ability-gated capability. See
``game/simulation/combat/ram_target_resolver.py``.

``WarheadAbility`` exposes a ``consumed: bool`` flag so the resolver
can mark warheads as one-shot detonated at collision time (mirrors
``BeamWeaponAbility.consume_on_fire`` for laserheads).
"""
from __future__ import annotations

from typing import Any, Dict, List

from .base import Ability, AbilityLayer
from .stat_keys import AbilityStatBinding, StatKey
from .ui_colors import HINT_DAMAGE
from .weapons import BeamWeaponAbility


class WarheadAbility(Ability):
    """Single-use explosive warhead.

    Carried by mines (primary use) and by fighters/ships for kamikaze /
    ram-attack designs. Detonation is unconditional once triggered — there
    is no second accuracy roll.

    Data shape:
        Dict: ``{"damage": <int>}``
        Scalar: ``50`` (treated as ``damage``)

    Attributes:
        damage: Effective detonation damage (``_base_damage`` scaled by
            ``damage_mult`` modifiers — e.g. ``simple_size_mount``).
        _base_damage: Authored damage value before modifier scaling.

    QA Obs 1 (2026-05-16): ``DAMAGE_MULT`` binding lets warheads scale
    through the same ``simple_size_mount`` modifier the rest of the
    weapon abilities use. Removes the need for parallel
    ``warhead_small / medium / large`` component tiers — one component
    plus a size-mount param produces any explosive yield.
    """

    layer = AbilityLayer.BOTH

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.DAMAGE_MULT, 'damage', 'multiply', '_base_damage'),
    ]

    def _parse_attrs(self, data: Any) -> None:
        """Parse ``damage`` from dict or scalar data."""
        if isinstance(data, dict):
            self._base_damage = float(data.get("damage", 0))
        elif isinstance(data, (int, float)):
            self._base_damage = float(data)
        else:
            self._base_damage = 0.0
        self.damage = self._base_damage
        # QA Obs 1b (2026-05-16): one-shot consumption flag set by
        # ``RamTargetResolver`` after a ram collision (and reusable by
        # any future one-shot detonation path). Once True, the warhead
        # contributes 0 damage; the resolver also zeros ``damage`` so
        # subsequent collisions see no contribution.
        self.consumed = False

    def recalculate(self) -> None:
        """Re-apply ``damage_mult`` after modifier stats change."""
        if self.consumed:
            return
        self.damage = self._base_damage * self.get_effective_stat(
            'damage_mult', 1.0,
        )

    def get_primary_value(self) -> float:
        return float(self.damage)

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        return [{
            "label": "Warhead Damage",
            "value": f"{self.damage:.0f}",
            "color_hint": HINT_DAMAGE,
        }]


class LaserheadAbility(BeamWeaponAbility):
    """Single-shot beam weapon mounted on mines.

    Subclasses :class:`BeamWeaponAbility` so the existing MRO-based
    family-detection at ``weapon_registry.py:78-94`` recognises it as the
    beam family without modification — the ``has_ability('BeamWeaponAbility')``
    check sees the inherited ability class through the component's
    ``ability_instances`` list.

    Adds one mine-specific data attribute: ``consume_on_fire``. The actual
    consume-after-fire logic is wired in PROJ-FMS-B Phase 3 by the tactical
    minefield resolver — this class only exposes the flag.
    """

    layer = AbilityLayer.BOTH

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        if isinstance(data, dict):
            self.consume_on_fire = bool(data.get("consume_on_fire", True))
        else:
            self.consume_on_fire = True

    def sync_data(self, data: Any) -> None:
        super().sync_data(data)
        if isinstance(data, dict) and "consume_on_fire" in data:
            self.consume_on_fire = bool(data["consume_on_fire"])


# NOTE: ``RamTargetAbility`` and its ``ram_target_module`` component were
# removed by the QA 2026-05-16 Obs 1b ramming redesign. Ramming is now a
# universal tactical action — any vehicle with movement can be assigned a
# ram target through ``RamTargetResolver.set_ram_target(rammer, target)``,
# and the resolver applies symmetric damage on collision. Kamikaze
# behaviour comes from the AI controller setting the ram target on spawn,
# not from a component on the design.
