"""
Fixtures for research system tests.
"""
import pytest
from unittest.mock import MagicMock

from game.research.data.research_tracker import ResearchTracker, NodeState


@pytest.fixture
def research_tracker():
    """Create a fresh ResearchTracker with a fixed seed for reproducibility."""
    return ResearchTracker(session_seed=12345)


@pytest.fixture
def populated_tracker(research_tracker):
    """Create a tracker with some pre-populated node states."""
    # Add some node states
    research_tracker.node_states['node_a'] = NodeState(current_level=1, current_chance=0.25, rp_allocation=50)
    research_tracker.node_states['node_b'] = NodeState(current_level=0, current_chance=0.10, rp_allocation=30)
    research_tracker.node_states['node_c'] = NodeState(current_level=2, current_chance=0.0, rp_allocation=0)
    return research_tracker


@pytest.fixture
def mock_tech_tree():
    """Create a mock TechTree for testing."""
    tree = MagicMock()

    # Create mock nodes
    node_a = MagicMock()
    node_a.id = 'node_a'
    node_a.get_status.return_value = 'available'

    node_b = MagicMock()
    node_b.id = 'node_b'
    node_b.get_status.return_value = 'available'

    node_c = MagicMock()
    node_c.id = 'node_c'
    node_c.get_status.return_value = 'completed'  # Already maxed

    node_d = MagicMock()
    node_d.id = 'node_d'
    node_d.get_status.return_value = 'locked'

    tree.nodes = {
        'node_a': node_a,
        'node_b': node_b,
        'node_c': node_c,
        'node_d': node_d
    }

    return tree
