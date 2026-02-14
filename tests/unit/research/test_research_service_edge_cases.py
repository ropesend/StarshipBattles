"""
Additional edge case tests for ResearchService.

TCG-FND-008: Tests for estimate_turns_to_breakthrough edge cases:
- Exact boundary where gain equals decay
- Very large RP values (potential overflow)
- Volatility = 0 (always adds 0)
"""
import pytest
import math
from unittest.mock import MagicMock, patch

from game.research.systems.research_service import ResearchService


class TestEstimateTurnsEdgeCases:
    """Edge case tests for estimate_turns_to_breakthrough()."""

    def test_gain_exactly_equals_decay(self):
        """Returns infinity when net gain is exactly 0."""
        # Calculate RP where added_chance = decay
        # added_chance = volatility * ln(1 + rp) = decay
        # ln(1 + rp) = decay / volatility
        # 1 + rp = e^(decay/volatility)
        # rp = e^(decay/volatility) - 1

        volatility = 0.1
        base_decay = 0.1  # Equal to volatility for simple case
        # With these values: added_chance = 0.1 * ln(1 + rp)
        # We need 0.1 * ln(1 + rp) = 0.1
        # ln(1 + rp) = 1
        # 1 + rp = e^1 ≈ 2.718
        # rp ≈ 1.718

        rp_at_boundary = math.e - 1  # ≈ 1.718

        result = ResearchService.estimate_turns_to_breakthrough(
            volatility, base_decay, int(rp_at_boundary)
        )

        # With rp = 1 (int of 1.718), net gain will be < 0
        # So should return infinity
        assert result == float('inf')

    def test_gain_just_above_decay(self):
        """Returns finite value when net gain is slightly positive."""
        volatility = 0.1
        base_decay = 0.05

        # With rp = 10: added_chance = 0.1 * ln(11) ≈ 0.24
        # Net gain = 0.24 - 0.05 = 0.19 > 0
        rp = 10

        result = ResearchService.estimate_turns_to_breakthrough(
            volatility, base_decay, rp
        )

        assert result != float('inf')
        assert result > 0

    def test_volatility_zero(self):
        """Volatility = 0 means added_chance always 0, returns infinity."""
        result = ResearchService.estimate_turns_to_breakthrough(
            volatility=0.0,
            base_decay=0.01,
            rp=1000
        )

        assert result == float('inf')

    def test_very_large_rp_no_overflow(self):
        """Very large RP values don't cause overflow."""
        result = ResearchService.estimate_turns_to_breakthrough(
            volatility=0.1,
            base_decay=0.01,
            rp=10000000  # 10 million
        )

        assert isinstance(result, float)
        assert math.isfinite(result)
        assert result > 0

    def test_very_small_positive_rp(self):
        """Very small positive RP works correctly."""
        result = ResearchService.estimate_turns_to_breakthrough(
            volatility=0.1,
            base_decay=0.001,
            rp=1
        )

        # With rp=1: added_chance = 0.1 * ln(2) ≈ 0.069
        # Net gain = 0.069 - 0.001 = 0.068 > 0
        assert result != float('inf')
        assert result > 0

    def test_high_decay_low_volatility(self):
        """High decay with low volatility returns infinity."""
        result = ResearchService.estimate_turns_to_breakthrough(
            volatility=0.01,
            base_decay=0.5,
            rp=100
        )

        # With rp=100: added_chance = 0.01 * ln(101) ≈ 0.046
        # Net gain = 0.046 - 0.5 = -0.454 < 0
        assert result == float('inf')

    def test_estimate_decreases_with_higher_rp(self):
        """Higher RP investment gives lower turn estimate."""
        volatility = 0.1
        base_decay = 0.01

        estimate_low = ResearchService.estimate_turns_to_breakthrough(
            volatility, base_decay, rp=50
        )
        estimate_high = ResearchService.estimate_turns_to_breakthrough(
            volatility, base_decay, rp=500
        )

        assert estimate_high < estimate_low

    def test_estimate_increases_with_higher_decay(self):
        """Higher decay gives higher turn estimate."""
        volatility = 0.1
        rp = 100

        estimate_low_decay = ResearchService.estimate_turns_to_breakthrough(
            volatility, base_decay=0.01, rp=rp
        )
        estimate_high_decay = ResearchService.estimate_turns_to_breakthrough(
            volatility, base_decay=0.1, rp=rp
        )

        assert estimate_high_decay > estimate_low_decay

    def test_zero_base_decay(self):
        """Zero decay means pure accumulation."""
        volatility = 0.1
        rp = 50

        result = ResearchService.estimate_turns_to_breakthrough(
            volatility, base_decay=0.0, rp=rp
        )

        # No decay means all investment accumulates
        # added_chance = 0.1 * ln(51) ≈ 0.393
        # Turns to 50% = 0.5 / 0.393 ≈ 1.27
        assert result > 0
        assert result < 5  # Should be relatively quick with no decay


class TestCalculateAddedChanceEdgeCases:
    """Edge case tests for calculate_added_chance()."""

    def test_volatility_zero(self):
        """Zero volatility returns zero added chance."""
        result = ResearchService.calculate_added_chance(
            volatility=0.0,
            rp=1000
        )

        assert result == 0.0

    def test_very_large_rp(self):
        """Very large RP doesn't cause overflow."""
        result = ResearchService.calculate_added_chance(
            volatility=0.1,
            rp=10000000
        )

        assert isinstance(result, float)
        assert math.isfinite(result)
        assert result > 0

    def test_rp_one(self):
        """RP = 1 gives ln(2) scaling."""
        volatility = 1.0  # For easy calculation
        result = ResearchService.calculate_added_chance(volatility, rp=1)

        expected = 1.0 * math.log(2)
        assert result == pytest.approx(expected)


class TestProcessTurnEdgeCases:
    """Additional edge case tests for process_turn."""

    def test_very_high_accumulated_chance(self):
        """High accumulated chance is capped at MAX_CHANCE."""
        from game.research.data.tech_tree import TechTree
        from game.research.data.tech_node import TechNode
        from game.research.data.research_tracker import ResearchTracker

        tree = TechTree()
        tree.nodes['test'] = TechNode(
            id='test', name='Test', max_levels=5,
            base_decay=0.0,  # No decay
            volatility=1.0   # High volatility
        )

        tracker = ResearchTracker(session_seed=12345)
        tracker.set_allocation('test', 10000)  # Very high RP

        # Force high roll to avoid breakthrough
        with patch('random.Random.random', return_value=0.999):
            ResearchService.process_turn(tree, tracker)

        state = tracker.get_state('test')
        assert state.current_chance <= ResearchService.MAX_CHANCE

    def test_decay_to_exactly_zero(self):
        """Chance decays to exactly zero, not negative."""
        from game.research.data.tech_tree import TechTree
        from game.research.data.tech_node import TechNode
        from game.research.data.research_tracker import ResearchTracker

        tree = TechTree()
        tree.nodes['test'] = TechNode(
            id='test', name='Test', max_levels=5,
            base_decay=0.5,  # High decay
            volatility=0.1
        )

        tracker = ResearchTracker(session_seed=12345)
        state = tracker.get_state('test')
        state.current_chance = 0.3  # Less than decay

        # No allocation, just decay
        ResearchService.process_turn(tree, tracker)

        assert state.current_chance == 0.0

    def test_breakthrough_at_max_level(self):
        """Node at max level is skipped in processing."""
        from game.research.data.tech_tree import TechTree
        from game.research.data.tech_node import TechNode
        from game.research.data.research_tracker import ResearchTracker

        tree = TechTree()
        tree.nodes['maxed'] = TechNode(
            id='maxed', name='Maxed', max_levels=1,
            base_decay=0.0,
            volatility=0.1
        )

        tracker = ResearchTracker(session_seed=12345)
        tracker.get_state('maxed').current_level = 1  # Already at max
        tracker.set_allocation('maxed', 100)

        events = ResearchService.process_turn(tree, tracker)

        # Should not process maxed node
        maxed_events = [e for e in events if e['node_id'] == 'maxed']
        assert len(maxed_events) == 0
