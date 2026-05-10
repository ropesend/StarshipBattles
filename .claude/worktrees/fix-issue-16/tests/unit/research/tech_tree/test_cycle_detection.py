"""
Unit tests for TechTree.detect_cycles() - Cycle Detection

TCG-FND-004: Tests for TechTree cycle detection algorithm.
Tests cover:
- No cycles (valid trees)
- Self-referential cycles (A -> A)
- Simple two-node cycles (A -> B -> A)
- Complex multi-node cycles (A -> B -> C -> A)
- Multiple independent cycles
- Cycles with negated dependencies (should be ignored)
- Diamond dependencies (not cycles)
- Nested cycles
"""
import pytest

from game.research.data.tech_tree import TechTree
from game.research.data.tech_node import TechNode, TechRequirement


class TestCycleDetectionNoCycles:
    """Tests for trees without cycles (valid cases)."""

    def test_empty_tree_no_cycles(self):
        """Empty tree has no cycles."""
        tree = TechTree()
        errors = tree.detect_cycles()
        assert errors == []

    def test_single_root_node_no_cycle(self):
        """Single root node with no dependencies."""
        tree = TechTree()
        tree.nodes['root'] = TechNode(id='root', name='Root', max_levels=1)

        errors = tree.detect_cycles()
        assert errors == []

    def test_linear_chain_no_cycle(self):
        """Linear chain A -> B -> C has no cycle."""
        tree = TechTree()
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1)

        req_a = TechRequirement('a', (1, 1))
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_a]])

        req_b = TechRequirement('b', (1, 1))
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=1, requirements=[[req_b]])

        errors = tree.detect_cycles()
        assert errors == []

    def test_diamond_dependency_no_cycle(self):
        """Diamond: A -> B -> D, A -> C -> D (not a cycle)."""
        tree = TechTree()
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1)

        req_a = TechRequirement('a', (1, 1))
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_a]])
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=1, requirements=[[req_a]])

        req_b = TechRequirement('b', (1, 1))
        req_c = TechRequirement('c', (1, 1))
        tree.nodes['d'] = TechNode(id='d', name='D', max_levels=1, requirements=[[req_b, req_c]])

        errors = tree.detect_cycles()
        assert errors == []

    def test_multiple_roots_no_cycle(self):
        """Multiple independent root nodes."""
        tree = TechTree()
        tree.nodes['root1'] = TechNode(id='root1', name='Root1', max_levels=1)
        tree.nodes['root2'] = TechNode(id='root2', name='Root2', max_levels=1)
        tree.nodes['root3'] = TechNode(id='root3', name='Root3', max_levels=1)

        errors = tree.detect_cycles()
        assert errors == []

    def test_or_group_no_cycle(self):
        """OR groups without cycles."""
        tree = TechTree()
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1)
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1)

        req_a = TechRequirement('a', (1, 1))
        req_b = TechRequirement('b', (1, 1))
        # C requires (A) OR (B) - two OR groups
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=1,
                                   requirements=[[req_a], [req_b]])

        errors = tree.detect_cycles()
        assert errors == []


class TestCycleDetectionWithCycles:
    """Tests for trees with cycles (invalid cases)."""

    def test_self_referential_cycle(self):
        """Node references itself: A -> A."""
        tree = TechTree()
        req_self = TechRequirement('self_ref', (1, 1))
        tree.nodes['self_ref'] = TechNode(id='self_ref', name='Self Ref', max_levels=1,
                                          requirements=[[req_self]])

        errors = tree.detect_cycles()
        assert len(errors) == 1
        assert 'self_ref' in errors[0]
        assert 'Cycle' in errors[0] or 'cycle' in errors[0].lower()

    def test_two_node_cycle(self):
        """Simple cycle: A -> B -> A."""
        tree = TechTree()

        req_b = TechRequirement('b', (1, 1))
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1, requirements=[[req_b]])

        req_a = TechRequirement('a', (1, 1))
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_a]])

        errors = tree.detect_cycles()
        assert len(errors) >= 1
        # Should mention both nodes in cycle
        cycle_error = errors[0]
        assert 'a' in cycle_error or 'b' in cycle_error

    def test_three_node_cycle(self):
        """Longer cycle: A -> B -> C -> A."""
        tree = TechTree()

        req_b = TechRequirement('b', (1, 1))
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1, requirements=[[req_b]])

        req_c = TechRequirement('c', (1, 1))
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_c]])

        req_a = TechRequirement('a', (1, 1))
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=1, requirements=[[req_a]])

        errors = tree.detect_cycles()
        assert len(errors) >= 1

    def test_cycle_with_long_chain(self):
        """Chain with cycle at end: A -> B -> C -> D -> B."""
        tree = TechTree()
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1)

        req_a = TechRequirement('a', (1, 1))
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_a]])

        req_b = TechRequirement('b', (1, 1))
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=1, requirements=[[req_b]])

        req_c = TechRequirement('c', (1, 1))
        tree.nodes['d'] = TechNode(id='d', name='D', max_levels=1, requirements=[[req_c]])

        # Add cycle: D also requires itself through B
        req_d = TechRequirement('d', (1, 1))
        tree.nodes['b'].requirements.append([req_d])

        errors = tree.detect_cycles()
        assert len(errors) >= 1

    def test_multiple_independent_cycles(self):
        """Two independent cycles in same tree."""
        tree = TechTree()

        # Cycle 1: A -> B -> A
        req_b = TechRequirement('b', (1, 1))
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1, requirements=[[req_b]])

        req_a = TechRequirement('a', (1, 1))
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_a]])

        # Cycle 2: X -> Y -> X
        req_y = TechRequirement('y', (1, 1))
        tree.nodes['x'] = TechNode(id='x', name='X', max_levels=1, requirements=[[req_y]])

        req_x = TechRequirement('x', (1, 1))
        tree.nodes['y'] = TechNode(id='y', name='Y', max_levels=1, requirements=[[req_x]])

        errors = tree.detect_cycles()
        # Should detect at least one cycle (may report multiple depending on traversal)
        assert len(errors) >= 1


class TestCycleDetectionNegatedRequirements:
    """Tests for negated requirements (should NOT create cycles)."""

    def test_negated_self_reference_not_cycle(self):
        """Negated self-reference: A requires NOT A - not a cycle."""
        tree = TechTree()
        req_self = TechRequirement('negated_self', (1, 1), negate=True)
        tree.nodes['negated_self'] = TechNode(id='negated_self', name='Negated Self',
                                               max_levels=1, requirements=[[req_self]])

        errors = tree.detect_cycles()
        # Negated dependencies don't create cycles
        assert errors == []

    def test_negated_mutual_reference_not_cycle(self):
        """A requires NOT B, B requires NOT A - not a cycle."""
        tree = TechTree()

        req_b_neg = TechRequirement('b', (1, 1), negate=True)
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1, requirements=[[req_b_neg]])

        req_a_neg = TechRequirement('a', (1, 1), negate=True)
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_a_neg]])

        errors = tree.detect_cycles()
        # Negated dependencies don't create true dependency cycles
        assert errors == []

    def test_mixed_negated_and_positive_cycle(self):
        """A -> B (positive), B -> A (negated) - cycle only via positive."""
        tree = TechTree()

        req_b_pos = TechRequirement('b', (1, 1), negate=False)
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1, requirements=[[req_b_pos]])

        req_a_neg = TechRequirement('a', (1, 1), negate=True)
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_a_neg]])

        errors = tree.detect_cycles()
        # Only positive dependency matters, so no cycle
        assert errors == []


class TestCycleDetectionEdgeCases:
    """Edge cases for cycle detection."""

    def test_missing_node_reference_not_cycle(self):
        """Reference to non-existent node is not a cycle."""
        tree = TechTree()
        req_missing = TechRequirement('nonexistent', (1, 1))
        tree.nodes['orphan'] = TechNode(id='orphan', name='Orphan', max_levels=1,
                                         requirements=[[req_missing]])

        errors = tree.detect_cycles()
        # Missing references are not cycles (validation catches them separately)
        assert errors == []

    def test_cycle_in_or_group(self):
        """Cycle detected even if in OR group: C requires (A OR B), B requires C."""
        tree = TechTree()
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1)

        req_c = TechRequirement('c', (1, 1))
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_c]])

        req_a = TechRequirement('a', (1, 1))
        req_b = TechRequirement('b', (1, 1))
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=1,
                                   requirements=[[req_a], [req_b]])  # OR groups

        errors = tree.detect_cycles()
        # Cycle exists via B -> C -> B
        assert len(errors) >= 1

    def test_cycle_in_and_group(self):
        """Cycle in AND group: C requires (A AND B), B requires C."""
        tree = TechTree()
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1)

        req_c = TechRequirement('c', (1, 1))
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_c]])

        req_a = TechRequirement('a', (1, 1))
        req_b = TechRequirement('b', (1, 1))
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=1,
                                   requirements=[[req_a, req_b]])  # AND group

        errors = tree.detect_cycles()
        assert len(errors) >= 1

    def test_validate_includes_cycle_errors(self):
        """validate() includes cycle errors along with requirement errors."""
        tree = TechTree()

        # Add a cycle
        req_self = TechRequirement('cyclic', (1, 1))
        tree.nodes['cyclic'] = TechNode(id='cyclic', name='Cyclic', max_levels=1,
                                        requirements=[[req_self]])

        errors = tree.validate()
        # validate() runs both validate_requirements and detect_cycles
        assert len(errors) >= 1
        cycle_found = any('cycle' in e.lower() for e in errors)
        assert cycle_found

    def test_deeply_nested_cycle(self):
        """Deep chain: A -> B -> C -> D -> E -> A."""
        tree = TechTree()

        req_b = TechRequirement('b', (1, 1))
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1, requirements=[[req_b]])

        req_c = TechRequirement('c', (1, 1))
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_c]])

        req_d = TechRequirement('d', (1, 1))
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=1, requirements=[[req_d]])

        req_e = TechRequirement('e', (1, 1))
        tree.nodes['d'] = TechNode(id='d', name='D', max_levels=1, requirements=[[req_e]])

        req_a = TechRequirement('a', (1, 1))
        tree.nodes['e'] = TechNode(id='e', name='E', max_levels=1, requirements=[[req_a]])

        errors = tree.detect_cycles()
        assert len(errors) >= 1


class TestCycleDetectionOutput:
    """Tests for cycle error message format."""

    def test_cycle_error_contains_path(self):
        """Cycle error message should show the cycle path."""
        tree = TechTree()

        req_b = TechRequirement('b', (1, 1))
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1, requirements=[[req_b]])

        req_a = TechRequirement('a', (1, 1))
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_a]])

        errors = tree.detect_cycles()
        assert len(errors) >= 1

        # Error should contain cycle indicator
        error_msg = errors[0].lower()
        assert 'cycle' in error_msg or '->' in errors[0]

    def test_self_cycle_error_shows_node(self):
        """Self-cycle error should clearly show the node."""
        tree = TechTree()
        req_self = TechRequirement('selfy', (1, 1))
        tree.nodes['selfy'] = TechNode(id='selfy', name='Selfy', max_levels=1,
                                       requirements=[[req_self]])

        errors = tree.detect_cycles()
        assert len(errors) == 1
        assert 'selfy' in errors[0]
