"""
Root test configuration for all unit tests.
Ensures game.ui package is imported early to prevent race conditions.
"""
import sys
import pytest

def pytest_configure(config):
    """
    Global configuration applied to ALL unit tests.
    Pre-imports game.ui before any test collection begins.
    """
    try:
        # Import game.ui package (will trigger __init__.py submodule loading)
        import game.ui
        
        # Verify submodules are loaded
        assert hasattr(game.ui, 'renderer'), "game.ui.renderer not loaded"
        assert hasattr(game.ui, 'screens'), "game.ui.screens not loaded"
        assert hasattr(game.ui, 'panels'), "game.ui.panels not loaded"
    except (ImportError, AssertionError) as e:
        print(f"Warning: Could not pre-import game.ui in root conftest: {e}", 
              file=sys.stderr)
        # Don't fail - tests may mock game.ui
