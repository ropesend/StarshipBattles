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

        # PROJ-258: RegistryManager is no longer a singleton — create directly
        # and set the module-level reference for wrapper functions
        from game.core.registry import set_default_registry_manager
        registry_mgr = RegistryManager()
        set_default_registry_manager(registry_mgr)

        return cls(
            registry_manager=registry_mgr,
            profiler=Profiler(),
            strategy_metadata=StrategyMetadataService(),
            component_cache=ComponentCacheManager(),
            strategy_manager=StrategyManager(),
            asset_manager=AssetManager(),
            sprite_manager=SpriteManager(),
            ship_theme_manager=ShipThemeManager(),
            screenshot_manager=ScreenshotManager(),
            game_settings=GameSettings(),
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
