"""
Unit tests for RaceConfig dataclass (post-PROJ-283 Phase 4 schema).

Phase 4 deleted 10 legacy fields from RaceConfig:
    gravity_ideal, gravity_tolerance, temperature_ideal, temperature_tolerance,
    water_ideal, water_tolerance, atmosphere_preferences, radiation_tolerance,
    aptitude_happiness, aptitude_population_growth

Environmental preferences now live in `RaceConfig.preferences: Dict[str,
EnvironmentalPreference]` keyed by `FACTOR_REGISTRY` ids; reproduction
and happiness are `base_reproduction_rate: float` and `base_happiness: float`.
"""
import pytest
import tempfile
import os
import json

from game.strategy.data.race_config import RaceConfig


# ---------------------------------------------------------------------------
# Basic construction
# ---------------------------------------------------------------------------


class TestRaceConfigBasic:
    def test_create_default_race_config(self):
        config = RaceConfig()
        assert config.race_id == ""
        assert config.name == ""
        assert config.theme_id == "Federation"
        # PROJ-283 Phase 4: legacy environment fields gone; defaults live
        # on `preferences` (registry-backfilled by __post_init__).
        assert config.preferences  # populated
        assert config.base_reproduction_rate == 0.03
        assert config.base_happiness == 0.5

    def test_create_race_config_with_visual_fields(self):
        config = RaceConfig(
            race_id="test_race",
            name="Test Race",
            flag_id="flag_001",
            portrait_id="portrait_001.jpg",
            theme_id="Klingons",
        )
        assert config.race_id == "test_race"
        assert config.name == "Test Race"
        assert config.flag_id == "flag_001"
        assert config.portrait_id == "portrait_001.jpg"
        assert config.theme_id == "Klingons"


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


class TestRaceConfigSerialization:
    def test_to_dict_includes_new_fields(self):
        config = RaceConfig(name="Test")
        data = config.to_dict()
        assert "preferences" in data
        assert "base_reproduction_rate" in data
        assert "base_happiness" in data

    def test_to_dict_excludes_deleted_legacy_fields(self):
        """Phase 4 dropped these keys from to_dict; old saves with them
        present are silently ignored on load."""
        data = RaceConfig().to_dict()
        for key in (
            "gravity_ideal", "gravity_tolerance",
            "temperature_ideal", "temperature_tolerance",
            "water_ideal", "water_tolerance",
            "atmosphere_preferences", "radiation_tolerance",
            "aptitude_happiness", "aptitude_population_growth",
        ):
            assert key not in data, f"Legacy key {key!r} should be gone"

    def test_round_trip_preserves_identity(self):
        original = RaceConfig(
            race_id="r1",
            name="Race One",
            faction_name="The Faction",
            race_name="Racer",
            government_type="Empire",
            leader_title="Emperor",
            leader_name="Zara IV",
        )
        restored = RaceConfig.from_dict(original.to_dict())
        assert restored.race_id == "r1"
        assert restored.name == "Race One"
        assert restored.faction_name == "The Faction"
        assert restored.race_name == "Racer"
        assert restored.government_type == "Empire"
        assert restored.leader_title == "Emperor"
        assert restored.leader_name == "Zara IV"

    def test_from_dict_silently_ignores_legacy_keys(self):
        """Old save files with legacy keys must not crash from_dict."""
        data = {
            "name": "Old Race",
            "gravity_ideal": 1.0,           # legacy — ignored
            "atmosphere_preferences": {     # legacy — ignored
                "Oxygen": 50,
            },
            "aptitude_happiness": 60,       # legacy — ignored
            "aptitude_population_growth": 70,  # legacy — ignored
        }
        config = RaceConfig.from_dict(data)
        assert config.name == "Old Race"
        # New fields default correctly.
        assert config.base_reproduction_rate == 0.03
        assert config.base_happiness == 0.5

    def test_from_dict_missing_fields_uses_defaults(self):
        config = RaceConfig.from_dict({"race_id": "minimal"})
        assert config.race_id == "minimal"
        assert config.name == ""
        assert config.theme_id == "Federation"


# ---------------------------------------------------------------------------
# File IO
# ---------------------------------------------------------------------------


class TestRaceConfigFileIO:
    def test_save_and_load(self):
        config = RaceConfig(
            race_id="io_race",
            name="IO Race",
            faction_name="IO Faction",
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            assert config.save(path)
            loaded = RaceConfig.load(path)
            assert loaded is not None
            assert loaded.race_id == "io_race"
            assert loaded.name == "IO Race"
            assert loaded.faction_name == "IO Faction"
        finally:
            os.unlink(path)

    def test_load_nonexistent_file_returns_none(self):
        assert RaceConfig.load("/no/such/path/race_config.json") is None

    def test_save_updates_modified_date(self):
        config = RaceConfig(name="Time Test")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            assert config.save(path)
            with open(path) as f:
                data = json.load(f)
            assert data["modified_date"]
            assert data["created_date"]
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestRaceConfigValidation:
    def _valid_config(self, **overrides):
        defaults = dict(
            name="Valid",
            flag_id="flag_1",
            portrait_id="portrait.jpg",
            theme_id="Federation",
        )
        defaults.update(overrides)
        return RaceConfig(**defaults)

    def test_default_valid_config(self):
        result = self._valid_config().validate()
        assert result.is_valid, f"Valid config should pass: {result.errors}"

    def test_validate_missing_name(self):
        config = self._valid_config(name="")
        result = config.validate()
        assert not result.is_valid
        assert "name" in str(result.errors).lower()

    def test_validate_missing_flag(self):
        config = self._valid_config(flag_id="")
        result = config.validate()
        assert not result.is_valid

    def test_validate_missing_portrait(self):
        config = self._valid_config(portrait_id="")
        result = config.validate()
        assert not result.is_valid

    def test_validate_missing_theme(self):
        config = self._valid_config(theme_id="")
        result = config.validate()
        assert not result.is_valid

    def test_validate_invalid_government_type(self):
        config = self._valid_config(government_type="NotARealType")
        result = config.validate()
        assert not result.is_valid

    def test_validate_invalid_homeworld_type(self):
        config = self._valid_config(homeworld_type="NOT_A_PLANET")
        result = config.validate()
        assert not result.is_valid

    def test_validate_aptitude_below_minimum(self):
        config = self._valid_config(aptitude_strength=0)
        result = config.validate()
        assert not result.is_valid

    def test_validate_aptitude_above_maximum(self):
        config = self._valid_config(aptitude_strength=101)
        result = config.validate()
        assert not result.is_valid

    def test_validate_description_too_long(self):
        config = self._valid_config(bio_description="x" * 501)
        result = config.validate()
        assert not result.is_valid

    def test_validate_negative_reproduction_rate(self):
        """PROJ-283 Phase 4: `base_reproduction_rate` must be non-negative."""
        config = self._valid_config(base_reproduction_rate=-0.01)
        result = config.validate()
        assert not result.is_valid

    def test_validate_happiness_out_of_range(self):
        """PROJ-283 Phase 4: `base_happiness` must be in [0, 1]."""
        config = self._valid_config(base_happiness=1.5)
        result = config.validate()
        assert not result.is_valid

    def test_is_complete(self):
        assert self._valid_config().is_complete()
        assert not self._valid_config(name="").is_complete()


# ---------------------------------------------------------------------------
# Constant lists (post-Phase 4 shapes)
# ---------------------------------------------------------------------------


class TestRaceConfigConstantLists:
    def test_government_types(self):
        from game.strategy.data.race_config import GOVERNMENT_TYPES
        assert len(GOVERNMENT_TYPES) == 14
        assert "Empire" in GOVERNMENT_TYPES

    def test_government_organizations(self):
        from game.strategy.data.race_config import GOVERNMENT_ORGANIZATIONS
        assert len(GOVERNMENT_ORGANIZATIONS) == 13

    def test_leader_titles(self):
        from game.strategy.data.race_config import LEADER_TITLES
        assert len(LEADER_TITLES) == 27

    def test_physical_types(self):
        from game.strategy.data.race_config import PHYSICAL_TYPES
        assert len(PHYSICAL_TYPES) == 14

    def test_society_types(self):
        from game.strategy.data.race_config import SOCIETY_TYPES
        assert len(SOCIETY_TYPES) == 17

    def test_aptitude_names_after_phase4_drop(self):
        """PROJ-283 Phase 4: APTITUDE_NAMES shrunk from 9 to 7 entries
        (`happiness` and `population_growth` are now `base_happiness` and
        `base_reproduction_rate` floats on RaceConfig)."""
        from game.strategy.data.race_config import APTITUDE_NAMES
        assert len(APTITUDE_NAMES) == 7
        assert "happiness" not in APTITUDE_NAMES
        assert "population_growth" not in APTITUDE_NAMES
        for name in (
            "strength", "intelligence", "constitution", "dexterity",
            "tolerance_other_species", "cooperation", "conflict_tolerance",
        ):
            assert name in APTITUDE_NAMES


# ---------------------------------------------------------------------------
# Identity fields
# ---------------------------------------------------------------------------


class TestRaceConfigIdentityFields:
    def test_identity_fields_default_empty(self):
        config = RaceConfig()
        for field in (
            "faction_name", "race_name", "race_name_plural",
            "government_type", "government_organization",
            "leader_title", "leader_name", "physical_type", "society_type",
        ):
            assert getattr(config, field) == ""

    def test_identity_fields_set_correctly(self):
        config = RaceConfig(
            faction_name="Rossarian Empire",
            race_name="Rossarian",
            race_name_plural="Rossarians",
            government_type="Empire",
            government_organization="Autocracy",
            leader_title="Emperor",
            leader_name="Zara IV",
            physical_type="Felinoid",
            society_type="Conquerors",
        )
        assert config.faction_name == "Rossarian Empire"
        assert config.race_name == "Rossarian"
        assert config.leader_name == "Zara IV"
        assert config.physical_type == "Felinoid"

    def test_leader_name_round_trip(self):
        config = RaceConfig(leader_title="Emperor", leader_name="Zara IV")
        restored = RaceConfig.from_dict(config.to_dict())
        assert restored.leader_name == "Zara IV"

    def test_homeworld_type_round_trip(self):
        config = RaceConfig(homeworld_type="CONTINENTAL")
        restored = RaceConfig.from_dict(config.to_dict())
        assert restored.homeworld_type == "CONTINENTAL"


# ---------------------------------------------------------------------------
# Aptitude fields (post-Phase 4: 7 paid)
# ---------------------------------------------------------------------------


class TestRaceConfigAptitudeFields:
    def test_default_aptitudes_are_50(self):
        config = RaceConfig()
        for name in (
            "strength", "intelligence", "constitution", "dexterity",
            "tolerance_other_species", "cooperation", "conflict_tolerance",
        ):
            assert getattr(config, f"aptitude_{name}") == 50

    def test_create_race_with_custom_aptitudes(self):
        config = RaceConfig(
            aptitude_strength=80,
            aptitude_intelligence=30,
            aptitude_constitution=70,
            aptitude_conflict_tolerance=10,
        )
        assert config.aptitude_strength == 80
        assert config.aptitude_intelligence == 30
        assert config.aptitude_constitution == 70
        assert config.aptitude_conflict_tolerance == 10


# ---------------------------------------------------------------------------
# PROJ-283 Phase 1 — preferences field
# ---------------------------------------------------------------------------


class TestRaceConfigPreferencesField:
    """`preferences: Dict[str, EnvironmentalPreference]` is populated from
    `FACTOR_REGISTRY` defaults via __post_init__."""

    def test_default_preferences_populated_from_registry(self):
        from game.strategy.data.habitability_factors import FACTOR_REGISTRY
        from game.strategy.data.environmental_preference import EnvironmentalPreference

        config = RaceConfig()
        assert len(config.preferences) == len(FACTOR_REGISTRY)
        for factor_id in FACTOR_REGISTRY:
            assert factor_id in config.preferences
            assert isinstance(config.preferences[factor_id], EnvironmentalPreference)

    def test_default_preferences_match_factor_defaults(self):
        from game.strategy.data.habitability_factors import FACTOR_REGISTRY

        config = RaceConfig()
        for factor_id, factor in FACTOR_REGISTRY.items():
            pref = config.preferences[factor_id]
            assert pref.setpoint == factor.default_setpoint
            assert pref.tolerance == factor.default_tolerance

    def test_explicit_preferences_are_preserved(self):
        from game.strategy.data.environmental_preference import EnvironmentalPreference

        custom_gravity = EnvironmentalPreference(
            setpoint=5.0, tolerance=1.0, min_value=0.1, max_value=30.0, step=0.98,
        )
        config = RaceConfig(preferences={"gravity": custom_gravity})
        assert config.preferences["gravity"] is custom_gravity
        # Other factors still filled from registry defaults.
        assert "gas.O2" in config.preferences

    def test_preferences_round_trip(self):
        from game.strategy.data.environmental_preference import EnvironmentalPreference

        original = RaceConfig()
        original.preferences["temperature"] = EnvironmentalPreference(
            setpoint=250.0, tolerance=5.0, min_value=50.0, max_value=2000.0, step=10.0,
        )
        restored = RaceConfig.from_dict(original.to_dict())
        assert restored.preferences["temperature"].setpoint == 250.0
        assert restored.preferences["temperature"].tolerance == 5.0

    def test_from_dict_accepts_partial_preferences(self):
        """Loading an old save with only a few preference keys must not
        crash — missing keys are filled from registry defaults."""
        from game.strategy.data.habitability_factors import FACTOR_REGISTRY

        partial = {
            "name": "Partial",
            "preferences": {
                "gravity": {
                    "setpoint": 11.0, "tolerance": 1.0,
                    "min_value": 0.1, "max_value": 30.0, "step": 0.98,
                },
            },
        }
        config = RaceConfig.from_dict(partial)
        # Explicit gravity preserved
        assert config.preferences["gravity"].setpoint == 11.0
        # Missing factors backfilled
        assert len(config.preferences) == len(FACTOR_REGISTRY)


class TestRaceConfigBaseReproductionAndHappiness:
    """`base_reproduction_rate` and `base_happiness` replace the deleted
    `aptitude_population_growth` / `aptitude_happiness` fields."""

    def test_default_base_reproduction_rate(self):
        assert RaceConfig().base_reproduction_rate == 0.03

    def test_default_base_happiness(self):
        assert RaceConfig().base_happiness == 0.5

    def test_round_trip_preserves_values(self):
        original = RaceConfig(base_reproduction_rate=0.05, base_happiness=0.8)
        restored = RaceConfig.from_dict(original.to_dict())
        assert restored.base_reproduction_rate == 0.05
        assert restored.base_happiness == 0.8

    def test_from_dict_backward_compat(self):
        """Old race JSON without the new keys → defaults."""
        config = RaceConfig.from_dict({"name": "Old Race"})
        assert config.base_reproduction_rate == 0.03
        assert config.base_happiness == 0.5


class TestRaceConfigValidateWithPreferences:
    """`validate()` delegates per-preference; `EnvironmentalPreference`
    self-validates at construction so a bad pref simply can't enter the
    map without raising first."""

    def test_invalid_preference_construction_rejected(self):
        from game.core.exceptions import ValidationException
        from game.strategy.data.environmental_preference import EnvironmentalPreference

        with pytest.raises(ValidationException):
            EnvironmentalPreference(
                setpoint=100.0, tolerance=1.0,
                min_value=0.0, max_value=10.0, step=1.0,  # setpoint outside bounds
            )
