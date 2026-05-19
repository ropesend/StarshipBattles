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
        assert state.sides[0].team_id == 0
        assert state.sides[1].team_id == 1

    def test_add_ship_from_design(self):
        """add_ship_from_design creates a ShipInstance and adds it to a fleet."""
        from game.ui.screens.battle_setup_state import BattleSetupState

        state = BattleSetupState()
        fleet = state.sides[0].create_fleet("Test Fleet")

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
        state.sides[0].create_fleet("Alpha")
        state.sides[1].create_fleet("Beta")

        data = state.to_dict()
        restored = BattleSetupState.from_dict(data)

        assert len(restored.sides[0].fleets) == 1
        assert len(restored.sides[1].fleets) == 1
        assert restored.sides[0].fleets[0].id is not None

    def test_clear_resets_state(self):
        """clear() removes all fleets and complexes."""
        from game.ui.screens.battle_setup_state import BattleSetupState

        state = BattleSetupState()
        state.sides[0].create_fleet("Alpha")
        state.sides[1].create_fleet("Beta")

        state.clear()
        assert len(state.sides[0].fleets) == 0
        assert len(state.sides[1].fleets) == 0


class TestBattleSetupSideComplexToggles:
    """PROJ-282 Phase 2: `*_complex_toggles` fields on BattleSetupSide.

    Complex toggles used to live on `FleetBattleSetupScreen._complex_toggles`
    (a screen-private dict keyed by `(side_id, scope, design_id)`). Phase 2
    moves them onto the data model so save/load persists them naturally and
    N-team support is per-side by construction (the old screen-level sync
    hardcoded sides 0 and 1, losing toggles for sides 2-7).
    """

    def test_new_side_has_empty_toggle_dicts(self):
        from game.ui.screens.battle_setup_state import BattleSetupSide

        side = BattleSetupSide(team_id=0)
        assert side.system_complex_toggles == {}
        assert side.sector_complex_toggles == {}

    def test_toggle_dicts_accept_design_id_keys(self):
        from game.ui.screens.battle_setup_state import BattleSetupSide

        side = BattleSetupSide(team_id=0)
        side.system_complex_toggles["qs_system_shield_booster_complex"] = True
        side.sector_complex_toggles["qs_sector_damage_booster_complex"] = False

        assert side.system_complex_toggles == {
            "qs_system_shield_booster_complex": True
        }
        assert side.sector_complex_toggles == {
            "qs_sector_damage_booster_complex": False
        }

    def test_to_dict_includes_toggle_fields(self):
        from game.ui.screens.battle_setup_state import BattleSetupSide

        side = BattleSetupSide(team_id=2)
        side.system_complex_toggles = {"qs_system_shield_booster_complex": True}
        side.sector_complex_toggles = {"qs_sector_damage_booster_complex": True}

        data = side.to_dict()
        assert data["system_complex_toggles"] == {
            "qs_system_shield_booster_complex": True
        }
        assert data["sector_complex_toggles"] == {
            "qs_sector_damage_booster_complex": True
        }

    def test_from_dict_restores_toggle_fields(self):
        from game.ui.screens.battle_setup_state import BattleSetupSide

        data = {
            "team_id": 3,
            "fleets": [],
            "system_complexes": [],
            "sector_complexes": [],
            "system_complex_toggles": {"qs_system_shield_booster_complex": True},
            "sector_complex_toggles": {"qs_sector_shield_suppressor_complex": True},
        }
        side = BattleSetupSide.from_dict(data)
        assert side.system_complex_toggles == {
            "qs_system_shield_booster_complex": True
        }
        assert side.sector_complex_toggles == {
            "qs_sector_shield_suppressor_complex": True
        }

    def test_from_dict_rejects_missing_system_complex_toggles(self):
        """PROJ-404 / Rule 3: legacy-tolerance branch is deleted. A payload
        that omits `system_complex_toggles` raises PersistenceException."""
        from game.core.exceptions import PersistenceException
        from game.ui.screens.battle_setup_state import BattleSetupSide

        legacy_data = {
            "team_id": 0,
            "fleets": [],
            "system_complexes": [],
            "sector_complexes": [],
            "sector_complex_toggles": {},
            # No system_complex_toggles
        }
        with pytest.raises(PersistenceException):
            BattleSetupSide.from_dict(legacy_data)

    def test_from_dict_rejects_missing_sector_complex_toggles(self):
        """PROJ-404 / Rule 3: legacy-tolerance branch is deleted. A payload
        that omits `sector_complex_toggles` raises PersistenceException."""
        from game.core.exceptions import PersistenceException
        from game.ui.screens.battle_setup_state import BattleSetupSide

        legacy_data = {
            "team_id": 0,
            "fleets": [],
            "system_complexes": [],
            "sector_complexes": [],
            "system_complex_toggles": {},
            # No sector_complex_toggles
        }
        with pytest.raises(PersistenceException):
            BattleSetupSide.from_dict(legacy_data)

    def test_toggle_roundtrip_through_to_dict_from_dict(self):
        from game.ui.screens.battle_setup_state import BattleSetupSide

        original = BattleSetupSide(team_id=1)
        original.system_complex_toggles = {
            "qs_system_shield_booster_complex": True,
            "qs_system_damage_suppressor_complex": False,
        }
        original.sector_complex_toggles = {
            "qs_sector_shield_projector_complex": True,
        }

        restored = BattleSetupSide.from_dict(original.to_dict())
        assert restored.system_complex_toggles == original.system_complex_toggles
        assert restored.sector_complex_toggles == original.sector_complex_toggles

    def test_multi_side_state_preserves_toggles_on_each_side(self):
        """Regression guard for the bug where `_sync_complex_toggles_to_state`
        hardcoded sides 0/1 and silently dropped toggles for sides 2-7."""
        from game.ui.screens.battle_setup_state import BattleSetupState

        state = BattleSetupState(side_count=3)
        state.sides[0].system_complex_toggles = {"a": True}
        state.sides[1].system_complex_toggles = {"b": True}
        state.sides[2].system_complex_toggles = {"c": True}

        restored = BattleSetupState.from_dict(state.to_dict())
        assert restored.sides[0].system_complex_toggles == {"a": True}
        assert restored.sides[1].system_complex_toggles == {"b": True}
        assert restored.sides[2].system_complex_toggles == {"c": True}


# PROJ-282 Phase 6: screen-level `_sync_complex_toggles_to_state` tests
# deleted — the method moved to `BattleSetupController`. Equivalent
# regression coverage lives in
# tests/unit/ui/screens/battle_setup/test_controller.py::TestSyncComplexTogglesIsNTeamSafe.


class TestScreenDelegatesViewStateToViewModel:
    """PROJ-282 Phase 3: screen's selection attributes back onto ViewModel.

    Guard that property shims route to `self.view_model.*` — if the shim
    is accidentally removed, these tests catch the silent divergence
    between `screen.view_model.active_side` and `screen.view_model.active_side`.
    """

    def test_active_side_shim_routes_to_view_model(self):
        from game.ui.screens.battle_setup.screen import FleetBattleSetupScreen
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        screen = object.__new__(FleetBattleSetupScreen)
        screen.view_model = BattleSetupViewModel()

        screen.view_model.active_side = 3
        assert screen.view_model.active_side == 3
        assert screen.view_model.active_side == 3  # read-through

    def test_selection_shims_route_to_view_model(self):
        from game.ui.screens.battle_setup.screen import FleetBattleSetupScreen
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        screen = object.__new__(FleetBattleSetupScreen)
        screen.view_model = BattleSetupViewModel()

        screen.view_model.selected_tf_index = 2
        screen.view_model.selected_sq_index = 1
        screen.view_model.selected_ship_index = 5

        assert screen.view_model.selected_tf_index == 2
        assert screen.view_model.selected_sq_index == 1
        assert screen.view_model.selected_ship_index == 5

    def test_available_designs_shim_routes_to_view_model(self):
        from game.ui.screens.battle_setup.screen import FleetBattleSetupScreen
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        screen = object.__new__(FleetBattleSetupScreen)
        screen.view_model = BattleSetupViewModel()

        designs = [{"name": "Fighter"}]
        screen.view_model.available_designs = designs
        assert screen.view_model.available_designs is designs
