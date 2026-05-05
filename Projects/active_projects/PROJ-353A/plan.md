# PROJ-353A: Closeout follow-up - Tooling and test-quality polish (T6.8 facade _session lint + Tier-7 polish bundle)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-353A` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-353 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. TBD | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Complete — Awaiting Verification
**Last Action:** Phase 2 (Tier-7) all 13 sub-tasks landed; full unit suite green (15,783 pass / 0 fail / 2 skip), lint clean.
**Next Action:** User verification.
**Blockers:** None.
**Context for Next Agent:** All 14 sub-tasks (T6.8 + Tier-7 2.1..2.13) committed per-concern with PROJ-353A Tier-7 tags. Concurrent-commit hygiene maintained (PROJ-351A/352 files left untouched). See decisions.md for the T6.8 convention-only rationale.

## Overview
[2-3 sentence description of what this project accomplishes]

## Goals
- [Goal 1]
- [Goal 2]

## Scope

**In (T6.8):**
- Decision documentation in [decisions.md](decisions.md).
- Optionally, a regression-trap test that fails fast if external `_session` access reappears (unit-level public-API check).

**In (Tier-7) — selected from synthesis lines 105-122:**
- LLMBackgroundCall `_done_event` race fix (`game/services/llm/background.py:210, 291-297`)
- production_spawner dispatch tests use `assert_called_once_with` not `assert_called_once`
- `_collect_team_modifiers` brittle import patch refactor
- `_apply_damage_to_ship` dead-branch pin annotations (link to ticket)
- `ActionExecutionEngine` test pin annotation (after PROJ-351A T6.3 lands)
- PROJ-332 lazy-property + factory tests
- PROJ-335 from_dict gaps (4 tests)
- PROJ-336 vacuous module-constant tests
- `test_get_font_enforces_minimum_size_8` quantize-to-2 step
- PROJ-326 misc (allowlist header, AST linter, Python version comment)
- PROJ-321 deleted `test_start_battle_ship_builder_*` recovery
- `TestRegisterOnConstruction` retrofit (no longer tests construction registration)
- `bypass_init` MRO leak risk under pytest-xdist parallel

**Out:**
- §2.4 LOC-ceiling refactors (race_setup/screen.py 484, new_game_setup_screen.py 733). Open as a separate PROJ if scope grows.
- Any production refactor not explicitly listed.

## Key Files
| Component | File Path |
|-----------|-----------|
| [Name] | `path/to/file.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
