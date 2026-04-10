"""
Tests for configuration module.

These configuration classes centralize magic numbers and constants
used throughout the codebase.
"""
import pytest


class TestDisplayConfig:
    """Tests for DisplayConfig."""

    def test_default_resolution_tuple(self):
        """default_resolution() returns tuple (4K)."""
        from game.core.config import DisplayConfig

        resolution = DisplayConfig.default_resolution()
        assert resolution == (3840, 2160)
        assert isinstance(resolution, tuple)

    def test_test_resolution_tuple(self):
        """test_resolution() returns tuple."""
        from game.core.config import DisplayConfig

        resolution = DisplayConfig.test_resolution()
        assert resolution == (1440, 900)
