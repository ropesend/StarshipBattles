"""Branch tests for builder schematic view sizing helpers."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame

from game.ui.screens.builder.schematic_view import SchematicView


def _make_view(class_definition):
    service = MagicMock()
    service.get_class_definition.return_value = class_definition
    view = SchematicView(
        pygame.Rect(0, 0, 200, 200),
        sprite_manager=MagicMock(),
        theme_manager=MagicMock(),
        vehicle_class_service=service,
    )
    return view, service


def test_schematic_max_radius_cube_root_scaling_uses_vehicle_class_mass():
    view, service = _make_view({"max_mass": 64_000})
    ship = SimpleNamespace(ship_class="Dreadnought")

    assert view._calculate_max_r(ship) == 280
    service.get_class_definition.assert_called_once_with("Dreadnought")


def test_schematic_max_radius_uses_default_mass_when_class_definition_missing():
    view, service = _make_view(None)
    ship = SimpleNamespace(ship_class="Unknown")

    assert view._calculate_max_r(ship) == 70
    service.get_class_definition.assert_called_once_with("Unknown")
