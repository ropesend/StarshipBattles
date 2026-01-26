"""
DEPRECATED: Use vehicle_design_service.py instead.
This file provides backward compatibility aliases.
"""
from game.simulation.services.vehicle_design_service import (
    VehicleDesignService as ShipBuilderService,
    DesignResult as ShipBuilderResult
)

# Explicit re-exports for clarity
__all__ = ['ShipBuilderService', 'ShipBuilderResult']
