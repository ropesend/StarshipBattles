"""Tests for TurnEngineConfig — frozen dataclass bundling optional engine parameters."""
import dataclasses
from unittest.mock import MagicMock

import pytest

from game.strategy.engine.turn_engine_config import TurnEngineConfig


class TestTurnEngineConfigDefaults:
    """Test default values."""

    def test_all_fields_default_to_none(self):
        config = TurnEngineConfig()
        for field in dataclasses.fields(config):
            assert getattr(config, field.name) is None, f"{field.name} should default to None"

    def test_is_frozen(self):
        config = TurnEngineConfig()
        with pytest.raises(dataclasses.FrozenInstanceError):
            config.movement_engine = MagicMock()

    def test_field_count(self):
        """TurnEngineConfig should have exactly 14 optional engine fields.

        PROJ-284 Phase 2 added `organics_consumption_engine` (14th).
        """
        assert len(dataclasses.fields(TurnEngineConfig())) == 14


class TestTurnEngineConfigCustomValues:
    """Test with custom engine values."""

    def test_accepts_mock_engines(self):
        mock_movement = MagicMock()
        mock_production = MagicMock()
        config = TurnEngineConfig(
            movement_engine=mock_movement,
            production_engine=mock_production,
        )
        assert config.movement_engine is mock_movement
        assert config.production_engine is mock_production

    def test_partial_fields(self):
        """Only specified fields are set, rest remain None."""
        config = TurnEngineConfig(conflict_engine=MagicMock())
        assert config.conflict_engine is not None
        assert config.movement_engine is None
        assert config.production_engine is None

    def test_all_fields_can_be_set(self):
        mocks = {field.name: MagicMock() for field in dataclasses.fields(TurnEngineConfig())}
        config = TurnEngineConfig(**mocks)
        for field_name, mock in mocks.items():
            assert getattr(config, field_name) is mock
