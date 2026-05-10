"""
Tests for TechRequirement negation logic.

TCG-FND-012: Tests for negation feature in tech requirements:
- Negation is tested in TechNode, but integration with TechTree needs coverage
- Combined negated and non-negated requirements in same AND group
- Full TechTree context with negated requirements
"""
import pytest
import random

from game.research.data.tech_tree import TechTree
from game.research.data.tech_node import TechNode, TechRequirement
from game.research.data.research_tracker import ResearchTracker


class TestTechRequirementNegation:
    """Tests for TechRequirement negate field."""

    def test_negated_requirement_is_met_below_level(self):
        """Negated requirement is met when level is BELOW target."""
        req = TechRequirement('tech_a', (2, 2))
        req.resolved_level = 2
        req.negate = True

        # Level 0 (below 2) - should pass
        assert req.is_met({'tech_a': 0}) is True

        # Level 1 (below 2) - should pass
        assert req.is_met({'tech_a': 1}) is True

    def test_negated_requirement_fails_at_or_above_level(self):
        """Negated requirement fails when level is AT OR ABOVE target."""
        req = TechRequirement('tech_a', (2, 2))
        req.resolved_level = 2
        req.negate = True

        # Level 2 (at target) - should fail
        assert req.is_met({'tech_a': 2}) is False

        # Level 3 (above target) - should fail
        assert req.is_met({'tech_a': 3}) is False

    def test_negated_with_missing_tech(self):
        """Negated requirement passes when tech is missing (level 0)."""
        req = TechRequirement('missing', (1, 1))
        req.resolved_level = 1
        req.negate = True

        # Missing tech defaults to level 0, which is below 1
        assert req.is_met({}) is True

    def test_non_negated_normal_behavior(self):
        """Non-negated requirement has normal >= behavior."""
        req = TechRequirement('tech_a', (2, 2))
        req.resolved_level = 2
        req.negate = False

        # Below level - should fail
        assert req.is_met({'tech_a': 1}) is False

        # At level - should pass
        assert req.is_met({'tech_a': 2}) is True

        # Above level - should pass
        assert req.is_met({'tech_a': 3}) is True


class TestNegatedRequirementsInTechTree:
    """Integration tests for negated requirements in TechTree."""

    def test_mutually_exclusive_paths(self):
        """Two techs that require NOT having the other (mutually exclusive)."""
        tree = TechTree()

        # Root tech
        tree.nodes['root'] = TechNode(id='root', name='Root', max_levels=1)

        # Path A: requires root, NOT path_b
        req_root_a = TechRequirement('root', (1, 1))
        req_root_a.resolved_level = 1
        req_not_b = TechRequirement('path_b', (1, 1))
        req_not_b.resolved_level = 1
        req_not_b.negate = True

        tree.nodes['path_a'] = TechNode(
            id='path_a', name='Path A', max_levels=1,
            requirements=[[req_root_a, req_not_b]]
        )

        # Path B: requires root, NOT path_a
        req_root_b = TechRequirement('root', (1, 1))
        req_root_b.resolved_level = 1
        req_not_a = TechRequirement('path_a', (1, 1))
        req_not_a.resolved_level = 1
        req_not_a.negate = True

        tree.nodes['path_b'] = TechNode(
            id='path_b', name='Path B', max_levels=1,
            requirements=[[req_root_b, req_not_a]]
        )

        # With only root researched, both should be available
        tech_levels = {'root': 1, 'path_a': 0, 'path_b': 0}

        assert tree.nodes['path_a'].get_status(0, tech_levels) == 'available'
        assert tree.nodes['path_b'].get_status(0, tech_levels) == 'available'

        # After researching path_a, path_b becomes locked
        tech_levels = {'root': 1, 'path_a': 1, 'path_b': 0}

        assert tree.nodes['path_a'].get_status(1, tech_levels) == 'completed'
        assert tree.nodes['path_b'].get_status(0, tech_levels) == 'locked'

    def test_combined_negated_and_positive_requirements(self):
        """AND group with both positive and negated requirements."""
        tree = TechTree()

        tree.nodes['tech_a'] = TechNode(id='tech_a', name='Tech A', max_levels=3)
        tree.nodes['tech_b'] = TechNode(id='tech_b', name='Tech B', max_levels=3)

        # Combined node: requires A level 2+, but B level < 2
        req_a = TechRequirement('tech_a', (2, 2))
        req_a.resolved_level = 2
        req_a.negate = False

        req_not_b = TechRequirement('tech_b', (2, 2))
        req_not_b.resolved_level = 2
        req_not_b.negate = True

        tree.nodes['combined'] = TechNode(
            id='combined', name='Combined', max_levels=1,
            requirements=[[req_a, req_not_b]]
        )

        # A too low - locked
        assert tree.nodes['combined'].get_status(0, {'tech_a': 1, 'tech_b': 0}) == 'locked'

        # A sufficient, B low - available
        assert tree.nodes['combined'].get_status(0, {'tech_a': 2, 'tech_b': 0}) == 'available'
        assert tree.nodes['combined'].get_status(0, {'tech_a': 2, 'tech_b': 1}) == 'available'

        # A sufficient, B too high - locked
        assert tree.nodes['combined'].get_status(0, {'tech_a': 2, 'tech_b': 2}) == 'locked'
        assert tree.nodes['combined'].get_status(0, {'tech_a': 3, 'tech_b': 3}) == 'locked'

    def test_negated_in_or_group(self):
        """Negated requirement in one of multiple OR groups."""
        tree = TechTree()

        tree.nodes['tech_a'] = TechNode(id='tech_a', name='Tech A', max_levels=2)
        tree.nodes['tech_b'] = TechNode(id='tech_b', name='Tech B', max_levels=2)

        # Can unlock via either:
        # - Group 1: A level 2+
        # - Group 2: NOT B level 2+

        req_a = TechRequirement('tech_a', (2, 2))
        req_a.resolved_level = 2

        req_not_b = TechRequirement('tech_b', (2, 2))
        req_not_b.resolved_level = 2
        req_not_b.negate = True

        tree.nodes['choice'] = TechNode(
            id='choice', name='Choice', max_levels=1,
            requirements=[[req_a], [req_not_b]]
        )

        # Neither condition met (A too low, B at level 2)
        assert tree.nodes['choice'].get_status(0, {'tech_a': 1, 'tech_b': 2}) == 'locked'

        # A high enough (first group passes)
        assert tree.nodes['choice'].get_status(0, {'tech_a': 2, 'tech_b': 2}) == 'available'

        # B low enough (second group passes)
        assert tree.nodes['choice'].get_status(0, {'tech_a': 0, 'tech_b': 0}) == 'available'
        assert tree.nodes['choice'].get_status(0, {'tech_a': 0, 'tech_b': 1}) == 'available'

    def test_negation_with_level_range(self):
        """Negated requirement with fuzzy level range resolution."""
        req = TechRequirement('tech', (2, 4))
        req.negate = True

        rng = random.Random(42)
        resolved = req.resolve(rng)

        # Should resolve to value in range
        assert 2 <= resolved <= 4

        # Negation: must be BELOW resolved level
        tech_levels = {'tech': resolved - 1}
        assert req.is_met(tech_levels) is True

        tech_levels = {'tech': resolved}
        assert req.is_met(tech_levels) is False


class TestNegatedCycleDetection:
    """Tests for cycle detection with negated requirements."""

    def test_negated_dependency_not_cycle(self):
        """Negated dependencies don't count as cycles."""
        tree = TechTree()

        # A requires NOT B
        req_not_b = TechRequirement('node_b', (1, 1))
        req_not_b.negate = True
        tree.nodes['node_a'] = TechNode(
            id='node_a', name='A', max_levels=1,
            requirements=[[req_not_b]]
        )

        # B requires A (positive)
        req_a = TechRequirement('node_a', (1, 1))
        tree.nodes['node_b'] = TechNode(
            id='node_b', name='B', max_levels=1,
            requirements=[[req_a]]
        )

        # This should NOT be a cycle because A's dependency on B is negated
        errors = tree.detect_cycles()
        assert errors == []

    def test_mixed_positive_negative_no_false_cycle(self):
        """Mixed positive/negative deps don't create false cycle detection."""
        tree = TechTree()

        # Complex structure: A -positive-> B -negative-> C -positive-> A
        # The A -> B -> C -> A would be a cycle if all positive
        # But B -> C is negated, so not a real dependency

        req_b = TechRequirement('node_b', (1, 1))
        tree.nodes['node_a'] = TechNode(
            id='node_a', name='A', max_levels=1,
            requirements=[[req_b]]
        )

        req_c = TechRequirement('node_c', (1, 1))
        req_c.negate = True  # Negated!
        tree.nodes['node_b'] = TechNode(
            id='node_b', name='B', max_levels=1,
            requirements=[[req_c]]
        )

        req_a = TechRequirement('node_a', (1, 1))
        tree.nodes['node_c'] = TechNode(
            id='node_c', name='C', max_levels=1,
            requirements=[[req_a]]
        )

        # Should NOT be detected as cycle (B's dep on C is negated)
        errors = tree.detect_cycles()
        assert errors == []


class TestNegationValidation:
    """Tests for validation with negated requirements."""

    def test_negated_reference_still_validated(self):
        """Negated references to non-existent nodes are still errors."""
        tree = TechTree()

        req_missing = TechRequirement('nonexistent', (1, 1))
        req_missing.negate = True  # Negated but still invalid ref

        tree.nodes['bad'] = TechNode(
            id='bad', name='Bad', max_levels=1,
            requirements=[[req_missing]]
        )

        errors = tree.validate_requirements()

        assert len(errors) == 1
        assert 'nonexistent' in errors[0]

    def test_negation_preserved_after_resolution(self):
        """Negation flag preserved after fuzzy resolution."""
        req = TechRequirement('tech', (1, 3))
        req.negate = True

        rng = random.Random(42)
        req.resolve(rng)

        # Negate should still be True
        assert req.negate is True

        # And should work correctly
        assert req.is_met({'tech': 0}) is True
        assert req.is_met({'tech': req.resolved_level}) is False
