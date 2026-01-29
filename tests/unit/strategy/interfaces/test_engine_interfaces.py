"""
Tests for strategy engine interfaces.

PROJ-43 Phase 4: Interface contracts for TurnEngine sub-engines.
Tests written BEFORE implementation (Strict TDD).

These interfaces enable:
- Constructor dependency injection in TurnEngine
- Unit testing with mock engines
- Clean separation of concerns
"""
import pytest
from abc import ABC
from typing import List, Optional, Tuple
from unittest.mock import MagicMock


# =============================================================================
# IMovementEngine Interface Tests
# =============================================================================


class TestIMovementEngineInterface:
    """Test IMovementEngine abstract base class interface contract."""

    def test_imovement_engine_importable(self):
        """IMovementEngine should be importable from interfaces module."""
        from game.strategy.interfaces.engines import IMovementEngine
        assert IMovementEngine is not None

    def test_imovement_engine_is_abstract(self):
        """IMovementEngine should be an abstract base class."""
        from game.strategy.interfaces.engines import IMovementEngine
        assert issubclass(IMovementEngine, ABC)

    def test_imovement_engine_cannot_instantiate(self):
        """IMovementEngine should not be directly instantiable."""
        from game.strategy.interfaces.engines import IMovementEngine
        with pytest.raises(TypeError):
            IMovementEngine()

    def test_imovement_engine_has_collect_movements_method(self):
        """IMovementEngine should define collect_movements abstract method."""
        from game.strategy.interfaces.engines import IMovementEngine
        assert hasattr(IMovementEngine, 'collect_movements')
        assert getattr(IMovementEngine.collect_movements, '__isabstractmethod__', False)

    def test_imovement_engine_has_apply_movements_method(self):
        """IMovementEngine should define apply_movements abstract method."""
        from game.strategy.interfaces.engines import IMovementEngine
        assert hasattr(IMovementEngine, 'apply_movements')
        assert getattr(IMovementEngine.apply_movements, '__isabstractmethod__', False)

    def test_imovement_engine_has_calculate_next_hex_method(self):
        """IMovementEngine should define calculate_next_hex abstract method."""
        from game.strategy.interfaces.engines import IMovementEngine
        assert hasattr(IMovementEngine, 'calculate_next_hex')
        assert getattr(IMovementEngine.calculate_next_hex, '__isabstractmethod__', False)


# =============================================================================
# IProductionEngine Interface Tests
# =============================================================================


class TestIProductionEngineInterface:
    """Test IProductionEngine abstract base class interface contract."""

    def test_iproduction_engine_importable(self):
        """IProductionEngine should be importable from interfaces module."""
        from game.strategy.interfaces.engines import IProductionEngine
        assert IProductionEngine is not None

    def test_iproduction_engine_is_abstract(self):
        """IProductionEngine should be an abstract base class."""
        from game.strategy.interfaces.engines import IProductionEngine
        assert issubclass(IProductionEngine, ABC)

    def test_iproduction_engine_cannot_instantiate(self):
        """IProductionEngine should not be directly instantiable."""
        from game.strategy.interfaces.engines import IProductionEngine
        with pytest.raises(TypeError):
            IProductionEngine()

    def test_iproduction_engine_has_process_production_method(self):
        """IProductionEngine should define process_production abstract method."""
        from game.strategy.interfaces.engines import IProductionEngine
        assert hasattr(IProductionEngine, 'process_production')
        assert getattr(IProductionEngine.process_production, '__isabstractmethod__', False)


# =============================================================================
# IOrderProcessor Interface Tests
# =============================================================================


class TestIOrderProcessorInterface:
    """Test IOrderProcessor abstract base class interface contract."""

    def test_iorder_processor_importable(self):
        """IOrderProcessor should be importable from interfaces module."""
        from game.strategy.interfaces.engines import IOrderProcessor
        assert IOrderProcessor is not None

    def test_iorder_processor_is_abstract(self):
        """IOrderProcessor should be an abstract base class."""
        from game.strategy.interfaces.engines import IOrderProcessor
        assert issubclass(IOrderProcessor, ABC)

    def test_iorder_processor_cannot_instantiate(self):
        """IOrderProcessor should not be directly instantiable."""
        from game.strategy.interfaces.engines import IOrderProcessor
        with pytest.raises(TypeError):
            IOrderProcessor()

    def test_iorder_processor_has_process_instant_orders_method(self):
        """IOrderProcessor should define process_instant_orders abstract method."""
        from game.strategy.interfaces.engines import IOrderProcessor
        assert hasattr(IOrderProcessor, 'process_instant_orders')
        assert getattr(IOrderProcessor.process_instant_orders, '__isabstractmethod__', False)

    def test_iorder_processor_has_process_end_turn_orders_method(self):
        """IOrderProcessor should define process_end_turn_orders abstract method."""
        from game.strategy.interfaces.engines import IOrderProcessor
        assert hasattr(IOrderProcessor, 'process_end_turn_orders')
        assert getattr(IOrderProcessor.process_end_turn_orders, '__isabstractmethod__', False)


# =============================================================================
# IConflictEngine Interface Tests
# =============================================================================


class TestIConflictEngineInterface:
    """Test IConflictEngine abstract base class interface contract."""

    def test_iconflict_engine_importable(self):
        """IConflictEngine should be importable from interfaces module."""
        from game.strategy.interfaces.engines import IConflictEngine
        assert IConflictEngine is not None

    def test_iconflict_engine_is_abstract(self):
        """IConflictEngine should be an abstract base class."""
        from game.strategy.interfaces.engines import IConflictEngine
        assert issubclass(IConflictEngine, ABC)

    def test_iconflict_engine_cannot_instantiate(self):
        """IConflictEngine should not be directly instantiable."""
        from game.strategy.interfaces.engines import IConflictEngine
        with pytest.raises(TypeError):
            IConflictEngine()

    def test_iconflict_engine_has_resolve_all_conflicts_method(self):
        """IConflictEngine should define resolve_all_conflicts abstract method."""
        from game.strategy.interfaces.engines import IConflictEngine
        assert hasattr(IConflictEngine, 'resolve_all_conflicts')
        assert getattr(IConflictEngine.resolve_all_conflicts, '__isabstractmethod__', False)


# =============================================================================
# IResourceEngine Interface Tests
# =============================================================================


class TestIResourceEngineInterface:
    """Test IResourceEngine abstract base class interface contract."""

    def test_iresource_engine_importable(self):
        """IResourceEngine should be importable from interfaces module."""
        from game.strategy.interfaces.engines import IResourceEngine
        assert IResourceEngine is not None

    def test_iresource_engine_is_abstract(self):
        """IResourceEngine should be an abstract base class."""
        from game.strategy.interfaces.engines import IResourceEngine
        assert issubclass(IResourceEngine, ABC)

    def test_iresource_engine_cannot_instantiate(self):
        """IResourceEngine should not be directly instantiable."""
        from game.strategy.interfaces.engines import IResourceEngine
        with pytest.raises(TypeError):
            IResourceEngine()

    def test_iresource_engine_has_process_per_turn_consumption_method(self):
        """IResourceEngine should define process_per_turn_consumption abstract method."""
        from game.strategy.interfaces.engines import IResourceEngine
        assert hasattr(IResourceEngine, 'process_per_turn_consumption')
        assert getattr(IResourceEngine.process_per_turn_consumption, '__isabstractmethod__', False)


# =============================================================================
# Concrete Implementation Tests
# =============================================================================


class TestConcreteImplementations:
    """Test that concrete implementations can be created."""

    def test_concrete_movement_engine_implementation(self):
        """Concrete IMovementEngine implementation should work."""
        from game.strategy.interfaces.engines import IMovementEngine

        class MockMovementEngine(IMovementEngine):
            def collect_movements(self, empires, galaxy, tick):
                return []

            def apply_movements(self, move_queue, galaxy):
                return []

            def calculate_next_hex(self, fleet, galaxy):
                return None

        engine = MockMovementEngine()
        assert engine is not None
        assert engine.collect_movements([], None, 1) == []

    def test_concrete_production_engine_implementation(self):
        """Concrete IProductionEngine implementation should work."""
        from game.strategy.interfaces.engines import IProductionEngine

        class MockProductionEngine(IProductionEngine):
            def process_production(self, empires, galaxy=None, save_path=None):
                pass

        engine = MockProductionEngine()
        assert engine is not None

    def test_concrete_order_processor_implementation(self):
        """Concrete IOrderProcessor implementation should work."""
        from game.strategy.interfaces.engines import IOrderProcessor

        class MockOrderProcessor(IOrderProcessor):
            def process_instant_orders(self, empires):
                return []

            def process_end_turn_orders(self, fleet, empire, galaxy):
                return False

        processor = MockOrderProcessor()
        assert processor is not None

    def test_concrete_conflict_engine_implementation(self):
        """Concrete IConflictEngine implementation should work."""
        from game.strategy.interfaces.engines import IConflictEngine

        class MockConflictEngine(IConflictEngine):
            def resolve_all_conflicts(self, empires):
                return MagicMock()

        engine = MockConflictEngine()
        assert engine is not None

    def test_concrete_resource_engine_implementation(self):
        """Concrete IResourceEngine implementation should work."""
        from game.strategy.interfaces.engines import IResourceEngine

        class MockResourceEngine(IResourceEngine):
            def process_per_turn_consumption(self, tick, empires):
                return []

        engine = MockResourceEngine()
        assert engine is not None


# =============================================================================
# Module Re-exports Test
# =============================================================================


class TestInterfacesModuleExports:
    """Test that interfaces module properly exports all engine interfaces."""

    def test_all_engine_interfaces_accessible_from_interfaces_package(self):
        """All engine interfaces should be accessible from game.strategy.interfaces."""
        from game.strategy.interfaces import (
            IMovementEngine,
            IProductionEngine,
            IOrderProcessor,
            IConflictEngine,
            IResourceEngine,
        )
        assert IMovementEngine is not None
        assert IProductionEngine is not None
        assert IOrderProcessor is not None
        assert IConflictEngine is not None
        assert IResourceEngine is not None

    def test_engines_module_exports_via_all(self):
        """engines.py should export all interfaces via __all__."""
        from game.strategy.interfaces import engines
        assert hasattr(engines, '__all__')
        assert 'IMovementEngine' in engines.__all__
        assert 'IProductionEngine' in engines.__all__
        assert 'IOrderProcessor' in engines.__all__
        assert 'IConflictEngine' in engines.__all__
        assert 'IResourceEngine' in engines.__all__
