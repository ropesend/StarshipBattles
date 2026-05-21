"""PROJ-471 Task 2.1 -- setter for _default_cache_manager + reset routing."""

import game.simulation.components.component_loader as cl
from game.simulation.components.component_loader import (
    ComponentCacheManager,
    get_default_cache_manager,
    set_default_cache_manager,
    reset_component_caches,
)


def test_setter_installs_instance_returned_by_getter():
    mgr = ComponentCacheManager()
    set_default_cache_manager(mgr)
    assert get_default_cache_manager() is mgr


def test_reset_routes_through_module_default():
    set_default_cache_manager(ComponentCacheManager())
    reset_component_caches()
    # After reset the getter returns a manager, and the module-level reference
    # is the same object the getter hands out (no divergence).
    assert get_default_cache_manager() is cl._default_cache_manager


def test_reset_does_not_diverge_from_a_live_context():
    """PROJ-471 Task 4.2 (Codex finding 2): a reference captured before reset
    (as ApplicationContext.component_cache is) must stay the live default and
    have its caches cleared in place, not be orphaned by an instance swap."""
    mgr = ComponentCacheManager()
    set_default_cache_manager(mgr)
    mgr.component_cache = {"x": 1}
    mgr.modifier_cache = {"y": 2}

    captured = get_default_cache_manager()  # what a live ctx would hold
    assert captured is mgr

    reset_component_caches()

    # Same instance still the module default (no divergence) ...
    assert get_default_cache_manager() is captured
    # ... and its caches were actually cleared.
    assert captured.component_cache is None
    assert captured.modifier_cache is None
