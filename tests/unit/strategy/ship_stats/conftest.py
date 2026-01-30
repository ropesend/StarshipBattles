"""
Shared fixtures for ShipStatsCalculator tests.

PROJ-48: Extracted from test_ship_stats_calculator.py during test file splitting.
"""

import pytest
from game.core.registry import GameRegistries


def create_mock_registries(components=None, modifiers=None):
    """Create a mock GameRegistries for testing.

    PROJ-42: Tests now use instance methods with injected registries.
    """
    return GameRegistries(
        components=components or {},
        modifiers=modifiers or {},
        vehicle_classes={},
        resources={}
    )


class MockComponent:
    """Mock component for testing without full registry."""

    def __init__(
        self,
        comp_id: str,
        mass: float = 100,
        max_hp: float = 100,
        abilities: dict = None,
        type_str: str = 'Generic',
        damage_threshold: float = 0.3
    ):
        self.id = comp_id
        self.mass = mass
        self.max_hp = max_hp
        self.abilities = abilities or {}
        self.type_str = type_str
        self.damage_threshold = damage_threshold


def make_design_data(components_by_layer: dict) -> dict:
    """Helper to create design_data structure for testing."""
    layers = {}
    for layer_name, comp_ids in components_by_layer.items():
        layers[layer_name] = [{'id': cid} for cid in comp_ids]
    return {'layers': layers}
