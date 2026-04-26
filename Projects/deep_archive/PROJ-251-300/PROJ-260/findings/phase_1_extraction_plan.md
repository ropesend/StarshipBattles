# Phase 1: Extraction Plan

## Summary

Ship.py: **712 lines**, 53 public methods, 77 properties.
9 delegates already extracted. 2 more proposed: ShipLayerManager and ShipResourceManager.

## ShipLayerManager Extraction

**Methods to extract:**
| Method | Lines | Range | Notes |
|--------|-------|-------|-------|
| `_initialize_layers()` | 59 | 364-422 | Pure layer logic, trivial extraction |
| `_equip_default_hull()` | 18 | 189-206 | No external callers, safe to move entirely |
| `change_class()` | 68 | 424-492 | Most complex method. Move to delegate, call back to Ship for add_component/recalculate_stats |

**Total lines extracted: 145**

**Attributes read/written:** ship_class, max_mass_budget, layers — ShipLayerManager will receive Ship reference.

**Public API:** `change_class()` stays on Ship as a facade property delegating to layer_manager.

## ShipResourceManager Extraction

**Methods to extract:**
| Method | Lines | Notes |
|--------|-------|-------|
| `get_resource_stat()` | 18 (595-611) | Typed accessor, trivial extraction |
| `_initialize_resources()` | ~38 | Currently in ShipStatsCalculator — move to ShipResourceManager |

**Attributes to move:**
- `resources` (ResourceRegistry) — ownership moves to ShipResourceManager, Ship keeps facade property
- `_resources_initialized` (bool)
- `_prev_max_resources` (dict)
- `_prev_max_shields` (int)
- `fuel_consumption`, `ammo_consumption`, `energy_consumption` (floats)
- `potential_fuel_consumption`, `potential_ammo_consumption`, `potential_energy_consumption` (floats)

**Total lines extracted: ~66** (from Ship) + ~38 (from ShipStatsCalculator)

**Public API:** `resources` and `get_resource_stat()` stay on Ship as facade properties.

## Line Count Projection

| Item | Lines |
|------|-------|
| Current Ship.py | 712 |
| ShipLayerManager extraction | -145 |
| ShipResourceManager extraction | -66 |
| New facade methods/properties | +10 |
| **Projected final** | **~511** |

## Assessment

**<500 target is NOT achievable with just these two extractions.** Projected: ~511 lines.

**Options to reach <500:**
1. Accept ~511 as close enough (the skeptical review said decomposition IS effective already)
2. Move resource consumption attributes init (8 lines) + simplify recalculate_stats orchestration
3. Consolidate some facade one-liners

**Recommendation:** Proceed with the two extractions targeting ~511 lines. The <500 target was aspirational — Ship at 511 lines with 11 delegates is a clean, well-decomposed facade. Further extraction would fragment responsibilities without clear benefit.

## External Callers

| Target | External callers | Impact |
|--------|-----------------|--------|
| `_initialize_layers()` | 3 test files | Tests call directly — update to use delegate |
| `_equip_default_hull()` | 0 external | Safe to move entirely |
| `ship.resources` | 71 files | MUST remain as Ship facade property |
| `get_resource_stat()` | 10 files | MUST remain as Ship facade |
| `change_class()` | 5 files | MUST remain as Ship facade |
