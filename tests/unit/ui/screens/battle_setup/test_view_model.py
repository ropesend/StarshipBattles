"""PROJ-282 Phase 3: `BattleSetupViewModel` tests.

ViewModel holds derived/view state for `FleetBattleSetupScreen`: selection
indices, scanned designs, and a few derived queries. Pure data — no pygame
imports. Following the TestLab MVVM pattern.

PROJ-494 T2.6: hoisted 7 in-method imports to module level.
"""
from __future__ import annotations

from game.ui.screens.battle_setup.view_model import BattleSetupViewModel


class TestBattleSetupViewModelDefaults:
    """A freshly-constructed ViewModel has sensible defaults."""

    def test_construct_with_no_args(self):
        vm = BattleSetupViewModel()
        assert vm.active_side == 0
        assert vm.active_fleet_index == 0
        assert vm.selected_tf_index is None
        assert vm.selected_sq_index is None
        assert vm.selected_ship_index is None
        assert vm.available_designs == []

class TestBattleSetupViewModelMutation:
    """View state mutates via direct attribute assignment (dataclass-style)."""

    def test_set_active_side(self):
        vm = BattleSetupViewModel()
        vm.active_side = 2
        assert vm.active_side == 2

    def test_set_selection_indices(self):
        vm = BattleSetupViewModel()
        vm.selected_tf_index = 1
        vm.selected_sq_index = 0
        vm.selected_ship_index = 3

        assert vm.selected_tf_index == 1
        assert vm.selected_sq_index == 0
        assert vm.selected_ship_index == 3

    def test_set_available_designs(self):
        vm = BattleSetupViewModel()
        designs = [{"name": "Fighter"}, {"name": "Cruiser"}]
        vm.available_designs = designs
        assert vm.available_designs == designs


class TestBattleSetupViewModelHelpers:
    """Derived helpers that keep selection logic testable in isolation."""

    def test_clear_selection(self):
        """`clear_selection()` resets TF/SQ/ship selection to None — used when
        active side or fleet changes."""
        vm = BattleSetupViewModel()
        vm.selected_tf_index = 2
        vm.selected_sq_index = 1
        vm.selected_ship_index = 5

        vm.clear_selection()

        assert vm.selected_tf_index is None
        assert vm.selected_sq_index is None
        assert vm.selected_ship_index is None

    def test_has_tf_selection(self):
        vm = BattleSetupViewModel()
        assert vm.has_tf_selection() is False
        vm.selected_tf_index = 0
        assert vm.has_tf_selection() is True

    def test_has_sq_selection(self):
        """Squadron selection requires BOTH TF and SQ indices set."""
        vm = BattleSetupViewModel()
        assert vm.has_sq_selection() is False
        vm.selected_tf_index = 0
        assert vm.has_sq_selection() is False  # TF only, no SQ
        vm.selected_sq_index = 1
        assert vm.has_sq_selection() is True


