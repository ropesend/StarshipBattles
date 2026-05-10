"""
Integration tests for Research System - Workflow and progression.

Tests full research workflow, multi-turn progression, and tech tree integration.
"""

import pytest

from game.research.data.tech_tree import TechTree
from game.research.data.tech_node import TechNode, TechRequirement
from game.research.data.research_tracker import ResearchTracker
from game.research.systems.research_service import ResearchService


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
        """Sustained investment eventually leads to breakthrough.

        PROJ-323 Task 5.4: seed RNG so the assertion is deterministic.
        With a seeded RNG, the (>=1 breakthrough) outcome is exact (no flake).
        Verified against random.Random(42) at investment=200 over 100 turns.
        """
        from unittest.mock import patch
        import random

        tracker.set_allocation('root_tech', 200)  # High investment

        breakthroughs = 0
        seeded_rng = random.Random(42)
        with patch('game.research.systems.research_service.random.Random', return_value=seeded_rng):
            for _ in range(100):
                events = ResearchService.process_turn(simple_tech_tree, tracker)
                breakthroughs += sum(1 for e in events if e['event'] == 'breakthrough')

        # With seeded RNG: deterministic, no flake.
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
            # With volatility 0.1 and 50 RP, added_chance ~ 0.39 per turn
            # Decay is 0.01, so net gain ~ 0.38 per turn
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
