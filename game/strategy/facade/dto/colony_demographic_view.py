"""Colony demographics view DTO (PROJ-288 Phase 3).

`ColonyDemographicView` aggregates everything a colony-demographics UI
panel needs in one read — per-species lines and per-resource projections,
plus a summed `total_upkeep` for empire-aggregation panels (PROJ-290).

Both DTOs are frozen `@dataclass` instances so the facade can hand them
straight to the UI layer with the CQRS-lite read-only contract intact.
The species tuple is ordered largest-count-first; UI consumers display
in that order without needing to re-sort.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple

from game.strategy.services.planet_economy_projector import ResourceProjection


@dataclass(frozen=True)
class SpeciesDemographicView:
    """One row in a colony's per-species demographics table.

    Fields:
        race_id:          Stable identifier (matches `RaceConfig.race_id`).
        race_name:        Display name; falls back to `race_id` if the race's
                          `race_name`/`name` are both empty.
        count:            Current population units (1 unit = 1,000 people).
        habitability:     `score_planet_for_race(planet, race_config)` -> [0, 1].
        happiness:        Current `pop.happiness` (HappinessEngine output, [0, 3]).
        growth_rate:      Per-capita next-turn rate from `projected_growth_rate`.
                          Multiply by `count` for absolute Δpop.
        food_ratio:       `cfg.last_food_ratio` (MIN across consumption resources).
        food_allocation:  `cfg.food_allocation` slider value.
    """
    race_id: str
    race_name: str
    count: int
    habitability: float
    happiness: float
    growth_rate: float
    food_ratio: float
    food_allocation: float


@dataclass(frozen=True)
class ColonyDemographicView:
    """One-shot snapshot of all demographic + economic data for a colony.

    Fields:
        planet_id:           Stable Planet identifier.
        planet_name:         Display name.
        species:             Per-species rows, ordered largest count first.
                             Species whose `race_id` cannot be resolved by
                             the registry are SKIPPED (save drift defence).
        resource_projections: Per-resource flux from
                             `PlanetEconomyProjector.project(planet)`.
        total_upkeep:        Sum of per-species upkeep across the colony,
                             keyed by resource_id. Used by Treasury /
                             empire-aggregation panels (PROJ-290).
    """
    planet_id: int
    planet_name: str
    species: Tuple[SpeciesDemographicView, ...]
    resource_projections: Tuple[ResourceProjection, ...]
    total_upkeep: Mapping[str, float]

    def __post_init__(self):
        # PROJ-292 m4: enforce read-only contract on `total_upkeep`. The
        # frozen dataclass prevents field reassignment but does NOT stop
        # callers from mutating the underlying mapping (e.g. `view.total_upkeep["x"] = 1`).
        # Wrapping in MappingProxyType makes that TypeError so the
        # CQRS-lite "facade hands UI a read-only snapshot" contract holds.
        object.__setattr__(
            self, "total_upkeep", MappingProxyType(dict(self.total_upkeep)),
        )
        # PROJ-292 m5: enforce largest-count-first ordering invariant in
        # the DTO itself. Previously the facade sorted before construction;
        # if a future caller skips that pre-sort, the DTO's docstring
        # contract still holds.
        object.__setattr__(
            self, "species",
            tuple(sorted(self.species, key=lambda s: s.count, reverse=True)),
        )
