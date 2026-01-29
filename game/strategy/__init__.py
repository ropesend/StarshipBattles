"""
Strategy package for Starship Battles.

Provides the 4X strategy layer including galaxy, fleets, empires,
turn processing, and the UI facade.

Public API
==========

Data (game.strategy.data):
    Fleet - Fleet of ships on strategy map
    ShipInstance - Individual ship in a fleet
    OrderType, FleetOrder - Fleet movement orders
    HexCoord - Hexagonal coordinate system

Engine (game.strategy.engine):
    TurnEngine - Turn processing orchestrator
    GameSession - Strategy game state manager
    GameConfig - Game configuration

Facade (game.strategy.facade):
    StrategySessionFacade - UI-to-engine communication facade

DTOs (game.strategy.facade.dto):
    FleetInfo, SystemInfo, PlanetInfo, EmpireInfo - Read-only DTOs

Interfaces (game.strategy.interfaces):
    IBattleResolver - Battle resolution interface
    BattleResult - Battle outcome DTO (strategy layer)
"""

# Data
from game.strategy.data.fleet import Fleet, OrderType, FleetOrder
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.hex_math import HexCoord

# Engine
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig

# Facade
from game.strategy.facade.strategy_session_facade import StrategySessionFacade

# DTOs
from game.strategy.facade.dto import (
    FleetInfo,
    SystemInfo,
    PlanetInfo,
    EmpireInfo,
)

# Interfaces
from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult


__all__ = [
    # Data
    'Fleet',
    'ShipInstance',
    'OrderType',
    'FleetOrder',
    'HexCoord',
    # Engine
    'TurnEngine',
    'GameSession',
    'GameConfig',
    # Facade
    'StrategySessionFacade',
    # DTOs
    'FleetInfo',
    'SystemInfo',
    'PlanetInfo',
    'EmpireInfo',
    # Interfaces
    'IBattleResolver',
    'BattleResult',
]
