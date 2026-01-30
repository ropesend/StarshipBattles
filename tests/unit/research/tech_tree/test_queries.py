"""
Unit tests for TechTree - Queries, depth, and validation.

Tests cover:
- Depth calculation for layout
- Tree query methods
- Tree validation (orphan nodes, valid connections)
"""
import pytest

from game.research.data.tech_tree import TechTree
from game.research.data.tech_node import TechNode, TechRequirement


class TestTechTreeDepthCalculation:
    """Tests for depth calculation."""

    def test_depth_root_node(self):
        """Root nodes (no requirements) have depth 0."""
        tree = TechTree()
        tree.nodes['root'] = TechNode(id='root', name='Root', max_levels=5)

        assert tree.calculate_depth('root') == 0

    def test_depth_single_dependency(self):
        """Single dependency adds 1 to depth."""
        tree = TechTree()
        req = TechRequirement('root', (1, 1))
        tree.nodes['root'] = TechNode(id='root', name='Root', max_levels=5)
        tree.nodes['child'] = TechNode(id='child', name='Child', max_levels=5, requirements=[[req]])

        assert tree.calculate_depth('root') == 0
        assert tree.calculate_depth('child') == 1

    def test_depth_chain(self):
        """Chain of dependencies increases depth linearly."""
        tree = TechTree()
        tree.nodes['level0'] = TechNode(id='level0', name='L0', max_levels=1)

        req1 = TechRequirement('level0', (1, 1))
        tree.nodes['level1'] = TechNode(id='level1', name='L1', max_levels=1, requirements=[[req1]])

        req2 = TechRequirement('level1', (1, 1))
        tree.nodes['level2'] = TechNode(id='level2', name='L2', max_levels=1, requirements=[[req2]])

        assert tree.calculate_depth('level0') == 0
        assert tree.calculate_depth('level1') == 1
        assert tree.calculate_depth('level2') == 2

    def test_depth_multiple_prerequisites(self):
        """Depth is max of prerequisites + 1."""
        tree = TechTree()
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1)  # depth 0
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1)  # depth 0

        req_a = TechRequirement('a', (1, 1))
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=1, requirements=[[req_a]])  # depth 1

        req_b = TechRequirement('b', (1, 1))
        req_c = TechRequirement('c', (1, 1))
        # Depends on both B (depth 0) and C (depth 1)
        tree.nodes['d'] = TechNode(id='d', name='D', max_levels=1, requirements=[[req_b, req_c]])

        # max(0, 1) + 1 = 2
        assert tree.calculate_depth('d') == 2

    def test_depth_or_groups(self):
        """OR groups: max across all prerequisites."""
        tree = TechTree()
        tree.nodes['shallow'] = TechNode(id='shallow', name='Shallow', max_levels=1)

        req_shallow = TechRequirement('shallow', (1, 1))
        tree.nodes['deep'] = TechNode(id='deep', name='Deep', max_levels=1, requirements=[[req_shallow]])

        req_deep = TechRequirement('deep', (1, 1))
        # OR: shallow (depth 0) OR deep (depth 1)
        tree.nodes['choice'] = TechNode(id='choice', name='Choice', max_levels=1,
                                        requirements=[[req_shallow], [req_deep]])

        # max(0, 1) + 1 = 2
        assert tree.calculate_depth('choice') == 2

    def test_depth_nonexistent_node(self):
        """Nonexistent node returns depth 0."""
        tree = TechTree()
        assert tree.calculate_depth('nonexistent') == 0

    def test_depth_caching(self):
        """Depth calculation is cached."""
        tree = TechTree()
        tree.nodes['root'] = TechNode(id='root', name='Root', max_levels=1)

        # First calculation
        depth1 = tree.calculate_depth('root')
        assert 'root' in tree._depth_cache

        # Should return cached value
        depth2 = tree.calculate_depth('root')
        assert depth1 == depth2

    def test_depth_dangling_reference(self):
        """Depth calculation handles dangling references gracefully."""
        tree = TechTree()
        req = TechRequirement('nonexistent', (1, 1))
        tree.nodes['orphan'] = TechNode(id='orphan', name='Orphan', max_levels=1, requirements=[[req]])

        # Should not crash, nonexistent node treated as depth 0
        assert tree.calculate_depth('orphan') == 1


class TestTechTreeQueries:
    """Tests for tree query methods."""

    def test_get_nodes_at_depth(self):
        """get_nodes_at_depth returns correct nodes."""
        tree = TechTree()
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1)
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1)

        req = TechRequirement('a', (1, 1))
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=1, requirements=[[req]])

        depth_0 = tree.get_nodes_at_depth(0)
        depth_1 = tree.get_nodes_at_depth(1)
        depth_2 = tree.get_nodes_at_depth(2)

        assert len(depth_0) == 2
        assert set(n.id for n in depth_0) == {'a', 'b'}
        assert len(depth_1) == 1
        assert depth_1[0].id == 'c'
        assert len(depth_2) == 0

    def test_get_max_depth_empty(self):
        """get_max_depth returns 0 for empty tree."""
        tree = TechTree()
        assert tree.get_max_depth() == 0

    def test_get_max_depth(self):
        """get_max_depth returns correct maximum."""
        tree = TechTree()
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1)

        req = TechRequirement('a', (1, 1))
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1, requirements=[[req]])

        req2 = TechRequirement('b', (1, 1))
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=1, requirements=[[req2]])

        assert tree.get_max_depth() == 2

    def test_get_node_exists(self):
        """get_node returns node if exists."""
        tree = TechTree()
        node = TechNode(id='test', name='Test', max_levels=1)
        tree.nodes['test'] = node

        result = tree.get_node('test')
        assert result is node

    def test_get_node_not_exists(self):
        """get_node returns None if not exists."""
        tree = TechTree()
        assert tree.get_node('nonexistent') is None

    def test_get_all_node_ids(self):
        """get_all_node_ids returns all IDs."""
        tree = TechTree()
        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=1)
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=1)
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=1)

        ids = tree.get_all_node_ids()
        assert set(ids) == {'a', 'b', 'c'}

    def test_get_all_node_ids_empty(self):
        """get_all_node_ids returns empty list for empty tree."""
        tree = TechTree()
        assert tree.get_all_node_ids() == []


class TestTechTreeValidation:
    """Tests for tree validation."""

    def test_validate_valid_tree(self):
        """validate_requirements returns empty list for valid tree."""
        tree = TechTree()
        tree.nodes['root'] = TechNode(id='root', name='Root', max_levels=1)

        req = TechRequirement('root', (1, 1))
        tree.nodes['child'] = TechNode(id='child', name='Child', max_levels=1, requirements=[[req]])

        errors = tree.validate_requirements()
        assert errors == []

    def test_validate_missing_reference(self):
        """validate_requirements catches missing node references."""
        tree = TechTree()
        req = TechRequirement('nonexistent', (1, 1))
        tree.nodes['orphan'] = TechNode(id='orphan', name='Orphan', max_levels=1, requirements=[[req]])

        errors = tree.validate_requirements()
        assert len(errors) == 1
        assert 'nonexistent' in errors[0]
        assert 'orphan' in errors[0]

    def test_validate_multiple_errors(self):
        """validate_requirements returns all errors."""
        tree = TechTree()
        req1 = TechRequirement('missing1', (1, 1))
        req2 = TechRequirement('missing2', (1, 1))
        tree.nodes['bad1'] = TechNode(id='bad1', name='Bad1', max_levels=1, requirements=[[req1]])
        tree.nodes['bad2'] = TechNode(id='bad2', name='Bad2', max_levels=1, requirements=[[req2]])

        errors = tree.validate_requirements()
        assert len(errors) == 2

    def test_validate_self_reference_valid(self):
        """Self-reference is valid (node exists)."""
        tree = TechTree()
        req = TechRequirement('self_ref', (1, 1))
        tree.nodes['self_ref'] = TechNode(id='self_ref', name='Self Ref', max_levels=5, requirements=[[req]])

        errors = tree.validate_requirements()
        assert errors == []

    def test_validate_or_groups(self):
        """Validation checks all OR groups."""
        tree = TechTree()
        tree.nodes['exists'] = TechNode(id='exists', name='Exists', max_levels=1)

        req_good = TechRequirement('exists', (1, 1))
        req_bad = TechRequirement('missing', (1, 1))

        # One OR group is valid, one is invalid
        tree.nodes['mixed'] = TechNode(id='mixed', name='Mixed', max_levels=1,
                                       requirements=[[req_good], [req_bad]])

        errors = tree.validate_requirements()
        assert len(errors) == 1
        assert 'missing' in errors[0]
