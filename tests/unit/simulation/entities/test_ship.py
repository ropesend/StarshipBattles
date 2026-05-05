"""Unit tests for Ship construction branches."""

import pytest

from game.core.constants import LayerType
from game.core.exceptions import ValidationException
from game.simulation.entities.ship import Ship
from game.simulation.physics_constants import DEFAULT_MAX_MASS


def test_ship_requires_registries() -> None:
    with pytest.raises(ValidationException) as exc_info:
        Ship(
            name="NoRegistries",
            x=0,
            y=0,
            color=(255, 255, 255),
            registries=None,
        )

    assert exc_info.value.context == {
        "class": "Ship",
        "parameter": "registries",
    }


def test_missing_vehicle_class_uses_fallback_layers_without_default_hull(
    fresh_registries,
) -> None:
    ship_class = "UnregisteredAuditClass"
    assert ship_class not in fresh_registries.vehicle_classes

    ship = Ship(
        name="FallbackLayers",
        x=0,
        y=0,
        color=(255, 255, 255),
        ship_class=ship_class,
        registries=fresh_registries,
    )

    assert set(ship.layers) == {
        LayerType.HULL,
        LayerType.CORE,
        LayerType.INNER,
        LayerType.OUTER,
        LayerType.ARMOR,
    }
    assert ship.layers[LayerType.HULL].components == []
    assert ship.vehicle_type == "Ship"
    assert ship.max_mass_budget == DEFAULT_MAX_MASS
