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
| 1. Establish 500-LOC convention in CLAUDE.md | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Decomposition design (10 files) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Execute decompositions (one file per sub-phase) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Final verification + tooling | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-26
**Active Phase:** Planning (approved, ready for implementation)
**Last Action:** Project created. Verified top-10 file list against current codebase
**Next Action:** Begin Phase 1 — establish the 500-LOC convention in CLAUDE.md so the boundary is documented before any file is split
**Blockers:** None — but recommend completing PROJ-298 / PROJ-306 first (some target files like `command_handlers.py` and `strategy_session_facade.py` are touched by those projects)
**Context for Next Agent:** This project intentionally targets the **top 10 largest files**, not all 62 files >500 LOC. The user's directive: "lets take the top 10 files and break them down in a way that makes them difficult to grow." Each split is a small architectural redesign — extract cohesive sub-modules, not arbitrary chunks. Per file, the target is: no resulting module >500 LOC, related logic stays together, public API of the original module preserved.

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
