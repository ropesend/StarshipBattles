"""Gap-fill characterization tests for SuperweaponOrderProcessor (PROJ-341 §2).

Pins behaviors that the existing 27-test file in
`test_superweapon_order_processor.py` does NOT cover:
- Stabilizer-blocking cancellation paths for the 5 non-self-destruct weapons.
- OPEN_WARP_POINT far-end Chebyshev-style direction math (OBS-004).
- CLOSE_WARP_POINT legacy-string-target back-compat path (OBS-005).
- Empty-fleet cleanup (SG-003) for SELF_DESTRUCT.
- Dyson-Sphere fallback atmosphere when `empire.race_config is None`.
- `_get_reference_planet` first-planet semantics (OBS-006).

Per master plan: pin current behavior, do NOT fix observations.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.star_system import StarSystem, WarpPoint
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.stars import Star
from game.strategy.engine.superweapon_order_processor import (
    SuperweaponOrderProcessor,
)


# ---------------------------------------------------------------------------
# Fixtures (copied per D-007 — no shared conftest)
# ---------------------------------------------------------------------------


# PROJ-368 Phase 4: SELF_DESTRUCT was lifted from SuperweaponOrderProcessor
# to SelfDestructHandler. Tests that called process_self_destruct now route
# through the handler with the same arguments and field shape.
def _lift_self_destruct(processor, fleet, empire, galaxy):
    from game.strategy.engine.order_handlers.self_destruct import SelfDestructHandler
    handler = SelfDestructHandler(event_bus=getattr(processor, "_event_bus", None))
    return handler.execute_action_order(fleet, empire, galaxy)


@pytest.fixture
def mock_galaxy():
    galaxy = MagicMock(spec=Galaxy)
    galaxy.systems = {}
    galaxy.name_map = {}
    galaxy.planets_by_id = {}
    galaxy._planet_to_system = {}
    galaxy._global_hex_planets = {}
    # Issue #31: ``open_warp_point`` routes through ``Galaxy.add_warp_point``.
    # Wire the mock to mutate ``warp_points`` so geometry assertions still hold.
    galaxy.add_warp_point.side_effect = (
        lambda system, wp: system.warp_points.append(wp)
    )
    return galaxy


@pytest.fixture
def mock_system():
    system = MagicMock(spec=StarSystem)
    system.name = "Alpha"
    system.global_location = HexCoord(10, 10)
    system.stars = [MagicMock(spec=Star, location=HexCoord(0, 0))]
    system.planets = []
    system.warp_points = []
    return system


@pytest.fixture
def mock_planet():
    planet = MagicMock(spec=Planet)
    planet.id = 1
    planet.name = "Alpha III"
    planet.location = HexCoord(2, 0)
    planet.planet_type = PlanetType.CONTINENTAL
    planet.owner_id = None
    return planet


@pytest.fixture
def mock_fleet():
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(10, 10)
    fleet.ships = []
    fleet.orders = []
    return fleet


@pytest.fixture
def component_registry():
    return {
        'planet_imploder': {'abilities': {'DestroyPlanet': {}}},
        'stellerator': {'abilities': {'DestroyStar': {}}},
        'quantum_tunneler': {'abilities': {'OpenWarpPoint': {}}},
        'quantum_disruptor': {'abilities': {'CloseWarpPoint': {}}},
        'dyson_constructor': {'abilities': {'CreateDysonSphere': {}}},
    }


def _stabilizer_block(name: str = "ChronoStabilizer"):
    """Build a fake StabilizerSpec-like object with the ability_name attr."""
    blocker = MagicMock()
    blocker.ability_name = name
    return blocker


FBS_PATH = "game.strategy.services.stabilizer_registry.find_blocking_stabilizer"


# ---------------------------------------------------------------------------
# §2.1 Stabilizer-blocking cancellation paths
# ---------------------------------------------------------------------------


class TestStabilizerCancellation:
    """All 5 non-self-destruct superweapons cancel when a stabilizer blocks."""

    def test_implode_planet_cancels_when_stabilizer_blocks(
        self, mock_fleet, mock_system, mock_planet, mock_galaxy, component_registry
    ):
        mock_system.planets = [mock_planet]
        mock_fleet.ships = [MagicMock(id="s1")]
        mock_fleet.location = mock_system.global_location + mock_planet.location

        order = Order(OrderType.IMPLODE_PLANET, target=mock_planet)
        mock_fleet.get_current_order.return_value = order

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        with patch(FBS_PATH, return_value=_stabilizer_block("ChronoStabilizer")):
            result = processor.process_implode_planet(
                mock_fleet, empire, mock_galaxy, [empire], component_registry
            )

        assert result.success is False
        assert "ChronoStabilizer" in result.message
        mock_fleet.pop_order.assert_called_once()
        mock_galaxy.unregister_planet.assert_not_called()

    def test_stellerate_star_cancels_when_stabilizer_blocks(
        self, mock_fleet, mock_system, mock_galaxy, component_registry
    ):
        mock_fleet.ships = [MagicMock(id="s1")]
        mock_fleet.location = mock_system.global_location

        order = Order(OrderType.STELLERATE_STAR)
        mock_fleet.get_current_order.return_value = order

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.id = 0

        # Patch `system_destroyer` via deferred-import surface and
        # `get_system_at_hex` so the system resolves regardless of mock_galaxy.
        sd_path = "game.strategy.services.system_destroyer"
        with patch(FBS_PATH, return_value=_stabilizer_block()), \
             patch("game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex",
                   return_value=mock_system), \
             patch(f"{sd_path}.collect_system_contents") as mock_collect, \
             patch(f"{sd_path}.destroy_system") as mock_destroy:
            result = processor.process_stellerate_star(
                mock_fleet, empire, mock_galaxy, [empire], component_registry
            )

        assert result.success is False
        # Cancel happens before any destruction; fleet not consumed.
        assert result.fleet_consumed is False
        mock_collect.assert_not_called()
        mock_destroy.assert_not_called()
        mock_fleet.pop_order.assert_called_once()

    def test_open_warp_point_cancels_when_stabilizer_blocks(
        self, mock_fleet, mock_galaxy, component_registry
    ):
        current_system = MagicMock(spec=StarSystem)
        current_system.name = "Alpha"
        current_system.global_location = HexCoord(10, 10)
        current_system.warp_points = []
        current_system.stars = [MagicMock(location=HexCoord(0, 0))]
        target_system = MagicMock(spec=StarSystem)
        target_system.name = "Beta"
        target_system.global_location = HexCoord(50, 50)
        target_system.warp_points = []

        mock_fleet.ships = [MagicMock(id="s1")]
        mock_fleet.location = current_system.global_location

        order = Order(OrderType.OPEN_WARP_POINT, target={"target_system_name": "Beta"})
        mock_fleet.get_current_order.return_value = order

        mock_galaxy.name_map = {"Alpha": current_system, "Beta": target_system}

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        with patch(FBS_PATH, return_value=_stabilizer_block()), \
             patch("game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex",
                   return_value=current_system):
            result = processor.process_open_warp_point(
                mock_fleet, empire, mock_galaxy, component_registry=component_registry
            )

        assert result.success is False
        assert current_system.warp_points == []
        assert target_system.warp_points == []
        mock_fleet.pop_order.assert_called_once()

    def test_close_warp_point_cancels_when_stabilizer_blocks(
        self, mock_fleet, mock_galaxy, component_registry
    ):
        current_system = MagicMock(spec=StarSystem)
        current_system.name = "Alpha"
        current_system.global_location = HexCoord(10, 10)
        current_system.warp_points = [WarpPoint("Beta", HexCoord(5, 0))]

        mock_fleet.ships = [MagicMock(id="s1")]
        mock_fleet.location = current_system.global_location + HexCoord(5, 0)

        order = Order(
            OrderType.CLOSE_WARP_POINT,
            target={"destination_id": "Beta", "target_hex": {"q": 15, "r": 10}},
        )
        mock_fleet.get_current_order.return_value = order

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        with patch(FBS_PATH, return_value=_stabilizer_block()), \
             patch("game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex",
                   return_value=current_system):
            result = processor.process_close_warp_point(
                mock_fleet, empire, mock_galaxy, component_registry=component_registry
            )

        assert result.success is False
        mock_galaxy.remove_warp_link.assert_not_called()
        mock_fleet.pop_order.assert_called_once()

    def test_create_dyson_sphere_cancels_when_stabilizer_blocks(
        self, mock_fleet, mock_system, mock_galaxy, component_registry
    ):
        mock_fleet.ships = [MagicMock(id="s1")]
        mock_fleet.location = mock_system.global_location
        mock_system.stars = [MagicMock(location=HexCoord(0, 0))]
        mock_system.planets = []

        order = Order(OrderType.CREATE_DYSON_SPHERE)
        mock_fleet.get_current_order.return_value = order

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        with patch(FBS_PATH, return_value=_stabilizer_block()), \
             patch("game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex",
                   return_value=mock_system):
            result = processor.process_create_dyson_sphere(
                mock_fleet, empire, mock_galaxy, [empire], component_registry
            )

        assert result.success is False
        # Stars not cleared, no Dyson registered.
        assert mock_system.stars != []
        mock_galaxy.unregister_planet.assert_not_called()
        mock_galaxy.register_planet.assert_not_called()
        mock_fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# §2.2 OPEN_WARP_POINT far-end geometry (OBS-004)
# ---------------------------------------------------------------------------


class TestOpenWarpPointFarEndGeometry:
    """Pin the Chebyshev-style normalisation in lines 376-384."""

    def _setup(self, current_loc: HexCoord, target_loc: HexCoord):
        current_system = MagicMock(spec=StarSystem)
        current_system.name = "Alpha"
        current_system.global_location = current_loc
        current_system.warp_points = []
        current_system.stars = [MagicMock(location=HexCoord(0, 0))]

        target_system = MagicMock(spec=StarSystem)
        target_system.name = "Beta"
        target_system.global_location = target_loc
        target_system.warp_points = []
        target_system.stars = [MagicMock(location=HexCoord(0, 0))]

        return current_system, target_system

    def test_open_warp_point_far_end_placed_on_axis_for_axial_pairing(
        self, mock_fleet, mock_galaxy, component_registry
    ):
        """Source (10,10) → Target (40,10): direction (-30,0), dist=30,
        far_q = round(-30/30 * 6) = -6, far_r = 0."""
        current_system, target_system = self._setup(HexCoord(10, 10), HexCoord(40, 10))

        ship = MagicMock(id="s1")
        mock_fleet.ships = [ship]
        mock_fleet.location = current_system.global_location

        order = Order(OrderType.OPEN_WARP_POINT, target={"target_system_name": "Beta"})
        mock_fleet.get_current_order.return_value = order

        mock_galaxy.name_map = {"Beta": target_system}

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        with patch(FBS_PATH, return_value=None), \
             patch("game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex",
                   return_value=current_system), \
             patch("game.strategy.engine.superweapon_order_processor."
                   "SuperweaponValidator.find_ship_with_ability", return_value=ship):
            processor.process_open_warp_point(
                mock_fleet, empire, mock_galaxy, [empire], component_registry
            )

        assert len(target_system.warp_points) == 1
        far_wp = target_system.warp_points[0]
        assert far_wp.location == HexCoord(-6, 0)

    def test_open_warp_point_far_end_uses_chebyshev_normalisation_for_diagonal_pairing(
        self, mock_fleet, mock_galaxy, component_registry
    ):
        """Source (50,50) → Target (10,10): direction (40,40), dist=40,
        far_q = round(40/40 * 6) = 6, far_r = 6 — diagonal placement."""
        current_system, target_system = self._setup(HexCoord(50, 50), HexCoord(10, 10))

        ship = MagicMock(id="s1")
        mock_fleet.ships = [ship]
        mock_fleet.location = current_system.global_location

        order = Order(OrderType.OPEN_WARP_POINT, target={"target_system_name": "Beta"})
        mock_fleet.get_current_order.return_value = order

        mock_galaxy.name_map = {"Beta": target_system}

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        with patch(FBS_PATH, return_value=None), \
             patch("game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex",
                   return_value=current_system), \
             patch("game.strategy.engine.superweapon_order_processor."
                   "SuperweaponValidator.find_ship_with_ability", return_value=ship):
            processor.process_open_warp_point(
                mock_fleet, empire, mock_galaxy, [empire], component_registry
            )

        assert len(target_system.warp_points) == 1
        far_wp = target_system.warp_points[0]
        assert far_wp.location == HexCoord(6, 6)


# ---------------------------------------------------------------------------
# §2.3 CLOSE_WARP_POINT legacy back-compat (OBS-005)
# ---------------------------------------------------------------------------


class TestCloseWarpPointLegacy:

    def test_close_warp_point_accepts_legacy_string_target_without_sector_check(
        self, mock_fleet, mock_galaxy, component_registry
    ):
        """OBS-005: when `order.target` is a plain string, expected_hex is
        None and the wrong-sector check is skipped."""
        current_system = MagicMock(spec=StarSystem)
        current_system.name = "Alpha"
        current_system.global_location = HexCoord(10, 10)
        current_system.warp_points = [WarpPoint("Beta", HexCoord(5, 0))]

        ship = MagicMock(id="s1")
        mock_fleet.ships = [ship]
        # Fleet is at the system center — would fail expected_hex if it
        # had been provided. Legacy path should still succeed.
        mock_fleet.location = current_system.global_location

        order = Order(OrderType.CLOSE_WARP_POINT, target="Beta")
        mock_fleet.get_current_order.return_value = order

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        with patch(FBS_PATH, return_value=None), \
             patch("game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex",
                   return_value=current_system), \
             patch("game.strategy.engine.superweapon_order_processor."
                   "SuperweaponValidator.find_ship_with_ability", return_value=ship):
            result = processor.process_close_warp_point(
                mock_fleet, empire, mock_galaxy, [empire], component_registry
            )

        assert result.success is True
        mock_galaxy.remove_warp_link.assert_called_once_with("Alpha", "Beta")


# ---------------------------------------------------------------------------
# §2.4 CLOSE_WARP_POINT precondition errors not yet pinned
# ---------------------------------------------------------------------------


class TestCloseWarpPointPreconditions:

    def test_close_warp_point_returns_failure_when_destination_id_is_empty_string(
        self, mock_fleet, mock_galaxy, component_registry
    ):
        ship = MagicMock(id="s1")
        mock_fleet.ships = [ship]
        mock_fleet.location = HexCoord(10, 10)

        order = Order(
            OrderType.CLOSE_WARP_POINT,
            target={"destination_id": "", "target_hex": {"q": 10, "r": 10}},
        )
        mock_fleet.get_current_order.return_value = order

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        with patch(FBS_PATH, return_value=None):
            result = processor.process_close_warp_point(
                mock_fleet, empire, mock_galaxy, [empire], component_registry
            )

        assert result.success is False
        assert "destination" in result.message.lower()
        mock_galaxy.remove_warp_link.assert_not_called()
        mock_fleet.pop_order.assert_called_once()

    def test_close_warp_point_returns_failure_when_fleet_not_at_a_system(
        self, mock_fleet, mock_galaxy, component_registry
    ):
        ship = MagicMock(id="s1")
        mock_fleet.ships = [ship]
        mock_fleet.location = HexCoord(999, 999)

        order = Order(
            OrderType.CLOSE_WARP_POINT,
            target={"destination_id": "Beta", "target_hex": {"q": 999, "r": 999}},
        )
        mock_fleet.get_current_order.return_value = order

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        with patch(FBS_PATH, return_value=None), \
             patch("game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex",
                   return_value=None):
            result = processor.process_close_warp_point(
                mock_fleet, empire, mock_galaxy, [empire], component_registry
            )

        assert result.success is False
        assert "not at a star system" in result.message.lower()
        mock_galaxy.remove_warp_link.assert_not_called()
        mock_fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# §2.5 SELF_DESTRUCT empty-fleet cleanup (SG-003) + invalid targets
# ---------------------------------------------------------------------------


class TestSelfDestructFleetCleanup:

    def test_self_destruct_removes_empty_fleet_from_empire(self, mock_fleet, mock_galaxy):
        ship = MagicMock(id="ship-1", name="Sole Survivor")
        # `fleet.ships` is mutated by `remove_ship` in production. Use a real
        # list and a real remove_ship side-effect so `len(fleet.ships) == 0`
        # holds at the cleanup check.
        mock_fleet.ships = [ship]
        mock_fleet.remove_ship.side_effect = lambda s: mock_fleet.ships.remove(s)

        order = Order(OrderType.SELF_DESTRUCT, target=["ship-1"])
        mock_fleet.get_current_order.return_value = order

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.id = 0

        result = _lift_self_destruct(processor, mock_fleet, empire, mock_galaxy)

        assert result.success is True
        assert result.fleet_consumed is True
        empire.remove_fleet.assert_called_once_with(mock_fleet, event_bus=None)

    def test_self_destruct_does_not_remove_fleet_when_ships_remain(self, mock_fleet, mock_galaxy):
        ship1 = MagicMock(id="ship-1", name="A")
        ship2 = MagicMock(id="ship-2", name="B")
        mock_fleet.ships = [ship1, ship2]
        mock_fleet.remove_ship.side_effect = lambda s: mock_fleet.ships.remove(s)

        order = Order(OrderType.SELF_DESTRUCT, target=["ship-1"])
        mock_fleet.get_current_order.return_value = order

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.id = 0

        result = _lift_self_destruct(processor, mock_fleet, empire, mock_galaxy)

        assert result.success is True
        assert result.fleet_consumed is False
        empire.remove_fleet.assert_not_called()

    def test_self_destruct_returns_failure_when_target_is_empty_list(self, mock_fleet, mock_galaxy):
        mock_fleet.ships = [MagicMock(id="ship-1")]

        order = Order(OrderType.SELF_DESTRUCT, target=[])
        mock_fleet.get_current_order.return_value = order

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        result = _lift_self_destruct(processor, mock_fleet, empire, mock_galaxy)

        assert result.success is False
        assert "no ships specified" in result.message.lower()

    def test_self_destruct_returns_failure_when_target_is_not_a_list(self, mock_fleet, mock_galaxy):
        mock_fleet.ships = [MagicMock(id="ship-1")]

        order = Order(OrderType.SELF_DESTRUCT, target="not-a-list")
        mock_fleet.get_current_order.return_value = order

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()

        result = _lift_self_destruct(processor, mock_fleet, empire, mock_galaxy)

        assert result.success is False
        assert "no ships specified" in result.message.lower()


# ---------------------------------------------------------------------------
# §2.6 Dyson-Sphere fallback atmosphere when race_config is missing
# ---------------------------------------------------------------------------


class TestDysonSphereRaceConfigFallback:

    def test_create_dyson_sphere_uses_default_atmosphere_when_empire_has_no_race_config(
        self, mock_fleet, mock_system, mock_galaxy, component_registry
    ):
        ship = MagicMock(id="s1")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        star = MagicMock(location=HexCoord(0, 0))
        mock_system.stars = [star]
        mock_system.planets = []

        order = Order(OrderType.CREATE_DYSON_SPHERE)
        mock_fleet.get_current_order.return_value = order

        processor = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []
        empire.race_config = None  # Triggers the fallback branch

        with patch(FBS_PATH, return_value=None), \
             patch("game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex",
                   return_value=mock_system), \
             patch("game.strategy.engine.superweapon_order_processor."
                   "SuperweaponValidator.find_ship_with_ability", return_value=ship):
            result = processor.process_create_dyson_sphere(
                mock_fleet, empire, mock_galaxy, [empire], component_registry
            )

        assert result.success is True
        mock_galaxy.register_planet.assert_called_once()
        dyson = mock_galaxy.register_planet.call_args[0][1]
        assert dyson.surface_gravity == 9.81
        assert dyson.surface_temperature == 288.0
        assert dyson.surface_water == 0.3
        assert dyson.atmosphere == {"O2": 21000.0, "N2": 79000.0}


# ---------------------------------------------------------------------------
# §2.7 _get_reference_planet
# ---------------------------------------------------------------------------


class TestGetReferencePlanet:

    def test_get_reference_planet_returns_first_planet_in_system(self, mock_galaxy):
        """OBS-006: returns the first planet in `system.planets`, not the
        closest to the fleet."""
        planet_close = MagicMock(spec=Planet, location=HexCoord(1, 0))
        planet_far = MagicMock(spec=Planet, location=HexCoord(5, 0))

        system = MagicMock(spec=StarSystem)
        # `planet_far` is FIRST in the list — closer planet is second.
        system.planets = [planet_far, planet_close]

        processor = SuperweaponOrderProcessor()

        with patch("game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.get_system_at_hex",
                   return_value=system):
            ref = processor._get_reference_planet(HexCoord(10, 10), mock_galaxy)

        assert ref is planet_far
