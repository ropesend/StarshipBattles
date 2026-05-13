"""Per-player UI view-state container (issue #28).

In hot-seat play UI view-state (column visibility, sort selection,
expanded tab indices, scroll positions) leaks between players: hiding
a column as player 1 makes the column hidden when player 2 opens the
same window on their turn. This container partitions snapshots by
``empire.id`` so each player sees their own view choices.

The container is owned by :class:`StrategyGameStateManager`. The
manager calls :meth:`save` at turn-end (in ``advance_turn`` before
``_next_live_player_index`` mutates ``current_player_index``) and
:meth:`load` at turn-start (at the top of ``_apply_turn_start_state``,
before issue #25's defeat short-circuit). Windows that opt in expose
``SNAPSHOT_SLOT``, ``capture_view_state`` and ``apply_view_state``.

Storage is ``dict[int, dict[str, Any]]``: outer key is ``empire.id``,
inner dict is keyed by a window-supplied slot name (e.g. ``"planet_list"``,
``"empire_panel"``). Slot values are opaque dicts; the container does
not interpret them.

Lifecycle: session-scoped, not serialised — symmetric with #25's
non-serialised ``_defeated_player_ids``. A new player's first turn
returns ``None`` from :meth:`load` and the window stays at construction
defaults.
"""
from __future__ import annotations

from typing import Any


class PerPlayerUiState:
    """Slot-based per-empire UI snapshot store."""

    def __init__(self) -> None:
        self._by_empire: dict[int, dict[str, dict]] = {}

    def save(self, empire_id: int, slot: str, snapshot: dict) -> None:
        """Persist a snapshot under ``(empire_id, slot)``.

        Overwrites any prior snapshot in the same slot.
        """
        self._by_empire.setdefault(empire_id, {})[slot] = snapshot

    def load(self, empire_id: int, slot: str) -> dict | None:
        """Return the snapshot saved under ``(empire_id, slot)`` or ``None``.

        ``None`` means "no saved state" — windows treat that as "use defaults".
        """
        return self._by_empire.get(empire_id, {}).get(slot)

    def has(self, empire_id: int, slot: str) -> bool:
        """Return True when a snapshot exists for ``(empire_id, slot)``."""
        return slot in self._by_empire.get(empire_id, {})

    def discard(self, empire_id: int) -> None:
        """Remove all slots for ``empire_id``. No-op when unknown."""
        self._by_empire.pop(empire_id, None)
