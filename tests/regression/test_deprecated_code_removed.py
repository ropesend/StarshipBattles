"""
Verification tests for deprecated code removal (PROJ-42).

These tests ensure that deprecated code stays removed and doesn't accidentally
get reintroduced. They serve as regression guards for the cleanup work.
"""
import pytest


class TestFleetMovementSimulatorRemoved:
    """Verify FleetMovementSimulator module has been removed."""

    def test_fleet_movement_simulator_import_fails(self):
        """FleetMovementSimulator should no longer be importable."""
        with pytest.raises(ImportError):
            from game.strategy.engine.fleet_movement import FleetMovementSimulator


class TestDeprecatedRegistryFunctionsRemoved:
    """Verify deprecated registry utility functions have been removed."""

    def test_get_component_registry_removed(self):
        """get_component_registry() function should not exist."""
        from game.core import registry
        assert not hasattr(registry, 'get_component_registry'), \
            "get_component_registry should be removed - use GameRegistries.components"

    def test_get_modifier_registry_removed(self):
        """get_modifier_registry() function should not exist."""
        from game.core import registry
        assert not hasattr(registry, 'get_modifier_registry'), \
            "get_modifier_registry should be removed - use GameRegistries.modifiers"

    def test_get_vehicle_classes_removed(self):
        """get_vehicle_classes() function should not exist."""
        from game.core import registry
        assert not hasattr(registry, 'get_vehicle_classes'), \
            "get_vehicle_classes should be removed - use GameRegistries.vehicle_classes"

    def test_get_resource_registry_removed(self):
        """get_resource_registry() function should not exist."""
        from game.core import registry
        assert not hasattr(registry, 'get_resource_registry'), \
            "get_resource_registry should be removed - use GameRegistries.resources"

    # PROJ-195: test_get_validator_global_removed REMOVED
    # The get_validator() module-level function was intentionally added in PROJ-195
    # to encapsulate RegistryManager.instance().get_validator() access in one place.
    # This enables non-root code to access the validator without direct singleton calls.


class TestGameStateAliasesRemoved:
    """Verify GameState aliases have been removed from app.py."""

    def test_menu_alias_removed(self):
        """MENU alias should not exist in app module."""
        from game import app
        assert not hasattr(app, 'MENU'), \
            "MENU alias should be removed - use GameState.MENU"

    def test_builder_alias_removed(self):
        """BUILDER alias should not exist in app module."""
        from game import app
        assert not hasattr(app, 'BUILDER'), \
            "BUILDER alias should be removed - use GameState.BUILDER"

    def test_battle_alias_removed(self):
        """BATTLE alias should not exist in app module."""
        from game import app
        assert not hasattr(app, 'BATTLE'), \
            "BATTLE alias should be removed - use GameState.BATTLE"

    def test_settings_alias_removed(self):
        """SETTINGS alias should not exist in app module."""
        from game import app
        assert not hasattr(app, 'SETTINGS'), \
            "SETTINGS alias should be removed - use GameState.SETTINGS"


class TestNewPatternsWork:
    """Verify new patterns work correctly as replacements."""

    def test_game_registries_accessible(self):
        """GameRegistries container should be importable and usable."""
        from game.core.registry import GameRegistries

        # Should be a frozen dataclass
        from dataclasses import is_dataclass
        assert is_dataclass(GameRegistries)

        # Should accept all four registry dicts
        gr = GameRegistries(
            components={"test": {}},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        assert "test" in gr.components

    def test_get_default_registries_function_removed(self):
        """get_default_registries() should be removed (PROJ-181)."""
        from game.core import registry
        assert not hasattr(registry, 'get_default_registries'), \
            "get_default_registries should be removed - use get_default_registry_provider()"

    def test_set_default_registries_function_removed(self):
        """set_default_registries() should be removed (PROJ-181)."""
        from game.core import registry
        assert not hasattr(registry, 'set_default_registries'), \
            "set_default_registries should be removed - use IRegistryProvider via DI"

    def test_get_default_registry_provider_function_exists(self):
        """get_default_registry_provider() should exist for DI patterns."""
        from game.core.registry import get_default_registry_provider
        assert callable(get_default_registry_provider)

    def test_registry_manager_direct_access_works(self):
        """RegistryManager.instance().components should work for direct access."""
        from game.core.registry import RegistryManager

        mgr = RegistryManager.instance()
        assert hasattr(mgr, 'components')
        assert hasattr(mgr, 'modifiers')
        assert hasattr(mgr, 'vehicle_classes')
        assert hasattr(mgr, 'resources')


class TestLegacyCrewRequirementRemoved:
    """Verify legacy crew requirement pattern has been removed."""

    def test_get_legacy_crew_requirement_removed(self):
        """_get_legacy_crew_requirement() should be removed from Component."""
        from game.simulation.components.component import Component
        assert not hasattr(Component, '_get_legacy_crew_requirement'), \
            "_get_legacy_crew_requirement should be removed - no components use negative CrewCapacity"
