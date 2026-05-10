"""Round-trip tests for RaceConfig and Empire (PROJ-223 Phase 2+3)."""

import pytest

from game.strategy.data.race_config import RaceConfig
from game.strategy.data.empire import Empire
from tests.fixtures.strategy_entities import create_test_race_config, create_test_empire
from tests.integration.save_load.conftest import assert_round_trip_fidelity, assert_field_preserved


class TestRaceConfigRoundTrip:
    """RaceConfig round-trip serialization tests."""

    def test_to_dict_includes_all_fields(self):
        """PROJ-283 Phase 4: legacy `gravity_ideal`/`atmosphere_preferences`/etc.
        keys deleted; the new schema uses `preferences`, `base_reproduction_rate`,
        `base_happiness`."""
        rc = create_test_race_config()
        d = rc.to_dict()
        # Identity fields
        assert d['race_id'] == rc.race_id
        assert d['name'] == rc.name
        assert d['faction_name'] == rc.faction_name
        assert d['race_name'] == rc.race_name
        # Visual
        assert 'flag_id' in d
        assert 'portrait_id' in d
        # Environment (registry-driven)
        assert 'preferences' in d
        assert 'base_reproduction_rate' in d
        assert 'base_happiness' in d
        # Preferences should round-trip per-factor
        assert 'gravity' in d['preferences']
        assert 'temperature' in d['preferences']
        assert 'water' in d['preferences']
        assert 'gas.O2' in d['preferences']
        # Aptitudes
        assert 'aptitude_strength' in d
        assert 'aptitude_intelligence' in d
        # Descriptions
        assert 'bio_description' in d
        assert 'socio_description' in d

    def test_from_dict_restores_all_fields(self):
        original = create_test_race_config()
        d = original.to_dict()
        restored = RaceConfig.from_dict(d)
        assert restored.race_id == original.race_id
        assert restored.name == original.name
        assert restored.faction_name == original.faction_name
        assert restored.preferences["gravity"].setpoint == original.preferences["gravity"].setpoint
        assert restored.aptitude_strength == original.aptitude_strength

    def test_round_trip_field_level(self):
        assert_round_trip_fidelity(create_test_race_config(), RaceConfig)

    def test_preferences_round_trip(self):
        """PROJ-283 Phase 4: `preferences` dict (formerly `atmosphere_preferences`
        + scalar `_ideal`/`_tolerance` fields) survives round-trip."""
        rc = create_test_race_config()
        d = rc.to_dict()
        restored = RaceConfig.from_dict(d)
        assert set(restored.preferences.keys()) == set(rc.preferences.keys())
        for fid in rc.preferences:
            assert restored.preferences[fid].setpoint == rc.preferences[fid].setpoint
            assert restored.preferences[fid].tolerance == rc.preferences[fid].tolerance

    def test_optional_field_defaults(self):
        """Optional fields default correctly when not in dict.

        PROJ-283 Phase 4: legacy `gravity_ideal` default check replaced by
        the registry-default for `preferences["gravity"]` (9.81 m/s²)."""
        minimal = {
            'race_id': 'minimal',
            'name': 'Minimal Race',
        }
        restored = RaceConfig.from_dict(minimal)
        assert restored.race_id == 'minimal'
        assert restored.preferences["gravity"].setpoint == 9.81  # registry default
        assert restored.aptitude_strength == 50  # default
        assert restored.base_reproduction_rate == 0.03  # default


# =============================================================================
# Phase 3: Empire compound round-trip tests
# =============================================================================

class TestEmpireRoundTrip:
    """Empire compound round-trip serialization tests.

    Colony resolution (requires galaxy) is tested in Phase 4.
    """

    def test_core_fields(self):
        e = create_test_empire(empire_id=3, name="Federation", color=(0, 100, 255))
        d = e.to_dict()
        restored = Empire.from_dict(d)
        assert restored.id == 3
        assert restored.name == "Federation"
        assert restored.color == (0, 100, 255)

    def test_theme_fields(self):
        e = create_test_empire(empire_theme_id="Klingons")
        d = e.to_dict()
        restored = Empire.from_dict(d)
        assert restored.empire_theme_id == "Klingons"

    def test_nested_fleets(self):
        e = create_test_empire(num_fleets=2)
        d = e.to_dict()
        restored = Empire.from_dict(d)
        assert len(restored.fleets) == 2
        for orig, rest in zip(e.fleets, restored.fleets):
            assert rest.id == orig.id
            assert len(rest.ships) == len(orig.ships)

    def test_colony_ids_serialized(self):
        """colony_ids are serialized as a list of ints (not Planet objects)."""
        e = create_test_empire()
        # Manually set colony_ids for testing (normally from add_colony)
        from tests.fixtures.strategy_entities import create_test_planet
        planet = create_test_planet(id=7, owner_id=e.id)
        e.colonies.append(planet)
        d = e.to_dict()
        assert d['colony_ids'] == [7]

    def test_built_ship_designs_sorted(self):
        e = create_test_empire()
        e.built_ship_designs = {"frigate", "escort", "dreadnought"}
        d = e.to_dict()
        assert d['built_ship_designs'] == ["dreadnought", "escort", "frigate"]
        restored = Empire.from_dict(d)
        assert restored.built_ship_designs == {"frigate", "escort", "dreadnought"}

    def test_next_fleet_display_number_preserved(self):
        e = create_test_empire()
        e._next_fleet_display_number = 42
        d = e.to_dict()
        restored = Empire.from_dict(d)
        assert restored._next_fleet_display_number == 42

    def test_design_serial_counters_preserved(self):
        e = create_test_empire()
        e._design_serial_counters = {"escort": 5, "frigate": 3}
        d = e.to_dict()
        restored = Empire.from_dict(d)
        assert restored._design_serial_counters == {"escort": 5, "frigate": 3}

    def test_resource_economy_fields(self):
        e = create_test_empire(
            resource_pool={"fuel": 500.0, "minerals": 300.0},
            max_storage={"fuel": 1000.0, "minerals": 1000.0},
        )
        d = e.to_dict()
        restored = Empire.from_dict(d)
        assert restored.resource_pool == {"fuel": 500.0, "minerals": 300.0}
        assert restored.max_storage == {"fuel": 1000.0, "minerals": 1000.0}

    def test_optional_flag_and_portrait(self):
        e = create_test_empire(flag_id="flag_test", portrait_id="portrait_test")
        d = e.to_dict()
        restored = Empire.from_dict(d)
        assert_field_preserved(e, restored, 'flag_id')
        assert_field_preserved(e, restored, 'portrait_id')

    def test_race_config_nested(self):
        rc = create_test_race_config(race_id="custom_race")
        e = create_test_empire(race_config=rc)
        d = e.to_dict()
        restored = Empire.from_dict(d)
        assert restored.race_config is not None
        assert restored.race_config.race_id == "custom_race"

    def test_registries_passed_to_fleets(self, fresh_registries):
        e = create_test_empire(num_fleets=1)
        d = e.to_dict()
        restored = Empire.from_dict(d, registries=fresh_registries)
        assert len(restored.fleets) == 1
        for ship in restored.fleets[0].ships:
            assert ship._registries is not None
