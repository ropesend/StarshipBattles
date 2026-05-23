"""
Combat Event System

Provides a synchronous, per-battle event bus for combat events.
The CombatEventBus lives on BattleEngine and emits events as damage
is processed through the pipeline.

Event detail levels allow trading granularity for performance:
- MINIMAL: Ship destroyed/derelict only
- NORMAL: + shield hits, component destroyed
- DETAILED: + every component hit, armor absorption

Usage:
    bus = CombatEventBus(detail_level=EventDetailLevel.NORMAL)
    bus.subscribe(CombatEventType.SHIELD_HIT, my_handler)
    bus.emit(CombatEvent(
        event_type=CombatEventType.SHIELD_HIT,
        target_ship=ship,
        damage_amount=50.0,
        context=DamageContext(attacker=attacker, damage_type="beam"),
    ))
"""
import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.components.component import Component
    from game.core.combat_types import DamageContext

logger = logging.getLogger(__name__)


# ============================================================================
# Enums
# ============================================================================

class CombatEventType(Enum):
    """All combat event types."""
    SHIELD_HIT = auto()
    ARMOR_ABSORBED = auto()
    COMPONENT_HIT = auto()
    COMPONENT_DESTROYED = auto()
    SHIP_DESTROYED = auto()
    SHIP_DERELICT = auto()


class EventDetailLevel(Enum):
    """Granularity toggle for event emission."""
    MINIMAL = 0    # Ship destroyed/derelict only
    NORMAL = 1     # + shield hits, component destroyed
    DETAILED = 2   # + every component hit, armor absorption


# ============================================================================
# Data Classes
# ============================================================================


@dataclass(frozen=True, slots=True)
class CombatEvent:
    """A single combat event emitted during damage resolution.

    Attributes:
        event_type: What happened (shield hit, component destroyed, etc.)
        target_ship: The ship that was affected
        damage_amount: How much damage was involved
        context: Who caused the damage (attacker, weapon, type)
        component: The component that was hit/destroyed (if applicable)
        layer_type: Which hull layer was hit (if applicable)
        shield_remaining: Shield HP after absorption (for SHIELD_HIT)
        was_lethal: True if this event killed the ship
    """
    event_type: CombatEventType
    target_ship: Any
    damage_amount: float = 0.0
    context: Optional["DamageContext"] = None
    component: Optional[Any] = None
    layer_type: Optional[Any] = None
    shield_remaining: float = 0.0
    was_lethal: bool = False


# ============================================================================
# Detail Level Mapping
# ============================================================================

_EVENT_DETAIL_LEVELS: Dict[CombatEventType, EventDetailLevel] = {
    CombatEventType.SHIP_DESTROYED: EventDetailLevel.MINIMAL,
    CombatEventType.SHIP_DERELICT: EventDetailLevel.MINIMAL,
    CombatEventType.SHIELD_HIT: EventDetailLevel.NORMAL,
    CombatEventType.COMPONENT_DESTROYED: EventDetailLevel.NORMAL,
    CombatEventType.COMPONENT_HIT: EventDetailLevel.DETAILED,
    CombatEventType.ARMOR_ABSORBED: EventDetailLevel.DETAILED,
}


# ============================================================================
# Event Bus
# ============================================================================

class CombatEventBus:
    """Synchronous combat event bus with detail level gating.

    One instance per battle, owned by BattleEngine. Subscribers must
    be fast — no queuing, no threading. Subscriber exceptions are
    caught and logged to prevent simulation crashes.
    """

    __slots__ = ('_subscribers', '_detail_level')

    def __init__(self, detail_level: EventDetailLevel = EventDetailLevel.NORMAL):
        self._subscribers: Dict[CombatEventType, List] = {}
        self._detail_level = detail_level

    @property
    def detail_level(self) -> EventDetailLevel:
        return self._detail_level

    @detail_level.setter
    def detail_level(self, value: EventDetailLevel) -> None:
        self._detail_level = value

    def subscribe(self, event_type: CombatEventType, callback) -> None:
        """Register a callback for an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: CombatEventType, callback) -> None:
        """Remove a callback for an event type. No-op if not found."""
        if event_type in self._subscribers:
            subs = self._subscribers[event_type]
            if callback in subs:
                subs.remove(callback)

    def emit(self, event: CombatEvent) -> None:
        """Emit an event to subscribers.

        Skips events below the current detail level. Subscriber
        exceptions are caught and logged.
        """
        required_level = _EVENT_DETAIL_LEVELS.get(
            event.event_type, EventDetailLevel.DETAILED
        )
        if required_level.value > self._detail_level.value:
            return

        handlers = self._subscribers.get(event.event_type)
        if not handlers:
            return

        for cb in handlers:
            try:
                cb(event)
            except Exception:  # Intentional broad catch: subscribers may raise anything; one buggy observer must not break combat event dispatch
                logger.exception(
                    f"Combat event handler error for {event.event_type}"
                )
