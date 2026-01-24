"""
Unit tests for TechNode and TechRequirement.

Tests cover:
- TechRequirement fuzzy resolution and checking
- TechNode construction and validation
- Prerequisite checking logic
- Unlock conditions evaluation
- Cost/price calculations with different curves
- Node state transitions (locked -> available -> completed)
- Edge cases: circular dependencies, missing prerequisites
"""
import pytest
import random
import math
from game.research.data.tech_node import TechNode, TechRequirement


class TestTechRequirement:
    """Tests for TechRequirement dataclass."""

    def test_default_initialization(self):
        """TechRequirement initializes with node_id and level_range."""
        req = TechRequirement(node_id='test_node', level_range=(1, 3))

        assert req.node_id == 'test_node'
        assert req.level_range == (1, 3)
        assert req.resolved_level is None

    def test_resolve_sets_fixed_level(self):
        """resolve() sets resolved_level within range."""
        req = TechRequirement(node_id='test_node', level_range=(2, 5))
        rng = random.Random(42)

        result = req.resolve(rng)

        assert req.resolved_level is not None
        assert 2 <= req.resolved_level <= 5
        assert result == req.resolved_level

    def test_resolve_deterministic_with_same_seed(self):
        """resolve() produces same result with same seed."""
        req1 = TechRequirement(node_id='test_node', level_range=(1, 10))
        req2 = TechRequirement(node_id='test_node', level_range=(1, 10))

        rng1 = random.Random(12345)
        rng2 = random.Random(12345)

        result1 = req1.resolve(rng1)
        result2 = req2.resolve(rng2)

        assert result1 == result2

    def test_resolve_single_value_range(self):
        """resolve() with single value range always returns that value."""
        req = TechRequirement(node_id='test_node', level_range=(3, 3))
        rng = random.Random(99999)

        result = req.resolve(rng)

        assert result == 3
        assert req.resolved_level == 3

    def test_is_met_with_resolved_level(self):
        """is_met() uses resolved_level when available."""
        req = TechRequirement(node_id='prereq', level_range=(1, 5))
        req.resolved_level = 3

        # Level 3 or higher should pass
        assert req.is_met({'prereq': 3}) is True
        assert req.is_met({'prereq': 5}) is True
        assert req.is_met({'prereq': 2}) is False

    def test_is_met_without_resolved_level(self):
        """is_met() uses minimum of level_range when not resolved."""
        req = TechRequirement(node_id='prereq', level_range=(2, 5))
        # Not resolved, so should use level_range[0] = 2

        assert req.is_met({'prereq': 2}) is True
        assert req.is_met({'prereq': 5}) is True
        assert req.is_met({'prereq': 1}) is False

    def test_is_met_missing_node(self):
        """is_met() treats missing nodes as level 0."""
        req = TechRequirement(node_id='prereq', level_range=(1, 3))
        req.resolved_level = 1

        # prereq not in tech_levels, defaults to 0
        assert req.is_met({}) is False
        assert req.is_met({'other_node': 5}) is False

    def test_is_met_zero_requirement(self):
        """is_met() with level 0 requirement always passes."""
        req = TechRequirement(node_id='prereq', level_range=(0, 0))
        req.resolved_level = 0

        assert req.is_met({}) is True
        assert req.is_met({'prereq': 0}) is True

    def test_get_required_level_resolved(self):
        """get_required_level() returns resolved_level when available."""
        req = TechRequirement(node_id='test', level_range=(1, 5))
        req.resolved_level = 4

        assert req.get_required_level() == 4

    def test_get_required_level_unresolved(self):
        """get_required_level() returns minimum when not resolved."""
        req = TechRequirement(node_id='test', level_range=(2, 5))

        assert req.get_required_level() == 2


class TestTechNodeBasic:
    """Tests for basic TechNode functionality."""

    def test_minimal_initialization(self):
        """TechNode can be created with just id, name, max_levels."""
        node = TechNode(id='test', name='Test Node', max_levels=5)

        assert node.id == 'test'
        assert node.name == 'Test Node'
        assert node.max_levels == 5
        assert node.requirements == []
        assert node.base_decay == 0.005
        assert node.volatility == 0.1
        assert node.price == 1.0
        assert node.price_curve == "flat"
        assert node.comment is None

    def test_full_initialization(self):
        """TechNode can be created with all parameters."""
        reqs = [[TechRequirement('prereq', (1, 2))]]
        node = TechNode(
            id='advanced',
            name='Advanced Tech',
            max_levels=3,
            requirements=reqs,
            base_decay=0.01,
            volatility=0.2,
            price=2.0,
            price_curve="quadratic",
            comment="Section: Testing"
        )

        assert node.id == 'advanced'
        assert node.max_levels == 3
        assert len(node.requirements) == 1
        assert node.base_decay == 0.01
        assert node.volatility == 0.2
        assert node.price == 2.0
        assert node.price_curve == "quadratic"
        assert node.comment == "Section: Testing"


class TestTechNodeStatus:
    """Tests for TechNode.get_status()."""

    def test_status_completed_at_max_level(self):
        """Node is 'completed' when at max_levels."""
        node = TechNode(id='test', name='Test', max_levels=3)

        assert node.get_status(3, {}) == 'completed'
        assert node.get_status(5, {}) == 'completed'  # Even above max

    def test_status_available_no_requirements(self):
        """Node with no requirements is always 'available' (root node)."""
        node = TechNode(id='root', name='Root', max_levels=5)

        assert node.get_status(0, {}) == 'available'
        assert node.get_status(2, {}) == 'available'

    def test_status_available_requirements_met(self):
        """Node is 'available' when all requirements in any OR-group are met."""
        req = TechRequirement('prereq', (1, 1))
        req.resolved_level = 1
        node = TechNode(id='child', name='Child', max_levels=3, requirements=[[req]])

        assert node.get_status(0, {'prereq': 1}) == 'available'
        assert node.get_status(0, {'prereq': 2}) == 'available'

    def test_status_locked_requirements_not_met(self):
        """Node is 'locked' when no OR-group has all requirements met."""
        req = TechRequirement('prereq', (2, 2))
        req.resolved_level = 2
        node = TechNode(id='child', name='Child', max_levels=3, requirements=[[req]])

        assert node.get_status(0, {'prereq': 1}) == 'locked'
        assert node.get_status(0, {}) == 'locked'

    def test_status_or_group_logic(self):
        """Multiple OR-groups: any one satisfied unlocks the node."""
        req_a = TechRequirement('tech_a', (1, 1))
        req_a.resolved_level = 1
        req_b = TechRequirement('tech_b', (1, 1))
        req_b.resolved_level = 1

        # Two OR-groups: [[tech_a]] or [[tech_b]]
        node = TechNode(
            id='choice',
            name='Choice',
            max_levels=1,
            requirements=[[req_a], [req_b]]
        )

        # Either prerequisite satisfies
        assert node.get_status(0, {'tech_a': 1}) == 'available'
        assert node.get_status(0, {'tech_b': 1}) == 'available'
        assert node.get_status(0, {'tech_a': 1, 'tech_b': 1}) == 'available'
        assert node.get_status(0, {}) == 'locked'

    def test_status_and_group_logic(self):
        """Within an OR-group, ALL requirements must be met."""
        req_a = TechRequirement('tech_a', (1, 1))
        req_a.resolved_level = 1
        req_b = TechRequirement('tech_b', (2, 2))
        req_b.resolved_level = 2

        # One OR-group with two AND requirements
        node = TechNode(
            id='combined',
            name='Combined',
            max_levels=1,
            requirements=[[req_a, req_b]]
        )

        # Both must be met
        assert node.get_status(0, {'tech_a': 1, 'tech_b': 2}) == 'available'
        assert node.get_status(0, {'tech_a': 1, 'tech_b': 1}) == 'locked'  # tech_b too low
        assert node.get_status(0, {'tech_a': 0, 'tech_b': 2}) == 'locked'  # tech_a too low

    def test_status_complex_requirements(self):
        """Complex requirement: (A AND B) OR (C)."""
        req_a = TechRequirement('tech_a', (1, 1))
        req_a.resolved_level = 1
        req_b = TechRequirement('tech_b', (1, 1))
        req_b.resolved_level = 1
        req_c = TechRequirement('tech_c', (2, 2))
        req_c.resolved_level = 2

        # Two OR-groups: [A, B] or [C]
        node = TechNode(
            id='complex',
            name='Complex',
            max_levels=1,
            requirements=[[req_a, req_b], [req_c]]
        )

        # A and B together
        assert node.get_status(0, {'tech_a': 1, 'tech_b': 1}) == 'available'
        # Just C
        assert node.get_status(0, {'tech_c': 2}) == 'available'
        # Just A (missing B)
        assert node.get_status(0, {'tech_a': 1}) == 'locked'
        # C too low
        assert node.get_status(0, {'tech_c': 1}) == 'locked'


class TestTechNodeResolveRequirements:
    """Tests for requirement resolution."""

    def test_resolve_requirements_all_groups(self):
        """resolve_requirements() resolves all requirements in all groups."""
        req_a = TechRequirement('a', (1, 5))
        req_b = TechRequirement('b', (2, 4))
        req_c = TechRequirement('c', (1, 3))

        node = TechNode(
            id='test',
            name='Test',
            max_levels=1,
            requirements=[[req_a, req_b], [req_c]]
        )

        rng = random.Random(42)
        node.resolve_requirements(rng)

        # All should be resolved
        assert req_a.resolved_level is not None
        assert 1 <= req_a.resolved_level <= 5
        assert req_b.resolved_level is not None
        assert 2 <= req_b.resolved_level <= 4
        assert req_c.resolved_level is not None
        assert 1 <= req_c.resolved_level <= 3

    def test_resolve_requirements_deterministic(self):
        """resolve_requirements() is deterministic with same seed."""
        def create_node():
            return TechNode(
                id='test',
                name='Test',
                max_levels=1,
                requirements=[
                    [TechRequirement('a', (1, 10))],
                    [TechRequirement('b', (1, 10))]
                ]
            )

        node1 = create_node()
        node2 = create_node()

        rng1 = random.Random(99999)
        rng2 = random.Random(99999)

        node1.resolve_requirements(rng1)
        node2.resolve_requirements(rng2)

        assert node1.requirements[0][0].resolved_level == node2.requirements[0][0].resolved_level
        assert node1.requirements[1][0].resolved_level == node2.requirements[1][0].resolved_level


class TestTechNodePriceCurves:
    """Tests for effective price calculations."""

    def test_price_flat(self):
        """Flat price curve returns base price regardless of level."""
        node = TechNode(id='test', name='Test', max_levels=5, price=2.0, price_curve="flat")

        assert node.get_effective_price(1) == 2.0
        assert node.get_effective_price(3) == 2.0
        assert node.get_effective_price(5) == 2.0

    def test_price_linear(self):
        """Linear price curve: +50% per level."""
        node = TechNode(id='test', name='Test', max_levels=5, price=1.0, price_curve="linear")

        # 1 + 0.5 * level
        assert node.get_effective_price(1) == 1.5   # 1 + 0.5
        assert node.get_effective_price(2) == 2.0   # 1 + 1.0
        assert node.get_effective_price(5) == 3.5   # 1 + 2.5

    def test_price_quadratic(self):
        """Quadratic price curve: 1 + 0.2 * level^2."""
        node = TechNode(id='test', name='Test', max_levels=5, price=1.0, price_curve="quadratic")

        # 1 + 0.2 * level^2
        assert node.get_effective_price(1) == pytest.approx(1.2)   # 1 + 0.2
        assert node.get_effective_price(2) == pytest.approx(1.8)   # 1 + 0.8
        assert node.get_effective_price(5) == pytest.approx(6.0)   # 1 + 5.0

    def test_price_exponential(self):
        """Exponential price curve: 1.5^level."""
        node = TechNode(id='test', name='Test', max_levels=5, price=1.0, price_curve="exponential")

        # 1.5^level
        assert node.get_effective_price(1) == pytest.approx(1.5)
        assert node.get_effective_price(2) == pytest.approx(2.25)
        assert node.get_effective_price(5) == pytest.approx(7.59375)

    def test_price_logarithmic(self):
        """Logarithmic price curve: 1 + log(1 + level)."""
        node = TechNode(id='test', name='Test', max_levels=5, price=1.0, price_curve="logarithmic")

        # 1 + log(1 + level)
        assert node.get_effective_price(1) == pytest.approx(1 + math.log(2))
        assert node.get_effective_price(2) == pytest.approx(1 + math.log(3))
        assert node.get_effective_price(5) == pytest.approx(1 + math.log(6))

    def test_price_sqrt(self):
        """Square root price curve: 1 + sqrt(level)."""
        node = TechNode(id='test', name='Test', max_levels=5, price=1.0, price_curve="sqrt")

        # 1 + sqrt(level)
        assert node.get_effective_price(1) == pytest.approx(2.0)      # 1 + 1
        assert node.get_effective_price(4) == pytest.approx(3.0)      # 1 + 2
        assert node.get_effective_price(9) == pytest.approx(4.0)      # 1 + 3

    def test_price_unknown_curve_defaults_to_flat(self):
        """Unknown price curve type defaults to base price."""
        node = TechNode(id='test', name='Test', max_levels=5, price=2.5, price_curve="unknown_curve")

        assert node.get_effective_price(1) == 2.5
        assert node.get_effective_price(5) == 2.5

    def test_price_with_multiplier(self):
        """Base price multiplier affects all curves."""
        node = TechNode(id='test', name='Test', max_levels=5, price=2.0, price_curve="linear")

        # 2.0 * (1 + 0.5 * level)
        assert node.get_effective_price(1) == 3.0   # 2 * 1.5
        assert node.get_effective_price(2) == 4.0   # 2 * 2.0


class TestTechNodePrerequisites:
    """Tests for prerequisite extraction."""

    def test_get_prerequisite_node_ids_empty(self):
        """get_prerequisite_node_ids() returns empty list for root node."""
        node = TechNode(id='root', name='Root', max_levels=1)

        assert node.get_prerequisite_node_ids() == []

    def test_get_prerequisite_node_ids_single(self):
        """get_prerequisite_node_ids() returns single prerequisite."""
        req = TechRequirement('prereq', (1, 1))
        node = TechNode(id='child', name='Child', max_levels=1, requirements=[[req]])

        assert node.get_prerequisite_node_ids() == ['prereq']

    def test_get_prerequisite_node_ids_multiple(self):
        """get_prerequisite_node_ids() returns all unique prerequisites."""
        req_a = TechRequirement('tech_a', (1, 1))
        req_b = TechRequirement('tech_b', (1, 1))
        req_c = TechRequirement('tech_c', (1, 1))

        node = TechNode(
            id='advanced',
            name='Advanced',
            max_levels=1,
            requirements=[[req_a, req_b], [req_c]]
        )

        prereqs = node.get_prerequisite_node_ids()
        assert set(prereqs) == {'tech_a', 'tech_b', 'tech_c'}

    def test_get_prerequisite_node_ids_deduplicates(self):
        """get_prerequisite_node_ids() removes duplicate node IDs."""
        req_a1 = TechRequirement('tech_a', (1, 1))
        req_a2 = TechRequirement('tech_a', (2, 2))  # Same node, different level

        node = TechNode(
            id='choice',
            name='Choice',
            max_levels=1,
            requirements=[[req_a1], [req_a2]]
        )

        prereqs = node.get_prerequisite_node_ids()
        assert prereqs == ['tech_a']


class TestTechNodeEdgeCases:
    """Tests for edge cases."""

    def test_zero_max_levels(self):
        """Node with max_levels=0 is always completed."""
        node = TechNode(id='instant', name='Instant', max_levels=0)

        assert node.get_status(0, {}) == 'completed'

    def test_level_zero_price(self):
        """get_effective_price at level 0."""
        node = TechNode(id='test', name='Test', max_levels=5, price=1.0, price_curve="linear")

        # Level 0: 1 + 0.5 * 0 = 1.0
        assert node.get_effective_price(0) == 1.0

    def test_very_high_level(self):
        """Price curves handle high levels."""
        node = TechNode(id='test', name='Test', max_levels=100, price=1.0, price_curve="exponential")

        # Should not overflow or error
        price = node.get_effective_price(50)
        assert price > 0
        assert math.isfinite(price)

    def test_requirement_with_self_reference(self):
        """Node can have requirement referencing itself (for level checks)."""
        req = TechRequirement('self_node', (1, 1))
        req.resolved_level = 1
        node = TechNode(
            id='self_node',
            name='Self Reference',
            max_levels=5,
            requirements=[[req]]
        )

        # At level 0, requirement for level 1 of self is not met
        assert node.get_status(0, {'self_node': 0}) == 'locked'
        # At level 1, requirement is met for next level
        assert node.get_status(1, {'self_node': 1}) == 'available'

    def test_empty_or_group(self):
        """Empty OR-group list means no requirements."""
        node = TechNode(id='test', name='Test', max_levels=5, requirements=[])

        assert node.get_status(0, {}) == 'available'

    def test_empty_and_group(self):
        """Empty AND-group is always satisfied (vacuous truth)."""
        node = TechNode(id='test', name='Test', max_levels=5, requirements=[[]])

        # Empty AND-group: all() of empty = True
        assert node.get_status(0, {}) == 'available'
