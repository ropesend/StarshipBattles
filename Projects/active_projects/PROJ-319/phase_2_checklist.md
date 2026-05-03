# Phase 2: Dead Functions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-319 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete the 2 verified dead helper functions identified by audit `Reviews/results/2026-05-02_184210_audit_shrink/`. Both have superseding implementations in their own files; the verifier confirmed zero call sites in production, tests, docs, or data.

---

## Tasks

### Task 2.1: Battle runner — drop dead weapon-summary helper [Simple]
**File:** `game/simulation/battle_runner.py`
**Tests:** `pytest tests/simulation/test_battle_runner.py` (or the closest available `tests/simulation/` path)

- [x] Remove method `_extract_weapon_summaries` (lines 647-671, ~25 LOC) — DEEP-02-001 (also pruned now-unused `WeaponSummary` import from `from game.simulation.battle_outcome import (...)` at line 35-43)
  - Per verifier: superseded by `WeaponSummaryAggregator` instantiated at battle_runner.py:402.
  - Before deleting: re-grep `_extract_weapon_summaries` across the repo to confirm zero callers (the verifier saw 0; this is the per-task safety net flagged in design.md). Confirmed 0 callers in this run.
- [x] Verify: `pytest tests/simulation/` passes; LOC delta ~ -25 (ran tests/unit/simulation/test_battle_runner*.py: 136 passed; full sharded suite: 16370/16374 passed, 1 unrelated flake in services/llm/test_background.py — see decisions.md)

---

### Task 2.2: Strategy detail formatter — drop dead shield-facility helper [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/ --testmon` (no targeted UI test path; let testmon select impacted tests)

- [x] Remove function `_planet_has_shield_facility` (lines 316-347, ~32 LOC) — DEEP-01-002
  - Per verifier: superseded by `_planet_has_ability_facility` at line 419 of the same file (uses registry lookup instead of hardcoded special case).
  - Before deleting: re-grep `_planet_has_shield_facility` across the repo to confirm zero callers. Confirmed 0 callers.
- [x] Verify: `pytest tests/ --testmon` passes; LOC delta ~ -32 (ran tests/unit/ui/screens/test_strategy_detail_fmt.py and test_strategy_detail_formatter.py: passed; full sharded: see Task 2.1 verify note)

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] `python Tools/test_sharded/test_sharded.py` passes (16374 tests, 16370 passed, 1 unrelated flake — `tests/unit/services/llm/test_background.py::test_elapsed_seconds_is_monotonic_then_frozen` is a pre-existing Windows timing flake, see decisions.md)
- [x] Total LOC delta is ~ -57
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4 (Phase 3 is skipped)

_Source audit: `Reviews/results/2026-05-02_184210_audit_shrink/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
