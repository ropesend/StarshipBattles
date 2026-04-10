"""
Tests for GalaxyLayoutsLoader.
"""

import pytest
import os

from game.strategy.generation.loaders.galaxy_layouts_loader import GalaxyLayoutsLoader
from game.core.exceptions import ValidationException


class TestGalaxyLayoutsLoader:
    """Tests for GalaxyLayoutsLoader."""

    @pytest.fixture
    def layouts_data(self):
        """Load the actual galaxy_layouts.json."""
        return GalaxyLayoutsLoader.load()

    def test_load_returns_dict(self, layouts_data):
        """load() should return a dict with layouts."""
        assert isinstance(layouts_data, dict)
        assert 'layouts' in layouts_data

    def test_load_contains_expected_layouts(self, layouts_data):
        """Should contain all 7 expected layout types."""
        expected = ['cluster', 'spiral', 'barred_spiral', 'ring', 'irregular', 'diamond', 'uniform']
        available = GalaxyLayoutsLoader.get_available_layouts(layouts_data)

        for layout_type in expected:
            assert layout_type in available, f"Missing layout type: {layout_type}"

    def test_get_layout_config_returns_config(self, layouts_data):
        """get_layout_config should return valid config."""
        config = GalaxyLayoutsLoader.get_layout_config('spiral', layouts_data)

        assert isinstance(config, dict)
        assert 'primitives' in config
        assert len(config['primitives']) > 0

    def test_get_layout_config_unknown_raises(self, layouts_data):
        """get_layout_config should raise for unknown type."""
        with pytest.raises(ValidationException, match="Unknown layout type"):
            GalaxyLayoutsLoader.get_layout_config('nonexistent', layouts_data)

    def test_get_available_layouts_returns_list(self, layouts_data):
        """get_available_layouts should return list of strings."""
        available = GalaxyLayoutsLoader.get_available_layouts(layouts_data)

        assert isinstance(available, list)
        assert all(isinstance(name, str) for name in available)
        assert len(available) >= 7

    def test_load_nonexistent_file_raises(self):
        """load() should raise for nonexistent file."""
        with pytest.raises(FileNotFoundError):
            GalaxyLayoutsLoader.load("nonexistent_file.json")


class TestLayoutScaling:
    """Tests for layout configuration scaling."""

    @pytest.fixture
    def layouts_data(self):
        """Load the actual galaxy_layouts.json."""
        return GalaxyLayoutsLoader.load()

    def test_scale_layout_multiplies_values(self, layouts_data):
        """Scaling should multiply relative values by radius."""
        raw_config = GalaxyLayoutsLoader.get_layout_config('spiral', layouts_data)
        scaled_config = GalaxyLayoutsLoader.scale_layout_for_radius(raw_config, galaxy_radius=1000)

        # Check that primitives were scaled
        assert 'primitives' in scaled_config
        for prim in scaled_config['primitives']:
            # sigma values should be scaled (if present)
            if 'sigma' in prim:
                # Original sigma is relative (0.15), scaled should be 150
                assert prim['sigma'] > 10  # Should be larger than relative value

    def test_scale_layout_preserves_structure(self, layouts_data):
        """Scaling should preserve config structure."""
        raw_config = GalaxyLayoutsLoader.get_layout_config('cluster', layouts_data)
        scaled_config = GalaxyLayoutsLoader.scale_layout_for_radius(raw_config, galaxy_radius=500)

        assert 'name' in scaled_config
        assert 'primitives' in scaled_config
        assert len(scaled_config['primitives']) == len(raw_config['primitives'])

    def test_load_and_scale_convenience(self):
        """load_and_scale should work as convenience method."""
        scaled = GalaxyLayoutsLoader.load_and_scale('ring', galaxy_radius=2000)

        assert 'name' in scaled
        assert 'primitives' in scaled

        # Ring radius should be scaled
        ring_prim = next(p for p in scaled['primitives'] if p.get('type') == 'ring')
        assert ring_prim['radius'] > 100  # Should be scaled from 0.7 * 2000 = 1400


class TestAllLayoutsValid:
    """Validate all layout configurations can create DensityMaps."""

    @pytest.fixture
    def layouts_data(self):
        """Load the actual galaxy_layouts.json."""
        return GalaxyLayoutsLoader.load()

    @pytest.mark.parametrize("layout_type", [
        'cluster', 'spiral', 'barred_spiral', 'ring', 'irregular', 'diamond', 'uniform'
    ])
    def test_layout_creates_density_map(self, layouts_data, layout_type):
        """Each layout should create a working DensityMap."""
        from game.strategy.generation.density.density_map import DensityMap

        scaled = GalaxyLayoutsLoader.scale_layout_for_radius(
            GalaxyLayoutsLoader.get_layout_config(layout_type, layouts_data),
            galaxy_radius=1000
        )
        dm = DensityMap.from_config(scaled, radius=1000)

        # Should have primitives
        assert len(dm) > 0

        # Should be able to evaluate
        density = dm.evaluate(0, 0)
        assert 0.0 <= density <= 1.0

    @pytest.mark.parametrize("layout_type", [
        'cluster', 'spiral', 'barred_spiral', 'ring', 'irregular', 'diamond', 'uniform'
    ])
    def test_layout_can_sample(self, layouts_data, layout_type):
        """Each layout should be able to sample coordinates."""
        from game.strategy.generation.density.density_map import DensityMap
        import random

        scaled = GalaxyLayoutsLoader.scale_layout_for_radius(
            GalaxyLayoutsLoader.get_layout_config(layout_type, layouts_data),
            galaxy_radius=500
        )
        dm = DensityMap.from_config(scaled, radius=500)

        # Should be able to sample
        rng = random.Random(42)
        coord = dm.sample(rng=rng, max_attempts=1000)

        # Should succeed (at least occasionally)
        # Note: Some sparse layouts might fail occasionally, but with 1000 attempts should work
        assert coord is not None
