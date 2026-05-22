# PROJ-474: Facade read-path: value/config UI-safe read-surface allowlist consolidation (follow-on from PROJ-472)

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
| 1. TBD | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-21
**Active Phase:** Stub (deferred tail of PROJ-472)
**Last Action:** Stub created + scoped during PROJ-472 planning.
**Next Action:** Do NOT start until PROJ-472's two read-path static guards have landed (this project extends their allowlists). Then plan phases.
**Blockers:** **GATED on PROJ-472** — the runtime-import read guard (`tests/static_guards/test_facade_read_path_imports_guard.py`) and its UI-safe allowlist must exist first.

## Overview
Follow-on from **PROJ-472** (close the StrategySessionFacade read-path gap).
PROJ-472 establishes the option-(b) policy (documented UI-safe read surface +
static guard + allowlist) and migrates the build-queue cluster + session
consumers. THIS project consolidates the **value/config UI-safe read surface**:
the immutable config/value/enum/protocol types that `game/ui/` legitimately reads
pre-session, codifying them in the guard allowlist + Pattern #5 so they are
explicitly blessed rather than silently tolerated. Mostly documentation +
allowlist cleanup, not facade expansion or major code motion.

## Goals
- Codify the allowed non-session read surface in the PROJ-472 import-guard
  allowlist with reason comments: `RaceConfig`, `GameConfig`,
  `EnvironmentalPreference`, `HabitabilityFactor`, `ContainableKind`,
  `ActivationPhase`, and the small set of explicitly-blessed pure query helpers.
- Verify each allowlisted type is genuinely immutable/pre-session/value-shaped at
  every `game/ui/` use site (not a live-session traversal hiding behind a value name).
- Tighten the guard so adding a NEW non-allowlisted strategy import still fails;
  the allowlist stays short and reasoned.

## Scope
**In:** The value/config/enum/protocol read-surface allowlist + the Pattern #5
documentation of it. The `game/ui/` sites that import these types (across panels /
race_setup / new_game_setup / transfer / planet-abilities, etc.).
**Out:** Live-session reader migration (PROJ-475); tooling/editor screen
migration (PROJ-476); the build-queue cluster + session consumers (PROJ-472).

## Key Files
| Component | File Path |
|-----------|-----------|
| Read-path policy + UI-safe type list | `docs/02_PATTERNS.md` (Pattern #5) |
| Runtime-import read guard + allowlist | `tests/static_guards/test_facade_read_path_imports_guard.py` (from PROJ-472) |
| Representative value/config use sites | `game/ui/screens/new_game_setup_controller.py:39-44`, `game/ui/panels/race_environment_panel.py:25-35`, `game/ui/widgets/preference_row.py:37-40`, `game/ui/screens/transfer_view_model.py:243-255`, `game/ui/screens/planet_abilities_controller.py:30-34` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
