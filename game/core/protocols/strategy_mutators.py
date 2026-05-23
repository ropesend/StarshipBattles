"""Strategy-layer mutator protocols.

Pair with the read protocols in `strategy_entities.py` and `strategy_domain.py`.
Engines depend on these to seam writes — the read protocols answer "what's the
state?" and the mutator protocols answer "who is allowed to change it?".

PROJ-370: introduced four `@runtime_checkable` Protocols (`IFleetMutator`,
`IPlanetMutator`, `IEmpireMutator`, `IShipInstanceMutator`) plus AST-guard
tests that lock the boundary. Direct attribute writes from outside the data
class itself (e.g., `fleet.location = X` from an engine) are illegal; the
write must route through the mutator. The data class itself, plus a small
allowlisted set of co-located helper modules, may write its own attributes.

See `Projects/active_projects/PROJ-370/design.md` for the rationale and the
write-traffic heatmap that drove the four-class scope.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from game.core.hex_math import HexCoord
    from game.strategy.data.bay_inventory import DropPod
    from game.strategy.data.carried_vehicle import CarriedVehicle
    from game.strategy.data.empire import Empire
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.order_types import Order
    from game.strategy.data.planet import Planet
    from game.strategy.data.ship_instance import ShipInstance


__all__ = [
    "IFleetMutator",
    "IPlanetMutator",
    "IEmpireMutator",
    "IShipInstanceMutator",
]


@runtime_checkable
class IFleetMutator(Protocol):
    """Owns writes to ``Fleet`` state from outside the data class.

    Implementations: ``FleetWriteService`` (non-navigation slice) +
    ``FleetNavigationService`` (location/path slice). A composite is wired
    in ``GameSession.__init__`` and threaded into engines that need it.
    """

    # Navigation slice (co-implemented by FleetNavigationService)
    def set_location(self, fleet: "Fleet", new_location: "HexCoord") -> None: ...
    def set_path(self, fleet: "Fleet", new_path: "list[HexCoord]") -> None: ...

    # Order queue
    def append_order(self, fleet: "Fleet", order: "Order") -> None: ...
    def insert_order(self, fleet: "Fleet", index: int, order: "Order") -> None: ...
    def pop_order(self, fleet: "Fleet", index: int = 0) -> "Order | None": ...
    def clear_orders(self, fleet: "Fleet") -> None: ...
    def swap_orders(self, fleet: "Fleet", index_a: int, index_b: int) -> None: ...

    # Ship membership
    def add_ship(self, fleet: "Fleet", ship: Any) -> None: ...
    def remove_ship(self, fleet: "Fleet", ship: Any) -> bool: ...

    # Identity / policy
    def set_display_name(self, fleet: "Fleet", name: str) -> None: ...
    def set_fleet_policy(self, fleet: "Fleet", policy: Any) -> None: ...

    # Construction queue
    def append_construction_item(self, fleet: "Fleet", item: dict[str, Any]) -> None: ...
    def pop_construction_item(self, fleet: "Fleet", index: int = 0) -> dict[str, Any]: ...
    def set_construction_queue_paused(self, fleet: "Fleet", paused: bool) -> None: ...

    # Hierarchy (TaskForce membership)
    def add_task_force(self, fleet: "Fleet", tf: Any) -> None: ...
    def remove_task_force(self, fleet: "Fleet", tf: Any) -> bool: ...


@runtime_checkable
class IPlanetMutator(Protocol):
    """Owns writes to ``Planet`` state from outside the data class.

    Implementation: ``PlanetWriteService`` (single owner).

    Note: ``set_owner_id`` does NOT cross into Empire's ``colonies`` list —
    callers must separately route ``Empire.add_colony``/``remove_colony``
    through ``IEmpireMutator``.
    """

    # Populations
    def add_species_population(self, planet: "Planet", species_pop: Any) -> None: ...
    def remove_species_population(self, planet: "Planet", species_pop: Any) -> bool: ...
    def update_population_count(
        self, planet: "Planet", race_id: str, new_count: float
    ) -> None: ...

    # Facilities
    def add_facility(self, planet: "Planet", facility: Any) -> None: ...
    def remove_facility(self, planet: "Planet", facility: Any) -> bool: ...

    # Stockpile
    def set_stockpile_amount(
        self, planet: "Planet", resource_id: str, amount: float
    ) -> None: ...
    def set_max_stockpile(self, planet: "Planet", new_max: dict[str, float]) -> None: ...

    # Staging yard
    # PROJ-450 Phase 3: substrate widened to typed
    # ``List[CarriedVehicle | DropPod]``; signatures tightened.
    def add_staging_item(
        self, planet: "Planet", item: "CarriedVehicle | DropPod"
    ) -> None: ...
    def pop_staging_item(
        self, planet: "Planet", index: int = 0
    ) -> "CarriedVehicle | DropPod | None": ...

    # Construction queue
    def append_construction_item(self, planet: "Planet", item: Any) -> None: ...
    def pop_construction_item(
        self, planet: "Planet", index: int = 0
    ) -> "dict[str, Any] | None": ...

    # Orders
    def append_order(self, planet: "Planet", order: "Order") -> None: ...
    def insert_order(self, planet: "Planet", index: int, order: "Order") -> None: ...
    def pop_order(self, planet: "Planet", index: int = 0) -> "Order | None": ...
    def clear_orders(self, planet: "Planet") -> None: ...

    # Scalar fields
    def set_owner_id(self, planet: "Planet", owner_id: Any) -> None: ...
    def set_atmosphere(self, planet: "Planet", value: Any) -> None: ...
    def set_atmosphere_target(self, planet: "Planet", value: Any) -> None: ...
    def set_energy(self, planet: "Planet", value: float) -> None: ...
    def set_energy_capacity(self, planet: "Planet", value: float) -> None: ...
    def set_energy_generation(self, planet: "Planet", value: float) -> None: ...
    def set_gravity_target(self, planet: "Planet", value: Any) -> None: ...
    def set_water_target(self, planet: "Planet", value: Any) -> None: ...
    def set_radiation_shielding(self, planet: "Planet", value: float) -> None: ...
    def set_radiation_shielding_target(
        self, planet: "Planet", value: float
    ) -> None: ...


@runtime_checkable
class IEmpireMutator(Protocol):
    """Owns writes to ``Empire`` state from outside the data class.

    Implementation: ``EmpireWriteService`` (single owner).

    Includes the post-battle empty-fleet pruning logic (today inlined at
    ``combat/post_battle_hook.py:200-218``).
    """

    def add_colony(self, empire: "Empire", planet: "Planet") -> None: ...
    def remove_colony(self, empire: "Empire", planet: "Planet") -> bool: ...
    def clear_colonies(self, empire: "Empire") -> None: ...
    def add_fleet(self, empire: "Empire", fleet: "Fleet") -> None: ...
    def remove_fleet(
        self, empire: "Empire", fleet: "Fleet", *, event_bus: Any = None
    ) -> bool: ...
    def set_max_storage_amount(
        self, empire: "Empire", resource_id: str, amount: float
    ) -> None: ...
    def replace_max_storage(
        self, empire: "Empire", new_max_storage: dict[str, float]
    ) -> None: ...
    def add_built_design(self, empire: "Empire", design_id: str) -> None: ...
    def prune_empty_fleets(
        self,
        empires_by_team_id: dict[int, "Empire"],
        fleets_by_team_id: dict[int, list["Fleet"]],
        *,
        event_bus: Any = None,
    ) -> list[Any]: ...


@runtime_checkable
class IShipInstanceMutator(Protocol):
    """Owns writes to ``ShipInstance`` state from outside the data class.

    Implementation: ``ShipInstanceWriteService`` (single owner). Cargo and
    consumable mutators forward to the existing ``ShipCargoManager`` and
    ``ShipConsumableManager`` (which are co-located with ``ShipInstance``
    in ``data/`` and treated as data-class-internal by the AST guard).
    """

    # Status flags
    def set_is_alive(self, instance: "ShipInstance", value: bool) -> None: ...
    def set_is_derelict(self, instance: "ShipInstance", value: bool) -> None: ...
    def set_current_hp(
        self, instance: "ShipInstance", value: float | None
    ) -> None: ...

    # Component dict (post-battle replacement) — also invalidates stats cache
    def replace_components(
        self, instance: "ShipInstance", new_components: dict[str, Any]
    ) -> None: ...

    # Cargo / consumables (forward to managers)
    def set_cargo_amount(
        self, instance: "ShipInstance", resource_id: str, amount: float
    ) -> None: ...
    def set_consumable_level(
        self, instance: "ShipInstance", resource_id: str, level: float
    ) -> None: ...

    # PROJ-431 Phase 1f: ``add_carried_item`` / ``pop_carried_item``
    # removed — no production callers. The typed bay_inventory + cargo
    # manager are the canonical write surface for carried inventory.

    # Per-component toggles & activation
    def set_component_toggle(
        self, instance: "ShipInstance", component_id: str, enabled: bool
    ) -> None: ...
    def set_activation_state(
        self, instance: "ShipInstance", component_id: str, state: Any
    ) -> None: ...

    # Combat record
    def increment_battles_survived(self, instance: "ShipInstance") -> None: ...
    def add_experience(self, instance: "ShipInstance", amount: float) -> None: ...
    def add_kill(self, instance: "ShipInstance") -> None: ...
