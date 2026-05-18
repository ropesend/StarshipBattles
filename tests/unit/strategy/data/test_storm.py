"""Unit tests for Storm entity (PROJ-189 Phase 1; PROJ-300 v2.0 abilities shape)."""

import pytest
from game.core.hex_math import HexCoord
from game.strategy.data.storm import Storm
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.star_system import StarSystem
from game.strategy.data.spectrum import Spectrum
from game.strategy.data.stars import Star, StarType


# StormEffect tests removed in PROJ-300 Phase 7 — the legacy dataclass was
# eradicated. Storm.abilities (Dict[str, Any]) replaces it; round-trip and
# generation tests below cover the new shape.


class TestStorm:
    """Tests for Storm dataclass."""

    def test_creation_with_default_effect(self):
        """Storm should allow creation with default StormEffect."""
        storm = Storm(
            name="Ion Storm Alpha",
            storm_type="ion_storm",
            location=HexCoord(5, -2),
            hex_offsets=frozenset({HexCoord(0, 0)}),
            abilities={},
            image_variant=1,
            intensity=0.8
        )
        assert storm.name == "Ion Storm Alpha"
        assert storm.storm_type == "ion_storm"
        assert storm.location == HexCoord(5, -2)
        assert storm.hex_offsets == frozenset({HexCoord(0, 0)})
        assert storm.abilities == {}
        assert storm.image_variant == 1
        assert storm.intensity == 0.8

    def test_occupied_hexes_single_hex(self):
        """Storm with only center offset occupies just the center hex."""
        storm = Storm(
            name="Small Storm",
            storm_type="plasma_storm",
            location=HexCoord(3, 4),
            hex_offsets=frozenset({HexCoord(0, 0)}),
            abilities={},
            image_variant=2,
            intensity=0.5
        )
        expected = frozenset({HexCoord(3, 4)})
        assert storm.occupied_hexes == expected

    def test_occupied_hexes_multi_hex(self):
        """Storm with multiple offsets computes occupied_hexes correctly."""
        # Storm at (10, 5) with center + 3 neighbors
        storm = Storm(
            name="Large Storm",
            storm_type="ion_storm",
            location=HexCoord(10, 5),
            hex_offsets=frozenset({
                HexCoord(0, 0),   # center
                HexCoord(1, 0),   # right
                HexCoord(0, 1),   # down-right
                HexCoord(-1, 1),  # down-left
            }),
            abilities={},
            image_variant=3,
            intensity=0.7
        )
        expected = frozenset({
            HexCoord(10, 5),   # center: (10+0, 5+0)
            HexCoord(11, 5),   # right: (10+1, 5+0)
            HexCoord(10, 6),   # down-right: (10+0, 5+1)
            HexCoord(9, 6),    # down-left: (10-1, 5+1)
        })
        assert storm.occupied_hexes == expected

    def test_to_dict(self):
        """Storm.to_dict should serialize all fields correctly (PROJ-300 v2.0)."""
        storm = Storm(
            name="Test Storm",
            storm_type="radiation_storm",
            description="A test storm",
            location=HexCoord(7, -3),
            hex_offsets=frozenset({HexCoord(0, 0), HexCoord(1, 0)}),
            abilities={
                "ShieldModifier": {"multiplier": 0.5, "scope": "sector"},
                "EnvironmentalDamage": {"rate": 5.0, "damage_type": "radiation", "scope": "sector"},
            },
            image_variant=4,
            intensity=0.6,
        )
        result = storm.to_dict()

        assert result['name'] == "Test Storm"
        assert result['storm_type'] == "radiation_storm"
        assert result['description'] == "A test storm"
        assert result['location'] == {'q': 7, 'r': -3}
        assert result['image_variant'] == 4
        assert result['intensity'] == 0.6
        assert result['abilities']['ShieldModifier']['multiplier'] == 0.5
        assert result['abilities']['EnvironmentalDamage']['rate'] == 5.0
        # No legacy 'effects' field in serialized output.
        assert 'effects' not in result
        # hex_offsets should be a list of dicts
        assert len(result['hex_offsets']) == 2
        offsets_as_tuples = {(d['q'], d['r']) for d in result['hex_offsets']}
        assert offsets_as_tuples == {(0, 0), (1, 0)}

    def test_from_dict(self):
        """Storm.from_dict deserializes the v2.0 abilities shape."""
        data = {
            'name': "Deserialized Storm",
            'storm_type': "plasma_storm",
            'description': "Plasma storm",
            'location': {'q': -5, 'r': 8},
            'hex_offsets': [{'q': 0, 'r': 0}, {'q': -1, 'r': 0}],
            'abilities': {
                'ShieldModifier': {'multiplier': 0.3, 'scope': 'sector'},
                'ThrustModifier': {'multiplier': 0.7, 'scope': 'sector'},
            },
            'image_variant': 5,
            'intensity': 0.9,
        }
        storm = Storm.from_dict(data)

        assert storm.name == "Deserialized Storm"
        assert storm.storm_type == "plasma_storm"
        assert storm.description == "Plasma storm"
        assert storm.location == HexCoord(-5, 8)
        assert storm.hex_offsets == frozenset({HexCoord(0, 0), HexCoord(-1, 0)})
        assert storm.abilities["ShieldModifier"]["multiplier"] == 0.3
        assert storm.abilities["ThrustModifier"]["multiplier"] == 0.7
        assert storm.image_variant == 5
        assert storm.intensity == 0.9

    def test_from_dict_with_missing_optional_fields(self):
        """Storm.from_dict uses defaults for missing optional fields."""
        data = {
            'name': "Minimal Storm",
            'storm_type': "ion_storm",
            'location': {'q': 0, 'r': 0},
            'hex_offsets': [{'q': 0, 'r': 0}],
        }
        storm = Storm.from_dict(data)

        assert storm.name == "Minimal Storm"
        assert storm.storm_type == "ion_storm"
        # PROJ-300: abilities defaults to empty dict.
        assert storm.abilities == {}
        assert storm.description == ''
        # image_variant and intensity should have defaults
        assert storm.image_variant == 1
        assert storm.intensity == 1.0

    def test_serialization_roundtrip(self):
        """Storm should serialize and deserialize identically (v2.0 shape)."""
        original = Storm(
            name="Roundtrip Storm",
            storm_type="radiation_storm",
            description="Round-trip test",
            location=HexCoord(-10, 15),
            hex_offsets=frozenset({
                HexCoord(0, 0),
                HexCoord(1, -1),
                HexCoord(0, -1),
                HexCoord(-1, 0),
            }),
            abilities={
                "ShieldModifier": {"multiplier": 0.4, "scope": "sector"},
                "ThrustModifier": {"multiplier": 0.6, "scope": "sector"},
                "StrategicSpeedModifier": {"multiplier": 0.8, "scope": "sector"},
                "EnvironmentalDamage": {"rate": 12.5, "damage_type": "radiation", "scope": "sector"},
                "FuelDrain": {"rate": 2.5, "scope": "sector"},
            },
            image_variant=6,
            intensity=0.75,
        )
        data = original.to_dict()
        restored = Storm.from_dict(data)

        assert restored.name == original.name
        assert restored.storm_type == original.storm_type
        assert restored.description == original.description
        assert restored.location == original.location
        assert restored.hex_offsets == original.hex_offsets
        assert restored.abilities == original.abilities
        assert restored.image_variant == original.image_variant
        assert restored.intensity == original.intensity

    def test_from_dict_invalid_location_raises(self):
        """Storm.from_dict should raise on invalid location format."""
        from game.core.exceptions import PersistenceException
        data = {
            'name': "Bad Storm",
            'storm_type': "ion_storm",
            'location': "not a dict",  # Invalid
            'hex_offsets': [{'q': 0, 'r': 0}],
        }
        with pytest.raises(PersistenceException):
            Storm.from_dict(data)

    def test_from_dict_missing_required_key_raises(self):
        """Storm.from_dict should raise on missing required keys."""
        from game.core.exceptions import PersistenceException
        data = {
            'name': "Missing Type Storm",
            # Missing 'storm_type'
            'location': {'q': 0, 'r': 0},
            'hex_offsets': [{'q': 0, 'r': 0}],
        }
        with pytest.raises(PersistenceException):
            Storm.from_dict(data)


class TestStarSystemStormIntegration:
    """Tests for Storm integration with StarSystem (Task 1.2)."""

    def test_star_system_has_storms_list(self):
        """StarSystem should have an empty storms list by default."""
        system = StarSystem(
            name="Test System",
            global_location=HexCoord(0, 0)
        )
        assert hasattr(system, 'storms')
        assert system.storms == []

    def test_star_system_with_storms_serializes(self):
        """StarSystem.to_dict should include storms."""
        system = StarSystem(
            name="Stormy System",
            global_location=HexCoord(5, 5)
        )
        storm = Storm(
            name="Ion Storm",
            storm_type="ion_storm",
            location=HexCoord(2, 3),
            hex_offsets=frozenset({HexCoord(0, 0)}),
            abilities={"ShieldModifier": {"multiplier": 0.5, "scope": "sector"}},
            image_variant=1,
            intensity=0.8,
        )
        system.storms.append(storm)

        data = system.to_dict()
        assert 'storms' in data
        assert len(data['storms']) == 1
        assert data['storms'][0]['name'] == "Ion Storm"
        assert data['storms'][0]['storm_type'] == "ion_storm"

    def test_star_system_with_storms_deserializes(self):
        """StarSystem.from_dict should restore storms (PROJ-300 v2.0)."""
        data = {
            'name': "Restored System",
            'global_location': {'q': 10, 'r': -5},
            'stars': [],
            'warp_points': [],
            'planets': [],
            'storms': [
                {
                    'name': "Plasma Storm",
                    'storm_type': "plasma_storm",
                    'location': {'q': 1, 'r': 2},
                    'hex_offsets': [{'q': 0, 'r': 0}, {'q': 1, 'r': 0}],
                    'abilities': {
                        'EnvironmentalDamage': {'rate': 5.0, 'damage_type': 'plasma', 'scope': 'sector'},
                    },
                    'image_variant': 3,
                    'intensity': 0.6,
                }
            ]
        }
        system = StarSystem.from_dict(data)

        assert len(system.storms) == 1
        storm = system.storms[0]
        assert storm.name == "Plasma Storm"
        assert storm.storm_type == "plasma_storm"
        assert storm.location == HexCoord(1, 2)
        assert storm.abilities['EnvironmentalDamage']['rate'] == 5.0
        assert storm.image_variant == 3
        assert storm.intensity == 0.6

    def test_star_system_serialization_roundtrip_with_storms(self):
        """StarSystem with storms should round-trip through serialization (v2.0)."""
        system = StarSystem(
            name="Roundtrip System",
            global_location=HexCoord(20, 20)
        )
        storm = Storm(
            name="Test Storm",
            storm_type="radiation_storm",
            location=HexCoord(-5, 3),
            hex_offsets=frozenset({HexCoord(0, 0), HexCoord(1, -1)}),
            abilities={
                "ShieldModifier": {"multiplier": 0.4, "scope": "sector"},
                "ThrustModifier": {"multiplier": 0.7, "scope": "sector"},
                "EnvironmentalDamage": {"rate": 10.0, "damage_type": "radiation", "scope": "sector"},
            },
            image_variant=5,
            intensity=0.9,
        )
        system.storms.append(storm)

        data = system.to_dict()
        restored = StarSystem.from_dict(data)

        assert len(restored.storms) == 1
        rs = restored.storms[0]
        assert rs.name == storm.name
        assert rs.storm_type == storm.storm_type
        assert rs.location == storm.location
        assert rs.hex_offsets == storm.hex_offsets
        assert rs.abilities == storm.abilities
        assert rs.image_variant == storm.image_variant
        assert rs.intensity == storm.intensity

    def test_star_system_from_dict_no_storms_key_backward_compat(self):
        """StarSystem.from_dict with no 'storms' key produces empty list."""
        # Simulating old save format without storms
        data = {
            'name': "Old System",
            'global_location': {'q': 0, 'r': 0},
            'stars': [],
            'warp_points': [],
            'planets': []
            # No 'storms' key
        }
        system = StarSystem.from_dict(data)
        assert system.storms == []

    def test_star_system_from_dict_raises_on_invalid_storm(self):
        """StarSystem.from_dict should raise PersistenceException for an
        invalid storm.

        PROJ-443 Phase 3a: this test originally asserted that malformed
        storms were silently skipped (``len(system.storms) == 2`` with the
        bad storm dropped). The production contract changed: see
        `star_system.py:149-152` — storms (along with warp_points and
        planets) now deserialize with ``strict=True``, so a corrupt entry
        fails loudly rather than being silently dropped. This is per the
        project's no-migration / disposable-save rule: save files should
        be well-formed; corruption is an error to surface, not a
        condition to paper over.
        """
        from game.core.exceptions import PersistenceException

        data = {
            'name': "Mixed System",
            'global_location': {'q': 0, 'r': 0},
            'storms': [
                {
                    'name': "Good Storm",
                    'storm_type': "ion_storm",
                    'location': {'q': 1, 'r': 1},
                    'hex_offsets': [{'q': 0, 'r': 0}],
                },
                {
                    'name': "Bad Storm",
                    # Missing storm_type - invalid
                    'location': {'q': 2, 'r': 2},
                    'hex_offsets': [{'q': 0, 'r': 0}],
                },
            ]
        }
        with pytest.raises(PersistenceException, match="storm at index 1"):
            StarSystem.from_dict(data)


class TestGalaxyStormZoneRegistration:
    """Tests for Galaxy zone registration of storms (Task 1.3)."""

    def _make_star(self, name: str = "TestStar") -> Star:
        """Helper to create a minimal star for testing."""
        return Star(
            name=name,
            mass=1.0,
            radius_hexes=1,
            temperature=5778,
            luminosity=1.0,
            spectrum=Spectrum(0, 0, 0, 0.3, 0.4, 0.3, 0, 0, 0),
            star_type=StarType.MAIN_SEQUENCE,
            color=(255, 255, 200),
            age=5e9,
            location=HexCoord(0, 0)
        )

    def test_galaxy_add_system_registers_storm_zones(self):
        """After adding a system with storms, zones should be registered."""
        galaxy = Galaxy(radius=50)

        system = StarSystem(
            name="Storm System",
            global_location=HexCoord(10, 10),
            stars=[self._make_star()]
        )
        # Storm at local (3, 2) with 2 hexes
        storm = Storm(
            name="Test Storm",
            storm_type="ion_storm",
            location=HexCoord(3, 2),
            hex_offsets=frozenset({HexCoord(0, 0), HexCoord(1, 0)}),
            abilities={},
            image_variant=1,
            intensity=0.8
        )
        system.storms.append(storm)

        galaxy.add_system(system)

        # Check zone registration at global hex: system(10,10) + local(3,2) = global(13,12)
        zones_at_center = galaxy.get_zones_at_global_hex(HexCoord(13, 12))
        assert storm in zones_at_center

        # Check offset hex: system(10,10) + local(4,2) = global(14,12)
        zones_at_offset = galaxy.get_zones_at_global_hex(HexCoord(14, 12))
        assert storm in zones_at_offset

    def test_storm_zones_coexist_with_star_zones(self):
        """Storm and star zones at the same hex should both be returned."""
        galaxy = Galaxy(radius=50)

        # Create star at center (0,0)
        star = self._make_star()
        system = StarSystem(
            name="Overlapping System",
            global_location=HexCoord(5, 5),
            stars=[star]
        )
        # Storm also at center (0,0) - overlaps with star
        storm = Storm(
            name="Overlapping Storm",
            storm_type="plasma_storm",
            location=HexCoord(0, 0),
            hex_offsets=frozenset({HexCoord(0, 0)}),
            abilities={},
            image_variant=2,
            intensity=0.5
        )
        system.storms.append(storm)

        galaxy.add_system(system)

        # Global (5, 5) should have both star and storm
        zones = galaxy.get_zones_at_global_hex(HexCoord(5, 5))
        assert star in zones
        assert storm in zones
        assert len(zones) == 2

    def test_storm_zones_registered_on_galaxy_from_dict(self):
        """Storms should be registered as zones when Galaxy is loaded from dict."""
        # Create a galaxy, add system with storm, serialize, deserialize
        galaxy = Galaxy(radius=50)
        system = StarSystem(
            name="Serialized System",
            global_location=HexCoord(20, 20),
            stars=[self._make_star()]
        )
        storm = Storm(
            name="Serialized Storm",
            storm_type="radiation_storm",
            location=HexCoord(5, 5),
            hex_offsets=frozenset({HexCoord(0, 0)}),
            abilities={"EnvironmentalDamage": {"rate": 10.0, "damage_type": "radiation", "scope": "sector"}},
            image_variant=4,
            intensity=0.7
        )
        system.storms.append(storm)
        galaxy.add_system(system)

        # Serialize and deserialize
        data = galaxy.to_dict()
        restored = Galaxy.from_dict(data)

        # Check zone registration at global hex: system(20,20) + local(5,5) = global(25,25)
        zones = restored.get_zones_at_global_hex(HexCoord(25, 25))

        # Find the storm in the zones (it's a new instance after deserialization)
        storm_zones = [z for z in zones if isinstance(z, Storm)]
        assert len(storm_zones) == 1
        assert storm_zones[0].name == "Serialized Storm"

    def test_multi_hex_storm_registers_all_hexes(self):
        """A storm with multiple hex_offsets should register all hexes."""
        galaxy = Galaxy(radius=50)

        system = StarSystem(
            name="Multi-Hex System",
            global_location=HexCoord(0, 0),
            stars=[self._make_star()]
        )
        # Storm with 4 hexes in an L-shape
        storm = Storm(
            name="Large Storm",
            storm_type="ion_storm",
            location=HexCoord(10, 10),
            hex_offsets=frozenset({
                HexCoord(0, 0),   # center
                HexCoord(1, 0),   # right
                HexCoord(2, 0),   # right-right
                HexCoord(0, 1),   # down
            }),
            abilities={},
            image_variant=3,
            intensity=0.6
        )
        system.storms.append(storm)
        galaxy.add_system(system)

        # All 4 hexes should have the storm registered
        expected_globals = [
            HexCoord(10, 10),  # center
            HexCoord(11, 10),  # right
            HexCoord(12, 10),  # right-right
            HexCoord(10, 11),  # down
        ]
        for global_hex in expected_globals:
            zones = galaxy.get_zones_at_global_hex(global_hex)
            assert storm in zones, f"Storm not found at {global_hex}"

        # A hex NOT in the storm should not have it
        zones_outside = galaxy.get_zones_at_global_hex(HexCoord(15, 15))
        assert storm not in zones_outside
