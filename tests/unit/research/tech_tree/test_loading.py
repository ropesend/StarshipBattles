"""
Unit tests for TechTree - Loading and requirements.

Tests cover:
- Tree loading from JSON/data files
- Requirement parsing and resolution
"""
import pytest
import json
import tempfile
import os

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
