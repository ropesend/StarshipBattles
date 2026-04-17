"""Tests for ApplicationContext — DI container for all application services."""
from unittest.mock import MagicMock

import pytest

from game.context import ApplicationContext


class TestApplicationContextInit:
    """ApplicationContext constructor accepts all 8 service instances."""

    def test_constructor_accepts_all_services(self):
        services = {name: MagicMock() for name in [
            'registry_manager', 'profiler',
            'component_cache', 'policy_manager', 'asset_manager',
            'sprite_manager', 'ship_theme_manager',
            'game_settings',
        ]}
        ctx = ApplicationContext(**services)
        assert ctx is not None

    def test_all_attributes_accessible(self):
        services = {name: MagicMock(name=name) for name in [
            'registry_manager', 'profiler',
            'component_cache', 'policy_manager', 'asset_manager',
            'sprite_manager', 'ship_theme_manager',
            'game_settings',
        ]}
        ctx = ApplicationContext(**services)
        for name, mock in services.items():
            assert getattr(ctx, name) is mock, f"{name} not accessible"

    def test_constructor_with_mock_objects(self):
        """Can construct with arbitrary objects, not just real singletons."""
        ctx = ApplicationContext(
            registry_manager="fake_registry",
            profiler="fake_profiler",
            component_cache="fake_cache",
            policy_manager="fake_policy",
            asset_manager="fake_assets",
            sprite_manager="fake_sprites",
            ship_theme_manager="fake_themes",
            game_settings="fake_settings",
        )
        assert ctx.registry_manager == "fake_registry"
        assert ctx.game_settings == "fake_settings"


class TestCreateProduction:
    """create_production() wraps existing singletons."""

    def test_returns_application_context(self):
        ctx = ApplicationContext.create_production()
        assert isinstance(ctx, ApplicationContext)

    def test_all_attributes_populated(self):
        ctx = ApplicationContext.create_production()
        for name in [
            'registry_manager', 'profiler',
            'component_cache', 'policy_manager', 'asset_manager',
            'sprite_manager', 'ship_theme_manager',
            'game_settings',
        ]:
            assert getattr(ctx, name) is not None, f"{name} is None"

    def test_registry_manager_is_correct_type(self):
        from game.core.registry import RegistryManager
        ctx = ApplicationContext.create_production()
        assert isinstance(ctx.registry_manager, RegistryManager)

    def test_profiler_is_correct_type(self):
        from game.core.profiling import Profiler
        ctx = ApplicationContext.create_production()
        assert isinstance(ctx.profiler, Profiler)


class TestCreateTest:
    """create_test() creates lightweight context with optional overrides."""

    def test_returns_application_context(self):
        ctx = ApplicationContext.create_test()
        assert isinstance(ctx, ApplicationContext)

    def test_all_attributes_populated(self):
        ctx = ApplicationContext.create_test()
        for name in [
            'registry_manager', 'profiler',
            'component_cache', 'policy_manager', 'asset_manager',
            'sprite_manager', 'ship_theme_manager',
            'game_settings',
        ]:
            assert getattr(ctx, name) is not None, f"{name} is None"

    def test_override_specific_service(self):
        mock_profiler = MagicMock(name="custom_profiler")
        ctx = ApplicationContext.create_test(profiler=mock_profiler)
        assert ctx.profiler is mock_profiler

    def test_override_replaces_only_specified(self):
        mock_profiler = MagicMock(name="custom_profiler")
        ctx = ApplicationContext.create_test(profiler=mock_profiler)
        assert ctx.profiler is mock_profiler
        assert ctx.registry_manager is not None
        assert ctx.registry_manager is not mock_profiler


class TestNotSingleton:
    """ApplicationContext is NOT a singleton — each call creates a new instance."""

    def test_two_create_test_calls_return_different_instances(self):
        ctx1 = ApplicationContext.create_test()
        ctx2 = ApplicationContext.create_test()
        assert ctx1 is not ctx2

    def test_independent_service_instances(self):
        ctx1 = ApplicationContext.create_test()
        ctx2 = ApplicationContext.create_test()
        assert ctx1.profiler is not ctx2.profiler
