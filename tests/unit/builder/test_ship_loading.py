"""Tests for ship loading and expected_stats validation.

These tests ensure that ships loaded from JSON files have stats that match
the expected_stats saved by the ship builder, validating that modifier
stacking is working correctly in the simulator.
"""
import pytest
import os
import glob

from game.simulation.entities.ship import Ship
from game.simulation.components.component import create_component
from game.core.json_utils import load_json


class TestModifierStacking:
    """Test that modifier stacking calculates HP correctly."""

    def test_simple_size_mount_hp_multiplier(self, fresh_registries):
        """simple_size_mount should multiply HP by the scale value."""
        laser = create_component('laser_cannon', registries=fresh_registries)
        base_hp = laser.max_hp

        # Add 8x size mount
        laser.add_modifier('simple_size_mount', 8)
        laser.recalculate_stats()

        expected_hp = base_hp * 8
        assert laser.max_hp == expected_hp, \
            f"Size mount 8x: expected {expected_hp}, got {laser.max_hp}"

    def test_range_mount_hp_multiplier(self, fresh_registries):
        """range_mount should multiply HP by 3.5^level."""
        laser = create_component('laser_cannon', registries=fresh_registries)
        base_hp = laser.max_hp

        # Add range mount level 2
        laser.add_modifier('range_mount', 2)
        laser.recalculate_stats()

        expected_multiplier = 3.5 ** 2  # 12.25
        expected_hp = int(base_hp * expected_multiplier)
        assert laser.max_hp == expected_hp, \
            f"Range mount level 2: expected {expected_hp}, got {laser.max_hp}"

    def test_stacked_modifiers_multiplicative(self, fresh_registries):
        """Multiple modifiers should stack multiplicatively."""
        laser = create_component('laser_cannon', registries=fresh_registries)
        base_hp = laser.max_hp

        # Add both size_mount(8) and range_mount(2)
        laser.add_modifier('simple_size_mount', 8)
        laser.add_modifier('range_mount', 2)
        laser.recalculate_stats()

        # 8 * 3.5^2 = 8 * 12.25 = 98
        expected_multiplier = 8 * (3.5 ** 2)
        expected_hp = int(base_hp * expected_multiplier)
        assert laser.max_hp == expected_hp, \
            f"Stacked modifiers: expected {expected_hp}, got {laser.max_hp}"

    def test_turret_mount_no_hp_change(self, fresh_registries):
        """turret_mount should not affect HP (only mass)."""
        laser = create_component('laser_cannon', registries=fresh_registries)
        base_hp = laser.max_hp
        base_mass = laser.mass

        laser.add_modifier('turret_mount', 180)
        laser.recalculate_stats()

        assert laser.max_hp == base_hp, \
            f"Turret mount should not change HP: expected {base_hp}, got {laser.max_hp}"
        assert laser.mass > base_mass, \
            "Turret mount should increase mass"


class TestAllShipDesigns:
    """Test all ship designs in the ships/ folder."""

    def test_all_ships_match_expected_stats(self, fresh_registries):
        """All ships should match their expected_stats if present."""
        # Find all ship JSON files in tests/unit/ships
        ships_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ships")
        ship_files = glob.glob(os.path.join(ships_dir, "*.json"))

        failures = []

        for ship_path in ship_files:
            try:
                data = load_json(ship_path)
                if data is None:
                    failures.append(f"{os.path.basename(ship_path)}: Failed to load JSON")
                    continue

                expected = data.get('expected_stats', {})
                if not expected:
                    continue  # Skip ships without expected_stats

                ship = Ship.from_dict(data, registries=fresh_registries)
                ship.recalculate_stats()

                ship_name = data.get('name', os.path.basename(ship_path))

                # Check HP
                if 'max_hp' in expected:
                    if abs(ship.max_hp - expected['max_hp']) > 1:
                        failures.append(f"{ship_name}: max_hp expected {expected['max_hp']}, got {ship.max_hp}")

                # Check fuel
                if 'max_fuel' in expected:
                    val = ship.resources.get_max_value("fuel")
                    if abs(val - expected['max_fuel']) > 1:
                        failures.append(f"{ship_name}: max_fuel expected {expected['max_fuel']}, got {val}")

                # Check ammo
                if 'max_ammo' in expected:
                    val = ship.resources.get_max_value("ammo")
                    if abs(val - expected['max_ammo']) > 1:
                        failures.append(f"{ship_name}: max_ammo expected {expected['max_ammo']}, got {val}")

                # Check energy
                if 'max_energy' in expected:
                    val = ship.resources.get_max_value("energy")
                    if abs(val - expected['max_energy']) > 1:
                        failures.append(f"{ship_name}: max_energy expected {expected['max_energy']}, got {val}")

            except Exception as e:
                failures.append(f"{os.path.basename(ship_path)}: Error loading - {e}")

        if failures:
            pytest.fail("Ships with stat mismatches:\n" + "\n".join(failures))
