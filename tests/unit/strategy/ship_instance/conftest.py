"""
Shared fixtures for ShipInstance PROJ-08 tests.

PROJ-48: Extracted from test_ship_instance_proj08.py during test file splitting.
"""

import pytest


@pytest.fixture
def make_design_data_with_stats():
    """Factory for creating design_data with expected_stats."""
    def _make(expected_stats=None):
        return {
            'layers': {},
            'name': 'TestShip',
            'expected_stats': expected_stats or {}
        }
    return _make
