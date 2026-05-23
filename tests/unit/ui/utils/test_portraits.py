"""Tests for game.ui.utils.portraits module."""
import pygame
import pytest

from game.ui.colors import (
    SHIP_CLASS_CRUISER,
    SHIP_CLASS_DEFAULT,
    SHIP_CLASS_FIGHTER,
)
from game.ui.utils.portraits import (
    create_placeholder_portrait,
    get_ship_class_color,
)


class TestGetShipClassColor:
    """Tests for get_ship_class_color utility."""

    # PROJ-480 Task 3.33: parametrize 4 color lookups. Ids preserve
    # each branch (known classes vs. unknown vs. None default).
    @pytest.mark.parametrize(
        "class_name, expected_color",
        [
            ("Fighter", SHIP_CLASS_FIGHTER),
            ("Cruiser", SHIP_CLASS_CRUISER),
            ("Dreadnought", SHIP_CLASS_DEFAULT),
            (None, SHIP_CLASS_DEFAULT),
        ],
        ids=["known_fighter", "known_cruiser",
             "unknown_returns_default", "none_returns_default"],
    )
    def test_get_ship_class_color(self, class_name, expected_color):
        assert get_ship_class_color(class_name) == expected_color


class TestCreatePlaceholderPortrait:
    """Tests for create_placeholder_portrait utility."""

    def test_returns_surface_of_correct_size(self):
        pygame.display.init()
        surface = create_placeholder_portrait(100, 80, (50, 100, 150), "Test Ship")
        assert surface.get_width() == 100
        assert surface.get_height() == 80

    def test_returns_surface_with_subtitle(self):
        pygame.display.init()
        surface = create_placeholder_portrait(200, 200, (50, 100, 150), "Test", subtitle="Escort")
        assert surface.get_width() == 200
        assert surface.get_height() == 200

    def test_returns_surface_without_subtitle(self):
        pygame.display.init()
        surface = create_placeholder_portrait(64, 64, (100, 100, 100), "Mini")
        assert isinstance(surface, pygame.Surface)
