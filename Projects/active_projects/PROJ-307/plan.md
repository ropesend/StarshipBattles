# PROJ-307: Documentation Freshness Timestamps

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-307` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-307 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Backfill timestamps to 21 docs | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Establish convention in CLAUDE.md | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-04-27
**Active Phase:** Complete — pending archive
**Last Action:** Phase 2 complete. CLAUDE.md Rule 2 gained a DO and a DO NOT bullet about the `Last verified:` date. `docs/03_CONVENTIONS.md` gained §8 Documentation Freshness; its own timestamp bumped to 2026-04-27.
**Next Action:** User verification, then archive PROJ-307.
**Blockers:** None
**Context for Next Agent:** Verifications all pass — `grep -L "Last verified" docs/...` returns zero files; `grep -n "Last verified" CLAUDE.md` returns 2 hits; `grep -n "Documentation Freshness" docs/03_CONVENTIONS.md` returns 1 hit.

## Overview
Add a "Last verified" timestamp line near the top of every `docs/**/*.md` file. Establish the convention in CLAUDE.md so future doc edits maintain freshness markers. Helps future agents and contributors quickly judge whether a doc is likely stale or current.

## Goals
- Add `> **Last verified:** YYYY-MM-DD` to all 21 doc files that lack it
- Use each file's most recent meaningful commit date (via `git log -1 --format=%cs`) as a starting baseline
- Add a §Documentation Conventions entry in CLAUDE.md (or `docs/03_CONVENTIONS.md`) requiring future doc edits to update the timestamp
- Define what "verified" means (the maintainer has read the file and confirmed it matches current code)

## Scope
**In:**
- All 22 .md files under `docs/`:
  - `docs/01_ARCHITECTURE.md` through `docs/06_UI_STYLE_GUIDE.md` (6 files)
  - `docs/README.md` (already done — verify format consistency)
  - `docs/guides/*.md` (7 files: adding_abilities, adding_modifiers, component_system, modifier_system, qs_complex_design, simulation_testing, testing_infrastructure)
  - `docs/systems/*.md` (8 files: ability_reference, ai_system, combat_simulation, orders_system, production_system, research_system, resource_system, strategy_layer)
- The `> **Last verified:** YYYY-MM-DD — <summary>` block placed just under the H1 of each file
- A convention entry in `CLAUDE.md` (Rule 2 documentation section) specifying that any doc edit must update the timestamp

**Out:**
- `docs/_ignore/` (per CLAUDE.md, this folder is the user's scratchpad — don't read or modify it)
- `CLAUDE.md` itself getting a "Last verified" timestamp (it's a special instruction file, not a doc — different lifecycle)
- `Projects/**/*.md`, `Reviews/**/*.md`, `Tracking/**/*.md` (not part of `docs/`)

## Key Files

### Files to add timestamps to (21 files)
| File | Most recent commit date (per `git log -1 --format=%cs`) |
|------|---------------------------------------------------------|
| `docs/01_ARCHITECTURE.md` | TBD (Phase 1 fills) |
| `docs/02_PATTERNS.md` | 2026-04-26 (per recent commits) |
| `docs/03_CONVENTIONS.md` | 2026-04-18 |
| `docs/04_SERVICES.md` | 2026-04-19 |
| `docs/05_ERROR_HANDLING.md` | 2026-04-06 |
| `docs/06_UI_STYLE_GUIDE.md` | 2026-04-11 |
| `docs/guides/adding_abilities.md` | TBD |
| `docs/guides/adding_modifiers.md` | TBD |
| `docs/guides/component_system.md` | TBD |
| `docs/guides/modifier_system.md` | TBD |
| `docs/guides/qs_complex_design.md` | TBD |
| `docs/guides/simulation_testing.md` | TBD |
| `docs/guides/testing_infrastructure.md` | TBD |
| `docs/systems/ability_reference.md` | TBD |
| `docs/systems/ai_system.md` | TBD |
| `docs/systems/combat_simulation.md` | TBD |
| `docs/systems/orders_system.md` | TBD |
| `docs/systems/production_system.md` | TBD |
| `docs/systems/research_system.md` | TBD |
| `docs/systems/resource_system.md` | TBD (created 2026-04-something) |
| `docs/systems/strategy_layer.md` | TBD |

### Files to update with convention
| File | Edit |
|------|------|
| `CLAUDE.md` | Add a sub-bullet under "Rule 2: Documentation" specifying the timestamp requirement |
| `docs/03_CONVENTIONS.md` | Add a "Documentation Freshness" section describing the format and update rule |

## Related Documents
- [design.md](design.md) - Format choice and rationale
- [decisions.md](decisions.md) - Decisions log

## Verification
- [ ] All phase checklists complete
- [ ] `grep -L "Last verified" docs/*.md docs/guides/*.md docs/systems/*.md` returns ZERO files (every doc has the marker)
- [ ] CLAUDE.md mentions the timestamp requirement
- [ ] `docs/03_CONVENTIONS.md` has a Documentation Freshness section
- [ ] User verified
