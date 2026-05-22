"""
Tests for BuildQueueScreen queue selector panel (PROJ-69 Phase 3).

Tests cover:
- Queue selector panel creation and visibility
- Single-click queue selection
- Ctrl+click multi-select toggle
- Queue display updates when switching queues
- Multi-select message display
"""

import pytest
from unittest.mock import MagicMock
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.build_queue_source import BuildQueueSource
from game.strategy.facade.dto import BuildQueueSourceDTO
from game.core.validation import ValidationResult
from game.strategy.systems.design_repository import DesignLoadResult


class MockGalaxy:
    """Minimal mock Galaxy for BuildQueueScreen tests."""
    def __init__(self):
        self.systems = {}
        self._global_hex_planets = {}  # HexCoord -> List[Planet]
        self.fleets_by_id = {}

    def get_planets_at_global_hex(self, hex_coord):
        """Return planets at a given global hex coordinate."""
        return self._global_hex_planets.get(hex_coord, [])

    def get_fleets_at(self, hex_coord):
        """Return fleets at a given global hex coordinate."""
        return []


class MockSession:
    def __init__(self, galaxy=None, empire=None, registries=None):
        self.savegame_path = "test_savegame"
        self.current_empire = empire or Empire(1, "Test Empire", (255, 0, 0))
        self.galaxy = galaxy or MockGalaxy()
        # PROJ-211: Add registries for DI
        self.registries = registries

    def get_registries(self):
        """PROJ-382 Phase 1: facade-shaped registries accessor."""
        return self.registries

    def get_colony_demographic_view(self, planet_id):
        """PROJ-382 Phase 1: facade-shaped demographic view stub for tests."""
        return None

    def get_turn_number(self) -> int:
        """PROJ-396 MAJ-003: facade-shaped turn-number accessor."""
        return 0

    def get_save_path(self):
        """PROJ-396 MAJ-004: facade-shaped save-path accessor."""
        return self.savegame_path

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

    # PROJ-472 Phase 1B: expose ``empires.hex_build_queues`` so BuildQueueScreen
    # resolves build-queue *DTOs* off the mock, mirroring
    # ``FacadeEmpireQueries.hex_build_queues`` (projects domain sources through
    # ``BuildQueueSourceDTO.from_domain``).
    @property
    def empires(self):
        from game.strategy.data.build_queue_source import collect_build_queues_at_hex
        from game.strategy.facade.dto import BuildQueueSourceDTO

        class _EmpiresNS:
            def __init__(self, parent):
                self._parent = parent
            def hex_build_queues(self, empire_id, hex_coord):
                sources = collect_build_queues_at_hex(
                    hex_coord,
                    self._parent.galaxy,
                    self._parent.current_empire,
                    registries=self._parent.get_registries(),
                )
                return [BuildQueueSourceDTO.from_domain(s) for s in sources]
        return _EmpiresNS(self)

    def handle_command(self, cmd):
        return ValidationResult()


@pytest.fixture
def mock_design_catalog():
    mock_instance = MagicMock()
    design = MagicMock()
    design.design_id = "mining_complex_mk1"
    design.name = "Mining Complex"
    design.vehicle_type = "Planetary Complex"
    mock_instance.scan_designs.return_value = [design]
    mock_instance.designs_folder = "test_designs"
    mock_instance.load_design_data.return_value = DesignLoadResult.not_found("test")
    return mock_instance


@pytest.fixture
def mock_design_loader():
    return MagicMock()


@pytest.fixture
def build_queue_screen(ui_manager, mock_design_catalog, mock_design_loader, mock_registries):
    """Create BuildQueueScreen for testing queue selector."""
    manager = ui_manager

    hex_coord = HexCoord(5, 5)
    planet = Planet(
        name="Test Colony",
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
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = 1
    planet.id = 100
    # Add PlanetaryYard facility so base queue source is created
    from game.strategy.data.planetary_facility import PlanetaryFacility
    yard = PlanetaryFacility(
        instance_id="yard_test", design_id="colony_hub", name="Colony Hub",
        design_data={"layers": {"CORE": [{"id": "hub", "abilities": {"PlanetaryYard": True}}]}},
    )
    planet.facilities = [yard]

    empire = Empire(1, "Test Empire", (255, 0, 0))
    galaxy = MockGalaxy()
    galaxy._global_hex_planets[hex_coord] = [planet]

    # PROJ-211: Pass registries for DI
    session = MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)
    on_close = MagicMock()

    from game.ui.screens.build_queue_screen import BuildQueueScreen
    bq_screen = BuildQueueScreen(
        manager,
        initial_yard=planet,
        on_close_callback=on_close,
        design_catalog=mock_design_catalog,
        design_loader=mock_design_loader,
        hex_coord=hex_coord,
        world=galaxy,  # PROJ-477 Phase 4
        empire=empire,
        facade=session,
        theme_id_supplier=lambda: "Federation",
    )

    manager.update(0.1)
    yield bq_screen


# --- Panel existence tests ---

def test_queue_selector_panel_exists(build_queue_screen):
    """Test that queue selector panel is created."""
    assert build_queue_screen._queue_selector is not None
    assert build_queue_screen._queue_selector.panel is not None


def test_queue_selector_scrollable_exists(build_queue_screen):
    """Test that queue selector scrollable container is created."""
    assert build_queue_screen._queue_selector is not None
    assert build_queue_screen._queue_selector.scrollable is not None


def test_queue_selector_buttons_exist(build_queue_screen):
    """Test that queue selector buttons are created for each queue source."""
    assert build_queue_screen._queue_selector is not None
    assert len(build_queue_screen._queue_selector.buttons) == len(build_queue_screen.queue_sources)


# --- Queue source initialization tests ---

def test_single_build_context_creates_one_queue_source(build_queue_screen):
    """Test that a single planet at hex creates one queue source DTO.

    PROJ-472 Phase 1B: the screen consumes immutable ``BuildQueueSourceDTO``
    projections, not live domain ``BuildQueueSource`` objects.
    """
    assert len(build_queue_screen.queue_sources) == 1
    source = build_queue_screen.queue_sources[0]
    assert isinstance(source, BuildQueueSourceDTO)
    assert source.context_type == "planet"
    assert source.can_build_complexes is True


def test_queue_source_holds_detached_queue_snapshot(build_queue_screen):
    """The DTO holds a *detached copy* of the queue, never the live list.

    PROJ-472 Phase 1B: ``BuildQueueSourceDTO`` is frozen and deep-copies the
    construction queue so the UI cannot mutate the domain entity. The snapshot
    must be value-equal to the domain queue but a distinct object.
    """
    source = build_queue_screen.queue_sources[0]
    domain_queue = build_queue_screen.build_context.construction_queue
    assert source.construction_queue is not domain_queue
    assert source.construction_queue == list(domain_queue)


def test_default_selection_is_first_queue(build_queue_screen):
    """Test that the first queue is selected by default."""
    assert 0 in build_queue_screen.selected_queue_indices
    assert build_queue_screen.active_queue_source is build_queue_screen.queue_sources[0]


# --- Queue selection tests ---

def test_on_queue_selected_updates_active_source(build_queue_screen):
    """Test that queue selection updates the active queue source."""
    # With single source, selecting index 0 should still work
    # PROJ-86: Use selector's internal method via screen's callback
    build_queue_screen._queue_selector._on_queue_selected(0)
    assert build_queue_screen.active_queue_source is build_queue_screen.queue_sources[0]
    assert build_queue_screen.selected_queue_indices == {0}


def test_on_queue_toggled_prevents_empty_selection(build_queue_screen):
    """Test that toggling off the only selected queue falls back to index 0."""
    # PROJ-86: Use selector's internal method via screen's callback
    build_queue_screen._queue_selector._on_queue_toggled(0)
    # Should not allow empty selection - falls back to {0}
    assert len(build_queue_screen.selected_queue_indices) > 0
    assert 0 in build_queue_screen.selected_queue_indices


# --- Multi-source tests (simulated) ---

def test_multiple_queue_sources_create_buttons(ui_manager):
    """Test that multiple queue sources create multiple selector buttons."""
    manager = ui_manager

    hex_coord = HexCoord(5, 5)
    planet = Planet(
        name="Test Colony",
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
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = 1
    planet.id = 100

    # Add PlanetaryYard facility so the base construction queue source is created
    yard = PlanetaryFacility(
        instance_id="yard_test", design_id="colony_hub", name="Colony Hub",
        design_data={"layers": {"CORE": [{"id": "hub", "abilities": {"PlanetaryYard": True}}]}},
    )
    planet.facilities.append(yard)

    # Add a shipyard facility so there are 2 queue sources
    shipyard = PlanetaryFacility(
        instance_id="shipyard-1",
        design_id="space_shipyard_complex",
        name="Space Shipyard",
        design_data={"layers": {"OUTER": [{"id": "space_shipyard", "modifiers": []}]}},
        is_operational=True
    )
    planet.facilities.append(shipyard)

    empire = Empire(1, "Test Empire", (255, 0, 0))
    galaxy = MockGalaxy()
    galaxy._global_hex_planets[hex_coord] = [planet]

    session = MockSession(galaxy=galaxy, empire=empire)

    mock_lib = MagicMock()
    mock_lib.scan_designs.return_value = []
    mock_lib.designs_folder = "test"
    mock_lib.load_design_data.return_value = DesignLoadResult.not_found("test")

    from game.ui.screens.build_queue_screen import BuildQueueScreen
    bq = BuildQueueScreen(
        manager,
        on_close_callback=lambda: None,
        initial_yard=planet,
        design_catalog=mock_lib, design_loader=MagicMock(),
        hex_coord=hex_coord,
        world=galaxy,  # PROJ-477 Phase 4
        empire=empire,
        facade=session,
        theme_id_supplier=lambda: "Federation",
    )

    # Should have 2 sources: planet base queue + shipyard facility queue
    assert len(bq.queue_sources) == 2
    assert len(bq._queue_selector.buttons) == 2


def test_multi_select_sets_active_to_none(ui_manager):
    """Test that selecting multiple queues sets active_queue_source to None."""
    manager = ui_manager

    hex_coord = HexCoord(5, 5)
    planet = Planet(
        name="Test Colony",
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
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = 1
    planet.id = 100
    from game.strategy.data.planetary_facility import PlanetaryFacility
    planet.facilities = [PlanetaryFacility(
        instance_id="yard_multi", design_id="hub", name="Hub",
        design_data={"layers": {"CORE": [{"id": "h", "abilities": {"PlanetaryYard": True}}]}},
    )]

    empire = Empire(1, "Test Empire", (255, 0, 0))
    galaxy = MockGalaxy()
    galaxy._global_hex_planets[hex_coord] = [planet]

    session = MockSession(galaxy=galaxy, empire=empire)

    mock_lib = MagicMock()
    mock_lib.scan_designs.return_value = []
    mock_lib.designs_folder = "test"
    mock_lib.load_design_data.return_value = DesignLoadResult.not_found("test")

    from game.ui.screens.build_queue_screen import BuildQueueScreen
    bq = BuildQueueScreen(
        manager,
        on_close_callback=lambda: None,
        initial_yard=planet,
        design_catalog=mock_lib, design_loader=MagicMock(),
        hex_coord=hex_coord,
        world=galaxy,  # PROJ-477 Phase 4
        empire=empire,
        facade=session,
        theme_id_supplier=lambda: "Federation",
    )

    # Manually add a second queue source to test multi-select behavior
    second_source = BuildQueueSource(
        queue_id="test_second",
        display_name="Test Second Queue",
        owner_entity=planet,
        construction_queue=[],
        can_build_ships=True,
        can_build_complexes=True,
        context_type="planet"
    )
    bq.queue_sources.append(second_source)
    bq._input_router._refresh_queue_selector()

    # Select both queues
    bq._queue_selector.selected_indices = {0}
    bq._queue_selector._on_queue_toggled(1)

    assert len(bq.selected_queue_indices) == 2
    assert bq.active_queue_source is None

    # Go back to single select
    bq._queue_selector._on_queue_selected(0)
    assert len(bq.selected_queue_indices) == 1
    assert bq.active_queue_source is bq.queue_sources[0]


def test_queue_display_shows_active_source_items(ui_manager):
    """Test that queue display shows items from the active queue source."""
    manager = ui_manager

    hex_coord = HexCoord(5, 5)
    planet = Planet(
        name="Test Colony",
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
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = 1
    planet.id = 100
    from game.strategy.data.planetary_facility import PlanetaryFacility
    planet.facilities = [PlanetaryFacility(
        instance_id="yard_disp", design_id="hub", name="Hub",
        design_data={"layers": {"CORE": [{"id": "h", "abilities": {"PlanetaryYard": True}}]}},
    )]

    empire = Empire(1, "Test Empire", (255, 0, 0))
    galaxy = MockGalaxy()
    galaxy._global_hex_planets[hex_coord] = [planet]

    session = MockSession(galaxy=galaxy, empire=empire)

    mock_lib = MagicMock()
    mock_lib.scan_designs.return_value = []
    mock_lib.designs_folder = "test"
    mock_lib.load_design_data.return_value = DesignLoadResult.not_found("test")

    from game.ui.screens.build_queue_screen import BuildQueueScreen
    bq = BuildQueueScreen(
        manager,
        on_close_callback=lambda: None,
        initial_yard=planet,
        design_catalog=mock_lib, design_loader=MagicMock(),
        hex_coord=hex_coord,
        world=galaxy,  # PROJ-477 Phase 4
        empire=empire,
        facade=session,
        theme_id_supplier=lambda: "Federation",
    )

    # PROJ-472 Phase 1B: the active queue source is an immutable DTO snapshot.
    # Mutate the *domain* base queue (what a command would do), re-project from
    # the facade, then refresh so the display reflects the new item.
    planet.construction_queue.append({
        "design_id": "test_item", "type": "complex", "turns_remaining": 3
    })
    bq._input_router._resync_sources_from_facade()
    bq._input_router._refresh_queue_display()

    # PROJ-221: VirtualTable manages queue display - verify data source has correct count
    assert bq.panels.data_source.get_row_count() == 1


def test_queue_selector_has_queue_source_index_tags(build_queue_screen):
    """Test that queue selector buttons have index mappings."""
    selector = build_queue_screen._queue_selector
    for idx, btn in enumerate(selector.buttons):
        assert btn in selector._button_index_map
        assert selector._button_index_map[btn] == idx
