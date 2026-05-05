"""
Defense stat contributor — armor pool, shields, regen, repair, armor abilities.

Splits two phases of the legacy calculator:

1. ``aggregate_defense`` (per-component): armor max-HP pool, ShieldProjection,
   ShieldRegeneration, and the shield-energy-cost passthrough that lives on
   shield-regen components' ResourceConsumption(energy) ability.
2. ``apply_armor_and_repair_scores`` (post-aggregation): EmissiveArmor,
   ShieldRegeneratingArmor, ShipRepair totals computed against active
   components (destroyed armor contributes nothing).

PROJ-360 Phase 2: extracted verbatim from
``ShipStatsCalculator._aggregate_defense_abilities`` and the matching block
in ``_phase_sensor_defense_scores``. No semantic change — golden snapshot
guards bit-equality.
"""
from __future__ import annotations

from typing import Any, Dict, List, TYPE_CHECKING

from game.core.constants import LayerType
from game.simulation.entities.ability_aggregator import get_ability_total
from game.simulation.entities.stat_contributors.registry import (
    is_builtin_suppressed_for,
)

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship


def aggregate_defense(ship: "Ship", comp: "Component", acc: Dict[str, Any]) -> None:
    """Aggregate armor HP pool, ShieldProjection, ShieldRegeneration, shield energy cost.

    Mutations:

    - ``ship.layers[LayerType.ARMOR].max_hp_pool`` (direct, bypasses ``acc``)
    - ``acc['max_shields']``, ``acc['shield_regen']``, ``acc['shield_cost']``

    PROJ-360 audit:

    - EXT-02: ``ShieldProjection`` and ``ShieldRegeneration`` blocks respect
      ``is_builtin_suppressed_for`` so a registered contributor can fully
      replace the built-in handling for either ability without double-counting.
    - EXT-05: shield energy cost is read via the typed
      ``get_abilities("ResourceConsumption")`` path filtered on
      ``resource_type == "energy"`` instead of scanning all
      ``comp.ability_instances``.
    """
    # Armor HP pool (using ability-based detection)
    if comp.abilities.get("Armor", False):
        if LayerType.ARMOR in ship.layers:
            ship.layers[LayerType.ARMOR].max_hp_pool += comp.max_hp

    # Shields from ShieldProjection abilities
    if not is_builtin_suppressed_for("ShieldProjection"):
        for ab in comp.get_abilities("ShieldProjection"):
            acc["max_shields"] += ab.capacity

    # Shield regen from ShieldRegeneration abilities + energy cost.
    # Note: shield-energy-cost extraction is colocated with the
    # ShieldRegeneration handling because both are tied to the same
    # underlying component role. Suppressing ShieldRegeneration takes
    # over both legacy responsibilities — extension contributors that
    # need only one half should still register their own substitute.
    if not is_builtin_suppressed_for("ShieldRegeneration"):
        for ab in comp.get_abilities("ShieldRegeneration"):
            acc["shield_regen"] += ab.rate

        # Shield energy cost from ResourceConsumption(energy) on shield-regen
        # components. EXT-05 fix: typed `get_abilities("ResourceConsumption")`
        # iterates only the resource-consumption instances, not the entire
        # ability list. Legacy "first match wins" + `has_ability` gate
        # semantics preserved.
        if comp.has_ability("ShieldRegeneration"):
            for ab in comp.get_abilities("ResourceConsumption"):
                if getattr(ab, "resource_type", None) == "energy":
                    acc["shield_cost"] += ab.amount
                    break


def apply_armor_and_repair_scores(
    ship: "Ship",
    component_pool: List["Component"],
) -> None:
    """Phase-5 post-aggregation: emissive armor, shield-regen armor, repair rate.

    Armor abilities count only on active components (destroyed armor has no
    effect). Repair rate sums over the full pool — matches legacy behavior.

    Mutations:

    - ``ship.emissive_armor``, ``ship.shield_regenerating_armor``, ``ship.repair_rate``
    """
    active_pool = [c for c in component_pool if c.is_active]
    ship.emissive_armor = get_ability_total(active_pool, "EmissiveArmor")
    ship.shield_regenerating_armor = get_ability_total(active_pool, "ShieldRegeneratingArmor")
    ship.repair_rate = get_ability_total(component_pool, "ShipRepair")


def init_armor_pool(ship: "Ship") -> None:
    """First-time fill of the armor HP pool to its max capacity.

    Idempotent: only fills when ``hp_pool`` is exactly 0 (initial state).
    Subsequent recalculations leave damaged pools alone.
    """
    if LayerType.ARMOR not in ship.layers:
        return
    armor = ship.layers[LayerType.ARMOR]
    if armor.hp_pool == 0:
        armor.hp_pool = armor.max_hp_pool
