"""
Tests for planet command handlers.

PROJ-264 Phase 1: Coverage for ClearPlanetOrdersCommandHandler,
DeletePlanetOrderCommandHandler, SetAtmosphereTargetCommandHandler.

PROJ-438 Phase 5: ``IssuePlanetOrderCommandHandler`` retired. Coverage
now lives on the typed ``ActivatePlanetAbilityCommandHandler`` /
``DeactivatePlanetAbilityCommandHandler`` test classes below.
"""

import pytest
from unittest.mock import MagicMock, patch

from game.core.validation import ValidationResult
from game.strategy.data.order_types import OrderType


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_session():
    """Create a mock GameSession with planet resolution support."""
    session = MagicMock()
    session.active_empire = MagicMock()
    session.active_empire.id = 0
    session.registries = MagicMock()
    session.registries.components = {}
    # Default: planet not found
    session._get_planet_by_id = MagicMock(return_value=None)
    return session


@pytest.fixture
def mock_planet():
    """Create a mock planet owned by player empire."""
    planet = MagicMock()
    planet.id = 100
    planet.name = "Test Colony"
    planet.owner_id = 0
    planet.orders = []
    planet.add_order = MagicMock()
    planet.clear_orders = MagicMock()
    planet.atmosphere_target = {}
    return planet


def _session_with_planet(session, planet):
    """Configure session so _resolve_planet finds the given planet."""
    session._get_planet_by_id = MagicMock(return_value=planet)


# =============================================================================
# Parametrized planet_not_found + wrong_owner (PROJ-479 Task 1.17)
# =============================================================================
#
# Every PlanetCommandHandler subclass returns an "is_valid=False" result
# when (a) the planet cannot be resolved, or (b) the resolved planet is
# owned by another empire. Rather than duplicate the same two tests in
# each of the 8 handler classes, the cases are enumerated here and run as
# a single parametrized matrix. Per-handler success / validation tests
# remain in the individual classes because they carry handler-specific
# assertions.


def _activate_cmd_factory():
    return _activate_cmd()


def _deactivate_cmd_factory():
    return _deactivate_cmd()


def _planet_id_only_cmd_factory():
    cmd = MagicMock()
    cmd.planet_id = 100
    return cmd


def _delete_order_cmd_factory():
    cmd = MagicMock()
    cmd.planet_id = 100
    cmd.order_index = 0
    return cmd


def _atmosphere_cmd_factory():
    cmd = MagicMock()
    cmd.planet_id = 100
    cmd.atmosphere_target = {'O2': 0.21}
    return cmd


def _gravity_cmd_factory():
    cmd = MagicMock()
    cmd.planet_id = 100
    cmd.gravity_target = 5.0
    return cmd


def _water_cmd_factory():
    cmd = MagicMock()
    cmd.planet_id = 100
    cmd.water_target = 0.5
    return cmd


def _radiation_cmd_factory():
    cmd = MagicMock()
    cmd.planet_id = 100
    cmd.shielding_target = 1.0
    return cmd


_HANDLER_CASES = [
    ("ActivatePlanetAbilityCommandHandler", _activate_cmd_factory),
    ("DeactivatePlanetAbilityCommandHandler", _deactivate_cmd_factory),
    ("ClearPlanetOrdersCommandHandler", _planet_id_only_cmd_factory),
    ("DeletePlanetOrderCommandHandler", _delete_order_cmd_factory),
    ("SetAtmosphereTargetCommandHandler", _atmosphere_cmd_factory),
    ("SetGravityTargetCommandHandler", _gravity_cmd_factory),
    ("SetWaterTargetCommandHandler", _water_cmd_factory),
    ("SetRadiationShieldTargetCommandHandler", _radiation_cmd_factory),
]


@pytest.mark.parametrize(
    "handler_name,cmd_factory",
    _HANDLER_CASES,
    ids=[h[0] for h in _HANDLER_CASES],
)
def test_planet_not_found_returns_invalid(handler_name, cmd_factory, mock_session):
    """Every planet command handler returns is_valid=False when the
    target planet cannot be resolved (PROJ-479 Task 1.17 consolidation)."""
    from game.strategy.engine import planet_command_handlers as _mod

    handler_cls = getattr(_mod, handler_name)
    result = handler_cls().execute(mock_session, cmd_factory())
    assert not result.is_valid


@pytest.mark.parametrize(
    "handler_name,cmd_factory",
    _HANDLER_CASES,
    ids=[h[0] for h in _HANDLER_CASES],
)
def test_wrong_owner_returns_invalid(
    handler_name, cmd_factory, mock_session, mock_planet
):
    """Every planet command handler returns is_valid=False when the
    resolved planet is owned by a different empire (PROJ-479 Task 1.17
    consolidation)."""
    from game.strategy.engine import planet_command_handlers as _mod

    mock_planet.owner_id = 99
    _session_with_planet(mock_session, mock_planet)
    handler_cls = getattr(_mod, handler_name)
    result = handler_cls().execute(mock_session, cmd_factory())
    assert not result.is_valid


# =============================================================================
# ActivatePlanetAbilityCommandHandler Tests (PROJ-438 Phase 5)
# =============================================================================


def _activate_cmd(**overrides):
    from game.strategy.engine.commands import ActivatePlanetAbilityCommand
    return ActivatePlanetAbilityCommand(
        planet_id=overrides.get('planet_id', 100),
        facility_instance_id=overrides.get('facility_instance_id', 'fac-1'),
        ability_name=overrides.get('ability_name', 'PlanetaryShield'),
        component_key=overrides.get('component_key', 'CORE:0:shield_gen'),
    )


def _deactivate_cmd(**overrides):
    from game.strategy.engine.commands import DeactivatePlanetAbilityCommand
    return DeactivatePlanetAbilityCommand(
        planet_id=overrides.get('planet_id', 100),
        facility_instance_id=overrides.get('facility_instance_id', 'fac-1'),
        ability_name=overrides.get('ability_name', 'PlanetaryShield'),
        component_key=overrides.get('component_key', 'CORE:0:shield_gen'),
    )


class TestActivatePlanetAbilityCommandHandler:
    """Tests for ActivatePlanetAbilityCommandHandler.execute() (Phase 5)."""

    # test_planet_not_found + test_wrong_owner now run under the
    # parametrized matrix at module scope (PROJ-479 Task 1.17). The
    # ActivatePlanetAbility-specific message-substring assertions
    # ("not found" / "does not belong") are preserved here as a
    # narrower companion test so the message contract is still pinned.
    def test_planet_not_found_message(self, mock_session):
        from game.strategy.engine.planet_command_handlers import (
            ActivatePlanetAbilityCommandHandler,
        )

        result = ActivatePlanetAbilityCommandHandler().execute(
            mock_session, _activate_cmd()
        )
        assert "not found" in result.message.lower()

    def test_wrong_owner_message(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import (
            ActivatePlanetAbilityCommandHandler,
        )

        mock_planet.owner_id = 99
        _session_with_planet(mock_session, mock_planet)

        result = ActivatePlanetAbilityCommandHandler().execute(
            mock_session, _activate_cmd()
        )
        assert "does not belong" in result.message.lower()

    def test_validation_failure(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import (
            ActivatePlanetAbilityCommandHandler,
        )
        from game.strategy.validation.planet_order_validator import (
            PlanetOrderValidator,
        )

        _session_with_planet(mock_session, mock_planet)

        with patch.object(
            PlanetOrderValidator,
            'validate_activate_ability',
            return_value=ValidationResult.error("Facility not found"),
        ):
            result = ActivatePlanetAbilityCommandHandler().execute(
                mock_session, _activate_cmd()
            )
        assert not result.is_valid

    def test_success_queues_activate_ability_order(
        self, mock_session, mock_planet
    ):
        from game.strategy.engine.planet_command_handlers import (
            ActivatePlanetAbilityCommandHandler,
        )
        from game.strategy.validation.planet_order_validator import (
            PlanetOrderValidator,
        )

        _session_with_planet(mock_session, mock_planet)

        with patch.object(
            PlanetOrderValidator,
            'validate_activate_ability',
            return_value=ValidationResult.success(),
        ):
            result = ActivatePlanetAbilityCommandHandler().execute(
                mock_session, _activate_cmd()
            )

        assert result.is_valid
        mock_planet.add_order.assert_called_once()
        order_arg = mock_planet.add_order.call_args[0][0]
        assert order_arg.type == OrderType.ACTIVATE_ABILITY
        assert order_arg.target['facility_instance_id'] == 'fac-1'
        assert order_arg.target['ability_name'] == 'PlanetaryShield'
        assert order_arg.target['component_key'] == 'CORE:0:shield_gen'


class TestDeactivatePlanetAbilityCommandHandler:
    """Tests for DeactivatePlanetAbilityCommandHandler.execute() (Phase 5)."""

    # See PROJ-479 Task 1.17: planet-not-found + wrong-owner moved to the
    # parametrized matrix at module scope. Message-substring assertion
    # retained below.
    def test_planet_not_found_message(self, mock_session):
        from game.strategy.engine.planet_command_handlers import (
            DeactivatePlanetAbilityCommandHandler,
        )

        result = DeactivatePlanetAbilityCommandHandler().execute(
            mock_session, _deactivate_cmd()
        )
        assert "not found" in result.message.lower()

    def test_wrong_owner_message(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import (
            DeactivatePlanetAbilityCommandHandler,
        )

        mock_planet.owner_id = 99
        _session_with_planet(mock_session, mock_planet)

        result = DeactivatePlanetAbilityCommandHandler().execute(
            mock_session, _deactivate_cmd()
        )
        assert "does not belong" in result.message.lower()

    def test_validation_failure(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import (
            DeactivatePlanetAbilityCommandHandler,
        )
        from game.strategy.validation.planet_order_validator import (
            PlanetOrderValidator,
        )

        _session_with_planet(mock_session, mock_planet)

        with patch.object(
            PlanetOrderValidator,
            'validate_deactivate_ability',
            return_value=ValidationResult.error("Facility not found"),
        ):
            result = DeactivatePlanetAbilityCommandHandler().execute(
                mock_session, _deactivate_cmd()
            )
        assert not result.is_valid

    def test_success_queues_deactivate_ability_order(
        self, mock_session, mock_planet
    ):
        from game.strategy.engine.planet_command_handlers import (
            DeactivatePlanetAbilityCommandHandler,
        )
        from game.strategy.validation.planet_order_validator import (
            PlanetOrderValidator,
        )

        _session_with_planet(mock_session, mock_planet)

        with patch.object(
            PlanetOrderValidator,
            'validate_deactivate_ability',
            return_value=ValidationResult.success(),
        ):
            result = DeactivatePlanetAbilityCommandHandler().execute(
                mock_session, _deactivate_cmd()
            )

        assert result.is_valid
        mock_planet.add_order.assert_called_once()
        order_arg = mock_planet.add_order.call_args[0][0]
        assert order_arg.type == OrderType.DEACTIVATE_ABILITY
        assert order_arg.target['facility_instance_id'] == 'fac-1'
        assert order_arg.target['ability_name'] == 'PlanetaryShield'
        assert order_arg.target['component_key'] == 'CORE:0:shield_gen'


# =============================================================================
# ClearPlanetOrdersCommandHandler Tests
# =============================================================================


class TestClearPlanetOrdersCommandHandler:
    """Tests for ClearPlanetOrdersCommandHandler.execute()."""

    def _make_cmd(self, planet_id=100):
        cmd = MagicMock()
        cmd.planet_id = planet_id
        return cmd

    # PROJ-479 Task 1.17: test_planet_not_found + test_wrong_owner moved
    # to the parametrized matrix at module scope.

    def test_success_clears_orders(self, mock_session, mock_planet):
        """Success calls planet.clear_orders()."""
        from game.strategy.engine.planet_command_handlers import ClearPlanetOrdersCommandHandler

        _session_with_planet(mock_session, mock_planet)

        handler = ClearPlanetOrdersCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())

        assert result.is_valid
        mock_planet.clear_orders.assert_called_once()


# =============================================================================
# DeletePlanetOrderCommandHandler Tests
# =============================================================================


class TestDeletePlanetOrderCommandHandler:
    """Tests for DeletePlanetOrderCommandHandler.execute()."""

    def _make_cmd(self, planet_id=100, order_index=0):
        cmd = MagicMock()
        cmd.planet_id = planet_id
        cmd.order_index = order_index
        return cmd

    # PROJ-479 Task 1.17: test_planet_not_found + test_wrong_owner moved
    # to the parametrized matrix at module scope.

    def test_index_negative(self, mock_session, mock_planet):
        """Returns error for negative index."""
        from game.strategy.engine.planet_command_handlers import DeletePlanetOrderCommandHandler

        mock_planet.orders = [MagicMock()]
        _session_with_planet(mock_session, mock_planet)

        handler = DeletePlanetOrderCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(order_index=-1))

        assert not result.is_valid
        assert "invalid" in result.message.lower()

    def test_index_out_of_range(self, mock_session, mock_planet):
        """Returns error for index >= len(orders)."""
        from game.strategy.engine.planet_command_handlers import DeletePlanetOrderCommandHandler

        mock_planet.orders = [MagicMock()]
        _session_with_planet(mock_session, mock_planet)

        handler = DeletePlanetOrderCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(order_index=5))

        assert not result.is_valid

    def test_success_removes_order(self, mock_session, mock_planet):
        """Success pops the correct order from the list."""
        from game.strategy.engine.planet_command_handlers import DeletePlanetOrderCommandHandler

        order0 = MagicMock()
        order0.type = MagicMock()
        order0.type.name = "ACTIVATE_ABILITY"
        order1 = MagicMock()
        order1.type = MagicMock()
        order1.type.name = "DEACTIVATE_ABILITY"
        mock_planet.orders = [order0, order1]
        _session_with_planet(mock_session, mock_planet)

        handler = DeletePlanetOrderCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(order_index=0))

        assert result.is_valid
        assert len(mock_planet.orders) == 1
        assert mock_planet.orders[0] is order1


# =============================================================================
# SetAtmosphereTargetCommandHandler Tests
# =============================================================================


class TestSetAtmosphereTargetCommandHandler:
    """Tests for SetAtmosphereTargetCommandHandler.execute()."""

    def _make_cmd(self, planet_id=100, atmosphere_target=None):
        cmd = MagicMock()
        cmd.planet_id = planet_id
        cmd.atmosphere_target = atmosphere_target if atmosphere_target is not None else {'O2': 0.21}
        return cmd

    # PROJ-479 Task 1.17: test_planet_not_found + test_wrong_owner moved
    # to the parametrized matrix at module scope.

    def test_success_sets_atmosphere_target(self, mock_session, mock_planet):
        """Success sets atmosphere_target on planet."""
        from game.strategy.engine.planet_command_handlers import SetAtmosphereTargetCommandHandler

        _session_with_planet(mock_session, mock_planet)
        target = {'O2': 0.21, 'N2': 0.78}

        handler = SetAtmosphereTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(atmosphere_target=target))

        assert result.is_valid
        assert mock_planet.atmosphere_target == {'O2': 0.21, 'N2': 0.78}

    def test_success_clear_atmosphere_target(self, mock_session, mock_planet):
        """Empty dict clears atmosphere target."""
        from game.strategy.engine.planet_command_handlers import SetAtmosphereTargetCommandHandler

        mock_planet.atmosphere_target = {'O2': 0.21}
        _session_with_planet(mock_session, mock_planet)

        handler = SetAtmosphereTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(atmosphere_target={}))

        assert result.is_valid
        assert mock_planet.atmosphere_target == {}


# =============================================================================
# SetGravityTargetCommandHandler Tests
# =============================================================================


class TestSetGravityTargetCommandHandler:
    """Tests for SetGravityTargetCommandHandler.execute()."""

    def _make_cmd(self, planet_id=100, gravity_target=5.0):
        cmd = MagicMock()
        cmd.planet_id = planet_id
        cmd.gravity_target = gravity_target
        return cmd

    # PROJ-479 Task 1.17: test_planet_not_found + test_wrong_owner moved
    # to the parametrized matrix at module scope.

    def test_success_sets_gravity_target(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import SetGravityTargetCommandHandler
        _session_with_planet(mock_session, mock_planet)
        handler = SetGravityTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(gravity_target=5.0))
        assert result.is_valid
        assert mock_planet.gravity_target == 5.0

    def test_success_clear_gravity_target(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import SetGravityTargetCommandHandler
        mock_planet.gravity_target = 5.0
        _session_with_planet(mock_session, mock_planet)
        handler = SetGravityTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(gravity_target=None))
        assert result.is_valid
        assert mock_planet.gravity_target is None


# =============================================================================
# SetWaterTargetCommandHandler Tests
# =============================================================================


class TestSetWaterTargetCommandHandler:
    """Tests for SetWaterTargetCommandHandler.execute()."""

    def _make_cmd(self, planet_id=100, water_target=0.5):
        cmd = MagicMock()
        cmd.planet_id = planet_id
        cmd.water_target = water_target
        return cmd

    # PROJ-479 Task 1.17: test_planet_not_found + test_wrong_owner moved
    # to the parametrized matrix at module scope.

    def test_success_sets_water_target(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import SetWaterTargetCommandHandler
        _session_with_planet(mock_session, mock_planet)
        handler = SetWaterTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(water_target=0.7))
        assert result.is_valid
        assert mock_planet.water_target == 0.7

    def test_success_clear_water_target(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import SetWaterTargetCommandHandler
        mock_planet.water_target = 0.5
        _session_with_planet(mock_session, mock_planet)
        handler = SetWaterTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(water_target=None))
        assert result.is_valid
        assert mock_planet.water_target is None


# =============================================================================
# SetRadiationShieldTargetCommandHandler Tests
# =============================================================================


class TestSetRadiationShieldTargetCommandHandler:
    """Tests for SetRadiationShieldTargetCommandHandler.execute()."""

    def _make_cmd(self, planet_id=100, shielding_target=1.0):
        cmd = MagicMock()
        cmd.planet_id = planet_id
        cmd.shielding_target = shielding_target
        return cmd

    # PROJ-479 Task 1.17: test_planet_not_found + test_wrong_owner moved
    # to the parametrized matrix at module scope.

    def test_success_sets_shielding_target(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import SetRadiationShieldTargetCommandHandler
        _session_with_planet(mock_session, mock_planet)
        handler = SetRadiationShieldTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(shielding_target=1.5))
        assert result.is_valid
        assert mock_planet.radiation_shielding_target == 1.5

    def test_success_clear_shielding_target(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import SetRadiationShieldTargetCommandHandler
        mock_planet.radiation_shielding_target = 1.0
        _session_with_planet(mock_session, mock_planet)
        handler = SetRadiationShieldTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(shielding_target=None))
        assert result.is_valid
        assert mock_planet.radiation_shielding_target is None
