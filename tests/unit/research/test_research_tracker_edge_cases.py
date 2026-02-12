"""
Unit tests for ResearchTracker serialization edge cases.

Tests NodeState and ResearchTracker serialization round-trips,
default value handling, and session seed consistency.
"""
import pytest

from game.research.data.research_tracker import NodeState, ResearchTracker


class TestNodeStateSerialization:
    """Tests for NodeState serialization edge cases."""

    def test_node_state_roundtrip(self):
        """from_dict(to_dict()) preserves all fields."""
        original = NodeState(
            current_level=5,
            current_chance=0.75,
            rp_allocation=150
        )

        serialized = original.to_dict()
        restored = NodeState.from_dict(serialized)

        assert restored.current_level == original.current_level
        assert restored.current_chance == original.current_chance
        assert restored.rp_allocation == original.rp_allocation

    def test_node_state_from_dict_defaults(self):
        """Missing keys use default values (0, 0.0, 0)."""
        # Empty dict should use all defaults
        state = NodeState.from_dict({})

        assert state.current_level == 0
        assert state.current_chance == 0.0
        assert state.rp_allocation == 0

    def test_node_state_from_dict_partial_data(self):
        """Partial data uses defaults for missing fields."""
        state = NodeState.from_dict({'current_level': 3})

        assert state.current_level == 3
        assert state.current_chance == 0.0  # default
        assert state.rp_allocation == 0  # default

    def test_node_state_zero_rp(self):
        """rp_allocation=0 serializes correctly."""
        state = NodeState(current_level=2, current_chance=0.5, rp_allocation=0)

        serialized = state.to_dict()
        restored = NodeState.from_dict(serialized)

        assert restored.rp_allocation == 0

    def test_node_state_max_chance(self):
        """current_chance=0.95 preserved after round-trip."""
        state = NodeState(current_level=10, current_chance=0.95, rp_allocation=100)

        serialized = state.to_dict()
        restored = NodeState.from_dict(serialized)

        assert restored.current_chance == 0.95


class TestResearchTrackerSerialization:
    """Tests for ResearchTracker serialization edge cases."""

    def test_tracker_roundtrip_empty_states(self):
        """Empty node_states dict preserved after round-trip."""
        tracker = ResearchTracker(session_seed=12345)
        tracker.rp_budget = 300
        tracker.turn_number = 5
        # No node states added

        serialized = tracker.to_dict()
        restored = ResearchTracker.from_dict(serialized)

        assert restored.session_seed == 12345
        assert restored.rp_budget == 300
        assert restored.turn_number == 5
        assert len(restored.node_states) == 0

    def test_tracker_roundtrip_with_states(self):
        """Multiple node states preserved after round-trip."""
        tracker = ResearchTracker(session_seed=54321)
        tracker.rp_budget = 250

        # Add some node states
        tracker.get_state("node_a").current_level = 2
        tracker.get_state("node_a").current_chance = 0.3
        tracker.get_state("node_a").rp_allocation = 50

        tracker.get_state("node_b").current_level = 5
        tracker.get_state("node_b").current_chance = 0.8
        tracker.get_state("node_b").rp_allocation = 100

        serialized = tracker.to_dict()
        restored = ResearchTracker.from_dict(serialized)

        assert len(restored.node_states) == 2
        assert restored.node_states["node_a"].current_level == 2
        assert restored.node_states["node_a"].current_chance == 0.3
        assert restored.node_states["node_a"].rp_allocation == 50
        assert restored.node_states["node_b"].current_level == 5
        assert restored.node_states["node_b"].current_chance == 0.8
        assert restored.node_states["node_b"].rp_allocation == 100

    def test_session_seed_consistency(self):
        """Same seed produces deterministic tracker."""
        seed = 999

        tracker1 = ResearchTracker(session_seed=seed)
        tracker2 = ResearchTracker(session_seed=seed)

        assert tracker1.session_seed == tracker2.session_seed == seed

    def test_session_seed_from_dict_preserved(self):
        """Session seed is preserved through serialization."""
        original_seed = 123456789

        tracker = ResearchTracker(session_seed=original_seed)
        serialized = tracker.to_dict()
        restored = ResearchTracker.from_dict(serialized)

        assert restored.session_seed == original_seed

    def test_auto_spread_enabled_roundtrip(self):
        """auto_spread_enabled flag preserved."""
        tracker = ResearchTracker(session_seed=111)
        tracker.auto_spread_enabled = True

        serialized = tracker.to_dict()
        restored = ResearchTracker.from_dict(serialized)

        assert restored.auto_spread_enabled is True

    def test_tracker_from_dict_defaults(self):
        """Missing fields in data use defaults."""
        # Minimal data - just seed
        data = {'session_seed': 42}

        tracker = ResearchTracker.from_dict(data)

        assert tracker.session_seed == 42
        assert tracker.rp_budget == ResearchTracker.DEFAULT_RP_BUDGET
        assert tracker.turn_number == 0
        assert tracker.auto_spread_enabled is False
        assert len(tracker.node_states) == 0
