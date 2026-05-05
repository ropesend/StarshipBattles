"""
Defense stat contributor — armor pool, shields, regen, repair, armor abilities.

Splits two phases of the legacy calculator:

1. Phase-3 per-ability contributors (registered into
   ``STAT_CONTRIBUTOR_REGISTRY``) — armor max-HP pool, ShieldProjection,
   ShieldRegeneration (which carries the shield-energy-cost passthrough on
   the shield-regen component's ResourceConsumption(energy) ability).
2. ``apply_armor_and_repair_scores`` (post-aggregation, Phase-5):
   EmissiveArmor, ShieldRegeneratingArmor, ShipRepair totals computed
   against active components (destroyed armor contributes nothing).

PROJ-360 Phase 2: extracted from
``ShipStatsCalculator._aggregate_defense_abilities`` and the matching block
in ``_phase_sensor_defense_scores``. PROJ-367 Phase 2: split into per-ability
``contribute_*`` functions that the registry seeds as default Phase-3
contributors at module import. ``apply_armor_and_repair_scores`` and
``init_armor_pool`` (Phase-5) stay imperative — out of scope.
"""
from __future__ import annotations

from typing import Any, Dict, List, TYPE_CHECKING

from game.core.constants import LayerType
from game.simulation.entities.ability_aggregator import get_ability_total

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship


# ---------------------------------------------------------------------------
# Per-ability Phase-3 contributors (PROJ-367 Phase 2)
# ---------------------------------------------------------------------------


def contribute_armor(
    ship: "Ship", comp: "Component", acc: Dict[str, Any]
) -> None:
    """Add this Armor component's max_hp into the ship's armor HP pool.

    Note: this contributor mutates ``ship`` directly, NOT ``acc`` — the armor
    pool is a side-channel on ``ship.layers[LayerType.ARMOR].max_hp_pool``.
    Kept for signature uniformity with the rest of the contributor surface.
    """
    if LayerType.ARMOR in ship.layers:
        ship.layers[LayerType.ARMOR].max_hp_pool += comp.max_hp


def contribute_shield_projection(
    ship: "Ship", comp: "Component", acc: Dict[str, Any]
) -> None:
    """Sum ShieldProjection capacity into ``acc['max_shields']``."""
    for ab in comp.get_abilities("ShieldProjection"):
        acc["max_shields"] += ab.capacity


def contribute_shield_regeneration(
    ship: "Ship", comp: "Component", acc: Dict[str, Any]
) -> None:
    """Sum ShieldRegeneration rate + first-match shield energy cost.

    The shield-energy-cost passthrough is colocated with the regen
    contributor: shields-regen components carry a ResourceConsumption(energy)
    ability that the legacy code reads as the per-tick energy cost. This
    coupling is preserved for golden-snapshot bit-equality. (Splitting it
    into a separate contributor would require a `ShieldRegenEnergy` predicate
    that doesn't exist; future project required.)
    """
    for ab in comp.get_abilities("ShieldRegeneration"):
        acc["shield_regen"] += ab.rate

    # Shield energy cost from ResourceConsumption(energy) on shield-regen
    # components. EXT-05 fix from PROJ-360: typed
    # `get_abilities("ResourceConsumption")` iterates only consumption
    # instances; "first-match-wins" semantics preserved.
    if comp.has_ability("ShieldRegeneration"):
        for ab in comp.get_abilities("ResourceConsumption"):
            if getattr(ab, "resource_type", None) == "energy":
                acc["shield_cost"] += ab.amount
                break


# ---------------------------------------------------------------------------
# Phase-5 helpers — UNCHANGED, out-of-scope for PROJ-367 Phase 2.
# ---------------------------------------------------------------------------


def apply_armor_and_repair_scores(
    ship: "Ship",
    component_pool: List["Component"],
) -> None:
    """Phase-5 post-aggregation: emissive armor, shield-regen armor, repair rate.

    Armor abilities count only on active components (destroyed armor has no
    effect). Repair rate sums over the full pool — matches legacy behavior.
    """
    active_pool = [c for c in component_pool if c.is_active]
    ship.emissive_armor = get_ability_total(active_pool, "EmissiveArmor")
    ship.shield_regenerating_armor = get_ability_total(active_pool, "ShieldRegeneratingArmor")
    ship.repair_rate = get_ability_total(component_pool, "ShipRepair")


def init_armor_pool(ship: "Ship") -> None:
    """First-time fill of the armor HP pool to its max capacity (idempotent)."""
    if LayerType.ARMOR not in ship.layers:
        return
    armor = ship.layers[LayerType.ARMOR]
    if armor.hp_pool == 0:
        armor.hp_pool = armor.max_hp_pool
