"""Tests for the shared label formatter (PROJ-300 D15)."""
from game.strategy.services.ability_sources import format_intrinsic_source_label


def test_planet_label():
    assert format_intrinsic_source_label(
        entity_name="Tarsis IV", type_name="Volcanic"
    ) == "Tarsis IV (Volcanic)"


def test_star_label():
    assert format_intrinsic_source_label(
        entity_name="Sol", type_name="G-class"
    ) == "Sol (G-class)"


def test_warp_point_label():
    assert format_intrinsic_source_label(
        entity_name="Warp Point Alpha", type_name="unstable"
    ) == "Warp Point Alpha (unstable)"


def test_keyword_only_args():
    """Helper requires keyword-only args to prevent positional confusion."""
    import pytest
    with pytest.raises(TypeError):
        format_intrinsic_source_label("Tarsis IV", "Volcanic")  # type: ignore[misc]
