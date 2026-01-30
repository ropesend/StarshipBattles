"""
Shared fixtures for research workflow integration tests.
"""

import pytest

from game.research.data.tech_tree import TechTree
from game.research.data.tech_node import TechNode, TechRequirement
from game.research.data.research_tracker import ResearchTracker


@pytest.fixture
def simple_tech_tree():
    """Create a simple tech tree for testing."""
    tree = TechTree()

    # Root node (no requirements)
    tree.nodes['root_tech'] = TechNode(
        id='root_tech',
        name='Root Technology',
        max_levels=3,
        base_decay=0.01,
        volatility=0.1,
        price=1.0,
        price_curve="flat"
    )

    # Child node (requires root level 1)
    req = TechRequirement('root_tech', (1, 1))
    req.resolved_level = 1
    tree.nodes['child_tech'] = TechNode(
        id='child_tech',
        name='Child Technology',
        max_levels=2,
        requirements=[[req]],
        base_decay=0.005,
        volatility=0.15,
        price=1.5,
        price_curve="linear"
    )

    # Advanced node (requires child level 2)
    req2 = TechRequirement('child_tech', (2, 2))
    req2.resolved_level = 2
    tree.nodes['advanced_tech'] = TechNode(
        id='advanced_tech',
        name='Advanced Technology',
        max_levels=1,
        requirements=[[req2]],
        base_decay=0.02,
        volatility=0.2,
        price=2.0,
        price_curve="quadratic"
    )

    return tree


@pytest.fixture
def tracker():
    """Create a fresh research tracker with fixed seed."""
    return ResearchTracker(session_seed=42)


@pytest.fixture
def tracker_with_allocation(tracker, simple_tech_tree):
    """Create tracker with initial RP allocation."""
    tracker.set_allocation('root_tech', 100)
    return tracker
