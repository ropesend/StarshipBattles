# PROJ-472: Close the StrategySessionFacade READ-path gap (UI reads bypass the facade)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-472` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-472 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1A. Policy doc (Pattern #5) + two read-path static guards | Complete | [phase_1a_checklist.md](phase_1a_checklist.md) |
| 1B. Build-queue cluster migration onto facade queries | Complete | [phase_1b_checklist.md](phase_1b_checklist.md) |
| 1C. StrategyScreen.session read-consumer cleanup | Not Started | [phase_1c_checklist.md](phase_1c_checklist.md) |

## Current State
**Last Updated:** 2026-05-21
**Active Phase:** Phase 1C (StrategyScreen.session read-consumer cleanup)
**Last Action:** Phase 1B complete. Build-queue UI cluster migrated onto
`facade.empires.hex_build_queues` returning `BuildQueueSourceDTO`; DTO enriched
with `is_paused` / `owner_global_hex` / `owner_system_name` (slice-projected
scalars, no live `owner_entity`). Found+fixed a data-flow bug: the input
router's add/remove/pause command dispatch now re-projects DTOs from the facade
(`_resync_sources_from_facade`) so the display reflects post-command domain
state — DTO snapshots are immutable and were going stale. Test doubles given an
`empires.hex_build_queues` namespace; the multi-queue controller fixture and
several integration assertions tightened to DTO semantics (assert live backing
queue, not the frozen snapshot). Full sharded suite GREEN modulo the two known
pre-existing combat_lab failures (TOHIT-ATK-FLEET-003/004). 676 read-path guard
tests pass. No codex audit this phase (runs after 1C).
**Next Action:** Execute Phase 1C — migrate `StrategyScreen.session` /
`facade_state.session` read consumers (incl. `strategy_build_queue_manager.py`'s
deferred `:82-84` session read) per phase_1c_checklist.md.
**Blockers:** None.
**Note:** `validate_phase.py` only accepts integer phase numbers, so
`validate_phase.py PROJ-472 1b` errors (`int('1b')`). The phase used letter
sub-phases (1A/1B/1C); validation here is the green test suite + guards, not the
integer-phase script.

## Overview
The `StrategySessionFacade` enforces the strategy **write path** (commands route
through `facade.handle_command()` / `facade.commands.<verb>()`, guarded by
`tests/static_guards/test_facade_bypass_guard.py`), but there is **no equivalent
guard for the read path**. A live repo search on 2026-05-21 found **93 files
under `game/ui/`** importing `game.strategy` directly
(`rg -l "import game\.strategy|from game\.strategy" game/ui -g '*.py'` → 93).
Many reach past the facade for live-session reads (`BuildQueueSource`,
`collect_build_queues_at_hex`, `FleetCapabilityCalculator`,
`.session.<attr>` / `facade_state.session.<attr>`), making the facade a
write-path-only half-facade.

This project closes the gap the same way the write-path guard was rolled out:
**policy → static guard → first migration slice → incremental** — and CAPS the
work at a contained Phase 1. It does NOT attempt the full ~93-file migration.

## Goals
- **Phase 1A:** Document the read-path policy (option (b): a UI-safe read
  surface enforced by static guard + exact allowlist + convention) in Pattern #5
  of `docs/02_PATTERNS.md`, and add **two** read-path static guards mirroring the
  write-path guard's structure (runtime-import guard + session-read guard), each
  with positive controls and reasoned allowlists. Guards-first so 1B/1C are
  enforced as they land.
- **Phase 1B:** Migrate the **build-queue UI cluster** (~13 files) onto facade
  queries (`empires.build_queues` / `empires.hex_build_queues`) instead of
  domain `BuildQueueSource` / `collect_build_queues_at_hex`. Enrich
  `BuildQueueSourceDTO` once (`is_paused` + the resolved owner scalars
  `owner_global_hex` / `owner_system_name`; NO live `owner_entity`) so the
  feature is not left with domain `BuildQueueSource` and DTOs mixed. Fleet
  closeout state reads via `facade.fleets.get(fleet_id)` → `FleetInfo`. The
  three `FleetCapabilityCalculator` late-imports stay allowlisted (deferred to
  PROJ-475), not migrated.
- **Phase 1C:** Migrate the `StrategyScreen.session` / `facade_state.session`
  read-consumers (`strategy_detail_formatter`, `strategy_windows/list_windows`,
  `strategy_render/hex_outlines`, `strategy_build_queue_manager`, and
  `strategy_render/fleets` path-projection) onto facade accessors, then turn the
  session-read guard from advisory to enforcing on those files. A small set of
  live session readers (`strategy_event_router`, `strategy_screen_selection`,
  `empire_panel_ctrl`, `strategy_screen_order_editing` read) is explicitly
  deferred to PROJ-475 as allowlisted-with-reason — 1C does NOT claim to fully
  close the read path.

**Honest scope note (do not overclaim):** Phase 1 does NOT fully close the read
path. `StrategyScreen` keeps documented **transitional pass-through properties**
(`galaxy`, `empires`, `systems`, `active_empire`, `human_player_ids`;
`game/ui/screens/strategy_screen.py:160-189`) that remain allowlisted-with-reason,
and `FacadeSessionState` still publicly holds `session`
(`game/strategy/facade/slices/_facade_state.py:63-86`). Deprecating those, plus
the ~75-file tail, is follow-on work (PROJ-475). The plan is honest that the read
path is tightened and net-new bypasses are blocked, not that it is sealed.

## Scope
**In:**
- Read-path policy recorded in Pattern #5 (`docs/02_PATTERNS.md`).
- Two read-path static guards under `tests/static_guards/`.
- Build-queue cluster migration (~13 files) + one-time `BuildQueueSourceDTO`
  enrichment.
- `StrategyScreen.session` / `facade_state.session` read-consumer cleanup
  (4 named sites + the extra verified readers).

**Out (deferred to follow-on projects, gated on 472's guards landing):**
- **PROJ-474** — value/config UI-safe read-surface allowlist consolidation
  (`GameConfig`, `RaceConfig`, `EnvironmentalPreference`, `HabitabilityFactor`,
  `ContainableKind`, `ActivationPhase`, etc.). Mostly doc + allowlist work.
- **PROJ-475** — remaining live strategy-screen + render readers, AND
  deprecation of `StrategyScreen` pass-through properties +
  `FacadeSessionState.session` public exposure.
- **PROJ-476** — tooling/editor screens (`battle_setup` x4, `galaxy_test` x3,
  `race_setup` x4, parts of `builder` x3) which likely need broader exemptions
  than the live strategy UI.
- Write-path facade work (already guarded; not in this project).

## Tail distribution (the deferred ~75 files, verified 2026-05-21)
`rg -l ... game/ui` → 93 files: 57 `screens/(root)`, 15 `panels`, 4
`screens/battle_setup`, 4 `screens/race_setup`, 3 each in
`screens/strategy_render` / `screens/strategy_windows` / `screens/builder` /
`screens/galaxy_test`, 1 `widgets`. Phase 1B/1C touch the build-queue cluster +
session-consumer subset; the remainder is PROJ-474/475/476.

## Key Files
| Component | File Path | Verified line refs (2026-05-21) |
|-----------|-----------|----------------------------------|
| Facade composer + grouped accessors | `game/strategy/facade/strategy_session_facade.py` | `:132-198` namespace properties |
| Grouped read namespaces (build_queues / hex_build_queues) | `game/strategy/facade/grouped_namespaces.py` | `:256-264` |
| Empire slice build-queue collectors | `game/strategy/facade/slices/empire_slice.py` | `:68-97` |
| BuildQueueSourceDTO (gap: no is_paused / owner_global_hex / owner_system_name) | `game/strategy/facade/dto/build_queue_dto.py` | `:6-42` |
| FleetInfo (fleet closeout state: orders / is_building / construction_queue_size) | `game/strategy/facade/dto/fleet_dto.py` | `:67-73`, populated `:221-227`; `facade.fleets.get` `fleet_slice.py:60-65` |
| FacadeSessionState (public `session`) | `game/strategy/facade/slices/_facade_state.py` | `:63-86`; perf-boundary note `:48-60` |
| Existing write-path guard (mirror, read-only) | `tests/static_guards/test_facade_bypass_guard.py` | `:53-60`, `:69-103`, `:105-155`, `:208-238` |
| NEW runtime-import read guard | `tests/static_guards/test_facade_read_path_imports_guard.py` | new |
| NEW session-read guard | `tests/static_guards/test_facade_read_path_session_guard.py` | new |
| Read-path policy doc | `docs/02_PATTERNS.md` (Pattern #5) | `:148-166` |
| build_queue_screen (runtime BuildQueueSource import) | `game/ui/screens/build_queue_screen.py` | `:23`, calls `:214-217`, `:333-336` |
| build_queue_controller (TYPE_CHECKING-only imports; live BQS coupling) | `game/ui/panels/build_queue_controller.py` | `:18-20` (TYPE_CHECKING), class coupling `:66-79`,`:117-150`,`:421-522` |
| build_queue_input_router (owner_entity / is_paused) | `game/ui/screens/build_queue_input_router.py` | `:83-84`,`:128`,`:164`,`:174` |
| empire_build_queue_window (owner_entity → owner_global_hex; entity_id/context_type for cmd) | `game/ui/screens/empire_build_queue_window.py` | `get_hex_for_source:363-374`, `_add_item_to_source:413-438` |
| empire_build_queue_formatter (owner_entity → owner_system_name / owner_global_hex) | `game/ui/screens/empire_build_queue_formatter.py` | `get_system_name:79-92`, `get_sector_text:95-114` |
| fleet_data_source (FleetCapabilityCalculator late-import; DEFERRED-allowlist) | `game/ui/screens/fleet_data_source.py` | `:241-245` |
| fleet_report_filters (FleetCapabilityCalculator late-imports; DEFERRED-allowlist) | `game/ui/screens/fleet_report_filters.py` | `:163`, `:302` |
| strategy_detail_formatter (.session.registries / .turn_engine) | `game/ui/screens/strategy_detail_formatter.py` | `:112`,`:278`,`:395-396` |
| list_windows (.session.empires / .registries) | `game/ui/screens/strategy_windows/list_windows.py` | `:69-70` |
| hex_outlines (.session.active_empire; render-hot) | `game/ui/screens/strategy_render/hex_outlines.py` | `:30`,`:76-79` |
| strategy_build_queue_manager (facade_state.session bypass + fleet closeout) | `game/ui/screens/strategy_build_queue_manager.py` | bypass `:82-83`; fleet closeout `:226-235`,`:253-276` |
| strategy_render/fleets (path-projection session read; migrate in 1C) | `game/ui/screens/strategy_render/fleets.py` | `:85` → `facade.fleets.path_projection(fleet.id, 50)` |
| StrategyScreen.session property + pass-throughs | `game/ui/screens/strategy_screen.py` | `:160-189` pass-throughs, `:242-276` session property |
| Deferred-to-PROJ-475 session readers (allowlisted-with-reason) | `strategy_event_router.py`, `strategy_screen_selection.py`, `empire_panel_ctrl.py`, `strategy_screen_order_editing.py` | `event_router:223/368`, `selection:93`, `empire_panel_ctrl:62`, `order_editing:42` (read; `:66/:92` write seams) |

## Follow-on projects (deferred tail)
- [PROJ-474](../PROJ-474/plan.md) — value/config allowlist consolidation
- [PROJ-475](../PROJ-475/plan.md) — remaining live strategy-screen + render readers + pass-through deprecation
- [PROJ-476](../PROJ-476/plan.md) — tooling/editor screens (battle_setup / galaxy_test / race_setup)

All three are **gated on PROJ-472's two guards landing** (they extend the
allowlists / tighten the matchers the guards establish).

## Related Documents
- [design.md](design.md) - Architecture analysis, the two-guard design, the DTO gap, honesty note
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - Per-phase file/conflict map

## Verification
- [ ] Phase 1A/1B/1C checklists complete
- [ ] `python Tools/test_sharded/test_sharded.py` green
- [ ] Both read-path guards in the static-guard suite, with passing positive controls
- [ ] Pattern audit Pattern #5 facade-bypass count drops for the migrated slice
- [ ] User verified
