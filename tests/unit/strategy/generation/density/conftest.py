"""
Fixtures for density primitive tests.
"""

import pytest
import random

from game.strategy.generation.density.primitives.radial import RadialPrimitive
from game.strategy.generation.density.primitives.ring import RingPrimitive
from game.strategy.generation.density.primitives.spiral_arm import SpiralArmPrimitive
from game.strategy.generation.density.primitives.linear import LinearPrimitive
from game.strategy.generation.density.primitives.noise import NoisePrimitive
from game.strategy.generation.density.primitives.geometric import GeometricPrimitive
from game.strategy.generation.density.density_map import DensityMap


@pytest.fixture
def radial_primitive():
    """Standard radial primitive for testing."""
    return RadialPrimitive(center_q=0, center_r=0, sigma=100, peak_density=1.0)


@pytest.fixture
def ring_primitive():
    """Standard ring primitive for testing."""
    return RingPrimitive(center_q=0, center_r=0, radius=500, width=50, peak_density=1.0)


@pytest.fixture
def spiral_arm_primitive():
    """Standard spiral arm primitive for testing."""
    return SpiralArmPrimitive(
        center_q=0, center_r=0, arm_count=2, pitch_angle=25,
        arm_width=80, rotation=0, peak_density=1.0
    )


@pytest.fixture
def linear_primitive():
    """Standard linear/bar primitive for testing."""
    return LinearPrimitive(
        center_q=0, center_r=0, length=400, width=50,
        rotation=0, peak_density=1.0
    )


@pytest.fixture
def noise_primitive():
    """Standard noise primitive for testing."""
    return NoisePrimitive(scale=50, octaves=3, persistence=0.5, seed=42, peak_density=1.0)


@pytest.fixture
def geometric_primitive():
    """Standard geometric/diamond primitive for testing."""
    return GeometricPrimitive(
        center_q=0, center_r=0, sides=4, radius=400,
        rotation=0.785, edge_falloff=30, peak_density=1.0
    )


@pytest.fixture
def seeded_rng():
    """Seeded random number generator for reproducible tests."""
    return random.Random(12345)


@pytest.fixture
def empty_density_map():
    """Empty DensityMap for testing."""
    return DensityMap(radius=1000)


@pytest.fixture
def simple_density_map(radial_primitive):
    """DensityMap with single radial primitive."""
    dm = DensityMap(radius=1000)
    dm.add_primitive(radial_primitive, weight=1.0)
    return dm


@pytest.fixture(params=[
    ('radial', RadialPrimitive, {'sigma': 100, 'peak_density': 1.0}),
    ('ring', RingPrimitive, {'radius': 300, 'width': 50, 'peak_density': 1.0}),
    ('spiral_arm', SpiralArmPrimitive, {'arm_count': 2, 'pitch_angle': 20, 'arm_width': 60, 'peak_density': 1.0}),
    ('linear', LinearPrimitive, {'length': 300, 'width': 40, 'peak_density': 1.0}),
    ('noise', NoisePrimitive, {'scale': 50, 'octaves': 2, 'seed': 42, 'peak_density': 1.0}),
    ('geometric', GeometricPrimitive, {'sides': 4, 'radius': 300, 'edge_falloff': 20, 'peak_density': 1.0}),
], ids=lambda x: x[0])
def all_primitive_types(request):
    """Parametrized fixture providing all primitive types."""
    name, cls, kwargs = request.param
    return name, cls(**kwargs)
