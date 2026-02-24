# Phase 2: Internalize RegistryManager

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-174 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove RegistryManager from `__all__`, making it an internal implementation detail. Update module docstring to show only TIER 1 pattern.

---

## Tasks

### Task 2.1: Remove RegistryManager from __all__ [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/ -v`

- [ ] Remove `'RegistryManager'` from `__all__` list (lines 29-43)
- [ ] Keep: GameRegistries, DefaultRegistryProvider, TestRegistryProvider, get_default_registry_provider, get_default_registries, set_default_registries, freeze_registry, clear_registry, set_validator
- [ ] Verify: `from game.core.registry import *` no longer exports RegistryManager

**Notes:** Composition roots (app.py, conftest.py) import RegistryManager by name — this still works even without __all__. Only `import *` is affected.

### Task 2.2: Update module docstring [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/refactor/test_deprecated_code_removed.py -v`

- [ ] Replace module docstring (lines 1-27) with single TIER 1 pattern:
  ```python
  """
  Registry Access
  ===============

  Dependency Injection [RECOMMENDED]:
      from game.core.registry import get_default_registry_provider

      # Production - uses the shared singleton-backed provider
      provider = get_default_registry_provider()
      components = provider.get_components()

      # Or receive via constructor (best):
      def __init__(self, registry: IRegistryProvider):
          self._registry = registry

      # Test - uses isolated data
      from game.core.registry import TestRegistryProvider
      provider = TestRegistryProvider(
          components={"test_laser": {...}},
          modifiers={},
          resources={}
      )

  Lifecycle (composition roots only):
      from game.core.registry import freeze_registry, clear_registry
      freeze_registry()   # After initialization
      clear_registry()    # Test cleanup
  """
  ```
- [ ] Verify: Docstring reflects single canonical pattern

**Notes:** Check if test_deprecated_code_removed.py asserts on specific docstring content and update accordingly.

### Task 2.3: Full suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: 12,023+ passed, 0 failed
- [ ] Verify no import errors from __all__ change

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
