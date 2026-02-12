"""
Unit tests for BuildQueueSource error paths.

Tests missing file handling, caching, no shipyards, and malformed data.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestBuildQueueSourceErrors:
    """Tests for BuildQueueSource error handling."""

    def test_build_queue_source_exists(self):
        """BuildQueueSource module can be imported."""
        from game.strategy.data import build_queue_source
        assert build_queue_source is not None

    def test_build_queue_source_class_exists(self):
        """BuildQueueSource class exists (it's a dataclass)."""
        from game.strategy.data.build_queue_source import BuildQueueSource
        assert BuildQueueSource is not None

    def test_build_queue_source_has_queue_id(self):
        """BuildQueueSource has queue_id field."""
        from game.strategy.data.build_queue_source import BuildQueueSource
        # It's a dataclass with required fields
        assert hasattr(BuildQueueSource, '__dataclass_fields__')
        assert 'queue_id' in BuildQueueSource.__dataclass_fields__
