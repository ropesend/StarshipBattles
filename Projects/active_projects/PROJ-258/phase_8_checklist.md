# Phase 8: Remove AI Singleton Shims

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-258 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove `.instance()` and `.reset()` compatibility shims from StrategyManager (AI layer). Replace every call site with direct construction or ApplicationContext access.

---

## Tasks

### Task 8.1: Remove StrategyManager shims [Medium]
**Files:** `game/ai/strategy_manager.py` + ~46 test call sites
**Shim calls:** 2 production (controller.py, workshop_data_loader.py), 46 test

- [ ] Update `game/ai/controller.py` — AIController receives StrategyManager via constructor or context instead of `.instance()`
- [ ] Update `game/ui/screens/workshop_data_loader.py` — receive StrategyManager via context
- [ ] Grep all `StrategyManager.instance()` and `StrategyManager.reset()` in tests/ — catalog every file
- [ ] Update `tests/unit/ai/test_strategy_manager_singleton.py` — rewrite for non-singleton pattern (direct construction)
- [ ] Update `tests/unit/ai/test_strategy_system.py` — replace `.reset()` / `.instance()` with fresh instances
- [ ] Update `tests/integration/ai_strategy/conftest.py` — replace `.instance()` / `.clear()` with direct construction
- [ ] Update `conftest.py` — replace `StrategyManager.instance()` with direct construction or module-level reference
- [ ] Sweep remaining: `grep -rn "StrategyManager\.\(instance\|reset\)()" tests/ conftest.py` — must be zero
- [ ] Remove `instance()` and `reset()` classmethods from StrategyManager
- [ ] Decide: keep or remove `_default_strategy_manager` (keep if conftest or module-level functions need it)
- [ ] Run: `pytest tests/ -x -q -n 4` — all pass
- [ ] Commit: "refactor: remove StrategyManager .instance()/.reset() shims"

**Notes:** StrategyManager is populated during conftest.py's reset_game_state fixture (line ~73). The fixture currently calls `StrategyManager.instance()` to get the manager and set `.strategies`. After removing shims, this needs to use the module-level reference or a fresh instance.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `grep -rn "StrategyManager\.\(instance\|reset\)()" game/ tests/ conftest.py` — zero results
- [ ] Full test suite passes (14783+ tests, 0 failures)
- [ ] 1 commit
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 9
