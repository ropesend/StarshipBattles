# PROJ-474: Value/config UI-safe read-surface allowlist consolidation (follow-on from PROJ-472)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-474` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-474 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Codify the UI-safe surface as machine-checkable data + reconcile drift + promote misfiled TAIL entries | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Codex exec-audit follow-ups (Finding 1 doc-drift + Finding 2 durable non-vacuity proof + parser hardening) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-22
**Active Phase:** Phases 1 + 2 complete — awaiting user verification.
**Last Action:** Implemented all 7 Phase-1 tasks via strict TDD: symbol-level `_UISAFE_SYMBOLS` (33 `(module, member)` pairs) + matcher branch; reconciled the 3 drifts; doc↔guard parity test + parseable fenced token block in Pattern #5; promoted the 12 misfiled TAIL symbols (RED step confirmed the no-misfile invariant fires); deleted the annotation-only `EmpireEconomySnapshot` runtime import (moved under `TYPE_CHECKING`); symbol-level positive control. Ran one-round Codex exec-audit: 2 VERIFIED findings + 1 minor robustness risk fixed in Phase 2; `get_default_economy_config` mutable-dict risk REJECTED (Codex recommended keeping the promotion). Validation: read-path imports guard 344 passed; all static guards 1399 passed; full sharded suite 24243 passed / 0 failed.
**Next Action:** User verification, then orchestrator commit. (Agent did NOT commit per instructions.)
**Blockers:** None.

## Overview
Follow-on from **PROJ-472**, which landed the read-path policy (option (b):
documented UI-safe read surface + static guard + exact allowlist) and two static
guards. PROJ-472 also *documented* the UI-safe surface in Pattern #5 and parked
those types in a `UISAFE`-**commented** block of the import-guard allowlist.

The work remaining for PROJ-474 is NOT writing more prose. The current
enforcement structure makes `UISAFE` a comment, not a checkable invariant
(`tests/static_guards/test_facade_read_path_imports_guard.py:63-118` — one flat
`frozenset` of `(file, module, member)` triples; category is conveyed only by a
section comment). That flat structure has **already drifted** (verified live
2026-05-22):
- `VALID_GALAXY_TYPES` is `UISAFE` in `new_game_setup_screen.py`
  (`...imports_guard.py:95`) but `TAIL` in `galaxy_test/galaxy_mode.py`
  (`...imports_guard.py:154`) — the same symbol, two categories.
- Pattern #5 names `RaceConfig` + `RacePointBudget` as UI-safe
  (`docs/02_PATTERNS.md:188-195`) but the race-setup imports of them sit in the
  `TAIL` block (`...imports_guard.py:181-182`, `:188-191`).
- `ComponentActivationState` is in the `UISAFE` block (`...imports_guard.py:104`)
  but Pattern #5 names only `ActivationPhase` (`docs/02_PATTERNS.md:190-193`).

PROJ-474 turns `UISAFE` into first-class **symbol-level data**, adds a doc↔guard
parity test and a no-misfile invariant, reconciles the existing drift, and
promotes the genuinely-detached value/config/enum/static-metadata symbols out of
`TAIL`. It STOPS before any live-reader or tooling migration (PROJ-475/476).

## Goals
- Make the UI-safe surface a machine-checkable `(module, member)` data structure
  (`_UISAFE_SYMBOLS`) the guard consults like the facade write-path prefix —
  replacing the comment-only `UISAFE` category. **Symbol-level, NOT module
  prefixes** (mixed modules like `race_description_llm_controller` carry both a
  safe enum and a live state-machine class — see Decisions).
- Add a **doc↔guard parity test**: `_UISAFE_SYMBOLS` must equal a parseable
  canonical token list embedded in Pattern #5, so neither can drift.
- Add a **no-misfile invariant**: no symbol in `_UISAFE_SYMBOLS` may also appear
  in the transitional (`TAIL`/`CLUSTER`/`FLEETCAP`) file-scoped allowlist.
- Reconcile the three known drifts above; promote the misfiled TAIL entries that
  meet the membership criteria (§ design.md). Keep the transitional allowlist
  file-scoped (the same symbol can be safe in one file, live in another).
- Decide the two open items in-pass: bless `ComponentActivationState` in the doc
  (it is a detached scalar+enum dataclass), and DELETE the
  `EmpireEconomySnapshot` runtime import (annotation-only → `TYPE_CHECKING`)
  rather than broaden policy for it.

## Scope
**In:**
- The value/config/enum/protocol read-surface as machine-checkable data + the
  Pattern #5 canonical token list + the two new invariant tests.
- Reconciling the known doc/guard drifts.
- Promoting the detached value/config/enum/static-metadata symbols listed in
  `design.md` §"Promote to UISAFE" out of the `TAIL` allowlist.
- Deleting the annotation-only `EmpireEconomySnapshot` runtime import.

**Out (deferred — see design.md §"Stay deferred"):**
- Live-session/service readers: `DesignValidator`, `EmpireEconomyService`,
  `compute_planet_production`, `calculate_habitability`, `component_abilities.*`,
  `FleetSpeedCalculator`, `system_effects_collector.*`, `FighterWing`/
  `SatelliteConstellation`, `FacilityAbilitySource`, `SectorEnvironment`,
  `DropPod`/`CarriedVehicle`, `cargo_transfer_service.*`, runtime `DesignCatalog`,
  live-`RaceLibrary`, `GameSession`, `SaveGameService`, `ReplayResolver`,
  `GalaxyPathfindingService` → **PROJ-475**.
- Tooling/editor/sandbox surfaces: `battle_setup` fleet/ship models, `galaxy_test`
  generation, `race_setup` `RaceLibrary`/`RaceRandomizer`/`RaceCaptionLoader`/
  `RaceDescriptionLLMController`, `get_default_design_role_registry`, tooling
  `DesignCatalog` browser → **PROJ-476**.
- Any facade-surface expansion or code motion in `game/ui/` beyond import-line
  edits (the `EmpireEconomySnapshot` `TYPE_CHECKING` move).
- The session-read guard (`test_facade_read_path_session_guard.py`) — unchanged
  by this project.

## Current State of the code (verified live 2026-05-22)
- `tests/static_guards/test_facade_read_path_imports_guard.py` is GREEN (340
  passed). `_IMPORT_ALLOWLIST` is one flat `frozenset` (`:66-222`); `UISAFE`
  block `:67-105`; `CLUSTER` `:107-112`; `FLEETCAP` `:114-116`; `TAIL`
  `:118-221`. The matcher allows the facade write path
  (`_is_always_allowed_module`, `:262-268`) and otherwise requires an exact
  triple (`:271-314`).
- Pattern #5 read-path policy: `docs/02_PATTERNS.md` `:168-230` (verified live
  2026-05-22). The UI-safe list is prose (`:188-199`) and declares itself
  "source of truth for the guard allowlist ... the `UISAFE` allowlist category
  must not drift from it."
- All cited `game/ui` use sites and `game/strategy` symbol definitions verified
  present at the lines cited in `design.md` (2026-05-22).

## Key Files
| Component | File Path | Verified refs (2026-05-22) |
|-----------|-----------|----------------------------|
| Read-path policy + UI-safe token list | `docs/02_PATTERNS.md` (Pattern #5) | `:168-230`; UI-safe prose `:188-199` |
| Runtime-import read guard + allowlist | `tests/static_guards/test_facade_read_path_imports_guard.py` | flat set `:66-222`; matcher `:262-314` |
| `game_config` scalars (incl. `VALID_GALAXY_TYPES`) | `game/strategy/engine/game_config.py` | `THEME_DEFAULTS:28`, `VALID_GALAXY_TYPES:39`, `DEFAULT_SYSTEM_COUNT:55` |
| `RaceConfig` (detached config dataclass) | `game/strategy/data/race_config.py` | `class RaceConfig:90` |
| `RacePointBudget` (detached cost calc) | `game/strategy/data/race_point_budget.py` | `class:35` |
| `OrderType` (pure enum) | `game/strategy/data/order_types.py` | `class:18` |
| `PlanetType` (pure enum) | `game/strategy/data/planet.py` | `class:89` |
| `BattleRole` / `CombatPolicy` | `game/strategy/data/fleet_hierarchy.py` | `BattleRole:18`, `CombatPolicy:32` |
| `ComponentActivationState` / `ActivationPhase` | `game/strategy/data/component_activation_state.py` | `ActivationPhase:24`, `ComponentActivationState:33` |
| `get_default_economy_config` (cached getter; module also has a mutating setter) | `game/strategy/config/economy_config.py` | `get:135`, `set:143` |
| `FieldStatus` enum (module also has live `RaceDescriptionLLMController`) | `game/strategy/services/race_description_llm_controller.py` | `FieldStatus:47`, controller `:90` |
| `StrategicKind` / `abilities_with_kind_tag` | `game/strategy/services/ability_metadata.py` | `StrategicKind:83`, `abilities_with_kind_tag:512` |
| `SUPERWEAPONS` static table | `game/strategy/services/superweapon_registry.py` | `SUPERWEAPONS:70` |
| `EmpireEconomySnapshot` (annotation-only import to DELETE) | `game/ui/panels/empire_treasury_panel.py` | import `:33`; uses `:65`,`:301`,`:306` |

## Related Documents
- [design.md](design.md) - Membership criteria, structure choice, full TAIL triage table
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File / conflict map

## Verification
- [x] Phase 1 checklist complete
- [x] Phase 2 (exec-audit follow-ups) checklist complete
- [x] `python Tools/test_sharded/test_sharded.py` green (24243 passed, 0 failed, 2026-05-22)
- [x] `_UISAFE_SYMBOLS` is machine-checkable data; parity + no-misfile tests pass
- [x] Doc↔guard parity: Pattern #5 token list == `_UISAFE_SYMBOLS`
- [ ] User verified
