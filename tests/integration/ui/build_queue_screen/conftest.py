"""
Shared fixtures for BuildQueueScreen tests.
"""

import pytest
from unittest.mock import MagicMock
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
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


class MockSession:
    """Mock that doubles as both a session and a facade for BuildQueueScreen
    integration tests. PROJ-382 Phase 1: BuildQueueScreen no longer accepts
    ``session=``; the same instance is now passed as ``facade=`` (for
    command dispatch + ``get_registries()``).
    PROJ-396 MAJ-002: ``portrait_session=`` retired in favor of a narrow
    ``theme_id_supplier=`` callable; tests pass ``lambda: "Federation"``."""

    def __init__(self, galaxy=None, empire=None, registries=None):
        self.savegame_path = "test_savegame"
        self.current_empire = empire or Empire(1, "Test Empire", (255, 0, 0))
        self.active_empire = self.current_empire
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
        """Mock command handler that tracks commands for test verification.

        PROJ-208: Updated to track commands and execute AddToConstructionQueueCommand.
        """
        self.commands_handled.append(cmd)

        # PROJ-208: Actually execute AddToConstructionQueueCommand to maintain queue behavior
        from game.strategy.engine.commands import AddToConstructionQueueCommand
        if isinstance(cmd, AddToConstructionQueueCommand):
            # Find the correct queue (entity's main queue or facility queue)
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
        """Resolve entity by ID and type for mock command execution."""
        if entity_type == "planet":
            for planets in self.galaxy._global_hex_planets.values():
                for planet in planets:
                    if getattr(planet, 'id', None) == entity_id:
                        return planet
        elif entity_type == "fleet":
            return self.galaxy.fleets_by_id.get(entity_id)
        return None

    def _resolve_queue(self, entity_id, entity_type, queue_id):
        """Resolve the construction queue, handling multi-queue entities.

        PROJ-208: Supports facility queues via queue_id.
        """
        entity = self._resolve_entity(entity_id, entity_type)
        if entity is None:
            return None

        # If no queue_id or matches base pattern, use entity's main queue
        if queue_id is None:
            return getattr(entity, 'construction_queue', None)

        # Check if queue_id matches a facility's instance_id
        if hasattr(entity, 'facilities'):
            for facility in entity.facilities:
                if getattr(facility, 'instance_id', None) == queue_id:
                    return getattr(facility, 'construction_queue', None)

        # Check if queue_id matches base queue pattern
        base_queue_pattern = f"planet_{entity_id}_base"
        if queue_id == base_queue_pattern:
            return getattr(entity, 'construction_queue', None)

        # Fallback to entity's main queue
        return getattr(entity, 'construction_queue', None)


@pytest.fixture
def mock_design_catalog():
    """Mock DesignLibrary for testing.

    PROJ-40: Updated to create mock directly instead of patching.
    Now injected via DI in build_queue_screen fixture.
    """
    mock_instance = MagicMock()

    complex_design = MagicMock()
    complex_design.design_id = "mining_complex_mk1"
    complex_design.name = "Mining Complex"
    complex_design.vehicle_type = "Planetary Complex"

    ship_design = MagicMock()
    ship_design.design_id = "frigate_mk1"
    ship_design.name = "Frigate"
    ship_design.vehicle_type = "Ship"

    satellite_design = MagicMock()
    satellite_design.design_id = "defense_sat_mk1"
    satellite_design.name = "Defense Satellite"
    satellite_design.vehicle_type = "Satellite"

    fighter_design = MagicMock()
    fighter_design.design_id = "interceptor_mk1"
    fighter_design.name = "Interceptor"
    fighter_design.vehicle_type = "Fighter"

    mock_instance.scan_designs.return_value = [
        complex_design, ship_design, satellite_design, fighter_design
    ]
    mock_instance.designs_folder = "test_designs"
    mock_instance.load_design_data.return_value = DesignLoadResult.not_found("test")

    return mock_instance


@pytest.fixture
def mock_design_loader():
    """Mock SimulationDesignLoader for testing.

    PROJ-40: New fixture for DI injection.
    """
    return MagicMock()


@pytest.fixture
def build_queue_screen(mock_design_catalog, mock_design_loader, mock_registries, ui_manager):
    """Create BuildQueueScreen for testing.

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

    # Create mock galaxy with planet
    empire = Empire(1, "Test Empire", (255, 0, 0))
    galaxy = MockGalaxy()
    galaxy._global_hex_planets[hex_coord] = [planet]

    # Create mock session with registries
    session = MockSession(galaxy=galaxy, empire=empire, registries=mock_registries)

    # Mock callback
    on_close = MagicMock()

    # Import and create screen with injected dependencies
    from game.ui.screens.build_queue_screen import BuildQueueScreen
    # PROJ-382 Phase 1: ``session=`` is gone; pass MockSession as facade
    # (command dispatch + get_registries).
    # PROJ-396 MAJ-002: portrait_session replaced by narrow theme_id_supplier.
    bq_screen = BuildQueueScreen(
        manager,
        initial_yard=planet,
        on_close_callback=on_close,
        design_catalog=mock_design_catalog,
        design_loader=mock_design_loader,
        hex_coord=hex_coord,
        galaxy=galaxy,
        empire=empire,
        facade=session,
        theme_id_supplier=lambda: "Federation",
    )

    yield bq_screen
