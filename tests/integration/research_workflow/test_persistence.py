"""
Integration tests for Research System - Persistence and management.

Tests save/load, auto-spread allocation, budget management, and edge cases.
"""

import pytest
import json

from game.research.data.tech_tree import TechTree
from game.research.data.research_tracker import ResearchTracker
from game.research.systems.research_service import ResearchService


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
