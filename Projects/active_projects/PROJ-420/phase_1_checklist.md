# Phase 1: Introduce shared registries-cache helper and migrate 3 modules

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-420 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Introduce a single helper (e.g. `game/core/registry_cache.py::get_cached_registries()`) that owns the lazy-init `GameRegistries` instance, and migrate the 3 modules that currently duplicate the pattern. PROJ-258 ApplicationContext migration is out of scope; the helper is a focused consolidation step.

Severity tier: Minor (consolidation; defers full ApplicationContext migration).

---

## Tasks

### Task 1.1: Introduce shared registries-cache helper
**File:** `game/core/registry_cache.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Create `game/core/registry_cache.py` with `def get_cached_registries() -> GameRegistries` and an internal module-level cache (single source of truth for the lazy `get_default_registry_provider() -> GameRegistries` pattern)
- [ ] Add a `reset_cached_registries()` test-helper for `conftest.py` style resets

---

### Task 1.2: Migrate game/ui/services/ship_io.py
**File:** `game/ui/services/ship_io.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Replace the `_cached_registries` global at `ship_io.py:39` and its `get_default_*()` lazy-init block with a call to `get_cached_registries()` from the new helper
- [ ] Remove the `global` keyword usage in this module

---

### Task 1.3: Migrate game/ui/screens/strategy_build_queue_manager.py
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Replace the `_cached_registries` global at `strategy_build_queue_manager.py:40` and its lazy-init block with `get_cached_registries()`
- [ ] Remove the `global` keyword usage in this module

---

### Task 1.4: Migrate game/ui/screens/setup_data_io.py
**File:** `game/ui/screens/setup_data_io.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Replace the `_ship_factory` global at `setup_data_io.py:30` with `ShipFactory(registry_provider=get_cached_registries())` constructed inline (ShipFactory.__init__ only stores the ref — no expensive work)
- [ ] Remove the `global` keyword usage in this module
- [ ] Update any tests that currently patch `game.ui.screens.setup_data_io._ship_factory` directly — rewrite to patch `ShipFactory` or `get_cached_registries()` instead

---

### Task 1.5: Delete dead code in game/ui/screens/setup_screen.py
**File:** `game/ui/screens/setup_screen.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Delete the dead `_ship_factory = None` global (line ~48) and the entire `_get_ship_factory()` function (lines ~51-65): this function is defined but never called — all IO is delegated to `setup_data_io.py`
- [ ] Remove the now-unused `from game.ui.services.ship_factory import ShipFactory` import if no other usage in the module remains
- [ ] Verify: `pytest tests/ --testmon` passes; `grep -rn 'global _cached_registries\|global _ship_factory' game/` returns zero hits

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

---

_Source audit: `Reviews/results/2026-05-13_194106_legacy-audit/`. See `findings/source_audit.md` for the link._
