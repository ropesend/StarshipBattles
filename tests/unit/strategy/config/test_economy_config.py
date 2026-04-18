"""Unit tests for `EconomyConfig` loader (PROJ-284 Phase 2).

Covers the data-driven food-resource config living at
`game/strategy/config/economy_config.py`. The loader follows the
`get_default_* / set_default_*` module-accessor pattern documented in
CLAUDE.md — a module-level `_default` singleton, lazy-loaded on first
read from `data/economy.json`, swappable via `set_default_economy_config`
for tests and mod-runtime overrides.

Default shape (per the PROJ-284 plan):
    {
        "population_food_resource": "organics",
        "food_per_pop_per_turn": 0.001
    }

`EconomyConfig` itself is a frozen dataclass — equality / round-trip are
dataclass defaults, no custom `to_dict`/`from_dict` since this is a
read-only loaded config (not persisted state).
"""
from __future__ import annotations

import json

import pytest


@pytest.fixture(autouse=True)
def _reset_default_economy_config():
    """Reset the module-level singleton before and after every test so
    `set_default_economy_config` state from one test can't bleed into
    another."""
    from game.strategy.config import economy_config as mod
    mod.set_default_economy_config(None)
    yield
    mod.set_default_economy_config(None)


class TestEconomyConfigDataclass:
    def test_is_frozen_dataclass(self):
        from game.strategy.config.economy_config import EconomyConfig
        cfg = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)
        with pytest.raises((AttributeError, Exception)):
            cfg.food_per_pop_per_turn = 0.5  # type: ignore[misc]

    def test_equality_by_field_values(self):
        from game.strategy.config.economy_config import EconomyConfig
        a = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)
        b = EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)
        c = EconomyConfig(population_food_resource="metals", food_per_pop_per_turn=0.001)
        assert a == b
        assert a != c


class TestLoadEconomyConfigFromDefault:
    def test_loads_default_from_data_path(self):
        """The shipped `data/economy.json` must exist and produce the
        documented defaults (organics, 0.001)."""
        from game.strategy.config.economy_config import load_economy_config
        cfg = load_economy_config()
        assert cfg.population_food_resource == "organics"
        assert cfg.food_per_pop_per_turn == pytest.approx(0.001)

    def test_missing_file_falls_back_to_defaults(self, tmp_path):
        """Per CLAUDE.md's system-migration policy (save files are
        disposable), a missing `data/economy.json` must return hardcoded
        defaults rather than crashing."""
        from game.strategy.config.economy_config import load_economy_config
        missing = tmp_path / "does_not_exist.json"
        cfg = load_economy_config(path=str(missing))
        assert cfg.population_food_resource == "organics"
        assert cfg.food_per_pop_per_turn == pytest.approx(0.001)


class TestLoadEconomyConfigFromCustomPath:
    def test_loads_custom_values(self, tmp_path):
        """Modders swap the food resource by editing the JSON; the loader
        must honor the override end-to-end."""
        from game.strategy.config.economy_config import load_economy_config
        custom = tmp_path / "economy.json"
        custom.write_text(json.dumps({
            "population_food_resource": "metals",
            "food_per_pop_per_turn": 0.005,
        }))
        cfg = load_economy_config(path=str(custom))
        assert cfg.population_food_resource == "metals"
        assert cfg.food_per_pop_per_turn == pytest.approx(0.005)

    def test_partial_json_falls_back_to_default_per_field(self, tmp_path):
        """If the JSON omits a key, the loader fills from the hardcoded
        defaults so a partial mod edit doesn't crash the game."""
        from game.strategy.config.economy_config import load_economy_config
        partial = tmp_path / "economy.json"
        partial.write_text(json.dumps({"food_per_pop_per_turn": 0.01}))
        cfg = load_economy_config(path=str(partial))
        assert cfg.population_food_resource == "organics"  # default
        assert cfg.food_per_pop_per_turn == pytest.approx(0.01)  # override


class TestDefaultSingletonAccessor:
    def test_get_default_is_cached(self):
        """Back-to-back calls return the SAME instance (module-level
        lazy-cache). JSON is loaded exactly once."""
        from game.strategy.config.economy_config import get_default_economy_config
        first = get_default_economy_config()
        second = get_default_economy_config()
        assert first is second

    def test_set_default_overrides_cache(self):
        """`set_default_economy_config(cfg)` replaces the singleton; the
        next `get_default_economy_config()` must return the injected
        instance without re-reading JSON."""
        from game.strategy.config.economy_config import (
            EconomyConfig,
            get_default_economy_config,
            set_default_economy_config,
        )
        injected = EconomyConfig(
            population_food_resource="metals",
            food_per_pop_per_turn=0.5,
        )
        set_default_economy_config(injected)
        assert get_default_economy_config() is injected

    def test_set_default_none_resets_cache(self):
        """Passing `None` clears the cache — the next read lazy-loads
        from disk again. Tests rely on this for isolation (see the
        autouse `_reset_default_economy_config` fixture)."""
        from game.strategy.config.economy_config import (
            EconomyConfig,
            get_default_economy_config,
            set_default_economy_config,
        )
        first = get_default_economy_config()
        set_default_economy_config(None)
        second = get_default_economy_config()
        # New instance loaded from JSON (equal by value but not identity).
        assert first is not second
        assert first == second
