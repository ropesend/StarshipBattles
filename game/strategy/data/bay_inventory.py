"""Typed BayInventory substrate.

PROJ-431 Phase 1 introduced two homogeneous typed slots replacing the
old ``ShipInstance.carried_items: List[Dict[str, Any]]`` mixed list:

* ``bay: list[CarriedVehicle]`` — design-backed mines/fighters/satellites
* ``pods: list[DropPod]`` — drop-pod payloads for colonisation

PROJ-436 Phase 2 widens BayInventory to a four-slot store mirroring the
unified Container substrate's three slices (items / resources /
population). The existing bay+pods slots stay typed and unchanged; two
new slots are added:

* ``resources: dict[str, float]`` — continuous resource amounts; mass
  resolved through the Core-layer ``ResourceCatalog``.
* ``population: dict[str, int]`` — per-species integer counts; mass
  resolved through ``species_mass_per_unit()``.

Mass accounting is unified through ``total_mass()`` which sums all
four slots. The class remains a dataclass — bay/pods stay actual
mutable list fields (PROJ-431 callers depend on that) — and gains the
new resource/population APIs.

For full Container-shaped reads, ``container_view()`` returns a
``Container`` projection (used by transfer/validation surfaces that
want to work in the unified abstraction).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.container import (
    Container,
    ContainerPolicy,
    _get_resource_catalog,
)
from game.strategy.data.containable import (
    ContainableKind,
    species_mass_per_unit,
)


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
    """Typed four-slot inventory for ``ShipInstance``.

    Slots:
    - ``bay``: design-backed carried vehicles (mines/fighters/satellites)
    - ``pods``: drop pods
    - ``resources``: continuous resource amounts by resource id
    - ``population``: per-species integer counts

    Existing PROJ-431 callers using ``bay`` / ``pods`` lists continue
    to work unchanged. PROJ-436 Phase 2 adds the typed resource +
    population slots and unified mass accounting.
    """

    bay: List[CarriedVehicle] = field(default_factory=list)
    pods: List[DropPod] = field(default_factory=list)
    resources: Dict[str, float] = field(default_factory=dict)
    population: Dict[str, int] = field(default_factory=dict)

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

    # PROJ-436 Phase 2: resource slot ----------------------------------

    def add_resource(self, resource_id: str, amount: float) -> None:
        """Add `amount` units of `resource_id` to the resource slot.

        Raises:
            KeyError: when `resource_id` is not in `ResourceCatalog`
                (fail-fast — silent default would mask data drift).
            ValueError: when `amount` is negative.
        """
        if amount < 0:
            raise ValueError(f"resource amount must be non-negative, got {amount}")
        # Validate the resource id via the catalog (fail-fast on
        # unknown ids). Mass-per-unit lookup is also the registry
        # check site, so call it for the side effect.
        _get_resource_catalog().get_mass_per_unit(resource_id)
        self.resources[resource_id] = self.resources.get(resource_id, 0.0) + float(amount)

    def remove_resource(self, resource_id: str, amount: float) -> bool:
        """Remove `amount` units of `resource_id`. Returns True on success.

        Returns False when the slot has fewer units than requested
        (slot is left unchanged in that case).
        """
        current = self.resources.get(resource_id, 0.0)
        if amount > current + 1e-9:
            return False
        new_amount = current - float(amount)
        if new_amount <= 1e-9:
            self.resources.pop(resource_id, None)
        else:
            self.resources[resource_id] = new_amount
        return True

    def get_resource(self, resource_id: str) -> float:
        return self.resources.get(resource_id, 0.0)

    # PROJ-436 Phase 2: population slot --------------------------------

    def add_population(self, species_id: str, count: int) -> None:
        """Add `count` individuals of `species_id` to the population slot.

        Raises:
            TypeError: when `count` is not an int.
            ValueError: when `count` is negative.
        """
        if not isinstance(count, int) or isinstance(count, bool):
            raise TypeError(
                f"population count must be int, got {type(count).__name__}"
            )
        if count < 0:
            raise ValueError(f"population count must be non-negative, got {count}")
        self.population[species_id] = self.population.get(species_id, 0) + count

    def remove_population(self, species_id: str, count: int) -> bool:
        current = self.population.get(species_id, 0)
        if count > current:
            return False
        new_count = current - int(count)
        if new_count == 0:
            self.population.pop(species_id, None)
        else:
            self.population[species_id] = new_count
        return True

    def get_population(self, species_id: str) -> int:
        return self.population.get(species_id, 0)

    # ------------------------------------------------------------------
    # Mass accounting — unified across all four slots
    # ------------------------------------------------------------------

    def total_bay_mass(self) -> float:
        return sum(v.mass for v in self.bay)

    def total_pod_mass(self) -> float:
        return sum(p.mass for p in self.pods)

    def total_resource_mass(self) -> float:
        catalog = _get_resource_catalog()
        return sum(
            amount * catalog.get_mass_per_unit(rid)
            for rid, amount in self.resources.items()
        )

    def total_population_mass(self) -> float:
        return sum(
            count * species_mass_per_unit(sid)
            for sid, count in self.population.items()
        )

    def total_mass(self) -> float:
        """Unified mass across all four slots."""
        return (
            self.total_bay_mass()
            + self.total_pod_mass()
            + self.total_resource_mass()
            + self.total_population_mass()
        )

    def is_empty(self) -> bool:
        return (
            not self.bay
            and not self.pods
            and not self.resources
            and not self.population
        )

    # ------------------------------------------------------------------
    # Container projection — for callers that want to work in the
    # unified abstraction (transfer / validation surfaces).
    # ------------------------------------------------------------------

    def container_view(
        self,
        *,
        capacity_mass: float = float("inf"),
        policy: ContainerPolicy | None = None,
    ) -> Container:
        """Return a `Container` projection of this BayInventory.

        Items are added as ``ItemRef`` instances using the existing
        ``CarriedVehicle`` / ``DropPod`` data; resources and population
        slots are populated verbatim. The returned Container is a
        snapshot — mutations on it do NOT propagate back to this
        BayInventory.
        """
        from game.strategy.data.containable import (
            ItemContainable,
            ItemRef,
            PopulationContainable,
            ResourceContainable,
        )

        if policy is None:
            policy = ContainerPolicy(
                allowed_kinds=frozenset({
                    ContainableKind.RESOURCE,
                    ContainableKind.ITEM,
                    ContainableKind.POPULATION,
                }),
                allowed_type_ids=None,
            )
        c = Container(capacity_mass=capacity_mass, policy=policy)

        for rid, amount in self.resources.items():
            c.add(ResourceContainable(rid), amount)
        for sid, count in self.population.items():
            c.add(PopulationContainable(sid), count)
        for idx, cv in enumerate(self.bay):
            c.add(
                ItemContainable(ItemRef(
                    design_id=cv.design_id,
                    instance_id=f"bay-{idx}",
                    mass=cv.mass,
                    state={"kind": "vehicle"},
                )),
                1,
            )
        for idx, pod in enumerate(self.pods):
            c.add(
                ItemContainable(ItemRef(
                    design_id=pod.design_id,
                    instance_id=f"pod-{idx}",
                    mass=pod.mass,
                    state={"kind": "pod"},
                )),
                1,
            )
        return c

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bay": [v.to_dict() for v in self.bay],
            "pods": [p.to_dict() for p in self.pods],
            "resources": dict(self.resources),
            "population": dict(self.population),
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
        # PROJ-436 Phase 2: pre-Phase-2 saves omit `resources` and
        # `population` — they read as empty dicts and round-trip fine.
        resources = dict(data.get("resources", {}) or {})
        population = {
            str(k): int(v) for k, v in (data.get("population", {}) or {}).items()
        }
        return cls(bay=bay, pods=pods, resources=resources, population=population)
