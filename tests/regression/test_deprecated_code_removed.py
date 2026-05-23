"""
Verification tests for deprecated code removal (PROJ-42).

These tests ensure that deprecated code stays removed and doesn't accidentally
get reintroduced. They serve as regression guards for the cleanup work.
"""
import pytest


class TestDeprecatedRegistryFunctionsRemoved:
    """Verify deprecated registry utility functions have been removed."""

    # PROJ-495 T3.1: parametrized the 4 deletion-guard tests on the attribute
    # name + intended replacement so adding a new deprecated symbol is a
    # single row, not a new method.
    @pytest.mark.parametrize(
        "attr_name,replacement_hint",
        [
            ("get_component_registry", "GameRegistries.components"),
            ("get_modifier_registry", "GameRegistries.modifiers"),
            ("get_vehicle_classes", "GameRegistries.vehicle_classes"),
            ("get_resource_registry", "GameRegistries.resources"),
        ],
    )
    def test_deprecated_attr_removed(self, attr_name: str, replacement_hint: str) -> None:
        """The deprecated module-level function should not exist."""
        from game.core import registry
        assert not hasattr(registry, attr_name), (
            f"{attr_name} should be removed - use {replacement_hint}"
        )

    # PROJ-195: test_get_validator_global_removed REMOVED
    # The get_validator() module-level function was intentionally added in PROJ-195
    # to encapsulate RegistryManager.instance().get_validator() access in one place.
    # This enables non-root code to access the validator without direct singleton calls.


class TestGameStateAliasesRemoved:
    """Verify GameState aliases have been removed from app.py."""

    @pytest.mark.parametrize(
        "alias",
        ["MENU", "BUILDER", "BATTLE", "SETTINGS"],
    )
    def test_alias_removed(self, alias: str) -> None:
        """The GameState alias should not exist on the app module."""
        from game import app
        assert not hasattr(app, alias), (
            f"{alias} alias should be removed - use GameState.{alias}"
        )


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
        """get_default_registry_manager() should provide direct access to registries."""
        from game.core.registry import get_default_registry_manager

        mgr = get_default_registry_manager()
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


class TestSingletonUsageCount:
    """
    PROJ-195: Regression guard for RegistryManager.instance() usage.

    This test ensures the deprecated .instance() shim doesn't creep back.
    After PROJ-258 completion, all code uses get_default_registry_manager()
    or ApplicationContext instead. The only remaining string occurrences
    are in this file's counting logic and test_data_layer_boundaries.py's
    production code guard.
    """

    # Expected counts after PROJ-258 shim removal:
    # game/: 0 (shim removed, all code uses get_default_registry_manager())
    # tests/: 13 (9 in this file's comments/strings + 4 in test_data_layer_boundaries.py's guard)
    EXPECTED_GAME_COUNT = 0
    EXPECTED_TESTS_COUNT = 13

    def test_singleton_usage_count_game(self):
        """RegistryManager.instance() count in game/ should not increase."""
        import os

        game_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'game')
        total = 0
        for root, _, files in os.walk(game_dir):
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            total += content.count('RegistryManager.instance()')
                    except UnicodeDecodeError:
                        pass # Ignore non-text or differently encoded files just in case

        assert total <= self.EXPECTED_GAME_COUNT, (
            f"RegistryManager.instance() count in game/ increased from "
            f"{self.EXPECTED_GAME_COUNT} to {total}. "
            f"Use get_default_registry_manager() instead of RegistryManager.instance(). "
            f"If this is truly necessary, update EXPECTED_GAME_COUNT in this test."
        )

    def test_singleton_usage_count_tests(self):
        """RegistryManager.instance() count in tests/ should not increase."""
        import os

        # Navigate from tests/regression/ up to tests/
        tests_dir = os.path.join(os.path.dirname(__file__), '..')
        total = 0
        for root, _, files in os.walk(tests_dir):
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            total += content.count('RegistryManager.instance()')
                    except UnicodeDecodeError:
                        pass

        assert total <= self.EXPECTED_TESTS_COUNT, (
            f"RegistryManager.instance() count in tests/ increased from "
            f"{self.EXPECTED_TESTS_COUNT} to {total}. "
            f"New tests should use get_default_registry_manager() or fresh_registries fixture. "
            f"If this is a legitimate usage, update EXPECTED_TESTS_COUNT."
        )
