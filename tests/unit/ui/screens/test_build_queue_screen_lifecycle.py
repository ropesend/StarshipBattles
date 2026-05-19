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
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.systems.design_repository import DesignLoadResult


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
    instead of session=.  PROJ-396 MAJ-002: portrait_session was retired in
    favor of theme_id_supplier — these tests pass ``lambda: "Federation"``)."""

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

    def get_turn_number(self) -> int:
        """PROJ-396 MAJ-003: facade-shaped turn-number accessor."""
        return self.turn

    def get_save_path(self):
        """PROJ-396 MAJ-004: facade-shaped save-path accessor."""
        return self.save_path

    # PROJ-430 / TD-08: expose grouped namespace accessors so production
    # code that calls ``facade.session_meta.registries()`` etc. resolves on the
    # mock without rewriting every helper method.
    @property
    def economy(self):
        class _EconomyNS:
            def __init__(self, parent):
                self._parent = parent
            def colony_demographic_view(self, planet_id):
                return self._parent.get_colony_demographic_view(planet_id) if hasattr(self._parent, "get_colony_demographic_view") else None
            def race_registry(self):
                return getattr(self._parent, "race_registry", None)
            def resolve_config(self):
                return getattr(self._parent, "economy_config", None)
        return _EconomyNS(self)

    @property
    def session_meta(self):
        class _SessionMetaNS:
            def __init__(self, parent):
                self._parent = parent
            def turn_number(self):
                if hasattr(self._parent, "get_turn_number"):
                    return self._parent.get_turn_number()
                return getattr(self._parent, "turn_number", 0)
            def save_path(self):
                if hasattr(self._parent, "get_save_path"):
                    return self._parent.get_save_path()
                return getattr(self._parent, "savegame_path", None) or getattr(self._parent, "save_path", None)
            def human_player_ids(self):
                if hasattr(self._parent, "get_human_player_ids"):
                    return self._parent.get_human_player_ids()
                return getattr(self._parent, "human_player_ids", [])
            def registries(self):
                return self._parent.get_registries() if hasattr(self._parent, "get_registries") else self._parent.registries
        return _SessionMetaNS(self)

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
def design_catalog_mock():
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
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire,
):
    """`BuildQueueScreen(initial_yard=None)` leaves yard state empty + no panels."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
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
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    """After ``open_for_yard``, all 12 yard-specific attributes are set."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    from game.strategy.data.build_queue_source import collect_build_queues_at_hex

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
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
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    """Behavior parity: eager (`initial_yard=`) vs lazy (`open_for_yard`)
    produce identical observable yard state."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    eager = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    lazy = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
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
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a, hex_b,
):
    """Cross-context-type (planet→fleet) kills + reconstructs the panel tree."""
    from game.ui.panels.planet_report_panel import PlanetReportPanel
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
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
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, planet_b, hex_a, hex_b,
):
    """Same-context-type opens reuse the existing panel tree."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    galaxy_with_planet._global_hex_planets[hex_b] = [planet_b]

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
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


# =========================================================================
# Obs 2 (PROJ-376 follow-up): planet info panel must refresh on yard switch
# =========================================================================
#
# BuildQueueScreen.open_for_yard() caches the screen across opens
# (PROJ-376 Phase 2) and updates build_context + the queue selector, but
# never refreshes the PlanetReportPanel — so re-opening on Planet B while
# panels were last bound to Planet A leaves Planet A's report visible.
#
# Fix: open_for_yard() calls panels.planet_report.update_planet(...) when
# the new yard is a planet and a planet_report panel already exists.
# When the previous context was a fleet (planet_report is None), or when
# the new context is a fleet, _rebuild_panels handles the transition.
# =========================================================================


def test_obs2_open_for_yard_planet_to_planet_refreshes_planet_report(
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, planet_b, hex_a, hex_b,
):
    """Open on Planet A → open on Planet B → panels.planet_report.planet
    must now be planet_b (was previously stuck at planet_a)."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    galaxy_with_planet._global_hex_planets[hex_b] = [planet_b]

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    assert screen.panels.planet_report is not None
    assert screen.panels.planet_report.planet is planet_a

    screen.open_for_yard(planet_b, hex_coord=hex_b)

    assert screen.panels.planet_report is not None, (
        "Obs 2: planet→planet open must keep the planet_report panel."
    )
    assert screen.panels.planet_report.planet is planet_b, (
        "Obs 2: planet→planet re-open must refresh planet_report.planet "
        "to the new yard. Today the cached panel stays bound to the "
        "previous planet, showing stale info on the new open."
    )


def test_obs2_open_for_yard_fleet_to_planet_rebuilds_panels(
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a, hex_b,
):
    """Fleet → Planet transition: panels.planet_report is None before
    the open (fleet path), so the screen MUST force _rebuild_panels to
    construct the PlanetReportPanel for the new context."""
    from game.ui.panels.planet_report_panel import PlanetReportPanel
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    fleet = _make_fleet(fleet_id=1, hex_coord=hex_b)
    galaxy_with_planet._fleets_at_hex[hex_b] = [fleet]
    galaxy_with_planet._global_hex_planets[hex_a] = [planet_a]

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_b,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=fleet,
    )

    # Fleet context: planet_report is None.
    assert screen.panels.planet_report is None

    # Switch to a planet.
    screen.open_for_yard(planet_a, hex_coord=hex_a)

    # Now planet_report must exist and be bound to planet_a.
    assert isinstance(screen.panels.context_report, PlanetReportPanel)
    assert screen.panels.planet_report is not None
    assert screen.panels.planet_report.planet is planet_a


def test_obs2_open_for_yard_planet_to_fleet_round_trip_back_to_planet(
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, planet_b, hex_a, hex_b,
):
    """Planet → Fleet → Planet round trip: the final planet_report must
    reflect the *new* planet, not the originally-opened one."""
    from game.ui.panels.planet_report_panel import PlanetReportPanel
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    fleet_hex = HexCoord(9, 9)
    fleet = _make_fleet(fleet_id=2, hex_coord=fleet_hex)
    galaxy_with_planet._fleets_at_hex[fleet_hex] = [fleet]
    galaxy_with_planet._global_hex_planets[hex_b] = [planet_b]

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    # Start: planet_a is bound.
    assert screen.panels.planet_report.planet is planet_a

    # Hop to fleet (cross-type — rebuilds panels, planet_report becomes None).
    screen.open_for_yard(fleet, hex_coord=fleet_hex)
    assert screen.panels.planet_report is None

    # Hop back to a *different* planet — must rebuild to a planet panel
    # AND bind to planet_b (not planet_a's stale reference).
    screen.open_for_yard(planet_b, hex_coord=hex_b)
    assert isinstance(screen.panels.context_report, PlanetReportPanel)
    assert screen.panels.planet_report is not None
    assert screen.panels.planet_report.planet is planet_b


# =========================================================================
# QA Obs 2 (2026-05-16): BuildQueueController.design_catalog not rebound
# on cached BuildQueueScreen reuse across player swap
# =========================================================================
#
# PROJ-410 Phase 4 Task 4.2 rebinds screen.design_catalog + drag_handler.design_catalog
# on the cached BuildQueueScreen when the manager calls open_for_yard with a
# fresh DesignLibrary (e.g. on hot-seat player swap). But the controller was
# constructed once in _rebuild_panels with the original DesignLibrary and its
# own self.design_catalog is never updated. Result: controller.scan_designs()
# reads from the original empire's folder even after the screen "thinks" it's
# bound to the new empire's library.
# =========================================================================


def test_obs_p2_design_catalog_open_for_yard_rebinds_controller_design_catalog(
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, planet_b, hex_a, hex_b,
):
    """Caller (strategy_build_queue_manager) sets screen.design_catalog to a
    new instance before open_for_yard. The controller must follow."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    galaxy_with_planet._global_hex_planets[hex_b] = [planet_b]

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    # Initial controller library matches the construction-time library.
    assert screen.controller.design_catalog is design_catalog_mock

    # Caller swaps to a new empire's library + loader (manager flow).
    new_library = MagicMock()
    new_library.scan_designs.return_value = []
    new_library.designs_folder = "test_designs_empire_2"
    new_library.load_design_data.return_value = (
        design_catalog_mock.load_design_data.return_value
    )
    new_loader = MagicMock()
    screen.design_catalog = new_library
    screen.design_loader = new_loader

    screen.open_for_yard(planet_b, hex_coord=hex_b)

    assert screen.controller.design_catalog is new_library, (
        "QA Obs 2: open_for_yard must rebind controller.design_catalog to "
        "the screen's current library. Without this, the cached controller "
        "keeps scanning the previous empire's designs folder after a "
        "hot-seat player swap (and rebind by the manager)."
    )
    assert screen.controller.design_loader is new_loader, (
        "QA Obs 2: open_for_yard must rebind controller.design_loader for "
        "parity with the library rebind."
    )


def test_drag_handler_reset_state_clears_all_5_fields():
    """``BuildQueueDragHandler.reset_state()`` zeros the 5 transient fields."""
    from game.ui.panels.build_queue_drag_handler import BuildQueueDragHandler

    handler = BuildQueueDragHandler(
        portrait_loader=MagicMock(),
        design_catalog=MagicMock(),
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
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
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
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
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
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    """``is_visible()`` covers shell-only / opened / hidden / shown."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    shell = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
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
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
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
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    """PROJ-376 Phase 2: ``_request_close`` is the close-button entry point.

    Calls ``hide()`` then ``on_close()``. Panels survive (no kill).
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    on_close = MagicMock()
    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=on_close,
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    assert screen.is_visible() is True

    screen._input_router._request_close()

    on_close.assert_called_once()
    assert not screen.is_visible()
    # Panels survive — only visibility toggled.
    assert screen.panels.background.alive()


def test_close_method_is_removed():
    """PROJ-376 Phase 2: ``_close()`` was replaced by ``_request_close()``.

    PROJ-457 Phase 1: ``_request_close`` was relocated from the screen to
    ``BuildQueueInputRouter``; the screen no longer carries either name.
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    from game.ui.screens.build_queue_input_router import BuildQueueInputRouter

    assert not hasattr(BuildQueueScreen, '_close')
    assert hasattr(BuildQueueInputRouter, '_request_close')


# =========================================================================
# PROJ-410: Build Queue Widget Cache Invalidation regression tests
# =========================================================================
#
# These tests assert the contract introduced by PROJ-410:
#   - VirtualTable exposes an `invalidate_widget_caches()` method (Phase 2).
#   - BuildQueueRenderer.refresh_queue_display() calls it on every push (Phase 3 B-hook).
#   - BuildQueueScreen.open_for_yard() resets controller queue refs even
#     when the new yard has zero sources (Phase 3 C-hook + Task 3.6).
#
# All tests below FAIL on current `main` (attribute does not exist) and
# PASS after Phase 2 + Phase 3 lands. They are intentionally written
# against the new contract — Strict TDD per AGENTS.md Rule 1.
# =========================================================================


def _planet_with_two_yards(name: str, planet_id: int, hex_coord: HexCoord) -> Planet:
    """Like _make_planet, but with BOTH a PlanetaryYard and a SpaceShipyard
    facility. Used for Task 1.5 (ship-yard <-> planetary-yard switch)."""
    planet = _make_planet(name, planet_id, hex_coord)
    shipyard = PlanetaryFacility(
        instance_id=f"shipyard_{planet_id}",
        design_id="space_shipyard",
        name="Space Shipyard",
        design_data={
            "layers": {
                "CORE": [{"id": "syd", "abilities": {"SpaceShipyardAbility": True}}]
            }
        },
    )
    planet.facilities.append(shipyard)
    return planet


def _planet_zero_sources(name: str, planet_id: int, hex_coord: HexCoord) -> Planet:
    """Like _make_planet, but with no yard facilities. Used for Task 1.9."""
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
    return planet


def _spy_invalidate(vt):
    """Wrap virtual_table.invalidate_widget_caches in a Mock spy.

    Returns the spy. Asserts the method exists first (Phase 2 contract).
    On current `main`, this assertion fails with a clear message — the
    test is intentionally red until Phase 2 lands.
    """
    assert hasattr(vt, "invalidate_widget_caches"), (
        "PROJ-410 Phase 2: VirtualTable must expose invalidate_widget_caches() method. "
        "See Projects/active_projects/PROJ-410/phase_2_checklist.md Task 2.2."
    )
    original = vt.invalidate_widget_caches
    spy = MagicMock(side_effect=original)
    vt.invalidate_widget_caches = spy
    return spy


def test_PROJ410_task_1_2_yard_switch_invalidates_widget_caches(
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    """Task 1.2: switching the active queue source on the same planet must
    invalidate widget caches in the row pool.

    Today: VirtualTable has no invalidate_widget_caches() method.
    After Phase 2 + Phase 3 Task 3.1: renderer calls invalidate on every refresh.
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    vt = screen.panels.virtual_table
    spy = _spy_invalidate(vt)

    # Trigger a refresh that pushes new data via the renderer's B-hook.
    # _refresh_queue_display routes through refresh_queue_display(), which
    # is where the invalidation must happen.
    screen._input_router._refresh_queue_display()

    assert spy.call_count >= 1, (
        "PROJ-410 Phase 3 Task 3.1: BuildQueueRenderer.refresh_queue_display() "
        "must call virtual_table.invalidate_widget_caches() before pushing new data."
    )


def test_PROJ410_task_1_3_close_and_reopen_invalidates_cache(
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    """Task 1.3: close + reopen on the same yard must flush widget caches.

    Today: panels survive close (PROJ-376), but caches are not flushed on
    reopen, so any data mutation between close and reopen leaves stale
    rows visible.
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    vt = screen.panels.virtual_table
    spy = _spy_invalidate(vt)
    panels_id_before = id(screen.panels)

    # Close (panels survive).
    screen._input_router._request_close()
    assert not screen.is_visible()

    # Reopen on the same yard.
    screen.open_for_yard(planet_a, hex_coord=hex_a)

    # Same panel tree (perf-lock).
    assert id(screen.panels) == panels_id_before
    # Cache invalidation MUST have fired on reopen.
    assert spy.call_count >= 1, (
        "PROJ-410: reopening a closed BuildQueueScreen must invalidate the "
        "VirtualTable's widget caches; otherwise rows display stale data from "
        "before the close."
    )


def test_PROJ410_task_1_5_ship_yard_to_planetary_yard_invalidates(
    ui_manager, design_catalog_mock, design_loader_mock, empire, hex_a, mock_registries,
):
    """Task 1.5: switching between ship-yard and planetary-yard on the
    SAME planet must invalidate widget caches between yard activations.
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    planet = _planet_with_two_yards("Twin-Yard", 300, hex_a)
    galaxy = _MockGalaxy()
    galaxy._global_hex_planets[hex_a] = [planet]
    session = _MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)

    screen = BuildQueueScreen(
        ui_manager,
        facade=session,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy,
        empire=empire,
        initial_yard=planet,
    )

    # Twin-yard planet collects a single base BuildQueueSource that
    # handles both ship and complex production (can_build_complexes=True,
    # can_build_ships=False on this hub). The yard-switching scenario in
    # the QA report manifests at the queue-display level: re-rendering
    # the queue with mutated content must always invalidate the row pool.
    assert len(screen.queue_sources) >= 1

    vt = screen.panels.virtual_table
    spy = _spy_invalidate(vt)

    # Simulate a yard-context refresh (mutated queue content).
    screen._input_router._refresh_queue_display()

    assert spy.call_count >= 1, (
        "PROJ-410: every queue-display refresh must invalidate widget caches; "
        "ship-yard and planetary-yard contents must not bleed across switches."
    )


def test_PROJ410_task_1_7_yard_selector_renders_for_second_empire(
    ui_manager, design_catalog_mock, design_loader_mock, hex_a, mock_registries,
):
    """Task 1.7: when the cached BuildQueueScreen is reused for a second
    empire's planet, the yard selector must enumerate the second empire's
    yards (filtered by planet.owner_id == new empire.id).

    Today (per Codex review arc01-002): the cached `screen.empire` retains
    empire 1's reference, so `collect_build_queues_at_hex` filters as
    empire 1 -- empire 2 sees no yards. Phase 4 Task 4.2 fixes this by
    rebinding `cached_screen.empire` before each `open_for_yard()`.

    This test simulates the rebind-then-open path. It fails today because
    the `screen.empire` rebind is not yet a documented contract; the
    fix in Phase 4 makes the manager perform it.
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    from game.strategy.data.build_queue_source import collect_build_queues_at_hex

    empire_1 = Empire(1, "Empire One", (255, 0, 0))
    empire_2 = Empire(2, "Empire Two", (0, 0, 255))

    # Empire 1's planet at hex_a.
    planet_1 = _planet_with_two_yards("Colony 1", 100, hex_a)
    planet_1.owner_id = 1

    # Empire 2's planet at hex_b (different hex to avoid filtering collisions).
    hex_b = HexCoord(7, 7)
    planet_2 = _planet_with_two_yards("Colony 2", 200, hex_b)
    planet_2.owner_id = 2

    galaxy = _MockGalaxy()
    galaxy._global_hex_planets[hex_a] = [planet_1]
    galaxy._global_hex_planets[hex_b] = [planet_2]

    # Session starts on empire 1.
    session = _MockSession(galaxy=galaxy, empire=empire_1, registries=mock_registries)

    screen = BuildQueueScreen(
        ui_manager,
        facade=session,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy,
        empire=empire_1,
        initial_yard=planet_1,
    )
    e1_source_count = len(screen.queue_sources)
    assert e1_source_count >= 1

    # Close (panels survive — production reuse).
    screen._input_router._request_close()

    # Phase 4 Task 4.2 wired the manager to rebind these refs before
    # every open_for_yard(). At the screen level we exercise the same
    # contract: the screen must accept rebound empire/galaxy/facade and
    # query queues against the new empire. (The manager-level path has
    # its own tests in test_strategy_build_queue_manager.py.)
    screen.empire = empire_2
    screen.galaxy = galaxy
    screen.facade = session

    # Reopen on empire 2's planet.
    screen.open_for_yard(planet_2, hex_coord=hex_b)

    # Yard selector must enumerate empire 2's yards (collected via the
    # rebound empire reference).
    expected_e2_sources = collect_build_queues_at_hex(
        hex_b, galaxy, empire_2, registries=mock_registries,
    )
    assert len(screen.queue_sources) == len(expected_e2_sources), (
        f"PROJ-410: after rebind, expected {len(expected_e2_sources)} "
        f"yards for empire 2 at hex_b, got {len(screen.queue_sources)}. "
        f"This indicates open_for_yard is still filtering by empire 1's id "
        f"(verify the screen.empire reassignment landed)."
    )
    assert len(screen.queue_sources) >= 1, (
        "PROJ-410 Task 1.7: empire 2's planet has yards but selector lists none."
    )

    # The yard selector must be visible (container.show propagation).
    # The `panels.background.visible` is the screen-level toggle; the
    # queue_selector's container must also be visible.
    assert screen.is_visible(), "screen must be visible after open"
    selector = screen.panels.queue_selector
    # The selector exposes _container or similar; this assertion may need
    # refinement during Phase 3 Task 3.4 implementation.
    assert getattr(selector, "active_source", None) is not None, (
        "PROJ-410: after rebind+open, the queue selector must have an active "
        "source for empire 2's yards."
    )


def test_PROJ410_task_1_9_zero_source_yard_clears_controller_queue_refs(
    ui_manager, design_catalog_mock, design_loader_mock, empire, hex_a, hex_b, mock_registries,
):
    """Task 1.9: when switching to a planet with NO yard facilities,
    controller.active_queue_source AND controller.selected_queue_sources
    must both be cleared.

    Today: open_for_yard() only calls controller.set_active_queue() when
    source is non-None (build_queue_screen.py:322-324). Zero-source yards
    leave controller refs populated with the prior yard's data.
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    planet_with_yard = _make_planet("With Yard", 400, hex_a)
    planet_zero = _planet_zero_sources("Zero Yard", 500, hex_b)

    galaxy = _MockGalaxy()
    galaxy._global_hex_planets[hex_a] = [planet_with_yard]
    galaxy._global_hex_planets[hex_b] = [planet_zero]
    session = _MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)

    screen = BuildQueueScreen(
        ui_manager,
        facade=session,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy,
        empire=empire,
        initial_yard=planet_with_yard,
    )
    # Sanity: yard A populated controller refs.
    assert screen.controller.active_queue_source is not None
    assert len(screen.queue_sources) >= 1

    # Switch to the zero-source planet.
    screen.open_for_yard(planet_zero, hex_coord=hex_b)

    # Both controller refs must be cleared.
    assert screen.controller.active_queue_source is None, (
        "PROJ-410 Task 1.9: zero-source yard switch must clear "
        "controller.active_queue_source. See Phase 3 Task 3.6."
    )
    selected = getattr(screen.controller, "selected_queue_sources", None)
    if selected is None:
        selected = []
    assert list(selected) == [], (
        f"PROJ-410 Task 1.9: zero-source yard switch must clear "
        f"controller.selected_queue_sources, got {selected!r}. "
        f"See Phase 3 Task 3.6."
    )


def test_request_close_can_be_re_opened(
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, planet_b, hex_a, hex_b,
):
    """PROJ-376 Phase 2: the cached instance is reusable after _request_close."""
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    galaxy_with_planet._global_hex_planets[hex_b] = [planet_b]

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )
    panels_id = id(screen.panels)

    screen._input_router._request_close()
    assert not screen.is_visible()

    # Re-open at a different planet — same context type, panels reused.
    screen.open_for_yard(planet_b, hex_coord=hex_b)
    assert screen.is_visible()
    assert id(screen.panels) == panels_id
    assert screen.build_context is planet_b


# =========================================================================
# Issue #17 regression tests
# =========================================================================
#
# Issue #17: after switching to a non-default yard, adding items, closing,
# and re-opening, the panel shows stale rows from the previously-active
# yard until first interaction. Two co-located bugs:
#
# 1) ``open_for_yard()`` never invokes ``renderer.update_queue_header(...)``,
#    so the header text remains bound to the previously-active source.
# 2) When the active queue source resets to ``queue_sources[0]`` on re-open,
#    ``update_visible_rows()`` correctly hides surplus pool rows via
#    ``row["bg"].hide()`` — but the subsequent ``self.show()`` calls
#    ``panels.background.show()`` which is pygame_gui's
#    ``UIPanel.show(show_contents=True)`` and recursively un-hides every
#    child via ``UIContainer.show``, re-exposing stale label text on those
#    rows. (Verified against pygame-ce 2.5.7's pygame_gui source.)
#
# The fix calls ``renderer.update_queue_header(self.active_queue_source)``
# in ``open_for_yard`` and extends ``invalidate_widget_caches`` to also
# clear pygame_gui widget content (set_text("")/set_image(blank)), not
# just the cache attrs.
# =========================================================================


def test_issue17_open_for_yard_invokes_update_queue_header(
    ui_manager, session_with_planet, design_catalog_mock, design_loader_mock,
    galaxy_with_planet, empire, planet_a, hex_a,
):
    """Issue #17 (header path): ``open_for_yard`` must invoke
    ``renderer.update_queue_header(self.active_queue_source)`` so the title
    bar reflects the active source after re-open / yard switch.

    Today ``update_queue_header`` is only invoked from
    ``_on_queue_selection_changed`` (build_queue_screen.py:407). On re-open
    the active source resets to ``queue_sources[0]`` but the header still
    points at whatever yard the user last clicked into.
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    screen = BuildQueueScreen(
        ui_manager,
        facade=session_with_planet,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy_with_planet,
        empire=empire,
        initial_yard=planet_a,
    )

    # Spy on update_queue_header to count invocations on re-open.
    original = screen.renderer.update_queue_header
    spy = MagicMock(side_effect=original)
    screen.renderer.update_queue_header = spy

    screen._input_router._request_close()
    screen.open_for_yard(planet_a, hex_coord=hex_a)

    assert spy.call_count >= 1, (
        "Issue #17: BuildQueueScreen.open_for_yard() must invoke "
        "renderer.update_queue_header(self.active_queue_source) so the "
        "title bar matches the active source after re-open."
    )
    # The arg must be the active queue source (not None when sources exist).
    last_call_args = spy.call_args
    assert last_call_args.args[0] is screen.active_queue_source, (
        "Issue #17: update_queue_header must be passed the current "
        "active_queue_source, so the title agrees with the rendered rows."
    )


def test_issue17_reopen_after_yard_switch_clears_stale_label_text(
    ui_manager, design_catalog_mock, design_loader_mock, empire, hex_a, mock_registries,
):
    """Issue #17 (row content path): close+reopen after a yard switch
    with items must leave NO stale label text on pool rows beyond
    ``data_source.get_row_count()``.

    pygame_gui's ``UIPanel.show(show_contents=True)`` -> ``UIContainer.show(True)``
    contract recursively un-hides every child element regardless of
    individual visible state (verified against pygame-ce 2.5.7). Therefore
    ``update_visible_rows()`` calling ``row["bg"].hide()`` on surplus rows
    is insufficient — the next ``panels.background.show()`` re-exposes
    them. ``invalidate_widget_caches`` must blank widget content too.
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    planet = _planet_with_two_yards("Twin-Yard", 301, hex_a)
    galaxy = _MockGalaxy()
    galaxy._global_hex_planets[hex_a] = [planet]
    session = _MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)

    screen = BuildQueueScreen(
        ui_manager,
        facade=session,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy,
        empire=empire,
        initial_yard=planet,
    )

    # Populate the planet's queue with synthetic items, simulate selector
    # picking the second source if available, and refresh so the row
    # pool's label widgets carry real text.
    if len(screen.queue_sources) >= 2:
        screen._input_router._on_queue_selection_changed(screen.queue_sources[1], {1})
    target_queue = screen._input_router._get_active_queue()
    target_queue.extend([
        {"design_id": f"qs_organics_complex", "name": "QS Organics Complex",
         "type": "complex", "turns_remaining": 4.0, "remaining_cost": {}}
        for _ in range(3)
    ])
    screen._input_router._refresh_queue_display()

    # Sanity: pool's first row(s) should carry the queue item's design id
    # in some label cell (the item-name column renders "<id> (<category>)").
    pool = screen.panels.virtual_table._row_pool
    pre_close_label_texts = []
    for row in pool[:3]:
        for w in row.get("widgets", []):
            if w.get("type") == "label":
                pre_close_label_texts.append(w["el"].text)
    assert any("organics" in t for t in pre_close_label_texts), (
        "test setup: expected at least one row to carry the queue item's "
        "design id before close; pool labels were: "
        + repr(pre_close_label_texts)
    )

    # Close — panels survive (PROJ-376). Widget text content remains.
    screen._input_router._request_close()

    # Empty the underlying queue (simulating the user opening a different
    # source whose queue is empty) then re-open on the same planet.
    del target_queue[:]
    screen.open_for_yard(planet, hex_coord=hex_a)

    # After re-open, the data source has no rows for surplus pool entries.
    # Every label widget on a pool row whose ``data_idx >= row_count`` must
    # not carry stale design-name text. The pygame_gui UIPanel.show
    # recursive un-hide will re-expose any stale text otherwise.
    row_count = screen.panels.virtual_table._data_source.get_row_count()
    stale_rows = []
    for pool_idx, row in enumerate(pool):
        data_idx = row.get("row_index", -1)
        if data_idx >= row_count or data_idx < 0:
            for w in row.get("widgets", []):
                if w.get("type") == "label":
                    text = w["el"].text or ""
                    if "organics" in text or "complex" in text:
                        stale_rows.append((pool_idx, data_idx, text))

    assert stale_rows == [], (
        f"Issue #17: out-of-range pool rows must not retain stale label "
        f"text after re-open. Found stale labels: {stale_rows!r}. The fix "
        f"must call set_text(\"\") on every label widget in "
        f"VirtualTable.invalidate_widget_caches() to defeat pygame_gui's "
        f"UIPanel.show(show_contents=True) recursive un-hide."
    )


# =========================================================================
# Issue #17 follow-up (rejected fix) regression tests
# =========================================================================
#
# After the first issue #17 fix (commit a3ced0e1f), QA reported in session
# 20260512_103437 that on a brand-new game with an empty Build Queue,
# opening the panel still shows ~40 phantom empty rows — each with
# +/-/^/v action buttons and a blank portrait slot. The first fix cleared
# label text and image surfaces but left the row pool widgets (action
# buttons, portrait UIImage) visible.
#
# Root cause (deeper layer): when an empty queue is bound via
# update_visible_rows(), the surplus pool rows ARE hidden via
# row["bg"].hide(). But BuildQueueScreen.open_for_yard() then calls
# self.show() which invokes panels.background.show() — pygame_gui's
# UIPanel.show(show_contents=True) recursively un-hides every descendant
# (verified against pygame-ce 2.5.7 source: ui_panel.py:468-476,
# ui_container.py:380-394). So the pool rows that update_visible_rows()
# just hid are immediately re-exposed.
#
# Fix has two parts:
# 1) invalidate_widget_caches() also hides each row["bg"] (covered by
#    test_virtual_table.py::test_invalidate_hides_row_backgrounds).
# 2) BuildQueueScreen.show() re-runs force_update() + update_visible_rows()
#    after panels.background.show() so the per-row visibility is re-asserted
#    AFTER pygame_gui's recursive un-hide (this test class).
# =========================================================================


def test_issue17_show_reasserts_row_visibility_after_panel_show(
    ui_manager, design_catalog_mock, design_loader_mock, empire, hex_a, mock_registries,
):
    """Issue #17 follow-up: ``BuildQueueScreen.show()`` must re-run the
    virtual table's visibility pass AFTER ``panels.background.show()``
    so out-of-range pool rows stay hidden.

    The scenario: empty queue, ``_refresh_queue_display()`` runs
    ``update_visible_rows()`` which hides every surplus row (data_idx >=
    row_count). Then ``show()`` invokes ``panels.background.show()``
    which is pygame_gui's ``UIPanel.show(show_contents=True)`` and
    recursively un-hides every descendant. Without the override, the
    just-hidden row backgrounds + their action buttons / image / label
    children are all re-exposed.

    FAILS today (pre-override): at least one out-of-range row_bg has
    ``visible == 1`` after show().
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    planet = _planet_with_two_yards("Twin-Yard", 17_001, hex_a)
    galaxy = _MockGalaxy()
    galaxy._global_hex_planets[hex_a] = [planet]
    session = _MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)

    screen = BuildQueueScreen(
        ui_manager,
        facade=session,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy,
        empire=empire,
        initial_yard=planet,
    )

    # Empty queue (default state — planet has yards but no items queued).
    assert screen._input_router._get_active_queue() == [], (
        "test setup: expected empty queue on a brand-new planet"
    )

    pool = screen.panels.virtual_table._row_pool
    row_count = screen.panels.virtual_table._data_source.get_row_count()
    assert row_count == 0, "test setup: expected zero queue items"
    assert len(pool) > 0, "test setup: expected a non-empty row pool"

    # Simulate the close-then-reopen path: hide + invalidate caches +
    # refresh + show, mirroring open_for_yard()'s flow.
    screen.hide()
    screen.panels.virtual_table.invalidate_widget_caches()
    screen._input_router._refresh_queue_display()
    screen.show()

    # After show(): every pool row whose data_idx >= row_count (== 0)
    # must have row_bg.visible falsy. pygame_gui sets `visible` to int
    # 0 or 1 (sometimes bool); compare via bool().
    visible_phantom_rows = []
    for pool_idx, row in enumerate(pool):
        data_idx = row.get("row_index", -1)
        if data_idx >= row_count or data_idx < 0:
            bg = row.get("bg")
            if bg is not None and bool(getattr(bg, "visible", 0)):
                visible_phantom_rows.append((pool_idx, data_idx))

    assert visible_phantom_rows == [], (
        f"Issue #17 follow-up: BuildQueueScreen.show() must re-run "
        f"the virtual table's visibility pass after pygame_gui's "
        f"UIPanel.show(show_contents=True) recursive un-hide. "
        f"Found {len(visible_phantom_rows)} phantom rows visible "
        f"after show() on an empty queue: {visible_phantom_rows!r}. "
        f"Fix: override BuildQueueScreen.show() to invoke "
        f"force_update() + update_visible_rows() after the existing "
        f"panels.background.show() call."
    )


def test_issue17_show_reasserts_child_widget_visibility_after_panel_show(
    ui_manager, design_catalog_mock, design_loader_mock, empire, hex_a, mock_registries,
):
    """Issue #17 follow-up: the child widgets inside hidden rows
    (action buttons, image, label) must also be hidden after
    ``BuildQueueScreen.show()`` returns.

    Why this is a separate assertion from the row_bg test: the QA
    rejection screenshot specifically called out the visible
    ``+ – ^ v`` action buttons and blank portrait slot — these are the
    children of row_bg. Hiding row_bg via
    ``UIPanel.hide(hide_contents=True)`` recursively hides them, so
    asserting at the child level pins the symptom from the QA report
    directly.

    FAILS today (pre-fix): action buttons on out-of-range rows have
    ``visible == 1``.
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen

    planet = _planet_with_two_yards("Twin-Yard", 17_002, hex_a)
    galaxy = _MockGalaxy()
    galaxy._global_hex_planets[hex_a] = [planet]
    session = _MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)

    screen = BuildQueueScreen(
        ui_manager,
        facade=session,
        theme_id_supplier=lambda: "Federation",
        on_close_callback=MagicMock(),
        design_catalog=design_catalog_mock,
        design_loader=design_loader_mock,
        hex_coord=hex_a,
        galaxy=galaxy,
        empire=empire,
        initial_yard=planet,
    )

    pool = screen.panels.virtual_table._row_pool
    row_count = screen.panels.virtual_table._data_source.get_row_count()
    assert row_count == 0

    # Close, invalidate, refresh, reopen — exercising the full reopen path.
    screen._input_router._request_close()
    screen.open_for_yard(planet, hex_coord=hex_a)

    visible_child_widgets = []
    for pool_idx, row in enumerate(pool):
        data_idx = row.get("row_index", -1)
        if data_idx >= row_count or data_idx < 0:
            for w in row.get("widgets", []):
                wtype = w.get("type")
                if wtype == "actions":
                    for action, btn in w.get("actions_dict", {}).items():
                        if bool(getattr(btn, "visible", 0)):
                            visible_child_widgets.append(
                                (pool_idx, wtype, action)
                            )
                elif wtype in ("image", "label"):
                    el = w.get("el")
                    if el is not None and bool(getattr(el, "visible", 0)):
                        visible_child_widgets.append(
                            (pool_idx, wtype, None)
                        )

    assert visible_child_widgets == [], (
        f"Issue #17 follow-up: after close + open_for_yard on an empty "
        f"queue, out-of-range pool rows' child widgets (+/-/^/v buttons, "
        f"portrait image, label) must all be hidden. The QA rejection "
        f"screenshot (2026-05-12 10:35) flagged exactly these widgets as "
        f"visible: action buttons and a blank portrait slot. "
        f"Visible widgets after reopen: {visible_child_widgets!r}."
    )
