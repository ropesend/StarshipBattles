# QA Lead Report: Hull Layer Migration

**Date:** 2026-01-08
**Focus:** Verification of Hull Layer Migration (LayerType.CORE -> LayerType.HULL)

## 1. Analysis of Existing Tests (`test_ship_core.py`)

The existing validtion suite `test_ship_core.py` was analyzed against the proposed `LayerType.HULL` architecture.

### Impact Assessment
| Test Class | Test Method | Status | Notes |
| :--- | :--- | :--- | :--- |
| `TestHullAutoEquip` | `test_hull_auto_equip` | **WILL FAIL** | Currently asserts Hull is in `LayerType.CORE`. Must be updated to assert Hull is in `LayerType.HULL`. |
| `TestMassAggregation` | `test_mass_from_components` | **VERIFY** | Should pass if `ship.layers.values()` iteration includes the new layer. Needs verification that base_mass remains 0. |
| `TestHPAggregation` | `test_hp_from_components` | **VERIFY** | Should pass if `ship.layers.values()` includes new layer. |
| `TestDerelictStatus` | `test_ship_not_derelict...` | **PASS** | Bridge remains in CORE. Independent of Hull location. |

### Required Updates (Refactoring)
- **Modify `test_hull_auto_equip`**:
  - Change lookup: `core_comps` -> `hull_comps = ship.layers[LayerType.HULL]['components']`.
  - Assert `len(hull_comps) == 1`.
  - Assert `LayerType.CORE` does **NOT** contain the Hull ID.

## 2. Requirements: `test_hull_layer.py`

A new test file `tests/unit/entities/test_hull_layer.py` is required to specifically target the new architecture.

### TC-3.2.6: Hull Layer Initialization
- **Setup**: Create Ship (default class).
- **Action**: Inspect `ship.layers`.
- **Assertions**:
  - `LayerType.HULL` key exists in `ship.layers`.
  - Hull component is present in `LayerType.HULL`.
  - Hull component is **ABSENT** from `LayerType.CORE`.
  - `ship.layers[LayerType.HULL]['search_radius']` (or equivalent) logic places it physically innermost (if applicable).

### TC-3.2.7: Layer Ordinality & Logic
- **Setup**: Ship with Hull (HULL), Bridge (CORE), Armor (OUTER).
- **Action**: Check `ship.layer_order` (or iteration order of keys).
- **Assertions**:
  - Ensure iteration logic respects `HULL` as the innermost layer (essential for damage calculation requiring penetration).
  - Verify `HULL` layer index/enum value logic matches "Innermost" intent (e.g. 0).

### TC-3.2.8: Persistence & Duplication Prevention
- **Setup**: `ship.to_dict()` then `Ship.from_dict()`.
- **Action**: Inspect loaded ship.
- **Assertions**:
  - Loaded ship has exactly **one** Hull component.
  - No "ghost" hull components left over in `CORE` layer from legacy save data (if migration logic exists) or fresh dict.

## 3. Regression Risks & Regressions Checklist

### High Risk Areas
1.  **UI Structure List**: The `LayerPanel` or `StructureList` validation often iterates layers. If it simply iterates `LayerType` enum or `ship.layers`, the Hull might reappear in the UI, violating the "Read Only / Invisible" requirement.
2.  **Damage Distribution**: If `take_damage` logic iterates layers hardcoded (Outer -> Core), it might miss the Hull layer entirely, or crash if it encounters `LayerType.HULL` and doesn't have a handler for it.

### Verification Steps (Manual/Integration)
- [ ] **Data Model**: Verify `Ship.base_mass` remains `0.0` and strict mass comes from `LayerType.HULL` component.
- [ ] **Builder UI**: Confirm Hull is NOT selectable/deletable in the standard "Structure" list.
- [ ] **Gameplay**: Verify ship destroyed when CORE is dead (as per plan), even if Hull layer remains "intact" (0 HP concept).

## 4. Final Recommendation
Proceed with `test_hull_layer.py` creation **before** implementation to TDD the layer existence. Update `test_ship_core.py` immediately after implementation to fix the broken regression check.
