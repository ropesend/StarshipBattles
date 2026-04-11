"""
Unit tests for BattleSetupState — data model for the fleet-based battle setup.

Phase 2: Tests the BattleSetupSide and BattleSetupState classes.
"""

import pytest
from unittest.mock import MagicMock


def _make_mock_registries():
    """Create minimal mock registries for testing."""
    registries = MagicMock()
    registries.components = {}
    registries.modifiers = {}
    registries.vehicle_classes = {}
    registries.resources = {}
    return registries


class TestBattleSetupSide:
    """Tests for BattleSetupSide — one side of the battle."""

    def test_side_starts_empty(self):
        """A new side has no fleets and no complexes."""
        from game.ui.screens.battle_setup_state import BattleSetupSide

        side = BattleSetupSide(team_id=0)
        assert side.fleets == []
        assert side.system_complexes == []
        assert side.sector_complexes == []
        assert side.team_id == 0

    def test_add_fleet(self):
        """Can add a fleet to a side."""
        from game.ui.screens.battle_setup_state import BattleSetupSide
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        side = BattleSetupSide(team_id=0)
        fleet = Fleet(1, 0, HexCoord(0, 0))

        side.add_fleet(fleet)
        assert len(side.fleets) == 1
        assert side.fleets[0] is fleet

    def test_remove_fleet(self):
        """Can remove a fleet from a side."""
        from game.ui.screens.battle_setup_state import BattleSetupSide
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        side = BattleSetupSide(team_id=0)
        fleet = Fleet(1, 0, HexCoord(0, 0))
        side.add_fleet(fleet)

        side.remove_fleet(fleet)
        assert len(side.fleets) == 0

    def test_create_fleet_generates_unique_ids(self):
        """create_fleet() creates a new fleet with a unique ID."""
        from game.ui.screens.battle_setup_state import BattleSetupSide

        side = BattleSetupSide(team_id=0)
        f1 = side.create_fleet("Alpha Force")
        f2 = side.create_fleet("Beta Force")

        assert f1.id != f2.id
        assert len(side.fleets) == 2

    def test_all_ships_across_fleets(self):
        """all_ships returns ships from all fleets."""
        from game.ui.screens.battle_setup_state import BattleSetupSide
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        side = BattleSetupSide(team_id=0)
        f1 = Fleet(1, 0, HexCoord(0, 0))
        f2 = Fleet(2, 0, HexCoord(0, 0))

        s1 = MagicMock()
        s1.instance_id = "s1"
        s1.is_combat_capable.return_value = True
        s1.vehicle_type = "Ship"
        s1.get_calculated_stats.return_value = {"mass": 1000, "strategic_movement": 100}

        s2 = MagicMock()
        s2.instance_id = "s2"
        s2.is_combat_capable.return_value = True
        s2.vehicle_type = "Ship"
        s2.get_calculated_stats.return_value = {"mass": 1000, "strategic_movement": 100}

        f1.add_ship(s1)
        f2.add_ship(s2)
        side.add_fleet(f1)
        side.add_fleet(f2)

        all_ships = side.all_ships
        assert len(all_ships) == 2


class TestBattleSetupState:
    """Tests for BattleSetupState — full battle setup with two sides."""

    def test_state_has_two_sides(self):
        """BattleSetupState has side_0 and side_1."""
        from game.ui.screens.battle_setup_state import BattleSetupState

        state = BattleSetupState()
        assert state.side_0.team_id == 0
        assert state.side_1.team_id == 1

    def test_add_ship_from_design(self):
        """add_ship_from_design creates a ShipInstance and adds it to a fleet."""
        from game.ui.screens.battle_setup_state import BattleSetupState

        state = BattleSetupState()
        fleet = state.side_0.create_fleet("Test Fleet")

        design_data = {
            "name": "Test Ship",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
        }

        state.add_ship_from_design(fleet, design_data, registries=_make_mock_registries())
        assert len(fleet.ships) == 1
        assert fleet.ships[0].name == "Test Ship"

    def test_serialization_round_trip(self):
        """BattleSetupState can serialize and deserialize."""
        from game.ui.screens.battle_setup_state import BattleSetupState

        state = BattleSetupState()
        state.side_0.create_fleet("Alpha")
        state.side_1.create_fleet("Beta")

        data = state.to_dict()
        restored = BattleSetupState.from_dict(data)

        assert len(restored.side_0.fleets) == 1
        assert len(restored.side_1.fleets) == 1
        assert restored.side_0.fleets[0].id is not None

    def test_clear_resets_state(self):
        """clear() removes all fleets and complexes."""
        from game.ui.screens.battle_setup_state import BattleSetupState

        state = BattleSetupState()
        state.side_0.create_fleet("Alpha")
        state.side_1.create_fleet("Beta")

        state.clear()
        assert len(state.side_0.fleets) == 0
        assert len(state.side_1.fleets) == 0
