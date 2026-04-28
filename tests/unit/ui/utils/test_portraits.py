"""Tests for game.ui.utils.portraits module."""


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
