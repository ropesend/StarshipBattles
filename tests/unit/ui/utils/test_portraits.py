"""Tests for game.ui.utils.portraits module."""
import pytest
import re


class TestParseShipClassName:
    """Tests for parse_ship_class_name utility."""

    def test_simple_class(self):
        from game.ui.utils.portraits import parse_ship_class_name
        assert parse_ship_class_name("Escort") == "Escort"

    def test_parenthetical_class(self):
        from game.ui.utils.portraits import parse_ship_class_name
        assert parse_ship_class_name("Large Escort (Scout)") == "ScoutLargeEscort"

    def test_parenthetical_with_spaces(self):
        from game.ui.utils.portraits import parse_ship_class_name
        assert parse_ship_class_name("Heavy Cruiser (Battle Group)") == "BattleGroupHeavyCruiser"

    def test_multi_word_no_parens(self):
        from game.ui.utils.portraits import parse_ship_class_name
        assert parse_ship_class_name("Heavy Escort") == "HeavyEscort"

    def test_none_returns_unknown(self):
        from game.ui.utils.portraits import parse_ship_class_name
        assert parse_ship_class_name(None) == "Unknown"

    def test_empty_string(self):
        from game.ui.utils.portraits import parse_ship_class_name
        assert parse_ship_class_name("") == "Unknown"

    def test_non_string_input(self):
        from game.ui.utils.portraits import parse_ship_class_name
        assert parse_ship_class_name(42) == "42"


class TestGetShipClassColor:
    """Tests for get_ship_class_color utility."""

    def test_known_class_fighter(self):
        from game.ui.utils.portraits import get_ship_class_color
        from game.ui.colors import SHIP_CLASS_FIGHTER
        assert get_ship_class_color("Fighter") == SHIP_CLASS_FIGHTER

    def test_known_class_cruiser(self):
        from game.ui.utils.portraits import get_ship_class_color
        from game.ui.colors import SHIP_CLASS_CRUISER
        assert get_ship_class_color("Cruiser") == SHIP_CLASS_CRUISER

    def test_unknown_class_returns_default(self):
        from game.ui.utils.portraits import get_ship_class_color
        from game.ui.colors import SHIP_CLASS_DEFAULT
        assert get_ship_class_color("Dreadnought") == SHIP_CLASS_DEFAULT

    def test_none_returns_default(self):
        from game.ui.utils.portraits import get_ship_class_color
        from game.ui.colors import SHIP_CLASS_DEFAULT
        assert get_ship_class_color(None) == SHIP_CLASS_DEFAULT


class TestGetPortraitFilename:
    """Tests for get_portrait_filename utility."""

    def test_simple_class(self):
        from game.ui.utils.portraits import get_portrait_filename
        assert get_portrait_filename("Escort") == "Escort_Portrait.jpg"

    def test_parenthetical_class(self):
        from game.ui.utils.portraits import get_portrait_filename
        assert get_portrait_filename("Large Escort (Scout)") == "ScoutLargeEscort_Portrait.jpg"

    def test_multi_word(self):
        from game.ui.utils.portraits import get_portrait_filename
        assert get_portrait_filename("Heavy Cruiser") == "HeavyCruiser_Portrait.jpg"


class TestGetPortraitSearchPaths:
    """Tests for get_portrait_search_paths utility."""

    def test_returns_list(self):
        from game.ui.utils.portraits import get_portrait_search_paths
        paths = get_portrait_search_paths("Federation", "Escort")
        assert isinstance(paths, list)
        assert len(paths) >= 2

    def test_contains_theme_path(self):
        from game.ui.utils.portraits import get_portrait_search_paths
        paths = get_portrait_search_paths("Federation", "Escort")
        assert any("ShipThemes" in p and "Federation" in p for p in paths)

    def test_contains_fallback_path(self):
        from game.ui.utils.portraits import get_portrait_search_paths
        paths = get_portrait_search_paths("Federation", "Escort")
        assert any("Default_Ship_Portrait" in p for p in paths)


class TestCreatePlaceholderPortrait:
    """Tests for create_placeholder_portrait utility."""

    def test_returns_surface_of_correct_size(self):
        import pygame
        pygame.display.init()
        from game.ui.utils.portraits import create_placeholder_portrait

        surface = create_placeholder_portrait(100, 80, (50, 100, 150), "Test Ship")
        assert surface.get_width() == 100
        assert surface.get_height() == 80

    def test_returns_surface_with_subtitle(self):
        import pygame
        pygame.display.init()
        from game.ui.utils.portraits import create_placeholder_portrait

        surface = create_placeholder_portrait(200, 200, (50, 100, 150), "Test", subtitle="Escort")
        assert surface.get_width() == 200
        assert surface.get_height() == 200

    def test_returns_surface_without_subtitle(self):
        import pygame
        pygame.display.init()
        from game.ui.utils.portraits import create_placeholder_portrait

        surface = create_placeholder_portrait(64, 64, (100, 100, 100), "Mini")
        assert isinstance(surface, pygame.Surface)
