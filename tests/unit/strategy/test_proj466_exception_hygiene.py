"""PROJ-466 Phase 2/3: domain-exception hygiene regression tests.

Each target site previously raised a generic builtin (TypeError, ValueError,
RuntimeError, NotImplementedError) at a validation/persistence/dependency
boundary. These tests assert the swap to the correct domain exception with the
expected ErrorCode, so a regression back to a bare builtin fails loudly.
"""
from __future__ import annotations

import pytest

from game.core.error_codes import ErrorCode
from game.core.exceptions import (
    PersistenceException,
    StateException,
    ValidationException,
)


# ---------------------------------------------------------------------------
# Task 2.1: replay_serialization boundary functions
# ---------------------------------------------------------------------------


class TestReplaySerializationBoundaries:
    def test_boundary_to_dict_unknown_subtype_raises_persistence(self):
        from game.simulation.replay.replay_serialization import boundary_to_dict

        class WeirdBoundary:
            pass

        with pytest.raises(PersistenceException) as ei:
            boundary_to_dict(WeirdBoundary())  # type: ignore[arg-type]
        assert ei.value.code == ErrorCode.CORRUPT_DATA.value

    def test_boundary_from_dict_unknown_type_raises_persistence(self):
        from game.simulation.replay.replay_serialization import boundary_from_dict

        with pytest.raises(PersistenceException) as ei:
            boundary_from_dict({"type": "hyperbolic", "exit_policy": "none"})
        assert ei.value.code == ErrorCode.CORRUPT_DATA.value


# ---------------------------------------------------------------------------
# Task 2.3: planetary_facility resource validation
# ---------------------------------------------------------------------------


class TestPlanetaryFacilityResourceValidation:
    def test_unknown_resource_id_raises_validation(self):
        from game.strategy.data.planetary_facility import PlanetaryFacility

        facility = PlanetaryFacility.__new__(PlanetaryFacility)
        with pytest.raises(ValidationException) as ei:
            facility._validate_resource_id("definitely_not_a_resource")
        assert ei.value.code == ErrorCode.RESOURCE_NOT_FOUND.value


# ---------------------------------------------------------------------------
# Task 2.4: ship_stats_cache missing registries
# ---------------------------------------------------------------------------


class TestShipStatsCacheMissingRegistries:
    def test_calculate_without_registries_raises_validation(self):
        from types import SimpleNamespace

        from game.strategy.data.ship_stats_cache import ShipStatsCache

        ship = SimpleNamespace(_registries=None)
        with pytest.raises(ValidationException) as ei:
            ShipStatsCache.calculate(ship)  # type: ignore[arg-type]
        assert ei.value.code == ErrorCode.MISSING_DEPENDENCY.value


# ---------------------------------------------------------------------------
# Task 2.5: fleet_capability_calculator missing registry (2 sites)
# ---------------------------------------------------------------------------


class TestFleetCapabilityMissingRegistry:
    def test_ship_has_spaceyard_without_registry_raises_validation(self):
        from types import SimpleNamespace

        from game.strategy.data.fleet_capability_calculator import (
            FleetCapabilityCalculator,
        )

        ship = SimpleNamespace(_registries=None)
        with pytest.raises(ValidationException) as ei:
            FleetCapabilityCalculator.ship_has_spaceyard(ship, None)
        assert ei.value.code == ErrorCode.MISSING_DEPENDENCY.value

    def test_get_registry_without_registry_raises_validation(self):
        from game.strategy.data.fleet_capability_calculator import (
            FleetCapabilityCalculator,
        )

        class FakeFleet:
            def get_combat_capable_ships(self):
                return []

        calc = FleetCapabilityCalculator(FakeFleet(), component_registry=None)
        with pytest.raises(ValidationException) as ei:
            calc._get_registry()
        assert ei.value.code == ErrorCode.MISSING_DEPENDENCY.value


# ---------------------------------------------------------------------------
# Task 3.2: fleet_write_service NotImplementedError -> ValidationException
# (lives here so all hygiene swaps are in one focused module)
# ---------------------------------------------------------------------------


class TestFleetWriteServiceUnsupported:
    def test_set_location_raises_validation_not_notimplemented(self):
        from game.strategy.services.fleet_write_service import FleetWriteService

        svc = FleetWriteService()
        with pytest.raises(ValidationException):
            svc.set_location(object(), object())

    def test_set_path_raises_validation_not_notimplemented(self):
        from game.strategy.services.fleet_write_service import FleetWriteService

        svc = FleetWriteService()
        with pytest.raises(ValidationException):
            svc.set_path(object(), object())


# ---------------------------------------------------------------------------
# Task 3.1: component_activation_state domain exceptions
# ---------------------------------------------------------------------------


class TestComponentActivationStateExceptions:
    def test_from_dict_missing_phase_raises_persistence(self):
        from game.strategy.data.component_activation_state import (
            ComponentActivationState,
        )

        with pytest.raises(PersistenceException) as ei:
            ComponentActivationState.from_dict({})
        assert ei.value.code == ErrorCode.CORRUPT_DATA.value

    def test_start_activating_from_wrong_phase_raises_state(self):
        from game.strategy.data.component_activation_state import (
            ActivationPhase,
            ComponentActivationState,
        )

        state = ComponentActivationState(phase=ActivationPhase.ACTIVE)
        with pytest.raises(StateException):
            state.start_activating(required_ticks=5, energy_drain_rate=1.0)

    def test_start_deactivating_from_wrong_phase_raises_state(self):
        from game.strategy.data.component_activation_state import (
            ActivationPhase,
            ComponentActivationState,
        )

        state = ComponentActivationState(phase=ActivationPhase.INACTIVE)
        with pytest.raises(StateException):
            state.start_deactivating(required_ticks=5)
