"""Tests for homeworld presets loading and application (PROJ-283 Phase 5).

Phase 5 rewrote the preset shape: each preset now declares a partial
`preferences: Dict[str, {setpoint, tolerance}]` keyed by `FACTOR_REGISTRY`
factor ids, plus an optional `base_reproduction_rate`. Factors not
listed in a preset's `preferences` retain whatever value the
`RaceConfig` already has (typically the registry default backfilled by
`__post_init__`).

This file replaces the Phase 4 transitional-shim tests entirely. The
legacy preset shape (display-name gas scores, gravity in g, etc.) is
gone from `data/homeworld_presets.json`.
"""
from __future__ import annotations

import pytest

from game.strategy.data.homeworld_presets import (
    apply_preset_to_config,
    get_available_homeworld_names,
    get_preset_for_planet_type,
    load_homeworld_presets,
)
from game.strategy.data.race_config import RaceConfig


# ---------------------------------------------------------------------------
# JSON loading + shape
# ---------------------------------------------------------------------------


class TestLoadHomeworldPresets:
    def test_returns_all_11_planet_types(self):
        presets = load_homeworld_presets()
        assert len(presets) == 11
        expected_types = {
            "CONTINENTAL", "ARID", "PELAGIC", "MAGMA", "CRYOPLANET",
            "BARREN", "JOVIAN", "ICE_GIANT", "CHTHONIAN", "ICE_DWARF", "PLANETOID",
        }
        assert set(presets.keys()) == expected_types

    def test_every_preset_has_id_name_description_preferences(self):
        for pid, preset in load_homeworld_presets().items():
            assert preset["id"] == pid
            assert isinstance(preset.get("name"), str)
            assert isinstance(preset.get("description"), str)
            assert isinstance(preset.get("preferences"), dict)


# ---------------------------------------------------------------------------
# Per-preset content
# ---------------------------------------------------------------------------


class TestGetPresetForPlanetType:
    def test_continental_is_earth_like(self):
        preset = get_preset_for_planet_type("CONTINENTAL")
        assert preset is not None
        assert preset["name"] == "Continental"
        prefs = preset["preferences"]
        # Earth-like surface conditions
        assert prefs["gravity"]["setpoint"] == pytest.approx(9.81, abs=0.1)
        assert prefs["temperature"]["setpoint"] == pytest.approx(293.0, abs=1.0)
        assert prefs["water"]["setpoint"] == pytest.approx(0.6, abs=0.05)
        # Earth-like atmosphere (registry stores Pa)
        assert prefs["gas.O2"]["setpoint"] == pytest.approx(21000.0, abs=1000.0)
        assert prefs["gas.N2"]["setpoint"] == pytest.approx(79000.0, abs=1000.0)

    def test_jovian_is_gas_giant(self):
        preset = get_preset_for_planet_type("JOVIAN")
        assert preset is not None
        prefs = preset["preferences"]
        assert prefs["gravity"]["setpoint"] > 9.81 * 2  # heavier than Earth
        # Hydrogen + helium dominated
        assert prefs["gas.H2"]["setpoint"] > 0
        assert prefs["gas.He"]["setpoint"] > 0
        assert prefs["gas.O2"]["setpoint"] == 0  # no oxygen

    def test_arid_is_hot_dry(self):
        preset = get_preset_for_planet_type("ARID")
        assert preset is not None
        prefs = preset["preferences"]
        assert prefs["temperature"]["setpoint"] > 300  # hot
        assert prefs["water"]["setpoint"] < 0.2  # dry

    def test_magma_extremes(self):
        preset = get_preset_for_planet_type("MAGMA")
        assert preset is not None
        prefs = preset["preferences"]
        assert prefs["temperature"]["setpoint"] >= 700  # very hot
        assert prefs["water"]["setpoint"] == pytest.approx(0.0, abs=0.05)

    def test_invalid_returns_none(self):
        assert get_preset_for_planet_type("INVALID_TYPE") is None


# ---------------------------------------------------------------------------
# apply_preset_to_config
# ---------------------------------------------------------------------------


class TestApplyPresetToConfig:
    @pytest.fixture
    def fresh_config(self):
        return RaceConfig(
            name="Test Race",
            flag_id="flag_test",
            portrait_id="portrait_test",
            theme_id="Federation",
        )

    def test_applies_gravity_setpoint(self, fresh_config):
        preset = get_preset_for_planet_type("JOVIAN")
        apply_preset_to_config(preset, fresh_config)
        assert fresh_config.preferences["gravity"].setpoint > 20  # ~2.5 g

    def test_applies_temperature(self, fresh_config):
        preset = get_preset_for_planet_type("CRYOPLANET")
        apply_preset_to_config(preset, fresh_config)
        assert fresh_config.preferences["temperature"].setpoint == pytest.approx(200, abs=1)

    def test_applies_water(self, fresh_config):
        preset = get_preset_for_planet_type("PELAGIC")
        apply_preset_to_config(preset, fresh_config)
        assert fresh_config.preferences["water"].setpoint == pytest.approx(0.95, abs=0.05)

    def test_applies_atmosphere(self, fresh_config):
        preset = get_preset_for_planet_type("ICE_GIANT")
        apply_preset_to_config(preset, fresh_config)
        # Ice giant: hydrogen + helium dominated
        assert fresh_config.preferences["gas.H2"].setpoint > 0
        assert fresh_config.preferences["gas.He"].setpoint > 0

    def test_sets_homeworld_type(self, fresh_config):
        preset = get_preset_for_planet_type("CONTINENTAL")
        apply_preset_to_config(preset, fresh_config)
        assert fresh_config.homeworld_type == "CONTINENTAL"

    def test_preserves_unspecified_factors(self, fresh_config):
        """A preset that doesn't list a factor leaves it untouched.

        E.g., Continental doesn't say anything about magnetic field —
        the race's `preferences['magnetic']` keeps its registry default."""
        from game.strategy.data.habitability_factors import get_factor

        magnetic = get_factor("magnetic")
        # Sanity: the fresh config has the registry default.
        assert fresh_config.preferences["magnetic"].setpoint == magnetic.default_setpoint

        preset = get_preset_for_planet_type("CONTINENTAL")
        apply_preset_to_config(preset, fresh_config)

        assert fresh_config.preferences["magnetic"].setpoint == magnetic.default_setpoint

    def test_none_preset_is_safe(self, fresh_config):
        """Passing None for the preset (e.g., '(Custom)' selection) must
        not mutate the config."""
        original_gravity = fresh_config.preferences["gravity"].setpoint
        apply_preset_to_config(None, fresh_config)
        assert fresh_config.preferences["gravity"].setpoint == original_gravity


# ---------------------------------------------------------------------------
# Dropdown helper
# ---------------------------------------------------------------------------


class TestGetAvailableHomeworldNames:
    def test_returns_11_names(self):
        names = get_available_homeworld_names()
        assert len(names) == 11
        assert "Continental" in names
        assert "Jovian" in names
        assert "Ice Giant" in names

    def test_names_are_display_formatted(self):
        for name in get_available_homeworld_names():
            assert name[0].isupper()
            assert "_" not in name
