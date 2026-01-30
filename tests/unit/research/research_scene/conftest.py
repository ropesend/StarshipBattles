"""
Shared fixtures for ResearchTreeScene tests.
"""
import pytest
import sys


@pytest.fixture(autouse=True)
def ensure_fresh_research_scene_import():
    """
    Ensure the research_scene module is freshly imported before each test.

    Other tests (particularly test_research_controls.py) may import
    game.research.ui.research_scene with a mocked pygame_gui, leaving
    corrupted references. This fixture ensures the module is properly
    loaded with the real pygame_gui before the test's patches are applied.
    """
    module_name = 'game.research.ui.research_scene'

    # Force import of the module to ensure it's in sys.modules
    # with proper pygame_gui binding BEFORE the test's patches run
    import importlib
    import pygame_gui as real_pygame_gui

    if module_name in sys.modules:
        mod = sys.modules[module_name]
        # Check if pygame_gui is corrupted (e.g., a MagicMock)
        if not hasattr(mod, 'pygame_gui') or mod.pygame_gui is not real_pygame_gui:
            importlib.reload(mod)
    else:
        # Module not loaded yet - import it fresh
        import game.research.ui.research_scene  # noqa: F401

    yield
