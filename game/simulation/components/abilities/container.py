"""
PROJ-436 Phase 1: `ContainerAbility` — the unified storage ability.

Component authors declare storage with a single shape:

    "Container": {
        "capacity_mass": 250,
        "allowed_kinds": ["RESOURCE", "ITEM", "POPULATION"],
        "allowed_type_ids": ["metals", "fuel"]
    }

`allowed_kinds` is a list of `ContainableKind` names (case-insensitive).
`allowed_type_ids` is either a list of strings (resource ids, design ids,
species ids) or `null` / missing for "any type_id of an allowed kind".

This replaces `ResourceStorage` / `CargoStorage` / `VehicleBay` going
forward. Those three abilities remain in the registry for Phase 1; the
parity helpers below convert each legacy shape into the equivalent
`(capacity_mass, ContainerPolicy)` view so runtime code in later
phases can read a uniform contract.

`capacity_mass` scales with `bay_capacity_mult` via the standard
`AbilityStatBinding` mechanism (same multiplier `VehicleBayAbility`
already uses, so `simple_size_mount` continues to work end-to-end).
"""
from __future__ import annotations

from typing import Any, Dict, List

from game.strategy.data.container import ContainerPolicy
from game.strategy.data.containable import (
    ContainableKind,
    SPECIES_DEFAULT_MASS_PER_UNIT,
)

from .base import Ability, AbilityLayer
from .cargo import CargoStorage
from .resources import ResourceStorage
from .stat_keys import AbilityStatBinding, StatKey
from .ui_colors import HINT_NEUTRAL
from .vehicle_bay import VehicleBayAbility


_VALID_KIND_NAMES: Dict[str, ContainableKind] = {
    member.name: member for member in ContainableKind
}


class ContainerAbility(Ability):
    """Mass-capped, policy-filtered storage on a component.

    Unifies the data shape that `ResourceStorage`, `CargoStorage`, and
    `VehicleBay` express today into one ability surface. Runtime
    storage state lives on the entity (ship / planet / fleet) — this
    ability is the *declaration* of capacity + policy.

    Attributes:
        capacity_mass: Maximum total mass this container holds, in tons.
            Scales with `bay_capacity_mult` so `simple_size_mount` drives
            size variation through one stat key (the same one
            `VehicleBayAbility` uses).
        policy: A `ContainerPolicy` carrying `allowed_kinds` and the
            optional `allowed_type_ids` allowlist.
    """

    layer = AbilityLayer.STRATEGIC

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(
            StatKey.BAY_CAPACITY_MULT,
            attribute_name="capacity_mass",
            operation="multiply",
            base_attribute="_base_capacity_mass",
        ),
    ]

    def _parse_attrs(self, data: Any) -> None:
        if not isinstance(data, dict):
            raise ValueError(
                "ContainerAbility requires a dict shape with keys "
                "'capacity_mass', 'allowed_kinds', 'allowed_type_ids' (optional)."
            )
        cap = float(data.get("capacity_mass", 0))
        self._base_capacity_mass: float = cap
        self.capacity_mass: float = cap

        kinds_raw = data.get("allowed_kinds", [])
        kinds: set[ContainableKind] = set()
        for k in kinds_raw:
            key = str(k).upper()
            if key not in _VALID_KIND_NAMES:
                raise ValueError(
                    f"ContainerAbility: unknown allowed_kinds entry {k!r}; "
                    f"expected one of {list(_VALID_KIND_NAMES)}"
                )
            kinds.add(_VALID_KIND_NAMES[key])

        type_ids_raw = data.get("allowed_type_ids")
        allowed_type_ids: frozenset[str] | None
        if type_ids_raw is None:
            allowed_type_ids = None
        else:
            allowed_type_ids = frozenset(str(t) for t in type_ids_raw)

        self.policy: ContainerPolicy = ContainerPolicy(
            allowed_kinds=frozenset(kinds),
            allowed_type_ids=allowed_type_ids,
        )

    def recalculate(self) -> None:
        """Apply `bay_capacity_mult` to `capacity_mass`."""
        mult = self.get_effective_stat("bay_capacity_mult", 1.0)
        self.capacity_mass = self._base_capacity_mass * mult

    def get_primary_value(self) -> float:
        return float(self.capacity_mass)

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        kinds_str = "/".join(sorted(k.name.lower() for k in self.policy.allowed_kinds))
        if self.policy.allowed_type_ids is None:
            type_filter = "any"
        else:
            type_filter = "/".join(sorted(self.policy.allowed_type_ids))
        return [{
            "label": "Container",
            "value": f"{self.capacity_mass:.0f} mass ({kinds_str}: {type_filter})",
            "color_hint": HINT_NEUTRAL,
        }]


# ---------------------------------------------------------------------------
# Parity helpers — compile a legacy ability into the equivalent
# (capacity_mass, ContainerPolicy) view.
# ---------------------------------------------------------------------------


def container_view_from_resource_storage(
    ability: ResourceStorage,
) -> tuple[float, ContainerPolicy]:
    """Compile a `ResourceStorage` into the equivalent Container view.

    `ResourceStorage(resource_id, max_amount)` stores up to `max_amount`
    native units of `resource_id`. The Container equivalent caps mass at
    `max_amount * mass_per_unit(resource_id)` and restricts policy to
    that single resource id.
    """
    # Import here to avoid pulling the resource catalog at module-import
    # time; tests inject catalogs via container.set_resource_catalog().
    from game.strategy.data.container import _get_resource_catalog

    catalog = _get_resource_catalog()
    mass_per_unit = catalog.get_mass_per_unit(ability.resource_type)
    capacity_mass = float(ability.max_amount) * mass_per_unit
    policy = ContainerPolicy(
        allowed_kinds=frozenset({ContainableKind.RESOURCE}),
        allowed_type_ids=frozenset({ability.resource_type}),
    )
    return capacity_mass, policy


def container_view_from_cargo_storage(
    ability: CargoStorage,
) -> tuple[float, ContainerPolicy]:
    """Compile a `CargoStorage` into the equivalent Container view.

    Today's `CargoStorage` has two meaningful shapes:
    - `cargo_type="passengers"`: population storage. The `capacity`
      number is interpreted as "number of population units", so the
      mass cap is `capacity * SPECIES_DEFAULT_MASS_PER_UNIT` and the
      policy accepts any population species.
    - Anything else ("generic" / custom): mass-cap is `capacity`
      directly (the unit semantics of legacy generic cargo are
      ambiguous; the safe compile is "any kind of containable up to
      that mass"). The policy accepts all three kinds.
    """
    if ability.cargo_type == "passengers":
        capacity_mass = float(ability.capacity) * SPECIES_DEFAULT_MASS_PER_UNIT
        policy = ContainerPolicy(
            allowed_kinds=frozenset({ContainableKind.POPULATION}),
            allowed_type_ids=None,
        )
    else:
        capacity_mass = float(ability.capacity)
        policy = ContainerPolicy(
            allowed_kinds=frozenset({
                ContainableKind.RESOURCE,
                ContainableKind.ITEM,
                ContainableKind.POPULATION,
            }),
            allowed_type_ids=None,
        )
    return capacity_mass, policy


def container_view_from_vehicle_bay(
    ability: VehicleBayAbility,
) -> tuple[float, ContainerPolicy]:
    """Compile a `VehicleBayAbility` into the equivalent Container view.

    The shape is already mass-based and type-allowlisted; the
    translation is direct.
    """
    capacity_mass = float(ability.capacity_mass)
    policy = ContainerPolicy(
        allowed_kinds=frozenset({ContainableKind.ITEM}),
        allowed_type_ids=frozenset(ability.allowed_types),
    )
    return capacity_mass, policy


__all__ = [
    "ContainerAbility",
    "container_view_from_cargo_storage",
    "container_view_from_resource_storage",
    "container_view_from_vehicle_bay",
]
