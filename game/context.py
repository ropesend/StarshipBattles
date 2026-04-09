"""Application dependency injection container.

Holds references to all application services. Created once at startup
(production) or per-test (testing). Passed explicitly to code that needs
service references.

NOT itself a singleton — the caller (app.py or conftest.py) manages
the instance lifetime.

Placed at game/ package level (outside any layer) to avoid upward
dependencies from Core to UI/AI. Factory methods use late imports.

PROJ-258: Initial implementation as wrapper around existing singletons.
"""
from typing import Any

__all__ = ['ApplicationContext']


class ApplicationContext:
    """Dependency injection container for all application services.

    Usage (production):
        ctx = ApplicationContext.create_production()
        battle_screen = BattleScreen(width, height, ctx=ctx)

    Usage (testing):
        ctx = ApplicationContext.create_test(profiler=mock_profiler)
    """

    def __init__(
        self,
        registry_manager: Any,
        profiler: Any,
        strategy_metadata: Any,
        component_cache: Any,
        strategy_manager: Any,
        asset_manager: Any,
        sprite_manager: Any,
        ship_theme_manager: Any,
        screenshot_manager: Any,
        game_settings: Any,
    ):
        self.registry_manager = registry_manager
        self.profiler = profiler
        self.strategy_metadata = strategy_metadata
        self.component_cache = component_cache
        self.strategy_manager = strategy_manager
        self.asset_manager = asset_manager
        self.sprite_manager = sprite_manager
        self.ship_theme_manager = ship_theme_manager
        self.screenshot_manager = screenshot_manager
        self.game_settings = game_settings

    @classmethod
    def create_production(cls) -> 'ApplicationContext':
        """Create the production application context.

        Creates service instances directly.
        Called once from game/app.py at startup.
        """
        # Late imports to avoid circular dependencies and upward layer imports
        from game.core.registry import RegistryManager
        from game.core.profiling import Profiler
        from game.core.strategy_metadata import StrategyMetadataService
        from game.simulation.components.component_loader import ComponentCacheManager
        from game.ai.strategy_manager import StrategyManager
        from game.assets.asset_manager import AssetManager
        from game.ui.renderer.sprites import SpriteManager
        from game.ui.assets.ship_theme_manager import ShipThemeManager
        from game.ui.services.screenshot_manager import ScreenshotManager
        from game.ui.services.game_settings import GameSettings

        # Create all service instances
        registry_mgr = RegistryManager()
        profiler = Profiler()
        strategy_metadata = StrategyMetadataService()
        component_cache = ComponentCacheManager()
        strategy_manager = StrategyManager()
        asset_manager = AssetManager()
        sprite_manager = SpriteManager()
        ship_theme_manager = ShipThemeManager()
        screenshot_manager = ScreenshotManager()
        game_settings = GameSettings()

        # PROJ-258: Set ALL module-level references so get_default_xxx()
        # returns the same instances as ctx.xxx (prevents instance divergence)
        from game.core.registry import set_default_registry_manager
        from game.core.profiling import set_default_profiler
        from game.core.strategy_metadata import get_default_strategy_metadata_service as _sms_mod
        from game.simulation.components.component_loader import get_default_cache_manager as _ccm_mod
        from game.ai.strategy_manager import get_default_strategy_manager as _sm_mod
        from game.assets.asset_manager import set_default_asset_manager
        from game.ui.renderer.sprites import set_default_sprite_manager
        from game.ui.assets.ship_theme_manager import set_default_ship_theme_manager
        from game.ui.services.screenshot_manager import set_default_screenshot_manager
        from game.ui.services.game_settings import set_default_game_settings

        set_default_registry_manager(registry_mgr)
        set_default_profiler(profiler)

        # Set module-level refs for services that have set_default_xxx()
        set_default_asset_manager(asset_manager)
        set_default_sprite_manager(sprite_manager)
        set_default_ship_theme_manager(ship_theme_manager)
        set_default_screenshot_manager(screenshot_manager)
        set_default_game_settings(game_settings)

        # Set module-level refs for services with only _default_xxx (no setter)
        import game.core.strategy_metadata as _sms_module
        _sms_module._default_service = strategy_metadata
        import game.simulation.components.component_loader as _ccm_module
        _ccm_module._default_cache_manager = component_cache
        import game.ai.strategy_manager as _sm_module
        _sm_module._default_strategy_manager = strategy_manager

        return cls(
            registry_manager=registry_mgr,
            profiler=profiler,
            strategy_metadata=strategy_metadata,
            component_cache=component_cache,
            strategy_manager=strategy_manager,
            asset_manager=asset_manager,
            sprite_manager=sprite_manager,
            ship_theme_manager=ship_theme_manager,
            screenshot_manager=screenshot_manager,
            game_settings=game_settings,
        )

    @classmethod
    def create_test(cls, **overrides) -> 'ApplicationContext':
        """Create a test application context with fresh instances.

        Creates lightweight service instances for testing. No file I/O
        or heavy initialization. Pass keyword arguments to override
        specific services with mocks or custom instances.
        """
        # Late imports
        from game.core.registry import RegistryManager
        from game.core.profiling import Profiler
        from game.core.strategy_metadata import StrategyMetadataService
        from game.simulation.components.component_loader import ComponentCacheManager
        from game.ai.strategy_manager import StrategyManager
        from game.assets.asset_manager import AssetManager
        from game.ui.renderer.sprites import SpriteManager
        from game.ui.assets.ship_theme_manager import ShipThemeManager
        from game.ui.services.screenshot_manager import ScreenshotManager
        from game.ui.services.game_settings import GameSettings

        defaults = {
            'registry_manager': RegistryManager(),
            'profiler': Profiler.__new__(Profiler),
            'strategy_metadata': StrategyMetadataService.__new__(StrategyMetadataService),
            'component_cache': ComponentCacheManager.__new__(ComponentCacheManager),
            'strategy_manager': StrategyManager.__new__(StrategyManager),
            'asset_manager': AssetManager.__new__(AssetManager),
            'sprite_manager': SpriteManager.__new__(SpriteManager),
            'ship_theme_manager': ShipThemeManager.__new__(ShipThemeManager),
            'screenshot_manager': ScreenshotManager.__new__(ScreenshotManager),
            'game_settings': GameSettings.__new__(GameSettings),
        }
        defaults.update(overrides)
        return cls(**defaults)
