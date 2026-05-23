"""
Shared fixtures for UI integration tests.

Provides a cached pygame_gui.UIManager to avoid the expensive per-test
initialization (theme parsing, font loading). The manager is rebuilt
only when the underlying display surface changes (root conftest handles
pygame init/font.init for every test).
"""

import pytest
import pygame
import pygame_gui

# Module-level cache for UIManager reuse across tests.
# Survives as long as pygame display stays alive.
_cached_manager = None
_cached_display_id = None


def _get_or_create_manager():
    """Return a valid UIManager, creating one if needed.

    Rebuilds if the display surface changed since the last call.
    """
    global _cached_manager, _cached_display_id

    if not pygame.display.get_surface():
        pygame.display.set_mode((1920, 1080))

    current_display_id = id(pygame.display.get_surface())
    if _cached_manager is None or _cached_display_id != current_display_id:
        _cached_manager = pygame_gui.UIManager((1920, 1080))
        _cached_display_id = current_display_id

    return _cached_manager


@pytest.fixture(autouse=True)
def _ensure_pygame():
    """Ensure a display surface exists before each UI test."""
    if not pygame.display.get_surface():
        pygame.display.set_mode((1920, 1080))


@pytest.fixture
def ui_manager():
    """Provide a clean UIManager for each test.

    Uses a cached manager to avoid expensive re-creation. Clears all
    widgets so each test starts fresh without the initialization cost.
    """
    manager = _get_or_create_manager()
    manager.clear_and_reset()
    return manager


# =============================================================================
# PROJ-494 T2.18: MockGalaxy / MockSession hoisted from
# `test_build_queue_formatting.py` so other UI integration tests can reuse them.
# =============================================================================


class MockGalaxy:
    """Minimal mock Galaxy for BuildQueueScreen integration tests."""
    def __init__(self):
        self.systems = {}
        self._global_hex_planets = {}  # HexCoord -> List[Planet]
        self.fleets_by_id = {}

    def get_planets_at_global_hex(self, hex_coord):
        """Return planets at a given global hex coordinate."""
        return self._global_hex_planets.get(hex_coord, [])


class MockSession:
    """Minimal mock GameSession with the facade-shaped namespaces that
    BuildQueueScreen production code reads from."""

    def __init__(self, galaxy=None, empire=None, registries=None):
        from game.strategy.data.empire import Empire
        self.save_path = "test_savegame"
        self.current_empire = empire or Empire(1, "Test Empire", (255, 0, 0))
        self.turn = 1
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
        """Mock command handler."""
        from game.core.validation import ValidationResult
        return ValidationResult()
