"""PROJ-282 Phase 7: `FleetHierarchyEditor`.

Stateless helper for fleet/TaskForce/Squadron CRUD and ship-cloning.
Extracted from `BattleSetupController` to centralize the duplicated
ship-cloning logic that Phase 6 left inline on `duplicate_task_force`
and `duplicate_squadron`.

All operations take a `Fleet` (and as needed, a `TaskForce` / `Squadron`)
and mutate them in place. No UI or controller layer dependencies — the
editor can be used by other screens that want to edit fleet hierarchies
(e.g. a future fleet-orders window).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from game.strategy.data.fleet_hierarchy import CombatPolicy
from game.strategy.data.squadron import Squadron
from game.strategy.data.task_force import TaskForce

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance


class FleetHierarchyEditor:
    """Stateless editor for Fleet / TaskForce / Squadron structures.

    All methods are `@staticmethod` — no instance state. The class form
    is preserved (rather than module-level functions) for symmetry with
    the rest of the battle_setup package's `BattleSetupRenderer` /
    `BattleSetupInputHandler` / `BattleSetupController` shape.
    """

    # === Create ===

    @staticmethod
    def create_task_force(fleet: "Fleet", name: Optional[str] = None) -> TaskForce:
        """Create an empty TaskForce and append it to `fleet`.

        Default name is `f"Task Force {N}"` where N is `len(fleet.task_forces) + 1`.
        """
        if name is None:
            name = f"Task Force {len(fleet.task_forces) + 1}"
        tf = TaskForce(name=name)
        fleet.add_task_force(tf)
        return tf

    @staticmethod
    def create_squadron(tf: TaskForce, name: Optional[str] = None) -> Squadron:
        """Create an empty Squadron and append it to `tf`.

        Default name is `f"Squadron {N}"` where N is `len(tf.squadrons) + 1`.
        """
        if name is None:
            name = f"Squadron {len(tf.squadrons) + 1}"
        sq = Squadron(name=name)
        tf.add_squadron(sq)
        return sq

    # === Duplicate ===

    @staticmethod
    def duplicate_squadron(
        fleet: "Fleet", tf: TaskForce, original: Squadron,
    ) -> Squadron:
        """Duplicate `original` into a new Squadron on `tf`.

        Ships are cloned via `ShipInstance.create`; the clones are added
        to both the new squadron AND the fleet's master ship list (fleet
        tracks all ships across all hierarchy nodes).
        """
        registries = _get_registries()
        new_sq = Squadron(
            name=f"{original.name} (Copy)",
            policy=CombatPolicy(
                targeting=original.policy.targeting,
                movement=original.policy.movement,
                retreat=original.policy.retreat,
            ),
            battle_role=original.battle_role,
            spatial_behavior=original.spatial_behavior,
        )
        for ship in original.ships:
            cloned = FleetHierarchyEditor._clone_ship(ship, registries)
            new_sq.add_ship(cloned)
            fleet.add_ship(cloned)
        tf.add_squadron(new_sq)
        return new_sq

    @staticmethod
    def duplicate_task_force(fleet: "Fleet", original: TaskForce) -> TaskForce:
        """Duplicate `original` into a new TaskForce on `fleet`.

        Copies all squadrons (with cloned ships) and lone ships. Each
        clone is added to the fleet's master ship list as well.
        """
        registries = _get_registries()

        new_tf = TaskForce(
            name=f"{original.name} (Copy)",
            policy=CombatPolicy(
                targeting=original.policy.targeting,
                movement=original.policy.movement,
                retreat=original.policy.retreat,
            ),
            battle_role=original.battle_role,
        )

        for sq in original.squadrons:
            new_sq = Squadron(
                name=sq.name,
                policy=CombatPolicy(
                    targeting=sq.policy.targeting,
                    movement=sq.policy.movement,
                    retreat=sq.policy.retreat,
                ),
                battle_role=sq.battle_role,
                spatial_behavior=sq.spatial_behavior,
                spatial_behavior_params=dict(sq.spatial_behavior_params)
                if sq.spatial_behavior_params else None,
            )
            for ship in sq.ships:
                cloned = FleetHierarchyEditor._clone_ship(ship, registries)
                new_sq.add_ship(cloned)
                fleet.add_ship(cloned)
            new_tf.add_squadron(new_sq)

        for ship in original.lone_ships:
            cloned = FleetHierarchyEditor._clone_ship(ship, registries)
            new_tf.add_lone_ship(cloned)
            fleet.add_ship(cloned)

        fleet.add_task_force(new_tf)
        return new_tf

    # === Delete ===

    @staticmethod
    def delete_task_force(fleet: "Fleet", tf: TaskForce) -> None:
        """Remove `tf` from `fleet` along with all its ships (from the
        fleet's master list)."""
        for ship in tf.all_ships:
            fleet.remove_ship(ship)
        fleet.remove_task_force(tf)

    @staticmethod
    def delete_squadron(fleet: "Fleet", tf: TaskForce, sq: Squadron) -> None:
        """Remove `sq` from `tf` along with all its ships (from the
        fleet's master list)."""
        for ship in sq.all_ships:
            fleet.remove_ship(ship)
        tf.remove_squadron(sq)

    # === Ship cloning ===

    @staticmethod
    def _clone_ship(ship: "ShipInstance", registries) -> "ShipInstance":
        """Create a new `ShipInstance` with the same design as `ship`.

        Shared dedup for `duplicate_task_force` + `duplicate_squadron` —
        previously each duplicated this call inline, which was one of the
        motivating issues for PROJ-282 Phase 7.
        """
        from game.strategy.data.ship_instance import ShipInstance
        return ShipInstance.create(
            design_data=ship.design_data,
            owner_id=ship.owner_id,
            name=ship.name,
            registries=registries,
        )


def _get_registries():
    """Pull GameRegistries from the default provider for ship-cloning.

    Returns None if the provider isn't initialized — tests that don't
    load data will see this path; production always has registries.
    """
    try:
        from game.core.registry import GameRegistries, get_default_registry_provider
        provider = get_default_registry_provider()
        return GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources=provider.get_resources(),
            resource_catalog=provider.get_resource_catalog(),
        )
    except Exception:
        return None
