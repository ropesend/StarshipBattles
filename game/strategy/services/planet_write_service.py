"""PlanetWriteService — owns Planet writes from outside the data class.

PROJ-370 Phase 3: implements ``IPlanetMutator``. Single owner service for
all 16 Planet attribute surfaces (populations, facilities, stockpile,
staging_yard, construction_queue, orders, owner_id, atmosphere/atmosphere_target,
energy/energy_capacity/energy_generation, gravity_target, water_target,
radiation_shielding[_target]).

Wiring:
    Constructed in ``GameSession.__init__``. Threaded through
    ``TurnEngineConfig.create_default()`` (post-PROJ-369). Engines
    accept ``planet_mutator: IPlanetMutator | None = None``.

Cross-class boundary note:
    ``set_owner_id(planet, empire_id)`` does NOT cross into Empire's
    ``colonies`` list — callers must separately route
    ``Empire.add_colony``/``remove_colony`` through ``IEmpireMutator``
    (Phase 4).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from game.strategy.data.bay_inventory import DropPod
    from game.strategy.data.carried_vehicle import CarriedVehicle
    from game.strategy.data.order_types import Order
    from game.strategy.data.planet import Planet


__all__ = ["PlanetWriteService"]


class PlanetWriteService:
    """Concrete ``IPlanetMutator`` implementation."""

    # --- Populations ---
    def add_species_population(
        self, planet: "Planet", species_pop: Any
    ) -> None:
        planet.populations.append(species_pop)

    def remove_species_population(
        self, planet: "Planet", species_pop: Any
    ) -> bool:
        if species_pop in planet.populations:
            planet.populations.remove(species_pop)
            return True
        return False

    def update_population_count(
        self, planet: "Planet", race_id: str, new_count: float
    ) -> None:
        for pop in planet.populations:
            if getattr(pop, "race_id", None) == race_id:
                pop.count = new_count
                return

    # --- Facilities ---
    def add_facility(
        self, planet: "Planet", facility: Any, *, empire: Any = None,
    ) -> None:
        """Append a facility to ``planet.facilities``.

        PROJ-412 Phase 5: when ``empire`` is supplied, the empire's
        ``_storage_dirty`` and ``_booster_dirty`` flags are flipped to
        invalidate ``HarvestingEngine``'s per-turn caches. Callers that
        omit ``empire`` still mutate state correctly — the engine's
        turn-key check will rebuild caches on the next turn boundary.
        """
        planet.facilities.append(facility)
        if empire is not None:
            empire._storage_dirty = True
            empire._booster_dirty = True

    def remove_facility(
        self, planet: "Planet", facility: Any, *, empire: Any = None,
    ) -> bool:
        """Remove a facility from ``planet.facilities``; return True on success.

        PROJ-412 Phase 5: see ``add_facility`` for the ``empire`` flag
        semantics.
        """
        if facility in planet.facilities:
            planet.facilities.remove(facility)
            if empire is not None:
                empire._storage_dirty = True
                empire._booster_dirty = True
            return True
        return False

    # --- Stockpile ---
    def set_stockpile_amount(
        self, planet: "Planet", resource_id: str, amount: float
    ) -> None:
        planet.stockpile[resource_id] = amount

    def set_max_stockpile(self, planet: "Planet", new_max: dict) -> None:
        planet._max_stockpile = dict(new_max)

    # --- Staging yard ---
    def add_staging_item(
        self,
        planet: "Planet",
        item: "CarriedVehicle | DropPod",
    ) -> None:
        # Delegate to existing public API (enforces capacity).
        # PROJ-450 Phase 3: signature tightened — substrate is typed,
        # so callers must hand in typed entries.
        planet.add_to_staging_yard(item)

    def pop_staging_item(
        self,
        planet: "Planet",
        index: int = 0,
    ) -> "CarriedVehicle | DropPod | None":
        # PROJ-450 Phase 3: route through ``pop_staging_yard_typed`` so
        # the return is always a typed entry (or None on out-of-range).
        return planet.pop_staging_yard_typed(index)

    # --- Construction queue ---
    def append_construction_item(self, planet: "Planet", item: Any) -> None:
        planet.construction_queue.append(item)

    def pop_construction_item(self, planet: "Planet", index: int = 0) -> Any:
        return planet.construction_queue.pop(index)

    # --- Orders ---
    def append_order(self, planet: "Planet", order: "Order") -> None:
        planet.add_order(order)

    def insert_order(
        self, planet: "Planet", index: int, order: "Order"
    ) -> None:
        planet.add_order(order, index=index)

    def pop_order(
        self, planet: "Planet", index: int = 0
    ) -> "Order | None":
        if index == 0:
            return planet.pop_order()
        # Planet's pop_order is index-0-only; emulate the data-class API
        # by direct list pop for non-zero indices.
        if 0 <= index < len(planet.orders):
            return planet.orders.pop(index)
        return None

    def clear_orders(self, planet: "Planet") -> None:
        planet.clear_orders()

    # --- Scalar fields ---
    def set_owner_id(self, planet: "Planet", owner_id: Any) -> None:
        planet.owner_id = owner_id

    def set_atmosphere(self, planet: "Planet", value: Any) -> None:
        planet.atmosphere = value

    def set_atmosphere_target(self, planet: "Planet", value: Any) -> None:
        planet.atmosphere_target = value

    def set_energy(self, planet: "Planet", value: float) -> None:
        planet.energy = value

    def set_energy_capacity(self, planet: "Planet", value: float) -> None:
        planet.energy_capacity = value

    def set_energy_generation(self, planet: "Planet", value: float) -> None:
        planet.energy_generation = value

    def set_gravity_target(self, planet: "Planet", value: Any) -> None:
        planet.gravity_target = value

    def set_water_target(self, planet: "Planet", value: Any) -> None:
        planet.water_target = value

    def set_radiation_shielding(
        self, planet: "Planet", value: float
    ) -> None:
        planet.radiation_shielding = value

    def set_radiation_shielding_target(
        self, planet: "Planet", value: float
    ) -> None:
        planet.radiation_shielding_target = value
