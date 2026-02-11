"""
Tests for SuperweaponValidator.

PROJ-102 Phase 4: Validates superweapon orders for fleets.
"""
import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy with basic methods."""
    galaxy = MagicMock()
    galaxy.systems = {}
    galaxy.name_map = {}
    return galaxy


@pytest.fixture
def mock_fleet():
    """Create a mock fleet at origin."""
    fleet = MagicMock()
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(0, 0)
    fleet.ships = []
    return fleet


@pytest.fixture
def mock_planet():
    """Create a mock planet."""
    planet = MagicMock()
    planet.name = "Test Planet"
    planet.owner_id = None
    planet.location = HexCoord(1, 0)  # Local offset from system
    return planet


@pytest.fixture
def mock_system():
    """Create a mock star system."""
    system = MagicMock()
    system.name = "Test System"
    system.global_location = HexCoord(0, 0)
    system.stars = [MagicMock()]  # Has at least one star
    system.planets = []
    system.warp_points = []
    return system


@pytest.fixture
def mock_component_registry():
    """Create mock component registry with superweapon abilities."""
    return {
        'planet_imploder': {
            'abilities': {'DestroyPlanet': {}}
        },
        'stellerator': {
            'abilities': {'DestroyStar': {}}
        },
        'qti_drive': {
            'abilities': {'OpenWarpPoint': {}}
        },
        'qtd_device': {
            'abilities': {'CloseWarpPoint': {}}
        },
        'dsc_core': {
            'abilities': {'CreateDysonSphere': {}}
        },
        'self_destruct': {
            'abilities': {'SelfDestruct': {}}
        },
        'regular_engine': {
            'abilities': {}  # No superweapon ability
        }
    }


def make_ship_with_component(ship_id: str, component_id: str) -> MagicMock:
    """Helper to create a mock ship with a specific component."""
    ship = MagicMock()
    ship.id = ship_id
    ship.design_data = {
        'layers': {
            'internal': [{'id': component_id}]
        }
    }
    return ship


# =============================================================================
# Test: find_ship_with_ability
# =============================================================================


class TestFindShipWithAbility:
    """Tests for find_ship_with_ability helper."""

    def test_finds_ship_with_matching_ability(self, mock_fleet, mock_component_registry):
        """Returns ship when fleet has a ship with the ability."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "planet_imploder")
        mock_fleet.ships = [ship]

        result = SuperweaponValidator.find_ship_with_ability(
            mock_fleet, "DestroyPlanet", mock_component_registry
        )

        assert result is ship

    def test_returns_none_when_no_ability(self, mock_fleet, mock_component_registry):
        """Returns None when no ship has the ability."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "regular_engine")
        mock_fleet.ships = [ship]

        result = SuperweaponValidator.find_ship_with_ability(
            mock_fleet, "DestroyPlanet", mock_component_registry
        )

        assert result is None

    def test_returns_none_for_empty_fleet(self, mock_fleet, mock_component_registry):
        """Returns None for fleet with no ships."""
        from game.strategy.validation import SuperweaponValidator

        mock_fleet.ships = []

        result = SuperweaponValidator.find_ship_with_ability(
            mock_fleet, "DestroyPlanet", mock_component_registry
        )

        assert result is None

    def test_finds_first_ship_with_ability(self, mock_fleet, mock_component_registry):
        """Returns first matching ship when multiple have ability."""
        from game.strategy.validation import SuperweaponValidator

        ship1 = make_ship_with_component("ship1", "regular_engine")
        ship2 = make_ship_with_component("ship2", "planet_imploder")
        ship3 = make_ship_with_component("ship3", "planet_imploder")
        mock_fleet.ships = [ship1, ship2, ship3]

        result = SuperweaponValidator.find_ship_with_ability(
            mock_fleet, "DestroyPlanet", mock_component_registry
        )

        assert result is ship2


# =============================================================================
# Test: validate_implode_planet
# =============================================================================


class TestValidateImplodePlanet:
    """Tests for validate_implode_planet."""

    def test_valid_implode_at_planet_hex(
        self, mock_galaxy, mock_fleet, mock_planet, mock_system, mock_component_registry
    ):
        """Valid: Fleet at planet hex with DestroyPlanet ability."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "planet_imploder")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location + mock_planet.location

        mock_galaxy.systems = {mock_system.global_location: mock_system}
        mock_system.planets = [mock_planet]

        result = SuperweaponValidator.validate_implode_planet(
            mock_galaxy, mock_fleet, mock_planet, mock_component_registry
        )

        assert result.is_valid is True

    def test_invalid_no_destroy_planet_ability(
        self, mock_galaxy, mock_fleet, mock_planet, mock_system, mock_component_registry
    ):
        """Invalid: Fleet has no DestroyPlanet ability."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "regular_engine")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location + mock_planet.location

        result = SuperweaponValidator.validate_implode_planet(
            mock_galaxy, mock_fleet, mock_planet, mock_component_registry
        )

        assert result.is_valid is False
        assert "DestroyPlanet" in result.message

    def test_invalid_planet_not_exist(
        self, mock_galaxy, mock_fleet, mock_component_registry
    ):
        """Invalid: Target planet is None."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "planet_imploder")
        mock_fleet.ships = [ship]

        result = SuperweaponValidator.validate_implode_planet(
            mock_galaxy, mock_fleet, None, mock_component_registry
        )

        assert result.is_valid is False
        assert "planet" in result.message.lower()


# =============================================================================
# Test: validate_stellerate_star
# =============================================================================


class TestValidateStellerateStar:
    """Tests for validate_stellerate_star."""

    def test_valid_stellerate_at_star_system(
        self, mock_galaxy, mock_fleet, mock_system, mock_component_registry
    ):
        """Valid: Fleet at star system with DestroyStar ability."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "stellerator")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        mock_galaxy.systems = {mock_system.global_location: mock_system}

        result = SuperweaponValidator.validate_stellerate_star(
            mock_galaxy, mock_fleet, mock_component_registry
        )

        assert result.is_valid is True

    def test_invalid_no_destroy_star_ability(
        self, mock_galaxy, mock_fleet, mock_system, mock_component_registry
    ):
        """Invalid: Fleet has no DestroyStar ability."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "regular_engine")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        mock_galaxy.systems = {mock_system.global_location: mock_system}

        result = SuperweaponValidator.validate_stellerate_star(
            mock_galaxy, mock_fleet, mock_component_registry
        )

        assert result.is_valid is False
        assert "DestroyStar" in result.message

    def test_invalid_not_at_star_system(
        self, mock_galaxy, mock_fleet, mock_component_registry
    ):
        """Invalid: Fleet not at any star system."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "stellerator")
        mock_fleet.ships = [ship]
        mock_fleet.location = HexCoord(99, 99)  # Deep space

        mock_galaxy.systems = {}

        result = SuperweaponValidator.validate_stellerate_star(
            mock_galaxy, mock_fleet, mock_component_registry
        )

        assert result.is_valid is False
        assert "system" in result.message.lower()


# =============================================================================
# Test: validate_open_warp_point
# =============================================================================


class TestValidateOpenWarpPoint:
    """Tests for validate_open_warp_point."""

    def test_valid_open_warp_point(
        self, mock_galaxy, mock_fleet, mock_system, mock_component_registry
    ):
        """Valid: Fleet at system with OpenWarpPoint ability, target system exists."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "qti_drive")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        target_system = MagicMock()
        target_system.name = "Target System"

        mock_galaxy.systems = {mock_system.global_location: mock_system}
        mock_galaxy.name_map = {
            "Test System": mock_system,
            "Target System": target_system
        }

        result = SuperweaponValidator.validate_open_warp_point(
            mock_galaxy, mock_fleet, "Target System", mock_component_registry
        )

        assert result.is_valid is True

    def test_invalid_target_system_not_exist(
        self, mock_galaxy, mock_fleet, mock_system, mock_component_registry
    ):
        """Invalid: Target system doesn't exist."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "qti_drive")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        mock_galaxy.systems = {mock_system.global_location: mock_system}
        mock_galaxy.name_map = {"Test System": mock_system}

        result = SuperweaponValidator.validate_open_warp_point(
            mock_galaxy, mock_fleet, "Nonexistent System", mock_component_registry
        )

        assert result.is_valid is False
        assert "exist" in result.message.lower()

    def test_invalid_warp_link_already_exists(
        self, mock_galaxy, mock_fleet, mock_system, mock_component_registry
    ):
        """Invalid: Warp link to target already exists."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "qti_drive")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        # Add existing warp point to target
        existing_wp = MagicMock()
        existing_wp.destination_id = "Target System"
        mock_system.warp_points = [existing_wp]

        target_system = MagicMock()
        target_system.name = "Target System"

        mock_galaxy.systems = {mock_system.global_location: mock_system}
        mock_galaxy.name_map = {
            "Test System": mock_system,
            "Target System": target_system
        }

        result = SuperweaponValidator.validate_open_warp_point(
            mock_galaxy, mock_fleet, "Target System", mock_component_registry
        )

        assert result.is_valid is False
        assert "already" in result.message.lower()

    def test_invalid_no_ability(
        self, mock_galaxy, mock_fleet, mock_system, mock_component_registry
    ):
        """Invalid: Fleet has no OpenWarpPoint ability."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "regular_engine")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        mock_galaxy.systems = {mock_system.global_location: mock_system}

        result = SuperweaponValidator.validate_open_warp_point(
            mock_galaxy, mock_fleet, "Target System", mock_component_registry
        )

        assert result.is_valid is False
        assert "OpenWarpPoint" in result.message


# =============================================================================
# Test: validate_close_warp_point
# =============================================================================


class TestValidateCloseWarpPoint:
    """Tests for validate_close_warp_point."""

    def test_valid_close_warp_point(
        self, mock_galaxy, mock_fleet, mock_system, mock_component_registry
    ):
        """Valid: Fleet at warp point hex with CloseWarpPoint ability."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "qtd_device")
        mock_fleet.ships = [ship]

        # Create warp point at fleet location
        warp_point = MagicMock()
        warp_point.destination_id = "Other System"
        warp_point.location = HexCoord(2, 0)
        mock_system.warp_points = [warp_point]

        mock_fleet.location = mock_system.global_location + warp_point.location
        mock_galaxy.systems = {mock_system.global_location: mock_system}

        result = SuperweaponValidator.validate_close_warp_point(
            mock_galaxy, mock_fleet, "Other System", mock_component_registry
        )

        assert result.is_valid is True

    def test_invalid_no_warp_point_at_location(
        self, mock_galaxy, mock_fleet, mock_system, mock_component_registry
    ):
        """Invalid: No warp point with matching destination at fleet location."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "qtd_device")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        mock_system.warp_points = []
        mock_galaxy.systems = {mock_system.global_location: mock_system}

        result = SuperweaponValidator.validate_close_warp_point(
            mock_galaxy, mock_fleet, "Other System", mock_component_registry
        )

        assert result.is_valid is False
        assert "warp point" in result.message.lower()

    def test_invalid_no_ability(
        self, mock_galaxy, mock_fleet, mock_system, mock_component_registry
    ):
        """Invalid: Fleet has no CloseWarpPoint ability."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "regular_engine")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        mock_galaxy.systems = {mock_system.global_location: mock_system}

        result = SuperweaponValidator.validate_close_warp_point(
            mock_galaxy, mock_fleet, "Other System", mock_component_registry
        )

        assert result.is_valid is False
        assert "CloseWarpPoint" in result.message


# =============================================================================
# Test: validate_create_dyson_sphere
# =============================================================================


class TestValidateCreateDysonSphere:
    """Tests for validate_create_dyson_sphere."""

    def test_valid_create_dyson_sphere(
        self, mock_galaxy, mock_fleet, mock_system, mock_component_registry
    ):
        """Valid: Fleet at star system with CreateDysonSphere ability."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "dsc_core")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        mock_galaxy.systems = {mock_system.global_location: mock_system}

        result = SuperweaponValidator.validate_create_dyson_sphere(
            mock_galaxy, mock_fleet, mock_component_registry
        )

        assert result.is_valid is True

    def test_invalid_system_no_stars(
        self, mock_galaxy, mock_fleet, mock_system, mock_component_registry
    ):
        """Invalid: System has no stars."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "dsc_core")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        mock_system.stars = []  # No stars
        mock_galaxy.systems = {mock_system.global_location: mock_system}

        result = SuperweaponValidator.validate_create_dyson_sphere(
            mock_galaxy, mock_fleet, mock_component_registry
        )

        assert result.is_valid is False
        assert "star" in result.message.lower()

    def test_invalid_no_ability(
        self, mock_galaxy, mock_fleet, mock_system, mock_component_registry
    ):
        """Invalid: Fleet has no CreateDysonSphere ability."""
        from game.strategy.validation import SuperweaponValidator

        ship = make_ship_with_component("ship1", "regular_engine")
        mock_fleet.ships = [ship]
        mock_fleet.location = mock_system.global_location

        mock_galaxy.systems = {mock_system.global_location: mock_system}

        result = SuperweaponValidator.validate_create_dyson_sphere(
            mock_galaxy, mock_fleet, mock_component_registry
        )

        assert result.is_valid is False
        assert "CreateDysonSphere" in result.message


# =============================================================================
# Test: validate_self_destruct
# =============================================================================


class TestValidateSelfDestruct:
    """Tests for validate_self_destruct."""

    def test_valid_self_destruct(self, mock_fleet, mock_component_registry):
        """Valid: All specified ships have SelfDestruct ability."""
        from game.strategy.validation import SuperweaponValidator

        ship1 = make_ship_with_component("ship1", "self_destruct")
        ship2 = make_ship_with_component("ship2", "self_destruct")
        mock_fleet.ships = [ship1, ship2]

        result = SuperweaponValidator.validate_self_destruct(
            mock_fleet, ["ship1", "ship2"], mock_component_registry
        )

        assert result.is_valid is True

    def test_invalid_ship_id_not_in_fleet(self, mock_fleet, mock_component_registry):
        """Invalid: Ship ID not found in fleet."""
        from game.strategy.validation import SuperweaponValidator

        ship1 = make_ship_with_component("ship1", "self_destruct")
        mock_fleet.ships = [ship1]

        result = SuperweaponValidator.validate_self_destruct(
            mock_fleet, ["ship1", "nonexistent"], mock_component_registry
        )

        assert result.is_valid is False
        assert "not found" in result.message.lower()

    def test_invalid_ship_lacks_ability(self, mock_fleet, mock_component_registry):
        """Invalid: Ship in list lacks SelfDestruct ability."""
        from game.strategy.validation import SuperweaponValidator

        ship1 = make_ship_with_component("ship1", "self_destruct")
        ship2 = make_ship_with_component("ship2", "regular_engine")  # No self-destruct
        mock_fleet.ships = [ship1, ship2]

        result = SuperweaponValidator.validate_self_destruct(
            mock_fleet, ["ship1", "ship2"], mock_component_registry
        )

        assert result.is_valid is False
        assert "SelfDestruct" in result.message

    def test_invalid_empty_ship_list(self, mock_fleet, mock_component_registry):
        """Invalid: Empty ship ID list."""
        from game.strategy.validation import SuperweaponValidator

        ship1 = make_ship_with_component("ship1", "self_destruct")
        mock_fleet.ships = [ship1]

        result = SuperweaponValidator.validate_self_destruct(
            mock_fleet, [], mock_component_registry
        )

        assert result.is_valid is False
        assert "ship" in result.message.lower()

    def test_valid_single_ship(self, mock_fleet, mock_component_registry):
        """Valid: Single ship with SelfDestruct ability."""
        from game.strategy.validation import SuperweaponValidator

        ship1 = make_ship_with_component("ship1", "self_destruct")
        mock_fleet.ships = [ship1]

        result = SuperweaponValidator.validate_self_destruct(
            mock_fleet, ["ship1"], mock_component_registry
        )

        assert result.is_valid is True
