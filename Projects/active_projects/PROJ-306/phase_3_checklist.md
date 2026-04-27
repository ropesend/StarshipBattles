# Phase 3: Verification & Doc Update

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-306 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Run the full sharded suite, confirm zero regressions, update docs that referred to the transitional fallback as legitimate.

**Prerequisites:** Phases 1 and 2 complete.

---

## Tasks

### Task 3.1: Update `docs/01_ARCHITECTURE.md` [Simple]
**File:** `docs/01_ARCHITECTURE.md`
**Tests:** Manual verification

- [ ] `grep -n "get_default_registry_provider\|_default_ship_builder_from_context\|PROJ-274.*fallback" docs/01_ARCHITECTURE.md`
- [ ] Update or remove any reference to the transitional fallback as a legitimate pattern
- [ ] If the doc mentions the layer-separation rule, add a note that Simulation→Core registry access is now exclusively via injected `IRegistryProvider` / `ApplicationContext`, never via global getters

**Notes:**

---

### Task 3.2: Sweep architectural docs for stale claims [Simple]
**File:** `docs/01_ARCHITECTURE.md`, `docs/04_SERVICES.md`
**Tests:** Manual verification

- [ ] `grep -rn "_default_ship_builder_from_context\|PROJ-274.*transitional" docs/`
- [ ] Update or remove

**Notes:**

---

### Task 3.3: Full sharded suite [Simple]
**File:** None (test execution)
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the full sharded suite
- [ ] Confirm baseline maintained (15389+ passing)
- [ ] Investigate any new failures — if any are caused by PROJ-306, fix them; if pre-existing, document and skip

**Notes:**

---

### Task 3.4: Manual smoke [Simple]
**File:** Game runtime
**Tests:** Manual.

- [ ] Launch the game (`python game/main.py` or equivalent)
- [ ] Start a battle from the strategy screen — verify it runs to completion
- [ ] Launch Combat Lab — run a scenario — verify it runs
- [ ] Confirm no `get_default_registry_provider` ImportError or AttributeError appears in logs

**Notes:**

---

### Task 3.5: Update MEMORY.md [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md`
**Tests:** None.

- [ ] After user verifies smoke, add an entry under "Recently Archived":
  - `- **PROJ-306** — Battle Simulation DI Cleanup (PROJ-274 closure) (2026-MM-DD). All 3 phases complete. Eliminated 2 surviving global-lookup fallbacks: `_default_ship_builder_from_context()` in battle_runner.py + `get_default_registry_provider()` call in registry_loader.py:91. Migration pattern: [chosen in Phase 1.2]. Sharded suite: [N]/[N] passing.`

**Notes:** Do this AFTER user verifies, not during implementation.

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `grep -rn "get_default_registry_provider" game/simulation/` returns ZERO results
- [ ] Full sharded suite at 15389+ passing
- [ ] Manual smoke passes
- [ ] User verified
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete — pending archive"
