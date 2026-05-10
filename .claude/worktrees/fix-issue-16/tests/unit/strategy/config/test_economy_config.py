"""Unit tests for `EconomyConfig` loader (PROJ-284 Phase 2 + PROJ-286 Phase 1).

Covers the data-driven population-consumption config living at
`game/strategy/config/economy_config.py`. The loader follows the
`get_default_* / set_default_*` module-accessor pattern documented in
CLAUDE.md — a module-level `_default` singleton, lazy-loaded on first
read from `data/economy.json`, swappable via `set_default_economy_config`
for tests and mod-runtime overrides.

Default shape (per PROJ-286 Phase 1):
    {
        "population_consumption": {
            "organics": 0.001,
            "metals": 0.0001,
            "radioactives": 0.00001
        }
    }

`EconomyConfig` is a frozen dataclass. Equality / round-trip are
dataclass defaults. `primary_resource` + `population_food_resource` are
computed properties; the latter is a read-only shim preserved until
PROJ-289 migrates UI call sites.
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
        cfg = EconomyConfig(population_consumption={"organics": 0.001})
        with pytest.raises((AttributeError, Exception)):
            cfg.population_consumption = {"metals": 0.5}  # type: ignore[misc]

    def test_equality_by_field_values(self):
        from game.strategy.config.economy_config import EconomyConfig
        a = EconomyConfig(population_consumption={"organics": 0.001})
        b = EconomyConfig(population_consumption={"organics": 0.001})
        c = EconomyConfig(population_consumption={"metals": 0.001})
        assert a == b
        assert a != c


class TestPrimaryResourceProperty:
    def test_primary_resource_returns_first_key(self):
        """`primary_resource` returns the first key in insertion order
        (Python 3.7+ dict ordering)."""
        from game.strategy.config.economy_config import EconomyConfig
        cfg = EconomyConfig(
            population_consumption={"organics": 0.001, "metals": 0.0001}
        )
        assert cfg.primary_resource == "organics"

    def test_primary_resource_empty_dict_fallback(self):
        """Empty `population_consumption` returns the hardcoded `"organics"`
        fallback so UI titles don't blow up on misconfigured data files."""
        from game.strategy.config.economy_config import EconomyConfig
        cfg = EconomyConfig(population_consumption={})
        assert cfg.primary_resource == "organics"

    def test_primary_resource_honours_insertion_order(self):
        """A modder that puts `metals` first gets `metals` back as the
        primary — data-file authors control ordering."""
        from game.strategy.config.economy_config import EconomyConfig
        cfg = EconomyConfig(population_consumption={"metals": 0.002, "organics": 0.001})
        assert cfg.primary_resource == "metals"


# PROJ-291 C2: `TestPopulationFoodResourceShim` was deleted along with
# the `population_food_resource` shim property. The FoodAllocationEditor
# now reads `EconomyConfig.primary_resource` directly.


class TestLoadEconomyConfigFromDefault:
    def test_loads_default_from_data_path(self):
        """The shipped `data/economy.json` must produce the documented
        three-resource defaults (organics 0.0001, metals 0.00001,
        radioactives 0.000001)."""
        from game.strategy.config.economy_config import load_economy_config
        cfg = load_economy_config()
        assert cfg.population_consumption == {
            "organics": pytest.approx(0.0001),
            "metals": pytest.approx(0.00001),
            "radioactives": pytest.approx(0.000001),
        }

    def test_missing_file_falls_back_to_defaults(self, tmp_path):
        """Per CLAUDE.md's system-migration policy (save files are
        disposable), a missing `data/economy.json` must return hardcoded
        defaults rather than crashing. The default is a single-resource
        organics dict matching PROJ-284 behavior so a missing JSON
        doesn't change gameplay."""
        from game.strategy.config.economy_config import load_economy_config
        missing = tmp_path / "does_not_exist.json"
        cfg = load_economy_config(path=str(missing))
        assert cfg.population_consumption == {"organics": pytest.approx(0.001)}


class TestLoadEconomyConfigFromCustomPath:
    def test_loads_custom_values(self, tmp_path):
        """Modders swap the upkeep dict by editing the JSON; the loader
        must honor the override end-to-end."""
        from game.strategy.config.economy_config import load_economy_config
        custom = tmp_path / "economy.json"
        custom.write_text(json.dumps({
            "population_consumption": {"metals": 0.005, "organics": 0.002},
        }))
        cfg = load_economy_config(path=str(custom))
        assert cfg.population_consumption == {
            "metals": pytest.approx(0.005),
            "organics": pytest.approx(0.002),
        }
        # Insertion order preserved → primary is metals.
        assert cfg.primary_resource == "metals"

    def test_missing_key_falls_back_to_default_dict(self, tmp_path):
        """If the JSON omits `population_consumption`, the loader falls
        back to the hardcoded single-organics default so a partial mod
        edit doesn't crash the game."""
        from game.strategy.config.economy_config import load_economy_config
        partial = tmp_path / "economy.json"
        partial.write_text(json.dumps({"unrelated_key": 42}))
        cfg = load_economy_config(path=str(partial))
        assert cfg.population_consumption == {"organics": pytest.approx(0.001)}

    def test_malformed_json_falls_back_to_defaults(self, tmp_path):
        """Broken JSON → default dict, not a crash."""
        from game.strategy.config.economy_config import load_economy_config
        broken = tmp_path / "economy.json"
        broken.write_text("{ this is not json")
        cfg = load_economy_config(path=str(broken))
        assert cfg.population_consumption == {"organics": pytest.approx(0.001)}

    def test_non_dict_consumption_value_falls_back(self, tmp_path):
        """If `population_consumption` is present but not a dict (e.g. a
        list or number from a botched edit), fall back to defaults rather
        than crashing on attribute access downstream."""
        from game.strategy.config.economy_config import load_economy_config
        bad = tmp_path / "economy.json"
        bad.write_text(json.dumps({"population_consumption": [1, 2, 3]}))
        cfg = load_economy_config(path=str(bad))
        assert cfg.population_consumption == {"organics": pytest.approx(0.001)}


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
        injected = EconomyConfig(population_consumption={"metals": 0.5})
        set_default_economy_config(injected)
        assert get_default_economy_config() is injected

    def test_set_default_none_resets_cache(self):
        """Passing `None` clears the cache — the next read lazy-loads
        from disk again. Tests rely on this for isolation (see the
        autouse `_reset_default_economy_config` fixture)."""
        from game.strategy.config.economy_config import (
            get_default_economy_config,
            set_default_economy_config,
        )
        first = get_default_economy_config()
        set_default_economy_config(None)
        second = get_default_economy_config()
        # New instance loaded from JSON (equal by value but not identity).
        assert first is not second
        assert first == second
