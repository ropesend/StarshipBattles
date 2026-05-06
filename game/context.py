"""Application dependency injection container.

Holds references to all application services. Created once at startup
(production) or per-test (testing). Passed explicitly to code that needs
service references.

NOT itself a singleton — the caller (app.py or conftest.py) manages
the instance lifetime.

Placed at game/ package level (outside any layer) to avoid upward
dependencies from Core to UI/AI. Factory methods use late imports.

PROJ-258: Initial implementation as wrapper around existing singletons.
PROJ-372 (Phase 0): added module-level habitability service accessors so
modders can swap `IHabitabilityCalculator` without monkey-patching. Phase
0 ships with the accessors returning ``None``; Phase 2 wires the real
``PlanetHabitabilityService`` default.
"""
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from game.strategy.data.galaxy_protocols import IHabitabilityCalculator

__all__ = [
    'ApplicationContext',
    'get_default_planet_habitability_service',
    'set_default_planet_habitability_service',
]


# PROJ-372 Phase 0: module-level habitability-calculator slot.
# Phase 0 leaves this None — `Planet.get_cached_habitability_multiplier`
# falls back to its existing late-import path. Phase 2 sets a real
# `PlanetHabitabilityService()` instance at import time.
_default_planet_habitability_service: Optional['IHabitabilityCalculator'] = None


def get_default_planet_habitability_service() -> Optional['IHabitabilityCalculator']:
    """Return the registered habitability calculator (or None).

    PROJ-372: Phase 0 always returns None (callers fall back to the
    late-imported `planet_habitability_multiplier`). Phase 2 wires the
    real default. Tests / mods may override via
    `set_default_planet_habitability_service` (PROJ-258 pattern).
    """
    return _default_planet_habitability_service


def set_default_planet_habitability_service(
    svc: Optional['IHabitabilityCalculator'],
) -> None:
    """Register the global habitability calculator. Pass None to clear."""
    global _default_planet_habitability_service
    _default_planet_habitability_service = svc


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
        component_cache: Any,
        policy_manager: Any,
        asset_manager: Any,
        sprite_manager: Any,
        ship_theme_manager: Any,
        game_settings: Any,
        llm_provider: Any = None,
        image_provider: Any = None,
    ):
        self.registry_manager = registry_manager
        self.profiler = profiler
        self.component_cache = component_cache
        self.policy_manager = policy_manager
        self.asset_manager = asset_manager
        self.sprite_manager = sprite_manager
        self.ship_theme_manager = ship_theme_manager
        self.game_settings = game_settings
        # PROJ-296: LLM service. May be None when no provider key is configured;
        # consumers must check `if ctx.llm_provider is not None:` before use.
        self.llm_provider = llm_provider
        # PROJ-314: image-generation service. May be None or the
        # NullImageProvider when no key is configured. Consumers must
        # treat both as "unavailable" rather than crashing.
        self.image_provider = image_provider

    @classmethod
    def create_production(cls) -> 'ApplicationContext':
        """Create the production application context.

        Creates service instances directly.
        Called once from game/app.py at startup.
        """
        # Late imports to avoid circular dependencies and upward layer imports
        from game.core.registry import RegistryManager
        from game.core.profiling import Profiler
        from game.simulation.components.component_loader import ComponentCacheManager
        from game.ai.policy_manager import PolicyManager
        from game.assets.asset_manager import AssetManager
        from game.ui.renderer.sprites import SpriteManager
        from game.ui.assets.ship_theme_manager import ShipThemeManager
        from game.ui.services.game_settings import GameSettings
        # PROJ-296: LLM service factory.
        from game.core.exceptions import LLMConfigError
        from game.services.llm import LLMProviderFactory
        # PROJ-314: image service factory.
        from game.core.exceptions import ImageConfigError
        from game.ui.services.image import (
            ImageProviderFactory,
            NullImageProvider,
        )

        # Create all service instances
        registry_mgr = RegistryManager()
        profiler = Profiler()
        component_cache = ComponentCacheManager()
        policy_manager = PolicyManager()
        asset_manager = AssetManager()
        sprite_manager = SpriteManager()
        ship_theme_manager = ShipThemeManager()
        game_settings = GameSettings()
        # PROJ-296: best-effort LLM provider. None when no key configured
        # OR when the provider's name is unknown — both are tolerated so
        # the game still launches without DEEPSEEK_API_KEY set.
        try:
            llm_provider = LLMProviderFactory.create()
        except LLMConfigError:
            llm_provider = None
        # PROJ-314: best-effort image provider. Falls back to
        # NullImageProvider when no OPENAI_API_KEY is configured so the
        # game still launches and consumers can detect "unavailable".
        try:
            image_provider = ImageProviderFactory.create()
        except ImageConfigError:
            image_provider = None
        if image_provider is None:
            image_provider = NullImageProvider()

        # PROJ-258: Set ALL module-level references so get_default_xxx()
        # returns the same instances as ctx.xxx (prevents instance divergence)
        from game.core.registry import set_default_registry_manager
        from game.core.profiling import set_default_profiler
        from game.assets.asset_manager import set_default_asset_manager
        from game.ui.renderer.sprites import set_default_sprite_manager
        from game.ui.assets.ship_theme_manager import set_default_ship_theme_manager
        from game.ui.services.game_settings import set_default_game_settings
        # PROJ-296: LLM provider module-level setter.
        from game.services.llm import set_default_llm_provider
        # PROJ-314: image provider module-level setter.
        from game.ui.services.image import set_default_image_provider

        set_default_registry_manager(registry_mgr)
        set_default_profiler(profiler)

        # Set module-level refs for services that have set_default_xxx()
        set_default_asset_manager(asset_manager)
        set_default_sprite_manager(sprite_manager)
        set_default_ship_theme_manager(ship_theme_manager)
        set_default_game_settings(game_settings)
        set_default_llm_provider(llm_provider)
        set_default_image_provider(image_provider)

        # Set module-level refs for services with only _default_xxx (no setter)
        import game.simulation.components.component_loader as _ccm_module
        _ccm_module._default_cache_manager = component_cache
        import game.ai.policy_manager as _pm_module
        _pm_module._default_policy_manager = policy_manager

        return cls(
            registry_manager=registry_mgr,
            profiler=profiler,
            component_cache=component_cache,
            policy_manager=policy_manager,
            asset_manager=asset_manager,
            sprite_manager=sprite_manager,
            ship_theme_manager=ship_theme_manager,
            game_settings=game_settings,
            llm_provider=llm_provider,
            image_provider=image_provider,
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
        from game.simulation.components.component_loader import ComponentCacheManager
        from game.ai.policy_manager import PolicyManager
        from game.assets.asset_manager import AssetManager
        from game.ui.renderer.sprites import SpriteManager
        from game.ui.assets.ship_theme_manager import ShipThemeManager
        from game.ui.services.game_settings import GameSettings
        # PROJ-314: tests get NullImageProvider by default — raises on
        # generate_image() so accidental real-network calls are caught loudly.
        from game.ui.services.image import NullImageProvider

        defaults = {
            'registry_manager': RegistryManager(),
            'profiler': Profiler.__new__(Profiler),
            'component_cache': ComponentCacheManager.__new__(ComponentCacheManager),
            'policy_manager': PolicyManager.__new__(PolicyManager),
            'asset_manager': AssetManager.__new__(AssetManager),
            'sprite_manager': SpriteManager.__new__(SpriteManager),
            'ship_theme_manager': ShipThemeManager.__new__(ShipThemeManager),
            'game_settings': GameSettings.__new__(GameSettings),
            # PROJ-296: tests opt-in to an LLM provider via override; default None.
            'llm_provider': None,
            # PROJ-314: tests get NullImageProvider by default.
            'image_provider': NullImageProvider(),
        }
        defaults.update(overrides)
        return cls(**defaults)
