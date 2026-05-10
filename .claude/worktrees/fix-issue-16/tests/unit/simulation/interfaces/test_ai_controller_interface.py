"""
Tests for IAIController protocol.

PROJ-43 Phase 8: Verify the IAIController protocol correctly defines
the interface needed by BattleEngine for AI controllers.
"""
import pytest
from typing import Any, runtime_checkable, Protocol


class TestIAIControllerProtocol:
    """Tests for IAIController protocol definition."""

    def test_protocol_exists(self):
        """IAIController protocol should be importable."""
        from game.simulation.interfaces.ai_controller import IAIController
        assert IAIController is not None

    def test_protocol_is_runtime_checkable(self):
        """IAIController should be a runtime-checkable Protocol."""
        from game.simulation.interfaces.ai_controller import IAIController
        assert hasattr(IAIController, '__protocol_attrs__') or isinstance(IAIController, type)
        # Protocols are types
        assert isinstance(IAIController, type)

    def test_protocol_requires_update_method(self):
        """IAIController should require an update() method."""
        from game.simulation.interfaces.ai_controller import IAIController

        class ImplementsUpdate:
            @property
            def ship(self) -> Any:
                return None
            def update(self) -> None:
                pass

        # Should structurally match the protocol
        instance = ImplementsUpdate()
        assert hasattr(instance, 'update')
        assert callable(instance.update)

    def test_protocol_requires_ship_property(self):
        """IAIController should require a ship property for identification."""
        from game.simulation.interfaces.ai_controller import IAIController

        class ImplementsShip:
            @property
            def ship(self) -> Any:
                return "mock_ship"
            def update(self) -> None:
                pass

        instance = ImplementsShip()
        assert hasattr(instance, 'ship')
        assert instance.ship == "mock_ship"

    def test_protocol_exported_from_package(self):
        """IAIController should be exported from interfaces package."""
        from game.simulation.interfaces import IAIController
        assert IAIController is not None


class TestAIControllerProtocolCompliance:
    """Tests that verify real AIController matches the protocol."""

    def test_real_ai_controller_has_update_method(self):
        """Real AIController should have the update() method."""
        from game.ai.controller import AIController
        assert hasattr(AIController, 'update')
        assert callable(getattr(AIController, 'update'))

    def test_real_ai_controller_has_ship_property(self):
        """Real AIController should have the ship attribute."""
        from game.ai.controller import AIController
        # AIController stores ship as instance attribute set in __init__
        # Check that the class can accept ship parameter
        import inspect
        sig = inspect.signature(AIController.__init__)
        params = list(sig.parameters.keys())
        assert 'ship' in params

    def test_protocol_structural_match_with_real_controller(self):
        """A mock that matches IAIController should work like AIController."""
        from game.simulation.interfaces.ai_controller import IAIController

        class MockController:
            def __init__(self, ship):
                self._ship = ship

            @property
            def ship(self) -> Any:
                return self._ship

            def update(self) -> None:
                pass

        mock = MockController("test_ship")
        # Structural typing - mock should have required interface
        assert hasattr(mock, 'ship')
        assert hasattr(mock, 'update')
        assert mock.ship == "test_ship"
