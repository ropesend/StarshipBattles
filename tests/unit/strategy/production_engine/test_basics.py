"""Tests for ProductionEngine creation, empty queues, and turn decrement."""
import pytest
from unittest.mock import MagicMock


class TestProductionEngineCreation:
    """Tests for ProductionEngine initialization."""

    def test_production_engine_can_be_created(self):
        """ProductionEngine can be instantiated."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()

        assert engine is not None

    def test_production_engine_has_process_production(self):
        """ProductionEngine has process_production method."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()

        assert hasattr(engine, 'process_production')
        assert callable(engine.process_production)


class TestEmptyQueueHandling:
    """Tests for colonies with empty construction queues."""

    def test_empty_queue_skipped(self, mock_empire, mock_planet):
        """Colonies with empty queues are skipped."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = []
        mock_empire.colonies = [mock_planet]

        # Should not raise any errors
        engine.process_production([mock_empire])

    def test_no_colonies_handled(self, mock_empire):
        """Empire with no colonies processes without error."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_empire.colonies = []

        engine.process_production([mock_empire])


class TestProductionTurnDecrement:
    """Tests for turn decrement in construction queue."""

    def test_production_decrements_turns_dict_format(self, mock_empire, mock_planet):
        """Production decrements turns remaining (dict format)."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 3}]
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 2


class TestDictFormatSupport:
    """Tests for dict format production queue items."""

    def test_dict_format_supported(self, mock_empire, mock_planet):
        """Dict format is fully supported."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [
            {"type": "ship", "design_id": "Cruiser", "turns_remaining": 5}
        ]
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 4
