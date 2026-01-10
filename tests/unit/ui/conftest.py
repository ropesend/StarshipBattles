"""
UI test configuration and shared fixtures.
Ensures proper import order and cleanup for parallel execution.

This conftest.py pre-imports game.ui submodules in a deterministic order
to prevent race conditions when pytest-xdist spawns multiple workers.
"""
import sys
import os
import pytest

def pytest_configure(config):
    """
    Called before test collection.
    Ensures game.ui modules are importable in consistent order.
    
    This prevents race conditions during parallel worker startup by forcing
    all game.ui submodules to be imported in a deterministic sequence before
    any tests run.
    """
    # Force import of game.ui subpackages in deterministic order
    # This prevents race conditions when pytest-xdist workers load modules
    try:
        # Import in dependency order: renderer first, then screens, then panels
        import game.ui.renderer.sprites
        import game.ui.renderer.camera
        import game.ui.renderer.game_renderer
        import game.ui.screens.battle_scene
        import game.ui.screens.battle_screen
        import game.ui.screens.builder_screen
        import game.ui.panels.battle_panels
        import game.ui.panels.builder_widgets
    except ImportError as e:
        # Log but don't fail - tests may mock these modules
        print(f"Warning: Could not pre-import game.ui modules: {e}", file=sys.stderr)

