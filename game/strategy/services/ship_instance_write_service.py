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


__all__ = ["ShipInstanceWriteService", "_DEFAULT_MAX_HP"]


# Fallback if stats dict lacks ``max_hp`` (should not happen with proper DI).
_DEFAULT_MAX_HP = 100


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
        # PROJ-436 Phase 3b: the ``set_cargo`` manager method is now
        # guaranteed to exist on every real ship instance (Phase 3b made
        # it a first-class part of ``ShipCargoManager``). Previously
        # this was a ``hasattr`` fallback; the fallback path is gone
        # because the dict-write would bypass the stable manager API
        # that Phase 3f's substrate cutover depends on.
        instance._cargo_mgr.set_cargo(resource_id, int(amount))

    def set_consumable_level(
        self, instance: "ShipInstance", resource_id: str, level: float
    ) -> None:
        # PROJ-436 Phase 3b: route through the stable ``set_level``
        # manager API; see ``set_cargo_amount`` comment.
        instance._resource_mgr.set_level(resource_id, level)

    # ------------------------------------------------------------------
    # PROJ-431 Phase 1f: ``add_carried_item`` / ``pop_carried_item``
    # removed. No production callers. Mutations to the carried bay /
    # pods go through the typed :class:`BayInventory` surface
    # (``ShipCargoManager.load_vehicle`` / ``unload_vehicle``) or
    # :meth:`ShipInstance.set_bay_inventory` directly.
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

    # ------------------------------------------------------------------
    # Component-toggle + repair (PROJ-425 Phase 4)
    #
    # Cache invalidation is centralized here — both branches go through
    # ``invalidate_stats_cache`` on the entity so the rule cannot drift.
    # ------------------------------------------------------------------
    def set_component_enabled(
        self, instance: "ShipInstance", component_id: str, enabled: bool
    ) -> None:
        """Enable / disable a component and invalidate cached stats."""
        instance.component_toggles[component_id] = bool(enabled)
        if hasattr(instance, "invalidate_stats_cache"):
            instance.invalidate_stats_cache()

    def repair(self, instance: "ShipInstance", amount: int) -> int:
        """Repair the ship by ``amount`` hp and invalidate cached stats.

        Returns the actual amount repaired. Mirrors the old
        ``ShipInstance.repair`` semantics:

        - When ``current_hp`` is ``None`` (already full health), nothing
          changes and the result is 0.
        - Otherwise hp is bumped toward ``max_hp`` (from
          ``get_calculated_stats``); on reaching full, ``current_hp`` is
          set back to ``None`` and every component is restored to its
          ``max_hp``.
        """
        if instance.current_hp is None:
            return 0  # Already at full health

        max_hp = instance.get_calculated_stats().get('max_hp', _DEFAULT_MAX_HP)
        old_hp = instance.current_hp
        instance.current_hp = min(max_hp, instance.current_hp + amount)

        # If fully repaired, restore every component to full HP.
        if instance.current_hp >= max_hp:
            instance.current_hp = None
            for cs in instance.components.values():
                cs.current_hp = cs.max_hp

        if hasattr(instance, "invalidate_stats_cache"):
            instance.invalidate_stats_cache()

        return (
            instance.current_hp - old_hp
            if instance.current_hp is not None
            else max_hp - old_hp
        )
