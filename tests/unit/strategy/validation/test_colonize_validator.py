"""
Tests for ColonizeValidator.

PROJ-36: Tests for centralized colonize order validation.
Migrated from test_turn_engine.py::TestColonizeValidation.
Phase 3: Updated to use carried_items with drop pods instead of cargo_contents.
"""
import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord


# Helper to create a standard drop pod item dict
def _drop_pod_item(design_id="test_pod", name="Test Pod"):
    return {
        "vehicle_type": "drop_pod",
        "design_id": design_id,
        "name": name,
        "design_data": {"layers": {"CORE": []}},
        "mass": 500,
    }


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_galaxy():
    """Create a mock galaxy."""
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex = MagicMock(return_value=[])
    return galaxy


@pytest.fixture
def mock_fleet():
    """Create a mock fleet."""
    fleet = MagicMock()
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = HexCoord(0, 0)
    fleet.ships = []
    fleet.orders = []
    return fleet


@pytest.fixture
def mock_planet():
    """Create a mock unowned planet."""
    from enum import Enum

    class MockPlanetType(Enum):
        CONTINENTAL = "CONTINENTAL"

    planet = MagicMock()
    planet.name = "Test Planet"
    planet.owner_id = None  # Unowned
    planet.location = HexCoord(0, 0)
    planet.planet_type = MockPlanetType.CONTINENTAL
    return planet


# =============================================================================
# Test: Basic Validation
# =============================================================================


class TestColonizeValidatorBasic:
    """Tests for basic colonize validation."""

    def test_validate_no_fleet(self, mock_galaxy):
        """Validation fails when fleet is None."""
        from game.strategy.validation import ColonizeValidator

        result = ColonizeValidator.validate(mock_galaxy, None, None)

        assert result.is_valid is False
        assert "fleet" in result.message.lower()

    def test_validate_unowned_planet(self, mock_galaxy, mock_fleet, mock_planet):
        """Valid colonize order on unowned planet."""
        from game.strategy.validation import ColonizeValidator

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        # Give fleet a ship with a drop pod in carried_items
        ship = MagicMock()
        ship.carried_items = [_drop_pod_item()]
        mock_fleet.ships = [ship]

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)

        assert result.is_valid is True

    def test_validate_owned_planet_fails(self, mock_galaxy, mock_fleet, mock_planet):
        """Cannot colonize already-owned planet."""
        from game.strategy.validation import ColonizeValidator

        mock_planet.owner_id = 1  # Already owned
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)

        assert result.is_valid is False
        assert result.error_code == "ALREADY_OWNED"

    def test_validate_wrong_location(self, mock_galaxy, mock_fleet, mock_planet):
        """Cannot colonize planet from different location."""
        from game.strategy.validation import ColonizeValidator

        mock_galaxy.get_planets_at_global_hex.return_value = []  # No planets at fleet location
        mock_fleet.location = HexCoord(100, 100)  # Far away

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)

        assert result.is_valid is False
        assert result.error_code == "WRONG_LOCATION"


# =============================================================================
# Test: "Any" Planet Validation
# =============================================================================


class TestColonizeValidatorAnyPlanet:
    """Tests for colonize validation with 'Any' planet target."""

    def test_validate_any_planet_success(self, mock_galaxy, mock_fleet, mock_planet):
        """Validate colonize order with 'Any' planet (None target)."""
        from game.strategy.validation import ColonizeValidator

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        # Give fleet a ship with a drop pod in carried_items
        ship = MagicMock()
        ship.carried_items = [_drop_pod_item()]
        mock_fleet.ships = [ship]

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, None)

        assert result.is_valid is True
        assert result.errors == []

    def test_validate_any_no_candidates(self, mock_galaxy, mock_fleet):
        """Colonize 'Any' fails when no unowned planets at location."""
        from game.strategy.validation import ColonizeValidator

        mock_galaxy.get_planets_at_global_hex.return_value = []

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, None)

        assert result.is_valid is False
        assert result.error_code == "NO_CANDIDATES"

    def test_validate_any_skips_owned_planets(self, mock_galaxy, mock_fleet, mock_planet):
        """Colonize 'Any' skips already-owned planets."""
        from game.strategy.validation import ColonizeValidator

        mock_planet.owner_id = 1  # Owned
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, None)

        assert result.is_valid is False
        assert result.error_code == "NO_CANDIDATES"


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestColonizeValidatorEdgeCases:
    """Tests for edge cases in colonize validation."""

    def test_multiple_planets_finds_valid_candidate(self, mock_galaxy, mock_fleet):
        """When multiple planets exist, finds a valid unowned candidate."""
        from game.strategy.validation import ColonizeValidator
        from enum import Enum

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        owned_planet = MagicMock()
        owned_planet.owner_id = 1
        owned_planet.name = "Owned Planet"

        unowned_planet = MagicMock()
        unowned_planet.owner_id = None
        unowned_planet.name = "Unowned Planet"
        unowned_planet.planet_type = MockPlanetType.CONTINENTAL

        mock_galaxy.get_planets_at_global_hex.return_value = [owned_planet, unowned_planet]
        mock_fleet.location = HexCoord(0, 0)

        # Give fleet a ship with a drop pod in carried_items
        ship = MagicMock()
        ship.carried_items = [_drop_pod_item()]
        mock_fleet.ships = [ship]

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, None)

        assert result.is_valid is True

    def test_validate_specific_planet_not_at_location(self, mock_galaxy, mock_fleet, mock_planet):
        """Specific planet validation fails if planet is not at fleet location."""
        from game.strategy.validation import ColonizeValidator

        other_planet = MagicMock()
        other_planet.owner_id = None
        other_planet.name = "Other Planet"

        # Planet at location is different from target
        mock_galaxy.get_planets_at_global_hex.return_value = [other_planet]
        mock_fleet.location = HexCoord(0, 0)

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)

        assert result.is_valid is False
        assert result.error_code == "WRONG_LOCATION"

    def test_fleet_moved_between_validation_and_execution(self, mock_galaxy, mock_fleet, mock_planet):
        """Validation reflects current fleet location, not cached location."""
        from game.strategy.validation import ColonizeValidator

        # Give fleet a ship with a drop pod in carried_items
        ship = MagicMock()
        ship.carried_items = [_drop_pod_item()]
        mock_fleet.ships = [ship]

        # Initially valid
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result1 = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)
        assert result1.is_valid is True

        # Fleet moves away
        mock_fleet.location = HexCoord(100, 100)
        mock_galaxy.get_planets_at_global_hex.return_value = []

        result2 = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)
        assert result2.is_valid is False
        assert result2.error_code == "WRONG_LOCATION"

    def test_planet_colonized_between_validation_and_execution(self, mock_galaxy, mock_fleet, mock_planet):
        """Validation reflects current planet ownership, not cached state."""
        from game.strategy.validation import ColonizeValidator

        # Give fleet a ship with a drop pod in carried_items
        ship = MagicMock()
        ship.carried_items = [_drop_pod_item()]
        mock_fleet.ships = [ship]

        # Initially valid
        mock_planet.owner_id = None
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result1 = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)
        assert result1.is_valid is True

        # Planet colonized by another empire
        mock_planet.owner_id = 2

        result2 = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)
        assert result2.is_valid is False
        assert result2.error_code == "ALREADY_OWNED"


# =============================================================================
# Test: Error Messages
# =============================================================================


class TestColonizeValidatorMessages:
    """Tests for error message content."""

    def test_no_fleet_message_mentions_fleet(self, mock_galaxy):
        """Error message for no fleet mentions 'fleet'."""
        from game.strategy.validation import ColonizeValidator

        result = ColonizeValidator.validate(mock_galaxy, None, None)

        assert "fleet" in result.message.lower()

    def test_already_owned_message_mentions_planet_name(self, mock_galaxy, mock_fleet, mock_planet):
        """Error message for owned planet mentions planet name."""
        from game.strategy.validation import ColonizeValidator

        mock_planet.name = "Alpha Centauri IV"
        mock_planet.owner_id = 1
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_fleet.location = mock_planet.location

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)

        assert mock_planet.name in result.message

    def test_no_candidates_message_is_clear(self, mock_galaxy, mock_fleet):
        """Error message for no candidates is descriptive."""
        from game.strategy.validation import ColonizeValidator

        mock_galaxy.get_planets_at_global_hex.return_value = []

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, None)

        assert "colonizable" in result.message.lower() or "no" in result.message.lower()


# =============================================================================
# Test: Colony Pod Validation (PROJ-55)
# =============================================================================


class TestColonizeValidatorColonyPods:
    """Tests for colony pod requirement validation."""

    @pytest.fixture
    def mock_planet_ice_dwarf(self):
        """Create a mock ICE_DWARF planet."""
        from enum import Enum
        from game.strategy.data.planet import Planet

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"

        # PROJ-193: Use spec=Planet but set all IPlanet protocol properties
        planet = MagicMock(spec=Planet)
        planet.name = "Frostworld"
        planet.owner_id = None
        planet.location = HexCoord(0, 0)
        planet.planet_type = MockPlanetType.ICE_DWARF
        planet.deposits = {}
        planet.id = 1
        planet.populations = []
        planet.max_population = 1000
        planet.facilities = []
        planet.atmosphere = {}
        planet.surface_gravity = 9.8
        planet.surface_temperature = 300.0
        planet.orbit_distance = 1
        planet.radius_hexes = 0
        planet.image_id = ""
        return planet

    @pytest.fixture
    def mock_planet_continental(self):
        """Create a mock CONTINENTAL planet."""
        from enum import Enum
        from game.strategy.data.planet import Planet

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        # PROJ-193: Use spec=Planet but set all IPlanet protocol properties
        planet = MagicMock(spec=Planet)
        planet.name = "Earth-like"
        planet.owner_id = None
        planet.location = HexCoord(0, 0)
        planet.planet_type = MockPlanetType.CONTINENTAL
        planet.deposits = {}
        planet.id = 2
        planet.populations = []
        planet.max_population = 1000
        planet.facilities = []
        planet.atmosphere = {}
        planet.surface_gravity = 9.8
        planet.surface_temperature = 300.0
        planet.orbit_distance = 1
        planet.radius_hexes = 0
        planet.image_id = ""
        return planet

    @pytest.fixture
    def mock_ship_with_ice_dwarf_pod(self):
        """Create a mock ship with a drop pod in carried_items."""
        ship = MagicMock()
        ship.name = "Colony Ship Alpha"
        ship.carried_items = [_drop_pod_item("ice_dwarf_pod", "Ice Dwarf Pod")]
        ship.is_combat_capable = MagicMock(return_value=True)
        return ship

    @pytest.fixture
    def mock_ship_with_continental_pod(self):
        """Create a mock ship with a drop pod in carried_items."""
        ship = MagicMock()
        ship.name = "Colony Ship Beta"
        ship.carried_items = [_drop_pod_item("continental_pod", "Continental Pod")]
        ship.is_combat_capable = MagicMock(return_value=True)
        return ship

    @pytest.fixture
    def mock_ship_without_pod(self):
        """Create a mock ship without any colony pod."""
        ship = MagicMock()
        ship.name = "Combat Ship"
        ship.carried_items = []
        ship.is_combat_capable = MagicMock(return_value=True)
        return ship

    @pytest.fixture
    def mock_component_registry(self):
        """Create a mock component registry (kept for API compatibility)."""
        return {}

    def test_validate_with_drop_pod_succeeds_any_planet_type(
        self, mock_galaxy, mock_planet_ice_dwarf, mock_ship_with_continental_pod, mock_component_registry
    ):
        """Phase 3: Drop pods are universal -- any drop pod works on any planet type."""
        from game.strategy.validation import ColonizeValidator

        # Fleet with any drop pod can colonize any planet type
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.ships = [mock_ship_with_continental_pod]
        fleet.orders = []

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet_ice_dwarf]

        result = ColonizeValidator.validate(
            mock_galaxy, fleet, mock_planet_ice_dwarf,
            component_registry=mock_component_registry
        )

        # Drop pods are universal
        assert result.is_valid is True

    def test_validate_accepts_drop_pod(
        self, mock_galaxy, mock_planet_ice_dwarf, mock_ship_with_ice_dwarf_pod, mock_component_registry
    ):
        """Validation passes when fleet has a drop pod."""
        from game.strategy.validation import ColonizeValidator

        # Fleet with drop pod colonizing planet
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.ships = [mock_ship_with_ice_dwarf_pod]
        fleet.orders = []

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet_ice_dwarf]

        result = ColonizeValidator.validate(
            mock_galaxy, fleet, mock_planet_ice_dwarf,
            component_registry=mock_component_registry
        )

        assert result.is_valid is True

    def test_validate_no_colony_pod_at_all(
        self, mock_galaxy, mock_planet_ice_dwarf, mock_ship_without_pod, mock_component_registry
    ):
        """Validation fails when fleet has no colony pods."""
        from game.strategy.validation import ColonizeValidator

        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.ships = [mock_ship_without_pod]
        fleet.orders = []

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet_ice_dwarf]

        result = ColonizeValidator.validate(
            mock_galaxy, fleet, mock_planet_ice_dwarf,
            component_registry=mock_component_registry
        )

        assert result.is_valid is False
        assert result.error_code == "NO_COLONY_POD"

    def test_get_available_colony_pods(
        self, mock_ship_with_ice_dwarf_pod, mock_ship_with_continental_pod, mock_component_registry
    ):
        """Should correctly count available drop pods."""
        from game.strategy.validation import ColonizeValidator

        fleet = MagicMock()
        fleet.ships = [mock_ship_with_ice_dwarf_pod, mock_ship_with_continental_pod]

        result = ColonizeValidator.get_available_colony_pods(fleet, mock_component_registry)

        # Phase 3: Returns {'drop_pod': N} -- pods are universal
        assert result == {"drop_pod": 2}

    def test_get_available_colony_pods_multiple_same_type(
        self, mock_ship_with_ice_dwarf_pod, mock_component_registry
    ):
        """Should count multiple drop pods."""
        from game.strategy.validation import ColonizeValidator

        # Create another ship with a drop pod
        ship2 = MagicMock()
        ship2.carried_items = [_drop_pod_item("pod_2", "Pod 2")]

        fleet = MagicMock()
        fleet.ships = [mock_ship_with_ice_dwarf_pod, ship2]

        result = ColonizeValidator.get_available_colony_pods(fleet, mock_component_registry)

        assert result == {"drop_pod": 2}

    def test_get_committed_colony_pods(self, mock_planet_ice_dwarf, mock_planet_continental):
        """Should correctly count committed colonize orders."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.order_types import OrderType

        order1 = MagicMock()
        order1.type = OrderType.COLONIZE
        order1.target = mock_planet_ice_dwarf

        order2 = MagicMock()
        order2.type = OrderType.COLONIZE
        order2.target = mock_planet_ice_dwarf

        order3 = MagicMock()
        order3.type = OrderType.COLONIZE
        order3.target = mock_planet_continental

        fleet = MagicMock()
        fleet.orders = [order1, order2, order3]

        result = ColonizeValidator.get_committed_colony_pods(fleet)

        # Phase 3: Returns {'drop_pod': N} -- counts all COLONIZE orders
        assert result == {"drop_pod": 3}

    def test_validate_rejects_overcommitted_pods(
        self, mock_galaxy, mock_planet_ice_dwarf, mock_ship_with_ice_dwarf_pod, mock_component_registry
    ):
        """Cannot queue colonization when all drop pods are committed."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.order_types import OrderType

        # Create an existing colonize order
        existing_order = MagicMock()
        existing_order.type = OrderType.COLONIZE
        existing_order.target = mock_planet_ice_dwarf

        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.ships = [mock_ship_with_ice_dwarf_pod]  # Only 1 drop pod
        fleet.orders = [existing_order]  # Already committed

        # Create a second planet
        another_planet = MagicMock()
        another_planet.name = "Frostworld 2"
        another_planet.owner_id = None
        another_planet.location = HexCoord(0, 0)

        from enum import Enum
        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"
        another_planet.planet_type = MockPlanetType.ICE_DWARF

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet_ice_dwarf, another_planet]

        # Try to queue second colonization -- should fail (1 pod, 1 committed)
        result = ColonizeValidator.validate(
            mock_galaxy, fleet, another_planet,
            component_registry=mock_component_registry
        )

        assert result.is_valid is False
        assert result.error_code == "COLONY_POD_EXHAUSTED"

    def test_validate_allows_second_pod_when_available(
        self, mock_galaxy, mock_planet_continental, mock_ship_with_ice_dwarf_pod,
        mock_ship_with_continental_pod, mock_component_registry
    ):
        """Phase 3: Two drop pods allow two colonize orders."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.order_types import OrderType

        # Create a planet that's already targeted
        ice_dwarf_planet = MagicMock()
        ice_dwarf_planet.name = "Frostworld"
        ice_dwarf_planet.owner_id = None
        ice_dwarf_planet.location = HexCoord(0, 0)

        from enum import Enum
        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"
        ice_dwarf_planet.planet_type = MockPlanetType.ICE_DWARF

        # Existing order uses one pod
        existing_order = MagicMock()
        existing_order.type = OrderType.COLONIZE
        existing_order.target = ice_dwarf_planet

        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        # Two ships, each with a drop pod = 2 pods total
        fleet.ships = [mock_ship_with_ice_dwarf_pod, mock_ship_with_continental_pod]
        fleet.orders = [existing_order]  # 1 committed, 1 remaining

        mock_galaxy.get_planets_at_global_hex.return_value = [ice_dwarf_planet, mock_planet_continental]

        # Should succeed -- 2 pods, 1 committed, 1 remaining
        result = ColonizeValidator.validate(
            mock_galaxy, fleet, mock_planet_continental,
            component_registry=mock_component_registry
        )

        assert result.is_valid is True


# =============================================================================
# Test: Zone Colonization (PROJ-139)
# =============================================================================


class TestColonizeValidatorZoneColonization:
    """Tests for colonizing planets from zone hexes."""

    def test_validate_colonize_dyson_sphere_from_zone_hex(self, mock_galaxy, mock_fleet):
        """Fleet in Dyson Sphere's zone can colonize it."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.planet import Planet
        from enum import Enum

        class MockPlanetType(Enum):
            DYSON_SPHERE = "DYSON_SPHERE"

        mock_dyson = MagicMock(spec=Planet)
        mock_dyson.name = "Dyson Sphere"
        mock_dyson.owner_id = None
        mock_dyson.location = HexCoord(0, 0)
        mock_dyson.planet_type = MockPlanetType.DYSON_SPHERE
        mock_dyson.radius_hexes = 6
        mock_dyson.resources = {}
        mock_dyson.id = 1
        mock_dyson.populations = []
        mock_dyson.max_population = 1000
        mock_dyson.facilities = []
        mock_dyson.atmosphere = {}
        mock_dyson.surface_gravity = 9.8
        mock_dyson.surface_temperature = 300.0
        mock_dyson.orbit_distance = 1
        mock_dyson.image_id = ""

        # Fleet is at zone hex (2, 0), not at center
        mock_fleet.location = HexCoord(2, 0)

        # Give fleet a ship with a drop pod in carried_items
        ship = MagicMock()
        ship.carried_items = [_drop_pod_item()]
        mock_fleet.ships = [ship]

        mock_galaxy.get_planets_at_global_hex.return_value = []
        mock_galaxy.get_zones_at_global_hex = MagicMock(return_value=[mock_dyson])

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_dyson)

        assert result.is_valid is True

    def test_validate_colonize_dyson_sphere_from_center(self, mock_galaxy, mock_fleet):
        """Fleet at Dyson Sphere's center can colonize it (standard case)."""
        from game.strategy.validation import ColonizeValidator
        from enum import Enum

        class MockPlanetType(Enum):
            DYSON_SPHERE = "DYSON_SPHERE"

        mock_dyson = MagicMock()
        mock_dyson.name = "Dyson Sphere"
        mock_dyson.owner_id = None
        mock_dyson.location = HexCoord(0, 0)
        mock_dyson.planet_type = MockPlanetType.DYSON_SPHERE

        mock_fleet.location = HexCoord(0, 0)

        # Give fleet a ship with a drop pod
        ship = MagicMock()
        ship.carried_items = [_drop_pod_item()]
        mock_fleet.ships = [ship]

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_dyson]
        mock_galaxy.get_zones_at_global_hex = MagicMock(return_value=[])

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_dyson)

        assert result.is_valid is True

    def test_validate_colonize_normal_planet_unchanged(self, mock_galaxy, mock_fleet):
        """Normal planets (no zone) work without zone lookup."""
        from game.strategy.validation import ColonizeValidator
        from enum import Enum

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        mock_planet = MagicMock()
        mock_planet.name = "Normal Planet"
        mock_planet.owner_id = None
        mock_planet.location = HexCoord(0, 0)
        mock_planet.planet_type = MockPlanetType.CONTINENTAL

        mock_fleet.location = HexCoord(0, 0)

        # Give fleet a ship with a drop pod
        ship = MagicMock()
        ship.carried_items = [_drop_pod_item()]
        mock_fleet.ships = [ship]

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet]
        mock_galaxy.get_zones_at_global_hex = MagicMock(return_value=[])

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_planet)

        assert result.is_valid is True

    def test_validate_zone_planet_not_at_different_location(self, mock_galaxy, mock_fleet):
        """Cannot colonize planet if fleet is outside both center and zone."""
        from game.strategy.validation import ColonizeValidator
        from enum import Enum

        class MockPlanetType(Enum):
            DYSON_SPHERE = "DYSON_SPHERE"

        mock_dyson = MagicMock()
        mock_dyson.name = "Dyson Sphere"
        mock_dyson.owner_id = None
        mock_dyson.location = HexCoord(0, 0)
        mock_dyson.planet_type = MockPlanetType.DYSON_SPHERE

        # Fleet is far away from zone
        mock_fleet.location = HexCoord(100, 100)
        mock_galaxy.get_planets_at_global_hex.return_value = []
        mock_galaxy.get_zones_at_global_hex = MagicMock(return_value=[])

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_dyson)

        assert result.is_valid is False
        assert result.error_code == "WRONG_LOCATION"


# =============================================================================
# Test: "Any Planet" Pod Validation (PROJ-140 Phase 2)
# =============================================================================


class TestColonizeValidatorAnyPlanetPods:
    """Tests for 'Any Planet' validation with colony pod matching."""

    @pytest.fixture
    def mock_galaxy(self):
        """Create a mock galaxy."""
        galaxy = MagicMock()
        galaxy.get_planets_at_global_hex = MagicMock(return_value=[])
        galaxy.get_zones_at_global_hex = MagicMock(return_value=[])
        return galaxy

    @pytest.fixture
    def mock_fleet(self):
        """Create a mock fleet."""
        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.ships = []
        fleet.orders = []
        return fleet

    @pytest.fixture
    def mock_component_registry(self):
        """Create a mock component registry (kept for API compatibility)."""
        return {}

    def _make_planet(self, planet_type_name: str, name: str = "Test Planet"):
        """Create a mock planet of the given type."""
        from enum import Enum
        from game.strategy.data.planet import Planet

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"
            CONTINENTAL = "CONTINENTAL"

        planet = MagicMock(spec=Planet)
        planet.name = name
        planet.owner_id = None
        planet.location = HexCoord(0, 0)
        planet.planet_type = MockPlanetType[planet_type_name]
        planet.deposits = {}
        planet.id = 1
        planet.populations = []
        planet.max_population = 1000
        planet.facilities = []
        planet.atmosphere = {}
        planet.surface_gravity = 9.8
        planet.surface_temperature = 300.0
        planet.orbit_distance = 1
        planet.radius_hexes = 0
        planet.image_id = ""
        return planet

    def _make_ship_with_pod(self, pod_type: str):
        """Create a mock ship with a drop pod in carried_items."""
        ship = MagicMock()
        ship.name = f"{pod_type} Colony Ship"
        ship.carried_items = [_drop_pod_item(f"{pod_type.lower()}_pod", f"{pod_type} Pod")]
        return ship

    def test_any_planet_no_ships_fails(
        self, mock_galaxy, mock_fleet, mock_component_registry
    ):
        """Any Planet fails when fleet has no ships (no drop pods)."""
        from game.strategy.validation import ColonizeValidator

        # Fleet has no ships
        mock_fleet.ships = []

        # Planet available
        ice_dwarf_planet = self._make_planet("ICE_DWARF", "Frostworld")
        mock_galaxy.get_planets_at_global_hex.return_value = [ice_dwarf_planet]

        result = ColonizeValidator.validate(
            mock_galaxy, mock_fleet, None,
            component_registry=mock_component_registry
        )

        assert result.is_valid is False
        assert result.error_code == "NO_COLONY_POD"

    def test_any_planet_with_drop_pod_succeeds(
        self, mock_galaxy, mock_fleet, mock_component_registry
    ):
        """Any Planet succeeds when fleet has a drop pod."""
        from game.strategy.validation import ColonizeValidator

        # Fleet has a drop pod
        mock_fleet.ships = [self._make_ship_with_pod("ICE_DWARF")]

        # Planet available
        ice_dwarf_planet = self._make_planet("ICE_DWARF", "Frostworld")
        mock_galaxy.get_planets_at_global_hex.return_value = [ice_dwarf_planet]

        result = ColonizeValidator.validate(
            mock_galaxy, mock_fleet, None,
            component_registry=mock_component_registry
        )

        assert result.is_valid is True

    def test_any_planet_without_drop_pod_fails(
        self, mock_galaxy, mock_fleet
    ):
        """Any Planet with no drop pods fails."""
        from game.strategy.validation import ColonizeValidator

        # Fleet has ship but no drop pods
        ship = MagicMock()
        ship.carried_items = []
        mock_fleet.ships = [ship]

        # Planet available
        ice_dwarf_planet = self._make_planet("ICE_DWARF", "Frostworld")
        mock_galaxy.get_planets_at_global_hex.return_value = [ice_dwarf_planet]

        result = ColonizeValidator.validate(
            mock_galaxy, mock_fleet, None,
        )

        assert result.is_valid is False
        assert result.error_code == "NO_COLONY_POD"

    def test_any_planet_exhausted_pods_fails(
        self, mock_galaxy, mock_fleet, mock_component_registry
    ):
        """Any Planet fails if all drop pods are already committed."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.order_types import OrderType

        # Fleet has one drop pod
        mock_fleet.ships = [self._make_ship_with_pod("ICE_DWARF")]

        # Two planets
        ice_dwarf_1 = self._make_planet("ICE_DWARF", "Frostworld 1")
        ice_dwarf_2 = self._make_planet("ICE_DWARF", "Frostworld 2")

        # Existing order commits the only drop pod
        existing_order = MagicMock()
        existing_order.type = OrderType.COLONIZE
        existing_order.target = ice_dwarf_1
        mock_fleet.orders = [existing_order]

        mock_galaxy.get_planets_at_global_hex.return_value = [ice_dwarf_1, ice_dwarf_2]

        result = ColonizeValidator.validate(
            mock_galaxy, mock_fleet, None,
            component_registry=mock_component_registry
        )

        assert result.is_valid is False
        assert result.error_code in ("NO_COLONY_POD", "COLONY_POD_EXHAUSTED")


# =============================================================================
# Test: Additional Edge Cases (Task 2.10)
# =============================================================================


class TestColonizeValidatorAdvancedEdgeCases:
    """Advanced edge case tests for ColonizeValidator."""

    @pytest.fixture
    def mock_component_registry(self):
        """Create a mock component registry (kept for API compatibility)."""
        return {}

    def _make_planet(self, planet_type_name: str, name: str = "Test Planet"):
        """Create a mock planet of the given type."""
        from enum import Enum
        from game.strategy.data.planet import Planet

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"
            CONTINENTAL = "CONTINENTAL"

        # PROJ-193: Use spec=Planet but set all IPlanet protocol properties
        planet = MagicMock(spec=Planet)
        planet.name = name
        planet.owner_id = None
        planet.location = HexCoord(0, 0)
        planet.planet_type = MockPlanetType[planet_type_name]
        planet.deposits = {}
        # PROJ-193: Required IPlanet properties
        planet.id = 1
        planet.populations = []
        planet.max_population = 1000
        planet.facilities = []
        planet.atmosphere = {}
        planet.surface_gravity = 9.8
        planet.surface_temperature = 300.0
        planet.orbit_distance = 1
        planet.radius_hexes = 0
        planet.image_id = ""
        return planet

    def test_skip_chain_check_allows_overcommit(self, mock_component_registry):
        """skip_chain_check=True allows validation even when pods exhausted."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.order_types import OrderType

        galaxy = MagicMock()
        planet = self._make_planet("ICE_DWARF")
        galaxy.get_planets_at_global_hex = MagicMock(return_value=[planet])

        # Fleet with one drop pod, already committed
        ship = MagicMock()
        ship.carried_items = [_drop_pod_item()]

        existing_order = MagicMock()
        existing_order.type = OrderType.COLONIZE
        existing_order.target = planet

        fleet = MagicMock()
        fleet.id = 1
        fleet.location = HexCoord(0, 0)
        fleet.ships = [ship]
        fleet.orders = [existing_order]

        # Without skip_chain_check: should fail
        result_without_skip = ColonizeValidator.validate(
            galaxy, fleet, planet,
            component_registry=mock_component_registry,
            skip_chain_check=False
        )
        assert result_without_skip.error_code == "COLONY_POD_EXHAUSTED"

        # With skip_chain_check: should pass
        result_with_skip = ColonizeValidator.validate(
            galaxy, fleet, planet,
            component_registry=mock_component_registry,
            skip_chain_check=True
        )
        assert result_with_skip.is_valid is True

    def test_drop_pod_validates(self, mock_component_registry):
        """Drop pod in carried_items validates for colonization."""
        from game.strategy.validation import ColonizeValidator

        galaxy = MagicMock()
        planet = self._make_planet("CONTINENTAL")
        galaxy.get_planets_at_global_hex = MagicMock(return_value=[planet])

        # Ship with drop pod in carried_items
        ship = MagicMock()
        ship.carried_items = [_drop_pod_item()]

        fleet = MagicMock()
        fleet.id = 1
        fleet.location = HexCoord(0, 0)
        fleet.ships = [ship]
        fleet.orders = []

        result = ColonizeValidator.validate(galaxy, fleet, planet)

        assert result.is_valid is True

    def test_no_drop_pod_does_not_satisfy_requirement(self, mock_component_registry):
        """Ship without drop pod in carried_items cannot colonize."""
        from game.strategy.validation import ColonizeValidator

        galaxy = MagicMock()
        planet = self._make_planet("ICE_DWARF")
        galaxy.get_planets_at_global_hex = MagicMock(return_value=[planet])

        # Ship with empty carried_items (no drop pods)
        ship = MagicMock()
        ship.carried_items = []

        fleet = MagicMock()
        fleet.id = 1
        fleet.location = HexCoord(0, 0)
        fleet.ships = [ship]
        fleet.orders = []

        result = ColonizeValidator.validate(galaxy, fleet, planet)

        assert result.is_valid is False
        assert result.error_code == "NO_COLONY_POD"

    def test_get_committed_empty_orders_list(self):
        """get_committed_colony_pods handles empty orders list."""
        from game.strategy.validation import ColonizeValidator

        fleet = MagicMock()
        fleet.orders = []

        result = ColonizeValidator.get_committed_colony_pods(fleet)

        assert result == {"drop_pod": 0}

    def test_get_committed_skips_non_colonize_orders(self):
        """get_committed_colony_pods ignores non-COLONIZE orders."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.order_types import OrderType

        planet = self._make_planet("ICE_DWARF")

        move_order = MagicMock()
        move_order.type = OrderType.MOVE
        move_order.target = None

        colonize_order = MagicMock()
        colonize_order.type = OrderType.COLONIZE
        colonize_order.target = planet

        fleet = MagicMock()
        fleet.orders = [move_order, colonize_order]

        result = ColonizeValidator.get_committed_colony_pods(fleet)

        # Only counts the COLONIZE order
        assert result == {"drop_pod": 1}

    def test_get_committed_counts_colonize_with_none_target(self):
        """get_committed_colony_pods counts COLONIZE orders with target=None."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.order_types import OrderType

        any_planet_order = MagicMock()
        any_planet_order.type = OrderType.COLONIZE
        any_planet_order.target = None  # "Any Planet" order

        fleet = MagicMock()
        fleet.orders = [any_planet_order]

        result = ColonizeValidator.get_committed_colony_pods(fleet)

        # Phase 3: All COLONIZE orders count (pods are universal)
        assert result == {"drop_pod": 1}

    def test_get_available_empty_ships_list(self, mock_component_registry):
        """get_available_colony_pods handles empty ships list."""
        from game.strategy.validation import ColonizeValidator

        fleet = MagicMock()
        fleet.ships = []

        result = ColonizeValidator.get_available_colony_pods(fleet)

        assert result == {"drop_pod": 0}

    def test_get_available_ships_without_pods(self, mock_component_registry):
        """get_available_colony_pods handles ships with no drop pods."""
        from game.strategy.validation import ColonizeValidator

        ship = MagicMock()
        ship.carried_items = []

        fleet = MagicMock()
        fleet.ships = [ship]

        result = ColonizeValidator.get_available_colony_pods(fleet)

        assert result == {"drop_pod": 0}

    def test_fleet_has_colony_pod_returns_true_with_drop_pod(self, mock_component_registry):
        """fleet_has_colony_pod returns True when ship has drop pod."""
        from game.strategy.validation import ColonizeValidator

        ship1 = MagicMock()
        ship1.carried_items = [_drop_pod_item()]

        ship2 = MagicMock()
        ship2.carried_items = [_drop_pod_item()]

        fleet = MagicMock()
        fleet.ships = [ship1, ship2]

        result = ColonizeValidator.fleet_has_colony_pod(fleet, "ICE_DWARF")

        assert result is True

    def test_fleet_has_colony_pod_returns_false_without_drop_pod(self, mock_component_registry):
        """fleet_has_colony_pod returns False when no drop pods."""
        from game.strategy.validation import ColonizeValidator

        ship = MagicMock()
        ship.carried_items = []

        fleet = MagicMock()
        fleet.ships = [ship]

        result = ColonizeValidator.fleet_has_colony_pod(fleet, "ICE_DWARF")

        assert result is False

    def test_any_planet_with_drop_pod_colonizes_any_type(self, mock_component_registry):
        """Phase 3: Drop pods are universal -- any unowned planet can be colonized."""
        from game.strategy.validation import ColonizeValidator

        galaxy = MagicMock()

        # Planet without planet_type attribute
        weird_planet = MagicMock()
        weird_planet.name = "Weird Planet"
        weird_planet.owner_id = None
        weird_planet.location = HexCoord(0, 0)
        del weird_planet.planet_type  # No planet_type

        galaxy.get_planets_at_global_hex = MagicMock(return_value=[weird_planet])

        ship = MagicMock()
        ship.carried_items = [_drop_pod_item()]

        fleet = MagicMock()
        fleet.id = 1
        fleet.location = HexCoord(0, 0)
        fleet.ships = [ship]
        fleet.orders = []

        result = ColonizeValidator.validate(
            galaxy, fleet, None,  # "Any Planet"
        )

        # Phase 3: Drop pods are universal -- should succeed
        assert result.is_valid is True

    def test_any_planet_two_pods_one_committed_succeeds(self, mock_component_registry):
        """Any Planet succeeds when fleet has 2 drop pods and 1 is committed."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.order_types import OrderType

        galaxy = MagicMock()

        # Two planets
        ice_planet = self._make_planet("ICE_DWARF", "Frostworld")
        cont_planet = self._make_planet("CONTINENTAL", "Earth-like")

        galaxy.get_planets_at_global_hex = MagicMock(return_value=[ice_planet, cont_planet])

        # Fleet has two ships, each with a drop pod
        ice_ship = MagicMock()
        ice_ship.carried_items = [_drop_pod_item("pod_1")]

        cont_ship = MagicMock()
        cont_ship.carried_items = [_drop_pod_item("pod_2")]

        # Commit one pod
        ice_order = MagicMock()
        ice_order.type = OrderType.COLONIZE
        ice_order.target = ice_planet

        fleet = MagicMock()
        fleet.id = 1
        fleet.location = HexCoord(0, 0)
        fleet.ships = [ice_ship, cont_ship]
        fleet.orders = [ice_order]  # 1 committed, 1 remaining

        result = ColonizeValidator.validate(
            galaxy, fleet, None,  # "Any Planet"
        )

        # Should succeed -- 2 pods, 1 committed, 1 still available
        assert result.is_valid is True

    # PROJ-191: test_galaxy_without_zone_registry deleted - Galaxy always has get_zones_at_global_hex

    def test_zone_objects_deduplication(self):
        """Zone objects already in planets list are not duplicated."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.planet import Planet
        from enum import Enum

        class MockPlanetType(Enum):
            DYSON_SPHERE = "DYSON_SPHERE"

        galaxy = MagicMock()

        dyson = MagicMock(spec=Planet)
        dyson.name = "Dyson Sphere"
        dyson.owner_id = None
        dyson.planet_type = MockPlanetType.DYSON_SPHERE
        dyson.location = HexCoord(0, 0)
        dyson.resources = {}
        dyson.id = 1
        dyson.populations = []
        dyson.max_population = 1000
        dyson.facilities = []
        dyson.atmosphere = {}
        dyson.surface_gravity = 9.8
        dyson.surface_temperature = 300.0
        dyson.orbit_distance = 1
        dyson.radius_hexes = 6
        dyson.image_id = ""

        # Both methods return the same object
        galaxy.get_planets_at_global_hex = MagicMock(return_value=[dyson])
        galaxy.get_zones_at_global_hex = MagicMock(return_value=[dyson])

        # Give fleet a ship with a drop pod
        ship = MagicMock()
        ship.carried_items = [_drop_pod_item()]

        fleet = MagicMock()
        fleet.id = 1
        fleet.location = HexCoord(0, 0)
        fleet.ships = [ship]
        fleet.orders = []

        result = ColonizeValidator.validate(galaxy, fleet, dyson)

        # Should still work (dyson in valid_candidates only once)
        assert result.is_valid is True
