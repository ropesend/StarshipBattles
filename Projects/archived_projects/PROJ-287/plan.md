# PROJ-287: Race Registry Facade + Empire.resident_species

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-287` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-287 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. `IRaceRegistry` protocol + `CachedRaceRegistry` impl | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Facade exposure: `StrategySessionFacade.get_race_registry()` | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `Empire.resident_species()` derived helper | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Docs + cleanup | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** ALL 4 PHASES COMPLETE — awaiting user sign-off
**Last Action:** Phase 4 done. Added a `### Race Registry (PROJ-287)` subsection to `docs/04_SERVICES.md` after the PROJ-285 Colony Economy Multiplier section covering: the `IRaceRegistry` protocol + its single method, `CachedRaceRegistry` implementation (hit + None caching, no locks, manual invalidation), the `StrategySessionFacade.get_race_registry()` lazy-init accessor, the race-editor invalidation discipline via `RaceSetupScreen`'s optional `race_registry` kwarg, and `Empire.resident_species()` as the companion API. Task 4.3 (patterns doc) skipped per its own "optional" flag — Pattern 6 CQRS-lite description already covers the facade read pattern. Task 4.1 was completed back in Phase 1 (IRaceRegistry in `docs/01_ARCHITECTURE.md § Key Protocols`; export count 45 → 46). Ran the full sharded suite: 14984/14985 passed in 137.4s across 12 shards. Single failure is the known pre-existing flake `test_copy_designs_without_themes_preserves_original` (theme bleed between fixtures) flagged in the handoff as not a PROJ-287 regression. Net new across all four phases: 19 tests.
**Next Action:** None — hand back to user for sign-off and to close PROJ-287 out in `projects_index.md`. Consumers PROJ-288, PROJ-289, PROJ-290 are unblocked and can begin.
**Blockers:** None.
**Context for Next Agent:** The three deliverables are complete and wired:
  1. `IRaceRegistry` protocol (`game/core/protocols.py`) + `CachedRaceRegistry` impl (`game/strategy/systems/race_library.py`) — cache hits AND None results; manual `invalidate(race_id=None)`.
  2. `StrategySessionFacade.get_race_registry() -> IRaceRegistry` — lazy-init, session-scoped; used by consumers pulling race configs once per session. `RaceSetupScreen.__init__` accepts an optional `race_registry` kwarg; `_do_save()` invalidates on successful save when supplied. Current pre-game callers (`app.py`, `new_game_setup_screen.py`) pass no registry — no behaviour change.
  3. `Empire.resident_species() -> Set[str]` (`game/strategy/data/empire.py`) — returns `race_id`s with `count >= 1` on ANY colony. Not cached.
  Engines (`PopulationEngine`, `HappinessEngine`) keep their own `_get_race_config` helpers — explicitly out of scope per decisions.md 2026-04-18. No save-format changes. Suite green (excluding pre-existing flake). Docs updated: `01_ARCHITECTURE.md` (Phase 1), `04_SERVICES.md` (Phase 4). `02_PATTERNS.md` intentionally not touched (noise). Final validator: `python Projects/scripts/validate_phase.py PROJ-287 4`.

## Overview

Add a cached race-registry protocol + facade exposure so UI panels can resolve `race_id → RaceConfig` without hitting the filesystem per call. Add `Empire.resident_species() -> Set[str]` as the canonical "which species live in this empire" query used by all downstream UI projects (notably PROJ-290's uncolonized-habitability display).

## Goals

- `IRaceRegistry` protocol at `game/core/protocols.py` — one method: `get_race(race_id: str) -> Optional[RaceConfig]`.
- `CachedRaceRegistry` implementation at `game/strategy/systems/race_library.py` (or a new sibling file) — wraps `RaceLibrary`, caches results on first access, exposes an `invalidate()` method for race-editor save flows.
- `StrategySessionFacade.get_race_registry() -> IRaceRegistry` — single shared instance per session.
- `Empire.resident_species() -> Set[str]` — derived property returning race_ids with `count >= 1` across `self.colonies`.
- Existing `PopulationEngine._get_race_config` + `HappinessEngine._get_race_config` can OPTIONALLY migrate to read from the registry (out of scope if risky; defer).
- Full sharded suite green.

## Scope

**In:**
- `IRaceRegistry` protocol + `CachedRaceRegistry` class + tests.
- `StrategySessionFacade.get_race_registry()` method.
- `Empire.resident_species()` helper + tests.
- Cache invalidation hook + one caller (race-save flow) that invokes it.
- Unit tests for the cache: first-call loads from library, second-call uses cache, invalidate() clears.

**Out:**
- Replacing `RaceLibrary` itself (file-backed) — the registry wraps it.
- Migrating `PopulationEngine` / `HappinessEngine` to use the new registry — they already have working race-config resolution. Optional future cleanup.
- Multi-race engine support (some future feature where engines iterate `resident_species()` themselves). Out of scope.

## Key Files

| Component | File Path |
|-----------|-----------|
| `IRaceRegistry` protocol | `game/core/protocols.py` |
| `CachedRaceRegistry` implementation | `game/strategy/systems/race_library.py` or new `race_registry.py` |
| `StrategySessionFacade.get_race_registry` | `game/strategy/facade/strategy_session_facade.py` |
| `Empire.resident_species` | `game/strategy/data/empire.py` |

## Related Documents
- [design.md](design.md) — Architecture rationale (cache strategy, invalidation)
- [decisions.md](decisions.md) — Decisions log
- [manifest.md](manifest.md) — Full file manifest

## Related Projects

| PROJ | Relationship |
|------|--------------|
| PROJ-286 | Parallel — no overlap (different files) |
| PROJ-288 | Consumer — uses `get_race_registry()` + `resident_species()` for projection helpers |
| PROJ-289 | Consumer — planet report panel iterates species on a colony, resolves race_config via registry |
| PROJ-290 | Consumer — uncolonized habitability iterates `empire.resident_species()` and scores each against the planet |

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing via `python Tools/test_sharded/test_sharded.py`
- [ ] Manual scenario:
  - [ ] Start game → open strategy screen → confirm no new per-frame filesystem reads (check via logging that `RaceLibrary.get_race` is called once per race_id per session).
  - [ ] Edit a race in the race editor, save → confirm the registry invalidates and the next read returns fresh data.
- [ ] User verified end-to-end.
