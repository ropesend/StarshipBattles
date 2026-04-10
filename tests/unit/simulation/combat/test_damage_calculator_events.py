"""
Tests for DamageCalculator event emissions during apply_damage().

PROJ-265 Phase 2: No existing test passes an event_bus to apply_damage().
These tests verify that combat events (SHIELD_HIT, ARMOR_ABSORBED,
COMPONENT_HIT, COMPONENT_DESTROYED, SHIP_DERELICT) are emitted correctly.
"""

import pytest
from unittest.mock import MagicMock

from game.simulation.combat.damage_calculator import DamageCalculator
from game.simulation.combat.combat_events import CombatEventType


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def calculator():
    """Create DamageCalculator with fixed RNG for reproducibility."""
    import random
    return DamageCalculator(rng=random.Random(42))


@pytest.fixture
def event_bus():
    """Create a mock event bus that records emitted events."""
    bus = MagicMock()
    bus.emitted = []

    def capture_emit(event):
        bus.emitted.append(event)

    bus.emit = MagicMock(side_effect=capture_emit)
    return bus


def _make_ship(shields=0, emissive_armor=0, sra=0, max_shields=0, hp=100):
    """Create a mock ship with configurable defenses."""
    ship = MagicMock()
    ship.is_alive = True
    ship.is_derelict = False
    ship.current_shields = shields
    ship.max_shields = max_shields
    ship.emissive_armor = emissive_armor
    ship.shield_regenerating_armor = sra

    # Create a single component in a single layer for hull damage
    comp = MagicMock()
    comp.current_hp = hp
    comp.take_damage = MagicMock(side_effect=lambda d: setattr(comp, 'current_hp', max(0, comp.current_hp - d)))

    layer = MagicMock()
    layer.components = [comp]
    layer.radius_pct = 1.0

    from game.core.constants import LayerType
    ship.layers = {LayerType.CORE: layer}

    ship.recalculate_stats_if_dirty = MagicMock()
    ship.update_derelict_status = MagicMock()

    ship._mock_comp = comp  # Expose for test assertions
    return ship


# =============================================================================
# Shield Hit Event Tests
# =============================================================================


class TestShieldHitEvent:
    """Tests for SHIELD_HIT event emission."""

    def test_shield_hit_emits_event(self, calculator, event_bus):
        """SHIELD_HIT emitted when shields absorb damage."""
        ship = _make_ship(shields=50, max_shields=100)

        calculator.apply_damage(ship, 30, event_bus=event_bus)

        assert len(event_bus.emitted) >= 1
        shield_events = [e for e in event_bus.emitted if e.event_type == CombatEventType.SHIELD_HIT]
        assert len(shield_events) == 1
        assert shield_events[0].damage_amount == 30
        assert shield_events[0].target_ship is ship

    def test_no_shield_no_event(self, calculator, event_bus):
        """No SHIELD_HIT when ship has no shields."""
        ship = _make_ship(shields=0)

        calculator.apply_damage(ship, 30, event_bus=event_bus)

        shield_events = [e for e in event_bus.emitted if e.event_type == CombatEventType.SHIELD_HIT]
        assert len(shield_events) == 0


# =============================================================================
# Armor Absorbed Event Tests
# =============================================================================


class TestArmorAbsorbedEvent:
    """Tests for ARMOR_ABSORBED event emission."""

    def test_emissive_armor_emits_event(self, calculator, event_bus):
        """ARMOR_ABSORBED emitted when emissive armor reduces damage."""
        ship = _make_ship(emissive_armor=20)

        calculator.apply_damage(ship, 50, event_bus=event_bus)

        armor_events = [e for e in event_bus.emitted if e.event_type == CombatEventType.ARMOR_ABSORBED]
        assert len(armor_events) >= 1
        assert armor_events[0].damage_amount == 20  # EA absorbs up to its value

    def test_sra_emits_armor_absorbed_event(self, calculator, event_bus):
        """ARMOR_ABSORBED emitted when SRA absorbs damage."""
        ship = _make_ship(sra=15, max_shields=100)

        calculator.apply_damage(ship, 50, event_bus=event_bus)

        armor_events = [e for e in event_bus.emitted if e.event_type == CombatEventType.ARMOR_ABSORBED]
        assert len(armor_events) >= 1


# =============================================================================
# Component Hit/Destroyed Event Tests
# =============================================================================


class TestComponentEvents:
    """Tests for COMPONENT_HIT and COMPONENT_DESTROYED events."""

    def test_component_hit_emits_event(self, calculator, event_bus):
        """COMPONENT_HIT emitted when component takes damage but survives."""
        ship = _make_ship(hp=100)

        calculator.apply_damage(ship, 30, event_bus=event_bus)

        hit_events = [e for e in event_bus.emitted if e.event_type == CombatEventType.COMPONENT_HIT]
        assert len(hit_events) == 1
        assert hit_events[0].damage_amount == 30

    def test_component_destroyed_emits_event(self, calculator, event_bus):
        """COMPONENT_DESTROYED emitted when component HP reaches 0."""
        ship = _make_ship(hp=20)

        calculator.apply_damage(ship, 50, event_bus=event_bus)

        destroyed_events = [e for e in event_bus.emitted if e.event_type == CombatEventType.COMPONENT_DESTROYED]
        assert len(destroyed_events) == 1
        assert destroyed_events[0].damage_amount == 20  # Only absorbed up to HP


# =============================================================================
# Ship Derelict Event Tests
# =============================================================================


class TestShipDerelictEvent:
    """Tests for SHIP_DERELICT event emission."""

    def test_derelict_emits_event(self, calculator, event_bus):
        """SHIP_DERELICT emitted when ship becomes derelict from damage."""
        ship = _make_ship(hp=10)
        # After damage, update_derelict_status will set is_derelict = True
        ship.update_derelict_status = MagicMock(
            side_effect=lambda: setattr(ship, 'is_derelict', True)
        )

        calculator.apply_damage(ship, 20, event_bus=event_bus)

        derelict_events = [e for e in event_bus.emitted if e.event_type == CombatEventType.SHIP_DERELICT]
        assert len(derelict_events) == 1
        assert derelict_events[0].target_ship is ship

    def test_already_derelict_no_event(self, calculator, event_bus):
        """No SHIP_DERELICT event when ship was already derelict."""
        ship = _make_ship(hp=10)
        ship.is_derelict = True  # Already derelict before damage

        calculator.apply_damage(ship, 20, event_bus=event_bus)

        derelict_events = [e for e in event_bus.emitted if e.event_type == CombatEventType.SHIP_DERELICT]
        assert len(derelict_events) == 0


# =============================================================================
# No Event Bus Tests
# =============================================================================


class TestNoEventBus:
    """Tests that damage still applies correctly without event_bus."""

    def test_damage_applies_without_event_bus(self, calculator):
        """Damage is applied even when no event_bus is provided."""
        ship = _make_ship(shields=20, max_shields=100, hp=100)

        calculator.apply_damage(ship, 50)

        assert ship.current_shields == 0  # 20 absorbed by shields
        # Remaining 30 goes to hull
