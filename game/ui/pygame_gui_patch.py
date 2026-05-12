"""PROJ-411 Phase 3 Task 3.1: Starship-scoped fix for pygame_gui's
pathological ``UIAppearanceTheme.build_all_combined_ids`` cache key.

Background
----------

pygame_gui 0.6.14's ``UIAppearanceTheme.build_all_combined_ids`` at
``pygame_gui/core/ui_appearance_theme.py:1608`` caches results in
``self.unique_theming_ids``. The cache itself works, but the cache key
is built via chained ``str.join`` (``ui_appearance_theme.py:1625-1627``)
where each ``str(x)`` argument is the *separator* and each character of
the prior result is an element. The key balloons to ~10 KB per call;
~284 widgets × ~5 lookups per construction = ~15 MB of string
allocation per window open. Phase 1 cProfile attributed ~72 % (47 / 65 s)
of total open time to ``str.join`` + ``build_all_combined_ids``.

Approach
--------

Per the codex consult at
``AgentCoordination/Scratchpad/Consult/20260512T035945Z_pygame-gui-cache-key-patch/``,
we do NOT monkey-patch the upstream class. We:

1. Subclass ``UIAppearanceTheme`` → ``StarshipUIAppearanceTheme``,
   overriding ``build_all_combined_ids`` to use a private tuple-keyed
   cache (``self._combined_ids_cache``). pygame_gui's own
   ``unique_theming_ids: Dict[str, List[str]]`` is left untouched so we
   don't violate its declared type.
2. Subclass ``UIManager`` → ``StarshipUIManager``, overriding
   ``create_new_theme`` to return our theme subclass.
3. Migrate production ``pygame_gui.UIManager`` construction sites to
   use ``StarshipUIManager``. Tests still construct upstream
   ``pygame_gui.UIManager`` where they don't need the speedup.
4. Source-fingerprint guard: ``UPSTREAM_HAS_KNOWN_BUG`` inspects the
   upstream source at import time. When pygame_gui releases a fix the
   flag flips False; this is the cue to delete the patch entirely.

Pinning
-------

``requirements.txt`` pins ``pygame_gui==0.6.14`` (was ``>=0.6.9``).
Removal of this patch must coincide with a re-bump.
"""
from __future__ import annotations

import inspect
import os
from typing import List, Optional, Tuple, Union

from pygame_gui import UIManager
from pygame_gui.core.ui_appearance_theme import UIAppearanceTheme

# ---------------------------------------------------------------------------
# Source-fingerprint guard
# ---------------------------------------------------------------------------

# The unique sentinel string from pygame_gui 0.6.14's pathological cache
# key. If this string is gone from ``UIAppearanceTheme.build_all_combined_ids``
# source, upstream has fixed the bug and this patch should be removed
# (the subclass becomes a no-op cost; reverting to upstream is simpler).
_KNOWN_BUG_FINGERPRINT = "str(element_base_ids).join("


def _detect_upstream_bug() -> bool:
    try:
        src = inspect.getsource(UIAppearanceTheme.build_all_combined_ids)
    except (OSError, TypeError):
        # Source unavailable (frozen install, etc.) — assume the bug is
        # present so the speedup still applies.
        return True
    return _KNOWN_BUG_FINGERPRINT in src


UPSTREAM_HAS_KNOWN_BUG: bool = _detect_upstream_bug()


# ---------------------------------------------------------------------------
# Patched theme
# ---------------------------------------------------------------------------

# Tuple cache key — four positions matching the upstream signature.
_CacheKey = Tuple[
    Optional[Tuple[Optional[str], ...]],
    Optional[Tuple[Optional[str], ...]],
    Optional[Tuple[Optional[str], ...]],
    Optional[Tuple[Optional[str], ...]],
]


def _to_tuple(value):
    """Convert ``list | None`` → ``tuple | None`` for cache-key hashing."""
    if value is None:
        return None
    return tuple(value)


class StarshipUIAppearanceTheme(UIAppearanceTheme):
    """``UIAppearanceTheme`` with a private tuple-keyed cache.

    The upstream method's body is preserved otherwise — including the
    mismatched-length ``ValueError`` validation and the dotted-id
    suffix expansion loop. Only the cache lookup/key is swapped.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Private cache; outlives ``reload_theming`` like the upstream
        # ``unique_theming_ids`` does (the combined-id list depends on
        # element IDs, not on theme data).
        self._combined_ids_cache: dict[_CacheKey, List[str]] = {}

    def build_all_combined_ids(
        self,
        element_base_ids: Union[None, List[Union[str, None]]],
        element_ids: Union[None, List[str]],
        class_ids: Union[None, List[Union[str, None]]],
        object_ids: Union[None, List[Union[str, None]]],
    ) -> List[str]:
        cache_key: _CacheKey = (
            _to_tuple(element_base_ids),
            _to_tuple(element_ids),
            _to_tuple(class_ids),
            _to_tuple(object_ids),
        )
        cached = self._combined_ids_cache.get(cache_key)
        if cached is not None:
            return cached

        combined_ids: List[str] = []
        if (
            object_ids is not None
            and element_ids is not None
            and class_ids is not None
            and element_base_ids is not None
        ):
            if (
                len(object_ids) != len(element_ids)
                or len(class_ids) != len(element_ids)
                or len(element_base_ids) != len(element_ids)
            ):
                raise ValueError(
                    f"Object & class ID hierarchy is not equal in length to Element ID"
                    f" hierarchyElement IDs: {str(element_ids)}"
                    + "\nClass IDs: "
                    + str(class_ids)
                    + "\n"
                    "\nObject IDs: " + str(object_ids) + "\n"
                )
            if len(element_ids) != 0:
                # Reuse upstream's recursive id-tree walker — same
                # signature, same semantics.
                self._get_next_id_node(  # type: ignore[attr-defined]
                    None,
                    element_base_ids,
                    element_ids,
                    class_ids,
                    object_ids,
                    0,
                    len(element_ids),
                    combined_ids,
                )

            found_all_ids = False
            current_ids = combined_ids[:]
            while not found_all_ids:
                if len(current_ids) > 0:
                    for index, current_id in enumerate(current_ids):
                        found_full_stop_index = current_id.find(".")
                        if found_full_stop_index == -1:
                            found_all_ids = True
                        else:
                            current_ids[index] = current_id[found_full_stop_index + 1:]
                            combined_ids.append(current_ids[index])
                else:
                    found_all_ids = True

        self._combined_ids_cache[cache_key] = combined_ids
        return combined_ids


# ---------------------------------------------------------------------------
# Patched manager
# ---------------------------------------------------------------------------

class StarshipUIManager(UIManager):
    """``UIManager`` whose ``create_new_theme`` returns ``StarshipUIAppearanceTheme``.

    ``UIManager.__init__`` invokes ``create_new_theme`` (via the
    upstream code path that constructs ``self.ui_theme``), so the
    subclass automatically supplies the fixed theme without further
    wiring at call sites.
    """

    def create_new_theme(
        self,
        theme_path=None,
    ) -> StarshipUIAppearanceTheme:
        theme = StarshipUIAppearanceTheme(self.resource_loader, self._locale)
        if theme_path is not None:
            theme.load_theme(theme_path)
        return theme


__all__ = [
    "StarshipUIAppearanceTheme",
    "StarshipUIManager",
    "UPSTREAM_HAS_KNOWN_BUG",
]
