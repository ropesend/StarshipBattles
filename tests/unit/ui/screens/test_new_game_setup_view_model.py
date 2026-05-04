"""Tests for NewGameSetupViewModel (PROJ-328 Phase B).

Pure-Python state-container tests — no pygame imports needed. Covers
defaults, player-slot visibility derivation, race set/clear/get,
modal-state tracking, and the system-count bound accessors.
"""

from unittest.mock import MagicMock

import pytest

from game.strategy.engine.game_config import (
    DEFAULT_SYSTEM_COUNT,
    MAX_SYSTEM_COUNT,
    MIN_SYSTEM_COUNT,
)
from game.ui.screens.new_game_setup_view_model import (
    DEFAULT_GALAXY_TYPE,
    DEFAULT_PLAYER_COUNT,
    MAX_PLAYER_SLOTS,
    NewGameSetupViewModel,
)


class TestDefaults:
    def test_default_player_count(self):
        vm = NewGameSetupViewModel()
        assert vm.player_count == DEFAULT_PLAYER_COUNT

    def test_default_galaxy_type(self):
        vm = NewGameSetupViewModel()
        assert vm.galaxy_type == DEFAULT_GALAXY_TYPE

    def test_default_system_count(self):
        vm = NewGameSetupViewModel()
        assert vm.system_count == DEFAULT_SYSTEM_COUNT

    def test_default_player_races_all_none(self):
        vm = NewGameSetupViewModel()
        assert vm.player_races == [None] * MAX_PLAYER_SLOTS

    def test_default_modal_state_clean(self):
        vm = NewGameSetupViewModel()
        assert vm.active_race_modal is None
        assert vm.race_modal_player_index == -1


class TestVisibility:
    @pytest.mark.parametrize("count,index,expected", [
        (2, 0, True),
        (2, 1, True),
        (2, 2, False),
        (2, 3, False),
        (4, 3, True),
        (1, 1, False),
    ])
    def test_is_player_visible(self, count, index, expected):
        vm = NewGameSetupViewModel(player_count=count)
        assert vm.is_player_visible(index) is expected


class TestSetPlayerCount:
    def test_increase_returns_no_hidden_indices(self):
        vm = NewGameSetupViewModel(player_count=2)
        assert vm.set_player_count(4) == []
        assert vm.player_count == 4

    def test_decrease_returns_newly_hidden_indices(self):
        vm = NewGameSetupViewModel(player_count=4)
        assert vm.set_player_count(2) == [2, 3]
        assert vm.player_count == 2

    def test_same_count_returns_empty(self):
        vm = NewGameSetupViewModel(player_count=2)
        assert vm.set_player_count(2) == []


class TestRaceSlots:
    def test_set_and_get_race(self):
        vm = NewGameSetupViewModel()
        race = MagicMock(name="race_config")
        vm.set_race(1, race)
        assert vm.get_race(1) is race

    def test_get_race_for_unset_slot_returns_none(self):
        vm = NewGameSetupViewModel()
        assert vm.get_race(0) is None

    def test_clear_race_resets_to_none(self):
        vm = NewGameSetupViewModel()
        vm.set_race(0, MagicMock())
        vm.clear_race(0)
        assert vm.get_race(0) is None

    def test_clear_race_idempotent(self):
        vm = NewGameSetupViewModel()
        vm.clear_race(0)  # already None
        vm.clear_race(0)
        assert vm.get_race(0) is None

    def test_set_race_out_of_range_silently_ignored(self):
        vm = NewGameSetupViewModel()
        vm.set_race(99, MagicMock())  # no IndexError
        assert vm.get_race(99) is None

    def test_active_player_races_returns_visible_slice(self):
        vm = NewGameSetupViewModel(player_count=2)
        race_0 = MagicMock(name="r0")
        race_1 = MagicMock(name="r1")
        race_3 = MagicMock(name="r3")
        vm.set_race(0, race_0)
        vm.set_race(1, race_1)
        vm.set_race(3, race_3)
        # Only first 2 slots returned (player_count=2).
        active = vm.active_player_races()
        assert active == [race_0, race_1]


class TestModalState:
    def test_open_race_modal_records_state(self):
        vm = NewGameSetupViewModel()
        modal = MagicMock(name="modal")
        vm.open_race_modal(modal, 2)
        assert vm.active_race_modal is modal
        assert vm.race_modal_player_index == 2

    def test_close_race_modal_clears_state(self):
        vm = NewGameSetupViewModel()
        vm.open_race_modal(MagicMock(), 1)
        vm.close_race_modal()
        assert vm.active_race_modal is None
        assert vm.race_modal_player_index == -1

    def test_close_race_modal_idempotent(self):
        vm = NewGameSetupViewModel()
        vm.close_race_modal()
        vm.close_race_modal()
        assert vm.active_race_modal is None
        assert vm.race_modal_player_index == -1


class TestSystemCountBounds:
    def test_min_matches_game_config(self):
        assert NewGameSetupViewModel.system_count_min() == MIN_SYSTEM_COUNT

    def test_max_matches_game_config(self):
        assert NewGameSetupViewModel.system_count_max() == MAX_SYSTEM_COUNT
