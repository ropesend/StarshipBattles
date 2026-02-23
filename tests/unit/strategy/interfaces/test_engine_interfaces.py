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

    def test_iproduction_engine_has_process_construction_tick_method(self):
        """IProductionEngine.process_construction_tick must be abstract (PROJ-75)."""
        from game.strategy.interfaces.engines import IProductionEngine
        assert hasattr(IProductionEngine, 'process_construction_tick')
        assert getattr(IProductionEngine.process_construction_tick, '__isabstractmethod__', False) is True


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
# IMaintenanceEngine Interface Tests
# =============================================================================


class TestIMaintenanceEngineInterface:
    """Test IMaintenanceEngine abstract base class interface contract."""

    def test_imaintenance_engine_importable(self):
        """IMaintenanceEngine should be importable from interfaces module."""
        from game.strategy.interfaces.engines import IMaintenanceEngine
        assert IMaintenanceEngine is not None

    def test_imaintenance_engine_is_abstract(self):
        """IMaintenanceEngine should be an abstract base class."""
        from game.strategy.interfaces.engines import IMaintenanceEngine
        assert issubclass(IMaintenanceEngine, ABC)

    def test_imaintenance_engine_cannot_instantiate(self):
        """IMaintenanceEngine should not be directly instantiable."""
        from game.strategy.interfaces.engines import IMaintenanceEngine
        with pytest.raises(TypeError):
            IMaintenanceEngine()

    def test_imaintenance_engine_has_process_maintenance_method(self):
        """IMaintenanceEngine should define process_maintenance abstract method."""
        from game.strategy.interfaces.engines import IMaintenanceEngine
        assert hasattr(IMaintenanceEngine, 'process_maintenance')
        assert getattr(IMaintenanceEngine.process_maintenance, '__isabstractmethod__', False)

    def test_imaintenance_engine_has_process_maintenance_tick_method(self):
        """IMaintenanceEngine should define process_maintenance_tick abstract method (PROJ-161)."""
        from game.strategy.interfaces.engines import IMaintenanceEngine
        assert hasattr(IMaintenanceEngine, 'process_maintenance_tick')
        assert getattr(IMaintenanceEngine.process_maintenance_tick, '__isabstractmethod__', False) is True


# =============================================================================
# IPopulationEngine Interface Tests
# =============================================================================


class TestIPopulationEngineInterface:
    """Test IPopulationEngine abstract base class interface contract."""

    def test_ipopulation_engine_importable(self):
        """IPopulationEngine should be importable from interfaces module."""
        from game.strategy.interfaces.engines import IPopulationEngine
        assert IPopulationEngine is not None

    def test_ipopulation_engine_is_abstract(self):
        """IPopulationEngine should be an abstract base class."""
        from game.strategy.interfaces.engines import IPopulationEngine
        assert issubclass(IPopulationEngine, ABC)

    def test_ipopulation_engine_cannot_instantiate(self):
        """IPopulationEngine cannot be instantiated directly."""
        from game.strategy.interfaces.engines import IPopulationEngine
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IPopulationEngine()

    def test_ipopulation_engine_has_process_population_growth_method(self):
        """IPopulationEngine.process_population_growth must be abstract."""
        from game.strategy.interfaces.engines import IPopulationEngine
        assert hasattr(IPopulationEngine, 'process_population_growth')
        assert getattr(IPopulationEngine.process_population_growth, '__isabstractmethod__', False) is True


# =============================================================================
# IResupplyEngine Interface Tests
# =============================================================================


class TestIResupplyEngineInterface:
    """Test IResupplyEngine abstract base class interface contract (PROJ-74)."""

    def test_iresupply_engine_importable(self):
        """IResupplyEngine should be importable from interfaces module."""
        from game.strategy.interfaces.engines import IResupplyEngine
        assert IResupplyEngine is not None

    def test_iresupply_engine_is_abstract(self):
        """IResupplyEngine should be an abstract base class."""
        from game.strategy.interfaces.engines import IResupplyEngine
        assert issubclass(IResupplyEngine, ABC)

    def test_iresupply_engine_cannot_instantiate(self):
        """IResupplyEngine cannot be instantiated directly."""
        from game.strategy.interfaces.engines import IResupplyEngine
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IResupplyEngine()

    def test_iresupply_engine_has_process_fuel_generation_method(self):
        """IResupplyEngine.process_fuel_generation must be abstract."""
        from game.strategy.interfaces.engines import IResupplyEngine
        assert hasattr(IResupplyEngine, 'process_fuel_generation')
        assert getattr(IResupplyEngine.process_fuel_generation, '__isabstractmethod__', False) is True

    def test_iresupply_engine_has_process_fleet_resupply_method(self):
        """IResupplyEngine.process_fleet_resupply must be abstract."""
        from game.strategy.interfaces.engines import IResupplyEngine
        assert hasattr(IResupplyEngine, 'process_fleet_resupply')
        assert getattr(IResupplyEngine.process_fleet_resupply, '__isabstractmethod__', False) is True


# =============================================================================
# IHarvestingEngine Interface Tests
# =============================================================================


class TestIHarvestingEngineInterface:
    """Test IHarvestingEngine abstract base class interface contract (PROJ-75)."""

    def test_iharvesting_engine_importable(self):
        """IHarvestingEngine should be importable from interfaces module."""
        from game.strategy.interfaces.engines import IHarvestingEngine
        assert IHarvestingEngine is not None

    def test_iharvesting_engine_is_abstract(self):
        """IHarvestingEngine should be an abstract base class."""
        from game.strategy.interfaces.engines import IHarvestingEngine
        assert issubclass(IHarvestingEngine, ABC)

    def test_iharvesting_engine_cannot_instantiate(self):
        """IHarvestingEngine cannot be instantiated directly."""
        from game.strategy.interfaces.engines import IHarvestingEngine
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IHarvestingEngine()

    def test_iharvesting_engine_has_process_harvesting_method(self):
        """IHarvestingEngine.process_harvesting must be abstract."""
        from game.strategy.interfaces.engines import IHarvestingEngine
        assert hasattr(IHarvestingEngine, 'process_harvesting')
        assert getattr(IHarvestingEngine.process_harvesting, '__isabstractmethod__', False) is True


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
            def process_construction_tick(self, tick, empires, galaxy, save_path=None, harvesting_engine=None):
                """PROJ-75/79: Per-tick construction resource consumption."""
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

    def test_concrete_maintenance_engine_implementation(self):
        """Concrete IMaintenanceEngine implementation should work."""
        from game.strategy.interfaces.engines import IMaintenanceEngine

        class MockMaintenanceEngine(IMaintenanceEngine):
            def process_maintenance(self, empires):
                return []

            def process_maintenance_tick(self, tick, empires):
                return []

        engine = MockMaintenanceEngine()
        assert engine is not None
        assert engine.process_maintenance([]) == []
        assert engine.process_maintenance_tick(1, []) == []

    def test_concrete_population_engine_implementation(self):
        """Concrete IPopulationEngine with all methods implemented works."""
        from game.strategy.interfaces.engines import IPopulationEngine

        class ConcretePopulationEngine(IPopulationEngine):
            def process_population_growth(self, empires):
                pass

        engine = ConcretePopulationEngine()
        assert engine is not None

    def test_concrete_resupply_engine_implementation(self):
        """Concrete IResupplyEngine with all methods implemented works."""
        from game.strategy.interfaces.engines import IResupplyEngine

        class ConcreteResupplyEngine(IResupplyEngine):
            def process_fuel_generation(self, tick, empires):
                return []

            def process_fleet_resupply(self, tick, empires, galaxy):
                return []

        engine = ConcreteResupplyEngine()
        assert engine is not None

    def test_concrete_harvesting_engine_implementation(self):
        """Concrete IHarvestingEngine with all methods implemented works."""
        from game.strategy.interfaces.engines import IHarvestingEngine

        class ConcreteHarvestingEngine(IHarvestingEngine):
            def process_harvesting(self, empires):
                pass

            def process_harvesting_tick(self, tick, empires):
                pass

        engine = ConcreteHarvestingEngine()
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
        assert 'IMaintenanceEngine' in engines.__all__
        assert 'IPopulationEngine' in engines.__all__
        assert 'IResupplyEngine' in engines.__all__
        assert 'IHarvestingEngine' in engines.__all__

    def test_all_interfaces_in_module_all(self):
        """All engine interfaces should be listed in __all__."""
        from game.strategy.interfaces import engines
        expected_exports = [
            'IMovementEngine',
            'IProductionEngine',
            'IOrderProcessor',
            'IConflictEngine',
            'IResourceEngine',
            'IPopulationEngine',
            'IResupplyEngine',
            'IHarvestingEngine',
            'IMaintenanceEngine',
        ]
        for interface_name in expected_exports:
            assert interface_name in engines.__all__, f"{interface_name} missing from __all__"

    def test_all_interfaces_importable_from_module(self):
        """All interfaces should be importable from engines module."""
        from game.strategy.interfaces.engines import (
            IMovementEngine,
            IProductionEngine,
            IOrderProcessor,
            IConflictEngine,
            IResourceEngine,
            IPopulationEngine,
            IResupplyEngine,
            IHarvestingEngine,
            IMaintenanceEngine,
        )
        # Just verify they're all ABC subclasses
        for interface in [
            IMovementEngine,
            IProductionEngine,
            IOrderProcessor,
            IConflictEngine,
            IResourceEngine,
            IPopulationEngine,
            IResupplyEngine,
            IHarvestingEngine,
            IMaintenanceEngine,
        ]:
            assert issubclass(interface, ABC)
