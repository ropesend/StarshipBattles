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
    owner_system_name=None,
    owner_global_hex=None,
):
    """Create a mock BuildQueueSourceDTO for testing.

    PROJ-472 1B: the formatter now consumes the immutable DTO scalars
    ``owner_system_name`` / ``owner_global_hex`` instead of a live
    ``owner_entity`` + galaxy lookup. ``owner_entity`` is retained on the
    stub only for unrelated capability/queue assertions that ignore it.
    """
    source = MagicMock()
    source.construction_queue = construction_queue if construction_queue is not None else []
    source.can_build_ships = can_build_ships
    source.can_build_complexes = can_build_complexes
    source.context_type = context_type
    source.owner_entity = owner_entity if owner_entity is not None else MagicMock()
    source.display_name = "Test Location"
    source.build_rate = {"metals": 10.0}
    source.owner_system_name = owner_system_name
    source.owner_global_hex = owner_global_hex
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
    """Tests for get_system_name function (PROJ-472 1B: DTO scalar)."""

    def test_planet_system_name_from_dto_scalar(self):
        """Planet source returns the projected ``owner_system_name``."""
        source = _make_source(context_type="planet", owner_system_name="Sol")
        assert get_system_name(source) == "Sol"

    def test_fleet_system_name_from_dto_scalar(self):
        """Fleet source returns the projected ``owner_system_name``."""
        source = _make_source(context_type="fleet", owner_system_name="Proxima")
        assert get_system_name(source) == "Proxima"

    def test_none_system_name_returns_dash(self):
        """Unresolved system name (None) returns '-'."""
        source = _make_source(context_type="planet", owner_system_name=None)
        assert get_system_name(source) == "-"


class TestGetSectorText:
    """Tests for get_sector_text function (PROJ-472 1B: DTO scalar)."""

    def test_fleet_global_hex_from_dto_scalar(self):
        """Fleet source returns str(owner_global_hex)."""
        from game.core.hex_math import HexCoord

        source = _make_source(
            context_type="fleet", owner_global_hex=HexCoord(5, 10)
        )
        assert get_sector_text(source) == str(HexCoord(5, 10))

    def test_planet_global_hex_from_dto_scalar(self):
        """Planet source returns str(owner_global_hex)."""
        from game.core.hex_math import HexCoord

        source = _make_source(
            context_type="planet", owner_global_hex=HexCoord(3, 7)
        )
        assert get_sector_text(source) == str(HexCoord(3, 7))

    def test_no_global_hex_returns_dash(self):
        """Unresolved global hex (None) returns '-'."""
        source = _make_source(context_type="fleet", owner_global_hex=None)
        assert get_sector_text(source) == "-"


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
        assert get_resource_rate_text(source, "metals") == "-"

    def test_with_cost_per_tick_returns_per_turn_value(self):
        """Queue with cost_per_tick returns formatted per-turn value (rate * 100)."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_rate_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "cost_per_tick": {"metals": 15.0}}
        ])
        # 15 per tick * 100 ticks/turn = 1500 per turn
        assert get_resource_rate_text(source, "metals") == "1,500"

    def test_legacy_item_without_cost_per_tick_returns_dash(self):
        """Legacy queue item without cost_per_tick key returns '-'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_rate_text
        source = _make_source(construction_queue=[
            {"design_id": "OldShip", "turns_remaining": 5}  # No cost_per_tick
        ])
        assert get_resource_rate_text(source, "metals") == "-"

    def test_resource_not_in_cost_returns_zero(self):
        """Resource not in cost_per_tick returns '0'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_rate_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "cost_per_tick": {"metals": 10.0}}
        ])
        assert get_resource_rate_text(source, "organics") == "0"

    def test_zero_rate_returns_zero(self):
        """Zero rate returns '0'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_rate_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "cost_per_tick": {"metals": 0.0}}
        ])
        assert get_resource_rate_text(source, "metals") == "0"


class TestGetResourceTotalText:
    """Tests for get_resource_total_text function."""

    def test_empty_queue_returns_dash(self):
        """Empty queue returns '-'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_total_text
        source = _make_source(construction_queue=[])
        assert get_resource_total_text(source, "metals") == "-"

    def test_with_total_cost_returns_formatted(self):
        """Queue with total_cost returns formatted with k suffix."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_total_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "total_cost": {"metals": 5000}}
        ])
        assert get_resource_total_text(source, "metals") == "5k"

    def test_large_value_uses_M_suffix(self):
        """Large total cost uses M suffix."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_total_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "total_cost": {"metals": 1500000}}
        ])
        assert get_resource_total_text(source, "metals") == "1.5M"

    def test_legacy_item_without_total_cost_returns_dash(self):
        """Legacy queue item without total_cost key returns '-'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_total_text
        source = _make_source(construction_queue=[
            {"design_id": "OldShip", "turns_remaining": 5}  # No total_cost
        ])
        assert get_resource_total_text(source, "metals") == "-"

    def test_resource_not_in_total_returns_zero(self):
        """Resource not in total_cost returns '0'."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_total_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "total_cost": {"metals": 100}}
        ])
        assert get_resource_total_text(source, "organics") == "0"

    def test_small_value_no_suffix(self):
        """Small values below 1000 have no suffix."""
        from game.ui.screens.empire_build_queue_formatter import get_resource_total_text
        source = _make_source(construction_queue=[
            {"design_id": "Ship", "total_cost": {"metals": 500}}
        ])
        assert get_resource_total_text(source, "metals") == "500"
