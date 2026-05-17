"""ShipInstanceFactory - Build ShipInstance objects from a design.

PROJ-425 Phase 3 (TD-06): extracted from ``ShipInstance.create(...)`` and
the module-level ``_build_full_hp_components_from_design`` helper.

``ShipInstance.create(...)`` remains as a thin shim that delegates here,
per TD-06 Weak-LLM Guardrail #1 ("Do not remove ShipInstance.create, ...
until grep proves their callers were migrated"). Caller migration is a
later concern; this phase only extracts the body.
"""
from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional

from game.core.component_state import ComponentState, component_state_key

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.strategy.data.empire import Empire
    from game.strategy.data.ship_instance import ShipInstance


__all__ = [
    "ShipInstanceFactory",
    "build_full_hp_components_from_design",
]


logger = logging.getLogger(__name__)


def build_full_hp_components_from_design(
    design_data: Dict[str, Any],
    registries: Optional["GameRegistries"],
) -> Dict[str, ComponentState]:
    """Build a full-HP `ComponentState` dict from a ship design.

    Walks the design's layers and creates one entry per component
    instance, keyed by `component_state_key(component_id, instance_index)`.
    `instance_index` resets per `component_id` (so three identical
    components produce indices 0, 1, 2).

    Uses `ShipSerializer.from_dict(...)` to materialize the ship so each
    component's `max_hp` is computed from the real formula pipeline.
    Returns an empty dict if `registries` is None or the design has no
    layers, or if materialization fails.

    PROJ-425 Phase 3: moved verbatim from
    ``game/strategy/data/ship_instance._build_full_hp_components_from_design``.
    """
    if registries is None:
        return {}
    # INTENTIONAL LATE IMPORT: Cross-layer boundary (strategy -> simulation).
    from game.simulation.entities.ship_serialization import ShipSerializer

    try:
        ship = ShipSerializer.from_dict(design_data, registries=registries)
    except Exception as e:  # Intentional broad catch: ShipSerializer.from_dict() may raise various exception types on corrupt/incomplete design data; falling back to empty components is safe — callers treat empty dict as "no per-component data available".
        logger.warning(
            f"Could not materialize ship from design for component-state "
            f"population: {e}. Falling back to empty components."
        )
        return {}

    components: Dict[str, ComponentState] = {}
    per_id_index: Dict[str, int] = {}
    for _layer_type, layer_data in ship.layers.items():
        for comp in getattr(layer_data, "components", []):
            comp_id = getattr(comp, "id", None)
            if not comp_id:
                continue
            idx = per_id_index.get(comp_id, 0)
            per_id_index[comp_id] = idx + 1
            key = component_state_key(comp_id, idx)
            comp_max_hp = float(getattr(comp, "max_hp", 0))
            components[key] = ComponentState(
                component_id=comp_id,
                instance_index=idx,
                current_hp=float(getattr(comp, "current_hp", comp_max_hp)),
                max_hp=comp_max_hp,
                is_active=bool(getattr(comp, "is_active", True)),
            )
    return components


class ShipInstanceFactory:
    """Factory for constructing ``ShipInstance`` objects from a design.

    PROJ-425 Phase 3: extracted from ``ShipInstance.create``. The entity's
    classmethod remains as a thin shim that delegates here.
    """

    @staticmethod
    def create(
        design_data: Dict[str, Any],
        owner_id: int,
        name: Optional[str] = None,
        design_id: Optional[str] = None,
        empire: Optional["Empire"] = None,
        registries: Optional["GameRegistries"] = None,
    ) -> "ShipInstance":
        """Create a new ``ShipInstance`` from a design.

        Args:
            design_data: Full ship design dictionary
                (from ``ShipSerializer.to_dict()``).
            owner_id: Empire that owns this ship.
            name: Instance name (defaults to design name).
            design_id: Design identifier (defaults to design name).
            empire: Empire to draw the serial number from. If None, no
                serial is assigned and a warning is logged.
            registries: ``GameRegistries`` for stats calculation. Required
                for proper DI. Without it, ``get_calculated_stats()`` will
                raise.

        Returns:
            New ``ShipInstance`` with a unique ``instance_id``.
        """
        from game.strategy.data.ship_instance import ShipInstance

        design_name = design_data.get('name', 'Unknown Ship')
        actual_design_id = design_id or design_name

        serial = None
        if empire is not None:
            serial = empire.get_next_serial(actual_design_id)
        else:
            logger.warning(
                f"ShipInstance.create() called without empire - "
                f"serial will be None for '{actual_design_id}'"
            )

        instance = ShipInstance(
            instance_id=str(uuid.uuid4()),
            design_id=actual_design_id,
            name=name or design_name,
            owner_id=owner_id,
            design_data=design_data,
        )
        instance.serial = serial
        instance._registries = registries

        # Initialize all resources to full capacity.
        stats = instance.get_calculated_stats()
        storage = stats.get('resource_storage', {})
        instance.consumable_levels = {
            name: float(val) for name, val in storage.items()
        }

        # Initialize cargo from design data (Phase 2: colony pods as cargo).
        initial_cargo = design_data.get('cargo', {})
        for cargo_type, amount in initial_cargo.items():
            instance.cargo_contents[cargo_type] = int(amount)

        # Populate per-component-instance state with full-HP defaults.
        instance.components = build_full_hp_components_from_design(
            design_data, registries
        )

        # Mirror design role on the instance so downstream consumers see it.
        if instance.design_role is None:
            instance.design_role = design_data.get("design_role")

        return instance
