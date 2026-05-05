"""PROJ-345 T3.3: direct-coverage tests for FleetMovementEngine.calculate_next_hex.

Existing coverage in ``tests/unit/strategy/fleet_movement_engine/`` exercises
``calculate_next_hex`` indirectly through ``FleetNavigationService`` with
patched module-level helpers. This file pins the engine's *own* behavior
on the ``calculate_next_hex`` boundary:

1. Lazy nav-service initialization when the engine is built without DI.
2. Pure pass-through when a nav-service is injected (DI happy path).
3. Pass-through of a None return from the nav-service.
4. Pass-through of a HexCoord return value (identity).
5. Argument forwarding: the engine forwards (fleet, galaxy) verbatim.
6. Cached nav-service is reused on subsequent calls (no re-import).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.engine.fleet_movement_engine import FleetMovementEngine


def test_calculate_next_hex_lazy_initializes_nav_service_when_none() -> None:
    """Engine constructed with nav_service=None lazily imports + instantiates."""
    engine = FleetMovementEngine(nav_service=None)
    assert engine._nav_service is None

    fake_service_cls = MagicMock()
    fake_service = MagicMock()
    fake_service.calculate_fleet_next_hex.return_value = HexCoord(2, -1)
    fake_service_cls.return_value = fake_service

    fleet = MagicMock()
    galaxy = MagicMock()

    with patch(
        "game.strategy.services.fleet_navigation_service.FleetNavigationService",
        fake_service_cls,
    ):
        result = engine.calculate_next_hex(fleet, galaxy)

    fake_service_cls.assert_called_once_with()
    assert engine._nav_service is fake_service
    assert result == HexCoord(2, -1)


def test_calculate_next_hex_uses_injected_nav_service_without_reimport() -> None:
    """Injected nav-service is used directly; no fresh class instantiation."""
    injected = MagicMock()
    injected.calculate_fleet_next_hex.return_value = HexCoord(0, 1)
    engine = FleetMovementEngine(nav_service=injected)

    fleet = MagicMock()
    galaxy = MagicMock()

    with patch(
        "game.strategy.services.fleet_navigation_service.FleetNavigationService",
    ) as fake_cls:
        result = engine.calculate_next_hex(fleet, galaxy)
        fake_cls.assert_not_called()

    injected.calculate_fleet_next_hex.assert_called_once_with(fleet, galaxy)
    assert result == HexCoord(0, 1)


def test_calculate_next_hex_returns_none_when_service_returns_none() -> None:
    """None return value from nav-service is passed through unchanged."""
    injected = MagicMock()
    injected.calculate_fleet_next_hex.return_value = None
    engine = FleetMovementEngine(nav_service=injected)

    result = engine.calculate_next_hex(MagicMock(), MagicMock())

    assert result is None


def test_calculate_next_hex_returns_service_hexcoord_identity() -> None:
    """Returned HexCoord identity is preserved (no copy/transform)."""
    target = HexCoord(7, -3)
    injected = MagicMock()
    injected.calculate_fleet_next_hex.return_value = target
    engine = FleetMovementEngine(nav_service=injected)

    result = engine.calculate_next_hex(MagicMock(), MagicMock())

    assert result is target


def test_calculate_next_hex_forwards_fleet_and_galaxy_verbatim() -> None:
    """Engine forwards both positional arguments to nav-service unchanged."""
    injected = MagicMock()
    injected.calculate_fleet_next_hex.return_value = HexCoord(1, 0)
    engine = FleetMovementEngine(nav_service=injected)

    fleet_sentinel = MagicMock(name="fleet")
    galaxy_sentinel = MagicMock(name="galaxy")

    engine.calculate_next_hex(fleet_sentinel, galaxy_sentinel)

    injected.calculate_fleet_next_hex.assert_called_once_with(
        fleet_sentinel, galaxy_sentinel
    )


def test_calculate_next_hex_caches_nav_service_after_lazy_init() -> None:
    """After lazy init, subsequent calls reuse the same nav-service instance."""
    engine = FleetMovementEngine(nav_service=None)

    fake_service = MagicMock()
    fake_service.calculate_fleet_next_hex.side_effect = [
        HexCoord(0, 0),
        HexCoord(1, 0),
    ]
    fake_service_cls = MagicMock(return_value=fake_service)

    fleet = MagicMock()
    galaxy = MagicMock()

    with patch(
        "game.strategy.services.fleet_navigation_service.FleetNavigationService",
        fake_service_cls,
    ):
        first = engine.calculate_next_hex(fleet, galaxy)
        second = engine.calculate_next_hex(fleet, galaxy)

    # Class instantiated exactly once across both calls.
    fake_service_cls.assert_called_once_with()
    assert first == HexCoord(0, 0)
    assert second == HexCoord(1, 0)
    assert fake_service.calculate_fleet_next_hex.call_count == 2
