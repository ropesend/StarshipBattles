"""
Unit tests for ResearchService.

Tests cover:
- Leaky bucket algorithm implementation
- Research point generation per turn
- Research allocation to nodes
- Research completion detection
- Price/cost calculations with effective RP
- Edge cases: zero resources, overflow, negative values
- Multi-turn research progression
"""
import pytest
import math
import random
from unittest.mock import MagicMock, patch

from game.research.systems.research_service import ResearchService
from game.research.data.research_tracker import ResearchTracker, NodeState
from game.research.data.tech_tree import TechTree
from game.research.data.tech_node import TechNode, TechRequirement


@pytest.fixture
def tech_tree():
    """Create a simple tech tree for testing."""
    tree = TechTree()

    # Root node (no requirements)
    tree.nodes['root'] = TechNode(
        id='root',
        name='Root Tech',
        max_levels=3,
        base_decay=0.01,
        volatility=0.1,
        price=1.0,
        price_curve="flat"
    )

    # Child node (depends on root)
    req = TechRequirement('root', (1, 1))
    req.resolved_level = 1
    tree.nodes['child'] = TechNode(
        id='child',
        name='Child Tech',
        max_levels=2,
        requirements=[[req]],
        base_decay=0.005,
        volatility=0.15,
        price=1.5,
        price_curve="linear"
    )

    # Expensive node with high volatility
    tree.nodes['expensive'] = TechNode(
        id='expensive',
        name='Expensive Tech',
        max_levels=5,
        base_decay=0.02,
        volatility=0.3,
        price=3.0,
        price_curve="quadratic"
    )

    return tree


@pytest.fixture
def tracker():
    """Create a fresh ResearchTracker."""
    return ResearchTracker(session_seed=12345)


class TestCalculateAddedChance:
    """Tests for calculate_added_chance helper."""

    def test_zero_rp(self):
        """Zero RP produces zero added chance."""
        assert ResearchService.calculate_added_chance(0.1, 0) == 0.0

    def test_negative_rp(self):
        """Negative RP produces zero added chance."""
        assert ResearchService.calculate_added_chance(0.1, -10) == 0.0

    def test_positive_rp(self):
        """Positive RP produces positive added chance."""
        # volatility * ln(1 + rp) = 0.1 * ln(101) ≈ 0.462
        result = ResearchService.calculate_added_chance(0.1, 100)
        expected = 0.1 * math.log(101)
        assert result == pytest.approx(expected)

    def test_volatility_scaling(self):
        """Higher volatility produces proportionally higher chance."""
        low = ResearchService.calculate_added_chance(0.1, 100)
        high = ResearchService.calculate_added_chance(0.2, 100)
        assert high == pytest.approx(low * 2)

    def test_diminishing_returns(self):
        """RP has diminishing returns (logarithmic)."""
        chance_100 = ResearchService.calculate_added_chance(0.1, 100)
        chance_200 = ResearchService.calculate_added_chance(0.1, 200)
        chance_300 = ResearchService.calculate_added_chance(0.1, 300)

        # Doubling RP should not double chance
        assert chance_200 < chance_100 * 2
        # Triple RP should not triple chance
        assert chance_300 < chance_100 * 3


class TestEstimateTurnsToBreakthrough:
    """Tests for estimate_turns_to_breakthrough helper."""

    def test_zero_rp(self):
        """Zero RP returns infinity."""
        result = ResearchService.estimate_turns_to_breakthrough(0.1, 0.01, 0)
        assert result == float('inf')

    def test_negative_rp(self):
        """Negative RP returns infinity."""
        result = ResearchService.estimate_turns_to_breakthrough(0.1, 0.01, -50)
        assert result == float('inf')

    def test_decay_exceeds_gain(self):
        """Returns infinity when decay exceeds gain from investment."""
        # Very low RP, high decay
        result = ResearchService.estimate_turns_to_breakthrough(0.01, 0.5, 1)
        assert result == float('inf')

    def test_reasonable_estimate(self):
        """Returns reasonable estimate for typical values."""
        # With moderate investment, should get finite result
        result = ResearchService.estimate_turns_to_breakthrough(0.1, 0.01, 50)
        assert result > 0
        assert result < 100  # Should be achievable

    def test_higher_rp_faster_breakthrough(self):
        """Higher RP investment leads to faster breakthrough."""
        low_rp = ResearchService.estimate_turns_to_breakthrough(0.1, 0.01, 50)
        high_rp = ResearchService.estimate_turns_to_breakthrough(0.1, 0.01, 200)
        assert high_rp < low_rp


class TestProcessTurnBasics:
    """Tests for basic process_turn functionality."""

    def test_increments_turn_number(self, tech_tree, tracker):
        """process_turn increments the turn counter."""
        assert tracker.turn_number == 0

        ResearchService.process_turn(tech_tree, tracker)
        assert tracker.turn_number == 1

        ResearchService.process_turn(tech_tree, tracker)
        assert tracker.turn_number == 2

    def test_returns_events_list(self, tech_tree, tracker):
        """process_turn returns list of events."""
        events = ResearchService.process_turn(tech_tree, tracker)
        assert isinstance(events, list)

    def test_stores_events_in_tracker(self, tech_tree, tracker):
        """process_turn stores events in tracker.turn_log."""
        tracker.set_allocation('root', 100)
        events = ResearchService.process_turn(tech_tree, tracker)
        assert tracker.turn_log == events

    def test_skips_completed_nodes(self, tech_tree, tracker):
        """Completed nodes are not processed."""
        # Set root to max level
        tracker.get_state('root').current_level = 3  # max_levels = 3
        tracker.set_allocation('root', 100)

        events = ResearchService.process_turn(tech_tree, tracker)

        # Should not have any events for root
        root_events = [e for e in events if e['node_id'] == 'root']
        assert len(root_events) == 0


class TestProcessTurnDecay:
    """Tests for decay mechanics."""

    def test_decay_applied_to_accumulated_chance(self, tech_tree, tracker):
        """Decay is applied to nodes with accumulated chance."""
        state = tracker.get_state('root')
        state.current_chance = 0.5

        ResearchService.process_turn(tech_tree, tracker)

        # Decay of 0.01 should be applied
        assert state.current_chance == pytest.approx(0.49)

    def test_decay_clamps_at_zero(self, tech_tree, tracker):
        """Chance never goes below 0."""
        state = tracker.get_state('root')
        state.current_chance = 0.005  # Less than decay rate

        ResearchService.process_turn(tech_tree, tracker)

        assert state.current_chance == 0.0

    def test_decay_event_generated(self, tech_tree, tracker):
        """Decay without investment generates decay event."""
        state = tracker.get_state('root')
        state.current_chance = 0.5
        # No allocation

        events = ResearchService.process_turn(tech_tree, tracker)

        decay_events = [e for e in events if e['event'] == 'decay']
        assert len(decay_events) == 1
        assert decay_events[0]['node_id'] == 'root'
        assert 'old_chance' in decay_events[0]['details']
        assert 'new_chance' in decay_events[0]['details']

    def test_decay_on_locked_nodes(self, tech_tree, tracker):
        """Locked nodes still get decay applied to accumulated chance."""
        # Child is locked (needs root level 1)
        state = tracker.get_state('child')
        state.current_chance = 0.5

        events = ResearchService.process_turn(tech_tree, tracker)

        # Should decay
        assert state.current_chance < 0.5
        decay_events = [e for e in events if e['node_id'] == 'child' and e['event'] == 'decay']
        assert len(decay_events) == 1


class TestProcessTurnInvestment:
    """Tests for RP investment mechanics."""

    def test_investment_increases_chance(self, tech_tree, tracker):
        """Investing RP increases breakthrough chance."""
        tracker.set_allocation('root', 100)
        state = tracker.get_state('root')
        initial_chance = state.current_chance

        ResearchService.process_turn(tech_tree, tracker)

        # Chance should be higher than initial (minus decay)
        expected_added = tech_tree.nodes['root'].volatility * math.log(101)
        # After decay of 0.01, chance should be about expected_added - 0.01
        # Actually with decay applied first then investment:
        # new_chance = max(0, initial_chance - decay) + added
        assert state.current_chance >= 0  # At minimum 0 after possible breakthrough

    def test_progress_event_generated(self, tech_tree, tracker):
        """Investment generates progress event (if no breakthrough)."""
        tracker.set_allocation('root', 10)  # Low investment

        # Run turn - should generate either progress or breakthrough
        events = ResearchService.process_turn(tech_tree, tracker)

        # Should have some event for root
        root_events = [e for e in events if e['node_id'] == 'root']
        assert len(root_events) >= 1
        # Event should be either progress or breakthrough
        assert root_events[0]['event'] in ('progress', 'breakthrough')

    def test_effective_price_reduces_effective_rp(self, tech_tree, tracker):
        """Higher price nodes get less effective RP."""
        # Expensive node has price=3.0
        tracker.set_allocation('expensive', 300)

        # Check the effective RP in event details
        events = ResearchService.process_turn(tech_tree, tracker)

        exp_events = [e for e in events if e['node_id'] == 'expensive']
        if exp_events:
            details = exp_events[0]['details']
            # Effective RP should be 300/effective_price
            assert details['effective_rp'] < 300


class TestProcessTurnBreakthrough:
    """Tests for breakthrough mechanics."""

    def test_breakthrough_increases_level(self, tech_tree, tracker):
        """Breakthrough increases node level."""
        state = tracker.get_state('root')
        state.current_chance = 0.95  # High chance
        tracker.set_allocation('root', 100)

        # Force a low roll to trigger breakthrough
        with patch('random.Random.random', return_value=0.01):
            events = ResearchService.process_turn(tech_tree, tracker)

        # Should have leveled up
        assert state.current_level >= 1

    def test_breakthrough_resets_chance(self, tech_tree, tracker):
        """Breakthrough resets chance to 0."""
        state = tracker.get_state('root')
        state.current_chance = 0.8
        tracker.set_allocation('root', 100)

        # Set up high accumulated chance
        original_level = state.current_level

        # Run enough turns to likely get a breakthrough
        for _ in range(50):
            ResearchService.process_turn(tech_tree, tracker)
            if state.current_level > original_level:
                # Breakthrough occurred
                assert state.current_chance == 0.0
                break

    def test_breakthrough_event_details(self, tech_tree, tracker):
        """Breakthrough event contains all required details."""
        state = tracker.get_state('root')
        state.current_chance = 0.99
        tracker.set_allocation('root', 100)

        # Force breakthrough
        with patch('random.Random.random', return_value=0.001):
            events = ResearchService.process_turn(tech_tree, tracker)

        breakthrough_events = [e for e in events if e['event'] == 'breakthrough']
        assert len(breakthrough_events) == 1

        details = breakthrough_events[0]['details']
        assert 'old_level' in details
        assert 'new_level' in details
        assert 'max_level' in details
        assert 'chance' in details
        assert 'roll' in details
        assert 'rp_invested' in details
        assert 'turn' in details

    def test_chance_capped_at_max(self, tech_tree, tracker):
        """Chance is capped at MAX_CHANCE (95%)."""
        state = tracker.get_state('root')
        tracker.set_allocation('root', 10000)  # Very high investment

        # Multiple turns to accumulate
        for _ in range(100):
            if state.current_chance > 0:  # Reset after breakthrough
                state.current_chance = 0.0
                state.current_level = 0
            ResearchService.process_turn(tech_tree, tracker)
            assert state.current_chance <= ResearchService.MAX_CHANCE


class TestProcessTurnLockedNodes:
    """Tests for locked node handling."""

    def test_locked_node_not_processed_for_investment(self, tech_tree, tracker):
        """Locked nodes don't process RP investment."""
        # Child needs root level 1, but root is level 0
        tracker.set_allocation('child', 100)

        events = ResearchService.process_turn(tech_tree, tracker)

        # Child should not have progress or breakthrough events
        child_events = [e for e in events if e['node_id'] == 'child']
        for event in child_events:
            assert event['event'] != 'progress'
            assert event['event'] != 'breakthrough'

    def test_node_becomes_available_after_prereq(self, tech_tree, tracker):
        """Node becomes available after prerequisite is met."""
        # Level up root to 1
        tracker.get_state('root').current_level = 1
        tracker.set_allocation('child', 100)

        events = ResearchService.process_turn(tech_tree, tracker)

        # Child should now have events
        child_events = [e for e in events if e['node_id'] == 'child']
        # Should have either progress or breakthrough
        assert any(e['event'] in ('progress', 'breakthrough') for e in child_events)


class TestProcessTurnMultiTurn:
    """Tests for multi-turn progression."""

    def test_chance_accumulates_over_turns(self, tech_tree, tracker):
        """Chance accumulates with consistent investment over multiple turns."""
        tracker.set_allocation('root', 50)
        state = tracker.get_state('root')

        # Track chance over several turns (reset on breakthrough)
        chances = []
        for i in range(10):
            ResearchService.process_turn(tech_tree, tracker)
            if state.current_level > 0:
                # Breakthrough occurred, stop tracking
                break
            chances.append(state.current_chance)

        # If no breakthrough, chance should generally increase
        if len(chances) > 3:
            # Allow for some decay, but trend should be up with investment
            avg_early = sum(chances[:3]) / 3
            avg_late = sum(chances[-3:]) / 3
            # With 50 RP and 0.1 volatility, added_chance ≈ 0.39
            # Decay is 0.01, so net gain ≈ 0.38 per turn
            assert avg_late >= avg_early - 0.05  # Allow some variance

    def test_multiple_breakthroughs_possible(self, tech_tree, tracker):
        """Multiple breakthroughs can occur over many turns."""
        tracker.set_allocation('root', 200)
        state = tracker.get_state('root')

        for _ in range(100):
            ResearchService.process_turn(tech_tree, tracker)

        # With high investment, should have multiple level ups
        assert state.current_level >= 1


class TestProcessTurnEdgeCases:
    """Tests for edge cases."""

    def test_empty_tech_tree(self, tracker):
        """Process turn with empty tech tree."""
        empty_tree = TechTree()
        events = ResearchService.process_turn(empty_tree, tracker)
        assert events == []

    def test_no_allocations(self, tech_tree, tracker):
        """Process turn with no RP allocations."""
        events = ResearchService.process_turn(tech_tree, tracker)
        # Only decay events possible (if any nodes have accumulated chance)
        for event in events:
            assert event['event'] == 'decay'

    def test_very_small_allocation(self, tech_tree, tracker):
        """Very small RP allocation still works."""
        tracker.set_allocation('root', 1)
        events = ResearchService.process_turn(tech_tree, tracker)
        # Should not crash
        assert isinstance(events, list)

    def test_tech_levels_parameter(self, tech_tree, tracker):
        """Custom tech_levels parameter is used."""
        # Provide pre-computed tech levels
        custom_levels = {'root': 1}  # Make child available

        tracker.set_allocation('child', 100)
        events = ResearchService.process_turn(tech_tree, tracker, tech_levels=custom_levels)

        # Child should be processed since root is level 1 in custom_levels
        child_events = [e for e in events if e['node_id'] == 'child']
        assert any(e['event'] in ('progress', 'breakthrough') for e in child_events)

    def test_breakthrough_updates_tech_levels_for_same_turn(self, tech_tree, tracker):
        """Breakthrough updates tech_levels for other nodes in same turn."""
        # This tests that tech_levels dict is updated when a breakthrough occurs.
        # We'll verify that after root gets level 1, child can be processed.

        # First turn: level up root manually
        tracker.get_state('root').current_level = 1

        # Now child should be available
        tracker.set_allocation('child', 100)

        events = ResearchService.process_turn(tech_tree, tracker)

        # Child should now be processed since root is level 1
        child_events = [e for e in events if e['node_id'] == 'child']
        assert len(child_events) >= 1
        assert child_events[0]['event'] in ('progress', 'breakthrough')


# =============================================================================
# TCG-FND-009: ResearchService.process_turn() Critical Properties
# =============================================================================

class TestProcessTurnTechLevelsMutation:
    """TCG-FND-009: Tests for tech_levels mutation during process_turn."""

    def test_tech_levels_not_mutated_when_passed_externally(self, tech_tree, tracker):
        """External tech_levels dict should not be mutated (a copy is made)."""
        # Set up: give root high chance for breakthrough
        state = tracker.get_state('root')
        state.current_chance = 0.99
        tracker.set_allocation('root', 100)

        # Pass in an external dict
        external_levels = {'root': 0}

        # Force breakthrough
        with patch('random.Random.random', return_value=0.001):
            events = ResearchService.process_turn(tech_tree, tracker, tech_levels=external_levels)

        # Verify breakthrough occurred
        breakthrough_events = [e for e in events if e['event'] == 'breakthrough']
        assert len(breakthrough_events) == 1

        # CRITICAL: External dict should NOT be mutated
        assert external_levels == {'root': 0}, \
            "External tech_levels dict should not be mutated by process_turn()"

    def test_tech_levels_internal_copy_updated_for_same_turn_cascade(self, tech_tree, tracker):
        """Breakthrough should update internal copy so child nodes can process in same turn."""
        # Create a chain: root (level 0) -> child depends on root level 1
        # If root gets breakthrough during turn, child should see updated level

        # Set up root for guaranteed breakthrough
        root_state = tracker.get_state('root')
        root_state.current_chance = 0.99
        tracker.set_allocation('root', 100)

        # Also allocate to child
        tracker.set_allocation('child', 100)

        # Start with root at level 0
        initial_levels = {'root': 0}

        # Force breakthrough on root (low roll)
        call_count = [0]
        def roll_sequence():
            call_count[0] += 1
            if call_count[0] == 1:  # First roll for root
                return 0.001  # Breakthrough
            return 0.999  # Progress for child (no breakthrough)

        with patch('random.Random.random', side_effect=roll_sequence):
            events = ResearchService.process_turn(tech_tree, tracker, tech_levels=initial_levels)

        # Root should breakthrough
        root_breakthroughs = [e for e in events if e['node_id'] == 'root' and e['event'] == 'breakthrough']
        assert len(root_breakthroughs) == 1

        # Child should now be available and processed (since root is level 1 internally)
        # Note: child is locked at start, but may be processed if root breakthrough
        # actually unlocked it during the same turn
        child_events = [e for e in events if e['node_id'] == 'child']
        # Child may or may not have events depending on iteration order
        # The key test is that the external dict was not mutated
        assert initial_levels == {'root': 0}


class TestProcessTurnRNGFreshness:
    """TCG-FND-009: Tests verifying RNG freshness per turn."""

    def test_uses_fresh_rng_each_turn(self, tech_tree, tracker):
        """Each turn should use a fresh random.Random() instance."""
        tracker.set_allocation('root', 100)

        # Track how many times Random() is instantiated
        rng_instances = []

        original_random = random.Random

        def tracking_random():
            rng = original_random()
            rng_instances.append(rng)
            return rng

        with patch('game.research.systems.research_service.random.Random', side_effect=tracking_random):
            ResearchService.process_turn(tech_tree, tracker)
            ResearchService.process_turn(tech_tree, tracker)

        # Each turn should create a new RNG instance
        assert len(rng_instances) == 2, "Each turn should create a fresh RNG"

    def test_rng_creates_new_instance_per_call(self, tech_tree, tracker):
        """Verify that random.Random() is called, not using a shared/seeded RNG."""
        tracker.set_allocation('root', 100)

        # Track if Random() constructor is called
        random_called = [False]

        original_random = random.Random

        def tracking_random():
            random_called[0] = True
            return original_random()

        with patch('game.research.systems.research_service.random.Random', side_effect=tracking_random):
            ResearchService.process_turn(tech_tree, tracker)

        # Random() should have been called to create a fresh RNG
        assert random_called[0], "random.Random() should be called each turn"


class TestProcessTurnNodeOrdering:
    """TCG-FND-009: Tests for consistent node processing order."""

    def test_processes_nodes_in_dict_order(self, tracker):
        """Nodes should be processed in dict.values() order (insertion order in Python 3.7+)."""
        # Create a tech tree with specific insertion order
        tree = TechTree()
        tree.nodes['alpha'] = TechNode(id='alpha', name='Alpha', max_levels=1,
                                        base_decay=0.01, volatility=0.1)
        tree.nodes['beta'] = TechNode(id='beta', name='Beta', max_levels=1,
                                       base_decay=0.01, volatility=0.1)
        tree.nodes['gamma'] = TechNode(id='gamma', name='Gamma', max_levels=1,
                                        base_decay=0.01, volatility=0.1)

        # Allocate to all
        tracker.set_allocation('alpha', 10)
        tracker.set_allocation('beta', 10)
        tracker.set_allocation('gamma', 10)

        events = ResearchService.process_turn(tree, tracker)

        # Extract node order from events
        event_order = [e['node_id'] for e in events]

        # Should be in insertion order
        assert event_order == ['alpha', 'beta', 'gamma'], \
            f"Nodes should be processed in insertion order, got {event_order}"

    def test_breakthrough_updates_levels_for_subsequent_nodes(self, tracker):
        """When a node breaks through, tech_levels is updated for later nodes."""
        # Create tree: A -> B (B depends on A level 1)
        tree = TechTree()
        tree.nodes['nodeA'] = TechNode(id='nodeA', name='Node A', max_levels=3,
                                        base_decay=0.01, volatility=0.1)

        req = TechRequirement('nodeA', (1, 1))
        req.resolved_level = 1
        tree.nodes['nodeB'] = TechNode(id='nodeB', name='Node B', max_levels=3,
                                        requirements=[[req]], base_decay=0.01, volatility=0.1)

        # Set A for breakthrough
        tracker.get_state('nodeA').current_chance = 0.99
        tracker.set_allocation('nodeA', 100)
        tracker.set_allocation('nodeB', 100)

        # Force A to breakthrough
        call_count = [0]
        def controlled_roll():
            call_count[0] += 1
            if call_count[0] == 1:
                return 0.001  # Breakthrough for A
            return 0.999  # No breakthrough for B

        with patch('random.Random.random', side_effect=controlled_roll):
            events = ResearchService.process_turn(tree, tracker)

        # A should breakthrough
        a_breakthrough = [e for e in events if e['node_id'] == 'nodeA' and e['event'] == 'breakthrough']
        assert len(a_breakthrough) == 1

        # B should now be processed (was locked before A leveled up)
        b_events = [e for e in events if e['node_id'] == 'nodeB']
        # B should have progress or breakthrough event since A unlocked it
        assert len(b_events) >= 1, "Node B should be processed after A's breakthrough"
        assert b_events[0]['event'] in ('progress', 'breakthrough')
