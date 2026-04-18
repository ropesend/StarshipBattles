"""Module-level accessor for the Combat Lab scenario_role registry (PROJ-278).

Provides `get_default_combat_lab_role_registry() -> RoleRegistry` — a
read-only `RoleRegistry` instance loaded from `combat_lab/data/scenario_roles.json`.

Combat Lab scenario_role labels (`attacker`, `target`, `ship1`, etc.) are
positional wiring identifiers used by `scenario.wire_ships(ships_by_role, ...)`
to find each ship's role in a test setup. They are NOT gameplay concepts —
players never see them, and the canonical list is owned by Combat Lab itself.

Relationship to gameplay design_role:
  - Same `RoleRegistry` machinery (`game.core.roles`)
  - Different instance, loaded from different file
  - This instance has `allow_runtime_add=False` — `add_user_role()` raises
    `RoleRegistryReadOnlyError`. (Gameplay design_role allows runtime add
    because players might add new roles during play; that doesn't apply here.)

Adding a new template that references a new role label REQUIRES adding the
role to `combat_lab/data/scenario_roles.json` — the consistency test in
`tests/unit/combat_lab/test_scenario_roles_consistency.py` will fail otherwise.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from game.core.roles import RoleRegistry

logger = logging.getLogger(__name__)


_DATA_FILE: Path = (
    Path(__file__).parent / "data" / "scenario_roles.json"
)

_default: Optional[RoleRegistry] = None


def get_default_combat_lab_role_registry() -> RoleRegistry:
    """Return the module-level Combat Lab role registry, lazy-constructed
    on first access. Subsequent calls return the same instance.
    """
    global _default
    if _default is None:
        _default = _build_default()
    return _default


def set_default_combat_lab_role_registry(registry: RoleRegistry) -> None:
    """Override the default registry (typically for tests).

    Subsequent `get_default_combat_lab_role_registry()` calls return
    `registry` until `reset_default_combat_lab_role_registry()` is called.
    """
    global _default
    _default = registry


def reset_default_combat_lab_role_registry() -> None:
    """Clear the cached default registry. Next `get_default_*` call will
    lazy-construct a fresh registry from the data file.
    """
    global _default
    _default = None


def _build_default() -> RoleRegistry:
    """Construct a read-only RoleRegistry loaded from the canonical Combat
    Lab scenario_roles data file.

    No mod overlay, no user overlay — Combat Lab roles are static. Players
    don't write Combat Lab scenarios, so runtime add is meaningless.
    """
    registry = RoleRegistry(allow_runtime_add=False)
    registry.load_from_file(_DATA_FILE, source_tag="combat_lab")
    logger.info(
        "combat_lab_role_registry: loaded %d scenario roles", len(registry.all())
    )
    return registry


__all__ = [
    "get_default_combat_lab_role_registry",
    "set_default_combat_lab_role_registry",
    "reset_default_combat_lab_role_registry",
]
