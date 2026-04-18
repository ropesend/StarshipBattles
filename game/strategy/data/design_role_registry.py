"""Module-level accessor for the gameplay design_role registry (PROJ-278).

Provides `get_default_design_role_registry() -> RoleRegistry` with layered
loading from base + mods + user overlay. Follows the same module-level
accessor pattern as other ApplicationContext-managed services
(`get_default_xxx` / `set_default_xxx` / `reset_default_xxx`).

Layered load order (later overrides earlier for the same role id):
  1. `data/design_roles.json` (base — modders edit this directly)
  2. `mods/<mod_name>/design_roles.json` (mod overlays — directory may not exist)
  3. `output/design_roles_overlay.json` (user overlay — may not exist on first run)

The returned `RoleRegistry` has `allow_runtime_add=True`, so subsystems can
register player-added roles via `add_user_role(role)`. Subsystems that cache
role-derived data should call `register_invalidation_callback(cb)` so they
refresh when the registry mutates.

Layer rule: this module lives in `game.strategy.data` because it knows about
file paths under `data/`, `mods/`, and `output/` — domain-specific concerns
that don't belong in the generic `game.core.roles` machinery.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from game.core.paths import Paths
from game.core.roles import RoleRegistry

logger = logging.getLogger(__name__)


_default: Optional[RoleRegistry] = None


def get_default_design_role_registry() -> RoleRegistry:
    """Return the module-level design_role registry, lazy-constructed on
    first access. Subsequent calls return the same instance.
    """
    global _default
    if _default is None:
        _default = _build_default()
    return _default


def set_default_design_role_registry(registry: RoleRegistry) -> None:
    """Override the default registry (typically for tests).

    Subsequent `get_default_design_role_registry()` calls return `registry`
    until `reset_default_design_role_registry()` is called.
    """
    global _default
    _default = registry


def reset_default_design_role_registry() -> None:
    """Clear the cached default registry. Next `get_default_*` call will
    lazy-construct a fresh registry from data files.
    """
    global _default
    _default = None


def _build_default() -> RoleRegistry:
    """Build a fresh RoleRegistry by loading base, mods, and user overlay
    in priority order.
    """
    registry = RoleRegistry(allow_runtime_add=True)

    # Layer 1: base data file (required — raises if missing/malformed)
    registry.load_from_file(Paths.DESIGN_ROLES_FILE, source_tag="base")

    # Layer 2: mod overlays (optional directory)
    mods_dir = Path(Paths.MODS_DIR)
    if mods_dir.is_dir():
        for mod_overlay in sorted(mods_dir.glob("*/design_roles.json")):
            mod_name = mod_overlay.parent.name
            registry.load_from_file(
                mod_overlay, source_tag=f"mod:{mod_name}"
            )

    # Layer 3: user overlay (optional file — typically absent on first run)
    registry.load_from_file_optional(
        Paths.USER_DESIGN_ROLES_FILE, source_tag="user"
    )

    logger.info(
        "design_role_registry: loaded %d roles", len(registry.all())
    )
    return registry


__all__ = [
    "get_default_design_role_registry",
    "set_default_design_role_registry",
    "reset_default_design_role_registry",
]
