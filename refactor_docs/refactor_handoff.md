# Ability System Refactor - Handoff & Test Ledger

## 1. High-Level Context
**Refactor Goal**: Transition from Inheritance-based Components (`Engine`, `Weapon`) to Composition-based Components (`Component` + `Abilities`).

**Current Phase**: ✅ Phase 6 COMPLETE (Data Migration)  
**Tests**: 470/470 PASSED (as of 2026-01-02)

**Status Summary**:
- Phase 1 ✅ Foundation (abilities.py created)
- Phase 2 ✅ Core Refactor (Component class, Legacy Shim)
- Phase 3 ✅ Stats & Physics Integration
- Phase 4 ✅ Combat System Complete
- Phase 5 ✅ UI & Capabilities Complete
- Phase 6 ✅ Data Migration COMPLETE
- **Phase 7 ⏳ Legacy Removal (Planned)**
  - ✅ Added `CommandAndControl` ability to `abilities.py`
  - ✅ Created migration script `scripts/migrate_legacy_components.py`
  - ✅ Migrated `data/components.json` (7 weapons, 2 engines, 2 thrusters)
  - ✅ Fixed weapon constructors to read from ability dicts
  - ✅ Fixed `WeaponAbility` to handle formula strings in damage/range/reload
  - ✅ Fixed `_apply_base_stats()` to read from ability dicts instead of data root
  - ✅ All 470 tests passing

---

## 2. PHASE 6 FINAL FIX SUMMARY

### Root Cause
After data migration, weapon stats (`range`, `firing_arc`, `damage`) moved from root level to ability dicts (e.g., `abilities.BeamWeaponAbility.range`). However, `_apply_base_stats()` still read from `self.data.get()` at root level, returning defaults (0/3) instead of actual values.

### Fix Applied
Added `get_weapon_data_for_stats()` helper in `_apply_base_stats()` that:
1. Checks root data first
2. Falls back to ability dicts (`ProjectileWeaponAbility`, `BeamWeaponAbility`, `SeekerWeaponAbility`)

### Files Modified
- `components.py`: Added helper in `_apply_base_stats()` (lines 479-490)
- `unit_tests/test_components.py`: Updated `test_range_stacking` to use `railgun.range`

---

## 3. Files Modified This Session

| File | Changes |
|------|---------|
| `abilities.py` | Added `CommandAndControl` class; Updated `WeaponAbility.__init__` to handle formula strings, store `_base_damage/_base_range/_base_reload` |
| `components.py` | Updated `Weapon/ProjectileWeapon/BeamWeapon` constructors for ability dict reading; Updated `_instantiate_abilities` shim; Fixed `_apply_base_stats` to use base values |
| `ui/builder/modifier_logic.py` | Updated to read `firing_arc` from ability dicts |
| `data/components.json` | Migrated by script (weapon stats moved to ability dicts) |
| `scripts/migrate_legacy_components.py` | Created migration script |
| `unit_tests/test_combat_endurance.py` | Updated to read from ability dicts |
| `unit_tests/test_modifier_defaults_robustness.py` | Updated assertions for new data structure |

---

## 4. Key Changes Summary

### 4.1 Data Migration (components.json)
Weapon stats (`damage`, `range`, `reload`, `firing_arc`, `projectile_speed`, `accuracy_falloff`, `base_accuracy`) moved from root level to ability dicts:
```json
// BEFORE
{"id": "railgun", "damage": 40, "range": 2400, ...}

// AFTER  
{"id": "railgun", "abilities": {"ProjectileWeaponAbility": {"damage": 40, "range": 2400, ...}}}
```

### 4.2 Formula String Handling
`WeaponAbility.__init__` now handles formula strings like `"=40 - (0.01 * range_to_target)"`:
- Evaluates at range 0 for base display value
- Stores `damage_formula` for runtime evaluation
- Stores `_base_damage`, `_base_range`, `_base_reload` for modifier sync

### 4.3 Constructor Shims
`Weapon`, `ProjectileWeapon`, `BeamWeapon` constructors now check both root level AND ability dicts for weapon stats using `get_weapon_data()` helper.

---

## 5. Test Verification Commands

```powershell
# Run full suite
python -m pytest unit_tests/ -n 16 --tb=no -q

# Run specific failing test with details
python -m pytest unit_tests/test_multitarget.py::TestMultitarget::test_pdc_missile_logic -v --tb=long
```

---

## 6. Next Steps (Phase 7)

1.  **Execute Legacy Removal Plan**: Follow `refactor_docs/legacy_removal_plan.md`.
2.  **Start with Stage 1**: Critical fixes in `ship_stats.py` (Shield Calculation Bug).
3.  **Proceed to Stage 2**: Systematic removal of `isinstance` checks in Core and Combat systems.
