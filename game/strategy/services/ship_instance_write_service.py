"""ShipInstanceWriteService — owns ShipInstance writes from outside the data class.

PROJ-370 Phase 5: implements ``IShipInstanceMutator``. Single owner service
for the 14 ShipInstance mutation surfaces. Cargo and consumable writes are
forwarded to the existing ``ShipCargoManager`` / ``ShipConsumableManager``;
those managers are co-located with ``ShipInstance`` in ``data/`` and treated
as data-class-internal by the AST guard.

Wiring:
    Constructed in ``GameSession.__init__``. Threaded through
    ``TurnEngineConfig.create_default()`` and into PostBattleHook /
    EnvironmentalHazardEngine via constructor kwargs.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


__all__ = ["ShipInstanceWriteService"]


class ShipInstanceWriteService:
    """Concrete ``IShipInstanceMutator`` implementation."""

    # ------------------------------------------------------------------
    # Status flags
    # ------------------------------------------------------------------
    def set_is_alive(self, instance: "ShipInstance", value: bool) -> None:
        instance.is_alive = bool(value)

    def set_is_derelict(self, instance: "ShipInstance", value: bool) -> None:
        instance.is_derelict = bool(value)

    def set_current_hp(
        self, instance: "ShipInstance", value: float | None
    ) -> None:
        instance.current_hp = value

    # ------------------------------------------------------------------
    # Component dict (post-battle replacement) — also invalidates stats cache
    # ------------------------------------------------------------------
    def replace_components(
        self, instance: "ShipInstance", new_components: dict
    ) -> None:
        """Replace the components dict and invalidate the cached stats.

        The post-battle hook used to do these two writes in sequence; the
        mutator bundles them so callers cannot forget the cache
        invalidation.
        """
        instance.components = new_components
        if hasattr(instance, "invalidate_stats_cache"):
            instance.invalidate_stats_cache()

    # ------------------------------------------------------------------
    # Cargo / consumables (forward to managers)
    # ------------------------------------------------------------------
    def set_cargo_amount(
        self, instance: "ShipInstance", resource_id: str, amount: float
    ) -> None:
        # The ShipCargoManager owns the capacity-aware write; we forward
        # to it so existing semantics (capacity clamp, sparse-key cleanup)
        # are preserved.
        manager = getattr(instance, "_cargo_manager", None)
        if manager is not None and hasattr(manager, "set_cargo"):
            manager.set_cargo(resource_id, amount)
        else:
            instance.cargo_contents[resource_id] = amount

    def set_consumable_level(
        self, instance: "ShipInstance", resource_id: str, level: float
    ) -> None:
        manager = getattr(instance, "_consumable_manager", None)
        if manager is not None and hasattr(manager, "set_level"):
            manager.set_level(resource_id, level)
        else:
            instance.consumable_levels[resource_id] = level

    # ------------------------------------------------------------------
    # Carried items (drop pods, etc.)
    # ------------------------------------------------------------------
    def add_carried_item(self, instance: "ShipInstance", item: Any) -> None:
        instance.carried_items.append(item)

    def pop_carried_item(
        self, instance: "ShipInstance", index: int = -1
    ) -> Any:
        return instance.carried_items.pop(index)

    # ------------------------------------------------------------------
    # Per-component toggles & activation states
    # ------------------------------------------------------------------
    def set_component_toggle(
        self, instance: "ShipInstance", component_id: str, enabled: bool
    ) -> None:
        instance.component_toggles[component_id] = bool(enabled)

    def set_activation_state(
        self, instance: "ShipInstance", component_id: str, state: Any
    ) -> None:
        instance.activation_states[component_id] = state

    # ------------------------------------------------------------------
    # Combat record
    # ------------------------------------------------------------------
    def increment_battles_survived(self, instance: "ShipInstance") -> None:
        instance.battles_survived = int(getattr(instance, "battles_survived", 0)) + 1

    def add_experience(
        self, instance: "ShipInstance", amount: float
    ) -> None:
        instance.experience = float(getattr(instance, "experience", 0.0)) + float(amount)

    def add_kill(self, instance: "ShipInstance") -> None:
        instance.kills = int(getattr(instance, "kills", 0)) + 1
