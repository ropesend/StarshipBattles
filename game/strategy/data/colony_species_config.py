"""Per-colony per-species configuration (PROJ-284 + PROJ-286).

`ColonySpeciesConfig` is the home for player-set sliders that apply to
ONE species on ONE colony. Currently:

    food_allocation:
        Scales the species' upkeep consumption AND the
        `happiness * reproduction` chain linearly. Default 1.0 =
        "normal rations". 0.0 = "starve them"; > 1.0 = "over-supply
        for happiness/growth bonuses". UI caps at 5.0 for the slider;
        typed input can exceed (with diminishing-returns territory).

    last_consumption_ratios:
        TRANSIENT per-resource supply-ratio dict written by
        `OrganicsConsumptionEngine` each turn. Keys are resource ids
        declared in `EconomyConfig.population_consumption`; values are
        `supplied / needed` per resource. NOT serialized — saving it
        would lie about the post-load demographic state, which the
        next turn's consumption pass overwrites anyway.

    last_food_ratio (computed property):
        `min(last_consumption_ratios.values())` with 1.0 fallback when
        the dict is empty. Models Liebig's Law of the Minimum — the
        colony is "as well-fed as its worst-supplied resource". Read by
        HappinessEngine + PopulationEngine unchanged; their source
        files do not change when upgrading from single-resource
        (PROJ-284) to multi-resource (PROJ-286) consumption.

    last_food_surplus (computed property — FEAT-19):
        `food_allocation × MIN(last_consumption_ratios)` with 1.0
        fallback when the dict is empty. Unbounded; only exceeds 1.0
        when allocation > 1.0 AND supply meets the elevated demand.
        Read by HappinessEngine to award an additive surplus-food
        happiness bonus. Identity: each per-resource ratio is
        `supplied / (count × allocation × rate)`, so multiplying by
        `allocation` yields `supplied / (count × rate)` —
        i.e. "supplied / needed_at_1x", which is the surplus the player
        is asking us to reward.

Storage location: `Planet.species_configs: Dict[race_id, ColonySpeciesConfig]`.
This keeps `SpeciesPopulation` pure runtime state and gives future
per-colony per-species knobs (labor allocation, taxation, etc.) a
proper home without polluting the population dataclass.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from game.core.exceptions import ValidationException


@dataclass
class ColonySpeciesConfig:
    """Per-colony per-species sliders. See module docstring."""

    food_allocation: float = 1.0
    # TRANSIENT — see module docstring. Default factory yields a fresh
    # dict per instance so mutating one colony's ratios can't leak into
    # another.
    last_consumption_ratios: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.food_allocation < 0:
            raise ValidationException(
                f"ColonySpeciesConfig: food_allocation must be >= 0, "
                f"got {self.food_allocation}"
            )

    @property
    def last_food_ratio(self) -> float:
        """Aggregate supply ratio for happiness / population formulas.

        MIN across all declared resource ratios — "as well-fed as the
        worst-supplied resource" (Liebig's Law of the Minimum). Returns
        1.0 when `last_consumption_ratios` is empty (uncolonized /
        pre-first-turn / zero-pop / zero-allocation), preserving the
        PROJ-284 default-1.0 contract for downstream HappinessEngine +
        PopulationEngine reads.

        No setter: callers that want to influence the ratio must write
        to `last_consumption_ratios` directly. This prevents tests and
        engines from accidentally shadowing the aggregate with a stale
        scalar while the dict contains different per-resource values.
        """
        if not self.last_consumption_ratios:
            return 1.0
        return min(self.last_consumption_ratios.values())

    @property
    def last_food_surplus(self) -> float:
        """FEAT-19 — unbounded "supplied / needed_at_1x" aggregate.

        Equals `food_allocation × MIN(last_consumption_ratios)`. Returns
        1.0 when the dict is empty (uncolonized / pre-first-turn /
        zero-pop), preserving the no-demand-no-surplus invariant.

        Only exceeds 1.0 when allocation > 1.0 AND every declared
        resource's supply meets the elevated demand — exactly the
        surplus-reward case. Below 1.0× allocation it equals
        `last_food_ratio` (MIN drags it down). HappinessEngine reads
        this to award an additive bonus when surplus > 1.0.
        """
        if not self.last_consumption_ratios:
            return 1.0
        return self.food_allocation * min(self.last_consumption_ratios.values())

    def to_dict(self) -> Dict[str, Any]:
        """Emit only persistable fields. `last_consumption_ratios` is
        transient — see module docstring."""
        return {"food_allocation": self.food_allocation}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ColonySpeciesConfig":
        """Rehydrate from save data. Ignores any transient-ratio keys
        (`last_consumption_ratios` / `last_food_ratio`) if present —
        next turn's consumption engine rewrites the dict anyway."""
        return cls(food_allocation=float(data.get("food_allocation", 1.0)))
