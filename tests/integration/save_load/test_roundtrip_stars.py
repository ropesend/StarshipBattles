"""Round-trip tests for Spectrum and Star serialization (PROJ-223 Phase 2)."""

import json
import pytest

from game.strategy.data.spectrum import Spectrum
from game.strategy.data.stars import Star, StarType
from game.core.hex_math import HexCoord
from tests.fixtures.strategy_entities import create_test_spectrum, create_test_star
from tests.integration.save_load.conftest import assert_round_trip_fidelity, assert_field_preserved


class TestSpectrumRoundTrip:
    """Spectrum round-trip serialization tests."""

    def test_to_dict_includes_all_9_bands(self):
        s = create_test_spectrum()
        d = s.to_dict()
        bands = ['gamma_ray', 'xray', 'ultraviolet', 'blue', 'green',
                 'red', 'infrared', 'microwave', 'radio']
        for band in bands:
            assert band in d, f"Missing band: {band}"
            assert isinstance(d[band], float)

    def test_from_dict_restores_all_9_bands(self):
        original = create_test_spectrum()
        d = original.to_dict()
        restored = Spectrum.from_dict(d)
        assert restored.gamma_ray == original.gamma_ray
        assert restored.xray == original.xray
        assert restored.ultraviolet == original.ultraviolet
        assert restored.blue == original.blue
        assert restored.green == original.green
        assert restored.red == original.red
        assert restored.infrared == original.infrared
        assert restored.microwave == original.microwave
        assert restored.radio == original.radio

    def test_round_trip_field_level(self):
        assert_round_trip_fidelity(create_test_spectrum(), Spectrum)

    def test_float_precision_extreme_values(self):
        """Spectrum values range from 1e-47 to 1e-7."""
        s = create_test_spectrum(
            gamma_ray=1.5e-47,
            radio=1.2e-18,
            blue=4.2e-7,
        )
        restored = assert_round_trip_fidelity(s, Spectrum)
        assert_field_preserved(s, restored, 'gamma_ray')
        assert_field_preserved(s, restored, 'radio')
        assert_field_preserved(s, restored, 'blue')

    def test_json_serializable(self):
        d = create_test_spectrum().to_dict()
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        restored = Spectrum.from_dict(parsed)
        assert restored == create_test_spectrum()


class TestStarRoundTrip:
    """Star round-trip serialization tests."""

    def test_to_dict_includes_all_fields(self):
        s = create_test_star()
        d = s.to_dict()
        expected_keys = ['name', 'mass', 'radius_hexes', 'temperature',
                         'luminosity', 'spectrum', 'star_type', 'color', 'age', 'location']
        for key in expected_keys:
            assert key in d, f"Missing key: {key}"

    def test_from_dict_restores_all_fields(self):
        original = create_test_star()
        d = original.to_dict()
        restored = Star.from_dict(d)
        assert restored.name == original.name
        assert restored.mass == original.mass
        assert restored.radius_hexes == original.radius_hexes
        assert restored.temperature == original.temperature
        assert restored.luminosity == original.luminosity
        assert restored.star_type == original.star_type
        assert restored.age == original.age

    def test_round_trip_float_tolerance(self):
        s = create_test_star(mass=1.0, temperature=5778.0, luminosity=1.0, age=4.6e9)
        restored = assert_round_trip_fidelity(s, Star)
        assert_field_preserved(s, restored, 'mass')
        assert_field_preserved(s, restored, 'temperature')

    def test_color_tuple_list_conversion(self):
        """Color is stored as tuple, serialized as list, restored as tuple."""
        s = create_test_star(color=(255, 220, 180))
        d = s.to_dict()
        assert isinstance(d['color'], list)
        restored = Star.from_dict(d)
        assert restored.color == (255, 220, 180)

    def test_hex_coord_location_round_trip(self):
        s = create_test_star(location=HexCoord(3, -2))
        d = s.to_dict()
        restored = Star.from_dict(d)
        assert restored.location == HexCoord(3, -2)

    def test_star_type_enum_round_trip(self):
        for st in StarType:
            s = create_test_star(star_type=st)
            d = s.to_dict()
            restored = Star.from_dict(d)
            assert restored.star_type == st

    def test_spectrum_nested_round_trip(self):
        """Spectrum within Star survives round-trip."""
        s = create_test_star()
        d = s.to_dict()
        restored = Star.from_dict(d)
        assert restored.spectrum == s.spectrum
