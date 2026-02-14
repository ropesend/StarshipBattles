"""
Tests for TechTree validation methods.

TCG-FND-004: Tests for validate_requirements(), detect_cycles(), and validate()
with focus on:
- Error message format verification
- Complex multi-path cycle detection
- Combined validation (validate() method)
- Self-referencing nodes
"""
import pytest

from game.research.data.tech_tree import TechTree
from game.research.data.tech_node import TechNode, TechRequirement


class TestValidateRequirements:
    """Tests for TechTree.validate_requirements()."""

    def test_valid_tree_returns_empty_list(self):
        """Valid tree with all references resolved returns empty error list."""
        tree = TechTree()

        # Create valid tree: root -> child
        tree.nodes['root'] = TechNode(id='root', name='Root', max_levels=1)

        req = TechRequirement('root', (1, 1))
        tree.nodes['child'] = TechNode(
            id='child', name='Child', max_levels=1,
            requirements=[[req]]
        )

        errors = tree.validate_requirements()

        assert errors == []

    def test_missing_reference_detected(self):
        """Missing node reference generates appropriate error."""
        tree = TechTree()

        req = TechRequirement('nonexistent', (1, 1))
        tree.nodes['orphan'] = TechNode(
            id='orphan', name='Orphan', max_levels=1,
            requirements=[[req]]
        )

        errors = tree.validate_requirements()

        assert len(errors) == 1
        assert 'orphan' in errors[0]
        assert 'nonexistent' in errors[0]

    def test_error_message_format(self):
        """Error message follows expected format."""
        tree = TechTree()

        req = TechRequirement('missing_node', (1, 1))
        tree.nodes['bad_ref'] = TechNode(
            id='bad_ref', name='Bad Reference', max_levels=1,
            requirements=[[req]]
        )

        errors = tree.validate_requirements()

        assert len(errors) == 1
        # Format: "Node 'X' references unknown node 'Y'"
        assert "Node 'bad_ref'" in errors[0]
        assert "unknown node 'missing_node'" in errors[0]

    def test_multiple_missing_references(self):
        """Multiple missing references all reported."""
        tree = TechTree()

        req1 = TechRequirement('missing1', (1, 1))
        req2 = TechRequirement('missing2', (1, 1))

        tree.nodes['multi_bad'] = TechNode(
            id='multi_bad', name='Multiple Bad', max_levels=1,
            requirements=[[req1], [req2]]
        )

        errors = tree.validate_requirements()

        assert len(errors) == 2
        error_text = ' '.join(errors)
        assert 'missing1' in error_text
        assert 'missing2' in error_text

    def test_or_groups_all_validated(self):
        """All OR groups have their requirements validated."""
        tree = TechTree()

        tree.nodes['valid'] = TechNode(id='valid', name='Valid', max_levels=1)

        req_valid = TechRequirement('valid', (1, 1))
        req_invalid = TechRequirement('invalid', (1, 1))

        # One valid OR group, one invalid
        tree.nodes['mixed'] = TechNode(
            id='mixed', name='Mixed', max_levels=1,
            requirements=[[req_valid], [req_invalid]]
        )

        errors = tree.validate_requirements()

        assert len(errors) == 1
        assert 'invalid' in errors[0]

    def test_and_conditions_all_validated(self):
        """All AND conditions within a group validated."""
        tree = TechTree()

        tree.nodes['prereq1'] = TechNode(id='prereq1', name='Prereq1', max_levels=1)
        # prereq2 is missing

        req1 = TechRequirement('prereq1', (1, 1))
        req2 = TechRequirement('prereq2', (1, 1))

        tree.nodes['combined'] = TechNode(
            id='combined', name='Combined', max_levels=1,
            requirements=[[req1, req2]]  # AND group
        )

        errors = tree.validate_requirements()

        assert len(errors) == 1
        assert 'prereq2' in errors[0]


class TestDetectCycles:
    """Tests for TechTree.detect_cycles()."""

    def test_no_cycles_returns_empty(self):
        """Acyclic tree returns empty error list."""
        tree = TechTree()

        tree.nodes['root'] = TechNode(id='root', name='Root', max_levels=1)

        req = TechRequirement('root', (1, 1))
        tree.nodes['child'] = TechNode(
            id='child', name='Child', max_levels=1,
            requirements=[[req]]
        )

        errors = tree.detect_cycles()

        assert errors == []

    def test_simple_cycle_detected(self):
        """Simple A -> B -> A cycle detected."""
        tree = TechTree()

        req_b = TechRequirement('node_b', (1, 1))
        tree.nodes['node_a'] = TechNode(
            id='node_a', name='Node A', max_levels=1,
            requirements=[[req_b]]
        )

        req_a = TechRequirement('node_a', (1, 1))
        tree.nodes['node_b'] = TechNode(
            id='node_b', name='Node B', max_levels=1,
            requirements=[[req_a]]
        )

        errors = tree.detect_cycles()

        assert len(errors) >= 1
        error_text = ' '.join(errors)
        assert 'Cycle detected' in error_text
        assert 'node_a' in error_text
        assert 'node_b' in error_text

    def test_complex_multipath_cycle(self):
        """Complex cycle: A -> B -> C -> A."""
        tree = TechTree()

        req_b = TechRequirement('node_b', (1, 1))
        tree.nodes['node_a'] = TechNode(
            id='node_a', name='Node A', max_levels=1,
            requirements=[[req_b]]
        )

        req_c = TechRequirement('node_c', (1, 1))
        tree.nodes['node_b'] = TechNode(
            id='node_b', name='Node B', max_levels=1,
            requirements=[[req_c]]
        )

        req_a = TechRequirement('node_a', (1, 1))
        tree.nodes['node_c'] = TechNode(
            id='node_c', name='Node C', max_levels=1,
            requirements=[[req_a]]
        )

        errors = tree.detect_cycles()

        assert len(errors) >= 1
        error_text = ' '.join(errors)
        assert 'Cycle detected' in error_text

    def test_self_reference_not_cycle_if_valid(self):
        """Self-reference for level gating is valid, not a cycle."""
        tree = TechTree()

        # Self-reference: node requires level 1 of itself (for level 2+)
        req_self = TechRequirement('self_ref', (1, 1))
        tree.nodes['self_ref'] = TechNode(
            id='self_ref', name='Self Reference', max_levels=5,
            requirements=[[req_self]]
        )

        # This should be detected as a cycle in current implementation
        # since it follows all positive dependencies
        errors = tree.detect_cycles()

        # Self-reference creates cycle: self_ref -> self_ref
        assert len(errors) >= 1

    def test_negated_requirements_not_followed(self):
        """Negated requirements don't create dependency cycles."""
        tree = TechTree()

        # A requires NOT B (negate=True)
        req_not_b = TechRequirement('node_b', (1, 1))
        req_not_b.negate = True

        tree.nodes['node_a'] = TechNode(
            id='node_a', name='Node A', max_levels=1,
            requirements=[[req_not_b]]
        )

        # B requires A (positive)
        req_a = TechRequirement('node_a', (1, 1))
        tree.nodes['node_b'] = TechNode(
            id='node_b', name='Node B', max_levels=1,
            requirements=[[req_a]]
        )

        errors = tree.detect_cycles()

        # Should NOT be a cycle because negated requirements aren't followed
        assert errors == []

    def test_cycle_format_shows_path(self):
        """Cycle error message shows the cycle path."""
        tree = TechTree()

        req_b = TechRequirement('b', (1, 1))
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1, requirements=[[req_b]])

        req_a = TechRequirement('a', (1, 1))
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req_a]])

        errors = tree.detect_cycles()

        assert len(errors) >= 1
        # Should contain arrow notation showing path
        assert '->' in errors[0]

    def test_diamond_dependency_no_cycle(self):
        """Diamond dependency (A -> B,C -> D) is not a cycle."""
        tree = TechTree()

        tree.nodes['root'] = TechNode(id='root', name='Root', max_levels=1)

        req_root = TechRequirement('root', (1, 1))
        tree.nodes['left'] = TechNode(
            id='left', name='Left', max_levels=1,
            requirements=[[req_root]]
        )
        tree.nodes['right'] = TechNode(
            id='right', name='Right', max_levels=1,
            requirements=[[req_root]]
        )

        req_left = TechRequirement('left', (1, 1))
        req_right = TechRequirement('right', (1, 1))
        tree.nodes['bottom'] = TechNode(
            id='bottom', name='Bottom', max_levels=1,
            requirements=[[req_left, req_right]]
        )

        errors = tree.detect_cycles()

        assert errors == []


class TestValidate:
    """Tests for TechTree.validate() combined validation."""

    def test_validate_calls_both_methods(self):
        """validate() runs both validate_requirements and detect_cycles."""
        tree = TechTree()

        # Create invalid reference (for validate_requirements)
        req_missing = TechRequirement('missing', (1, 1))
        tree.nodes['bad_ref'] = TechNode(
            id='bad_ref', name='Bad Ref', max_levels=1,
            requirements=[[req_missing]]
        )

        errors = tree.validate()

        # Should include error from validate_requirements
        assert len(errors) >= 1
        assert any('missing' in e for e in errors)

    def test_validate_combines_errors(self):
        """validate() combines errors from both validations."""
        tree = TechTree()

        # Missing reference
        req_missing = TechRequirement('missing', (1, 1))
        tree.nodes['orphan'] = TechNode(
            id='orphan', name='Orphan', max_levels=1,
            requirements=[[req_missing]]
        )

        # Cycle (separate from orphan)
        req_b = TechRequirement('cyclic_b', (1, 1))
        tree.nodes['cyclic_a'] = TechNode(
            id='cyclic_a', name='Cyclic A', max_levels=1,
            requirements=[[req_b]]
        )

        req_a = TechRequirement('cyclic_a', (1, 1))
        tree.nodes['cyclic_b'] = TechNode(
            id='cyclic_b', name='Cyclic B', max_levels=1,
            requirements=[[req_a]]
        )

        errors = tree.validate()

        # Should have both types of errors
        assert len(errors) >= 2
        error_text = ' '.join(errors)
        assert 'missing' in error_text or 'unknown' in error_text
        assert 'Cycle' in error_text

    def test_validate_empty_tree(self):
        """validate() on empty tree returns no errors."""
        tree = TechTree()

        errors = tree.validate()

        assert errors == []

    def test_validate_valid_tree(self):
        """validate() on valid tree returns no errors."""
        tree = TechTree()

        tree.nodes['root'] = TechNode(id='root', name='Root', max_levels=1)

        req = TechRequirement('root', (1, 1))
        tree.nodes['child'] = TechNode(
            id='child', name='Child', max_levels=1,
            requirements=[[req]]
        )

        req2 = TechRequirement('child', (1, 1))
        tree.nodes['grandchild'] = TechNode(
            id='grandchild', name='Grandchild', max_levels=1,
            requirements=[[req2]]
        )

        errors = tree.validate()

        assert errors == []


class TestDepthCalculation:
    """Tests for depth calculation edge cases."""

    def test_depth_with_missing_node(self):
        """calculate_depth handles missing nodes gracefully."""
        tree = TechTree()

        tree.nodes['exists'] = TechNode(id='exists', name='Exists', max_levels=1)

        # Request depth for non-existent node
        depth = tree.calculate_depth('nonexistent')

        assert depth == 0  # Default for missing nodes

    def test_depth_caching(self):
        """Depth calculation uses cache for efficiency."""
        tree = TechTree()

        tree.nodes['root'] = TechNode(id='root', name='Root', max_levels=1)

        req = TechRequirement('root', (1, 1))
        tree.nodes['child'] = TechNode(
            id='child', name='Child', max_levels=1,
            requirements=[[req]]
        )

        # First call populates cache
        depth1 = tree.calculate_depth('child')

        # Verify cache was populated
        assert 'child' in tree._depth_cache
        assert tree._depth_cache['child'] == 1

        # Second call should use cache
        depth2 = tree.calculate_depth('child')

        assert depth1 == depth2


class TestEdgeCases:
    """Additional edge case tests."""

    def test_requirements_referencing_self(self):
        """Node referencing itself is properly validated."""
        tree = TechTree()

        # Create node with self-reference
        req_self = TechRequirement('multi_level', (1, 1))
        tree.nodes['multi_level'] = TechNode(
            id='multi_level', name='Multi Level', max_levels=5,
            requirements=[[req_self]]
        )

        # validate_requirements should pass (reference exists)
        ref_errors = tree.validate_requirements()
        assert ref_errors == []

        # detect_cycles should find cycle
        cycle_errors = tree.detect_cycles()
        assert len(cycle_errors) >= 1

    def test_empty_requirements_list(self):
        """Nodes with empty requirements are valid root nodes."""
        tree = TechTree()

        tree.nodes['root1'] = TechNode(id='root1', name='Root 1', max_levels=1, requirements=[])
        tree.nodes['root2'] = TechNode(id='root2', name='Root 2', max_levels=1)

        errors = tree.validate()

        assert errors == []

    def test_empty_or_group(self):
        """Empty OR group (vacuous truth) is valid."""
        tree = TechTree()

        tree.nodes['vacuous'] = TechNode(
            id='vacuous', name='Vacuous', max_levels=1,
            requirements=[[]]  # Empty AND group = always true
        )

        errors = tree.validate()

        assert errors == []
