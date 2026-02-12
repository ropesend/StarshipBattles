"""
Contract tests for strategy engine interfaces (engines.py).

PROJ-110 Phase 3, Task 3.6: Verify abstract method presence and
instantiation behavior for all engine interfaces.

These tests verify:
- Abstract classes cannot be instantiated (TypeError on ABC instantiation)
- All required abstract methods are present and marked as abstract
- Concrete implementations can be created when all methods are implemented

Complements test_engine_interfaces.py with additional coverage for:
- IPopulationEngine (missing from original tests)
- IResupplyEngine (missing from original tests)
- IHarvestingEngine (missing from original tests)
- IProductionEngine.process_construction_tick (missing method test)
"""
import pytest
from abc import ABC


# =============================================================================
# IMovementEngine Contract Tests
# =============================================================================


class TestIMovementEngineContract:
    """Contract tests for IMovementEngine abstract interface."""

    def test_is_abstract_base_class(self):
        """IMovementEngine should be an ABC subclass."""
        from game.strategy.interfaces.engines import IMovementEngine
        assert issubclass(IMovementEngine, ABC)

    def test_cannot_instantiate_directly(self):
        """IMovementEngine cannot be instantiated directly."""
        from game.strategy.interfaces.engines import IMovementEngine
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IMovementEngine()

    def test_has_abstract_collect_movements(self):
        """IMovementEngine.collect_movements must be abstract."""
        from game.strategy.interfaces.engines import IMovementEngine
        assert hasattr(IMovementEngine, 'collect_movements')
        assert getattr(IMovementEngine.collect_movements, '__isabstractmethod__', False) is True

    def test_has_abstract_apply_movements(self):
        """IMovementEngine.apply_movements must be abstract."""
        from game.strategy.interfaces.engines import IMovementEngine
        assert hasattr(IMovementEngine, 'apply_movements')
        assert getattr(IMovementEngine.apply_movements, '__isabstractmethod__', False) is True

    def test_has_abstract_calculate_next_hex(self):
        """IMovementEngine.calculate_next_hex must be abstract."""
        from game.strategy.interfaces.engines import IMovementEngine
        assert hasattr(IMovementEngine, 'calculate_next_hex')
        assert getattr(IMovementEngine.calculate_next_hex, '__isabstractmethod__', False) is True


# =============================================================================
# IProductionEngine Contract Tests
# =============================================================================


class TestIProductionEngineContract:
    """Contract tests for IProductionEngine abstract interface."""

    def test_is_abstract_base_class(self):
        """IProductionEngine should be an ABC subclass."""
        from game.strategy.interfaces.engines import IProductionEngine
        assert issubclass(IProductionEngine, ABC)

    def test_cannot_instantiate_directly(self):
        """IProductionEngine cannot be instantiated directly."""
        from game.strategy.interfaces.engines import IProductionEngine
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IProductionEngine()

    def test_has_abstract_process_construction_tick(self):
        """IProductionEngine.process_construction_tick must be abstract (PROJ-75)."""
        from game.strategy.interfaces.engines import IProductionEngine
        assert hasattr(IProductionEngine, 'process_construction_tick')
        assert getattr(IProductionEngine.process_construction_tick, '__isabstractmethod__', False) is True

    def test_has_abstract_process_production(self):
        """IProductionEngine.process_production must be abstract."""
        from game.strategy.interfaces.engines import IProductionEngine
        assert hasattr(IProductionEngine, 'process_production')
        assert getattr(IProductionEngine.process_production, '__isabstractmethod__', False) is True

    def test_has_abstract_process_fleet_production(self):
        """IProductionEngine.process_fleet_production must be abstract (PROJ-67)."""
        from game.strategy.interfaces.engines import IProductionEngine
        assert hasattr(IProductionEngine, 'process_fleet_production')
        assert getattr(IProductionEngine.process_fleet_production, '__isabstractmethod__', False) is True


# =============================================================================
# IOrderProcessor Contract Tests
# =============================================================================


class TestIOrderProcessorContract:
    """Contract tests for IOrderProcessor abstract interface."""

    def test_is_abstract_base_class(self):
        """IOrderProcessor should be an ABC subclass."""
        from game.strategy.interfaces.engines import IOrderProcessor
        assert issubclass(IOrderProcessor, ABC)

    def test_cannot_instantiate_directly(self):
        """IOrderProcessor cannot be instantiated directly."""
        from game.strategy.interfaces.engines import IOrderProcessor
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IOrderProcessor()

    def test_has_abstract_process_instant_orders(self):
        """IOrderProcessor.process_instant_orders must be abstract."""
        from game.strategy.interfaces.engines import IOrderProcessor
        assert hasattr(IOrderProcessor, 'process_instant_orders')
        assert getattr(IOrderProcessor.process_instant_orders, '__isabstractmethod__', False) is True

    def test_has_abstract_process_end_turn_orders(self):
        """IOrderProcessor.process_end_turn_orders must be abstract."""
        from game.strategy.interfaces.engines import IOrderProcessor
        assert hasattr(IOrderProcessor, 'process_end_turn_orders')
        assert getattr(IOrderProcessor.process_end_turn_orders, '__isabstractmethod__', False) is True


# =============================================================================
# IConflictEngine Contract Tests
# =============================================================================


class TestIConflictEngineContract:
    """Contract tests for IConflictEngine abstract interface."""

    def test_is_abstract_base_class(self):
        """IConflictEngine should be an ABC subclass."""
        from game.strategy.interfaces.engines import IConflictEngine
        assert issubclass(IConflictEngine, ABC)

    def test_cannot_instantiate_directly(self):
        """IConflictEngine cannot be instantiated directly."""
        from game.strategy.interfaces.engines import IConflictEngine
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IConflictEngine()

    def test_has_abstract_resolve_all_conflicts(self):
        """IConflictEngine.resolve_all_conflicts must be abstract."""
        from game.strategy.interfaces.engines import IConflictEngine
        assert hasattr(IConflictEngine, 'resolve_all_conflicts')
        assert getattr(IConflictEngine.resolve_all_conflicts, '__isabstractmethod__', False) is True


# =============================================================================
# IResourceEngine Contract Tests
# =============================================================================


class TestIResourceEngineContract:
    """Contract tests for IResourceEngine abstract interface."""

    def test_is_abstract_base_class(self):
        """IResourceEngine should be an ABC subclass."""
        from game.strategy.interfaces.engines import IResourceEngine
        assert issubclass(IResourceEngine, ABC)

    def test_cannot_instantiate_directly(self):
        """IResourceEngine cannot be instantiated directly."""
        from game.strategy.interfaces.engines import IResourceEngine
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IResourceEngine()

    def test_has_abstract_process_per_turn_consumption(self):
        """IResourceEngine.process_per_turn_consumption must be abstract."""
        from game.strategy.interfaces.engines import IResourceEngine
        assert hasattr(IResourceEngine, 'process_per_turn_consumption')
        assert getattr(IResourceEngine.process_per_turn_consumption, '__isabstractmethod__', False) is True


# =============================================================================
# IPopulationEngine Contract Tests
# =============================================================================


class TestIPopulationEngineContract:
    """Contract tests for IPopulationEngine abstract interface."""

    def test_is_abstract_base_class(self):
        """IPopulationEngine should be an ABC subclass."""
        from game.strategy.interfaces.engines import IPopulationEngine
        assert issubclass(IPopulationEngine, ABC)

    def test_cannot_instantiate_directly(self):
        """IPopulationEngine cannot be instantiated directly."""
        from game.strategy.interfaces.engines import IPopulationEngine
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IPopulationEngine()

    def test_has_abstract_process_population_growth(self):
        """IPopulationEngine.process_population_growth must be abstract."""
        from game.strategy.interfaces.engines import IPopulationEngine
        assert hasattr(IPopulationEngine, 'process_population_growth')
        assert getattr(IPopulationEngine.process_population_growth, '__isabstractmethod__', False) is True

    def test_concrete_implementation_can_be_instantiated(self):
        """Concrete IPopulationEngine with all methods implemented works."""
        from game.strategy.interfaces.engines import IPopulationEngine

        class ConcretePopulationEngine(IPopulationEngine):
            def process_population_growth(self, empires):
                pass

        engine = ConcretePopulationEngine()
        assert engine is not None


# =============================================================================
# IResupplyEngine Contract Tests
# =============================================================================


class TestIResupplyEngineContract:
    """Contract tests for IResupplyEngine abstract interface (PROJ-74)."""

    def test_is_abstract_base_class(self):
        """IResupplyEngine should be an ABC subclass."""
        from game.strategy.interfaces.engines import IResupplyEngine
        assert issubclass(IResupplyEngine, ABC)

    def test_cannot_instantiate_directly(self):
        """IResupplyEngine cannot be instantiated directly."""
        from game.strategy.interfaces.engines import IResupplyEngine
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IResupplyEngine()

    def test_has_abstract_process_fuel_generation(self):
        """IResupplyEngine.process_fuel_generation must be abstract."""
        from game.strategy.interfaces.engines import IResupplyEngine
        assert hasattr(IResupplyEngine, 'process_fuel_generation')
        assert getattr(IResupplyEngine.process_fuel_generation, '__isabstractmethod__', False) is True

    def test_has_abstract_process_fleet_resupply(self):
        """IResupplyEngine.process_fleet_resupply must be abstract."""
        from game.strategy.interfaces.engines import IResupplyEngine
        assert hasattr(IResupplyEngine, 'process_fleet_resupply')
        assert getattr(IResupplyEngine.process_fleet_resupply, '__isabstractmethod__', False) is True

    def test_concrete_implementation_can_be_instantiated(self):
        """Concrete IResupplyEngine with all methods implemented works."""
        from game.strategy.interfaces.engines import IResupplyEngine

        class ConcreteResupplyEngine(IResupplyEngine):
            def process_fuel_generation(self, tick, empires):
                return []

            def process_fleet_resupply(self, tick, empires, galaxy):
                return []

        engine = ConcreteResupplyEngine()
        assert engine is not None


# =============================================================================
# IHarvestingEngine Contract Tests
# =============================================================================


class TestIHarvestingEngineContract:
    """Contract tests for IHarvestingEngine abstract interface (PROJ-75)."""

    def test_is_abstract_base_class(self):
        """IHarvestingEngine should be an ABC subclass."""
        from game.strategy.interfaces.engines import IHarvestingEngine
        assert issubclass(IHarvestingEngine, ABC)

    def test_cannot_instantiate_directly(self):
        """IHarvestingEngine cannot be instantiated directly."""
        from game.strategy.interfaces.engines import IHarvestingEngine
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IHarvestingEngine()

    def test_has_abstract_process_harvesting(self):
        """IHarvestingEngine.process_harvesting must be abstract."""
        from game.strategy.interfaces.engines import IHarvestingEngine
        assert hasattr(IHarvestingEngine, 'process_harvesting')
        assert getattr(IHarvestingEngine.process_harvesting, '__isabstractmethod__', False) is True

    def test_concrete_implementation_can_be_instantiated(self):
        """Concrete IHarvestingEngine with all methods implemented works."""
        from game.strategy.interfaces.engines import IHarvestingEngine

        class ConcreteHarvestingEngine(IHarvestingEngine):
            def process_harvesting(self, empires):
                pass

        engine = ConcreteHarvestingEngine()
        assert engine is not None


# =============================================================================
# IMaintenanceEngine Contract Tests
# =============================================================================


class TestIMaintenanceEngineContract:
    """Contract tests for IMaintenanceEngine abstract interface (PROJ-75)."""

    def test_is_abstract_base_class(self):
        """IMaintenanceEngine should be an ABC subclass."""
        from game.strategy.interfaces.engines import IMaintenanceEngine
        assert issubclass(IMaintenanceEngine, ABC)

    def test_cannot_instantiate_directly(self):
        """IMaintenanceEngine cannot be instantiated directly."""
        from game.strategy.interfaces.engines import IMaintenanceEngine
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IMaintenanceEngine()

    def test_has_abstract_process_maintenance(self):
        """IMaintenanceEngine.process_maintenance must be abstract."""
        from game.strategy.interfaces.engines import IMaintenanceEngine
        assert hasattr(IMaintenanceEngine, 'process_maintenance')
        assert getattr(IMaintenanceEngine.process_maintenance, '__isabstractmethod__', False) is True


# =============================================================================
# Module __all__ Export Tests
# =============================================================================


class TestEnginesModuleExports:
    """Test that engines.py exports all interfaces correctly."""

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
