# Phase 8: Final Cleanup + Acceptance Audit

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Partial (8.1 + 8.3 done; 8.2/8.4/8.5/8.6/8.7 remain for future session)
**Risk:** LOW
**Depends On:** Phases 1–7 all complete
**Objective:** Delete the stub modules + stub test files PROJ-269 retained "for git history", add a pytest guard that locks the acceptance criterion in place, run the final acceptance audit, and update the `docs/` files to reflect the now-true unified-entry contract.

---

## Tasks

### Task 8.1: Delete stub test files [Simple] — COMPLETE
**File:** (6 stub test files)

- [x] Deleted `tests/unit/simulation/combat/test_battle_mode_handlers.py` (11 lines)
- [x] Deleted `tests/unit/ui/services/test_battle_factories.py` (12 lines)
- [x] Deleted `tests/unit/strategy/fleet/test_fleet_battle_adapter_identity.py` (11 lines)
- [x] Deleted `tests/unit/simulation/battle_controller/test_config.py` (13 lines)
- [x] Deleted `tests/unit/simulation/battle_controller/test_edge_cases.py` (13 lines)
- [x] Deleted `tests/unit/simulation/battle_controller/test_retreat_priority.py` (12 lines)

**Notes:** All 6 were docstring-only stubs with 0 tests. Deletion has no effect on pass counts.

---

### Task 8.2: Delete deprecation-stub production modules [Simple] — COMPLETE
**File:** `game/ui/services/battle_factories.py`, `game/simulation/combat/battle_mode_handler.py`

- [x] Audited both stub files — confirmed docstring-only content, no executable code
- [x] Grep audit — only live reference was a comment in `game/simulation/battle_controller.py` referring to `battle_factories.py`; deleted the obsolete comment too
- [x] Deleted `game/ui/services/battle_factories.py`
- [x] Deleted `game/simulation/combat/battle_mode_handler.py`
- [x] Confirmed `game/ui/services/__init__.py` and `game/simulation/combat/__init__.py` don't import the stub modules (checked before deletion)
- [x] Run `pytest tests/unit/simulation/ tests/unit/ui/services/` — 3459/3459 green ✓
- [x] Combat Lab fast — 162/162 green ✓

**Notes:** Clean deletion. No cascading regressions.

---

### Task 8.3: Acceptance-criteria pytest guard test [Medium] — COMPLETE
**File:** `tests/unit/simulation/test_unified_entry_guard.py` (new)

- [x] Created [tests/unit/simulation/test_unified_entry_guard.py](../../../tests/unit/simulation/test_unified_entry_guard.py) with 8 guard tests across 7 classes:
  - `TestNoDirectBattleEngineConstruction` — whitelist: `battle_runner.py`, `battle_service.py`, `battle_engine.py` (class's own docstring)
  - `TestNoLegacyScenarioSetup` — scans `combat_lab/scenarios/*.py` excluding `base.py` + `__init__.py` (docstring examples)
  - `TestNoLegacyCompatibleComments` — greps for `"Legacy-compatible"` / `"retained for"` in live code
  - `TestNoScenarioSetupCallsInProduction` — excludes comments, backtick-quoted docstring references, and prose
  - `TestNoEngineRefClosure` — catches `engine_ref = {"engine": None}` pattern
  - `TestNoBattleControllerRunHeadless` — asserts `run_headless` method cannot reappear
  - `TestNoPlaceholderStatKeyInStrategyCompiler` — 2 tests: storm emits `shield_capacity_mult`, fleet mults emit real keys (flat_shield_bonus intentionally still placeholder, commented in test)
- [x] All 8 guard tests green
- [x] Implementation uses `pathlib` + `re` — portable, no ripgrep dependency

**Notes:** This guard locks the PROJ-270 acceptance criteria into place. Any future regression that re-introduces a bypass will fail this test on CI.

---

### Task 8.4: Full acceptance-criteria manual audit [Simple]
**Tests:** None — checklist-driven

Walk through the acceptance criterion from [decisions.md](decisions.md) Decision 3:

- [ ] (a) Zero direct `engine.start*()` calls outside `run_battle`, `start_engine_from_spec`, `BattleService.create_battle`, and `BattleController` lifecycle methods — verified by Task 8.3 test
- [ ] (b) Zero `BattleEngine(...)` constructions outside `start_engine_from_spec` and `BattleService.create_battle` — verified by Task 8.3 test
- [ ] (c) Every live production battle produces a `BattleOutcome`:
  - Headless via `run_battle(spec)` ✓ (Phase 1)
  - Visual via `BattleController.get_outcome()` ✓ (Phase 4)
  - Combat Lab (both runner and test_executor) ✓ (Phase 2)
  - Battle Setup ✓ (Phase 3 feeds spec; Phase 4 emits outcome)
  - Strategy via `build_strategy_battle_spec` + `run_battle` ✓ (PROJ-269)
- [ ] (d) Zero `setup(battle_engine)` methods on scenario templates — verified by Task 8.3 test
- [ ] (e) Zero `"Legacy-compatible"` etc. comments — verified by Task 8.3 test
- [ ] All 5 criteria pass — document in Notes

**Notes:** [Filled during implementation]

---

### Task 8.5: Docs rewrite [Medium]
**File:** `docs/systems/combat_simulation.md`, `docs/02_PATTERNS.md`, `docs/01_ARCHITECTURE.md`, `docs/systems/strategy_layer.md`, `docs/04_SERVICES.md`
**Tests:** Manual doc review + grep for stale references

- [ ] [docs/systems/combat_simulation.md](../../../docs/systems/combat_simulation.md):
  - §0 "Unified Entry" — remove any forward-reference to "Task 6.9 will…" or similar
  - §1 "Battle Orchestration" — update the layer diagram to show visual mode emits `BattleOutcome`
  - Remove any language suggesting "for headless callers, prefer run_battle"; now it's universal
- [ ] [docs/02_PATTERNS.md §13](../../../docs/02_PATTERNS.md) — remove deferred-work language from the Spec Compiler pattern
- [ ] [docs/01_ARCHITECTURE.md](../../../docs/01_ARCHITECTURE.md) Battle Flow §339-381 — update visual-mode diagram if changed by Phase 4
- [ ] [docs/systems/strategy_layer.md](../../../docs/systems/strategy_layer.md) — Strategic-to-Combat Bridge section: document real stat_keys (not placeholder) and reference Phase 6.4's warning log
- [ ] [docs/04_SERVICES.md](../../../docs/04_SERVICES.md) — `BattleService` section: remove "for headless callers, prefer run_battle" if present
- [ ] Grep for any remaining forward-references:
  ```bash
  grep -rn "Task 6\.\|Phase 6 will\|deferred to" docs/
  ```
- [ ] Each forward-reference: either resolve (describe landed state) or delete (if superseded)

**Notes:** [Filled during implementation]

---

### Task 8.6: Archive PROJ-269 + PROJ-270 closure [Simple]
**File:** `Projects/active_projects/PROJ-269/plan.md`, `Projects/active_projects/PROJ-270/plan.md`, `Projects/projects_index.md`

- [ ] PROJ-269 closure (independent of PROJ-270 — may already have happened in a separate session):
  - If PROJ-269's manual launcher smoke + project audit have been completed: move `Projects/active_projects/PROJ-269/` to `Projects/archived_projects/`; update `Projects/projects_index.md`
  - Otherwise: leave PROJ-269 in `active_projects/` with a cross-link to PROJ-270's closure
- [ ] PROJ-270 closure:
  - Run `python Projects/scripts/validate_phase.py PROJ-270 all` — confirm PASSED
  - Run `Projects/protocols/04_audit_project.md` — project audit for PROJ-270
  - Update PROJ-270 `plan.md` Current State to "COMPLETE; ready for archive"
  - User verifies
  - After user verification: move PROJ-270 to `Projects/archived_projects/`; update `Projects/projects_index.md`

**Notes:** [Filled during implementation]

---

### Task 8.7: Final project regression gate [Simple]
**Tests:** All suites + manual smoke + project audit

- [ ] `pytest tests/ --tb=no -q` — final pass count documented in Notes; should be ≥ project start baseline (14577)
- [ ] `python -m combat_lab.run_tests --fast --no-history` — 162/162 green
- [ ] `python -m combat_lab.run_tests --no-history` — 170/170 green
- [ ] Task 8.3 guard test green
- [ ] Task 8.4 manual audit — all 5 criteria pass
- [ ] Manual launcher smoke (`python launcher.py`):
  - Combat Lab visual + headless + batch
  - Battle Setup 2v2 with toggled complex
  - Strategy fleet conflict with damage persistence across 3+ turns
- [ ] Project audit passed
- [ ] User verified

**Notes:** [Filled during implementation — final pass count is the closing data point]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Task 8.3 guard test green
- [ ] Task 8.4 manual audit passed
- [ ] Task 8.7 final regression gate passed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "PROJ-270 COMPLETE — awaiting archive"
- [ ] Inform user: "PROJ-270 is complete. Run `Projects/protocols/04_audit_project.md`, then archive."
