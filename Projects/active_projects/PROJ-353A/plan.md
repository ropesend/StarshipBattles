# PROJ-353A: Closeout follow-up - Tooling and test-quality polish (T6.8 facade _session lint + Tier-7 polish bundle)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-353A` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. T6.8 — facade `_session` lint decision | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Tier-7 polish bundle (test-quality MAJORs) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Complete — Awaiting Verification
**Last Action:** Phase 2 (Tier-7) all 13 sub-tasks landed; full unit suite green (15,783 pass / 0 fail / 2 skip), lint clean.
**Next Action:** User verification.
**Blockers:** None.
**Context for Next Agent:** All 14 sub-tasks (T6.8 + Tier-7 2.1..2.13) committed per-concern with PROJ-353A Tier-7 tags. Concurrent-commit hygiene maintained (PROJ-351A/352 files left untouched). See decisions.md for the T6.8 convention-only rationale.

## Overview

Two unrelated closeout-follow-up areas grouped because both are low-risk polish: T6.8 is a tooling decision; Tier-7 is a long list of small test-quality improvements. They share "do not block merge of the closeout arc" status.

## Goals

- T6.8: Make an explicit decision on facade `_session` lint enforcement. Codex's recommendation (accepted in arc01_004 consensus): convention-only for now; add a lint only if an external-access regression appears. Phase 1 documents the decision and adds a test-or-comment trap that catches a regression cheaply.
- Tier-7: Land the polish items from synthesis lines 105-122 that improve test quality without changing production behavior. Tackle in priority order; commit per concern.

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

## Key Files (selection)

| Concern | File Path |
|---|---|
| T6.8 facade `_session` | `game/strategy/facade/strategy_session_facade.py:80-90, 156-182` |
| LLM race | `game/services/llm/background.py:210, 291-297` |
| production_spawner pins | `tests/unit/strategy/engine/test_production_spawner.py` |
| Other Tier-7 — see synthesis line refs | various |

## Related Documents

- [design.md](design.md) — context analysis
- [decisions.md](decisions.md) — decisions log
- [manifest.md](manifest.md) — file manifest
- Source synthesis: `AgentCoordination/Scratchpad/plans/proj321_341_unified_remediation_plan.md` (gitignored, lines 105-122 = Tier 7)
- Codex review consensus: `AgentCoordination/Scratchpad/Discussion/20260505T020232Z_proj343-349-codex-review/plans/proj343_349_remaining_plan_r003.md`

## Verification

- [ ] All phase checklists complete
- [ ] `pytest tests/unit/ -q -p no:cacheprovider` — full suite green
- [ ] `python Tools/lint_test_files.py` — 0 violations
- [ ] User verified
