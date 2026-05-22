"""Tests for CameraNavigator - FEAT-04: center_on_hex for event log navigation."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord, hex_to_pixel
from game.ui.screens.strategy_camera_nav import CameraNavigator, ZOOM_KEYBOARD_STEP


def _stub_world(systems):
    """PROJ-477 Phase 4: CameraNavigator reads systems through ``scene.world``
    (live traversal seam). This stub mirrors the StrategyWorldAccess surface the
    navigator uses: ``iter_systems()`` + ``system_for_object(obj)``."""

    def _system_for_object(obj):
        return next(
            (
                s
                for s in systems
                if obj in getattr(s, "planets", [])
                or obj in getattr(s, "warp_points", [])
            ),
            None,
        )

    return SimpleNamespace(
        iter_systems=lambda: iter(systems),
        system_for_object=_system_for_object,
    )


class MockScene:
    """Mock scene providing camera and hex_size for CameraNavigator."""

    def __init__(self, hex_size=50):
        self.camera = MagicMock()
        self.camera.position = MagicMock()
        self.camera.position.x = 0.0
        self.camera.position.y = 0.0
        self.hex_size = hex_size
        self.systems = []
        self.world = _stub_world(self.systems)


class TestCenterOnHex:
    """Test CameraNavigator.center_on_hex for direct hex coordinate navigation."""

    def test_center_on_hex_sets_camera_position(self):
        """center_on_hex should set camera position to hex pixel coordinates."""
        scene = MockScene(hex_size=50)
        nav = CameraNavigator(scene)

        target = HexCoord(5, -3)
        nav.center_on_hex(target)

        expected_x, expected_y = hex_to_pixel(target, 50)
        assert scene.camera.position.x == expected_x
        assert scene.camera.position.y == expected_y

    def test_center_on_hex_origin(self):
        """center_on_hex at origin should set camera to (0, 0) pixel position."""
        scene = MockScene(hex_size=50)
        nav = CameraNavigator(scene)

        target = HexCoord(0, 0)
        nav.center_on_hex(target)

        assert scene.camera.position.x == 0.0
        assert scene.camera.position.y == 0.0


class _ZoomScene:
    """Mock scene with a real-attribute camera for keyboard zoom step tests.

    MagicMock's auto-attributes don't behave well with arithmetic mutation,
    so we use a plain object exposing target_zoom / min_zoom / max_zoom.
    """

    def __init__(self, target_zoom: float = 1.0, min_zoom: float = 0.01, max_zoom: float = 5.0):
        camera = type("_Cam", (), {})()
        camera.target_zoom = target_zoom
        camera.min_zoom = min_zoom
        camera.max_zoom = max_zoom
        self.camera = camera
        self.hex_size = 50
        self.systems = []
        self.world = _stub_world(self.systems)


class TestZoomInStep:
    """FEAT-21: keyboard zoom-in step on CameraNavigator."""

    def test_zoom_in_multiplies_target_zoom_by_step(self):
        scene = _ZoomScene(target_zoom=1.0)
        nav = CameraNavigator(scene)

        nav.zoom_in_step()

        assert scene.camera.target_zoom == pytest.approx(1.0 * ZOOM_KEYBOARD_STEP)

    def test_zoom_in_clamps_at_max_zoom(self):
        scene = _ZoomScene(target_zoom=4.9, max_zoom=5.0)
        nav = CameraNavigator(scene)

        # 4.9 * 1.5 = 7.35, must clamp to 5.0
        nav.zoom_in_step()
        assert scene.camera.target_zoom == 5.0

        # Repeated presses stay at max
        nav.zoom_in_step()
        assert scene.camera.target_zoom == 5.0


class TestZoomOutStep:
    """FEAT-21: keyboard zoom-out step on CameraNavigator."""

    def test_zoom_out_divides_target_zoom_by_step(self):
        scene = _ZoomScene(target_zoom=1.0)
        nav = CameraNavigator(scene)

        nav.zoom_out_step()

        assert scene.camera.target_zoom == pytest.approx(1.0 / ZOOM_KEYBOARD_STEP)

    def test_zoom_out_clamps_at_min_zoom(self):
        scene = _ZoomScene(target_zoom=0.012, min_zoom=0.01)
        nav = CameraNavigator(scene)

        # 0.012 / 1.5 = 0.008, must clamp to 0.01
        nav.zoom_out_step()
        assert scene.camera.target_zoom == 0.01

        # Repeated presses stay at min
        nav.zoom_out_step()
        assert scene.camera.target_zoom == 0.01


class TestZoomStepReversibility:
    """One zoom-in followed by one zoom-out returns to ~original target_zoom."""

    def test_in_then_out_returns_to_origin(self):
        scene = _ZoomScene(target_zoom=1.0)
        nav = CameraNavigator(scene)

        nav.zoom_in_step()
        nav.zoom_out_step()

        assert scene.camera.target_zoom == pytest.approx(1.0)


class _Camera:
    def __init__(self, *, width: int = 1000, height: int = 800) -> None:
        self.position = SimpleNamespace(x=0.0, y=0.0)
        self.width = width
        self.height = height
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.min_zoom = 0.2
        self.max_zoom = 5.0


def _system(name: str, location: HexCoord) -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        global_location=location,
        stars=[],
        planets=[],
        warp_points=[],
    )


def _planet(location: HexCoord) -> SimpleNamespace:
    return SimpleNamespace(planet_type=SimpleNamespace(name="Rocky"), location=location)


def _fleet(location: HexCoord) -> SimpleNamespace:
    return SimpleNamespace(ships=[], orders=[], location=location)


class TestCenterOnObjects:
    def test_center_on_planet_resolves_system_local_location(self):
        planet = _planet(HexCoord(2, -1))
        system = _system("Sol", HexCoord(10, 4))
        system.planets = [planet]
        scene = SimpleNamespace(camera=_Camera(), hex_size=50, systems=[system], world=_stub_world([system]))
        nav = CameraNavigator(scene)

        nav.center_on(planet)

        expected_x, expected_y = hex_to_pixel(HexCoord(12, 3), 50)
        assert scene.camera.position.x == expected_x
        assert scene.camera.position.y == expected_y

    def test_center_on_fleet_uses_global_location(self):
        fleet = _fleet(HexCoord(-3, 8))
        scene = SimpleNamespace(camera=_Camera(), hex_size=50, systems=[], world=_stub_world([]))
        nav = CameraNavigator(scene)

        nav.center_on(fleet)

        expected_x, expected_y = hex_to_pixel(HexCoord(-3, 8), 50)
        assert scene.camera.position.x == expected_x
        assert scene.camera.position.y == expected_y

    def test_center_on_unknown_object_leaves_camera_position(self):
        scene = SimpleNamespace(camera=_Camera(), hex_size=50, systems=[], world=_stub_world([]))
        scene.camera.position.x = 123.0
        scene.camera.position.y = 456.0
        nav = CameraNavigator(scene)

        nav.center_on(object())

        assert scene.camera.position.x == 123.0
        assert scene.camera.position.y == 456.0


class TestZoomToGalaxy:
    def test_camera_zoom_to_galaxy_bounds_clamps(self):
        systems = [_system("A", HexCoord(-100, 0)), _system("B", HexCoord(100, 0))]
        scene = SimpleNamespace(camera=_Camera(width=100, height=100), hex_size=50, systems=systems, world=_stub_world(systems))
        nav = CameraNavigator(scene)

        nav.zoom_to_galaxy()

        assert scene.camera.zoom == scene.camera.min_zoom
        assert scene.camera.target_zoom == scene.camera.min_zoom

    def test_zoom_to_galaxy_centers_between_system_positions(self):
        systems = [_system("A", HexCoord(0, 0)), _system("B", HexCoord(4, 0))]
        scene = SimpleNamespace(camera=_Camera(width=4000, height=4000), hex_size=50, systems=systems, world=_stub_world(systems))
        nav = CameraNavigator(scene)

        nav.zoom_to_galaxy()

        a_x, a_y = hex_to_pixel(systems[0].global_location, 50)
        b_x, b_y = hex_to_pixel(systems[1].global_location, 50)
        assert scene.camera.position.x == pytest.approx((a_x + b_x) / 2)
        assert scene.camera.position.y == pytest.approx((a_y + b_y) / 2)
        assert scene.camera.min_zoom <= scene.camera.zoom <= scene.camera.max_zoom

    def test_zoom_to_galaxy_no_systems_is_noop(self):
        scene = SimpleNamespace(camera=_Camera(), hex_size=50, systems=[], world=_stub_world([]))
        scene.camera.position.x = 12.0
        scene.camera.zoom = 1.25
        nav = CameraNavigator(scene)

        nav.zoom_to_galaxy()

        assert scene.camera.position.x == 12.0
        assert scene.camera.zoom == 1.25


class TestZoomToSystem:
    def test_zoom_to_system_uses_last_selected_system(self):
        system = _system("Sol", HexCoord(8, -2))
        scene = SimpleNamespace(
            camera=_Camera(),
            hex_size=50,
            systems=[system],
            world=_stub_world([system]),
            last_selected_system=system,
            selected_object=None,
        )
        nav = CameraNavigator(scene)

        nav.zoom_to_system()

        expected_x, expected_y = hex_to_pixel(system.global_location, 50)
        assert scene.camera.position.x == expected_x
        assert scene.camera.position.y == expected_y
        assert scene.camera.zoom == 2.0
        assert scene.camera.target_zoom == 2.0

    def test_zoom_to_system_infers_from_selected_planet(self):
        planet = _planet(HexCoord(1, 0))
        system = _system("Sol", HexCoord(4, 4))
        system.planets = [planet]
        scene = SimpleNamespace(
            camera=_Camera(),
            hex_size=50,
            systems=[system],
            world=_stub_world([system]),
            last_selected_system=None,
            selected_object=planet,
        )
        nav = CameraNavigator(scene)

        nav.zoom_to_system()

        expected_x, expected_y = hex_to_pixel(system.global_location, 50)
        assert scene.camera.position.x == expected_x
        assert scene.camera.position.y == expected_y
        assert scene.camera.zoom == 2.0

    def test_zoom_to_system_without_target_is_noop(self):
        scene = SimpleNamespace(
            camera=_Camera(),
            hex_size=50,
            systems=[],
            world=_stub_world([]),
            last_selected_system=None,
            selected_object=None,
        )
        scene.camera.position.x = 9.0
        scene.camera.zoom = 1.1
        nav = CameraNavigator(scene)

        nav.zoom_to_system()

        assert scene.camera.position.x == 9.0
        assert scene.camera.zoom == 1.1


class TestCycleSelection:
    def test_cycle_selection_wraps_forward_from_no_selection(self):
        first = object()
        second = object()
        scene = SimpleNamespace(
            camera=_Camera(),
            hex_size=50,
            systems=[],
            world=_stub_world([]),
            selected_object=None,
            current_empire=SimpleNamespace(colonies=[first, second], fleets=[]),
        )
        nav = CameraNavigator(scene)

        assert nav.cycle_selection("colony", 1) is first

    def test_cycle_selection_wraps_backward_from_first_target(self):
        first = object()
        second = object()
        scene = SimpleNamespace(
            camera=_Camera(),
            hex_size=50,
            systems=[],
            world=_stub_world([]),
            selected_object=first,
            current_empire=SimpleNamespace(colonies=[], fleets=[first, second]),
        )
        nav = CameraNavigator(scene)

        assert nav.cycle_selection("fleet", -1) is second

    def test_cycle_selection_unknown_type_returns_none(self):
        scene = SimpleNamespace(
            camera=_Camera(),
            hex_size=50,
            systems=[],
            world=_stub_world([]),
            selected_object=None,
            current_empire=SimpleNamespace(colonies=[object()], fleets=[object()]),
        )
        nav = CameraNavigator(scene)

        assert nav.cycle_selection("station", 1) is None
