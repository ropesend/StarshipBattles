"""PROJ-376 Phase 1: Lifecycle seam tests for ``BuildQueueScreen``.

Covers the new shell-vs-yard split:
- ``__init__(initial_yard=None)`` constructs the UI shell only (no panels).
- ``open_for_yard(yard, *, hex_coord, portrait_surface=None)`` populates
  yard-specific state and reproduces today's post-init field values.
- ``hide()`` / ``show()`` / ``is_visible()`` toggle visibility without
  destroying widgets.
- Cross-context-type (planet ↔ fleet) opens trigger ``_rebuild_panels``;
  same-context-type opens reuse the existing panels.
- ``BuildQueueDragHandler.reset_state()`` clears all 5 transient drag fields.

Tests parallel the fixture pattern in
``tests/integration/ui/build_queue_screen/conftest.py`` (``MockGalaxy`` /
``MockSession`` / ``Empire`` / ``HexCoord`` / ``Planet``).
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.strategy.systems.design_library import DesignLoadResult


# -------------------------------------------------------------------------
# Local mock galaxy/session (mirror tests/integration/.../conftest.py).
# -------------------------------------------------------------------------


class _MockGalaxy:
    """Minimal mock Galaxy supporting hex-keyed planet/fleet lookup."""

    def __init__(self):
        self.systems = {}
        self._global_hex_planets: dict = {}
        self.fleets_by_id: dict = {}
        self._fleets_at_hex: dict = {}

    def get_planets_at_global_hex(self, hex_coord):
        return self._global_hex_planets.get(hex_coord, [])

    def get_fleets_at_hex(self, hex_coord):
        return self._fleets_at_hex.get(hex_coord, [])


class _MockSession:
    """Doubles as both a session and a facade for these lifecycle tests
    (PROJ-382 Phase 1: BuildQueueScreen takes facade= + portrait_session=
    instead of session=)."""

    def __init__(self, galaxy=None, empire=None, registries=None):
        self.savegame_path = "test_savegame"
        self.save_path = "test_savegame"
        self.current_empire = empire or Empire(1, "Test Empire", (255, 0, 0))
        self.active_empire = self.current_empire
        self.galaxy = galaxy or _MockGalaxy()
        self.registries = registries
        self.commands_handled: list = []
        self.turn = 0

    def get_registries(self):
        """PROJ-382 Phase 1: facade-shaped registries accessor."""
        return self.registries

    def get_colony_demographic_view(self, planet_id):
        """PROJ-382 Phase 1: facade-shaped demographic view stub."""
        return None

    def handle_command(self, cmd):
        self.commands_handled.append(cmd)
        return ValidationResult()


# -------------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------------


def _make_planet(name: str, planet_id: int, hex_coord: HexCoord) -> Planet:
    planet = Planet(
        name=name,
        location=hex_coord,
        orbit_distance=3,
        mass=5.97e24,
        radius=6371000,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.81,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.1,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
    )
    planet.owner_id = 1
    planet.id = planet_id
    yard = PlanetaryFacility(
        instance_id=f"yard_{planet_id}",
        design_id="colony_hub",
        name="Colony Hub",
        design_data={
            "layers": {
                "CORE": [{"id": "hub", "abilities": {"PlanetaryYard": True}}]
            }
        },
    )
    planet.facilities.append(yard)
    return planet


@pytest.fixture
def design_library_mock():
    mock = MagicMock()
    complex_design = MagicMock()
    complex_design.design_id = "mining_complex_mk1"
    complex_design.name = "Mining Complex"
    complex_design.vehicle_type = "Planetary Complex"
    mock.scan_designs.return_value = [complex_design]
    mock.designs_folder = "test_designs"
    mock.load_design_data.return_value = DesignLoadResult.not_found("test")
    return mock


@pytest.fixture
def design_loader_mock():
    return MagicMock()


@pytest.fixture
def hex_a():
    return HexCoord(5, 5)


@pytest.fixture
def hex_b():
    return HexCoord(7, 7)


@pytest.fixture
def empire():
    return Empire(1, "Test Empire", (255, 0, 0))


@pytest.fixture
def planet_a(hex_a):
    return _make_planet("Colony A", 100, hex_a)


@pytest.fixture
def planet_b(hex_b):
    return _make_planet("Colony B", 200, hex_b)


@pytest.fixture
def galaxy_with_planet(planet_a, hex_a):
    g = _MockGalaxy()
    g._global_hex_planets[hex_a] = [planet_a]
    return g


@pytest.fixture
def session_with_planet(galaxy_with_planet, empire, mock_registries):
    return _MockSession(
        galaxy=galaxy_with_planet, empire=empire, registries=mock_registries
    )


def _make_fleet(fleet_id: int, hex_coord: HexCoord, name: str = "Test Fleet"):
    """Build a MagicMock fleet that satisfies the panel factory's fleet path."""
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.owner_id = 1
    fleet.location = hex_coord
    fleet.context_type = "fleet"
    fleet.name = name
    fleet.display_name = name
    fleet.ships = []
    fleet.has_space_shipyard = True
    fleet.construction_queue = []
    return fleet


# -------------------------------------------------------------------------
# Task 1.1 tests
# -------------------------------------------------------------------------


def test_init_with_no_yard_constructs_ui_shell_only(
    ui_manager, session_with_planet, design_library_mock, design_loader_mock,
    galaxy_with_planet, empire,
):
    """`BuildQueueScreen(initial_yard=None)` leaves yard state empty + no panels."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        build_context=None,
        facade=session_with_planet,
        portrait_session=session_with_planet,
        on_close_callback=MagicMock(),
        design_library=design_library_mock,
        design_loader=design_loader_mock,
        hex_coord=None,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=None,
    )

    assert screen.build_context is None
    assert screen.hex_coord is None
    assert screen.queue_sources == []
    assert screen.active_queue_source is None
    assert screen.selected_queue_indices == set()
    # Shell-only: panel-dependent collaborators stay None until a yard arrives.
    assert screen.panels is None
    assert screen.controller is None
    assert screen.drag_handler is None


def test_open_for_yard_populates_state_for_planet(
    ui_manager, session_with_planet, design_library_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    """After ``open_for_yard``, all 12 yard-specific attributes are set."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    from game.strategy.data.build_queue_source import collect_build_queues_at_hex

    screen = BuildQueueScreen(
        ui_manager,
        build_context=None,
        facade=session_with_planet,
        portrait_session=session_with_planet,
        on_close_callback=MagicMock(),
        design_library=design_library_mock,
        design_loader=design_loader_mock,
        hex_coord=None,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=None,
    )
    screen.open_for_yard(planet_a, hex_coord=hex_a)

    expected_sources = collect_build_queues_at_hex(
        hex_a, galaxy_with_planet, empire,
        registries=session_with_planet.registries,
    )

    assert screen.build_context is planet_a
    assert screen.hex_coord is hex_a
    assert len(screen.queue_sources) == len(expected_sources)
    assert screen.active_queue_source is screen.queue_sources[0]
    assert screen.selected_queue_indices == {0}
    assert screen.selected_queue_index is None
    assert screen.planet_selection_window is None
    assert screen.controller.build_context is planet_a
    assert screen.controller.hex_coord is hex_a
    assert screen.controller.active_queue_source is screen.active_queue_source
    assert screen.controller.selected_category == "complex"
    assert screen.controller.selected_role == "Any"


def test_open_for_yard_initial_yard_kwarg_matches_post_open_state(
    ui_manager, session_with_planet, design_library_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    """Behavior parity: eager (`initial_yard=`) vs lazy (`open_for_yard`)
    produce identical observable yard state."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    eager = BuildQueueScreen(
        ui_manager,
        build_context=None,
        facade=session_with_planet,
        portrait_session=session_with_planet,
        on_close_callback=MagicMock(),
        design_library=design_library_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    lazy = BuildQueueScreen(
        ui_manager,
        build_context=None,
        facade=session_with_planet,
        portrait_session=session_with_planet,
        on_close_callback=MagicMock(),
        design_library=design_library_mock,
        design_loader=design_loader_mock,
        hex_coord=None,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=None,
    )
    lazy.open_for_yard(planet_a, hex_coord=hex_a)

    assert eager.build_context is lazy.build_context
    assert eager.hex_coord == lazy.hex_coord
    assert len(eager.queue_sources) == len(lazy.queue_sources)
    assert eager.selected_queue_indices == lazy.selected_queue_indices
    assert (eager.active_queue_source is None) == (
        lazy.active_queue_source is None
    )
    assert eager.selected_queue_index == lazy.selected_queue_index
    assert eager.planet_selection_window == lazy.planet_selection_window
    assert eager.controller.build_context is lazy.controller.build_context
    assert eager.controller.hex_coord == lazy.controller.hex_coord
    assert eager.controller.selected_category == lazy.controller.selected_category
    assert eager.controller.selected_role == lazy.controller.selected_role


def test_open_for_yard_planet_to_fleet_rebuilds_panels(
    ui_manager, session_with_planet, design_library_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a, hex_b,
):
    """Cross-context-type (planet→fleet) kills + reconstructs the panel tree."""
    from game.ui.panels.planet_report_panel import PlanetReportPanel
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        build_context=None,
        facade=session_with_planet,
        portrait_session=session_with_planet,
        on_close_callback=MagicMock(),
        design_library=design_library_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    assert isinstance(screen.panels.context_report, PlanetReportPanel)
    old_panels = screen.panels
    old_background = screen.panels.background

    fleet = _make_fleet(fleet_id=1, hex_coord=hex_b)
    galaxy_with_planet._fleets_at_hex[hex_b] = [fleet]
    screen.open_for_yard(fleet, hex_coord=hex_b)

    # Fresh panels object after rebuild.
    assert screen.panels is not old_panels
    # Old background was killed.
    assert not old_background.alive()
    # New context_report is NOT the planet-report variant.
    assert not isinstance(screen.panels.context_report, PlanetReportPanel)


def test_open_for_yard_planet_to_planet_does_not_rebuild_panels(
    ui_manager, session_with_planet, design_library_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, planet_b, hex_a, hex_b,
):
    """Same-context-type opens reuse the existing panel tree."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    galaxy_with_planet._global_hex_planets[hex_b] = [planet_b]

    screen = BuildQueueScreen(
        ui_manager,
        build_context=None,
        facade=session_with_planet,
        portrait_session=session_with_planet,
        on_close_callback=MagicMock(),
        design_library=design_library_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    panels_id = id(screen.panels)
    assert screen.panels.background.alive()

    screen.open_for_yard(planet_b, hex_coord=hex_b)

    assert id(screen.panels) == panels_id
    assert screen.panels.background.alive()
    assert screen.build_context is planet_b


def test_drag_handler_reset_state_clears_all_5_fields():
    """``BuildQueueDragHandler.reset_state()`` zeros the 5 transient fields."""
    from game.ui.panels.build_queue_drag_handler import BuildQueueDragHandler

    handler = BuildQueueDragHandler(
        portrait_loader=MagicMock(),
        design_library=MagicMock(),
        on_add_to_queue=MagicMock(),
        on_refresh_queue=MagicMock(),
        on_refresh_design_report=MagicMock(),
        on_remove_from_queue=MagicMock(),
    )
    handler.dragged_item = {"design_id": "x"}
    handler.drag_preview = MagicMock()
    handler.drag_start_pos = (10, 20)
    handler._pending_queue_index = 3
    handler.selected_design = "ship_001"

    handler.reset_state()

    assert handler.dragged_item is None
    assert handler.drag_preview is None
    assert handler.drag_start_pos is None
    assert handler._pending_queue_index is None
    assert handler.selected_design is None


def test_hide_makes_panels_invisible_but_alive(
    ui_manager, session_with_planet, design_library_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        build_context=None,
        facade=session_with_planet,
        portrait_session=session_with_planet,
        on_close_callback=MagicMock(),
        design_library=design_library_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    screen.hide()

    assert screen.panels.background.alive()
    assert not screen.panels.background.visible


def test_show_after_hide_makes_panels_visible(
    ui_manager, session_with_planet, design_library_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        build_context=None,
        facade=session_with_planet,
        portrait_session=session_with_planet,
        on_close_callback=MagicMock(),
        design_library=design_library_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    screen.hide()
    assert not screen.panels.background.visible
    screen.show()
    assert bool(screen.panels.background.visible)


def test_is_visible_reflects_panel_visibility(
    ui_manager, session_with_planet, design_library_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    """``is_visible()`` covers shell-only / opened / hidden / shown."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    shell = BuildQueueScreen(
        ui_manager,
        build_context=None,
        facade=session_with_planet,
        portrait_session=session_with_planet,
        on_close_callback=MagicMock(),
        design_library=design_library_mock,
        design_loader=design_loader_mock,
        hex_coord=None,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=None,
    )
    assert shell.is_visible() is False  # No panels yet.

    shell.open_for_yard(planet_a, hex_coord=hex_a)
    assert shell.is_visible() is True

    shell.hide()
    assert shell.is_visible() is False

    shell.show()
    assert shell.is_visible() is True


def test_hide_kills_planet_selection_window_if_open(
    ui_manager, session_with_planet, design_library_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        build_context=None,
        facade=session_with_planet,
        portrait_session=session_with_planet,
        on_close_callback=MagicMock(),
        design_library=design_library_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    fake_window = MagicMock()
    screen.planet_selection_window = fake_window

    screen.hide()

    assert fake_window.kill.called
    assert screen.planet_selection_window is None


# -------------------------------------------------------------------------
# PROJ-376 Phase 2 — close routing tests
# -------------------------------------------------------------------------


def test_request_close_hides_and_invokes_on_close(
    ui_manager, session_with_planet, design_library_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    """PROJ-376 Phase 2: ``_request_close`` is the close-button entry point.

    Calls ``hide()`` then ``on_close()``. Panels survive (no kill).
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    on_close = MagicMock()
    screen = BuildQueueScreen(
        ui_manager,
        build_context=None,
        facade=session_with_planet,
        portrait_session=session_with_planet,
        on_close_callback=on_close,
        design_library=design_library_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    assert screen.is_visible() is True

    screen._request_close()

    on_close.assert_called_once()
    assert not screen.is_visible()
    # Panels survive — only visibility toggled.
    assert screen.panels.background.alive()


def test_close_method_is_removed():
    """PROJ-376 Phase 2: ``_close()`` was replaced by ``_request_close()``."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    assert not hasattr(BuildQueueScreen, '_close')
    assert hasattr(BuildQueueScreen, '_request_close')


def test_request_close_can_be_re_opened(
    ui_manager, session_with_planet, design_library_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, planet_b, hex_a, hex_b,
):
    """PROJ-376 Phase 2: the cached instance is reusable after _request_close."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    galaxy_with_planet._global_hex_planets[hex_b] = [planet_b]

    screen = BuildQueueScreen(
        ui_manager,
        build_context=None,
        facade=session_with_planet,
        portrait_session=session_with_planet,
        on_close_callback=MagicMock(),
        design_library=design_library_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )
    panels_id = id(screen.panels)

    screen._request_close()
    assert not screen.is_visible()

    # Re-open at a different planet — same context type, panels reused.
    screen.open_for_yard(planet_b, hex_coord=hex_b)
    assert screen.is_visible()
    assert id(screen.panels) == panels_id
    assert screen.build_context is planet_b
