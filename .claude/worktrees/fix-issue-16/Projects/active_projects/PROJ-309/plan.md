# PROJ-309: Top-10 File Decomposition and 500-LOC Convention

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-309` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-309 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Establish 500-LOC convention in CLAUDE.md | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Decomposition design (10 files) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Execute decompositions (one file per sub-phase) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Final verification + tooling | In Progress (4.1, 4.2, 4.4 done; 4.3 manual smoke + 4.5 MEMORY pending user) | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-27
**Active Phase:** Phase 4 — automated work complete; awaiting user manual smoke (4.3) and final MEMORY update (4.5)
**Last Action:** Phase 3 ALL 10 SUB-PHASES COMPLETE (3.4, 3.5, 3.8, 3.7, 3.3, 3.6, 3.2, 3.10, 3.1, 3.9 — full sequence done in this session). Phase 4.1 (top-25 sweep), 4.2 (sharded suite 15582/15582), and 4.4 (`Tools/check_file_size.py`) complete. **All 10 PROJ-309 target files now <500 LOC** (max: `screen_router.py` 496, `strategy_session_facade.py` 476, `workshop_viewmodel.py` 462). 174 new contract tests landed across the project (locking the public-API surface of every decomposed module). Full sharded suite: **15582/15582 passed**, baseline grew from 15405 → 15582.
**Next Action:** USER ACTION REQUIRED — Phase 4.3 manual smoke per `phase_4_checklist.md`: launch the game, navigate every screen touched by a decomposed file (Race Setup, Strategy screen all render layers, command issuing, Workshop, Combat Lab, sub-windows). Confirm no console errors / silent UI breakage. After that, archive per `04_audit_project.md` and apply Phase 4.5 MEMORY.md update.
**Blockers:** Manual-smoke verification gate. No code work blocking.
**Context for Next Agent:** Project is feature-complete. All 10 decompositions landed; tests green; convention documented + tooling provided. The 52 residual >500-LOC files in `game/` are OUT OF SCOPE for PROJ-309 (only the top-10 by directive). Future PROJ-3xx can chip away at the residual under the now-established convention.

Decomposition shapes used (catalogue for future similar projects):
- **Package-replaces-file** (3.4 protocols, 3.3 test_lab/renderer, 3.10 strategy_window_manager, 3.2 strategy_renderer): original file deleted; package directory takes the import path; `__init__.py` re-exports.
- **Subpackage + Option-A shim** (3.5 command_handlers, 3.6 test_run_details, 3.1 race_setup_screen): subpackage gets a NEW name; original file becomes a thin re-export shim.
- **Composer + slice subpackage** (3.7 strategy_session_facade): composer kept at original path; per-domain slices in subpackage; shared state via dataclass.
- **Flat helper extraction** (3.8 workshop_viewmodel): public class kept at original path; private helpers as flat sibling modules (per §1.3 workshop convention).
- **Multi-file extraction at top level** (3.9 app.py): bootstrap / run-loop / screen-router as flat siblings; `app.py` keeps `Game`/`main`.

Latent items flagged but not fixed (preserve-and-flag per design instructions):
1. `screen_diameter` NameError in `strategy_render/dyson_spheres.py` (was at original L846/854).
2. `_temp_screen_pos`/`_temp_draw_r` smear onto planet domain in `strategy_render/systems.py`.
3. Polar-angle table duplicated with `strategy_click_dispatcher.py:448`.
4. `BootstrapResult` frozen dataclass mutated via `object.__setattr__` for resize.
5. `start_builder(return_to=...)` and `on_builder_return(custom_ship=...)` unused params preserved.

Latent items FIXED during PROJ-309 (clean-sheet improvements that fell within the move):
- `planet_abilities_window` now `None`-initialized AND included in `StrategyEventRouter.has_modal_open()` 15-slot scan (was missing).
- `ResourceCatalog.from_json()` no longer called twice during bootstrap.
- Triple-duplicated dialog teardown in race-setup save flow consolidated into `renderer.close_save_update_dialog()`.
- `apply_append_selection`'s mid-loop mutation bug under toggle (workshop_viewmodel) fixed by tracking `current_objs` alongside `result`.

Convention enforcement: `Tools/check_file_size.py` walks `game/` and fails if any file >500. Currently 52 violations (all OUT OF SCOPE). Convention also in CLAUDE.md "Code Quality" + `docs/03_CONVENTIONS.md` §2.3.

## Overview
Split the 10 largest source files in `game/` into smaller, single-responsibility modules. Each split is a one-or-two-week effort with its own design phase (since each file has different reasons for being big). Establish the 500-LOC ceiling as a CLAUDE.md convention so the codebase resists growing back into mega-files.

## Goals
- Add a "500-LOC ceiling" rule to CLAUDE.md ("Code Quality" section) requiring authors to split when a file crosses 500 LOC
- Decompose each of the top 10 files such that no resulting module exceeds 500 LOC
- Keep the public API of each original module surface-compatible (callers import from the same name; the module becomes a re-export OR the file is renamed and callers updated)
- Maintain the test baseline (15389+ passing) throughout

## Scope

**In: top 10 files (verified 2026-04-26)**

| Rank | File | Lines | Likely decomposition direction |
|------|------|------:|--------------------------------|
| 1 | `game/ui/screens/race_setup_screen.py` | **1588** | Tabs / sections (genome, traits, preview, controls) → separate panels |
| 2 | `game/ui/screens/strategy_renderer.py` | **1205** | Layer-by-layer renderers (background, planets, fleets, overlay, HUD) |
| 3 | `game/ui/screens/test_lab/renderer.py` | **1193** | Per-rendering-concern modules; possibly mirror PROJ-309 strategy_renderer split |
| 4 | `game/core/protocols.py` | **1087** | Group protocols by domain (combat, AI, strategy, UI) → submodules under `game/core/protocols/` |
| 5 | `game/strategy/engine/command_handlers.py` | **1072** | One handler-class-per-file under `game/strategy/engine/handlers/` |
| 6 | `game/ui/screens/test_lab/test_run_details.py` | **957** | Sub-panels and viewmodels |
| 7 | `game/strategy/facade/strategy_session_facade.py` | **922** | Per-domain facade slices (fleet, planet, research, economy) |
| 8 | `game/ui/screens/workshop_viewmodel.py` | **873** | View-state, command handlers, validation as separate modules |
| 9 | `game/app.py` | **849** | Bootstrap, run-loop, and screen-management as separate concerns |
| 10 | `game/ui/screens/strategy_window_manager.py` | **817** | Window-lifecycle and event-routing |

**In:** Convention update in CLAUDE.md.

**Out:**
- The other 52 files >500 LOC — not targeted by name. The CLAUDE.md convention will eventually cause them to be split as they're touched, but blanket rewrites are out of scope here.
- Test files (the convention applies to production source; test files have different size dynamics — long test files are often acceptable)
- File renames where the public API changes — keep the import surface stable

## Key Files

### Top-10 list (see Quick Status table above for line counts)
- See per-phase checklist for which sub-phase owns each file

### Convention enforcement
| File | Edit |
|------|------|
| `CLAUDE.md` | Add 500-LOC rule under "Code Quality" or "Long-Term Quality" |
| `docs/03_CONVENTIONS.md` | Add §"File Size" section |

## Related Documents
- [design.md](design.md) - Per-file decomposition rationale (high-level; details in Phase 2 per-file design docs)
- [decisions.md](decisions.md) - Decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All 10 target files decomposed; no resulting module >500 LOC
- [ ] CLAUDE.md mentions the 500-LOC ceiling rule
- [ ] `docs/03_CONVENTIONS.md` has a §File Size section
- [ ] Full sharded suite passes (15389+ baseline)
- [ ] Manual smoke: launch the game, navigate every screen touched by a decomposed file
- [ ] User verified
