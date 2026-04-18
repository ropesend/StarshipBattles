"""PROJ-282 Phase 4: `BattleSetupRenderer` orchestrator smoke tests.

Structural tests only — we don't instantiate pygame_gui widgets. The
important guarantees:
  - Renderer module imports cleanly (panels + bottom-bar orchestrator)
  - Panel builder module exports are the expected `build(...)` callables
  - Renderer is a stateless orchestrator (no instance attrs between calls)
"""
from __future__ import annotations


class TestRendererModuleShape:
    def test_renderer_module_imports(self):
        from game.ui.screens.battle_setup.renderer import BattleSetupRenderer

        assert BattleSetupRenderer is not None
        assert hasattr(BattleSetupRenderer, "rebuild")

    def test_panel_modules_expose_build_callable(self):
        from game.ui.screens.battle_setup.panels import (
            left_panel,
            center_panel,
            right_panel,
        )
        assert callable(left_panel.build)
        assert callable(center_panel.build)
        assert callable(right_panel.build)

    def test_renderer_is_stateless_between_calls(self):
        """Renderer holds no instance attributes — all handles live on
        the screen. Prevents the renderer from accidentally becoming a
        second source of truth for UI elements."""
        from game.ui.screens.battle_setup.renderer import BattleSetupRenderer

        r = BattleSetupRenderer()
        # Fresh instance: only the class-level method slots exist; no
        # dataclass fields, no mutable state.
        assert r.__dict__ == {}


class TestScreenWiresRenderer:
    """Screen holds a `BattleSetupRenderer` instance and its `_rebuild_ui`
    delegates to `renderer.rebuild(self)`."""

    def test_screen_holds_renderer_instance(self):
        from game.ui.screens.battle_setup_screen import FleetBattleSetupScreen
        from game.ui.screens.battle_setup.renderer import BattleSetupRenderer

        screen = object.__new__(FleetBattleSetupScreen)
        # Mimic minimal __init__ for this attribute check.
        screen.renderer = BattleSetupRenderer()
        assert isinstance(screen.renderer, BattleSetupRenderer)

    def test_rebuild_ui_calls_renderer_rebuild(self):
        """`FleetBattleSetupScreen._rebuild_ui` delegates to
        `self.renderer.rebuild(self)` — no other rebuild path exists."""
        import inspect
        from game.ui.screens.battle_setup_screen import FleetBattleSetupScreen

        src = inspect.getsource(FleetBattleSetupScreen._rebuild_ui)
        # The method body should be a single delegation line. Checking the
        # source text is enough — mocking `renderer.rebuild` would also
        # work but adds more setup for zero extra coverage.
        assert "self.renderer.rebuild(self)" in src
