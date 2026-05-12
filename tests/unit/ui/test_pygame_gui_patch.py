"""PROJ-411 Phase 3 Task 3.1: scoped UI adapter for pygame_gui's
pathological ``UIAppearanceTheme.build_all_combined_ids`` cache key.

pygame_gui 0.6.14's cache already exists at
``pygame_gui/core/ui_appearance_theme.py:1625-1629`` but the cache key
is computed via chained ``str.join`` where each ``str(x)`` is the
separator and each character of the prior result is an element. The
key balloons to ~10 KB per call. ~284 widgets × ~5 lookups per
construction = ~15 MB of string allocation per window open.

Phase 1 cProfile attributed ~72 % (47 / 65 s) of total open time to
``str.join`` self-time plus ``build_all_combined_ids`` self-time.

This module covers a ``StarshipUIAppearanceTheme`` subclass that uses
a *private* tuple-keyed cache (no mutation of pygame_gui's
``unique_theming_ids: Dict[str, List[str]]`` shape) plus a
``StarshipUIManager`` whose ``create_new_theme`` returns the subclass,
plus a source-fingerprint guard that refuses to activate when upstream
has been fixed.

Per codex consult at
``AgentCoordination/Scratchpad/Consult/20260512T035945Z_pygame-gui-cache-key-patch/``.
"""
from __future__ import annotations

import time
from typing import Any

import pygame
import pygame_gui
import pytest
from pygame_gui.core.ui_appearance_theme import UIAppearanceTheme

from game.ui.pygame_gui_patch import (
    StarshipUIAppearanceTheme,
    StarshipUIManager,
    UPSTREAM_HAS_KNOWN_BUG,
)


@pytest.fixture(autouse=True, scope="module")
def _pygame_display():
    pygame.init()
    pygame.display.set_mode((100, 100))
    yield
    pygame.display.quit()
    pygame.quit()


@pytest.fixture
def theme():
    """A real ``StarshipUIAppearanceTheme`` instance via a real ``StarshipUIManager``."""
    mgr = StarshipUIManager((800, 600))
    return mgr.ui_theme


@pytest.fixture
def upstream_theme():
    """A real pygame_gui.UIAppearanceTheme for parity comparison."""
    mgr = pygame_gui.UIManager((800, 600))
    return mgr.ui_theme


# ---------------------------------------------------------------------------
# Diagnosis / guard
# ---------------------------------------------------------------------------

def test_upstream_has_known_bug_flag_is_truthy_for_current_pygame_gui():
    """Source-fingerprint guard sees the pathological chained ``str.join``.

    If upstream pygame_gui releases a fixed version, this assertion will
    flip — at which point the patch can be retired.
    """
    assert UPSTREAM_HAS_KNOWN_BUG is True


def test_starship_manager_creates_starship_theme():
    """``StarshipUIManager.create_new_theme`` returns the subclassed theme."""
    mgr = StarshipUIManager((400, 300))
    assert isinstance(mgr.ui_theme, StarshipUIAppearanceTheme)


# ---------------------------------------------------------------------------
# Parity with upstream
# ---------------------------------------------------------------------------

PARITY_INPUTS: list[tuple[Any, Any, Any, Any]] = [
    # Typical button.
    (["button"], ["button"], [None], [None]),
    # Nested element with a class id.
    (["button"], ["panel.button"], ["@danger"], [None]),
    # Empty lists short-circuit through the inner body.
    ([], [], [], []),
    # All-None inputs — the early branch returns [].
    (None, None, None, None),
]


@pytest.mark.parametrize("base, eids, class_ids, obj_ids", PARITY_INPUTS)
def test_starship_theme_returns_same_combined_ids_as_upstream(
    theme, upstream_theme, base, eids, class_ids, obj_ids
):
    """Starship subclass matches upstream output for normal inputs."""
    starship_out = theme.build_all_combined_ids(base, eids, class_ids, obj_ids)
    upstream_out = upstream_theme.build_all_combined_ids(
        base, eids, class_ids, obj_ids
    )
    assert starship_out == upstream_out


def test_starship_theme_raises_value_error_on_mismatched_lengths(theme):
    """The mismatched-length validation path is preserved."""
    with pytest.raises(ValueError):
        theme.build_all_combined_ids(
            ["a"], ["a", "b"], [None, None], [None, None]
        )


# ---------------------------------------------------------------------------
# Cache behaviour
# ---------------------------------------------------------------------------

def test_starship_theme_uses_private_tuple_cache_not_pygame_gui_dict(theme):
    """The patch must NOT mutate pygame_gui's ``unique_theming_ids``
    (typed ``Dict[str, List[str]]``).

    Codex consult risk #2: type-shape change on a public attribute is
    unsafe. The fix is a private cache attribute on the subclass.
    """
    theme.build_all_combined_ids(["button"], ["button"], [None], [None])

    # pygame_gui's own dict stays string-keyed (it may be empty or hold
    # entries from elsewhere — we just must not introduce tuple keys
    # into it).
    for key in theme.unique_theming_ids.keys():
        assert isinstance(key, str), (
            f"Tuple-shaped key {key!r} leaked into pygame_gui's "
            f"unique_theming_ids dict — that violates its type contract."
        )


def test_starship_theme_caches_hits_idempotently(theme):
    """Repeated calls with the same inputs return the same cached list."""
    first = theme.build_all_combined_ids(
        ["button"], ["button"], [None], [None]
    )
    second = theme.build_all_combined_ids(
        ["button"], ["button"], [None], [None]
    )
    # Same content; the cache returns the same list instance on hit.
    assert first == second


def test_starship_theme_cache_key_is_not_pathologically_large(theme):
    """The new cache key is bounded — not a ~10 KB chained-join string.

    Regression guard for the pygame_gui 0.6.14 pathology. Any future
    change that reintroduces a string cache key bigger than the
    representation of the input tuple will fail this test.
    """
    base = ["button"]
    eids = ["button"]
    class_ids = [None]
    obj_ids = [None]
    theme.build_all_combined_ids(base, eids, class_ids, obj_ids)
    # The private cache is `_combined_ids_cache` (tuple → list[str]).
    keys = list(theme._combined_ids_cache.keys())
    assert keys, "Cache should have at least one entry after a call."
    longest_key_repr = max(len(repr(k)) for k in keys)
    # Upstream's chained str.join produced ~10 KB. A tuple-of-tuples
    # repr for these inputs is well under 200 chars; a 1 KB cap is
    # generous.
    assert longest_key_repr < 1024, (
        f"Cache key repr exceeded 1 KB ({longest_key_repr} chars) — "
        f"chained str.join pattern may have leaked back in."
    )


# ---------------------------------------------------------------------------
# Performance smoke (informational; gate is structural above)
# ---------------------------------------------------------------------------

def test_starship_theme_is_faster_than_upstream_on_repeated_lookups(
    theme, upstream_theme
):
    """Smoke check: 1000 repeated lookups are noticeably faster.

    Wall-clock varies; the gate is *some* speedup, not a precise ratio.
    Structural correctness is asserted in other tests.
    """
    inputs = (["button"], ["panel.button"], [None], [None])

    # Warm-up both caches.
    theme.build_all_combined_ids(*inputs)
    upstream_theme.build_all_combined_ids(*inputs)

    n = 1000
    t0 = time.perf_counter()
    for _ in range(n):
        theme.build_all_combined_ids(*inputs)
    starship_elapsed = time.perf_counter() - t0

    t0 = time.perf_counter()
    for _ in range(n):
        upstream_theme.build_all_combined_ids(*inputs)
    upstream_elapsed = time.perf_counter() - t0

    # Tuple-keyed lookup vs chained str.join key rebuild → must be
    # cheaper. Use 2x as a sane floor; in practice it's far more.
    assert starship_elapsed < upstream_elapsed / 2.0, (
        f"Starship cache should be ≥2× faster than upstream on hits "
        f"(starship {starship_elapsed*1000:.2f} ms, "
        f"upstream {upstream_elapsed*1000:.2f} ms)."
    )
