"""PROJ-471 Task 2.10 -- invalidation hook for transfer_mass_preview._catalog."""

import game.ui.screens.transfer_mass_preview as tmp


def test_clear_catalog_forces_reload():
    first = tmp._get_catalog()
    assert tmp._catalog is first

    tmp._clear_catalog()
    assert tmp._catalog is None

    second = tmp._get_catalog()
    assert second is not None
    # A fresh object is loaded after invalidation (no stale process cache).
    assert tmp._catalog is second
