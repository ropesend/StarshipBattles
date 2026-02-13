"""UI services layer for decoupling UI from simulation layer.

This package provides facades and factories that wrap simulation layer
objects, allowing UI code to interact with ships and components without
directly importing simulation modules.

PROJ-43 Phase 12: Added BattleUIService for battle display.
PROJ-132: Added battle factory functions (moved from simulation layer).
"""
from game.ui.services.ship_factory import ShipFactory
from game.ui.services.component_service import ComponentService
from game.ui.services.vehicle_class_service import VehicleClassService
from game.ui.services.validation_service import ValidationService
from game.ui.services.ship_io_adapter import ShipIOAdapter
from game.ui.services.design_loader_adapter import DesignLoaderAdapter
from game.ui.services.battle_ui_service import BattleUIService
from game.ui.services.battle_factories import (
    create_manual_battle,
    create_test_battle,
    create_strategy_battle,
    create_hypothetical_battle,
)

__all__ = [
    'ShipFactory',
    'ComponentService',
    'VehicleClassService',
    'ValidationService',
    'ShipIOAdapter',
    'DesignLoaderAdapter',
    'BattleUIService',
    'create_manual_battle',
    'create_test_battle',
    'create_strategy_battle',
    'create_hypothetical_battle',
]
