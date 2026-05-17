"""PROJ-431 Phase 1 — typed BayInventory substrate.

Replaces the ``ShipInstance.carried_items: List[Dict[str, Any]]`` mixed-
shape list with two homogeneous typed slots:

* ``bay: list[CarriedVehicle]`` — design-backed mines/fighters/satellites
* ``pods: list[DropPod]`` — drop-pod payloads for colonisation

The bay is homogeneous, so the legacy ``CarriedVehicle.from_any()``
discriminator is no longer needed: every entry in ``bay`` is already a
typed ``CarriedVehicle``, every entry in ``pods`` is a typed
``DropPod``. Cross-slot leakage raises ``TypeError`` at add-time.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from game.strategy.data.carried_vehicle import CarriedVehicle


@dataclass
class DropPod:
    """Typed drop-pod entry.

    Drop pods previously lived as untyped dicts inside
    ``ShipInstance.carried_items``. They are now typed dataclasses
    inside ``BayInventory.pods``. The pod design is preserved as a full
    snapshot so the colonisation order handler can rehydrate the pod at
    deploy time without going back to the registry.
    """

    design_id: str
    design_data: Dict[str, Any] = field(default_factory=dict)
    mass: float = 0.0
    # Optional payload — colonist count, supplies, etc. — preserved
    # opaquely through the bay inventory. The colonisation handler owns
    # the schema.
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "design_id": self.design_id,
            "design_data": self.design_data,
            "mass": float(self.mass),
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DropPod":
        return cls(
            design_id=str(data.get("design_id", "")),
            design_data=dict(data.get("design_data", {})),
            mass=float(data.get("mass", 0.0)),
            payload=dict(data.get("payload", {})),
        )


@dataclass
class BayInventory:
    """Typed two-slot inventory for ``ShipInstance``.

    ``bay`` holds design-backed carried vehicles (mines, fighters,
    satellites). ``pods`` holds drop pods. Adding to either slot is
    typed: passing the wrong type raises ``TypeError`` at add-time
    rather than producing a half-typed mixed list.
    """

    bay: List[CarriedVehicle] = field(default_factory=list)
    pods: List[DropPod] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Mutation — strict typing
    # ------------------------------------------------------------------

    def add_vehicle(self, vehicle: CarriedVehicle) -> None:
        if not isinstance(vehicle, CarriedVehicle):
            raise TypeError(
                f"BayInventory.add_vehicle expects CarriedVehicle, "
                f"got {type(vehicle).__name__}"
            )
        self.bay.append(vehicle)

    def add_pod(self, pod: DropPod) -> None:
        if not isinstance(pod, DropPod):
            raise TypeError(
                f"BayInventory.add_pod expects DropPod, "
                f"got {type(pod).__name__}"
            )
        self.pods.append(pod)

    # ------------------------------------------------------------------
    # Mass accounting
    # ------------------------------------------------------------------

    def total_pod_mass(self) -> float:
        return sum(p.mass for p in self.pods)

    def total_bay_mass(self) -> float:
        return sum(v.mass for v in self.bay)

    def is_empty(self) -> bool:
        return not self.bay and not self.pods

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bay": [v.to_dict() for v in self.bay],
            "pods": [p.to_dict() for p in self.pods],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BayInventory":
        if not data:
            return cls()
        bay_data = data.get("bay", []) or []
        pods_data = data.get("pods", []) or []
        bay: List[CarriedVehicle] = []
        for entry in bay_data:
            if isinstance(entry, CarriedVehicle):
                bay.append(entry)
            elif isinstance(entry, dict):
                bay.append(CarriedVehicle.from_dict(entry))
        pods: List[DropPod] = []
        for entry in pods_data:
            if isinstance(entry, DropPod):
                pods.append(entry)
            elif isinstance(entry, dict):
                pods.append(DropPod.from_dict(entry))
        return cls(bay=bay, pods=pods)
