# -*- coding: utf-8 -*-
"""Tests for fleet display name system.

Part 2 of fleet ID collision fix: separate internal ID (immutable, globally
unique) from display_name (per-empire sequential, renamable).
"""
import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.empire import Empire


class TestFleetDisplayName:
    """Fleet.display_name is the renamable display label."""

    def test_fleet_name_returns_display_name_when_set(self):
        """Fleet.name property should return display_name."""
        fleet = Fleet(fleet_id=42, owner_id=0, location=HexCoord(0, 0),
                      display_name="Alpha Strike Force")
        assert fleet.name == "Alpha Strike Force"

    def test_fleet_name_fallback_when_empty(self):
        """Fleet.name should fall back to 'Fleet {id}' when display_name is empty."""
        fleet = Fleet(fleet_id=42, owner_id=0, location=HexCoord(0, 0))
        assert fleet.name == "Fleet 42"

    def test_fleet_display_name_is_renamable(self):
        """display_name should be directly settable."""
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0),
                      display_name="Fleet 1")
        fleet.display_name = "Death Squadron"
        assert fleet.name == "Death Squadron"

    def test_fleet_composition_summary_single_ship(self):
        """composition_summary should describe fleet contents for tooltips."""
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0),
                      display_name="Fleet 1")
        ship = MagicMock()
        ship.name = "HMS Victory"
        ship.is_combat_capable = MagicMock(return_value=True)
        ship.get_calculated_stats = MagicMock(return_value={'strategic_movement': 5.0})
        fleet.ships.append(ship)
        summary = fleet.composition_summary
        assert "HMS Victory" in summary

    def test_fleet_composition_summary_multiple_ships(self):
        """composition_summary with multiple ships should show count."""
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0),
                      display_name="Fleet 1")
        for i in range(3):
            ship = MagicMock()
            ship.name = f"Ship {i}"
            ship.is_combat_capable = MagicMock(return_value=True)
            ship.get_calculated_stats = MagicMock(return_value={'strategic_movement': 5.0})
            fleet.ships.append(ship)
        summary = fleet.composition_summary
        assert "3" in summary

    def test_fleet_composition_summary_empty_fleet(self):
        """composition_summary for empty fleet should indicate empty."""
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0),
                      display_name="Fleet 1")
        summary = fleet.composition_summary
        assert "empty" in summary.lower() or "Empty" in summary


class TestFleetDisplayNameSerialization:
    """display_name should persist across save/load."""

    def test_display_name_in_to_dict(self):
        """Fleet.to_dict should include display_name."""
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0),
                      display_name="Iron Fist")
        data = fleet.to_dict()
        assert data['display_name'] == "Iron Fist"

    def test_display_name_restored_from_dict(self):
        """Fleet.from_dict should restore display_name."""
        data = {
            'id': 1,
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [],
            'path': [],
            'construction_queue': [],
            'display_name': "Iron Fist",
        }
        fleet = Fleet.from_dict(data)
        assert fleet.display_name == "Iron Fist"
        assert fleet.name == "Iron Fist"

    def test_missing_display_name_in_save_falls_back(self):
        """Old saves without display_name should still load (backward compat)."""
        data = {
            'id': 1,
            'owner_id': 0,
            'location': {'q': 0, 'r': 0},
            'speed': 5.0,
            'ships': [],
            'orders': [],
            'path': [],
            'construction_queue': [],
        }
        fleet = Fleet.from_dict(data)
        # Should fall back to "Fleet {id}"
        assert fleet.name == "Fleet 1"


class TestEmpireDisplayNumbering:
    """Per-empire display numbering for auto-naming fleets."""

    def test_empire_display_numbers_are_sequential(self):
        """Each empire has its own sequential display number counter."""
        empire = Empire(0, "Player", (0, 0, 255))
        assert empire.get_next_fleet_display_number() == 1
        assert empire.get_next_fleet_display_number() == 2
        assert empire.get_next_fleet_display_number() == 3

    def test_two_empires_have_independent_display_numbers(self):
        """Display numbers are per-empire, so both start at 1."""
        empire0 = Empire(0, "Player", (0, 0, 255))
        empire1 = Empire(1, "AI", (255, 0, 0))
        assert empire0.get_next_fleet_display_number() == 1
        assert empire1.get_next_fleet_display_number() == 1
        assert empire0.get_next_fleet_display_number() == 2

    def test_empire_display_number_serialization(self):
        """Display number counter should survive save/load."""
        empire = Empire(0, "Player", (0, 0, 255))
        empire.get_next_fleet_display_number()  # consume 1
        empire.get_next_fleet_display_number()  # consume 2

        data = empire.to_dict()
        assert '_next_fleet_display_number' in data

        restored = Empire.from_dict(data)
        assert restored.get_next_fleet_display_number() == 3
