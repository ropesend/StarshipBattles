"""Tests for shared density primitive helpers."""

from game.strategy.generation.density.primitives.density_primitive import clamp_density


def test_clamp_density_preserves_values_inside_range() -> None:
    assert clamp_density(0.0) == 0.0
    assert clamp_density(0.45) == 0.45
    assert clamp_density(1.0) == 1.0


def test_clamp_density_caps_values_outside_range() -> None:
    assert clamp_density(-0.25) == 0.0
    assert clamp_density(1.25) == 1.0
