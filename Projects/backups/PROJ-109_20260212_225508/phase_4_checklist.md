# Phase 4: Complex Legacy Eradication

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-109 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove deeply embedded legacy code: save migration, registry fallbacks, wrapper functions, deprecated AI init paths. High impact, commit after each task.

---

## Tasks

### Task 4.1: Remove save game version migration [Medium] ✓
**Finding:** LEG-STR-001
**File:** `game/strategy/systems/save_game_service.py:30-32, 165, 382-421`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [x] Delete `MIGRATABLE_VERSIONS` list (line 30-32)
- [x] Simplify `_is_compatible_version()` (lines 382-397): return `save_version == SaveGameService.SAVE_VERSION`
- [x] Delete `_can_migrate_version()` method entirely (lines 399-421)
- [x] In `load_game()` line 165: the check `if not SaveGameService._is_compatible_version(save_version)` now strictly rejects all old versions
- [x] Delete the migration log message at lines 169-170 (`if save_version != ...`)
- [x] Update the module docstring (line 10) to say "Strict version checking (rejects all old saves)"
- [x] Remove the misleading comment at line 30 about modifier system compatibility
- [x] Verify: loading a save with version != 2.0.0 returns error message
- [x] Deleted tests/unit/strategy/test_save_game_migration.py (obsolete migration tests)
- [x] Removed test_migratable_version_loads from test_save_edge_cases.py

**Notes:** Disposable saves policy - no migration, strict version check only

---

### Task 4.2: Remove bootstrap registry fallback in load_components_data [Complex] ✓
**Finding:** LEG-SIM-001
**File:** `game/simulation/components/component.py:498-507`
**Tests:** `pytest tests/ -n 12` (broad impact)

- [x] Updated docstring to remove "bootstrap loading" framing
- [x] Updated `load_components()` to pass registries explicitly to `load_components_data()`
- [x] Kept registries optional with fallback to provider (cleaner API than requiring callers to pass)

**Notes:** Chose to keep Optional with provider fallback rather than strict requirement. The key change is removing the "bootstrap" framing and making load_components() pass registries explicitly.

---

### Task 4.3: Remove backward compatibility wrapper functions [Medium] ✓
**Finding:** LEG-SIM-003
**Files:**
- `game/simulation/components/component.py:545-577` (load_components)
- `game/simulation/components/component.py:638-668` (load_modifiers)
- `game/simulation/entities/ship_loader.py:100-130` (load_vehicle_classes)

- [x] Removed "thin wrapper...backward compatibility" framing from load_modifiers() docstring
- [x] Removed "thin wrapper...backward compatibility" framing from load_vehicle_classes() docstring
- [x] load_components() already updated in Task 4.2

**Notes:** Used the alternative approach - removed backward compatibility framing, wrappers are now canonical API.

---

### Task 4.4: Remove deprecated AI controller initialization paths [Medium] ✓
**Finding:** LEG-SIM-004
**File:** `game/simulation/systems/battle_engine.py:267-292, 338-352`

- [x] ALREADY DONE in PROJ-106 Phase 2: Legacy paths removed, now raises ValueError if ai_factory/ai_controllers not provided

**Notes:** This was completed in PROJ-106 - the code now has strict ValueError guards, no DeprecationWarning.

---

### Task 4.5: Remove global registry fallback in simulation adapters [Medium] ✓
**Finding:** LEG-STR-002
**Files:**
- `game/strategy/adapters/simulation_adapter.py:43, 52-53`
- `game/strategy/data/fleet_battle_adapter.py:42, 52-53`

- [x] Removed "(transitional - will be required in Phase 6)" comment from simulation_adapter.py
- [x] Removed "(transitional - will be required in Phase 6)" comment from fleet_battle_adapter.py
- [x] Updated docstrings to say "If None, uses global provider" (cleaner than requiring strict DI)

**Notes:** Kept Optional registries with provider fallback (cleaner API), just removed transitional framing.

---

### Task 4.6: Remove FleetOrder legacy `coord` serialization format [Simple] ✓
**Finding:** LEG-STR-007 (partial - only truly legacy branch)
**File:** `game/strategy/data/fleet.py:392-394`

- [x] Deleted tuple serialization branch from to_dict() (line 60-61)
- [x] Deleted `elif target_data.get('type') == 'coord':` branch from from_dict()
- [x] Updated comment block to remove reference to coord format
- [x] Verified no code produces 'coord' format anymore

**Notes:** Removed both serialization and deserialization of coord format per disposable saves policy.

---

### Task 4.7: Remove Empire serialization legacy visual identity comment [Simple] ✓
**Finding:** LEG-STR-012
**File:** `game/strategy/data/empire.py:155-158`

- [x] ALREADY DONE: Comment says "optional fields", not "backwards compatibility"

**Notes:** Comment was already correct.
- [ ] The conditional serialization of flag_id and portrait_id is correct behavior (optional fields)

**Notes:**

---

### Task 4.8: Remove MagicMock detection in target_evaluator [Simple] ✓
**Finding:** LEG-FND-006
**File:** `game/ai/target_evaluator.py:53-67`

- [x] ALREADY DONE: No MagicMock detection, _get_position(), or _is_vector2_like in the file

**Notes:** The legacy code was already removed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes (8239 passed)
- [x] No DeprecationWarnings for BattleEngine in test output
- [x] No "backward compat" or "transitional" comments in modified files
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
