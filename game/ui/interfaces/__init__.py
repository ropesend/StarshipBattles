"""UI interface protocols for decoupling UI from simulation layer.

This package provides Protocol classes that define the contracts between
UI code and underlying services. Implementations are provided by the
services package.

PROJ-43 Phase 12: Added IBattleUI protocol and DTOs.
"""
from game.ui.interfaces.battle_ui import (
    IBattleUI,
    ShipDTO,
    ComponentDTO,
    ProjectileDTO,
    BeamDTO,
    ResourceDTO,
)

__all__ = [
    'IBattleUI',
    'ShipDTO',
    'ComponentDTO',
    'ProjectileDTO',
    'BeamDTO',
    'ResourceDTO',
]
