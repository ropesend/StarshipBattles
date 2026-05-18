"""Grouped facade namespaces (PROJ-430 / TD-08 Phase 2).

Thin wrappers that expose each facade slice's public verbs through a
domain-grouped surface on ``StrategySessionFacade``:

- ``facade.commands.<verb>(...)`` — write-path command helpers (the 36
  former ``dispatch_*`` helpers, prefix stripped).
- ``facade.fleets.<verb>(...)`` / ``planets`` / ``systems`` / ``empires`` /
  ``events`` / ``session_meta`` / ``economy`` / ``validation`` — read paths
  with the redundant ``get_`` prefix and domain-noun prefix stripped where
  unambiguous.

Each namespace dataclass takes the underlying slice at construction. The
facade composer holds one instance per group as a per-facade attribute and
exposes it through a ``@property``. The slices themselves are unchanged —
this file is a re-export layer, no behavior moves here.

Phase 5 (PROJ-430) deletes the legacy flat helpers from the facade; from
that point on these namespaces are the only path to the slice verbs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterable, List, Optional, Tuple

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.facade.dto import (
    BuildQueueSourceDTO,
    ColonyDemographicView,
    ColonySummary,
    ContainerSnapshotInfo,
    EmpireInfo,
    FleetInfo,
    FleetSummary,
    PlanetInfo,
    StarInfo,
    SystemInfo,
)

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.core.registry import GameRegistries
    from game.strategy.config.economy_config import EconomyConfig
    from game.strategy.engine.commands import Command
    from game.strategy.facade.slices._facade_state import FacadeSessionState
    from game.strategy.facade.slices.command_dispatch_slice import (
        CommandDispatchSlice,
    )
    from game.strategy.facade.slices.economy_slice import EconomySlice
    from game.strategy.facade.slices.empire_slice import EmpireSlice
    from game.strategy.facade.slices.event_slice import EventSlice
    from game.strategy.facade.slices.fleet_slice import FleetSlice
    from game.strategy.facade.slices.planet_slice import PlanetSlice
    from game.strategy.facade.slices.system_slice import SystemSlice


# ---------------------------------------------------------------------------
# Commands (write path)
# ---------------------------------------------------------------------------


class FacadeCommands:
    """Grouped command-dispatch surface.

    Wraps :class:`CommandDispatchSlice` and exposes each registered command
    helper with the ``dispatch_`` prefix stripped (e.g.
    ``commands.issue_move(...)`` proxies to ``dispatch_issue_move`` on the
    slice).

    ``__init__`` accepts the iterable of ``(helper_name, command_class)``
    pairs as a parameter rather than importing ``command_registry`` directly,
    so a TD-03 reshape of ``specs_by_facade_helper()`` is decoupled from this
    namespace.
    """

    __slots__ = ("_slice", "_verb_to_helper")

    def __init__(
        self,
        slice_: "CommandDispatchSlice",
        helper_pairs: Iterable[Tuple[str, type]],
    ) -> None:
        self._slice = slice_
        # Build verb -> dispatch_<helper_name> map once. The slice's
        # ``__getattr__`` resolves the helper on each call, so we don't
        # need to materialise closures here.
        self._verb_to_helper: dict[str, str] = {}
        for helper_name, _command_cls in helper_pairs:
            assert helper_name.startswith("dispatch_"), helper_name
            verb = helper_name[len("dispatch_"):]
            self._verb_to_helper[verb] = helper_name

    def __getattr__(self, verb: str) -> Callable[..., ValidationResult]:
        # Avoid infinite recursion: ``_verb_to_helper`` and ``_slice`` go
        # through ``__getattribute__`` normally because they're in
        # ``__slots__``.
        try:
            helper_name = self._verb_to_helper[verb]
        except KeyError as exc:
            raise AttributeError(
                f"FacadeCommands has no command verb {verb!r}. Available: "
                f"{sorted(self._verb_to_helper.keys())[:5]}..."
            ) from exc
        return getattr(self._slice, helper_name)

    def __dir__(self) -> list[str]:
        # Make ``hasattr(commands, verb)`` and the public-API contract
        # test's ``dir()`` walk see every verb without having to call
        # ``__getattr__`` once per verb.
        return sorted(list(self._verb_to_helper.keys()) + ["_slice"])


# ---------------------------------------------------------------------------
# Fleets
# ---------------------------------------------------------------------------


class FacadeFleetQueries:
    """Grouped fleet read surface."""

    __slots__ = ("_slice",)

    def __init__(self, slice_: "FleetSlice") -> None:
        self._slice = slice_

    def get(self, fleet_id: int) -> Optional[FleetInfo]:
        """Get fleet information by ID."""
        return self._slice.get_fleet(fleet_id)

    def at_hex(self, hex_coord: HexCoord) -> List[FleetInfo]:
        """Get all fleets at a specific hex coordinate."""
        return self._slice.get_fleets_at_hex(hex_coord)

    def path_preview(
        self, fleet_id: int, target_hex: HexCoord
    ) -> Optional[List[HexCoord]]:
        """Calculate a path preview for a fleet to a target."""
        return self._slice.get_fleet_path_preview(fleet_id, target_hex)

    def path_projection(
        self, fleet_id: int, max_turns: int = 50
    ) -> List[dict]:
        """Get turn-by-turn path projection for a fleet."""
        return self._slice.get_fleet_path_projection(fleet_id, max_turns)

    def remaining_pods(self, fleet_id: int) -> dict:
        """Get remaining colony pods for a fleet."""
        return self._slice.get_fleet_remaining_pods(fleet_id)

    def get_containers(
        self, fleet_id: int,
    ) -> Tuple[ContainerSnapshotInfo, ...]:
        """Container snapshots for each ship in the fleet (PROJ-437 Phase 1a)."""
        return self._slice.get_fleet_containers(fleet_id)


# ---------------------------------------------------------------------------
# Planets
# ---------------------------------------------------------------------------


class FacadePlanetQueries:
    """Grouped planet read surface."""

    __slots__ = ("_slice",)

    def __init__(self, slice_: "PlanetSlice") -> None:
        self._slice = slice_

    def get(self, planet_id: int) -> Optional[PlanetInfo]:
        """Get planet information by ID."""
        return self._slice.get_planet(planet_id)

    def at_hex(self, hex_coord: HexCoord) -> List[PlanetInfo]:
        """Get planets whose global position matches the given hex."""
        return self._slice.get_planets_at_hex(hex_coord)

    def get_containers(
        self, planet_id: int,
    ) -> Tuple[ContainerSnapshotInfo, ...]:
        """Container snapshots for the planet's stockpile + staging yard
        (PROJ-437 Phase 1a)."""
        return self._slice.get_planet_containers(planet_id)


# ---------------------------------------------------------------------------
# Systems / stars / storms
# ---------------------------------------------------------------------------


class FacadeSystemQueries:
    """Grouped system / star / storm read surface."""

    __slots__ = ("_slice",)

    def __init__(self, slice_: "SystemSlice") -> None:
        self._slice = slice_

    def all(self) -> List[SystemInfo]:
        """Information about every star system in the galaxy."""
        return self._slice.get_all_systems()

    def all_stars(self) -> List[StarInfo]:
        """Information about every star in the galaxy (per-turn cached)."""
        return self._slice.get_all_stars()

    def at_hex(self, hex_coord: HexCoord) -> Optional[SystemInfo]:
        """System at a specific global hex coordinate."""
        return self._slice.get_system_at_hex(hex_coord)

    def containing_fleet(self, fleet_id: int) -> Optional[SystemInfo]:
        """System containing (or closest to) a fleet."""
        return self._slice.get_system_containing_fleet(fleet_id)

    def near_hex(
        self, hex_coord: HexCoord, max_dist: int = 8
    ) -> Optional[SystemInfo]:
        """System at or near a hex coordinate."""
        return self._slice.get_system_near_hex(hex_coord, max_dist)

    def storm_names_at_hex(self, hex_coord: HexCoord) -> List[str]:
        """Storm names affecting a global hex coordinate."""
        return self._slice.get_storm_names_at_hex(hex_coord)


# ---------------------------------------------------------------------------
# Empires
# ---------------------------------------------------------------------------


class FacadeEmpireQueries:
    """Grouped empire read surface."""

    __slots__ = ("_slice",)

    def __init__(self, slice_: "EmpireSlice") -> None:
        self._slice = slice_

    def all(self) -> List[EmpireInfo]:
        """Information about every empire."""
        return self._slice.get_all_empires()

    def get(self, empire_id: int) -> Optional[EmpireInfo]:
        """Get empire information by ID."""
        return self._slice.get_empire(empire_id)

    def colonies(self, empire_id: int) -> List[ColonySummary]:
        """Colony summaries for an empire."""
        return self._slice.get_empire_colonies(empire_id)

    def fleets(self, empire_id: int) -> List[FleetSummary]:
        """Fleet summaries for an empire."""
        return self._slice.get_empire_fleets(empire_id)

    def build_queues(self, empire_id: int) -> List[BuildQueueSourceDTO]:
        """All build queue sources for an empire."""
        return self._slice.get_empire_build_queues(empire_id)

    def hex_build_queues(
        self, empire_id: int, hex_coord: HexCoord
    ) -> List[BuildQueueSourceDTO]:
        """All build queue sources at a hex for a specific empire."""
        return self._slice.get_hex_build_queues(empire_id, hex_coord)


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


class FacadeEventQueries:
    """Grouped event-log read surface."""

    __slots__ = ("_slice",)

    def __init__(self, slice_: "EventSlice") -> None:
        self._slice = slice_

    def turn_events(
        self, turn: Optional[int] = None, *, empire_id: Optional[int] = None
    ) -> List[dict]:
        """Events for a specific turn (current turn if ``None``)."""
        return self._slice.get_turn_events(turn, empire_id=empire_id)

    def all(self, *, empire_id: Optional[int] = None) -> List[dict]:
        """Every event in the log (optionally scoped to an empire)."""
        return self._slice.get_all_events(empire_id=empire_id)

    def by_category(
        self, category: str, *, empire_id: Optional[int] = None
    ) -> List[dict]:
        """Events filtered by category (optionally scoped to an empire)."""
        return self._slice.get_events_by_category(category, empire_id=empire_id)


# ---------------------------------------------------------------------------
# Session metadata
# ---------------------------------------------------------------------------


class FacadeSessionInfo:
    """Grouped session-metadata surface."""

    __slots__ = ("_slice", "_session")

    def __init__(self, slice_: "EventSlice", session) -> None:
        # ``EventSlice`` historically also hosted the plain session reads;
        # we re-use it here rather than introduce a fifth slice.
        self._slice = slice_
        # ``registries`` is sourced from the session directly (the legacy
        # ``get_registries`` was a session passthrough, not a slice method);
        # captured here so the namespace owns its DI.
        self._session = session

    def turn_number(self) -> int:
        """Current turn number (1-indexed)."""
        return self._slice.get_turn_number()

    def save_path(self) -> Optional[str]:
        """Current save game file path, or ``None`` if unsaved."""
        return self._slice.get_save_path()

    def human_player_ids(self) -> List[int]:
        """Empire IDs of human players."""
        return self._slice.get_human_player_ids()

    def registries(self) -> "GameRegistries":
        """Session-scoped ``GameRegistries`` bundle (PROJ-382 Phase 1).

        Generic DI accessor — kept on session_meta rather than economy so
        the economy namespace stays focused on economy/demographics
        concerns. Moved off ``economy`` in PROJ-430 Phase 7 after Codex
        consult flagged it as a cross-concern leak.
        """
        return self._session.registries


# ---------------------------------------------------------------------------
# Economy / demographics
# ---------------------------------------------------------------------------


class FacadeEconomyQueries:
    """Grouped economy / demographics surface."""

    __slots__ = ("_slice",)

    def __init__(self, slice_: "EconomySlice") -> None:
        self._slice = slice_

    def race_registry(self) -> "IRaceRegistry":
        """Session-scoped race registry (lazy)."""
        return self._slice.get_race_registry()

    def colony_demographic_view(
        self, planet_id: int
    ) -> Optional[ColonyDemographicView]:
        """One-shot snapshot of a colony's demographics."""
        return self._slice.get_colony_demographic_view(planet_id)

    def resolve_config(self) -> "EconomyConfig":
        """Active ``EconomyConfig`` for the session (lazy fallback)."""
        return self._slice.resolve_economy_config()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class FacadeValidation:
    """Grouped validation surface (read-only safety checks)."""

    __slots__ = ("_fleet_slice", "_planet_slice")

    def __init__(
        self, fleet_slice: "FleetSlice", planet_slice: "PlanetSlice"
    ) -> None:
        self._fleet_slice = fleet_slice
        self._planet_slice = planet_slice

    def can_colonize(
        self, fleet_id: int, planet_id: Optional[int]
    ) -> ValidationResult:
        """Check if a fleet can colonize a planet."""
        return self._planet_slice.can_colonize(fleet_id, planet_id)

    def can_move_to(
        self, fleet_id: int, target_hex: HexCoord
    ) -> ValidationResult:
        """Check if a fleet can move to a target hex."""
        return self._fleet_slice.can_move_to(fleet_id, target_hex)


__all__ = [
    "FacadeCommands",
    "FacadeFleetQueries",
    "FacadePlanetQueries",
    "FacadeSystemQueries",
    "FacadeEmpireQueries",
    "FacadeEventQueries",
    "FacadeSessionInfo",
    "FacadeEconomyQueries",
    "FacadeValidation",
]
