"""Tests for production completion and shipyard requirements."""
import pytest
from unittest.mock import MagicMock, patch


class TestProductionCompletion:
    """Tests for production completion (turns reach zero)."""

    def test_production_completes_at_zero(self, mock_empire, mock_planet, mock_galaxy):
        """Production completes when turns reach zero."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 1}]
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_ship') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()
            assert len(mock_planet.construction_queue) == 0

    def test_complex_production_completes(self, mock_empire, mock_planet, mock_galaxy):
        """Complex production completes when turns reach zero."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "complex", "design_id": "Factory", "turns_remaining": 1}]
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_complex') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()

    def test_dict_format_default_type_is_ship(self, mock_empire, mock_planet, mock_galaxy):
        """Dict format without 'type' key defaults to ship type."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"design_id": "Scout", "turns_remaining": 1}]  # No "type" key
        mock_planet.has_space_shipyard = True
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_ship') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            # Should call _spawn_ship (default type)
            mock_spawn.assert_called()


class TestShipyardRequirements:
    """Tests for shipyard requirements on production."""

    def test_no_shipyard_pauses_ship_production(self, mock_empire, mock_planet):
        """Ships require shipyard to build."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "ship", "design_id": "Scout", "turns_remaining": 2}]
        mock_planet.has_space_shipyard = False
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        # Turns should NOT decrement
        assert mock_planet.construction_queue[0]["turns_remaining"] == 2

    def test_no_shipyard_pauses_fighter_production(self, mock_empire, mock_planet):
        """Fighters require shipyard to build."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "fighter", "design_id": "Fighter", "turns_remaining": 2}]
        mock_planet.has_space_shipyard = False
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 2

    def test_no_shipyard_pauses_satellite_production(self, mock_empire, mock_planet):
        """Satellites require shipyard to build."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "satellite", "design_id": "Satellite", "turns_remaining": 2}]
        mock_planet.has_space_shipyard = False
        mock_empire.colonies = [mock_planet]

        engine.process_production([mock_empire])

        assert mock_planet.construction_queue[0]["turns_remaining"] == 2

    def test_complex_production_no_shipyard_needed(self, mock_empire, mock_planet, mock_galaxy):
        """Complexes don't need shipyard."""
        from game.strategy.engine.production_engine import ProductionEngine

        engine = ProductionEngine()
        mock_planet.construction_queue = [{"type": "complex", "design_id": "Factory", "turns_remaining": 1}]
        mock_planet.has_space_shipyard = False
        mock_empire.colonies = [mock_planet]

        with patch.object(engine, '_spawn_complex') as mock_spawn:
            engine.process_production([mock_empire], mock_galaxy)

            mock_spawn.assert_called()
