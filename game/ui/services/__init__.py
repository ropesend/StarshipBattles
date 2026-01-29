"""UI services layer for decoupling UI from simulation layer.

This package provides facades and factories that wrap simulation layer
objects, allowing UI code to interact with ships and components without
directly importing simulation modules.
"""
from game.ui.services.ship_factory import ShipFactory
from game.ui.services.component_service import ComponentService
from game.ui.services.vehicle_class_service import VehicleClassService
from game.ui.services.validation_service import ValidationService

__all__ = ['ShipFactory', 'ComponentService', 'VehicleClassService', 'ValidationService']
