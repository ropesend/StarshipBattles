"""
Tests for combat event system.

TDD tests for CombatEventBus, CombatEvent, DamageContext, and
event detail level filtering.
"""
import pytest
from unittest.mock import Mock, MagicMock

from game.simulation.combat.combat_events import (
    CombatEventBus,
    CombatEvent,
    CombatEventType,
    DamageContext,
    EventDetailLevel,
)


# ============================================================================
# DamageContext
# ============================================================================

class TestDamageContext:
    """Tests for the attacker identity dataclass."""

    def test_creation_with_all_fields(self):
        attacker = Mock()
        weapon = Mock()
        ctx = DamageContext(attacker=attacker, source_weapon=weapon, damage_type="beam")
        assert ctx.attacker is attacker
        assert ctx.source_weapon is weapon
        assert ctx.damage_type == "beam"

    def test_defaults(self):
        ctx = DamageContext()
        assert ctx.attacker is None
        assert ctx.source_weapon is None
        assert ctx.damage_type == "unknown"

    def test_frozen(self):
        ctx = DamageContext()
        with pytest.raises(AttributeError):
            ctx.attacker = Mock()


# ============================================================================
# CombatEvent
# ============================================================================

class TestCombatEvent:
    """Tests for the combat event dataclass."""

    def test_creation(self):
        ship = Mock()
        ctx = DamageContext(attacker=Mock(), damage_type="projectile")
        event = CombatEvent(
            event_type=CombatEventType.SHIELD_HIT,
            target_ship=ship,
            damage_amount=50.0,
            context=ctx,
            shield_remaining=100.0,
        )
        assert event.event_type == CombatEventType.SHIELD_HIT
        assert event.target_ship is ship
        assert event.damage_amount == 50.0
        assert event.context is ctx
        assert event.shield_remaining == 100.0

    def test_defaults(self):
        event = CombatEvent(
            event_type=CombatEventType.COMPONENT_HIT,
            target_ship=Mock(),
        )
        assert event.damage_amount == 0.0
        assert event.context is None
        assert event.component is None
        assert event.layer_type is None
        assert event.shield_remaining == 0.0
        assert event.was_lethal is False

    def test_frozen(self):
        event = CombatEvent(
            event_type=CombatEventType.SHIP_DESTROYED,
            target_ship=Mock(),
        )
        with pytest.raises(AttributeError):
            event.damage_amount = 999


# ============================================================================
# CombatEventBus - Subscribe/Emit
# ============================================================================

class TestCombatEventBusBasics:
    """Tests for basic subscribe/emit/unsubscribe."""

    def test_subscribe_and_emit(self):
        bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
        received = []
        bus.subscribe(CombatEventType.SHIELD_HIT, received.append)

        event = CombatEvent(
            event_type=CombatEventType.SHIELD_HIT,
            target_ship=Mock(),
            damage_amount=10.0,
        )
        bus.emit(event)

        assert len(received) == 1
        assert received[0] is event

    def test_multiple_subscribers(self):
        bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
        received_a = []
        received_b = []
        bus.subscribe(CombatEventType.SHIELD_HIT, received_a.append)
        bus.subscribe(CombatEventType.SHIELD_HIT, received_b.append)

        event = CombatEvent(
            event_type=CombatEventType.SHIELD_HIT,
            target_ship=Mock(),
        )
        bus.emit(event)

        assert len(received_a) == 1
        assert len(received_b) == 1

    def test_no_crosstalk(self):
        """Subscribers to one event type don't receive other types."""
        bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
        received = []
        bus.subscribe(CombatEventType.SHIELD_HIT, received.append)

        event = CombatEvent(
            event_type=CombatEventType.SHIP_DESTROYED,
            target_ship=Mock(),
        )
        bus.emit(event)

        assert len(received) == 0

    def test_unsubscribe(self):
        bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
        received = []
        bus.subscribe(CombatEventType.SHIELD_HIT, received.append)
        bus.unsubscribe(CombatEventType.SHIELD_HIT, received.append)

        event = CombatEvent(
            event_type=CombatEventType.SHIELD_HIT,
            target_ship=Mock(),
        )
        bus.emit(event)

        assert len(received) == 0

    def test_unsubscribe_nonexistent_no_error(self):
        """Unsubscribing a callback that was never subscribed doesn't raise."""
        bus = CombatEventBus()
        bus.unsubscribe(CombatEventType.SHIELD_HIT, lambda e: None)

    def test_emit_no_subscribers_no_error(self):
        """Emitting with no subscribers doesn't raise."""
        bus = CombatEventBus()
        event = CombatEvent(
            event_type=CombatEventType.SHIP_DESTROYED,
            target_ship=Mock(),
        )
        bus.emit(event)  # Should not raise


# ============================================================================
# CombatEventBus - Error Isolation
# ============================================================================

class TestCombatEventBusErrorIsolation:
    """Tests for subscriber error isolation."""

    def test_subscriber_exception_does_not_propagate(self):
        bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)

        def bad_handler(event):
            raise RuntimeError("handler bug")

        received = []
        bus.subscribe(CombatEventType.SHIELD_HIT, bad_handler)
        bus.subscribe(CombatEventType.SHIELD_HIT, received.append)

        event = CombatEvent(
            event_type=CombatEventType.SHIELD_HIT,
            target_ship=Mock(),
        )
        bus.emit(event)

        # Second handler still called despite first raising
        assert len(received) == 1


# ============================================================================
# CombatEventBus - Detail Level Filtering
# ============================================================================

class TestCombatEventBusDetailLevel:
    """Tests for event detail level gating."""

    def test_minimal_only_emits_ship_events(self):
        bus = CombatEventBus(detail_level=EventDetailLevel.MINIMAL)
        received = []

        for event_type in CombatEventType:
            bus.subscribe(event_type, received.append)

        ship = Mock()
        # Emit one of each type
        for event_type in CombatEventType:
            bus.emit(CombatEvent(event_type=event_type, target_ship=ship))

        # Only SHIP_DESTROYED and SHIP_DERELICT should come through
        types = [e.event_type for e in received]
        assert CombatEventType.SHIP_DESTROYED in types
        assert CombatEventType.SHIP_DERELICT in types
        assert CombatEventType.SHIELD_HIT not in types
        assert CombatEventType.COMPONENT_HIT not in types
        assert CombatEventType.ARMOR_ABSORBED not in types

    def test_normal_includes_shield_and_component_destroyed(self):
        bus = CombatEventBus(detail_level=EventDetailLevel.NORMAL)
        received = []

        for event_type in CombatEventType:
            bus.subscribe(event_type, received.append)

        ship = Mock()
        for event_type in CombatEventType:
            bus.emit(CombatEvent(event_type=event_type, target_ship=ship))

        types = [e.event_type for e in received]
        assert CombatEventType.SHIP_DESTROYED in types
        assert CombatEventType.SHIP_DERELICT in types
        assert CombatEventType.SHIELD_HIT in types
        assert CombatEventType.COMPONENT_DESTROYED in types
        # DETAILED-only events should be filtered
        assert CombatEventType.COMPONENT_HIT not in types
        assert CombatEventType.ARMOR_ABSORBED not in types

    def test_detailed_emits_everything(self):
        bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
        received = []

        for event_type in CombatEventType:
            bus.subscribe(event_type, received.append)

        ship = Mock()
        for event_type in CombatEventType:
            bus.emit(CombatEvent(event_type=event_type, target_ship=ship))

        types = [e.event_type for e in received]
        for event_type in CombatEventType:
            assert event_type in types

    def test_detail_level_can_be_changed(self):
        bus = CombatEventBus(detail_level=EventDetailLevel.MINIMAL)
        received = []
        bus.subscribe(CombatEventType.SHIELD_HIT, received.append)

        ship = Mock()
        bus.emit(CombatEvent(event_type=CombatEventType.SHIELD_HIT, target_ship=ship))
        assert len(received) == 0  # Filtered out

        bus.detail_level = EventDetailLevel.NORMAL
        bus.emit(CombatEvent(event_type=CombatEventType.SHIELD_HIT, target_ship=ship))
        assert len(received) == 1  # Now comes through
