"""PROJ-471 Task 2.6: the module-level sprite-manager accessor must not
silently auto-create a fresh ``SpriteManager`` when none has been set.

ST-01-005: the old lazy-init fallback created a divergent manager if any
code touched ``get_default_sprite_manager()`` before
``set_default_sprite_manager()`` ran in ``create_production()``. That hid
ordering bugs and could return an unloaded manager. The accessor now raises
a descriptive error instead.
"""
from __future__ import annotations

import pytest

import game.ui.renderer.sprites as sprites_module
from game.ui.renderer.sprites import (
    SpriteManager,
    get_default_sprite_manager,
    set_default_sprite_manager,
)


@pytest.fixture(autouse=True)
def restore_default():
    saved = sprites_module._default_sprite_manager
    yield
    sprites_module._default_sprite_manager = saved


def test_get_default_raises_when_unset():
    sprites_module._default_sprite_manager = None
    with pytest.raises(RuntimeError, match="set_default_sprite_manager"):
        get_default_sprite_manager()


def test_get_default_returns_set_instance():
    mgr = SpriteManager()
    set_default_sprite_manager(mgr)
    assert get_default_sprite_manager() is mgr


def test_no_silent_new_instance_created():
    """Calling the accessor while unset must not mutate the module slot."""
    sprites_module._default_sprite_manager = None
    with pytest.raises(RuntimeError):
        get_default_sprite_manager()
    assert sprites_module._default_sprite_manager is None
