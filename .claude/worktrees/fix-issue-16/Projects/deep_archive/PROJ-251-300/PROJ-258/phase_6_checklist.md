# Phase 6: Documentation + Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-258 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all documentation to reflect the new ApplicationContext DI pattern. Run final verification to confirm zero regressions and complete eradication of singleton access patterns.

---

## Tasks

### Task 6.1: Update docs/02_PATTERNS.md [Medium]
**File:** `docs/02_PATTERNS.md`

- [ ] Rewrite Section 1 "Singleton (SingletonMeta)":
  - Mark SingletonMeta as **deprecated/unused** (kept but no production users)
  - List that all 11 former singletons now use ApplicationContext DI
  - Remove the "When to Use" guidance pointing to SingletonMeta
- [ ] Update Section 3 "Dependency Injection (Registry)":
  - Add ApplicationContext as the primary DI container
  - Document `create_production()` and `create_test()` factory methods
  - Document that IRegistryProvider still exists for narrower injection
  - Show example of receiving ApplicationContext via constructor
- [ ] Add new pattern section "ApplicationContext (DI Container)":
  - Where: `game/context.py`
  - How It Works: container with factory methods, passed explicitly
  - When to Use: any code needing access to shared services
  - Code examples for production and test usage

**Notes:**

---

### Task 6.2: Update docs/01_ARCHITECTURE.md [Simple]
**File:** `docs/01_ARCHITECTURE.md`

- [ ] Update "Cross-Layer Communication" section:
  - Add ApplicationContext as a new subsection alongside existing DI section
  - Document that `game/context.py` sits outside the layer hierarchy
  - Document the factory method pattern
- [ ] Update "Package Directory Map":
  - Add `game/context.py` to the game/ root level
- [ ] Update "Entry Point" section:
  - Note that `Game.__init__` creates ApplicationContext via `create_production()`

**Notes:**

---

### Task 6.3: Update docs/03_CONVENTIONS.md [Simple]
**File:** `docs/03_CONVENTIONS.md`

- [ ] Update Section 6.3 "Preferred Patterns":
  - "Dependency injection via ApplicationContext" replaces "Dependency injection" in the "Prefer" column
  - Add explicit entry: "ApplicationContext DI" over "Singleton access via .instance()"
- [ ] Update any references to SingletonMeta usage patterns

**Notes:**

---

### Task 6.4: Update guides/testing_infrastructure.md [Medium]
**File:** `docs/guides/testing_infrastructure.md`

- [ ] Document the `test_context` fixture
- [ ] Document `ApplicationContext.create_test(**overrides)` for test setup
- [ ] Update conftest.py documentation to reflect simplified reset logic
- [ ] Remove references to `.reset()` singleton cleanup pattern

**Notes:**

---

### Task 6.5: Final Verification Sweep [Medium]
**Tests:** Full suite + grep verification

- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ tests pass, 0 failures
- [ ] Grep verification: zero `metaclass=SingletonMeta` in production code (only in `game/core/singleton.py` definition)
  - `grep -r "metaclass=SingletonMeta" game/` should return 0 results (excluding singleton.py itself)
- [ ] Grep verification: zero `.instance()` calls on former singletons in production code
  - `grep -r "\.instance()" game/` should return 0 results (or only in singleton.py docstring)
- [ ] Grep verification: zero `.reset()` calls on former singletons in test code
  - `grep -r "RegistryManager\.reset\|Profiler\.reset\|StrategyManager\.reset\|AssetManager\.reset\|SpriteManager\.reset\|ShipThemeManager\.reset\|ScreenshotManager\.reset\|StrategyMetadataService\.reset\|ComponentCacheManager\.reset\|GameSettings\.reset" tests/` should return 0
- [ ] Verify `game/core/singleton.py` still exists (kept for potential future use)
- [ ] Verify `ApplicationContext` is not itself a singleton (no metaclass, no class-level instance)
- [ ] Update plan.md Verification section -- check all items

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `docs/01_ARCHITECTURE.md` updated
- [ ] `docs/02_PATTERNS.md` updated (Singleton section rewritten, ApplicationContext added)
- [ ] `docs/03_CONVENTIONS.md` updated
- [ ] `docs/guides/testing_infrastructure.md` updated
- [ ] All grep verifications pass (zero singleton usage in production)
- [ ] Full test suite passes (14783+ tests, 0 failures)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
