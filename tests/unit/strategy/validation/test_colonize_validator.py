"""
Tests for ColonizeValidator.

PROJ-36: Tests for centralized colonize order validation.
Migrated from test_turn_engine.py::TestColonizeValidation.
"""
import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord


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
    return fleet


@pytest.fixture
def mock_planet():
    """Create a mock unowned planet."""
    planet = MagicMock()
    planet.name = "Test Planet"
    planet.owner_id = None  # Unowned
    planet.location = HexCoord(0, 0)
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

        owned_planet = MagicMock()
        owned_planet.owner_id = 1
        owned_planet.name = "Owned Planet"

        unowned_planet = MagicMock()
        unowned_planet.owner_id = None
        unowned_planet.name = "Unowned Planet"

        mock_galaxy.get_planets_at_global_hex.return_value = [owned_planet, unowned_planet]
        mock_fleet.location = HexCoord(0, 0)

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

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"

        planet = MagicMock()
        planet.name = "Frostworld"
        planet.owner_id = None
        planet.location = HexCoord(0, 0)
        planet.planet_type = MockPlanetType.ICE_DWARF
        return planet

    @pytest.fixture
    def mock_planet_continental(self):
        """Create a mock CONTINENTAL planet."""
        from enum import Enum

        class MockPlanetType(Enum):
            CONTINENTAL = "CONTINENTAL"

        planet = MagicMock()
        planet.name = "Earth-like"
        planet.owner_id = None
        planet.location = HexCoord(0, 0)
        planet.planet_type = MockPlanetType.CONTINENTAL
        return planet

    @pytest.fixture
    def mock_ship_with_ice_dwarf_pod(self):
        """Create a mock ship with an Ice Dwarf colony pod."""
        ship = MagicMock()
        ship.name = "Colony Ship Alpha"
        ship.design_data = {
            'layers': {
                'HULL': [
                    {'id': 'ice_dwarf_colony_pod'}
                ]
            }
        }
        ship.is_combat_capable = MagicMock(return_value=True)
        return ship

    @pytest.fixture
    def mock_ship_with_continental_pod(self):
        """Create a mock ship with a Continental colony pod."""
        ship = MagicMock()
        ship.name = "Colony Ship Beta"
        ship.design_data = {
            'layers': {
                'HULL': [
                    {'id': 'continental_colony_pod'}
                ]
            }
        }
        ship.is_combat_capable = MagicMock(return_value=True)
        return ship

    @pytest.fixture
    def mock_ship_without_pod(self):
        """Create a mock ship without any colony pod."""
        ship = MagicMock()
        ship.name = "Combat Ship"
        ship.design_data = {
            'layers': {
                'HULL': [
                    {'id': 'basic_engine'},
                    {'id': 'laser_cannon'}
                ]
            }
        }
        ship.is_combat_capable = MagicMock(return_value=True)
        return ship

    @pytest.fixture
    def mock_component_registry(self):
        """Create a mock component registry with colony pod components."""
        registry = {
            'ice_dwarf_colony_pod': {
                'id': 'ice_dwarf_colony_pod',
                'abilities': {'ColonizePlanet': 'ICE_DWARF'}
            },
            'continental_colony_pod': {
                'id': 'continental_colony_pod',
                'abilities': {'ColonizePlanet': 'CONTINENTAL'}
            },
            'basic_engine': {
                'id': 'basic_engine',
                'abilities': {}
            },
            'laser_cannon': {
                'id': 'laser_cannon',
                'abilities': {}
            },
        }
        return registry

    def test_validate_requires_matching_colony_pod(
        self, mock_galaxy, mock_planet_ice_dwarf, mock_ship_with_continental_pod, mock_component_registry
    ):
        """Validation fails when fleet has wrong type of colony pod."""
        from game.strategy.validation import ColonizeValidator

        # Fleet with Continental pod trying to colonize Ice Dwarf planet
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

        assert result.is_valid is False
        assert result.error_code == "NO_COLONY_POD"

    def test_validate_accepts_matching_colony_pod(
        self, mock_galaxy, mock_planet_ice_dwarf, mock_ship_with_ice_dwarf_pod, mock_component_registry
    ):
        """Validation passes when fleet has matching colony pod."""
        from game.strategy.validation import ColonizeValidator

        # Fleet with Ice Dwarf pod colonizing Ice Dwarf planet
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
        """Should correctly count available colony pods by type."""
        from game.strategy.validation import ColonizeValidator

        fleet = MagicMock()
        fleet.ships = [mock_ship_with_ice_dwarf_pod, mock_ship_with_continental_pod]

        result = ColonizeValidator.get_available_colony_pods(fleet, mock_component_registry)

        assert result == {"ICE_DWARF": 1, "CONTINENTAL": 1}

    def test_get_available_colony_pods_multiple_same_type(
        self, mock_ship_with_ice_dwarf_pod, mock_component_registry
    ):
        """Should count multiple pods of the same type."""
        from game.strategy.validation import ColonizeValidator

        # Create another ice dwarf ship
        ship2 = MagicMock()
        ship2.design_data = {
            'layers': {
                'HULL': [{'id': 'ice_dwarf_colony_pod'}]
            }
        }

        fleet = MagicMock()
        fleet.ships = [mock_ship_with_ice_dwarf_pod, ship2]

        result = ColonizeValidator.get_available_colony_pods(fleet, mock_component_registry)

        assert result == {"ICE_DWARF": 2}

    def test_get_committed_colony_pods(self, mock_planet_ice_dwarf, mock_planet_continental):
        """Should correctly count committed colony pods from orders."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.fleet import OrderType

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

        assert result == {"ICE_DWARF": 2, "CONTINENTAL": 1}

    def test_validate_rejects_overcommitted_pods(
        self, mock_galaxy, mock_planet_ice_dwarf, mock_ship_with_ice_dwarf_pod, mock_component_registry
    ):
        """Cannot queue colonization when all matching pods are committed."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.fleet import OrderType

        # Create an existing colonize order for the ice dwarf pod
        existing_order = MagicMock()
        existing_order.type = OrderType.COLONIZE
        existing_order.target = mock_planet_ice_dwarf  # Committed to colonize ice dwarf

        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.ships = [mock_ship_with_ice_dwarf_pod]  # Only 1 ice dwarf pod
        fleet.orders = [existing_order]  # Already committed

        # Create a second ice dwarf planet
        another_ice_dwarf = MagicMock()
        another_ice_dwarf.name = "Frostworld 2"
        another_ice_dwarf.owner_id = None
        another_ice_dwarf.location = HexCoord(0, 0)

        from enum import Enum
        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"
        another_ice_dwarf.planet_type = MockPlanetType.ICE_DWARF

        mock_galaxy.get_planets_at_global_hex.return_value = [mock_planet_ice_dwarf, another_ice_dwarf]

        # Try to queue second colonization
        result = ColonizeValidator.validate(
            mock_galaxy, fleet, another_ice_dwarf,
            component_registry=mock_component_registry
        )

        assert result.is_valid is False
        assert result.error_code == "COLONY_POD_EXHAUSTED"

    def test_validate_allows_different_pod_types_independently(
        self, mock_galaxy, mock_planet_continental, mock_ship_with_ice_dwarf_pod,
        mock_ship_with_continental_pod, mock_component_registry
    ):
        """Different pod types are tracked independently."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.fleet import OrderType

        # Create an ice dwarf planet that's already targeted
        ice_dwarf_planet = MagicMock()
        ice_dwarf_planet.name = "Frostworld"
        ice_dwarf_planet.owner_id = None
        ice_dwarf_planet.location = HexCoord(0, 0)

        from enum import Enum
        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"
        ice_dwarf_planet.planet_type = MockPlanetType.ICE_DWARF

        # Existing order for ice dwarf
        existing_order = MagicMock()
        existing_order.type = OrderType.COLONIZE
        existing_order.target = ice_dwarf_planet

        fleet = MagicMock()
        fleet.id = 1
        fleet.owner_id = 0
        fleet.location = HexCoord(0, 0)
        fleet.ships = [mock_ship_with_ice_dwarf_pod, mock_ship_with_continental_pod]
        fleet.orders = [existing_order]  # Ice dwarf pod committed

        mock_galaxy.get_planets_at_global_hex.return_value = [ice_dwarf_planet, mock_planet_continental]

        # Should still be able to colonize continental (different pod type)
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
        from enum import Enum

        class MockPlanetType(Enum):
            DYSON_SPHERE = "DYSON_SPHERE"

        # Create a Dyson Sphere at center (0,0) with zone extending to fleet hex (2,0)
        mock_dyson = MagicMock()
        mock_dyson.name = "Dyson Sphere"
        mock_dyson.owner_id = None
        mock_dyson.location = HexCoord(0, 0)
        mock_dyson.planet_type = MockPlanetType.DYSON_SPHERE
        mock_dyson.diameter_hexes = 11.0  # Multi-hex zone

        # Fleet is at zone hex (2, 0), not at center
        mock_fleet.location = HexCoord(2, 0)

        # get_planets_at_global_hex returns empty (Dyson center is not at fleet location)
        mock_galaxy.get_planets_at_global_hex.return_value = []

        # Zone registry returns the Dyson Sphere
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

        # Standard case: planet found at fleet location
        mock_galaxy.get_planets_at_global_hex.return_value = [mock_dyson]
        mock_galaxy.get_zones_at_global_hex = MagicMock(return_value=[])

        result = ColonizeValidator.validate(mock_galaxy, mock_fleet, mock_dyson)

        assert result.is_valid is True

    def test_validate_colonize_normal_planet_unchanged(self, mock_galaxy, mock_fleet):
        """Normal planets (no zone) work without zone lookup."""
        from game.strategy.validation import ColonizeValidator

        mock_planet = MagicMock()
        mock_planet.name = "Normal Planet"
        mock_planet.owner_id = None
        mock_planet.location = HexCoord(0, 0)

        mock_fleet.location = HexCoord(0, 0)
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
        fleet.orders = []
        return fleet

    @pytest.fixture
    def mock_component_registry(self):
        """Create a mock component registry with colony pod components."""
        return {
            'ice_dwarf_colony_pod': {
                'id': 'ice_dwarf_colony_pod',
                'abilities': {'ColonizePlanet': 'ICE_DWARF'}
            },
            'continental_colony_pod': {
                'id': 'continental_colony_pod',
                'abilities': {'ColonizePlanet': 'CONTINENTAL'}
            },
        }

    def _make_planet(self, planet_type_name: str, name: str = "Test Planet"):
        """Create a mock planet of the given type."""
        from enum import Enum

        class MockPlanetType(Enum):
            ICE_DWARF = "ICE_DWARF"
            CONTINENTAL = "CONTINENTAL"

        planet = MagicMock()
        planet.name = name
        planet.owner_id = None
        planet.location = HexCoord(0, 0)
        planet.planet_type = MockPlanetType[planet_type_name]
        return planet

    def _make_ship_with_pod(self, pod_type: str):
        """Create a mock ship with a specific colony pod type."""
        ship = MagicMock()
        ship.name = f"{pod_type} Colony Ship"
        pod_id = f"{pod_type.lower()}_colony_pod"
        ship.design_data = {
            'layers': {
                'HULL': [{'id': pod_id}]
            }
        }
        return ship

    def test_any_planet_with_registry_no_matching_pod_fails(
        self, mock_galaxy, mock_fleet, mock_component_registry
    ):
        """Any Planet with registry fails if no pod matches any candidate."""
        from game.strategy.validation import ColonizeValidator

        # Fleet has CONTINENTAL pod
        mock_fleet.ships = [self._make_ship_with_pod("CONTINENTAL")]

        # Only ICE_DWARF planets available
        ice_dwarf_planet = self._make_planet("ICE_DWARF", "Frostworld")
        mock_galaxy.get_planets_at_global_hex.return_value = [ice_dwarf_planet]

        result = ColonizeValidator.validate(
            mock_galaxy, mock_fleet, None,  # None = "Any Planet"
            component_registry=mock_component_registry
        )

        assert result.is_valid is False
        assert result.error_code == "NO_COLONY_POD"

    def test_any_planet_with_registry_matching_pod_succeeds(
        self, mock_galaxy, mock_fleet, mock_component_registry
    ):
        """Any Planet with registry succeeds if a pod matches a candidate."""
        from game.strategy.validation import ColonizeValidator

        # Fleet has ICE_DWARF pod
        mock_fleet.ships = [self._make_ship_with_pod("ICE_DWARF")]

        # ICE_DWARF planet available
        ice_dwarf_planet = self._make_planet("ICE_DWARF", "Frostworld")
        mock_galaxy.get_planets_at_global_hex.return_value = [ice_dwarf_planet]

        result = ColonizeValidator.validate(
            mock_galaxy, mock_fleet, None,  # None = "Any Planet"
            component_registry=mock_component_registry
        )

        assert result.is_valid is True

    def test_any_planet_without_registry_skips_pod_check(
        self, mock_galaxy, mock_fleet
    ):
        """Any Planet without registry skips pod check (backward compat)."""
        from game.strategy.validation import ColonizeValidator

        # Fleet has no ships (would fail pod check if it ran)
        mock_fleet.ships = []

        # ICE_DWARF planet available
        ice_dwarf_planet = self._make_planet("ICE_DWARF", "Frostworld")
        mock_galaxy.get_planets_at_global_hex.return_value = [ice_dwarf_planet]

        result = ColonizeValidator.validate(
            mock_galaxy, mock_fleet, None,  # None = "Any Planet"
            component_registry=None  # No registry = skip pod check
        )

        assert result.is_valid is True

    def test_any_planet_with_registry_exhausted_pods_fails(
        self, mock_galaxy, mock_fleet, mock_component_registry
    ):
        """Any Planet fails if all matching pods are already committed."""
        from game.strategy.validation import ColonizeValidator
        from game.strategy.data.fleet import OrderType

        # Fleet has one ICE_DWARF pod
        mock_fleet.ships = [self._make_ship_with_pod("ICE_DWARF")]

        # ICE_DWARF planet 1 (already targeted by existing order)
        ice_dwarf_1 = self._make_planet("ICE_DWARF", "Frostworld 1")

        # ICE_DWARF planet 2 (another candidate)
        ice_dwarf_2 = self._make_planet("ICE_DWARF", "Frostworld 2")

        # Existing order commits the only ICE_DWARF pod
        existing_order = MagicMock()
        existing_order.type = OrderType.COLONIZE
        existing_order.target = ice_dwarf_1
        mock_fleet.orders = [existing_order]

        mock_galaxy.get_planets_at_global_hex.return_value = [ice_dwarf_1, ice_dwarf_2]

        result = ColonizeValidator.validate(
            mock_galaxy, mock_fleet, None,  # None = "Any Planet"
            component_registry=mock_component_registry
        )

        assert result.is_valid is False
        # Could be either error code depending on implementation
        assert result.error_code in ("NO_COLONY_POD", "COLONY_POD_EXHAUSTED")
