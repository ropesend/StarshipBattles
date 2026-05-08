"""Economy configuration loader (PROJ-284 Phase 2 + PROJ-286 Phase 1).

Loads the per-resource population-consumption dict from
`data/economy.json` so modders can declare any planetary resources as
population upkeep without touching code. UI labels resolve via
`ResourceCatalog.get(id).display_name` — never hardcode resource
display names outside this file's JSON.

Schema (PROJ-286 + FEAT-19):
    {
        "population_consumption": {
            "<resource_id>": <rate_per_pop_per_turn>,
            ...
        },
        "surplus_food_bonus_per_x": <happiness per +1.0 surplus, default 0.20>,
        "surplus_food_bonus_cap": <max bonus per turn, default 0.20>
    }

FEAT-19 surplus fields are optional. HappinessEngine reads them to
award an additive happiness bonus when `cfg.last_food_surplus > 1.0`
(allocation > 1.0× AND supply meets the elevated demand). Both have
dataclass defaults so existing economy.json files keep working.

The engine iterates `population_consumption.items()`, drains each
resource from the colony stockpile per turn, and writes a per-resource
supply ratio onto `ColonySpeciesConfig.last_consumption_ratios`. The
aggregate `last_food_ratio` (MIN across resources — Liebig's Law)
feeds HappinessEngine + PopulationEngine unchanged.

Pattern: module-level `_default` singleton + `get_default_* / set_default_*`
accessors (CLAUDE.md). Chose this over `@lru_cache` (as used by
`ClassificationConfig`) because CLAUDE.md's module-accessor form gives
tests a clean swap API without poking `.cache_clear()`.

Graceful fallback: missing / malformed JSON, or `population_consumption`
present but not a dict, falls back to the hardcoded single-organics
default at `DEFAULT_POPULATION_CONSUMPTION`. A fresh install missing
`data/economy.json` still boots with PROJ-284-equivalent gameplay.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional

from game.core.json_utils import load_json
from game.core.paths import Paths

logger = logging.getLogger(__name__)

__all__ = [
    "EconomyConfig",
    "DEFAULT_POPULATION_CONSUMPTION",
    "load_economy_config",
    "get_default_economy_config",
    "set_default_economy_config",
]


DEFAULT_POPULATION_CONSUMPTION: Dict[str, float] = {"organics": 0.001}


@dataclass(frozen=True)
class EconomyConfig:
    """Immutable economy parameters loaded from `data/economy.json`."""

    population_consumption: Dict[str, float]
    # FEAT-19 — additive happiness bonus when cfg.last_food_surplus > 1.0.
    # Defaults shipped at +0.20 per +1.0 surplus, capped at +0.20 per turn.
    surplus_food_bonus_per_x: float = 0.20
    surplus_food_bonus_cap: float = 0.20

    @property
    def primary_resource(self) -> str:
        """First resource in `population_consumption` — used by UI titles
        that name the primary food resource (e.g. FoodAllocationEditor).
        Dict insertion order is preserved (Python 3.7+); data-file
        authors control ordering. Returns `"organics"` as a safe fallback
        when the dict is empty.

        PROJ-291 C2: the `population_food_resource` legacy shim was
        retired — the FoodAllocationEditor now reads this property
        directly.
        """
        return next(iter(self.population_consumption), "organics")


def load_economy_config(path: Optional[str] = None) -> EconomyConfig:
    """Load `EconomyConfig` from JSON, falling back to defaults on error.

    Args:
        path: Optional override path. Defaults to `<data>/economy.json`.

    Returns:
        `EconomyConfig`. Missing file, unreadable file, malformed JSON,
        or a `population_consumption` value that isn't a dict all
        produce the hardcoded `DEFAULT_POPULATION_CONSUMPTION` — a
        single-organics dict matching PROJ-284 behavior so a missing
        JSON doesn't silently change gameplay.
    """
    import os

    resolved = path if path is not None else os.path.join(Paths.DATA_DIR, "economy.json")
    # PROJ-381 Phase 2 (ERR-02-004): route through canonical json_utils so
    # missing-file / corrupt-JSON / OSError all collapse into the same
    # default-{} graceful-degradation contract used everywhere else in
    # the strategy layer.
    data = load_json(resolved, default={})

    if not isinstance(data, dict):
        logger.warning("economy.json did not contain a JSON object; using defaults.")
        data = {}

    raw_consumption = data.get("population_consumption")
    if not isinstance(raw_consumption, dict):
        consumption = dict(DEFAULT_POPULATION_CONSUMPTION)
    else:
        consumption = {str(k): float(v) for k, v in raw_consumption.items()}

    # FEAT-19 — graceful defaults so a file missing the surplus keys still
    # boots with the standard +0.20 / +0.20 cap shipped values.
    bonus_per_x = float(data.get("surplus_food_bonus_per_x", 0.20))
    bonus_cap = float(data.get("surplus_food_bonus_cap", 0.20))

    return EconomyConfig(
        population_consumption=consumption,
        surplus_food_bonus_per_x=bonus_per_x,
        surplus_food_bonus_cap=bonus_cap,
    )


_default: Optional[EconomyConfig] = None


def get_default_economy_config() -> EconomyConfig:
    """Return the cached default `EconomyConfig`, lazy-loading on first call."""
    global _default
    if _default is None:
        _default = load_economy_config()
    return _default


def set_default_economy_config(cfg: Optional[EconomyConfig]) -> None:
    """Override the cached default. Pass `None` to clear the cache so
    the next `get_default_economy_config()` lazy-loads from disk."""
    global _default
    _default = cfg
