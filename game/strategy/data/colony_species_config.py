"""Per-colony per-species configuration (PROJ-284).

`ColonySpeciesConfig` is the home for player-set sliders that apply to
ONE species on ONE colony. Currently:

    food_allocation:  scales the species' organics consumption AND the
                      `happiness * reproduction` chain linearly. Default
                      1.0 = "normal rations". 0.0 = "starve them"; > 1.0
                      = "over-supply for happiness/growth bonuses". UI
                      caps at 5.0 for the slider; typed input can exceed
                      (with diminishing-returns territory).
    last_food_ratio:  TRANSIENT cache written by
                      `OrganicsConsumptionEngine` each turn:
                          last_food_ratio = supplied / needed
                      Read by `HappinessEngine` and `PopulationEngine`.
                      NOT serialized — saving it would lie about the
                      post-load demographic state, which the next turn's
                      consumption pass will overwrite anyway.

Storage location: `Planet.species_configs: Dict[race_id, ColonySpeciesConfig]`.
This keeps `SpeciesPopulation` pure runtime state and gives future
per-colony per-species knobs (labor allocation, taxation, etc.) a
proper home without polluting the population dataclass.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from game.core.exceptions import ValidationException


@dataclass
class ColonySpeciesConfig:
    """Per-colony per-species sliders. See module docstring."""

    food_allocation: float = 1.0
    last_food_ratio: float = 1.0  # TRANSIENT — see module docstring

    def __post_init__(self) -> None:
        if self.food_allocation < 0:
            raise ValidationException(
                f"ColonySpeciesConfig: food_allocation must be >= 0, "
                f"got {self.food_allocation}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Emit only persistable fields. `last_food_ratio` is transient."""
        return {"food_allocation": self.food_allocation}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ColonySpeciesConfig":
        """Rehydrate from save data. Ignores `last_food_ratio` if
        present (back-compat for forks of the schema); it stays at the
        constructor default."""
        return cls(food_allocation=float(data.get("food_allocation", 1.0)))
