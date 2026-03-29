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

    def test_resource_shortage_value(self) -> None:
        assert EventType.RESOURCE_SHORTAGE == "resource_shortage"

    def test_fleet_joined_value(self) -> None:
        assert EventType.FLEET_JOINED == "fleet_joined"

    def test_fleet_join_redirected_value(self) -> None:
        assert EventType.FLEET_JOIN_REDIRECTED == "fleet_join_redirected"

    def test_fleet_join_cancelled_value(self) -> None:
        assert EventType.FLEET_JOIN_CANCELLED == "fleet_join_cancelled"

    def test_has_seventeen_members(self) -> None:
        # Original 4 + 6 superweapon events (PROJ-102) + RESOURCE_SHORTAGE (FEAT-09)
        # + 3 fleet events (PROJ-222) + 3 shield events (PROJ-237)
        assert len(EventType) == 17


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

    def test_fleet_operations_value(self) -> None:
        assert EventCategory.FLEET_OPERATIONS == "fleet_operations"

    def test_has_seven_members(self) -> None:
        # Original 4 + SUPERWEAPONS (PROJ-102) + FLEET_OPERATIONS (PROJ-222)
        # + PLANET_OPERATIONS (PROJ-237)
        assert len(EventCategory) == 7
