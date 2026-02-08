"""Tests for EventType and EventCategory enums."""

from game.strategy.events.event_types import EventCategory, EventType


class TestEventType:
    """Tests for the EventType enum."""

    def test_ship_built_value(self) -> None:
        assert EventType.SHIP_BUILT == "ship_built"

    def test_complex_built_value(self) -> None:
        assert EventType.COMPLEX_BUILT == "complex_built"

    def test_colony_founded_value(self) -> None:
        assert EventType.COLONY_FOUNDED == "colony_founded"

    def test_combat_resolved_value(self) -> None:
        assert EventType.COMBAT_RESOLVED == "combat_resolved"

    def test_all_values_are_strings(self) -> None:
        for member in EventType:
            assert isinstance(member.value, str)

    def test_has_four_members(self) -> None:
        assert len(EventType) == 4


class TestEventCategory:
    """Tests for the EventCategory enum."""

    def test_production_value(self) -> None:
        assert EventCategory.PRODUCTION == "production"

    def test_colonies_value(self) -> None:
        assert EventCategory.COLONIES == "colonies"

    def test_combat_value(self) -> None:
        assert EventCategory.COMBAT == "combat"

    def test_all_value(self) -> None:
        assert EventCategory.ALL == "all"

    def test_all_values_are_strings(self) -> None:
        for member in EventCategory:
            assert isinstance(member.value, str)

    def test_has_four_members(self) -> None:
        assert len(EventCategory) == 4
