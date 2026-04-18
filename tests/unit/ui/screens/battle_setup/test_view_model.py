"""PROJ-282 Phase 3: `BattleSetupViewModel` tests.

ViewModel holds derived/view state for `FleetBattleSetupScreen`: selection
indices, scanned designs, and a few derived queries. Pure data — no pygame
imports. Following the TestLab MVVM pattern.
"""
from __future__ import annotations


class TestBattleSetupViewModelDefaults:
    """A freshly-constructed ViewModel has sensible defaults."""

    def test_construct_with_no_args(self):
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        vm = BattleSetupViewModel()
        assert vm.active_side == 0
        assert vm.active_fleet_index == 0
        assert vm.selected_tf_index is None
        assert vm.selected_sq_index is None
        assert vm.selected_ship_index is None
        assert vm.available_designs == []

    def test_no_pygame_import_in_view_model_module(self):
        """ViewModel must remain pygame-free (TestLab convention)."""
        import ast
        import inspect

        from game.ui.screens.battle_setup import view_model as vm_mod

        src = inspect.getsource(vm_mod)
        tree = ast.parse(src)
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        assert not any(name.startswith("pygame") for name in imports), imports


class TestBattleSetupViewModelMutation:
    """View state mutates via direct attribute assignment (dataclass-style)."""

    def test_set_active_side(self):
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        vm = BattleSetupViewModel()
        vm.active_side = 2
        assert vm.active_side == 2

    def test_set_selection_indices(self):
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        vm = BattleSetupViewModel()
        vm.selected_tf_index = 1
        vm.selected_sq_index = 0
        vm.selected_ship_index = 3

        assert vm.selected_tf_index == 1
        assert vm.selected_sq_index == 0
        assert vm.selected_ship_index == 3

    def test_set_available_designs(self):
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        vm = BattleSetupViewModel()
        designs = [{"name": "Fighter"}, {"name": "Cruiser"}]
        vm.available_designs = designs
        assert vm.available_designs == designs


class TestBattleSetupViewModelHelpers:
    """Derived helpers that keep selection logic testable in isolation."""

    def test_clear_selection(self):
        """`clear_selection()` resets TF/SQ/ship selection to None — used when
        active side or fleet changes."""
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        vm = BattleSetupViewModel()
        vm.selected_tf_index = 2
        vm.selected_sq_index = 1
        vm.selected_ship_index = 5

        vm.clear_selection()

        assert vm.selected_tf_index is None
        assert vm.selected_sq_index is None
        assert vm.selected_ship_index is None

    def test_has_tf_selection(self):
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        vm = BattleSetupViewModel()
        assert vm.has_tf_selection() is False
        vm.selected_tf_index = 0
        assert vm.has_tf_selection() is True

    def test_has_sq_selection(self):
        """Squadron selection requires BOTH TF and SQ indices set."""
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        vm = BattleSetupViewModel()
        assert vm.has_sq_selection() is False
        vm.selected_tf_index = 0
        assert vm.has_sq_selection() is False  # TF only, no SQ
        vm.selected_sq_index = 1
        assert vm.has_sq_selection() is True


class TestBattleSetupViewModelIndependence:
    """ViewModel has no import-time dependency on BattleSetupState.

    Phase 3 invariant: tests for view-model behavior should construct the
    model in isolation, without needing a state or registries.
    """

    def test_can_construct_without_registries_or_state(self):
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        # Should not raise even with zero external setup.
        vm = BattleSetupViewModel()
        assert vm is not None
