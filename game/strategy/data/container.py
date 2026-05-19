"""
Unified Container substrate (PROJ-436 Phase 0).

`Container` is a mass-based, policy-driven storage abstraction used
by ships, planets, fleets, facilities, and bays. It carries three
internal slices:

- `resources`: continuous per-resource amounts (Dict[str, float]).
- `items`: discrete per-instance ItemRef list (List[ItemRef]).
- `population`: per-species integer counts (Dict[str, int]).

All three share one `capacity_mass` and one `ContainerPolicy` (allowed
kinds + optional allowed type_id allowlist). The math is uniform; the
read API is per-slice convenience plus the unified `contents()` view.

Resource mass-per-unit reads from the Core-layer `ResourceCatalog`
(no parallel strategy-local registry per PROJ-436 charter). Item mass
comes from the carried `ItemRef`. Population mass comes from
`species_mass_per_unit()` in containable.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterator

from game.core.resources import ResourceCatalog
from game.strategy.data.containable import (
    Containable,
    ContainableKind,
    ItemContainable,
    ItemRef,
    PopulationContainable,
    ResourceContainable,
    species_mass_per_unit,
)


class AddResult(Enum):
    OK = "ok"
    REJECTED_POLICY = "rejected_policy"
    REJECTED_CAPACITY = "rejected_capacity"


class RemoveResult(Enum):
    OK = "ok"
    NOT_ENOUGH = "not_enough"


@dataclass(frozen=True)
class ContainerPolicy:
    """Content-policy filter for a Container.

    `allowed_kinds` is the set of `ContainableKind`s accepted.
    `allowed_type_ids` further restricts to a specific allowlist of
    type IDs (resource_id / design_id / species_id). When None, any
    type_id of an allowed kind is accepted.
    """

    allowed_kinds: frozenset[ContainableKind]
    allowed_type_ids: frozenset[str] | None = None


@dataclass(frozen=True)
class ContainerEntry:
    """One unified read-view row across the three slices."""

    kind: ContainableKind
    type_id: str
    quantity: float
    mass_total: float


# Module-level catalog handle. Tests may swap via set_resource_catalog
# for isolated unit tests; production code uses the default
# ResourceCatalog.from_json() at first access.
_resource_catalog: ResourceCatalog | None = None


def _get_resource_catalog() -> ResourceCatalog:
    global _resource_catalog
    if _resource_catalog is None:
        _resource_catalog = ResourceCatalog.from_json()
    return _resource_catalog


def set_resource_catalog(catalog: ResourceCatalog | None) -> None:
    """Override the resource catalog used for resource mass lookups.

    Pass None to reset to the default `ResourceCatalog.from_json()`
    behavior. Tests use this to inject deterministic catalogs without
    touching disk.
    """
    global _resource_catalog
    _resource_catalog = catalog


def _resource_mass_per_unit(resource_id: str) -> float:
    """Resolve mass-per-unit for `resource_id` via the Core catalog.

    Raises `KeyError` when the resource is unknown — fail-fast per
    PROJ-436 Phase 0 D3 default ("no silent default to 1.0 or 0.0").
    """
    catalog = _get_resource_catalog()
    defn = catalog.get(resource_id)
    if defn is None:
        raise KeyError(f"Unknown resource id: {resource_id!r}")
    return defn.mass_per_unit


class Container:
    """Mass-capped, policy-filtered storage for resources / items / population.

    The three internal slices share a single `capacity_mass` budget
    and a single `ContainerPolicy`. Math is uniform across slices.

    See `container.py` module docstring and
    `Projects/active_projects/PROJ-436/design.md` for context.
    """

    def __init__(
        self,
        capacity_mass: float,
        policy: ContainerPolicy,
        *,
        resources: dict[str, float] | None = None,
        items: list[ItemRef] | None = None,
        population: dict[str, int] | None = None,
    ) -> None:
        if capacity_mass < 0:
            raise ValueError(f"capacity_mass must be non-negative, got {capacity_mass}")
        self._capacity_mass: float = float(capacity_mass)
        self._policy: ContainerPolicy = policy
        self._resources: dict[str, float] = dict(resources or {})
        self._items: list[ItemRef] = list(items or [])
        self._population: dict[str, int] = dict(population or {})

    # -- read surface ---------------------------------------------------

    @property
    def capacity_mass(self) -> float:
        return self._capacity_mass

    @property
    def policy(self) -> ContainerPolicy:
        return self._policy

    @property
    def mass_used(self) -> float:
        resource_mass = sum(
            amount * _resource_mass_per_unit(rid)
            for rid, amount in self._resources.items()
        )
        item_mass = sum(item.mass for item in self._items)
        population_mass = sum(
            count * species_mass_per_unit(sid)
            for sid, count in self._population.items()
        )
        return resource_mass + item_mass + population_mass

    @property
    def mass_remaining(self) -> float:
        return self._capacity_mass - self.mass_used

    def get_resource(self, resource_id: str) -> float:
        return self._resources.get(resource_id, 0.0)

    def get_items(self) -> tuple[ItemRef, ...]:
        return tuple(self._items)

    def get_population(self, species_id: str) -> int:
        return self._population.get(species_id, 0)

    # -- policy ---------------------------------------------------------

    def accepts(self, containable: Containable) -> bool:
        kind = containable.kind
        if kind not in self._policy.allowed_kinds:
            return False
        if self._policy.allowed_type_ids is None:
            return True
        return containable.type_id in self._policy.allowed_type_ids

    # -- write surface --------------------------------------------------

    def add(self, containable: Containable, quantity: float | int) -> AddResult:
        if not self.accepts(containable):
            return AddResult.REJECTED_POLICY

        if isinstance(containable, ResourceContainable):
            if quantity < 0:
                raise ValueError("resource quantity must be non-negative")
            mass_delta = quantity * _resource_mass_per_unit(containable.resource_id)
            if mass_delta > self.mass_remaining + 1e-9:
                return AddResult.REJECTED_CAPACITY
            self._resources[containable.resource_id] = (
                self._resources.get(containable.resource_id, 0.0) + float(quantity)
            )
            return AddResult.OK

        if isinstance(containable, ItemContainable):
            if quantity != 1:
                raise ValueError("item quantity must be exactly 1 (items carry per-instance identity)")
            mass_delta = containable.item_ref.mass
            if mass_delta > self.mass_remaining + 1e-9:
                return AddResult.REJECTED_CAPACITY
            self._items.append(containable.item_ref)
            return AddResult.OK

        if isinstance(containable, PopulationContainable):
            if not isinstance(quantity, int) or isinstance(quantity, bool):
                raise TypeError("population quantity must be int")
            if quantity < 0:
                raise ValueError("population quantity must be non-negative")
            mass_delta = quantity * species_mass_per_unit(containable.species_id)
            if mass_delta > self.mass_remaining + 1e-9:
                return AddResult.REJECTED_CAPACITY
            self._population[containable.species_id] = (
                self._population.get(containable.species_id, 0) + quantity
            )
            return AddResult.OK

        raise TypeError(f"Unknown Containable variant: {type(containable).__name__}")

    def remove(self, containable: Containable, quantity: float | int) -> RemoveResult:
        if isinstance(containable, ResourceContainable):
            if quantity < 0:
                raise ValueError("resource quantity must be non-negative")
            current = self._resources.get(containable.resource_id, 0.0)
            if quantity > current + 1e-9:
                return RemoveResult.NOT_ENOUGH
            new_amount = current - float(quantity)
            if new_amount <= 1e-9:
                self._resources.pop(containable.resource_id, None)
            else:
                self._resources[containable.resource_id] = new_amount
            return RemoveResult.OK

        if isinstance(containable, ItemContainable):
            target_id = containable.item_ref.instance_id
            for idx, existing in enumerate(self._items):
                if existing.instance_id == target_id:
                    self._items.pop(idx)
                    return RemoveResult.OK
            return RemoveResult.NOT_ENOUGH

        if isinstance(containable, PopulationContainable):
            if quantity < 0:
                raise ValueError("population quantity must be non-negative")
            current = self._population.get(containable.species_id, 0)
            if quantity > current:
                return RemoveResult.NOT_ENOUGH
            new_count = current - int(quantity)
            if new_count == 0:
                self._population.pop(containable.species_id, None)
            else:
                self._population[containable.species_id] = new_count
            return RemoveResult.OK

        raise TypeError(f"Unknown Containable variant: {type(containable).__name__}")

    # -- unified read ---------------------------------------------------

    def contents(self) -> Iterator[ContainerEntry]:
        for rid, amount in self._resources.items():
            yield ContainerEntry(
                kind=ContainableKind.RESOURCE,
                type_id=rid,
                quantity=amount,
                mass_total=amount * _resource_mass_per_unit(rid),
            )
        for item in self._items:
            yield ContainerEntry(
                kind=ContainableKind.ITEM,
                type_id=item.design_id,
                quantity=1.0,
                mass_total=item.mass,
            )
        for sid, count in self._population.items():
            yield ContainerEntry(
                kind=ContainableKind.POPULATION,
                type_id=sid,
                quantity=float(count),
                mass_total=count * species_mass_per_unit(sid),
            )

    # -- serialization --------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "capacity_mass": self._capacity_mass,
            "policy": {
                "allowed_kinds": sorted(k.value for k in self._policy.allowed_kinds),
                "allowed_type_ids": (
                    sorted(self._policy.allowed_type_ids)
                    if self._policy.allowed_type_ids is not None
                    else None
                ),
            },
            "resources": dict(self._resources),
            "items": [
                {
                    "design_id": item.design_id,
                    "instance_id": item.instance_id,
                    "mass": item.mass,
                    "state": dict(item.state),
                }
                for item in self._items
            ],
            "population": dict(self._population),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Container":
        policy_data = data.get("policy", {})
        allowed_kinds = frozenset(
            ContainableKind(value) for value in policy_data.get("allowed_kinds", [])
        )
        raw_type_ids = policy_data.get("allowed_type_ids")
        allowed_type_ids: frozenset[str] | None = (
            frozenset(raw_type_ids) if raw_type_ids is not None else None
        )
        policy = ContainerPolicy(
            allowed_kinds=allowed_kinds,
            allowed_type_ids=allowed_type_ids,
        )
        items = [
            ItemRef(
                design_id=entry["design_id"],
                instance_id=entry["instance_id"],
                mass=entry["mass"],
                state=dict(entry.get("state", {})),
            )
            for entry in data.get("items", [])
        ]
        return cls(
            capacity_mass=data.get("capacity_mass", 0.0),
            policy=policy,
            resources=dict(data.get("resources", {})),
            items=items,
            population=dict(data.get("population", {})),
        )


__all__ = [
    "AddResult",
    "Container",
    "ContainerEntry",
    "ContainerPolicy",
    "RemoveResult",
    "set_resource_catalog",
]
