# Phase 4: Complex Legacy Eradication

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-109 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove deeply embedded legacy code: save migration, registry fallbacks, wrapper functions, deprecated AI init paths. High impact, commit after each task.

---

## Tasks

### Task 4.1: Remove save game version migration [Medium]
**Finding:** LEG-STR-001
**File:** `game/strategy/systems/save_game_service.py:30-32, 165, 382-421`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] Delete `MIGRATABLE_VERSIONS` list (line 30-32)
- [ ] Simplify `_is_compatible_version()` (lines 382-397): return `save_version == SaveGameService.SAVE_VERSION`
- [ ] Delete `_can_migrate_version()` method entirely (lines 399-421)
- [ ] In `load_game()` line 165: the check `if not SaveGameService._is_compatible_version(save_version)` now strictly rejects all old versions
- [ ] Delete the migration log message at lines 169-170 (`if save_version != ...`)
- [ ] Update the module docstring (line 10) to say "Strict version checking (rejects all old saves)"
- [ ] Remove the misleading comment at line 30 about modifier system compatibility
- [ ] Verify: loading a save with version != 2.0.0 returns error message
- [ ] Commit: "PROJ-109: Remove save game migration (disposable saves policy)"

**Notes:**

---

### Task 4.2: Remove bootstrap registry fallback in load_components_data [Complex]
**Finding:** LEG-SIM-001
**File:** `game/simulation/components/component.py:498-507`
**Tests:** `pytest tests/ -n 12` (broad impact)

- [ ] In `load_components_data()`: Make `registries` parameter required (remove `Optional`, remove `= None`)
- [ ] Delete the bootstrap fallback block (lines 498-507): the `if registries is None:` block that creates registries from provider
- [ ] Add `if registries is None: raise TypeError("registries is required")` guard
- [ ] Grep for callers of `load_components_data(`: found in `component.py:566` (load_components wrapper)
- [ ] In `load_components()` (line 566): the call to `load_components_data(file_path)` needs registries - this function itself uses the global provider, so pass `registries=GameRegistries(...)` from provider
- [ ] Grep for external callers: `tests/unit/core/test_pure_loaders.py`, `conftest.py`, `simulation_tests/conftest.py`
- [ ] Update all external callers to pass `registries` explicitly
- [ ] Remove the `from game.core.registry import get_default_registry_provider` import if no longer needed in component.py
- [ ] Verify: no code path calls `load_components_data()` without registries
- [ ] Commit: "PROJ-109: Require registries in load_components_data (strict DI)"

**Notes:**

---

### Task 4.3: Remove backward compatibility wrapper functions [Medium]
**Finding:** LEG-SIM-003
**Files:**
- `game/simulation/components/component.py:545-577` (load_components)
- `game/simulation/components/component.py:638-668` (load_modifiers)
- `game/simulation/entities/ship_loader.py:100-130` (load_vehicle_classes)
**Callers:**
- `load_components()`: `game/simulation/services/registry_loader.py`, `game/app.py`, `game/ui/screens/workshop_data_loader.py`
- `load_modifiers()`: `game/simulation/services/registry_loader.py`, `game/app.py`, `game/ui/screens/workshop_data_loader.py`
- `load_vehicle_classes()`: `game/simulation/services/registry_loader.py`, `game/ui/screens/workshop_data_loader.py`
**Tests:** `pytest tests/ -n 12` (broad impact)

- [ ] For `load_components()` (lines 545-577): migrate callers to use `load_components_data()` + registry population, then delete wrapper
- [ ] For `load_modifiers()` (lines 638-668): migrate callers to use `load_modifiers_data()` + registry population, then delete wrapper
- [ ] For `load_vehicle_classes()` (lines 100-130): migrate callers to use `load_vehicle_classes_data()` + registry population, then delete wrapper
- [ ] Alternative: If migration is too broad, just remove the "backward compatibility" comments and rename wrappers to remove the "thin wrapper" framing
- [ ] Update imports in all caller files
- [ ] Verify: no "backward compat" framing in function docstrings
- [ ] Commit: "PROJ-109: Remove backward compatibility wrapper functions"

**Notes:** This task may be split if full wrapper removal is too risky. The minimum viable change is removing the "backward compatibility" framing and making the wrappers the canonical API.

---

### Task 4.4: Remove deprecated AI controller initialization paths [Medium]
**Finding:** LEG-SIM-004
**File:** `game/simulation/systems/battle_engine.py:267-292, 338-352`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ tests/unit/ai/ -n 12`

- [ ] In `start()` method (around line 267): Remove the `else` branch that creates AIController directly
- [ ] Require `ai_controllers` or `ai_factory` parameter - if neither provided, raise TypeError
- [ ] In `add_ship_mid_battle()` (around line 338): Remove the `else` branch (lines 339-352)
- [ ] Require `ai_controller` or `ai_factory` for mid-battle ship additions
- [ ] Remove the `import warnings` if no longer needed in this scope
- [ ] Remove `from game.ai.controller import AIController` lazy imports in the deleted branches
- [ ] Grep for callers that use `start()` without ai_controllers/ai_factory: update them
- [ ] Focus on: `tests/unit/combat/test_battle_setup_logic.py`, `tests/unit/ai/test_ai.py`, `tests/unit/ai/test_movement_and_ai.py`
- [ ] Verify: no DeprecationWarning for BattleEngine in test output
- [ ] Commit: "PROJ-109: Require AI factory/controllers in BattleEngine (remove deprecated init)"

**Notes:**

---

### Task 4.5: Remove global registry fallback in simulation adapters [Medium]
**Finding:** LEG-STR-002
**Files:**
- `game/strategy/adapters/simulation_adapter.py:43, 52-53`
- `game/strategy/data/fleet_battle_adapter.py:42, 52-53`
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ -n 12`

- [ ] In `simulation_adapter.py`: Make `registries` parameter required (remove `Optional`, remove `= None` default)
- [ ] Remove the "(transitional - will be required in Phase 6)" comment
- [ ] Add `if registries is None: raise TypeError(...)` guard
- [ ] In `fleet_battle_adapter.py`: Make `registries` parameter required similarly
- [ ] Grep for callers: verify all callers pass registries
- [ ] Verify: no `Optional` registries remain in these adapter files
- [ ] Commit: "PROJ-109: Require registries in simulation adapters (strict DI)"

**Notes:**

---

### Task 4.6: Remove FleetOrder legacy `coord` serialization format [Simple]
**Finding:** LEG-STR-007 (partial - only truly legacy branch)
**File:** `game/strategy/data/fleet.py:392-394`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] Delete the `elif target_data.get('type') == 'coord':` branch (lines 392-394) which handles `{'type': 'coord', 'value': [x,y]}`
- [ ] Remove the comment about "Tuple-style coord format"
- [ ] Update the comment block at lines 374-381 to remove reference to format 2 (`coord` type)
- [ ] Verify: `grep -r "'coord'" game/strategy/` confirms no code produces this format
- [ ] Commit: "PROJ-109: Remove legacy coord serialization format from FleetOrder"

**Notes:** See DEC-004 - only the `coord` branch is truly legacy. All other branches are active current formats.

---

### Task 4.7: Remove Empire serialization legacy visual identity comment [Simple]
**Finding:** LEG-STR-012
**File:** `game/strategy/data/empire.py:155-158`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] Replace "Include race visual identity if set (backwards compatibility)" comment with "Include race visual identity if set"
- [ ] The conditional serialization of flag_id and portrait_id is correct behavior (optional fields)

**Notes:**

---

### Task 4.8: Remove MagicMock detection in target_evaluator [Simple]
**Finding:** LEG-FND-006
**File:** `game/ai/target_evaluator.py:53-67`
**Tests:** `pytest tests/unit/ai/ -n 12`

- [ ] Simplify `_get_position()`: Use `get_position()` interface if available, otherwise `entity.position` directly
- [ ] Remove the `_is_vector2_like` check and the MagicMock detection logic
- [ ] Remove the "MagicMock" comment
- [ ] Keep the basic try/except for interface method failure (that's defensive programming, not legacy)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` passes (8164 baseline)
- [ ] No DeprecationWarnings for BattleEngine in test output
- [ ] No "backward compat" or "transitional" comments in modified files
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
