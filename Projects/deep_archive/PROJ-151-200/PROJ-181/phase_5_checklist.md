# Phase 5: Documentation Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-181 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix stale documentation showing deprecated registry access patterns as recommended usage.

---

## Tasks

### Task 5.1: Update component_system.md [Simple]
**File:** `docs/guides/component_system.md:134-139`
**Tests:** N/A (documentation)

- [x] Replace deprecated example (lines 134-139):
  ```python
  # CURRENT (wrong):
  from game.core.registries import get_default_registries
  registries = get_default_registries()
  comp_data = registries.components.get('laser_mk1')
  component = Component(comp_data)

  # REPLACEMENT:
  from game.core.registry import get_default_registry_provider
  provider = get_default_registry_provider()
  comp_data = provider.get_components().get('laser_mk1')
  component = Component(comp_data)
  ```
- [x] Note: Also fixes module name (`registries` -> `registry`)

**Notes:** Updated lines 134-140 with correct provider pattern.

### Task 5.2: Review PATTERNS.md singleton section [Simple]
**File:** `docs/architecture/PATTERNS.md`
**Tests:** N/A (documentation)

- [x] In the Singleton Pattern section (lines ~63-93), add a note that `RegistryManager.instance()` is internal-only for composition roots
- [x] Add reference to `get_default_registry_provider()` as the recommended pattern for consumers

**Notes:** Added "Access Pattern" column to table, new "Registry Access Pattern" subsection with code example, and updated Usage Guidelines with point 5.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Verify no documentation references `get_default_registries` or `game.core.registries`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
