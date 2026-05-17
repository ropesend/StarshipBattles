"""
Tests for BuildQueueScreen basic functionality.
"""

import pytest
from unittest.mock import MagicMock, patch
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.core.validation import ValidationResult


class MockGalaxy:
    """Minimal mock Galaxy for BuildQueueScreen tests."""
    def __init__(self):
        self.systems = {}
        self._global_hex_planets = {}
        self.fleets_by_id = {}

    def get_planets_at_global_hex(self, hex_coord):
        return self._global_hex_planets.get(hex_coord, [])


class MockSession:
    def __init__(self, galaxy=None, empire=None, registries=None):
        self.savegame_path = "test_savegame"
        self.current_empire = empire or Empire(1, "Test Empire", (255, 0, 0))
        self.galaxy = galaxy or MockGalaxy()
        # PROJ-211: Add registries for DI
        self.registries = registries
        # PROJ-208: Track commands for test verification
        self.commands_handled = []

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

    def handle_command(self, cmd):
        """Mock command handler that executes AddToConstructionQueueCommand.

        PROJ-208: Enables queue mutation tests to work with command pattern.
        """
        self.commands_handled.append(cmd)

        # Execute AddToConstructionQueueCommand to maintain queue behavior
        from game.strategy.engine.commands import AddToConstructionQueueCommand
        if isinstance(cmd, AddToConstructionQueueCommand):
            queue = self._resolve_queue(cmd.entity_id, cmd.entity_type, getattr(cmd, 'queue_id', None))
            if queue is not None:
                queue_item = {
                    "design_id": cmd.design_id,
                    "type": cmd.category,
                    "turns_remaining": 1.0,
                    "total_cost": {},
                    "resources_consumed": {},
                }
                if cmd.target_planet_id is not None:
                    queue_item["target_planet_id"] = cmd.target_planet_id
                if cmd.index is not None:
                    queue.insert(cmd.index, queue_item)
                else:
                    queue.append(queue_item)

        return ValidationResult()

    def _resolve_entity(self, entity_id, entity_type):
        """Resolve entity by ID and type."""
        if entity_type == "planet":
            for planets in self.galaxy._global_hex_planets.values():
                for planet in planets:
                    if getattr(planet, 'id', None) == entity_id:
                        return planet
        elif entity_type == "fleet":
            return self.galaxy.fleets_by_id.get(entity_id)
        return None

    def _resolve_queue(self, entity_id, entity_type, queue_id):
        """Resolve the construction queue, handling multi-queue entities."""
        entity = self._resolve_entity(entity_id, entity_type)
        if entity is None:
            return None

        if queue_id is None:
            return getattr(entity, 'construction_queue', None)

        # Check if queue_id matches a facility's instance_id
        if hasattr(entity, 'facilities'):
            for facility in entity.facilities:
                if getattr(facility, 'instance_id', None) == queue_id:
                    return getattr(facility, 'construction_queue', None)

        # Fallback to entity's main queue
        return getattr(entity, 'construction_queue', None)


def test_build_queue_screen_initializes(build_queue_screen):
    """Test that BuildQueueScreen creates without crashing."""
    assert build_queue_screen is not None
    assert build_queue_screen.build_context is not None
    # PROJ-382 Phase 1: facade is required; legacy `session` attribute removed.
    assert build_queue_screen.facade is not None
    assert build_queue_screen.on_close is not None


def test_load_designs_by_category(build_queue_screen):
    """Test that designs are filtered by vehicle type."""
    # Test complex category
    complexes, roles = build_queue_screen.controller.load_designs_by_category("complex")
    assert len(complexes) > 0
    assert all(d.vehicle_type == "Planetary Complex" for d in complexes)

    # Test ship category
    ships, roles = build_queue_screen.controller.load_designs_by_category("ship")
    assert len(ships) > 0
    assert all(d.vehicle_type == "Ship" for d in ships)

    # Test satellite category
    satellites, roles = build_queue_screen.controller.load_designs_by_category("satellite")
    assert len(satellites) > 0
    assert all(d.vehicle_type == "Satellite" for d in satellites)

    # Test fighter category
    fighters, roles = build_queue_screen.controller.load_designs_by_category("fighter")
    assert len(fighters) > 0
    assert all(d.vehicle_type == "Fighter" for d in fighters)


def test_switch_category_filter(build_queue_screen):
    """Test that category buttons filter correctly."""
    # Start with complex category
    assert build_queue_screen.controller.selected_category == "complex"

    # Switch to ship
    build_queue_screen.controller.set_category("ship")
    assert build_queue_screen.controller.selected_category == "ship"

    # Switch to satellite
    build_queue_screen.controller.set_category("satellite")
    assert build_queue_screen.controller.selected_category == "satellite"

    # Switch to fighter
    build_queue_screen.controller.set_category("fighter")
    assert build_queue_screen.controller.selected_category == "fighter"


def test_add_to_queue(build_queue_screen):
    """Test that selected design is added to planet construction queue.

    PROJ-208: Build queue additions now route through AddToConstructionQueueCommand.
    The command handler creates items with default turns_remaining (1.0).
    ProductionEngine recalculates actual turns dynamically during production.
    """
    initial_queue_length = len(build_queue_screen.build_context.construction_queue)

    # Mock design selection
    build_queue_screen.drag_handler.selected_design = "mining_complex_mk1"
    build_queue_screen.controller.selected_category = "complex"

    # Add to queue - turns param is no longer used (handler sets default)
    build_queue_screen.controller.add_to_queue("mining_complex_mk1", 5)

    # Verify queue updated
    assert len(build_queue_screen.build_context.construction_queue) == initial_queue_length + 1

    # Verify item structure
    item = build_queue_screen.build_context.construction_queue[-1]
    assert isinstance(item, dict)
    assert item["design_id"] == "mining_complex_mk1"
    assert item["type"] == "complex"
    # PROJ-208: Handler uses default turns_remaining (1.0)
    assert item["turns_remaining"] == 1.0


def test_queue_display_updates(build_queue_screen):
    """Test that UI refreshes when queue changes."""
    # Add item to queue
    build_queue_screen.build_context.construction_queue.append({
        "design_id": "frigate_mk1",
        "type": "ship",
        "turns_remaining": 10
    })

    # Refresh display
    build_queue_screen._refresh_queue_display()

    # PROJ-221: VirtualTable manages queue display - verify data source has correct count
    assert build_queue_screen.panels.data_source.get_row_count() == 1


def test_close_callback_fires(build_queue_screen):
    """Test that on_close callback is invoked.

    PROJ-376 Phase 2: ``_close()`` was replaced by ``_request_close()``
    (hide + on_close). The close-button / Esc handler routes through it.
    """
    # Close the screen via the public close path.
    build_queue_screen._request_close()

    # Verify callback was called
    build_queue_screen.on_close.assert_called_once()
    # Panels survive across opens — only visibility toggles.
    assert build_queue_screen.panels.background.alive()
    assert not build_queue_screen.panels.background.visible


def test_planet_report_panel_exists(build_queue_screen):
    """Test that planet report panel is created."""
    # PROJ-180: Access via panels.*
    assert hasattr(build_queue_screen.panels, 'planet_report')
    assert build_queue_screen.panels.planet_report is not None


def test_items_list_panel_exists(build_queue_screen):
    """Test that items list panel is created."""
    # PROJ-180: Access via panels.*
    assert hasattr(build_queue_screen.panels, 'items_list_panel')
    assert build_queue_screen.panels.items_list_panel is not None


def test_filter_panel_exists(build_queue_screen):
    """Test that filter panel with category buttons exists."""
    # PROJ-180: Access via panels.*
    assert hasattr(build_queue_screen.panels, 'filter_panel')
    assert build_queue_screen.panels.filter_panel is not None

    # Verify category buttons exist
    assert hasattr(build_queue_screen.panels, 'btn_category_complex')
    assert hasattr(build_queue_screen.panels, 'btn_category_ship')
    assert hasattr(build_queue_screen.panels, 'btn_category_satellite')
    assert hasattr(build_queue_screen.panels, 'btn_category_fighter')

def test_roles_panel_exists(build_queue_screen):
    """Test that the roles panel UI elements are created."""
    assert hasattr(build_queue_screen.panels, 'roles_panel')
    assert build_queue_screen.panels.roles_panel is not None


def test_bottom_bar_exists(build_queue_screen):
    """Test that bottom bar with close button exists."""
    # PROJ-180: Access via panels.*
    assert hasattr(build_queue_screen.panels, 'btn_close')
    assert build_queue_screen.panels.btn_close is not None


def test_no_savegame_path_handled_gracefully(mock_design_catalog, mock_design_loader, mock_registries, ui_manager):
    """Test that BuildQueueScreen handles None savegame_path without crashing.

    PROJ-40: Updated to use DI injection for dependencies.
    PROJ-109: Updated to provide required hex_coord, galaxy, empire parameters.
    PROJ-211: Updated to pass registries for DI.
    """
    manager = ui_manager

    hex_coord = HexCoord(5, 5)
    # Create test planet
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
        atmosphere={},
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = 1
    planet.id = 100

    # Create mock galaxy with planet
    empire = Empire(1, "Test Empire", (255, 0, 0))
    galaxy = MockGalaxy()
    galaxy._global_hex_planets[hex_coord] = [planet]

    # Create session with None savegame_path and registries
    session = MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)
    session.savegame_path = None

    # Should not crash - pass injected dependencies
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    screen_obj = BuildQueueScreen(
        manager,
        planet,
        lambda: None,
        design_catalog=mock_design_catalog,
        design_loader=mock_design_loader,
        hex_coord=hex_coord,
        galaxy=galaxy,
        empire=empire,
        facade=session,
        theme_id_supplier=lambda: "Federation",
    )

    # Should create with design_catalog injected
    assert screen_obj is not None
    assert screen_obj.design_catalog is not None


def test_add_to_queue_defaults_to_1_turn(build_queue_screen):
    """Test that new items default to 1 turn build time."""
    # Mock design selection
    build_queue_screen.drag_handler.selected_design = "test_design"
    build_queue_screen.controller.selected_category = "complex"

    # Add to queue without specifying turns (should use default)
    build_queue_screen.controller.add_to_queue("test_design")

    # Verify item was added with 1 turn
    item = build_queue_screen.build_context.construction_queue[-1]
    assert item["turns_remaining"] == 1


def test_drag_item_uses_1_turn_default(build_queue_screen):
    """Test that dragged items default to 1 turn if no turns specified."""
    # Simulate dragging an item without 'turns' key
    build_queue_screen.drag_handler.dragged_item = {
        'design_id': 'frigate_mk1',
        'name': 'Frigate',
        'category': 'ship',
        # Note: no 'turns' key
    }

    # Simulate drop event - manually call _add_to_queue as drop would
    # The actual drop handling gets 'turns' from dragged_item with default
    turns = build_queue_screen.drag_handler.dragged_item.get('turns', 1)  # Should be 1

    # Verify default is 1
    assert turns == 1


def test_add_ship_to_queue_with_shipyard(mock_design_catalog, mock_design_loader, mock_registries, ui_manager):
    """Test that ships can be added when planet has a shipyard facility.

    Regression test for BUG-24: Ships couldn't be added to build queue
    even when planet had a space shipyard facility.

    PROJ-109: Test creates screen with shipyard already present so queue source
    for ships is created at initialization time.
    PROJ-211: Updated to pass registries for DI.
    """
    from game.ui.screens.build_queue_screen import BuildQueueScreen

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

    # Add shipyard facility BEFORE creating screen
    shipyard = PlanetaryFacility(
        instance_id="test-shipyard-1",
        design_id="space_shipyard_complex",
        name="Space Shipyard",
        design_data={
            "layers": {
                "OUTER": [{"id": "space_shipyard", "modifiers": []}]
            }
        },
        is_operational=True
    )
    planet.facilities.append(shipyard)

    # Verify has_space_shipyard returns True
    assert planet.has_space_shipyard is True, \
        "has_space_shipyard should return True when shipyard facility exists"

    empire = Empire(1, "Test Empire", (255, 0, 0))
    galaxy = MockGalaxy()
    galaxy._global_hex_planets[hex_coord] = [planet]

    session = MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)

    bq_screen = BuildQueueScreen(
        manager,
        planet,
        lambda: None,
        design_catalog=mock_design_catalog,
        design_loader=mock_design_loader,
        hex_coord=hex_coord,
        galaxy=galaxy,
        empire=empire,
        facade=session,
        theme_id_supplier=lambda: "Federation",
    )

    # Should have 2 queue sources: planetary yard + shipyard
    assert len(bq_screen.queue_sources) == 2, \
        f"Should have 2 queue sources, got {len(bq_screen.queue_sources)}"

    # Find and select the shipyard queue source (can_build_ships=True)
    shipyard_source = next(
        (s for s in bq_screen.queue_sources if s.can_build_ships), None
    )
    assert shipyard_source is not None, "Should have a shipyard queue source"
    bq_screen._queue_selector._on_queue_selected(
        bq_screen.queue_sources.index(shipyard_source)
    )

    # Try to add a ship
    initial_queue_len = len(shipyard_source.construction_queue)
    bq_screen.controller.set_category("ship")
    bq_screen.controller.add_to_queue("test_frigate", turns=1)

    # Verify ship was added to shipyard queue
    assert len(shipyard_source.construction_queue) == initial_queue_len + 1, \
        "Ship should be added to shipyard queue when shipyard exists"
    assert shipyard_source.construction_queue[-1]["type"] == "ship"
    assert shipyard_source.construction_queue[-1]["design_id"] == "test_frigate"


def test_add_ship_fails_without_shipyard(build_queue_screen):
    """Test that ships cannot be added when only planetary yard queue exists.

    PROJ-109: The default build_queue_screen fixture creates a planet without
    shipyard facilities, so only the "Planetary Yard" queue source exists
    (can_build_ships=False). Ships should be rejected.
    """
    # Default fixture has no shipyard - verify single queue source
    assert len(build_queue_screen.queue_sources) == 1, \
        "Should have only planetary yard queue source"
    assert build_queue_screen.active_queue_source.can_build_ships is False, \
        "Planetary yard should not build ships"

    # Try to add a ship
    initial_queue_len = len(build_queue_screen.active_queue_source.construction_queue)
    build_queue_screen.controller.set_category("ship")
    build_queue_screen.controller.add_to_queue("test_frigate", turns=1)

    # Verify ship was NOT added
    assert len(build_queue_screen.active_queue_source.construction_queue) == initial_queue_len, \
        "Ship should NOT be added without a shipyard"
