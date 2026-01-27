"""
Unit tests for TechTree.

Tests cover:
- Tree loading from JSON/data files
- Tree validation (orphan nodes, valid connections)
- Depth calculation for layout
- Available nodes calculation
- Tree traversal methods
- Error handling for malformed tree data
"""
import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock

from game.research.data.tech_tree import TechTree
from game.research.data.tech_node import TechNode, TechRequirement


class TestTechTreeBasic:
    """Tests for basic TechTree functionality."""

    def test_empty_initialization(self):
        """TechTree initializes empty."""
        tree = TechTree()

        assert tree.nodes == {}
        assert tree._depth_cache == {}

    def test_add_node_directly(self):
        """Nodes can be added directly to tree.nodes."""
        tree = TechTree()
        node = TechNode(id='test', name='Test Node', max_levels=5)
        tree.nodes['test'] = node

        assert 'test' in tree.nodes
        assert tree.nodes['test'] is node


class TestTechTreeLoadFromJson:
    """Tests for JSON loading."""

    def test_load_empty_tree(self):
        """Loading empty JSON creates empty tree."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"tech_tree": []}, f)
            f.flush()
            filepath = f.name

        try:
            tree = TechTree.load_from_json(filepath)
            assert tree.nodes == {}
        finally:
            os.unlink(filepath)

    def test_load_single_node(self):
        """Loading single node from JSON."""
        data = {
            "tech_tree": [
                {
                    "id": "basic_tech",
                    "name": "Basic Technology",
                    "max_levels": 3
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            f.flush()
            filepath = f.name

        try:
            tree = TechTree.load_from_json(filepath)
            assert 'basic_tech' in tree.nodes
            node = tree.nodes['basic_tech']
            assert node.name == "Basic Technology"
            assert node.max_levels == 3
        finally:
            os.unlink(filepath)

    def test_load_node_with_all_fields(self):
        """Loading node with all optional fields."""
        data = {
            "tech_tree": [
                {
                    "id": "advanced",
                    "name": "Advanced Tech",
                    "max_levels": 5,
                    "base_decay": 0.01,
                    "volatility": 0.2,
                    "price": 2.0,
                    "price_curve": "quadratic",
                    "comment": "Section: Testing"
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            f.flush()
            filepath = f.name

        try:
            tree = TechTree.load_from_json(filepath)
            node = tree.nodes['advanced']
            assert node.base_decay == 0.01
            assert node.volatility == 0.2
            assert node.price == 2.0
            assert node.price_curve == "quadratic"
            assert node.comment == "Section: Testing"
        finally:
            os.unlink(filepath)

    def test_load_node_with_requirements_level_range(self):
        """Loading node with fuzzy level_range requirements."""
        data = {
            "tech_tree": [
                {"id": "root", "name": "Root", "max_levels": 3},
                {
                    "id": "child",
                    "name": "Child",
                    "max_levels": 2,
                    "requirements": [
                        [{"node_id": "root", "level_range": [1, 3]}]
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            f.flush()
            filepath = f.name

        try:
            tree = TechTree.load_from_json(filepath)
            child = tree.nodes['child']
            assert len(child.requirements) == 1
            assert len(child.requirements[0]) == 1
            req = child.requirements[0][0]
            assert req.node_id == "root"
            assert req.level_range == (1, 3)
        finally:
            os.unlink(filepath)

    def test_load_node_with_requirements_single_level(self):
        """Loading node with single level requirement (same min/max)."""
        data = {
            "tech_tree": [
                {"id": "root", "name": "Root", "max_levels": 3},
                {
                    "id": "child",
                    "name": "Child",
                    "max_levels": 2,
                    "requirements": [
                        [{"node_id": "root", "level_range": [2, 2]}]
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            f.flush()
            filepath = f.name

        try:
            tree = TechTree.load_from_json(filepath)
            child = tree.nodes['child']
            req = child.requirements[0][0]
            assert req.level_range == (2, 2)
        finally:
            os.unlink(filepath)

    def test_load_node_with_requirements_default_level(self):
        """Loading requirement without level defaults to (1, 1)."""
        data = {
            "tech_tree": [
                {"id": "root", "name": "Root", "max_levels": 3},
                {
                    "id": "child",
                    "name": "Child",
                    "max_levels": 2,
                    "requirements": [
                        [{"node_id": "root"}]  # No level specified
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            f.flush()
            filepath = f.name

        try:
            tree = TechTree.load_from_json(filepath)
            child = tree.nodes['child']
            req = child.requirements[0][0]
            assert req.level_range == (1, 1)
        finally:
            os.unlink(filepath)

    def test_load_skips_comment_entries(self):
        """Comment-only entries (no id) are skipped."""
        data = {
            "tech_tree": [
                {"comment": "This is a section header"},
                {"id": "real_tech", "name": "Real Tech", "max_levels": 1}
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            f.flush()
            filepath = f.name

        try:
            tree = TechTree.load_from_json(filepath)
            assert len(tree.nodes) == 1
            assert 'real_tech' in tree.nodes
        finally:
            os.unlink(filepath)

    def test_load_skips_entries_without_required_fields(self):
        """Entries without id or name are skipped."""
        data = {
            "tech_tree": [
                {"id": "valid", "name": "Valid"},
                {"id": "missing_name"},  # No name
                {"name": "Missing ID"},  # No id
                {}  # Empty
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            f.flush()
            filepath = f.name

        try:
            tree = TechTree.load_from_json(filepath)
            assert len(tree.nodes) == 1
            assert 'valid' in tree.nodes
        finally:
            os.unlink(filepath)

    def test_load_with_complex_requirements(self):
        """Loading OR/AND requirement structure."""
        data = {
            "tech_tree": [
                {"id": "a", "name": "A", "max_levels": 1},
                {"id": "b", "name": "B", "max_levels": 1},
                {"id": "c", "name": "C", "max_levels": 1},
                {
                    "id": "complex",
                    "name": "Complex",
                    "max_levels": 1,
                    "requirements": [
                        [{"node_id": "a"}, {"node_id": "b"}],  # A AND B
                        [{"node_id": "c", "level": 2}]         # OR C@2
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            f.flush()
            filepath = f.name

        try:
            tree = TechTree.load_from_json(filepath)
            complex_node = tree.nodes['complex']
            assert len(complex_node.requirements) == 2
            assert len(complex_node.requirements[0]) == 2  # A AND B
            assert len(complex_node.requirements[1]) == 1  # C
        finally:
            os.unlink(filepath)

    def test_load_missing_file_returns_empty_tree(self):
        """Loading non-existent file returns empty tree (via load_json default)."""
        tree = TechTree.load_from_json("/nonexistent/path/techtree.json")
        assert tree.nodes == {}

    def test_load_default_values(self):
        """Nodes get default values for optional fields."""
        data = {
            "tech_tree": [
                {"id": "minimal", "name": "Minimal"}
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            f.flush()
            filepath = f.name

        try:
            tree = TechTree.load_from_json(filepath)
            node = tree.nodes['minimal']
            assert node.max_levels == 1
            assert node.base_decay == 0.005
            assert node.volatility == 0.1
            assert node.price == 1.0
            assert node.price_curve == "flat"
        finally:
            os.unlink(filepath)


class TestTechTreeResolveRequirements:
    """Tests for requirement resolution."""

    def test_resolve_all_requirements(self):
        """resolve_all_requirements resolves all nodes."""
        tree = TechTree()
        req1 = TechRequirement('a', (1, 5))
        req2 = TechRequirement('b', (2, 4))

        tree.nodes['a'] = TechNode(id='a', name='A', max_levels=5)
        tree.nodes['b'] = TechNode(id='b', name='B', max_levels=5)
        tree.nodes['c'] = TechNode(id='c', name='C', max_levels=5, requirements=[[req1, req2]])

        tree.resolve_all_requirements(seed=12345)

        # All requirements should be resolved
        assert req1.resolved_level is not None
        assert 1 <= req1.resolved_level <= 5
        assert req2.resolved_level is not None
        assert 2 <= req2.resolved_level <= 4

    def test_resolve_deterministic(self):
        """Resolution is deterministic with same seed."""
        def create_tree():
            tree = TechTree()
            req = TechRequirement('a', (1, 10))
            tree.nodes['a'] = TechNode(id='a', name='A', max_levels=10)
            tree.nodes['b'] = TechNode(id='b', name='B', max_levels=5, requirements=[[req]])
            return tree

        tree1 = create_tree()
        tree2 = create_tree()

        tree1.resolve_all_requirements(seed=42)
        tree2.resolve_all_requirements(seed=42)

        assert tree1.nodes['b'].requirements[0][0].resolved_level == \
               tree2.nodes['b'].requirements[0][0].resolved_level


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
