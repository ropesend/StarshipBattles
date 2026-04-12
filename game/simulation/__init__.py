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
    BattleServiceResult - Result object for battle operations

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
from game.simulation.systems.battle_end_conditions import (
    IEndCondition,
    TickLimitCondition,
    TeamEliminatedCondition,
    TeamIncapacitatedCondition,
    EscapeCondition,
    ShipDestroyedCondition,
    NeverCondition,
    AnyCondition,
    AllCondition,
    end_condition_from_dict,
)

# Services
from game.simulation.services.battle_service import BattleService, BattleServiceResult

# State
from game.simulation.battle_state import BattleState

# Validation
from game.simulation.validation.ship_validator import ShipDesignValidator

# Unified Battle Spec/Outcome DTOs (PROJ-269 Phase 1)
from game.simulation.battle_spec import (
    AIPolicy,
    BattleSpec,
    CombatPolicies,
    ComponentStateSpec,
    EntryVector,
    PostBattleHook,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.battle_outcome import (
    BattleOutcome,
    EndReason,
    HitRecord,
    ModifierApplication,
    ShipOutcome,
    ShipStats,
    ShipStatus,
    TaskForceOutcome,
    TeamOutcome,
    WeaponSummary,
)


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
    'IEndCondition',
    'TeamEliminatedCondition',
    'TickLimitCondition',
    'end_condition_from_dict',
    # Services
    'BattleService',
    'BattleServiceResult',
    # State
    'BattleState',
    # Validation
    'ShipDesignValidator',
    # BattleSpec DTOs (PROJ-269)
    'AIPolicy',
    'BattleSpec',
    'CombatPolicies',
    'ComponentStateSpec',
    'EntryVector',
    'PostBattleHook',
    'ShipSpec',
    'SquadronSpec',
    'TaskForceSpec',
    'TeamSpec',
    # BattleOutcome DTOs (PROJ-269)
    'BattleOutcome',
    'EndReason',
    'HitRecord',
    'ModifierApplication',
    'ShipOutcome',
    'ShipStats',
    'ShipStatus',
    'TaskForceOutcome',
    'TeamOutcome',
    'WeaponSummary',
]
