"""Shared Role schema + RoleRegistry machinery (PROJ-278).

Two registry instances exist in the running app:
  - `design_role_registry` (gameplay archetypes — carrier / interceptor / etc.)
    layered base + mods + user overlay; supports runtime `add_user_role`.
  - `combat_lab_role_registry` (Combat Lab scenario wiring labels —
    attacker / target / ship1 / ship2). Static, no runtime add.

Both share this schema and registry implementation. Per
`Projects/active_projects/PROJ-278/design.md`, Combat Lab and gameplay roles
serve different purposes (positional vs descriptive) — sharing the *machinery*
is a clean win, sharing *instances* would conflate two orthogonal axes.

Layer rule: this module lives in `game.core`, so every layer (Combat Lab, UI,
strategy, simulation) can import it without violating dependency rules.

JSON file format consumed by `RoleRegistry.load_from_file`:

    {
        "_comment": "optional — _-prefixed keys are skipped",
        "roles": [
            {
                "id": "carrier",
                "display_name": "Carrier",
                "description": "Hangar-bay focused capital ship.",
                "vehicle_type_filter": ["Battleship", "Cruiser"]
            }
        ]
    }

`vehicle_type_filter` is optional; defaults to empty (no filter).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Tuple, Union

from game.core.exceptions import StateException
from game.core.json_utils import load_json_required

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Role:
    """One role definition.

    `id` is the canonical lookup key; `display_name` and `description` are
    UI-facing text. `vehicle_type_filter` is an optional whitelist of vehicle
    type strings — empty tuple means the role accepts any vehicle type
    (Combat Lab scenario roles always leave this empty).
    """

    id: str
    display_name: str
    description: str
    vehicle_type_filter: Tuple[str, ...] = ()


class RoleRegistryReadOnlyError(StateException):
    """Raised when `add_user_role` is called on a registry that disallows
    runtime mutation (e.g. `combat_lab_role_registry`).

    PROJ-466: inherits from ``StateException`` (and thus ``GameException``)
    so it participates in the ``code`` / ``context`` contract instead of
    bypassing the hierarchy as a bare ``Exception`` subclass.
    """


class RoleRegistry:
    """Generic registry of `Role` objects.

    Two distinct instances live in the running app — one for gameplay
    `design_role` (`allow_runtime_add=True`), one for Combat Lab
    `scenario_role` (`allow_runtime_add=False`).

    Loading:
        `load_from_file(path, source_tag)` reads a `{"roles": [...]}` JSON
        file and merges it into the registry. Multiple calls layer in
        priority order — later sources override earlier ones for the same
        role id (precedence: base < mods < user overlay).

    Runtime add:
        `add_user_role(role)` inserts a new role at the highest precedence
        (overrides any loaded role with the same id). Fires every
        registered invalidation callback so subsystems caching role-derived
        data can refresh. Raises `RoleRegistryReadOnlyError` if the
        registry was constructed with `allow_runtime_add=False`.

    Invalidation:
        Subsystems that cache role-derived data (e.g. AI behavior dispatch,
        formation defaults) should call `register_invalidation_callback(cb)`
        at construction time. The callback fires every time `add_user_role`
        succeeds. Loading from file does NOT fire invalidation — that's
        initialization, not mutation.
    """

    def __init__(self, *, allow_runtime_add: bool):
        self._roles: Dict[str, Role] = {}
        self._allow_runtime_add = allow_runtime_add
        self._invalidation_callbacks: List[Callable[[], None]] = []
        # Re-entrance guard: prevents stack overflow if a callback
        # itself calls add_user_role. Closure audit (PROJ-278) flagged
        # this as a real edge case even though no current users hit it.
        self._firing_callbacks: bool = False

    def __contains__(self, role_id: str) -> bool:
        return role_id in self._roles

    def get(self, role_id: str) -> Role:
        """Return the Role for `role_id`. Raises `KeyError` if missing."""
        return self._roles[role_id]

    def all(self) -> List[Role]:
        """Return all roles, sorted by id for deterministic iteration."""
        return [self._roles[k] for k in sorted(self._roles.keys())]

    def get_roles_for_vehicle_type(self, vehicle_type: str) -> List[Role]:
        """Return roles whose `vehicle_type_filter` accepts `vehicle_type`.

        A role with empty `vehicle_type_filter` matches ANY vehicle type
        (no restriction). Result is sorted by `display_name` for stable
        UI ordering.
        """
        matches = [
            role for role in self._roles.values()
            if not role.vehicle_type_filter or vehicle_type in role.vehicle_type_filter
        ]
        matches.sort(key=lambda r: r.display_name)
        return matches

    def load_from_file(self, path: Union[str, Path], source_tag: str) -> None:
        """Load roles from a JSON file at `path`.

        `source_tag` is informational (used in log messages identifying
        precedence layers like "base", "mod:foo", "user"). Later calls
        override earlier ones for the same role id.

        Raises:
            FileNotFoundError: if `path` does not exist
            json.JSONDecodeError: if the file is not valid JSON
        """
        path = Path(path)
        data = load_json_required(path)

        roles_list = data.get("roles", [])
        for role_dict in roles_list:
            role = self._role_from_dict(role_dict)
            if role.id in self._roles:
                logger.debug(
                    "RoleRegistry: %r overrides existing entry "
                    "(source=%s, path=%s)",
                    role.id, source_tag, path,
                )
            self._roles[role.id] = role

    def load_from_file_optional(self, path: Union[str, Path], source_tag: str) -> None:
        """Load roles from `path` if it exists; silently no-op if it doesn't.

        Used for the user-overlay layer (e.g. `user_data/design_roles.json`)
        which won't exist on first run. Malformed JSON still raises — only
        missingness is tolerated, not corruption.

        Raises:
            json.JSONDecodeError: if the file exists but is not valid JSON
        """
        path = Path(path)
        if not path.exists():
            logger.debug(
                "RoleRegistry: optional file not present (source=%s, path=%s)",
                source_tag, path,
            )
            return
        self.load_from_file(path, source_tag=source_tag)

    def add_user_role(self, role: Role) -> None:
        """Register `role` at runtime; fires invalidation callbacks.

        Raises:
            RoleRegistryReadOnlyError: if this registry was constructed
                with `allow_runtime_add=False`.
        """
        if not self._allow_runtime_add:
            raise RoleRegistryReadOnlyError(
                f"Registry is read-only; cannot add role {role.id!r} at runtime"
            )
        self._roles[role.id] = role
        self._fire_invalidation_callbacks()

    def register_invalidation_callback(self, cb: Callable[[], None]) -> None:
        """Register `cb` to be invoked after every successful `add_user_role`.

        Callback exceptions are caught and logged — a misbehaving subscriber
        cannot block role registration or prevent other callbacks from firing.
        """
        self._invalidation_callbacks.append(cb)

    # ---- internals -------------------------------------------------------

    @staticmethod
    def _role_from_dict(role_dict: dict) -> Role:
        """Build a Role from a JSON dict, skipping `_`-prefixed keys.

        Per project convention (memory: "_-prefixed JSON keys are skipped
        during formula parsing — prevents `_comment` section-header spam"),
        any key starting with `_` is treated as a comment and ignored.
        """
        cleaned = {k: v for k, v in role_dict.items() if not k.startswith("_")}
        vehicle_filter = cleaned.get("vehicle_type_filter", ())
        return Role(
            id=cleaned["id"],
            display_name=cleaned["display_name"],
            description=cleaned["description"],
            vehicle_type_filter=tuple(vehicle_filter),
        )

    def _fire_invalidation_callbacks(self) -> None:
        """Fire every registered callback; log + swallow exceptions.

        Guarded against re-entrance: if a callback itself calls
        `add_user_role`, the inner mutation still succeeds but does NOT
        re-fire callbacks (would cause stack overflow). Outer firing loop
        continues unaffected.
        """
        if self._firing_callbacks:
            logger.warning(
                "RoleRegistry: re-entrant add_user_role detected during "
                "invalidation firing; mutation applied but nested "
                "invalidation suppressed to prevent recursion"
            )
            return
        self._firing_callbacks = True
        try:
            for cb in self._invalidation_callbacks:
                try:
                    cb()
                except Exception:  # Intentional broad catch: subscriber callbacks may raise anything; one bad subscriber must not abort the rest of the invalidation fan-out
                    logger.exception(
                        "RoleRegistry: invalidation callback %r raised; "
                        "continuing to fire remaining callbacks",
                        cb,
                    )
        finally:
            self._firing_callbacks = False


__all__ = [
    "Role",
    "RoleRegistry",
    "RoleRegistryReadOnlyError",
]
