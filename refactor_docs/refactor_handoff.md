# Ability System Refactor - Handoff & Test Ledger

## 1. High-Level Context
**Refactor Goal**: Transition from Inheritance-based Components (`Engine`, `Weapon`) to Composition-based Components (`Component` + `Abilities`).

**Current Phase**: Phase 4 In Progress  
**Tests**: 462/462 PASSED (baseline as of 2026-01-02)

**Status Summary**:
- Phase 1 ✅ Foundation (abilities.py created)
- Phase 2 ✅ Core Refactor (Component class, Legacy Shim)
- Phase 3 ✅ Stats & Physics Integration
- Phase 4 🔄 Combat System Migration (PARTIAL - see remaining tasks below)
- Phase 5 ⬜ UI & Capabilities
- Phase 6 ⬜ Data Migration

---

## 2. Phase 4 Completed Work

The following Phase 4 tasks have been completed:

| Task | File | Status |
|------|------|--------|
| `Ship.max_weapon_range` → ability iteration | ship.py:231-252 | ✅ Done |
| Replace `isinstance(Hangar)` in fire_weapons | ship_combat.py:64 | ✅ Done |
| Replace `isinstance(Weapon)` in fire_weapons | ship_combat.py:78 | ✅ Done |
| PDC detection → `has_pdc_ability()` | ship_combat.py:108 | ✅ Done |
| Replace `isinstance(Weapon)` in ai.py:369 | ai.py:369 | ✅ Done |
| Replace `isinstance(Engine,Thruster)` in ai.py:505 | ai.py:502-506 | ✅ Done |
| Add `has_pdc_ability()` helper | components.py:152-168 | ✅ Done |

---

## 3. Phase 4 Remaining Work (CRITICAL)

The following issues were identified by independent code reviews and **MUST be completed** before Phase 5:

### 3.1 Weapon Subclass isinstance Checks (ship_combat.py)

| Line | Current Code | Replacement |
|------|--------------|-------------|
| 117 | `isinstance(comp, SeekerWeapon)` | `comp.has_ability('SeekerWeaponAbility')` | ✅ Done |
| 135 | `isinstance(comp, SeekerWeapon)` | `comp.has_ability('SeekerWeaponAbility')` | ✅ Done |
| 149 | `isinstance(comp, BeamWeapon)` | `comp.has_ability('BeamWeaponAbility')` | ✅ Done |
| 174 | `isinstance(comp, SeekerWeapon)` | `comp.has_ability('SeekerWeaponAbility')` | ✅ Done |
| 253 | `isinstance(comp, ProjectileWeapon)` | `comp.has_ability('ProjectileWeaponAbility')` | ✅ Done |

### 3.2 Direct Attribute Access (ship_combat.py)

Lines using `comp.damage` and `comp.range` directly:
- Lines 116, 161, 162, 190, 191, 212, 213, 236

**Action**: Continue using legacy shim for now OR create accessor methods on Component.

### 3.3 Resource Legacy Path (ship_combat.py:22-42)

Shield regeneration energy consumption bypasses ability system:
```python
energy_res.consume(cost_amount)  # Direct call at line 34
```

**Action**: Migrate to check `is_operational` on ShieldRegenerator components.

### 3.4 EnergyConsumption Trigger Bug (abilities.py:278) - ✅ FIXED

```python
"trigger": "constant"  # FIXED - was "conditional"
```

---

## 4. Phase 5 Scope (UI Migration)

Identified by code reviews. **32 total isinstance checks** to replace:

| File | Checks | Priority |
|------|--------|----------|
| weapons_panel.py | 8 | High |
| schematic_view.py | 4 | High |
| detail_panel.py | 1 | High |
| battle_ui.py | 2 | Medium |
| battle_panels.py | 2 | Medium |
| rendering.py | 3 | Low |
| modifier_logic.py | type_str checks | Medium |

### Test Coverage Gaps

Add tests for:
- `BeamWeaponAbility`, `SeekerWeaponAbility`, `ResourceGeneration`
- `get_abilities()`, `has_pdc_ability()` helper methods
- Update `MockPDC` in test_pdc.py to use tag-based detection

---

## 5. Test Ledger

| Test File | Status | Target Phase |
|-----------|--------|--------------|
| test_components.py | **Active** | Phase 2 |
| test_component_resources.py | **Active** | Phase 2 |
| test_component_composition.py | **Active** | Phase 2 |
| test_legacy_shim.py | **Active** | Phase 2 |
| test_ship_stats.py | **Active** | Phase 3 |
| test_ship_physics_mixin.py | **Active** | Phase 3 |
| test_weapons.py | **Active** | Phase 4 |
| test_pdc.py | **Active** | Phase 4 |
| test_fighter_launch.py | **Active** | Phase 4 |
| test_ai.py | **Active** | Phase 4 |
| test_battle_panels.py | **Active** | Phase 5 |
| test_ui_dynamic_update.py | **Active** | Phase 5 |
| test_builder_validation.py | **Active** | Phase 6 |

---

## 6. Next Agent Instructions

### Immediate Actions (Phase 4 Completion)

1. ✅ **COMPLETED** - Fixed EnergyConsumption trigger in `abilities.py:278`

2. ✅ **COMPLETED** - Replaced weapon subclass isinstance checks in `ship_combat.py`

3. **Run tests after each change**:
   ```powershell
   python -m pytest unit_tests/ -n 16 --tb=no -q
   ```

### Key Files

- `ship_combat.py` - Main focus for remaining Phase 4 work
- `abilities.py` - EnergyConsumption trigger fix
- `components.py` - `has_pdc_ability()` already implemented

### Cautions

- **PDC backward compatibility**: `has_pdc_ability()` checks both new tag system (`'pdc' in ab.tags`) AND legacy dict (`abilities.get('PointDefense')`)
- **Legacy shim active**: `comp.damage`/`comp.range` still work via shim - no rush to migrate these
- **Test baseline**: 462 tests must all pass before Phase 5

---

## 7. Reference: Completed Phase 3 Changes

| Change | Location |
|--------|----------|
| Modifier-to-Ability Sync | components.py:538-564 |
| `Ship.get_total_ability_value()` | ship.py:546-578 |
| Engine/Thruster/Shield isinstance → ability | ship_stats.py |
| Physics thrust → ability helper | ship_physics.py:19 |
