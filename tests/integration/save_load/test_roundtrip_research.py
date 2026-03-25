"""Round-trip tests for NodeState and ResearchTracker serialization (PROJ-223 Phase 2+3)."""

import pytest

from game.research.data.research_tracker import NodeState, ResearchTracker
from tests.fixtures.strategy_entities import create_test_node_state, create_test_research_tracker
from tests.integration.save_load.conftest import assert_round_trip_fidelity


class TestNodeStateRoundTrip:
    """NodeState round-trip serialization tests."""

    def test_to_dict_includes_all_3_fields(self):
        ns = create_test_node_state()
        d = ns.to_dict()
        assert 'current_level' in d
        assert 'current_chance' in d
        assert 'rp_allocation' in d

    def test_from_dict_restores_all_fields(self):
        original = create_test_node_state(current_level=3, current_chance=0.45, rp_allocation=80)
        d = original.to_dict()
        restored = NodeState.from_dict(d)
        assert restored.current_level == 3
        assert restored.current_chance == 0.45
        assert restored.rp_allocation == 80

    def test_round_trip_field_level(self):
        assert_round_trip_fidelity(create_test_node_state(), NodeState)

    def test_defaults_for_missing_fields(self):
        restored = NodeState.from_dict({})
        assert restored.current_level == 0
        assert restored.current_chance == 0.0
        assert restored.rp_allocation == 0


# =============================================================================
# Phase 3: ResearchTracker compound round-trip tests
# =============================================================================

class TestResearchTrackerRoundTrip:
    """ResearchTracker compound round-trip serialization tests."""

    def test_all_fields_preserved(self):
        rt = create_test_research_tracker()
        restored = assert_round_trip_fidelity(rt, ResearchTracker)
        assert restored.session_seed == rt.session_seed
        assert restored.rp_budget == rt.rp_budget
        assert restored.turn_number == rt.turn_number
        assert restored.auto_spread_enabled == rt.auto_spread_enabled

    def test_node_states_with_multiple_entries(self):
        rt = create_test_research_tracker()
        restored = assert_round_trip_fidelity(rt, ResearchTracker)
        assert len(restored.node_states) == len(rt.node_states)
        for node_id, orig_state in rt.node_states.items():
            rest_state = restored.node_states[node_id]
            assert rest_state.current_level == orig_state.current_level
            assert rest_state.current_chance == orig_state.current_chance
            assert rest_state.rp_allocation == orig_state.rp_allocation

    def test_empty_tracker_round_trip(self):
        rt = ResearchTracker(session_seed=99)
        restored = assert_round_trip_fidelity(rt, ResearchTracker)
        assert restored.session_seed == 99
        assert len(restored.node_states) == 0
        assert restored.rp_budget == ResearchTracker.DEFAULT_RP_BUDGET
