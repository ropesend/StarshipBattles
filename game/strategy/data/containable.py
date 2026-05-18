"""
Containable types for the unified storage substrate (PROJ-436).

Provides three Containable variants — `ResourceContainable`,
`ItemContainable`, `PopulationContainable` — sharing a common kind /
type_id / mass_per_unit surface that `Container` (see container.py)
dispatches on.

Per the PROJ-436 charter:
- RESOURCE: continuous (float), no identity; mass-per-unit comes from
  the existing Core-layer `ResourceCatalog` in game/core/resources.py.
- ITEM: discrete with identity; mass-per-unit is on the carried
  `ItemRef` (resolved from design metadata at construction time).
- POPULATION: discrete per-species (integer count); mass-per-unit
  defaults to 0.1 (10 individuals per ton) per user direction.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# Default mass per individual member of a species, in tons (per user
# directive: 10 individuals per ton). Race JSONs may override per
# species in later phases; Phase 0 ships the default only.
SPECIES_DEFAULT_MASS_PER_UNIT: float = 0.1


class ContainableKind(Enum):
    """The three top-level content kinds the unified Container supports."""

    RESOURCE = "resource"
    ITEM = "item"
    POPULATION = "population"


@dataclass(frozen=True)
class ItemRef:
    """A discrete item with identity carried in a Container's items slice.

    Mass is explicit rather than looked up from a registry because
    item mass derives from the design + per-instance state (damage,
    cargo, etc.) at the time the item was constructed.

    Attributes:
        design_id: the design this item was built from.
        instance_id: stable per-instance identity (uuid-ish; the
            substrate does not assign one — callers do).
        mass: total mass of this specific item, in tons.
        state: arbitrary per-instance state (damage map, etc.).
    """

    design_id: str
    instance_id: str
    mass: float
    state: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResourceContainable:
    """Resource entry: continuous, identified by `resource_id`.

    Mass resolves through the existing Core-layer `ResourceCatalog`.
    Construction itself does not consult the catalog so this class
    stays a pure value type; the `Container` performs the mass lookup
    at add/remove time so a stub catalog can be injected in tests
    without monkey-patching the dataclass.
    """

    resource_id: str

    @property
    def kind(self) -> ContainableKind:
        return ContainableKind.RESOURCE

    @property
    def type_id(self) -> str:
        return self.resource_id


@dataclass(frozen=True)
class ItemContainable:
    """Item entry: discrete with identity.

    The carried `ItemRef` is the source of truth for both identity
    (`instance_id`) and mass.
    """

    item_ref: ItemRef

    @property
    def kind(self) -> ContainableKind:
        return ContainableKind.ITEM

    @property
    def type_id(self) -> str:
        return self.item_ref.design_id


@dataclass(frozen=True)
class PopulationContainable:
    """Population entry: discrete per-species (integer counts).

    The `type_id` is the `species_id`. Mass-per-unit defaults to
    `SPECIES_DEFAULT_MASS_PER_UNIT` (0.1 per user directive); race
    JSON extension is deferred to PROJ-436 Phase 3 per design.
    """

    species_id: str

    @property
    def kind(self) -> ContainableKind:
        return ContainableKind.POPULATION

    @property
    def type_id(self) -> str:
        return self.species_id


# Union type alias for any Containable.
Containable = ResourceContainable | ItemContainable | PopulationContainable


def species_mass_per_unit(species_id: str) -> float:
    """Mass per individual of `species_id`, in tons.

    Phase 0 returns `SPECIES_DEFAULT_MASS_PER_UNIT` for any species.
    Phase 3 (or wherever the first population transfer integration
    test lands) will extend race JSONs with an override field; this
    helper is the single lookup site that will swap to the registry
    at that time.
    """
    return SPECIES_DEFAULT_MASS_PER_UNIT
