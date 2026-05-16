"""PROJ-FMS-A Phase 3 — CarriedVehicle dataclass.

Typed entry for design-backed vehicles (mines / fighters / satellites)
stored inside a :class:`~game.strategy.data.ship_instance.ShipInstance`
``VehicleBay`` or in a :class:`~game.strategy.data.planet.Planet`
``staging_yard``.

The existing drop-pod ``carried_items`` flow uses untyped dicts. This
class formalises the design-backed surface for the FMS sequence. Drop
pods continue to use the dict shape; ``CarriedVehicle`` is the new path
for mines / fighters / satellites that need per-instance HP, design
snapshots, and (optionally) per-component damage state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from game.core.component_state import ComponentState


VALID_VEHICLE_TYPES: frozenset[str] = frozenset({"mine", "fighter", "satellite"})


@dataclass
class CarriedVehicle:
    """Design-backed vehicle stored as bay cargo.

    Attributes:
        design_id: Reference to the source design.
        design_data: Full design snapshot, sufficient for cold reconstruction
            into a tactical-layer entity at deploy time.
        vehicle_type: One of ``mine`` / ``fighter`` / ``satellite``.
        mass: Stored mass; the bay's ``capacity_mass`` gates loading.
        current_hp: Per-instance HP. Fighters/satellites use this on
            recovery; mines are one-way and ignore it.
        component_states: Optional per-component damage state, reusing
            :class:`game.core.component_state.ComponentState`. Carried
            through serialisation; only populated when a vehicle is
            recovered with damaged components.
    """

    design_id: str
    design_data: Dict[str, Any]
    vehicle_type: str
    mass: float
    current_hp: int = 0
    component_states: Optional[Dict[str, ComponentState]] = field(default=None)

    def __post_init__(self) -> None:
        # Normalise vehicle_type; reject unknown kinds at construction
        # time so the bay-side accept() check doesn't have to.
        vt = self.vehicle_type.lower()
        if vt not in VALID_VEHICLE_TYPES:
            raise ValueError(
                f"CarriedVehicle.vehicle_type={self.vehicle_type!r} "
                f"must be one of {sorted(VALID_VEHICLE_TYPES)}"
            )
        self.vehicle_type = vt

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a save-game-safe dict.

        Component state is serialised as nested dicts using
        ``ComponentState.to_dict()`` where available; otherwise stored
        as None to keep the format stable.
        """
        comp_states: Optional[Dict[str, Any]] = None
        if self.component_states is not None:
            comp_states = {}
            for key, cs in self.component_states.items():
                if hasattr(cs, "to_dict"):
                    comp_states[key] = cs.to_dict()
                else:
                    comp_states[key] = cs
        return {
            "design_id": self.design_id,
            "design_data": self.design_data,
            "vehicle_type": self.vehicle_type,
            "mass": self.mass,
            "current_hp": self.current_hp,
            "component_states": comp_states,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CarriedVehicle":
        """Reverse of :meth:`to_dict`."""
        comp_states_data = data.get("component_states")
        comp_states: Optional[Dict[str, ComponentState]] = None
        if isinstance(comp_states_data, dict) and comp_states_data:
            comp_states = {}
            for key, cs_data in comp_states_data.items():
                if isinstance(cs_data, ComponentState):
                    comp_states[key] = cs_data
                elif isinstance(cs_data, dict) and hasattr(ComponentState, "from_dict"):
                    comp_states[key] = ComponentState.from_dict(cs_data)
        return cls(
            design_id=data["design_id"],
            design_data=data.get("design_data", {}),
            vehicle_type=data["vehicle_type"],
            mass=float(data.get("mass", 0)),
            current_hp=int(data.get("current_hp", 0)),
            component_states=comp_states,
        )

    @classmethod
    def from_any(cls, item: Any) -> Optional["CarriedVehicle"]:
        """Best-effort conversion from an untyped carried-items dict.

        Returns ``None`` for items that lack ``vehicle_type`` in the
        accepted set (e.g. drop-pod entries) — callers should keep those
        on the legacy ``carried_items`` path.
        """
        if isinstance(item, cls):
            return item
        if not isinstance(item, dict):
            return None
        vt = str(item.get("vehicle_type", "")).lower()
        if vt not in VALID_VEHICLE_TYPES:
            return None
        return cls.from_dict(item)
