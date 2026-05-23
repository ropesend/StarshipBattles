"""Tests for BaseCommandHandler resolution methods.

PROJ-176 Phase 2: Unit tests for fleet/planet resolution helpers.
PROJ-381 Phase 3 (ERR-01-003): updated to expect ValidationException
instead of ValueError; also asserts on the error `code` field.
"""
import pytest
from unittest.mock import Mock, MagicMock

from game.core.error_codes import ErrorCode
from game.core.exceptions import ValidationException
from game.strategy.engine.handlers import BaseCommandHandler


class TestFindShip:
    """DUP-X-7 (PROJ-465): shared `_find_ship` on BaseCommandHandler."""

    def test_find_ship_matches_by_str_instance_id(self):
        ship_a = Mock()
        ship_a.instance_id = 7
        ship_b = Mock()
        ship_b.instance_id = "abc"
        fleet = Mock()
        fleet.ships = [ship_a, ship_b]

        assert BaseCommandHandler._find_ship(fleet, "7") is ship_a
        assert BaseCommandHandler._find_ship(fleet, 7) is ship_a
        assert BaseCommandHandler._find_ship(fleet, "abc") is ship_b
        assert BaseCommandHandler._find_ship(fleet, "missing") is None

    def test_find_ship_returns_first_match(self):
        ship_a = Mock()
        ship_a.instance_id = "x"
        ship_b = Mock()
        ship_b.instance_id = "x"
        fleet = Mock()
        fleet.ships = [ship_a, ship_b]
        assert BaseCommandHandler._find_ship(fleet, "x") is ship_a


class TestResolveFleet:
    """Tests for BaseCommandHandler._resolve_fleet().

    PROJ-495 T3.20: parametrized the 2 negative-result tests on
    ``(session_setup, resolve_kwargs, expected_substring)``. The two
    cases (no fleet vs wrong-owner fleet) share the same assertion
    shape (returns None, error.is_valid False, substring in
    error.errors[0]).
    """

    @staticmethod
    def _session_no_fleet() -> Mock:
        session = Mock()
        session._get_fleet_by_id.return_value = None
        return session

    @staticmethod
    def _session_wrong_owner() -> Mock:
        session = Mock()
        mock_fleet = Mock()
        mock_fleet.owner_id = 1
        session._get_fleet_by_id.return_value = mock_fleet
        return session

    @pytest.mark.parametrize(
        "session_factory,resolve_kwargs,expected_substring",
        [
            (_session_no_fleet, {"fleet_id": 999}, "Fleet not found"),
            (
                _session_wrong_owner,
                {"fleet_id": 100, "empire_id": 2},
                "does not belong",
            ),
        ],
        ids=["fleet_not_found", "wrong_owner"],
    )
    def test_resolve_fleet_negative_paths(
        self, session_factory, resolve_kwargs, expected_substring
    ):
        """Returns (None, error) with the expected message substring."""
        session = session_factory()

        fleet, error = BaseCommandHandler._resolve_fleet(session, **resolve_kwargs)

        assert fleet is None
        assert error is not None
        assert not error.is_valid
        assert expected_substring in error.errors[0]

    def test_resolve_fleet_success(self):
        """Returns fleet when found and owner matches."""
        session = Mock()
        mock_fleet = Mock()
        mock_fleet.owner_id = 1
        session._get_fleet_by_id.return_value = mock_fleet

        fleet, error = BaseCommandHandler._resolve_fleet(session, fleet_id=100, empire_id=1)

        assert fleet is mock_fleet
        assert error is None


class TestResolveFleetRequired:
    """Tests for BaseCommandHandler._resolve_fleet_required()."""

    def test_resolve_fleet_required_success(self):
        """Returns fleet when found and ownership matches."""
        session = Mock()
        mock_fleet = Mock()
        mock_fleet.owner_id = 1
        session._get_fleet_by_id.return_value = mock_fleet

        fleet = BaseCommandHandler._resolve_fleet_required(
            session, fleet_id=100, empire_id=1
        )

        assert fleet is mock_fleet

    def test_resolve_fleet_required_not_found_raises(self):
        """Raises ValidationException(MISSING_ENTITY) when fleet does not exist."""
        session = Mock()
        session._get_fleet_by_id.return_value = None

        with pytest.raises(ValidationException, match="Fleet not found") as exc:
            BaseCommandHandler._resolve_fleet_required(session, fleet_id=999)
        assert exc.value.code == ErrorCode.MISSING_ENTITY.value
        assert exc.value.context.get("fleet_id") == 999

    def test_resolve_fleet_required_wrong_owner_raises(self):
        """Raises ValidationException(OWNERSHIP_MISMATCH) on owner mismatch."""
        session = Mock()
        mock_fleet = Mock()
        mock_fleet.owner_id = 1
        session._get_fleet_by_id.return_value = mock_fleet

        with pytest.raises(ValidationException, match="does not belong") as exc:
            BaseCommandHandler._resolve_fleet_required(
                session, fleet_id=100, empire_id=2
            )
        assert exc.value.code == ErrorCode.OWNERSHIP_MISMATCH.value
        assert exc.value.context.get("fleet_id") == 100
        assert exc.value.context.get("empire_id") == 2

    def test_resolve_fleet_success_no_owner_check(self):
        """Returns fleet when found without owner validation."""
        session = Mock()
        mock_fleet = Mock()
        mock_fleet.owner_id = 1
        session._get_fleet_by_id.return_value = mock_fleet

        fleet, error = BaseCommandHandler._resolve_fleet(session, fleet_id=100)

        assert fleet is mock_fleet
        assert error is None


class TestResolvePlanet:
    """Tests for BaseCommandHandler._resolve_planet()."""

    def test_resolve_planet_not_found(self):
        """Returns error when planet doesn't exist."""
        session = Mock()
        session._get_planet_by_id.return_value = None

        planet, error = BaseCommandHandler._resolve_planet(session, planet_id=999)

        assert planet is None
        assert error is not None
        assert not error.is_valid
        assert "Planet not found" in error.errors[0]

    def test_resolve_planet_success(self):
        """Returns planet when found."""
        session = Mock()
        mock_planet = Mock()
        session._get_planet_by_id.return_value = mock_planet

        planet, error = BaseCommandHandler._resolve_planet(session, planet_id=100)

        assert planet is mock_planet
        assert error is None


class TestResolvePlayerPlanet:
    """PROJ-375 Task 2.2: tests for BaseCommandHandler._resolve_player_planet()."""

    def test_no_active_empire_returns_error(self):
        session = Mock()
        session.active_empire = None

        planet, error = BaseCommandHandler._resolve_player_planet(session, planet_id=1)

        assert planet is None
        assert error is not None
        assert not error.is_valid
        assert "No active empire" in error.errors[0]

    def test_planet_not_found_returns_error(self):
        session = Mock()
        active = Mock()
        active.id = 7
        session.active_empire = active
        session._get_planet_by_id.return_value = None

        planet, error = BaseCommandHandler._resolve_player_planet(session, planet_id=999)

        assert planet is None
        assert error is not None
        assert "Planet not found" in error.errors[0]

    def test_planet_owned_by_other_empire_returns_error(self):
        session = Mock()
        active = Mock()
        active.id = 7
        session.active_empire = active
        mock_planet = Mock()
        mock_planet.owner_id = 99
        session._get_planet_by_id.return_value = mock_planet

        planet, error = BaseCommandHandler._resolve_player_planet(session, planet_id=10)

        assert planet is None
        assert error is not None
        assert "does not belong" in error.errors[0]

    def test_success_returns_planet(self):
        session = Mock()
        active = Mock()
        active.id = 7
        session.active_empire = active
        mock_planet = Mock()
        mock_planet.owner_id = 7
        session._get_planet_by_id.return_value = mock_planet

        planet, error = BaseCommandHandler._resolve_player_planet(session, planet_id=10)

        assert planet is mock_planet
        assert error is None


class TestResolvePlanetOptional:
    """Tests for BaseCommandHandler._resolve_planet_optional()."""

    def test_resolve_planet_optional_returns_planet_when_found(self):
        """Returns planet when lookup succeeds."""
        session = Mock()
        mock_planet = Mock()
        session._get_planet_by_id.return_value = mock_planet

        planet = BaseCommandHandler._resolve_planet_optional(session, planet_id=100)

        assert planet is mock_planet

    def test_resolve_planet_optional_required_false_returns_none(self):
        """Returns None for missing optional planets."""
        session = Mock()
        session._get_planet_by_id.return_value = None

        planet = BaseCommandHandler._resolve_planet_optional(
            session, planet_id=999, required=False
        )

        assert planet is None

    def test_resolve_planet_optional_required_true_raises(self):
        """Raises ValidationException(MISSING_ENTITY) for missing required planets."""
        session = Mock()
        session._get_planet_by_id.return_value = None

        with pytest.raises(ValidationException, match="Planet not found") as exc:
            BaseCommandHandler._resolve_planet_optional(
                session, planet_id=999, required=True
            )
        assert exc.value.code == ErrorCode.MISSING_ENTITY.value
        assert exc.value.context.get("planet_id") == 999


class TestResolveBuildEntity:
    """Tests for BaseCommandHandler._resolve_build_entity()."""

    def test_resolve_build_entity_planet(self):
        """Resolves planet entities through the planet lookup."""
        session = Mock()
        mock_planet = Mock()
        session._get_planet_by_id.return_value = mock_planet

        entity = BaseCommandHandler._resolve_build_entity(
            session, entity_id=10, entity_type="planet"
        )

        assert entity is mock_planet

    def test_resolve_build_entity_fleet(self):
        """Resolves fleet entities through the fleet lookup."""
        session = Mock()
        mock_fleet = Mock()
        session._get_fleet_by_id.return_value = mock_fleet

        entity = BaseCommandHandler._resolve_build_entity(
            session, entity_id=20, entity_type="fleet"
        )

        assert entity is mock_fleet

    def test_resolve_build_entity_unknown_type_returns_none(self):
        """Unknown build entity types do not resolve."""
        session = Mock()

        entity = BaseCommandHandler._resolve_build_entity(
            session, entity_id=20, entity_type="station"
        )

        assert entity is None


class TestResolveQueue:
    """Tests for construction queue resolution helpers."""

    def test_resolve_queue_none_uses_entity_main_queue(self):
        """No queue id resolves to the entity construction queue."""
        entity = Mock()
        entity.construction_queue = ["base"]

        queue = BaseCommandHandler._resolve_queue(entity, queue_id=None)

        assert queue is entity.construction_queue

    def test_resolve_queue_facility_instance_id_uses_facility_queue(self):
        """Facility queue ids resolve to the matching facility queue."""
        facility = Mock()
        facility.instance_id = "yard-1"
        facility.construction_queue = ["facility"]
        entity = Mock()
        entity.id = 5
        entity.facilities = [facility]
        entity.construction_queue = ["base"]

        queue = BaseCommandHandler._resolve_queue(entity, queue_id="yard-1")

        assert queue is facility.construction_queue

    def test_resolve_queue_base_pattern_uses_entity_queue(self):
        """Planet base queue ids resolve to the entity construction queue."""
        entity = Mock()
        entity.id = 5
        entity.facilities = []
        entity.construction_queue = ["base"]

        queue = BaseCommandHandler._resolve_queue(
            entity, queue_id="planet_5_base"
        )

        assert queue is entity.construction_queue

    def test_resolve_queue_unknown_id_falls_back_to_main_queue(self):
        """Queue lookup remains backward-compatible for unknown queue ids."""
        entity = Mock()
        entity.id = 5
        entity.facilities = []
        entity.construction_queue = ["base"]

        queue = BaseCommandHandler._resolve_queue(entity, queue_id="missing")

        assert queue is entity.construction_queue


class TestResolveQueueOwner:
    """Tests for queue owner resolution."""

    def test_resolve_queue_owner_none_returns_entity(self):
        """No queue id is owned by the entity."""
        entity = Mock()

        owner = BaseCommandHandler._resolve_queue_owner(entity, queue_id=None)

        assert owner is entity

    def test_resolve_queue_owner_facility_instance_id_returns_facility(self):
        """Facility queue ids are owned by the matching facility."""
        facility = Mock()
        facility.instance_id = "yard-1"
        entity = Mock()
        entity.id = 5
        entity.facilities = [facility]

        owner = BaseCommandHandler._resolve_queue_owner(entity, queue_id="yard-1")

        assert owner is facility

    def test_resolve_queue_owner_base_pattern_returns_entity(self):
        """Planet base queue ids are owned by the planet."""
        entity = Mock()
        entity.id = 5
        entity.facilities = []

        owner = BaseCommandHandler._resolve_queue_owner(
            entity, queue_id="planet_5_base"
        )

        assert owner is entity

    def test_resolve_queue_owner_fleet_yard_pattern_returns_fleet(self):
        """Fleet yard queue ids are owned by the fleet."""
        entity = Mock()
        entity.id = 7
        entity.facilities = []

        owner = BaseCommandHandler._resolve_queue_owner(
            entity, queue_id="fleet_7_yard_0"
        )

        assert owner is entity

    def test_resolve_queue_owner_unknown_id_returns_none(self):
        """Unknown queue owners are reported as missing."""
        entity = Mock()
        entity.id = 5
        entity.facilities = []

        owner = BaseCommandHandler._resolve_queue_owner(entity, queue_id="missing")

        assert owner is None


class TestBuildColonizeTarget:
    """Tests for BaseCommandHandler._build_colonize_target()."""

    def test_build_colonize_target_returns_planet_without_transfer_amounts(self):
        """Plain colonize commands keep the planet target shape."""
        planet = Mock()
        cmd = Mock()
        cmd.population_amount = None
        cmd.cargo_amounts = None

        target = BaseCommandHandler._build_colonize_target(planet, cmd)

        assert target is planet

    def test_build_colonize_target_wraps_population_and_cargo_amounts(self):
        """Population/cargo transfer requests are carried in the order target."""
        planet = Mock()
        cmd = Mock()
        cmd.population_amount = 25
        cmd.cargo_amounts = {"metals": 10}

        target = BaseCommandHandler._build_colonize_target(planet, cmd)

        assert target == {
            "planet": planet,
            "population": 25,
            "cargo": {"metals": 10},
        }
