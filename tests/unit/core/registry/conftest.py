"""
Shared fixtures for registry tests.

NOTE: This conftest.py only applies to tests in this registry/ subdirectory.
The autouse fixture ensures registry state is isolated for these specific tests.
"""

import pytest


@pytest.fixture(autouse=True)
def reset_registry(request):
    """Reset registry state before and after each test.

    This fixture provides a clean module-level RegistryManager for each test,
    then restores the original instance AND its data afterward to prevent
    pollution of other test files that run later in the suite.

    We save both the instance reference AND copies of its data, because the
    reset_game_state fixture (in root conftest) may clear the data between tests.

    PROJ-181: _default_registries module variable removed - no longer saved/restored.
    """
    from game.core.registry import (
        RegistryManager, get_default_registry_manager,
        set_default_registry_manager,
    )
    from game.core.exceptions import StateException

    # Store original instance AND its data to restore after test
    try:
        original_instance = get_default_registry_manager()
    except StateException:
        original_instance = None

    original_data = None
    if original_instance is not None:
        # Deep copy the data in case it gets cleared during the test
        original_data = {
            'components': dict(original_instance.components),
            'modifiers': dict(original_instance.modifiers),
            'vehicle_classes': dict(original_instance.vehicle_classes),
            'resources': dict(original_instance.resources),
        }

    # Reset to clean state for this test
    set_default_registry_manager(RegistryManager())

    yield

    # Restore original instance AND its data to prevent pollution
    if original_instance is not None:
        set_default_registry_manager(original_instance)
        if original_data is not None:
            # Restore the data that may have been cleared
            original_instance.components.clear()
            original_instance.components.update(original_data['components'])
            original_instance.modifiers.clear()
            original_instance.modifiers.update(original_data['modifiers'])
            original_instance.vehicle_classes.clear()
            original_instance.vehicle_classes.update(original_data['vehicle_classes'])
            original_instance.resources.clear()
            original_instance.resources.update(original_data['resources'])
    else:
        set_default_registry_manager(RegistryManager())


@pytest.fixture
def registry():
    """Get a fresh registry instance."""
    from game.core.registry import (
        RegistryManager, set_default_registry_manager,
        get_default_registry_manager,
    )
    set_default_registry_manager(RegistryManager())
    return get_default_registry_manager()
