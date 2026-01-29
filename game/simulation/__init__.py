"""
Simulation package for Starship Battles.

Provides the core combat simulation, including ships, components, weapons,
and the battle engine.

Public API
==========

Entities (game.simulation.entities):
    Ship - Main ship entity with physics and combat
    ShipSerializer - Serialization/deserialization for ships

Components (game.simulation.components):
    Component - Base component class
    create_component - Factory function for creating components

Battle System (game.simulation.systems):
    BattleEngine - Core combat simulation engine
    BattleLogger - Battle event logging

Services (game.simulation.services):
    BattleService - High-level battle management
    BattleResult - Result object for battle operations

Battle State (game.simulation):
    BattleState - State container for battle simulation

Validation (game.simulation):
    ShipDesignValidator - Ship design validation
"""

# Core entities
from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_serialization import ShipSerializer

# Components
from game.simulation.components.component import Component, create_component

# Battle system
from game.simulation.systems.battle_engine import BattleEngine, BattleLogger
from game.simulation.systems.battle_end_conditions import BattleEndMode, BattleEndCondition

# Services
from game.simulation.services.battle_service import BattleService, BattleResult

# State
from game.simulation.battle_state import BattleState

# Validation
from game.simulation.ship_validator import ShipDesignValidator


__all__ = [
    # Entities
    'Ship',
    'ShipSerializer',
    # Components
    'Component',
    'create_component',
    # Battle system
    'BattleEngine',
    'BattleLogger',
    'BattleEndMode',
    'BattleEndCondition',
    # Services
    'BattleService',
    'BattleResult',
    # State
    'BattleState',
    # Validation
    'ShipDesignValidator',
]
