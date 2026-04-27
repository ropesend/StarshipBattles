# Phase 3: LLMProviderFactory [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-296 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Provider selection by env var. Uses a stub provider for unit tests; the real DeepSeek provider lands in Phase 4. Returns `None` if no provider can be constructed (deferred validation).

---

## Tasks

### Task 3.1: Create `_StubProvider` test fixture [Simple]
**File:** `tests/unit/services/llm/conftest.py` (NEW)
**Tests:** None (fixture only)

- [ ] Create a `_StubProvider` class implementing `LLMProvider`. Returns a hardcoded `CompletionResult` from `complete()`. Used by Phase 3 + 5 tests.
- [ ] Expose as a pytest fixture `stub_llm_provider`
- [ ] Add `mock_llm_provider` fixture using `unittest.mock.MagicMock(spec=LLMProvider)` for tests that need to assert call shape

**Notes:**

### Task 3.2: Implement `LLMProviderFactory` [Medium]
**File:** `game/services/llm/factory.py` (NEW)
**Tests:** `pytest tests/unit/services/llm/test_factory.py`

- [ ] Write failing tests:
  - `LLMProviderFactory.create()` reads `LLM_PROVIDER` env var (default `"deepseek"`)
  - When provider name is in `_PROVIDERS` registry, returns the registered class instance
  - When provider name is unknown, raises `LLMConfigError` with code `L001` and `context={'provider': '<bad name>'}`
  - When a registered provider's constructor raises `LLMConfigError` (e.g., no API key), `create()` returns `None` (NOT a partially-built provider, NOT propagating)
  - `_PROVIDERS` is a module-level dict, not hardcoded if/elif (per `docs/03_CONVENTIONS.md` §6.5)
- [ ] Implement:
  ```python
  # game/services/llm/factory.py
  import os
  from typing import Dict, Type, Optional

  from game.core.exceptions import LLMConfigError
  from game.core.error_codes import ErrorCode
  from game.services.llm.provider import LLMProvider

  _PROVIDERS: Dict[str, Type[LLMProvider]] = {}

  def register_provider(name: str, provider_cls: Type[LLMProvider]) -> None:
      """Register a provider implementation under a string name."""
      _PROVIDERS[name] = provider_cls

  class LLMProviderFactory:
      @staticmethod
      def create(name: Optional[str] = None) -> Optional[LLMProvider]:
          """Create a provider by name (or LLM_PROVIDER env var, default 'deepseek').
          Returns None if the registered provider can't initialize (e.g., no API key).
          Raises LLMConfigError if the name is unknown."""
          if name is None:
              name = os.environ.get("LLM_PROVIDER", "deepseek")
          cls = _PROVIDERS.get(name)
          if cls is None:
              raise LLMConfigError(
                  f"Unknown LLM provider '{name}'. Registered: {list(_PROVIDERS)}",
                  code=ErrorCode.LLM_CONFIG_MISSING.value,
                  context={'provider': name, 'registered': list(_PROVIDERS)},
              )
          try:
              return cls()
          except LLMConfigError:
              return None
  ```
- [ ] Tests register `_StubProvider` via `register_provider('stub', _StubProvider)` then call `LLMProviderFactory.create('stub')`. Use a fixture to clean up `_PROVIDERS` between tests.
- [ ] Run tests, confirm pass

**Notes:**

### Task 3.3: Add factory + `register_provider` to package exports [Simple]
**File:** `game/services/llm/__init__.py`
**Tests:** `pytest tests/unit/services/llm/`

- [ ] Add `LLMProviderFactory` and `register_provider` to imports + `__all__`
- [ ] Run all `tests/unit/services/llm/` tests, confirm green

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] ~6 new tests in `test_factory.py`
- [ ] `pytest tests/unit/services/llm/` — all green
- [ ] No regression
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 4
