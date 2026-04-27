"""Integration tests for storm generation in galaxy creation (PROJ-189 Phase 8).

Tests verify that:
- Storms are generated in star systems during galaxy creation
- Storm counts match blueprint constraints
- Storm hexes don't overlap star hexes
- Storms are properly registered as zones
- Storm serialization round-trips correctly
"""

import pytest
import random
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.storm import Storm


class TestGalaxyGenerationStorms:
    """Integration tests for storm generation during galaxy creation."""

    def test_galaxy_generation_creates_storms_in_some_systems(self):
        """Generate full galaxy and verify storms exist in at least some systems."""
        random.seed(42)  # Deterministic
        galaxy = Galaxy(radius=1000)
        galaxy.generate_systems(count=20, min_dist=50)

        # Count systems with storms
        systems_with_storms = sum(
            1 for sys in galaxy.systems.values() if sys.storms
        )

        # With 20 systems, at least some should have storms
        # Based on blueprints: most have 0-2 storms, some have 1-3
        assert systems_with_storms > 0, "No systems have storms"

        # At least 25% should have storms (conservative estimate)
        assert systems_with_storms >= 5, (
            f"Too few systems with storms: {systems_with_storms}/20"
        )

    def test_storm_counts_match_blueprint_constraints(self):
        """Verify storm counts per system are within blueprint min/max."""
        random.seed(123)
        galaxy = Galaxy(radius=800)
        galaxy.generate_systems(count=15, min_dist=40)

        for system in galaxy.systems.values():
            storm_count = len(system.storms)
            # Max from any blueprint is 3 (red_dwarf_pack, empty_warp_hub)
            # Min is always 0
            assert 0 <= storm_count <= 3, (
                f"System '{system.name}' has {storm_count} storms, expected 0-3"
            )

    def test_storm_hexes_do_not_overlap_star_hexes(self):
        """Verify no storm hexes overlap with star occupied hexes."""
        random.seed(456)
        galaxy = Galaxy(radius=800)
        galaxy.generate_systems(count=15, min_dist=40)

        for system in galaxy.systems.values():
            if not system.storms:
                continue

            # Collect all star hexes
            star_hexes = set()
            for star in system.stars:
                star_hexes.update(star.occupied_hexes)

            # Check all storm hexes
            for storm in system.storms:
                storm_hexes = storm.occupied_hexes
                overlap = star_hexes & storm_hexes
                assert not overlap, (
                    f"System '{system.name}': storm '{storm.name}' overlaps "
                    f"star hexes at {overlap}"
                )

    def test_storms_registered_as_zones_queryable(self):
        """Verify storms are registered and queryable via get_zones_at_global_hex."""
        random.seed(789)
        galaxy = Galaxy(radius=800)
        galaxy.generate_systems(count=10, min_dist=40)

        # Find a system with storms
        system_with_storms = None
        for system in galaxy.systems.values():
            if system.storms:
                system_with_storms = system
                break

        if system_with_storms is None:
            pytest.skip("No systems with storms generated (rare)")

        # Pick a storm and check its hexes are queryable
        storm = system_with_storms.storms[0]

        # Convert local hex to global
        for local_hex in storm.occupied_hexes:
            global_hex = system_with_storms.global_location + local_hex
            zones = galaxy.get_zones_at_global_hex(global_hex)

            assert storm in zones, (
                f"Storm '{storm.name}' not found at global hex {global_hex}"
            )

    def test_storm_serialization_roundtrip_full_galaxy(self):
        """Verify storm serialization/deserialization round-trips for full galaxy."""
        random.seed(101112)
        galaxy = Galaxy(radius=500)
        galaxy.generate_systems(count=8, min_dist=30)

        # Collect original storm data
        # PROJ-300 Phase 7: Storm.effects/StormEffect were eradicated; the
        # abilities-dict shape is now the single source of truth.
        original_storms = {}
        for system in galaxy.systems.values():
            if system.storms:
                original_storms[system.name] = [
                    (s.name, s.storm_type, s.location, s.hex_offsets,
                     dict(s.abilities), s.image_variant, s.intensity)
                    for s in system.storms
                ]

        # Serialize to dict
        galaxy_dict = galaxy.to_dict()

        # Verify storms are in serialized data
        # Galaxy.to_dict() format: [{'coord': {...}, 'system': {...}}, ...]
        for entry in galaxy_dict.get('systems', []):
            system_data = entry['system']
            if system_data['name'] in original_storms:
                assert 'storms' in system_data
                assert len(system_data['storms']) == len(original_storms[system_data['name']])

        # Deserialize
        restored_galaxy = Galaxy.from_dict(galaxy_dict)

        # Verify storms are restored correctly
        for system_name, original_storm_list in original_storms.items():
            restored_system = restored_galaxy.get_system_by_name(system_name)
            assert restored_system is not None
            assert len(restored_system.storms) == len(original_storm_list)

            for i, (name, stype, loc, offsets, abilities, variant, intensity) in enumerate(original_storm_list):
                restored = restored_system.storms[i]
                assert restored.name == name
                assert restored.storm_type == stype
                assert restored.location == loc
                assert restored.hex_offsets == offsets
                assert dict(restored.abilities) == abilities
                assert restored.image_variant == variant
                assert restored.intensity == intensity

    def test_storm_attributes_are_valid(self):
        """Verify all generated storms have valid attribute values."""
        random.seed(131415)
        galaxy = Galaxy(radius=600)
        galaxy.generate_systems(count=12, min_dist=35)

        valid_storm_types = {
            'ion_storm', 'plasma_storm', 'gravitational_anomaly',
            'radiation_belt', 'dark_nebula'
        }

        for system in galaxy.systems.values():
            for storm in system.storms:
                # Name should be non-empty
                assert storm.name, f"Storm has empty name in {system.name}"

                # Type should be valid
                assert storm.storm_type in valid_storm_types, (
                    f"Invalid storm type '{storm.storm_type}' in {system.name}"
                )

                # Should have at least 1 hex (the center)
                assert len(storm.hex_offsets) >= 1, (
                    f"Storm '{storm.name}' has no hexes"
                )

                # Image variant should be 1-6
                assert 1 <= storm.image_variant <= 6, (
                    f"Invalid image_variant {storm.image_variant} for '{storm.name}'"
                )

                # Intensity should be 0-1
                assert 0.0 <= storm.intensity <= 1.0, (
                    f"Invalid intensity {storm.intensity} for '{storm.name}'"
                )

                # PROJ-300 v2.0 — abilities dict, not StormEffect dataclass.
                # Each ability entry: multipliers in [0.0, 1.0], rates >= 0.
                for ability_name, entry in storm.abilities.items():
                    if not isinstance(entry, dict):
                        continue
                    if 'multiplier' in entry:
                        assert 0.0 <= entry['multiplier'] <= 1.0, (
                            f"Storm '{storm.name}' {ability_name} multiplier "
                            f"{entry['multiplier']} out of [0.0, 1.0]"
                        )
                    if 'rate' in entry:
                        assert entry['rate'] >= 0.0, (
                            f"Storm '{storm.name}' {ability_name} rate "
                            f"{entry['rate']} is negative"
                        )
