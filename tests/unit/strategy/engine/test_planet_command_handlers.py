"""
Tests for planet command handlers.

PROJ-264 Phase 1: Coverage for IssuePlanetOrderCommandHandler,
ClearPlanetOrdersCommandHandler, DeletePlanetOrderCommandHandler,
SetAtmosphereTargetCommandHandler.
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
    session.player_empire = MagicMock()
    session.player_empire.id = 0
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
# IssuePlanetOrderCommandHandler Tests
# =============================================================================


class TestIssuePlanetOrderCommandHandler:
    """Tests for IssuePlanetOrderCommandHandler.execute()."""

    def _make_cmd(self, **overrides):
        cmd = MagicMock()
        cmd.planet_id = overrides.get('planet_id', 100)
        cmd.order_type = overrides.get('order_type', 'ACTIVATE_ABILITY')
        cmd.facility_instance_id = overrides.get('facility_instance_id', 'fac-1')
        cmd.ability_name = overrides.get('ability_name', 'PlanetaryShield')
        cmd.component_key = overrides.get('component_key', None)
        cmd.component_id = overrides.get('component_id', None)
        return cmd

    def test_planet_not_found(self, mock_session):
        """Returns error when planet is not found."""
        from game.strategy.engine.planet_command_handlers import IssuePlanetOrderCommandHandler

        handler = IssuePlanetOrderCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())

        assert not result.is_valid
        assert "not found" in result.message.lower()

    def test_wrong_owner(self, mock_session, mock_planet):
        """Returns error when planet owned by different empire."""
        from game.strategy.engine.planet_command_handlers import IssuePlanetOrderCommandHandler

        mock_planet.owner_id = 99
        _session_with_planet(mock_session, mock_planet)

        handler = IssuePlanetOrderCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())

        assert not result.is_valid
        assert "does not belong" in result.message.lower()

    def test_unknown_order_type(self, mock_session, mock_planet):
        """Returns error for unknown order type string."""
        from game.strategy.engine.planet_command_handlers import IssuePlanetOrderCommandHandler

        _session_with_planet(mock_session, mock_planet)

        handler = IssuePlanetOrderCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(order_type='BOGUS_TYPE'))

        assert not result.is_valid
        assert "unknown" in result.message.lower()

    def test_activate_without_ability_name(self, mock_session, mock_planet):
        """Returns error when ACTIVATE_ABILITY lacks ability_name."""
        from game.strategy.engine.planet_command_handlers import IssuePlanetOrderCommandHandler

        _session_with_planet(mock_session, mock_planet)

        handler = IssuePlanetOrderCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(ability_name=None))

        assert not result.is_valid
        assert "ability_name" in result.message.lower()

    def test_deactivate_without_ability_name(self, mock_session, mock_planet):
        """Returns error when DEACTIVATE_ABILITY lacks ability_name."""
        from game.strategy.engine.planet_command_handlers import IssuePlanetOrderCommandHandler

        _session_with_planet(mock_session, mock_planet)

        handler = IssuePlanetOrderCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(
            order_type='DEACTIVATE_ABILITY', ability_name=None
        ))

        assert not result.is_valid
        assert "ability_name" in result.message.lower()

    def test_activate_validation_failure(self, mock_session, mock_planet):
        """Returns error when validator rejects activation."""
        from game.strategy.engine.planet_command_handlers import IssuePlanetOrderCommandHandler

        _session_with_planet(mock_session, mock_planet)

        handler = IssuePlanetOrderCommandHandler()
        with patch.object(
            __import__('game.strategy.validation.planet_order_validator', fromlist=['PlanetOrderValidator']).PlanetOrderValidator,
            'validate_activate_ability',
            return_value=ValidationResult.error("Facility not found"),
        ):
            result = handler.execute(mock_session, self._make_cmd())

        assert not result.is_valid

    def test_activate_success_queues_order(self, mock_session, mock_planet):
        """Successful activation queues order on planet."""
        from game.strategy.engine.planet_command_handlers import IssuePlanetOrderCommandHandler
        from game.strategy.validation.planet_order_validator import PlanetOrderValidator

        _session_with_planet(mock_session, mock_planet)

        handler = IssuePlanetOrderCommandHandler()
        with patch.object(
            PlanetOrderValidator, 'validate_activate_ability',
            return_value=ValidationResult.success(),
        ):
            result = handler.execute(mock_session, self._make_cmd())

        assert result.is_valid
        mock_planet.add_order.assert_called_once()
        order_arg = mock_planet.add_order.call_args[0][0]
        assert order_arg.type == OrderType.ACTIVATE_ABILITY
        assert order_arg.target['facility_instance_id'] == 'fac-1'
        assert order_arg.target['ability_name'] == 'PlanetaryShield'

    def test_activate_with_component_key_includes_key_in_target(self, mock_session, mock_planet):
        """Activation with component_key includes it in order target."""
        from game.strategy.engine.planet_command_handlers import IssuePlanetOrderCommandHandler
        from game.strategy.validation.planet_order_validator import PlanetOrderValidator

        _session_with_planet(mock_session, mock_planet)

        handler = IssuePlanetOrderCommandHandler()
        cmd = self._make_cmd(
            component_key='CORE:0:shield_gen',
            component_id='shield_gen',
        )
        with patch.object(
            PlanetOrderValidator, 'validate_activate_ability',
            return_value=ValidationResult.success(),
        ):
            result = handler.execute(mock_session, cmd)

        assert result.is_valid
        order_arg = mock_planet.add_order.call_args[0][0]
        assert order_arg.target['component_key'] == 'CORE:0:shield_gen'
        assert order_arg.target['component_id'] == 'shield_gen'

    def test_deactivate_success(self, mock_session, mock_planet):
        """Successful deactivation queues deactivate order."""
        from game.strategy.engine.planet_command_handlers import IssuePlanetOrderCommandHandler
        from game.strategy.validation.planet_order_validator import PlanetOrderValidator

        _session_with_planet(mock_session, mock_planet)

        handler = IssuePlanetOrderCommandHandler()
        cmd = self._make_cmd(order_type='DEACTIVATE_ABILITY')
        with patch.object(
            PlanetOrderValidator, 'validate_deactivate_ability',
            return_value=ValidationResult.success(),
        ):
            result = handler.execute(mock_session, cmd)

        assert result.is_valid
        order_arg = mock_planet.add_order.call_args[0][0]
        assert order_arg.type == OrderType.DEACTIVATE_ABILITY

    def test_unsupported_order_type(self, mock_session, mock_planet):
        """Returns error for unsupported (but valid) order type."""
        from game.strategy.engine.planet_command_handlers import IssuePlanetOrderCommandHandler

        _session_with_planet(mock_session, mock_planet)

        handler = IssuePlanetOrderCommandHandler()
        result = handler.execute(mock_session, self._make_cmd(order_type='MOVE'))

        assert not result.is_valid
        assert "unsupported" in result.message.lower()


# =============================================================================
# ClearPlanetOrdersCommandHandler Tests
# =============================================================================


class TestClearPlanetOrdersCommandHandler:
    """Tests for ClearPlanetOrdersCommandHandler.execute()."""

    def _make_cmd(self, planet_id=100):
        cmd = MagicMock()
        cmd.planet_id = planet_id
        return cmd

    def test_planet_not_found(self, mock_session):
        """Returns error when planet is not found."""
        from game.strategy.engine.planet_command_handlers import ClearPlanetOrdersCommandHandler

        handler = ClearPlanetOrdersCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())

        assert not result.is_valid

    def test_wrong_owner(self, mock_session, mock_planet):
        """Returns error when planet owned by different empire."""
        from game.strategy.engine.planet_command_handlers import ClearPlanetOrdersCommandHandler

        mock_planet.owner_id = 99
        _session_with_planet(mock_session, mock_planet)

        handler = ClearPlanetOrdersCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())

        assert not result.is_valid

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

    def test_planet_not_found(self, mock_session):
        """Returns error when planet is not found."""
        from game.strategy.engine.planet_command_handlers import DeletePlanetOrderCommandHandler

        handler = DeletePlanetOrderCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())

        assert not result.is_valid

    def test_wrong_owner(self, mock_session, mock_planet):
        """Returns error when planet owned by different empire."""
        from game.strategy.engine.planet_command_handlers import DeletePlanetOrderCommandHandler

        mock_planet.owner_id = 99
        _session_with_planet(mock_session, mock_planet)

        handler = DeletePlanetOrderCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())

        assert not result.is_valid

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

    def test_planet_not_found(self, mock_session):
        """Returns error when planet not found."""
        from game.strategy.engine.planet_command_handlers import SetAtmosphereTargetCommandHandler

        handler = SetAtmosphereTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())

        assert not result.is_valid

    def test_wrong_owner(self, mock_session, mock_planet):
        """Returns error when wrong owner."""
        from game.strategy.engine.planet_command_handlers import SetAtmosphereTargetCommandHandler

        mock_planet.owner_id = 99
        _session_with_planet(mock_session, mock_planet)

        handler = SetAtmosphereTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())

        assert not result.is_valid

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

    def test_planet_not_found(self, mock_session):
        from game.strategy.engine.planet_command_handlers import SetGravityTargetCommandHandler
        handler = SetGravityTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())
        assert not result.is_valid

    def test_wrong_owner(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import SetGravityTargetCommandHandler
        mock_planet.owner_id = 99
        _session_with_planet(mock_session, mock_planet)
        handler = SetGravityTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())
        assert not result.is_valid

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

    def test_planet_not_found(self, mock_session):
        from game.strategy.engine.planet_command_handlers import SetWaterTargetCommandHandler
        handler = SetWaterTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())
        assert not result.is_valid

    def test_wrong_owner(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import SetWaterTargetCommandHandler
        mock_planet.owner_id = 99
        _session_with_planet(mock_session, mock_planet)
        handler = SetWaterTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())
        assert not result.is_valid

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

    def test_planet_not_found(self, mock_session):
        from game.strategy.engine.planet_command_handlers import SetRadiationShieldTargetCommandHandler
        handler = SetRadiationShieldTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())
        assert not result.is_valid

    def test_wrong_owner(self, mock_session, mock_planet):
        from game.strategy.engine.planet_command_handlers import SetRadiationShieldTargetCommandHandler
        mock_planet.owner_id = 99
        _session_with_planet(mock_session, mock_planet)
        handler = SetRadiationShieldTargetCommandHandler()
        result = handler.execute(mock_session, self._make_cmd())
        assert not result.is_valid

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
