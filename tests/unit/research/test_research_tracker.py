"""
Unit tests for ResearchTracker.

Tests cover:
- Initialization with various configurations
- Node state management
- RP allocation and budget tracking
- Serialization/deserialization
- Edge cases (empty state, corrupted data, missing keys)
"""
import pytest
from game.research.data.research_tracker import ResearchTracker, NodeState


class TestNodeState:
    """Tests for NodeState dataclass."""

    def test_default_initialization(self):
        """NodeState defaults to level 0, chance 0.0, allocation 0."""
        state = NodeState()
        assert state.current_level == 0
        assert state.current_chance == 0.0
        assert state.rp_allocation == 0

    def test_custom_initialization(self):
        """NodeState can be initialized with custom values."""
        state = NodeState(current_level=3, current_chance=0.5, rp_allocation=100)
        assert state.current_level == 3
        assert state.current_chance == 0.5
        assert state.rp_allocation == 100

    def test_to_dict_serialization(self):
        """NodeState can be serialized to a dictionary."""
        state = NodeState(current_level=2, current_chance=0.75, rp_allocation=50)
        data = state.to_dict()

        assert data == {
            'current_level': 2,
            'current_chance': 0.75,
            'rp_allocation': 50
        }

    def test_from_dict_deserialization(self):
        """NodeState can be deserialized from a dictionary."""
        data = {
            'current_level': 5,
            'current_chance': 0.33,
            'rp_allocation': 75
        }
        state = NodeState.from_dict(data)

        assert state.current_level == 5
        assert state.current_chance == 0.33
        assert state.rp_allocation == 75

    def test_from_dict_with_missing_keys(self):
        """NodeState uses defaults for missing keys."""
        state = NodeState.from_dict({})

        assert state.current_level == 0
        assert state.current_chance == 0.0
        assert state.rp_allocation == 0

    def test_from_dict_with_partial_data(self):
        """NodeState uses defaults for partially provided data."""
        data = {'current_level': 3}
        state = NodeState.from_dict(data)

        assert state.current_level == 3
        assert state.current_chance == 0.0
        assert state.rp_allocation == 0


class TestResearchTrackerInitialization:
    """Tests for ResearchTracker initialization."""

    def test_default_initialization(self):
        """ResearchTracker initializes with defaults."""
        tracker = ResearchTracker()

        assert tracker.node_states == {}
        assert tracker.rp_budget == ResearchTracker.DEFAULT_RP_BUDGET
        assert tracker.turn_number == 0
        assert tracker.turn_log == []
        assert tracker.auto_spread_enabled is False
        # Session seed should be set (random if not provided)
        assert isinstance(tracker.session_seed, int)

    def test_initialization_with_seed(self):
        """ResearchTracker uses provided session seed."""
        tracker = ResearchTracker(session_seed=42)
        assert tracker.session_seed == 42

    def test_initialization_generates_random_seed(self):
        """ResearchTracker generates random seed when none provided."""
        tracker1 = ResearchTracker()
        tracker2 = ResearchTracker()
        # Seeds could be same but highly unlikely
        # At minimum, both should be valid integers
        assert isinstance(tracker1.session_seed, int)
        assert isinstance(tracker2.session_seed, int)
        assert 0 <= tracker1.session_seed < 2**31
        assert 0 <= tracker2.session_seed < 2**31


class TestResearchTrackerNodeState:
    """Tests for node state management."""

    def test_get_state_creates_new_state(self, research_tracker):
        """get_state creates a new NodeState if node doesn't exist."""
        state = research_tracker.get_state('new_node')

        assert 'new_node' in research_tracker.node_states
        assert state.current_level == 0
        assert state.current_chance == 0.0
        assert state.rp_allocation == 0

    def test_get_state_returns_existing(self, populated_tracker):
        """get_state returns existing NodeState for known node."""
        state = populated_tracker.get_state('node_a')

        assert state.current_level == 1
        assert state.current_chance == 0.25
        assert state.rp_allocation == 50

    def test_get_all_tech_levels(self, populated_tracker):
        """get_all_tech_levels returns mapping of node_id to level."""
        levels = populated_tracker.get_all_tech_levels()

        assert levels == {
            'node_a': 1,
            'node_b': 0,
            'node_c': 2
        }

    def test_get_all_tech_levels_empty(self, research_tracker):
        """get_all_tech_levels returns empty dict for new tracker."""
        levels = research_tracker.get_all_tech_levels()
        assert levels == {}


class TestResearchTrackerRPAllocation:
    """Tests for RP allocation and budget management."""

    def test_get_total_allocated(self, populated_tracker):
        """get_total_allocated sums all node allocations."""
        # node_a: 50, node_b: 30, node_c: 0
        assert populated_tracker.get_total_allocated() == 80

    def test_get_total_allocated_empty(self, research_tracker):
        """get_total_allocated returns 0 for new tracker."""
        assert research_tracker.get_total_allocated() == 0

    def test_get_remaining_rp(self, populated_tracker):
        """get_remaining_rp returns budget minus allocated."""
        # Budget 200, allocated 80
        assert populated_tracker.get_remaining_rp() == 120

    def test_get_remaining_rp_full_budget(self, research_tracker):
        """get_remaining_rp returns full budget when nothing allocated."""
        assert research_tracker.get_remaining_rp() == 200

    def test_set_allocation_success(self, research_tracker):
        """set_allocation sets RP for a node."""
        result = research_tracker.set_allocation('test_node', 100)

        assert result is True
        assert research_tracker.get_state('test_node').rp_allocation == 100

    def test_set_allocation_exceeds_budget(self, research_tracker):
        """set_allocation clamps to available RP when exceeding budget."""
        # Budget is 200, try to allocate 300
        result = research_tracker.set_allocation('test_node', 300)

        assert result is False  # Could not allocate full amount
        assert research_tracker.get_state('test_node').rp_allocation == 200

    def test_set_allocation_negative_clamped(self, research_tracker):
        """set_allocation clamps negative values to 0."""
        result = research_tracker.set_allocation('test_node', -50)

        assert result is False
        assert research_tracker.get_state('test_node').rp_allocation == 0

    def test_set_allocation_updates_remaining(self, research_tracker):
        """set_allocation affects remaining RP correctly."""
        research_tracker.set_allocation('node1', 50)
        assert research_tracker.get_remaining_rp() == 150

        research_tracker.set_allocation('node2', 100)
        assert research_tracker.get_remaining_rp() == 50

    def test_set_allocation_replace_existing(self, populated_tracker):
        """set_allocation can replace existing allocation."""
        # node_a has 50 allocated
        populated_tracker.set_allocation('node_a', 100)

        assert populated_tracker.get_state('node_a').rp_allocation == 100
        # Total should increase by 50 (node_a: 100, node_b: 30, node_c: 0)
        assert populated_tracker.get_total_allocated() == 130

    def test_clear_allocation(self, populated_tracker):
        """clear_allocation sets node allocation to 0."""
        populated_tracker.clear_allocation('node_a')

        assert populated_tracker.get_state('node_a').rp_allocation == 0
        assert populated_tracker.get_total_allocated() == 30  # Only node_b

    def test_clear_allocation_nonexistent_node(self, research_tracker):
        """clear_allocation does nothing for nonexistent node."""
        # Should not raise
        research_tracker.clear_allocation('nonexistent')
        assert research_tracker.get_total_allocated() == 0

    def test_clear_all_allocations(self, populated_tracker):
        """clear_all_allocations sets all allocations to 0."""
        populated_tracker.clear_all_allocations()

        assert populated_tracker.get_total_allocated() == 0
        assert populated_tracker.get_state('node_a').rp_allocation == 0
        assert populated_tracker.get_state('node_b').rp_allocation == 0

    def test_get_nodes_with_allocation(self, populated_tracker):
        """get_nodes_with_allocation returns nodes with non-zero allocation."""
        nodes = populated_tracker.get_nodes_with_allocation()

        assert set(nodes) == {'node_a', 'node_b'}
        assert 'node_c' not in nodes  # node_c has 0 allocation

    def test_get_nodes_with_allocation_empty(self, research_tracker):
        """get_nodes_with_allocation returns empty list for new tracker."""
        assert research_tracker.get_nodes_with_allocation() == []


class TestResearchTrackerBudget:
    """Tests for RP budget management."""

    def test_set_rp_budget(self, research_tracker):
        """set_rp_budget sets the budget."""
        research_tracker.set_rp_budget(300)
        assert research_tracker.rp_budget == 300

    def test_set_rp_budget_clamps_to_min(self, research_tracker):
        """set_rp_budget clamps to minimum."""
        research_tracker.set_rp_budget(10)  # Below MIN_RP_BUDGET
        assert research_tracker.rp_budget == ResearchTracker.MIN_RP_BUDGET

    def test_set_rp_budget_clamps_to_max(self, research_tracker):
        """set_rp_budget clamps to maximum."""
        research_tracker.set_rp_budget(1000)  # Above MAX_RP_BUDGET
        assert research_tracker.rp_budget == ResearchTracker.MAX_RP_BUDGET

    def test_budget_constants(self):
        """Budget constants are defined correctly."""
        assert ResearchTracker.MIN_RP_BUDGET == 50
        assert ResearchTracker.MAX_RP_BUDGET == 500
        assert ResearchTracker.DEFAULT_RP_BUDGET == 200


class TestResearchTrackerTurnManagement:
    """Tests for turn tracking."""

    def test_increment_turn(self, research_tracker):
        """increment_turn increases turn counter."""
        assert research_tracker.turn_number == 0

        research_tracker.increment_turn()
        assert research_tracker.turn_number == 1

        research_tracker.increment_turn()
        assert research_tracker.turn_number == 2

    def test_set_turn_log(self, research_tracker):
        """set_turn_log stores events."""
        events = [
            {'type': 'breakthrough', 'node': 'node_a'},
            {'type': 'level_up', 'node': 'node_b'}
        ]
        research_tracker.set_turn_log(events)

        assert research_tracker.turn_log == events

    def test_set_turn_log_replaces(self, research_tracker):
        """set_turn_log replaces existing log."""
        research_tracker.set_turn_log([{'old': 'event'}])
        research_tracker.set_turn_log([{'new': 'event'}])

        assert research_tracker.turn_log == [{'new': 'event'}]


class TestResearchTrackerSpreadRP:
    """Tests for RP spreading functionality."""

    def test_spread_rp_evenly(self, research_tracker, mock_tech_tree):
        """spread_rp_evenly distributes RP across available nodes."""
        count = research_tracker.spread_rp_evenly(mock_tech_tree)

        # Only node_a and node_b are available
        assert count == 2
        assert research_tracker.get_state('node_a').rp_allocation == 100
        assert research_tracker.get_state('node_b').rp_allocation == 100

    def test_spread_rp_evenly_clears_previous(self, populated_tracker, mock_tech_tree):
        """spread_rp_evenly clears previous allocations first."""
        populated_tracker.spread_rp_evenly(mock_tech_tree)

        # Previous allocations should be cleared and redistributed
        total = populated_tracker.get_total_allocated()
        assert total == populated_tracker.rp_budget

    def test_spread_rp_evenly_handles_remainder(self, research_tracker, mock_tech_tree):
        """spread_rp_evenly distributes remainder to first N nodes."""
        research_tracker.set_rp_budget(201)  # Not evenly divisible by 2
        research_tracker.spread_rp_evenly(mock_tech_tree)

        # 201 / 2 = 100 with remainder 1
        alloc_a = research_tracker.get_state('node_a').rp_allocation
        alloc_b = research_tracker.get_state('node_b').rp_allocation

        assert alloc_a + alloc_b == 201
        assert alloc_a == 101  # First node gets the remainder
        assert alloc_b == 100

    def test_spread_rp_evenly_no_available_nodes(self, research_tracker):
        """spread_rp_evenly returns 0 when no nodes available."""
        from unittest.mock import MagicMock

        tree = MagicMock()
        tree.nodes = {}  # No nodes

        count = research_tracker.spread_rp_evenly(tree)
        assert count == 0

    def test_spread_rp_skips_locked_and_completed(self, research_tracker, mock_tech_tree):
        """spread_rp_evenly only allocates to 'available' nodes."""
        count = research_tracker.spread_rp_evenly(mock_tech_tree)

        # node_c is completed, node_d is locked - should be skipped
        assert 'node_c' not in research_tracker.get_nodes_with_allocation()
        assert 'node_d' not in research_tracker.get_nodes_with_allocation()


class TestResearchTrackerSerialization:
    """Tests for save/load functionality."""

    def test_to_dict(self, populated_tracker):
        """to_dict serializes tracker state."""
        populated_tracker.turn_number = 5
        populated_tracker.auto_spread_enabled = True

        data = populated_tracker.to_dict()

        assert data['session_seed'] == 12345
        assert data['rp_budget'] == 200
        assert data['turn_number'] == 5
        assert data['auto_spread_enabled'] is True
        assert 'node_a' in data['node_states']
        assert data['node_states']['node_a']['current_level'] == 1

    def test_from_dict(self):
        """from_dict deserializes tracker state."""
        data = {
            'session_seed': 99999,
            'rp_budget': 300,
            'turn_number': 10,
            'auto_spread_enabled': True,
            'node_states': {
                'test_node': {
                    'current_level': 3,
                    'current_chance': 0.5,
                    'rp_allocation': 75
                }
            }
        }

        tracker = ResearchTracker.from_dict(data)

        assert tracker.session_seed == 99999
        assert tracker.rp_budget == 300
        assert tracker.turn_number == 10
        assert tracker.auto_spread_enabled is True
        assert tracker.get_state('test_node').current_level == 3

    def test_from_dict_empty(self):
        """from_dict handles empty data with defaults."""
        tracker = ResearchTracker.from_dict({})

        assert tracker.rp_budget == ResearchTracker.DEFAULT_RP_BUDGET
        assert tracker.turn_number == 0
        assert tracker.auto_spread_enabled is False
        assert tracker.node_states == {}

    def test_round_trip(self, populated_tracker):
        """Serialization round-trip preserves state."""
        populated_tracker.turn_number = 7
        populated_tracker.auto_spread_enabled = True

        data = populated_tracker.to_dict()
        restored = ResearchTracker.from_dict(data)

        assert restored.session_seed == populated_tracker.session_seed
        assert restored.rp_budget == populated_tracker.rp_budget
        assert restored.turn_number == populated_tracker.turn_number
        assert restored.auto_spread_enabled == populated_tracker.auto_spread_enabled
        assert restored.get_all_tech_levels() == populated_tracker.get_all_tech_levels()
        assert restored.get_total_allocated() == populated_tracker.get_total_allocated()


class TestResearchTrackerReset:
    """Tests for reset functionality."""

    def test_reset_clears_state(self, populated_tracker):
        """reset clears nodes, turn number, and log but keeps seed and budget."""
        populated_tracker.turn_number = 10
        populated_tracker.turn_log = [{'event': 'test'}]
        original_seed = populated_tracker.session_seed
        original_budget = populated_tracker.rp_budget

        populated_tracker.reset()

        assert populated_tracker.node_states == {}
        assert populated_tracker.turn_number == 0
        assert populated_tracker.turn_log == []
        assert populated_tracker.session_seed == original_seed
        assert populated_tracker.rp_budget == original_budget


class TestResearchTrackerEdgeCases:
    """Tests for edge cases and error handling."""

    def test_allocation_to_zero_remaining(self, research_tracker):
        """Allocation when budget is exhausted."""
        research_tracker.set_allocation('node1', 200)  # Use full budget

        result = research_tracker.set_allocation('node2', 50)

        assert result is False
        assert research_tracker.get_state('node2').rp_allocation == 0

    def test_reallocation_frees_rp(self, research_tracker):
        """Reducing allocation frees RP for other nodes."""
        research_tracker.set_allocation('node1', 150)
        research_tracker.set_allocation('node2', 50)  # Uses remaining 50

        # Now reduce node1's allocation
        research_tracker.set_allocation('node1', 100)

        # 50 RP should now be free
        assert research_tracker.get_remaining_rp() == 50

        # Can now allocate more to node2
        research_tracker.set_allocation('node2', 100)
        assert research_tracker.get_state('node2').rp_allocation == 100

    def test_from_dict_ignores_unknown_keys(self):
        """from_dict ignores unknown keys in data."""
        data = {
            'session_seed': 123,
            'unknown_key': 'should be ignored',
            'another_unknown': [1, 2, 3]
        }

        tracker = ResearchTracker.from_dict(data)
        assert tracker.session_seed == 123
        # Should not raise or cause issues

    def test_node_state_from_dict_ignores_unknown_keys(self):
        """NodeState.from_dict ignores unknown keys."""
        data = {
            'current_level': 2,
            'unknown_field': 'ignored'
        }

        state = NodeState.from_dict(data)
        assert state.current_level == 2


# =============================================================================
# TCG-FND-019: spread_rp_evenly with Pre-Computed tech_levels
# =============================================================================

class TestSpreadRPEvenlyPrecomputedTechLevels:
    """TCG-FND-019: Tests for spread_rp_evenly() with pre-computed tech_levels.

    The method accepts an optional tech_levels parameter for performance.
    All existing tests call it without this parameter, always using the
    default path that calls get_all_tech_levels(). These tests verify
    the pre-computed path works correctly.
    """

    def test_spread_rp_with_precomputed_tech_levels_matches_auto(self, research_tracker, mock_tech_tree):
        """Pre-computed tech_levels produces same result as automatic path."""
        # First, use automatic path
        count_auto = research_tracker.spread_rp_evenly(mock_tech_tree)
        alloc_a_auto = research_tracker.get_state('node_a').rp_allocation
        alloc_b_auto = research_tracker.get_state('node_b').rp_allocation

        # Reset allocations
        research_tracker.clear_all_allocations()

        # Now use pre-computed tech_levels
        tech_levels = research_tracker.get_all_tech_levels()
        count_precomputed = research_tracker.spread_rp_evenly(mock_tech_tree, tech_levels=tech_levels)
        alloc_a_precomputed = research_tracker.get_state('node_a').rp_allocation
        alloc_b_precomputed = research_tracker.get_state('node_b').rp_allocation

        # Results should be identical
        assert count_auto == count_precomputed
        assert alloc_a_auto == alloc_a_precomputed
        assert alloc_b_auto == alloc_b_precomputed

    def test_spread_rp_with_explicit_tech_levels_dict(self, research_tracker, mock_tech_tree):
        """spread_rp_evenly uses provided tech_levels dict."""
        # Provide explicit tech_levels
        explicit_tech_levels = {
            'node_a': 0,
            'node_b': 0,
            'node_c': 5,  # Completed
            'node_d': 0   # Locked
        }

        count = research_tracker.spread_rp_evenly(mock_tech_tree, tech_levels=explicit_tech_levels)

        # Should still distribute to available nodes
        assert count == 2
        assert research_tracker.get_state('node_a').rp_allocation == 100
        assert research_tracker.get_state('node_b').rp_allocation == 100

    def test_spread_rp_with_empty_tech_levels_dict(self, research_tracker, mock_tech_tree):
        """spread_rp_evenly with empty tech_levels dict still works."""
        # Empty dict - node.get_status will be called with empty tech_levels
        count = research_tracker.spread_rp_evenly(mock_tech_tree, tech_levels={})

        # Mock nodes return hardcoded status values, so result should be same
        assert count == 2

    def test_precomputed_tech_levels_avoids_get_all_tech_levels(self, research_tracker, mock_tech_tree):
        """Pre-computed tech_levels avoids calling get_all_tech_levels()."""
        from unittest.mock import patch

        tech_levels = {'node_a': 1, 'node_b': 2}

        with patch.object(research_tracker, 'get_all_tech_levels') as mock_get:
            research_tracker.spread_rp_evenly(mock_tech_tree, tech_levels=tech_levels)

            # get_all_tech_levels should NOT be called
            mock_get.assert_not_called()

    def test_default_path_calls_get_all_tech_levels(self, research_tracker, mock_tech_tree):
        """Default path (no tech_levels) calls get_all_tech_levels()."""
        from unittest.mock import patch

        with patch.object(research_tracker, 'get_all_tech_levels', return_value={}) as mock_get:
            research_tracker.spread_rp_evenly(mock_tech_tree)

            # get_all_tech_levels SHOULD be called
            mock_get.assert_called_once()

    def test_precomputed_with_populated_tracker(self, populated_tracker, mock_tech_tree):
        """Pre-computed tech_levels works with populated tracker."""
        # Get the current tech levels from populated tracker
        tech_levels = populated_tracker.get_all_tech_levels()

        # Should have levels from the populated state
        assert tech_levels['node_a'] == 1
        assert tech_levels['node_b'] == 0
        assert tech_levels['node_c'] == 2

        # Spread with pre-computed levels
        count = populated_tracker.spread_rp_evenly(mock_tech_tree, tech_levels=tech_levels)

        # Should work correctly
        assert count == 2
        assert populated_tracker.get_total_allocated() == populated_tracker.rp_budget

    def test_precomputed_tech_levels_passed_to_get_status(self, research_tracker):
        """Verify tech_levels is actually passed to node.get_status()."""
        from unittest.mock import MagicMock, call

        # Create a tree with a single node that we can inspect
        tree = MagicMock()
        node = MagicMock()
        node.id = 'test_node'
        node.get_status.return_value = 'available'
        tree.nodes = {'test_node': node}

        explicit_levels = {'test_node': 5, 'other_node': 3}

        research_tracker.spread_rp_evenly(tree, tech_levels=explicit_levels)

        # Verify get_status was called with our explicit tech_levels
        node.get_status.assert_called()
        # The second argument to get_status should be our tech_levels
        call_args = node.get_status.call_args
        assert call_args[0][1] == explicit_levels
