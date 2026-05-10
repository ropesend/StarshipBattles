"""
Shared fixtures for research controls tests.

PROJ-147: Updated module path from game.research.ui to game.ui.research.
"""
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def mock_pygame_gui():
    """Mock pygame_gui elements for testing.

    Note: We must clean up stale package attributes after the test
    because patch.dict removes entries from sys.modules but does NOT
    remove the corresponding attributes from parent packages. This
    leaves an inconsistent state that breaks subsequent imports via
    unittest.mock.patch().
    """
    import sys

    with patch.dict('sys.modules', {'pygame_gui': MagicMock()}):
        # Re-import with mocks
        import importlib
        import game.ui.research.research_controls as rc
        importlib.reload(rc)
        yield rc

    # After patch.dict exits, the modules that were imported during the context
    # have corrupted pygame_gui references (they're bound to the MagicMock that
    # was in sys.modules during import). If research_scene was imported (via the
    # game.ui.research __init__.py), it now has a stale pygame_gui reference.
    #
    # Fix: Reload the research_scene module to rebind pygame_gui to the real module.
    if 'game.ui.research.research_scene' in sys.modules:
        import importlib
        import game.ui.research.research_scene
        importlib.reload(game.ui.research.research_scene)


@pytest.fixture
def mock_manager():
    """Create a mock pygame_gui UI manager."""
    return MagicMock()


@pytest.fixture
def mock_tracker():
    """Create a mock ResearchTracker."""
    tracker = MagicMock()
    tracker.turn_number = 0
    tracker.rp_budget = 200
    tracker.auto_spread_enabled = False
    tracker.get_total_allocated.return_value = 50
    tracker.get_remaining_rp.return_value = 150
    tracker.get_state.return_value = MagicMock(
        current_level=0,
        current_chance=0.25,
        rp_allocation=50
    )
    tracker.get_all_tech_levels.return_value = {}
    tracker.MIN_RP_BUDGET = 50
    tracker.MAX_RP_BUDGET = 500
    return tracker


@pytest.fixture
def mock_tech_tree():
    """Create a mock TechTree."""
    tree = MagicMock()
    tree.nodes = {}
    return tree


@pytest.fixture
def mock_node():
    """Create a mock TechNode."""
    node = MagicMock()
    node.id = 'test_node'
    node.name = 'Test Node'
    node.max_levels = 5
    node.base_decay = 0.01
    node.volatility = 0.1
    node.price = 1.0
    node.price_curve = 'flat'
    node.get_status.return_value = 'available'
    node.get_effective_price.return_value = 1.0
    return node
