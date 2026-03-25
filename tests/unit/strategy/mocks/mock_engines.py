"""
Mock implementations of strategy engine interfaces.

PROJ-43 Phase 4: These mocks implement the engine interfaces
for isolated unit testing of TurnEngine and related components.

Usage:
    from tests.unit.strategy.mocks import MockMovementEngine

    mock_movement = MockMovementEngine()
    mock_movement.collect_movements_result = [(fleet, hex)]

    engine = TurnEngine(movement_engine=mock_movement)
    engine._process_tick(1, [empire], galaxy)

    assert mock_movement.collect_movements_called
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Any

from game.strategy.interfaces.engines import (
    IMovementEngine,
    IProductionEngine,
    IOrderProcessor,
    IConflictEngine,
    IResourceEngine,
    IMaintenanceEngine,
)


class MockMovementEngine(IMovementEngine):
    """
    Mock implementation of IMovementEngine for testing.

    Tracks method calls and allows configurable return values.

    Attributes:
        collect_movements_result: Return value for collect_movements()
        apply_movements_result: Return value for apply_movements()
        calculate_next_hex_result: Return value for calculate_next_hex()
        collect_movements_calls: List of (empires, galaxy, tick) call args
        apply_movements_calls: List of (move_queue, galaxy) call args
        calculate_next_hex_calls: List of (fleet, galaxy) call args
    """

    def __init__(self):
        self.collect_movements_result: List[Tuple] = []
        self.apply_movements_result: List = []
        self.calculate_next_hex_result: Optional[Any] = None

        self.collect_movements_calls: List[Tuple] = []
        self.apply_movements_calls: List[Tuple] = []
        self.calculate_next_hex_calls: List[Tuple] = []

    @property
    def collect_movements_called(self) -> bool:
        return len(self.collect_movements_calls) > 0

    @property
    def apply_movements_called(self) -> bool:
        return len(self.apply_movements_calls) > 0

    @property
    def calculate_next_hex_called(self) -> bool:
        return len(self.calculate_next_hex_calls) > 0

    def collect_movements(self, empires, galaxy, tick):
        self.collect_movements_calls.append((empires, galaxy, tick))
        return self.collect_movements_result

    def apply_movements(self, move_queue, galaxy):
        self.apply_movements_calls.append((move_queue, galaxy))
        return self.apply_movements_result

    def calculate_next_hex(self, fleet, galaxy):
        self.calculate_next_hex_calls.append((fleet, galaxy))
        return self.calculate_next_hex_result


class MockProductionEngine(IProductionEngine):
    """
    Mock implementation of IProductionEngine for testing.

    PROJ-158: Removed process_production and process_fleet_production tracking
    as those methods were deleted from the interface (they were dead stubs).

    Tracks method calls and allows configurable behavior.

    Attributes:
        process_construction_tick_calls: List of (tick, empires, galaxy, save_path, harvesting_engine) call args
    """

    def __init__(self):
        self.process_construction_tick_calls: List[Tuple] = []

    @property
    def process_construction_tick_called(self) -> bool:
        return len(self.process_construction_tick_calls) > 0

    def process_construction_tick(self, tick, empires, galaxy, save_path=None, harvesting_engine=None):
        """PROJ-75/79: Per-tick construction resource consumption mock."""
        self.process_construction_tick_calls.append((tick, empires, galaxy, save_path, harvesting_engine))


class MockOrderProcessor(IOrderProcessor):
    """
    Mock implementation of IOrderProcessor for testing.

    Tracks method calls and allows configurable return values.

    Attributes:
        process_instant_orders_result: Return value for process_instant_orders()
        execute_action_order_result: Return value for execute_action_order()
        process_instant_orders_calls: List of (empires,) call args
        execute_action_order_calls: List of (fleet, empire, galaxy, component_registry, empires) call args
    """

    def __init__(self):
        self.process_instant_orders_result: List[Tuple] = []
        self.execute_action_order_result: bool = False

        self.process_instant_orders_calls: List[Tuple] = []
        self.execute_action_order_calls: List[Tuple] = []

    @property
    def process_instant_orders_called(self) -> bool:
        return len(self.process_instant_orders_calls) > 0

    @property
    def execute_action_order_called(self) -> bool:
        return len(self.execute_action_order_calls) > 0

    def process_instant_orders(self, empires):
        self.process_instant_orders_calls.append((empires,))
        return self.process_instant_orders_result

    def execute_action_order(self, fleet, empire, galaxy, component_registry=None, empires=None):
        """Execute the fleet's current action order."""
        self.execute_action_order_calls.append((fleet, empire, galaxy, component_registry, empires))
        return self.execute_action_order_result


@dataclass
class MockConflictResult:
    """Mock ConflictResult for testing."""
    combats_resolved: int = 0
    fleets_destroyed: List[int] = field(default_factory=list)


class MockConflictEngine(IConflictEngine):
    """
    Mock implementation of IConflictEngine for testing.

    Tracks method calls and allows configurable return values.

    Attributes:
        resolve_all_conflicts_result: Return value for resolve_all_conflicts()
        resolve_all_conflicts_calls: List of (empires,) call args
    """

    def __init__(self):
        self.resolve_all_conflicts_result = MockConflictResult()
        self.resolve_all_conflicts_calls: List[Tuple] = []

    @property
    def resolve_all_conflicts_called(self) -> bool:
        return len(self.resolve_all_conflicts_calls) > 0

    def resolve_all_conflicts(self, empires, galaxy=None):
        self.resolve_all_conflicts_calls.append((empires, galaxy))
        return self.resolve_all_conflicts_result


class MockResourceEngine(IResourceEngine):
    """
    Mock implementation of IResourceEngine for testing.

    Tracks method calls and allows configurable return values.

    Attributes:
        process_per_turn_consumption_result: Return value for process_per_turn_consumption()
        process_per_turn_consumption_calls: List of (tick, empires) call args
    """

    def __init__(self):
        self.process_per_turn_consumption_result: List = []
        self.process_per_turn_consumption_calls: List[Tuple] = []

    @property
    def process_per_turn_consumption_called(self) -> bool:
        return len(self.process_per_turn_consumption_calls) > 0

    def process_per_turn_consumption(self, tick, empires):
        self.process_per_turn_consumption_calls.append((tick, empires))
        return self.process_per_turn_consumption_result


class MockMaintenanceEngine(IMaintenanceEngine):
    """
    Mock implementation of IMaintenanceEngine for testing.

    PROJ-75 Phase 5: Maintenance engine mock.
    PROJ-161: Per-tick only (legacy full-turn method removed).

    Tracks method calls and allows configurable return values.

    Attributes:
        process_maintenance_tick_result: Return value for process_maintenance_tick()
        process_maintenance_tick_calls: List of (tick, empires) call args
    """

    def __init__(self):
        self.process_maintenance_tick_result: List = []
        self.process_maintenance_tick_calls: List[Tuple] = []

    @property
    def process_maintenance_tick_called(self) -> bool:
        return len(self.process_maintenance_tick_calls) > 0

    def process_maintenance_tick(self, tick, empires):
        self.process_maintenance_tick_calls.append((tick, empires))
        return self.process_maintenance_tick_result
