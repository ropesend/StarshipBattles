"""PROJ-FMS-A Phase 2 — mine warheads, laserheads, and ram-target abilities.

These three classes are data-bearing skeletons. They expose their config
attributes for the validator, design library, and stat aggregator, but
combat behavior (mine trigger, beam fire, ram damage) lands in PROJ-FMS-B.

Files split out from ``weapons.py`` to keep that module under the 500-LOC
ceiling and to keep the mine-specific surface area discoverable from a
single module.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .base import Ability, AbilityLayer
from .stat_keys import AbilityStatBinding
from .ui_colors import HINT_DAMAGE, HINT_NEUTRAL
from .weapons import BeamWeaponAbility


class WarheadAbility(Ability):
    """Single-use explosive warhead.

    Carried by mines (primary use) and by fighters/ships for kamikaze /
    ram-attack designs. Detonation is unconditional once triggered — there
    is no second accuracy roll. Behavior wired in PROJ-FMS-B Phase 3 (mine
    resolver + ram pipeline). For PROJ-FMS-A this is purely a data carrier.

    Data shape:
        Dict: ``{"damage": <int>}``
        Scalar: ``50`` (treated as ``damage``)

    Attributes:
        damage: Detonation damage value, applied via the damage pipeline.
    """

    layer = AbilityLayer.BOTH

    # No modifier stat bindings — warheads carry static damage.
    STAT_BINDINGS: List[AbilityStatBinding] = []

    def _parse_attrs(self, data: Any) -> None:
        """Parse ``damage`` from dict or scalar data."""
        if isinstance(data, dict):
            self.damage = float(data.get("damage", 0))
        elif isinstance(data, (int, float)):
            self.damage = float(data)
        else:
            self.damage = 0.0

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


class RamTargetAbility(Ability):
    """Marks a vehicle as able to designate a ram target.

    On collision with the assigned target, every :class:`WarheadAbility`
    on the rammer detonates against it via the damage pipeline; rammer
    is destroyed. Designs that carry warheads without a ``RamTarget``
    ability cannot self-detonate on contact — they remain inert.

    Behavior wired in PROJ-FMS-B Phase 4 (ram resolver hook). For
    PROJ-FMS-A this class only stores the optional ``target_id`` runtime
    state so designs can validate and the engine has a place to hang
    state onto.
    """

    layer = AbilityLayer.COMBAT

    STAT_BINDINGS: List[AbilityStatBinding] = []

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        # Runtime state — not data-derived, not serialised through ``data``.
        # Combat engine sets this when the player picks a target; resolver
        # reads it on collision.
        self.target_id: str | None = None

    def get_primary_value(self) -> float:
        return 1.0

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        return [{
            "label": "Ram Target",
            "value": "Active" if self.target_id else "Idle",
            "color_hint": HINT_NEUTRAL,
        }]
