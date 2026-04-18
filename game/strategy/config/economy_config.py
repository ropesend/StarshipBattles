"""Economy configuration loader (PROJ-284 Phase 2).

Loads the population food resource and per-pop-per-turn rate from
`data/economy.json` so modders can swap "organics" for any other
planetary resource without touching code. UI labels resolve via
`ResourceCatalog.get(id).display_name` — never hardcode the resource
name outside this file's JSON.

Pattern: module-level `_default` singleton + `get_default_* / set_default_*`
accessors (CLAUDE.md). Chose this over `@lru_cache` (as used by
`ClassificationConfig`) because the PROJ-284 plan and CLAUDE.md both
lean toward the module-accessor form, and the setter gives tests a
clean swap API without poking `.cache_clear()`.

Graceful fallback: missing / malformed JSON falls back to the hardcoded
defaults documented at `DEFAULT_POPULATION_FOOD_RESOURCE` /
`DEFAULT_FOOD_PER_POP_PER_TURN` rather than raising. Per CLAUDE.md's
System Migration Policy, save compatibility isn't a concern — but a
fresh install where `data/economy.json` is missing should still boot.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Optional

from game.core.paths import Paths

logger = logging.getLogger(__name__)

__all__ = [
    "EconomyConfig",
    "DEFAULT_POPULATION_FOOD_RESOURCE",
    "DEFAULT_FOOD_PER_POP_PER_TURN",
    "load_economy_config",
    "get_default_economy_config",
    "set_default_economy_config",
]


DEFAULT_POPULATION_FOOD_RESOURCE: str = "organics"
DEFAULT_FOOD_PER_POP_PER_TURN: float = 0.001


@dataclass(frozen=True)
class EconomyConfig:
    """Immutable economy parameters loaded from `data/economy.json`."""

    population_food_resource: str
    food_per_pop_per_turn: float


def load_economy_config(path: Optional[str] = None) -> EconomyConfig:
    """Load `EconomyConfig` from JSON, falling back to defaults on error.

    Args:
        path: Optional override path. Defaults to `<data>/economy.json`.

    Returns:
        `EconomyConfig`. Missing file, unreadable file, or malformed JSON
        all produce the hardcoded defaults — consistent with the
        graceful-fallback behavior of other strategy-layer data-driven
        configs (see `ClassificationConfig.get_classification_config`).
    """
    import os

    resolved = path if path is not None else os.path.join(Paths.DATA_DIR, "economy.json")
    try:
        with open(resolved, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (FileNotFoundError, OSError, json.JSONDecodeError) as e:
        logger.warning(
            "Failed to load economy config from %s: %s. Using defaults.",
            resolved, e,
        )
        data = {}

    if not isinstance(data, dict):
        logger.warning("economy.json did not contain a JSON object; using defaults.")
        data = {}

    return EconomyConfig(
        population_food_resource=str(
            data.get("population_food_resource", DEFAULT_POPULATION_FOOD_RESOURCE)
        ),
        food_per_pop_per_turn=float(
            data.get("food_per_pop_per_turn", DEFAULT_FOOD_PER_POP_PER_TURN)
        ),
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
