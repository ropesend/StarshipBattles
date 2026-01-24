"""
Integration tests for Research System (PROJ-08).

Tests end-to-end functionality of the research system including:
- Full research workflow: start -> invest -> earn breakthrough -> verify effects
- Research persistence across save/load
- Multi-turn research progression
- Tech tree structure and node unlocking
- Auto-spread RP allocation

These tests use real implementations where possible to verify correct integration.
"""

import pytest
import json
import tempfile
import os
import math
from pathlib import Path
from typing import Dict, Any, List

from game.research.data.tech_tree import TechTree
from game.research.data.tech_node import TechNode, TechRequirement
from game.research.data.research_tracker import ResearchTracker, NodeState
from game.research.systems.research_service import ResearchService


# -----------------------------------------------------------------------------
# Test Fixtures
# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------
# Full Workflow Tests
# -----------------------------------------------------------------------------

class TestFullResearchWorkflow:
    """Tests for complete research workflows."""

    def test_start_game_research_state_initialized(self, simple_tech_tree, tracker):
        """Starting a research session initializes all node states."""
        # All nodes should have initialized states
        for node_id in simple_tech_tree.nodes:
            state = tracker.get_state(node_id)
            assert state is not None
            assert state.current_level == 0
            assert state.current_chance == 0.0
            assert state.rp_allocation == 0

    def test_allocate_rp_and_verify_tracking(self, simple_tech_tree, tracker):
        """RP allocation is tracked correctly."""
        tracker.set_allocation('root_tech', 150)

        state = tracker.get_state('root_tech')
        assert state.rp_allocation == 150
        assert tracker.get_total_allocated() == 150

    def test_process_turn_accumulates_chance(self, simple_tech_tree, tracker):
        """Processing a turn accumulates breakthrough chance."""
        tracker.set_allocation('root_tech', 100)
        initial_chance = tracker.get_state('root_tech').current_chance

        events = ResearchService.process_turn(simple_tech_tree, tracker)

        # Chance should have increased (unless breakthrough occurred)
        state = tracker.get_state('root_tech')
        # If breakthrough occurred, chance resets to 0, otherwise it increases
        if any(e['event'] == 'breakthrough' and e['node_id'] == 'root_tech' for e in events):
            assert state.current_level == 1
            assert state.current_chance == 0.0
        else:
            assert state.current_chance > initial_chance

    def test_multiple_turns_lead_to_breakthrough(self, simple_tech_tree, tracker):
        """Sustained investment eventually leads to breakthrough."""
        tracker.set_allocation('root_tech', 200)  # High investment

        breakthroughs = 0
        for _ in range(100):
            events = ResearchService.process_turn(simple_tech_tree, tracker)
            breakthroughs += sum(1 for e in events if e['event'] == 'breakthrough')

        # With high investment over 100 turns, should have at least one breakthrough
        assert breakthroughs >= 1

    def test_breakthrough_unlocks_dependent_node(self, simple_tech_tree, tracker):
        """Breakthrough in prerequisite unlocks dependent node."""
        # Initially child_tech should be locked
        tech_levels = tracker.get_all_tech_levels()
        child_status = simple_tech_tree.nodes['child_tech'].get_status(0, tech_levels)
        assert child_status == 'locked'

        # Get root_tech to level 1
        tracker.get_state('root_tech').current_level = 1

        # Now child_tech should be available
        tech_levels = tracker.get_all_tech_levels()
        child_status = simple_tech_tree.nodes['child_tech'].get_status(0, tech_levels)
        assert child_status == 'available'

    def test_complete_tech_path(self, simple_tech_tree, tracker):
        """Can complete an entire tech path from root to advanced."""
        # Manually set levels to simulate completed research
        tracker.get_state('root_tech').current_level = 3
        tracker.get_state('child_tech').current_level = 2
        tracker.get_state('advanced_tech').current_level = 1

        # All techs should show as completed
        tech_levels = tracker.get_all_tech_levels()

        root_status = simple_tech_tree.nodes['root_tech'].get_status(3, tech_levels)
        child_status = simple_tech_tree.nodes['child_tech'].get_status(2, tech_levels)
        advanced_status = simple_tech_tree.nodes['advanced_tech'].get_status(1, tech_levels)

        assert root_status == 'completed'
        assert child_status == 'completed'
        assert advanced_status == 'completed'


class TestResearchPersistence:
    """Tests for research state save/load."""

    def test_save_and_load_preserves_levels(self, simple_tech_tree, tracker):
        """Saving and loading preserves tech levels."""
        # Set some levels
        tracker.get_state('root_tech').current_level = 2
        tracker.get_state('child_tech').current_level = 1

        # Save
        save_data = tracker.to_dict()

        # Create new tracker and load
        new_tracker = ResearchTracker(session_seed=42)
        new_tracker = ResearchTracker.from_dict(save_data)

        # Verify levels preserved
        assert new_tracker.get_state('root_tech').current_level == 2
        assert new_tracker.get_state('child_tech').current_level == 1

    def test_save_and_load_preserves_chance(self, simple_tech_tree, tracker):
        """Saving and loading preserves accumulated chance."""
        # Set accumulated chance
        tracker.get_state('root_tech').current_chance = 0.45

        # Save
        save_data = tracker.to_dict()

        # Load
        new_tracker = ResearchTracker.from_dict(save_data)

        # Verify chance preserved
        assert new_tracker.get_state('root_tech').current_chance == pytest.approx(0.45)

    def test_save_and_load_preserves_allocations(self, simple_tech_tree, tracker):
        """Saving and loading preserves RP allocations."""
        tracker.set_allocation('root_tech', 75)
        tracker.set_allocation('child_tech', 50)

        # Save
        save_data = tracker.to_dict()

        # Load
        new_tracker = ResearchTracker.from_dict(save_data)

        # Verify allocations preserved
        assert new_tracker.get_state('root_tech').rp_allocation == 75
        assert new_tracker.get_state('child_tech').rp_allocation == 50

    def test_save_and_load_preserves_turn_number(self, simple_tech_tree, tracker):
        """Saving and loading preserves turn number."""
        # Simulate some turns
        for _ in range(5):
            tracker.increment_turn()

        # Save
        save_data = tracker.to_dict()

        # Load
        new_tracker = ResearchTracker.from_dict(save_data)

        # Verify turn preserved
        assert new_tracker.turn_number == 5

    def test_save_and_load_preserves_session_seed(self, tracker):
        """Saving and loading preserves session seed."""
        # Save
        save_data = tracker.to_dict()

        # Load
        new_tracker = ResearchTracker.from_dict(save_data)

        # Verify seed preserved
        assert new_tracker.session_seed == tracker.session_seed

    def test_round_trip_serialization(self, simple_tech_tree, tracker):
        """Complete round-trip serialization works correctly."""
        # Set up complex state
        tracker.get_state('root_tech').current_level = 1
        tracker.get_state('root_tech').current_chance = 0.35
        tracker.set_allocation('root_tech', 100)
        tracker.get_state('child_tech').current_chance = 0.10
        tracker.set_allocation('child_tech', 50)
        tracker.set_rp_budget(250)

        for _ in range(3):
            tracker.increment_turn()

        # Round-trip
        save_data = tracker.to_dict()
        json_str = json.dumps(save_data)
        loaded_data = json.loads(json_str)
        new_tracker = ResearchTracker.from_dict(loaded_data)

        # Verify everything
        assert new_tracker.turn_number == 3
        assert new_tracker.rp_budget == 250
        assert new_tracker.get_state('root_tech').current_level == 1
        assert new_tracker.get_state('root_tech').current_chance == pytest.approx(0.35)
        assert new_tracker.get_state('root_tech').rp_allocation == 100
        assert new_tracker.get_state('child_tech').current_chance == pytest.approx(0.10)


class TestMultiTurnProgression:
    """Tests for multi-turn research progression."""

    def test_chance_accumulates_over_turns(self, simple_tech_tree, tracker):
        """Chance accumulates with consistent investment."""
        tracker.set_allocation('root_tech', 50)

        chances = []
        for _ in range(10):
            ResearchService.process_turn(simple_tech_tree, tracker)
            state = tracker.get_state('root_tech')
            if state.current_level == 0:  # No breakthrough yet
                chances.append(state.current_chance)
            else:
                break  # Stop if breakthrough occurred

        # If we have enough data points, verify accumulation
        if len(chances) >= 3:
            # Later chances should generally be higher (net of decay)
            # With volatility 0.1 and 50 RP, added_chance ≈ 0.39 per turn
            # Decay is 0.01, so net gain ≈ 0.38 per turn
            assert chances[-1] > chances[0]

    def test_decay_applies_without_investment(self, simple_tech_tree, tracker):
        """Accumulated chance decays without investment."""
        # Set initial chance
        tracker.get_state('root_tech').current_chance = 0.50
        tracker.set_allocation('root_tech', 0)  # No investment

        ResearchService.process_turn(simple_tech_tree, tracker)

        # Should have decayed
        state = tracker.get_state('root_tech')
        assert state.current_chance < 0.50
        # Should have decayed by base_decay (0.01)
        assert state.current_chance == pytest.approx(0.49)

    def test_turn_counter_increments(self, simple_tech_tree, tracker):
        """Turn counter increments each turn."""
        assert tracker.turn_number == 0

        ResearchService.process_turn(simple_tech_tree, tracker)
        assert tracker.turn_number == 1

        ResearchService.process_turn(simple_tech_tree, tracker)
        assert tracker.turn_number == 2

    def test_events_recorded_each_turn(self, simple_tech_tree, tracker):
        """Events are recorded in tracker.turn_log."""
        tracker.set_allocation('root_tech', 100)

        ResearchService.process_turn(simple_tech_tree, tracker)

        # Should have events in turn_log
        assert tracker.turn_log is not None
        assert len(tracker.turn_log) >= 1

    def test_max_chance_cap_enforced(self, simple_tech_tree, tracker):
        """Chance is capped at MAX_CHANCE (95%)."""
        # Set very high allocation
        tracker.set_allocation('root_tech', 10000)

        # Process multiple turns (reset level after breakthrough)
        for _ in range(50):
            state = tracker.get_state('root_tech')
            if state.current_level > 0:
                state.current_level = 0
                state.current_chance = 0.0

            ResearchService.process_turn(simple_tech_tree, tracker)

            # Verify cap
            assert state.current_chance <= ResearchService.MAX_CHANCE


class TestTechTreeIntegration:
    """Tests for tech tree structure and loading."""

    def test_load_real_tech_tree(self):
        """Can load the real tech tree from JSON."""
        try:
            tree = TechTree.load_from_json()
            assert len(tree.nodes) > 0
        except FileNotFoundError:
            pytest.skip("Tech tree JSON not found")

    def test_tech_tree_validation(self, simple_tech_tree):
        """Tech tree validation catches errors."""
        # Valid tree should have no errors
        errors = simple_tech_tree.validate_requirements()
        assert len(errors) == 0

    def test_depth_calculation(self, simple_tech_tree):
        """Depth calculation works correctly."""
        # root_tech is depth 0
        # child_tech is depth 1
        # advanced_tech is depth 2
        max_depth = simple_tech_tree.get_max_depth()
        assert max_depth == 2

        depth_0 = simple_tech_tree.get_nodes_at_depth(0)
        depth_1 = simple_tech_tree.get_nodes_at_depth(1)
        depth_2 = simple_tech_tree.get_nodes_at_depth(2)

        assert len(depth_0) == 1
        assert depth_0[0].id == 'root_tech'
        assert len(depth_1) == 1
        assert depth_1[0].id == 'child_tech'
        assert len(depth_2) == 1
        assert depth_2[0].id == 'advanced_tech'


class TestAutoSpreadAllocation:
    """Tests for auto-spread RP allocation."""

    def test_auto_spread_distributes_evenly(self, simple_tech_tree, tracker):
        """Auto-spread distributes RP evenly among available nodes."""
        tracker.set_rp_budget(200)
        tracker.spread_rp_evenly(simple_tech_tree)

        # Only root_tech is available initially
        assert tracker.get_state('root_tech').rp_allocation == 200
        assert tracker.get_state('child_tech').rp_allocation == 0

    def test_auto_spread_with_multiple_available(self, simple_tech_tree, tracker):
        """Auto-spread distributes among multiple available nodes."""
        # Make child_tech available
        tracker.get_state('root_tech').current_level = 1

        tracker.set_rp_budget(200)
        tracker.spread_rp_evenly(simple_tech_tree)

        # Both root_tech and child_tech are available
        root_alloc = tracker.get_state('root_tech').rp_allocation
        child_alloc = tracker.get_state('child_tech').rp_allocation

        # Should be evenly split (100 each)
        assert root_alloc + child_alloc == 200
        assert root_alloc == child_alloc == 100

    def test_auto_spread_respects_budget(self, simple_tech_tree, tracker):
        """Auto-spread doesn't exceed budget."""
        tracker.set_rp_budget(150)
        tracker.spread_rp_evenly(simple_tech_tree)

        total = tracker.get_total_allocated()
        assert total <= 150


class TestBudgetManagement:
    """Tests for RP budget management."""

    def test_allocation_capped_at_budget(self, simple_tech_tree, tracker):
        """RP allocation is capped at budget."""
        tracker.set_rp_budget(100)
        tracker.set_allocation('root_tech', 150)

        # Should be capped
        assert tracker.get_state('root_tech').rp_allocation <= 100

    def test_remaining_rp_calculation(self, simple_tech_tree, tracker):
        """Remaining RP is calculated correctly."""
        tracker.set_rp_budget(200)
        tracker.set_allocation('root_tech', 75)

        remaining = tracker.get_remaining_rp()
        assert remaining == 125

    def test_budget_change_affects_remaining(self, simple_tech_tree, tracker):
        """Changing budget affects remaining RP."""
        tracker.set_allocation('root_tech', 100)

        tracker.set_rp_budget(300)
        assert tracker.get_remaining_rp() == 200

        tracker.set_rp_budget(150)
        assert tracker.get_remaining_rp() == 50


class TestEffectivePriceCalculation:
    """Tests for effective price/cost calculations."""

    def test_flat_price_curve(self, simple_tech_tree):
        """Flat price curve returns base price."""
        node = simple_tech_tree.nodes['root_tech']
        assert node.price_curve == "flat"

        # All levels should have same price
        assert node.get_effective_price(1) == 1.0
        assert node.get_effective_price(2) == 1.0
        assert node.get_effective_price(3) == 1.0

    def test_linear_price_curve(self, simple_tech_tree):
        """Linear price curve increases with level."""
        node = simple_tech_tree.nodes['child_tech']
        assert node.price_curve == "linear"

        # Price increases linearly
        price_1 = node.get_effective_price(1)
        price_2 = node.get_effective_price(2)
        assert price_2 > price_1

    def test_quadratic_price_curve(self, simple_tech_tree):
        """Quadratic price curve increases faster."""
        node = simple_tech_tree.nodes['advanced_tech']
        assert node.price_curve == "quadratic"

        # Price increases quadratically
        price_1 = node.get_effective_price(1)
        assert price_1 > node.price  # Higher than base

    def test_effective_rp_calculation(self, simple_tech_tree, tracker):
        """Effective RP is raw RP divided by effective price."""
        # Allocate 300 RP to expensive node
        tracker.set_allocation('advanced_tech', 300)
        # Make it available
        tracker.get_state('root_tech').current_level = 3
        tracker.get_state('child_tech').current_level = 2

        events = ResearchService.process_turn(simple_tech_tree, tracker)

        # Find the event for advanced_tech
        adv_events = [e for e in events if e['node_id'] == 'advanced_tech']
        if adv_events:
            details = adv_events[0]['details']
            # Effective RP should be less than raw RP due to price
            assert details['effective_rp'] < 300


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_rp_allocation(self, simple_tech_tree, tracker):
        """Zero RP allocation produces decay only."""
        tracker.get_state('root_tech').current_chance = 0.50
        tracker.set_allocation('root_tech', 0)

        events = ResearchService.process_turn(simple_tech_tree, tracker)

        # Should have decay event
        decay_events = [e for e in events if e['event'] == 'decay' and e['node_id'] == 'root_tech']
        assert len(decay_events) == 1

    def test_empty_tech_tree(self, tracker):
        """Processing with empty tree produces no events."""
        empty_tree = TechTree()

        events = ResearchService.process_turn(empty_tree, tracker)

        assert events == []

    def test_all_nodes_completed(self, simple_tech_tree, tracker):
        """Processing with all nodes completed produces no events."""
        # Max out all nodes
        for node_id in simple_tech_tree.nodes:
            node = simple_tech_tree.nodes[node_id]
            tracker.get_state(node_id).current_level = node.max_levels

        events = ResearchService.process_turn(simple_tech_tree, tracker)

        # No progress or breakthrough events
        assert all(e['event'] not in ('progress', 'breakthrough') for e in events)

    def test_very_small_allocation(self, simple_tech_tree, tracker):
        """Very small allocation still works."""
        tracker.set_allocation('root_tech', 1)

        # Should not crash
        events = ResearchService.process_turn(simple_tech_tree, tracker)
        assert isinstance(events, list)

    def test_chance_reset_on_breakthrough(self, simple_tech_tree, tracker):
        """Chance resets to 0 on breakthrough."""
        # Set very high chance to guarantee breakthrough
        tracker.get_state('root_tech').current_chance = 0.99
        tracker.set_allocation('root_tech', 1000)

        # Run until breakthrough
        for _ in range(100):
            events = ResearchService.process_turn(simple_tech_tree, tracker)
            bt_events = [e for e in events if e['event'] == 'breakthrough' and e['node_id'] == 'root_tech']
            if bt_events:
                # Verify chance was reset
                assert tracker.get_state('root_tech').current_chance == 0.0
                break
