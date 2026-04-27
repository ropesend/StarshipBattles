# Phase 6: ApplicationContext Wiring [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-296 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire LLM provider into the DI container. Module-level `_default_llm_provider` slot + `get_default_llm_provider()` / `set_default_llm_provider()` accessors. 5 specific edits to `game/context.py`. Update 1 affected test file.

---

## Tasks

### Task 6.1: Module-level accessors [Simple]
**File:** `game/services/llm/__init__.py` (extend)
**Tests:** `pytest tests/unit/services/llm/test_defaults.py` (NEW)

- [ ] Write failing tests:
  - `get_default_llm_provider()` returns `None` when no provider has been set
  - `set_default_llm_provider(p)` then `get_default_llm_provider()` returns `p`
  - `set_default_llm_provider(None)` clears the slot
- [ ] Add to `game/services/llm/__init__.py`:
  ```python
  from typing import Optional
  from game.services.llm.provider import LLMProvider

  _default_llm_provider: Optional[LLMProvider] = None

  def get_default_llm_provider() -> Optional[LLMProvider]:
      """Get the application-wide default LLM provider, or None if unconfigured.
      Consumers should check `if provider is not None:` before using."""
      return _default_llm_provider

  def set_default_llm_provider(provider: Optional[LLMProvider]) -> None:
      """Set the application-wide default LLM provider. Called once by
      ApplicationContext.create_production() at startup, or by tests."""
      global _default_llm_provider
      _default_llm_provider = provider
  ```
- [ ] Add a fixture `reset_llm_default_provider` in `tests/unit/services/llm/conftest.py` that clears the slot before/after each test that touches it.
- [ ] Run tests, confirm pass

**Notes:**

### Task 6.2: Wire into `ApplicationContext` [Medium]
**File:** `game/context.py`
**Tests:** `pytest tests/unit/core/test_application_context.py`

- [ ] Write failing tests in `test_application_context.py`:
  - `ApplicationContext.create_production()` sets `ctx.llm_provider` (may be `None` if no key in env)
  - After `create_production()`, `get_default_llm_provider()` returns the same instance as `ctx.llm_provider`
  - `ApplicationContext.create_test(llm_provider=fake)` uses the override
- [ ] Edit `game/context.py` (5 specific edits per Phase A findings):
  1. **`__init__` signature** (around line 31-41): add `llm_provider: Any,` parameter
  2. **`__init__` body** (around line 49): add `self.llm_provider = llm_provider`
  3. **`create_production()` late imports** (around line 58): add `from game.services.llm import LLMProviderFactory`
  4. **`create_production()` instantiation** (around line 69-76): add:
     ```python
     try:
         llm_provider = LLMProviderFactory.create()
     except LLMConfigError:
         llm_provider = None
     ```
  5. **`create_production()` module-level setter** (around line 80-95): add:
     ```python
     from game.services.llm import set_default_llm_provider
     set_default_llm_provider(llm_provider)
     ```
  6. **`create_production()` return** (around line 103-112): add `llm_provider=llm_provider,` to the `cls(...)` call
  7. **`create_test()` defaults dict** (around line 132-141): add `'llm_provider': None,` (tests inject explicitly when needed)
- [ ] Run `pytest tests/unit/core/test_application_context.py`, confirm pass
- [ ] Run full sharded suite to confirm no regression in any of the 11 files that reference `ApplicationContext`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] ~3 new tests in `test_application_context.py` + `test_defaults.py`
- [ ] `pytest tests/unit/core/ tests/unit/services/llm/` — all green
- [ ] Full sharded suite — baseline preserved
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 7
