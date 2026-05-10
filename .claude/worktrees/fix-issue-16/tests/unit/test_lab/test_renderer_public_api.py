"""Contract tests for the public API of `game.ui.screens.test_lab.renderer`.

PROJ-309 sub-phase 3.3 decomposes `renderer.py` into a `renderer/` subpackage.
These tests lock the public surface so the split is invisible to callers:

* `TestLabRenderer` class is importable from the canonical path.
* `TestLabRenderer()` no-arg constructor works (after pygame init).
* `TestLabRenderer.draw` callable.
* Static/pure-method aliases on the class — `_format_check_pair`,
  `_is_condition_verified` — are still present so existing tests in
  `tests/unit/ui/screens/test_lab/test_renderer_pure_functions.py` continue
  to pass against the class attribute.

These tests must PASS pre-split (against the original 1195-line file) AND
post-split (against the new subpackage). That guarantees byte-for-byte
public-API stability.
"""
from __future__ import annotations


def test_test_lab_renderer_importable_from_canonical_path() -> None:
    """`TestLabRenderer` must remain importable from
    `game.ui.screens.test_lab.renderer` (the path used by `screen.py`)."""
    from game.ui.screens.test_lab.renderer import TestLabRenderer

    assert TestLabRenderer is not None
    assert isinstance(TestLabRenderer, type)


def test_format_check_pair_accessible_as_class_attr() -> None:
    """Existing tests access `TestLabRenderer._format_check_pair` as a class
    attribute (staticmethod). Post-split the alias must persist."""
    from game.ui.screens.test_lab.renderer import TestLabRenderer

    assert hasattr(TestLabRenderer, "_format_check_pair")
    # Callable as static method (no `self` needed)
    exp, act = TestLabRenderer._format_check_pair(None, None)
    assert exp == "—"
    assert act == "—"


def test_is_condition_verified_accessible_as_class_attr() -> None:
    """Existing tests instantiate via `__new__` and call
    `_is_condition_verified` as an unbound method. The attribute must persist."""
    from game.ui.screens.test_lab.renderer import TestLabRenderer

    assert hasattr(TestLabRenderer, "_is_condition_verified")
    # Bypass __init__ (matches existing test pattern)
    r = TestLabRenderer.__new__(TestLabRenderer)
    # Empty validation list — should return False, never raise.
    assert r._is_condition_verified("Beam Damage: 5", []) is False


def test_draw_method_present_on_class() -> None:
    """The only public method exercised by `screen.py` is `.draw(...)`.
    Verify it survives the split."""
    from game.ui.screens.test_lab.renderer import TestLabRenderer

    assert hasattr(TestLabRenderer, "draw")
    assert callable(TestLabRenderer.draw)
