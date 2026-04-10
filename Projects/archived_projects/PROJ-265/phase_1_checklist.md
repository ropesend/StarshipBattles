# Phase 1 Checklist: component_loader.py Unit Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-265 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create dedicated test file for `component_loader.py`, covering all error paths, cache behavior, and factory function guards. Raise coverage from 64.2% toward 95%+.

**Test File:** `tests/unit/simulation/components/test_component_loader.py` (new)
**Source File:** `game/simulation/components/component_loader.py`

---

## Task 1.1: load_components_data Error Paths [Medium]
**Tests:** `pytest tests/unit/simulation/components/test_component_loader.py -v -k "test_load_components_data"`

- [ ] Write test: `load_components_data` with nonexistent file path returns empty dict (lines 93-99)
- [ ] Write test: `load_components_data` with nonexistent file logs error message
- [ ] Write test: `load_components_data` with malformed JSON returns empty dict (lines 126-128)
- [ ] Write test: `load_components_data` with JSON missing 'components' key returns empty dict (lines 123-125)
- [ ] Write test: `load_components_data` with invalid component data (bad dict) logs error, returns partial dict with valid components (lines 111-116)
- [ ] Write test: `load_components_data` with component raising AttributeError logs error, returns partial dict (lines 114-116)
- [ ] Run tests -- confirm they pass against existing production code
- [ ] Verify coverage of lines 93-99, 111-116, 123-128

**Approach:** Use `tmp_path` fixture to create temporary JSON files with malformed/invalid content. Pass a real `GameRegistries` with empty dicts for the registries parameter.

**Notes:** [Filled during implementation]

---

## Task 1.2: load_modifiers_data Error Paths [Medium]
**Tests:** `pytest tests/unit/simulation/components/test_component_loader.py -v -k "test_load_modifiers_data"`

- [ ] Write test: `load_modifiers_data` with nonexistent file path returns empty dict (lines 194-201)
- [ ] Write test: `load_modifiers_data` with nonexistent file logs error message
- [ ] Write test: `load_modifiers_data` with malformed JSON returns empty dict (lines 227-228)
- [ ] Write test: `load_modifiers_data` with JSON missing 'modifiers' key returns empty dict (lines 224-226)
- [ ] Write test: `load_modifiers_data` with invalid modifier data logs error, returns partial dict (lines 215-218)
- [ ] Run tests -- confirm they pass against existing production code
- [ ] Verify coverage of lines 194-201, 215-218, 224-228

**Approach:** Same as Task 1.1 -- use `tmp_path` for temporary JSON files. `load_modifiers_data` has no `registries` param (simpler).

**Notes:** [Filled during implementation]

---

## Task 1.3: load_components / load_modifiers Registry Guards [Simple]
**Tests:** `pytest tests/unit/simulation/components/test_component_loader.py -v -k "test_load_components_guard or test_load_modifiers_guard"`

- [ ] Write test: `load_components(registry_provider=None)` raises ValueError (line 146)
- [ ] Write test: `load_modifiers(registry_provider=None)` raises ValueError (line 244)
- [ ] Run tests -- confirm they pass

**Notes:** [Filled during implementation]

---

## Task 1.4: Cache Hit Paths [Medium]
**Tests:** `pytest tests/unit/simulation/components/test_component_loader.py -v -k "test_cache"`

- [ ] Write test: `load_components` second call with same file_path uses cache (lines 154-157) -- verify component_cache is populated after first call, cloned on second
- [ ] Write test: `load_modifiers` second call with same file_path uses cache (lines 253-256) -- verify modifier_cache is populated after first call, deep-copied on second
- [ ] Write test: `reset_component_caches()` clears both caches and allows fresh load
- [ ] Write test: `load_components` with different file_path bypasses cache (cache key is file_path)
- [ ] Run tests -- confirm they pass

**Approach:** Use a mock `registry_provider` with real dict returns. Use a real small components JSON via `tmp_path`. Call `reset_component_caches()` in test setup for isolation. Verify cache population by inspecting `get_default_cache_manager()` state.

**Notes:** [Filled during implementation]

---

## Task 1.5: Factory Function Guards [Simple]
**Tests:** `pytest tests/unit/simulation/components/test_component_loader.py -v -k "test_create_component or test_get_all_components"`

- [ ] Write test: `create_component(registries=None)` raises `ValidationException` with `ErrorCode.MISSING_DEPENDENCY` (lines 285-290)
- [ ] Write test: `get_all_components(registries=None)` raises `ValidationException` with `ErrorCode.MISSING_DEPENDENCY` (lines 312-317)
- [ ] Write test: `create_component` with valid registries and existing component_id returns a clone
- [ ] Write test: `create_component` with valid registries and nonexistent component_id returns None (line 297-298)
- [ ] Write test: `get_all_components` with valid registries returns list of components (line 318)
- [ ] Run tests -- confirm they pass

**Approach:** Use a mock `GameRegistries` with a dict containing a mock component (with `.clone()` returning a fresh mock). For None tests, just pass `registries=None`.

**Notes:** [Filled during implementation]

---

## Task 1.6: Full Phase Verification [Simple]
**Tests:** `pytest tests/unit/simulation/components/test_component_loader.py -v`

- [ ] Run full new test file -- all tests pass
- [ ] Run existing simulation tests: `pytest tests/unit/simulation/ -v` -- no regressions
- [ ] Measure coverage: `pytest tests/unit/simulation/components/test_component_loader.py --cov=game/simulation/components/component_loader --cov-report=term-missing`
- [ ] Verify coverage improvement from 64.2% baseline

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
