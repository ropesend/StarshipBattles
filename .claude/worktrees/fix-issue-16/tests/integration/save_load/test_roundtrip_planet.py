"""Round-trip tests for SpeciesPopulation, PlanetaryFacility, and Planet (PROJ-223 Phase 2+3)."""

import pytest

from game.strategy.data.species_population import SpeciesPopulation
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.data.planet import Planet, PlanetType
from game.core.hex_math import HexCoord
from tests.fixtures.strategy_entities import (
    create_test_species_population,
    create_test_facility,
    create_test_planet,
)
from tests.integration.save_load.conftest import assert_round_trip_fidelity, assert_field_preserved


class TestSpeciesPopulationRoundTrip:
    """SpeciesPopulation round-trip serialization tests."""

    def test_to_dict_includes_all_fields(self):
        """SpeciesPopulation is a dataclass — uses asdict or manual dict."""
        p = create_test_species_population()
        # SpeciesPopulation doesn't have to_dict, but from_dict expects a dict
        d = {'race_id': p.race_id, 'count': p.count, 'happiness': p.happiness}
        restored = SpeciesPopulation.from_dict(d)
        assert restored.race_id == p.race_id
        assert restored.count == p.count
        assert restored.happiness == p.happiness

    def test_from_dict_restores_all_fields(self):
        d = {'race_id': 'humans', 'count': 5000, 'happiness': 0.85}
        restored = SpeciesPopulation.from_dict(d)
        assert restored.race_id == 'humans'
        assert restored.count == 5000
        assert restored.happiness == 0.85

    def test_happiness_defaults_to_0_5_when_missing(self):
        d = {'race_id': 'test', 'count': 100}
        restored = SpeciesPopulation.from_dict(d)
        assert restored.happiness == 0.5

    def test_round_trip_preserves_all_fields(self):
        original = create_test_species_population(race_id="xenos", count=2500, happiness=0.9)
        d = {'race_id': original.race_id, 'count': original.count, 'happiness': original.happiness}
        restored = SpeciesPopulation.from_dict(d)
        assert_field_preserved(original, restored, 'race_id')
        assert_field_preserved(original, restored, 'count')
        assert_field_preserved(original, restored, 'happiness')


class TestPlanetaryFacilityRoundTrip:
    """PlanetaryFacility round-trip serialization tests."""

    def _to_dict(self, f: PlanetaryFacility) -> dict:
        """Manual to_dict since PlanetaryFacility only has from_dict."""
        return {
            'instance_id': f.instance_id,
            'design_id': f.design_id,
            'name': f.name,
            'design_data': f.design_data,
            'is_operational': f.is_operational,
            'construction_queue': f.construction_queue,
            'consumable_levels': f.consumable_levels,
        }

    def test_to_dict_includes_all_7_fields(self):
        f = create_test_facility()
        d = self._to_dict(f)
        expected = ['instance_id', 'design_id', 'name', 'design_data',
                    'is_operational', 'construction_queue', 'consumable_levels']
        for key in expected:
            assert key in d, f"Missing key: {key}"

    def test_from_dict_restores_all_fields(self):
        original = create_test_facility()
        d = self._to_dict(original)
        restored = PlanetaryFacility.from_dict(d)
        assert restored.instance_id == original.instance_id
        assert restored.design_id == original.design_id
        assert restored.name == original.name
        assert restored.design_data == original.design_data
        assert restored.is_operational == original.is_operational
        assert restored.construction_queue == original.construction_queue

    def test_consumable_levels_with_values(self):
        f = create_test_facility(consumable_levels={"fuel": 50.0, "energy": 100.0})
        d = self._to_dict(f)
        restored = PlanetaryFacility.from_dict(d)
        assert restored.consumable_levels == {"fuel": 50.0, "energy": 100.0}

    def test_empty_consumable_levels(self):
        f = create_test_facility(consumable_levels={})
        d = self._to_dict(f)
        restored = PlanetaryFacility.from_dict(d)
        assert restored.consumable_levels == {}

    def test_round_trip_preserves_design_data(self):
        """Complex nested design_data dict survives round-trip."""
        f = create_test_facility()
        d = self._to_dict(f)
        restored = PlanetaryFacility.from_dict(d)
        assert restored.design_data == f.design_data


# =============================================================================
# Phase 3: Planet compound round-trip tests
# =============================================================================

class TestPlanetRoundTrip:
    """Planet compound round-trip serialization tests."""

    def test_all_physics_fields_preserved(self):
        p = create_test_planet(has_facilities=False, has_population=False)
        restored = assert_round_trip_fidelity(p, Planet)
        assert_field_preserved(p, restored, 'mass')
        assert_field_preserved(p, restored, 'radius')
        assert_field_preserved(p, restored, 'surface_area')
        assert_field_preserved(p, restored, 'density')
        assert_field_preserved(p, restored, 'surface_gravity')
        assert_field_preserved(p, restored, 'surface_pressure')
        assert_field_preserved(p, restored, 'surface_temperature')
        assert_field_preserved(p, restored, 'surface_water')
        assert_field_preserved(p, restored, 'tectonic_activity')
        assert_field_preserved(p, restored, 'magnetic_field')

    def test_nested_facilities_round_trip(self):
        p = create_test_planet(has_facilities=True)
        restored = assert_round_trip_fidelity(p, Planet)
        assert len(restored.facilities) == len(p.facilities)
        assert restored.facilities[0].instance_id == p.facilities[0].instance_id
        assert restored.facilities[0].design_data == p.facilities[0].design_data

    def test_nested_populations_round_trip(self):
        p = create_test_planet(has_population=True)
        restored = assert_round_trip_fidelity(p, Planet)
        assert len(restored.populations) == len(p.populations)
        assert restored.populations[0].race_id == p.populations[0].race_id
        assert restored.populations[0].count == p.populations[0].count

    def test_resources_dict_round_trip(self):
        p = create_test_planet(deposits={"minerals": {"amount": 500, "quality": 0.8}})
        restored = assert_round_trip_fidelity(p, Planet)
        assert restored.deposits == p.deposits

    def test_atmosphere_dict_round_trip(self):
        p = create_test_planet(atmosphere={"nitrogen": 0.78, "oxygen": 0.21})
        restored = assert_round_trip_fidelity(p, Planet)
        assert restored.atmosphere == p.atmosphere

    def test_owner_id_null_and_non_null(self):
        p_owned = create_test_planet(owner_id=2)
        restored_owned = assert_round_trip_fidelity(p_owned, Planet)
        assert restored_owned.owner_id == 2

        p_unowned = create_test_planet(owner_id=None)
        restored_unowned = assert_round_trip_fidelity(p_unowned, Planet)
        assert restored_unowned.owner_id is None

    def test_visual_fields(self):
        p = create_test_planet(image_id="planet_arid_02", image_rotation=123.5, radius_hexes=2)
        restored = assert_round_trip_fidelity(p, Planet)
        assert_field_preserved(p, restored, 'image_id')
        assert_field_preserved(p, restored, 'image_rotation')
        assert_field_preserved(p, restored, 'radius_hexes')

    def test_planet_type_enum_round_trip(self):
        for pt in PlanetType:
            p = create_test_planet(planet_type=pt)
            restored = assert_round_trip_fidelity(p, Planet)
            assert restored.planet_type == pt

    def test_hex_coord_location_round_trip(self):
        p = create_test_planet(location=HexCoord(7, -3))
        restored = assert_round_trip_fidelity(p, Planet)
        assert restored.location == HexCoord(7, -3)

    def test_id_preserved(self):
        p = create_test_planet(id=42)
        restored = assert_round_trip_fidelity(p, Planet)
        assert restored.id == 42
