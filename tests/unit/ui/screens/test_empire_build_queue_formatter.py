"""Unit tests for empire_build_queue_formatter.py.

Tests pure data formatting functions with no UI dependencies.
Created as part of PROJ-89 Phase 2.
"""
import pytest
from unittest.mock import MagicMock

from game.ui.screens.empire_build_queue_formatter import (
    get_queue_summary,
    get_first_item_text,
    get_capabilities_text,
    get_system_name,
    get_sector_text,
    get_turns_left_text,
)


def _make_source(
    construction_queue=None,
    can_build_ships=True,
    can_build_complexes=False,
    context_type="planet",
    owner_entity=None,
):
    """Create a mock BuildQueueSource for testing."""
    source = MagicMock()
    source.construction_queue = construction_queue if construction_queue is not None else []
    source.can_build_ships = can_build_ships
    source.can_build_complexes = can_build_complexes
    source.context_type = context_type
    source.owner_entity = owner_entity if owner_entity is not None else MagicMock()
    source.display_name = "Test Location"
    source.build_rate = {"Metals": 10.0}
    return source


class TestGetQueueSummary:
    """Tests for get_queue_summary function."""

    def test_empty_queue_returns_dash(self):
        """Empty queue should return '-'."""
        source = _make_source(construction_queue=[])
        assert get_queue_summary(source) == "-"

    def test_single_item_no_plural(self):
        """Single item should return '1 item' (no plural)."""
        source = _make_source(construction_queue=[{"design_id": "Ship1"}])
        assert get_queue_summary(source) == "1 item"

    def test_multiple_items_plural(self):
        """Multiple items should return 'N items'."""
        source = _make_source(construction_queue=[
            {"design_id": "Ship1"},
            {"design_id": "Ship2"},
            {"design_id": "Ship3"},
        ])
        assert get_queue_summary(source) == "3 items"


class TestGetFirstItemText:
    """Tests for get_first_item_text function."""

    def test_empty_queue_returns_dash(self):
        """Empty queue should return '-'."""
        source = _make_source(construction_queue=[])
        assert get_first_item_text(source) == "-"

    def test_queue_with_item_returns_design_and_turns(self):
        """Queue with item returns design_id and turns."""
        source = _make_source(construction_queue=[
            {"design_id": "Cruiser", "turns_remaining": 5}
        ])
        assert get_first_item_text(source) == "Cruiser (5t)"

    def test_missing_turns_shows_question_mark(self):
        """Missing turns_remaining shows '?'."""
        source = _make_source(construction_queue=[{"design_id": "Fighter"}])
        assert get_first_item_text(source) == "Fighter (?t)"

    def test_missing_design_id_shows_unknown(self):
        """Missing design_id shows 'Unknown'."""
        source = _make_source(construction_queue=[{"turns_remaining": 3}])
        assert get_first_item_text(source) == "Unknown (3t)"


class TestGetCapabilitiesText:
    """Tests for get_capabilities_text function."""

    def test_ships_only(self):
        """Ships only capability returns 'Ships'."""
        source = _make_source(can_build_ships=True, can_build_complexes=False)
        assert get_capabilities_text(source) == "Ships"

    def test_complexes_only(self):
        """Complexes only capability returns 'Complexes'."""
        source = _make_source(can_build_ships=False, can_build_complexes=True)
        assert get_capabilities_text(source) == "Complexes"

    def test_both_capabilities(self):
        """Both capabilities returns 'Ships & Complexes'."""
        source = _make_source(can_build_ships=True, can_build_complexes=True)
        assert get_capabilities_text(source) == "Ships & Complexes"

    def test_no_capabilities(self):
        """No capabilities returns 'None'."""
        source = _make_source(can_build_ships=False, can_build_complexes=False)
        assert get_capabilities_text(source) == "None"


class TestGetSystemName:
    """Tests for get_system_name function."""

    def test_planet_with_galaxy_lookup(self):
        """Planet with galaxy lookup returns system name."""
        entity = MagicMock()
        entity.system_name = None
        del entity.system_name  # Remove the attribute entirely

        system_obj = MagicMock()
        system_obj.name = "Sol"

        galaxy = MagicMock()
        galaxy.get_system_of_planet.return_value = system_obj

        source = _make_source(context_type="planet", owner_entity=entity)

        result = get_system_name(source, galaxy=galaxy)
        assert result == "Sol"

    def test_fleet_with_location_returns_system_name(self):
        """Fleet with location returns system name from galaxy lookup."""
        entity = MagicMock()
        entity.location = MagicMock()  # Some hex coordinate

        system_obj = MagicMock()
        system_obj.name = "Proxima"

        galaxy = MagicMock()
        galaxy.get_system_at_hex.return_value = system_obj

        source = _make_source(context_type="fleet", owner_entity=entity)

        result = get_system_name(source, galaxy=galaxy)
        assert result == "Proxima"

    def test_no_system_found_returns_dash(self):
        """No system found returns '-'."""
        entity = MagicMock()
        del entity.system_name  # Remove any attribute

        galaxy = MagicMock()
        galaxy.get_system_of_planet.return_value = None

        source = _make_source(context_type="planet", owner_entity=entity)

        result = get_system_name(source, galaxy=galaxy)
        assert result == "-"

    def test_no_galaxy_returns_dash(self):
        """No galaxy provided returns '-' if no system_name attr."""
        entity = MagicMock()
        del entity.system_name

        source = _make_source(context_type="planet", owner_entity=entity)

        result = get_system_name(source, galaxy=None)
        assert result == "-"


class TestGetSectorText:
    """Tests for get_sector_text function."""

    def test_fleet_with_location(self):
        """Fleet with location returns str(location)."""
        entity = MagicMock()
        entity.location = MagicMock()
        entity.location.__str__ = lambda self: "(5, 10)"

        source = _make_source(context_type="fleet", owner_entity=entity)

        result = get_sector_text(source)
        assert result == "(5, 10)"

    def test_planet_with_location(self):
        """Planet with location returns str(location)."""
        entity = MagicMock()
        entity.global_hex = None
        entity.location = MagicMock()
        entity.location.__str__ = lambda self: "(3, 7)"

        source = _make_source(context_type="planet", owner_entity=entity)

        result = get_sector_text(source)
        assert result == "(3, 7)"

    def test_no_location_returns_dash(self):
        """No location returns '-'."""
        entity = MagicMock()
        entity.location = None
        entity.global_hex = None

        source = _make_source(context_type="fleet", owner_entity=entity)

        result = get_sector_text(source)
        assert result == "-"


class TestGetTurnsLeftText:
    """Tests for get_turns_left_text function."""

    def test_empty_queue_returns_dash(self):
        """Empty queue returns '-'."""
        source = _make_source(construction_queue=[])
        assert get_turns_left_text(source) == "-"

    def test_queue_with_item_returns_turns_format(self):
        """Queue with item returns 'Nt' format."""
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "turns_remaining": 8}
        ])
        assert get_turns_left_text(source) == "8t"

    def test_missing_turns_shows_question_mark(self):
        """Missing turns_remaining shows '?t'."""
        source = _make_source(construction_queue=[{"design_id": "Ship"}])
        assert get_turns_left_text(source) == "?t"


class TestGetResourceRateText:
    """Tests for get_resource_rate_text function."""

    def test_empty_queue_returns_dash(self):
        """Empty queue returns '-'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_rate_text
        source = _make_source(construction_queue=[])
        assert get_resource_rate_text(source, "Metals") == "-"

    def test_with_cost_per_tick_returns_per_turn_value(self):
        """Queue with cost_per_tick returns formatted per-turn value (rate * 100)."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_rate_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "cost_per_tick": {"Metals": 15.0}}
        ])
        # 15 per tick * 100 ticks/turn = 1500 per turn
        assert get_resource_rate_text(source, "Metals") == "1,500"

    def test_legacy_item_without_cost_per_tick_returns_dash(self):
        """Legacy queue item without cost_per_tick key returns '-'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_rate_text
        source = _make_source(construction_queue=[
            {"design_id": "OldShip", "turns_remaining": 5}  # No cost_per_tick
        ])
        assert get_resource_rate_text(source, "Metals") == "-"

    def test_resource_not_in_cost_returns_zero(self):
        """Resource not in cost_per_tick returns '0'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_rate_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "cost_per_tick": {"Metals": 10.0}}
        ])
        assert get_resource_rate_text(source, "Organics") == "0"

    def test_zero_rate_returns_zero(self):
        """Zero rate returns '0'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_rate_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "cost_per_tick": {"Metals": 0.0}}
        ])
        assert get_resource_rate_text(source, "Metals") == "0"


class TestGetResourceTotalText:
    """Tests for get_resource_total_text function."""

    def test_empty_queue_returns_dash(self):
        """Empty queue returns '-'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_total_text
        source = _make_source(construction_queue=[])
        assert get_resource_total_text(source, "Metals") == "-"

    def test_with_total_cost_returns_formatted(self):
        """Queue with total_cost returns formatted with k suffix."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_total_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "total_cost": {"Metals": 5000}}
        ])
        assert get_resource_total_text(source, "Metals") == "5k"

    def test_large_value_uses_M_suffix(self):
        """Large total cost uses M suffix."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_total_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "total_cost": {"Metals": 1500000}}
        ])
        assert get_resource_total_text(source, "Metals") == "1.5M"

    def test_legacy_item_without_total_cost_returns_dash(self):
        """Legacy queue item without total_cost key returns '-'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_total_text
        source = _make_source(construction_queue=[
            {"design_id": "OldShip", "turns_remaining": 5}  # No total_cost
        ])
        assert get_resource_total_text(source, "Metals") == "-"

    def test_resource_not_in_total_returns_zero(self):
        """Resource not in total_cost returns '0'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_total_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "total_cost": {"Metals": 100}}
        ])
        assert get_resource_total_text(source, "Organics") == "0"

    def test_small_value_no_suffix(self):
        """Small values below 1000 have no suffix."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_total_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "total_cost": {"Metals": 500}}
        ])
        assert get_resource_total_text(source, "Metals") == "500"
