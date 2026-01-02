# Audit Report: Battle UI & Rendering

## Executive Summary
This audit covers `battle_ui.py`, `battle_panels.py`, `rendering.py`, and `battle_setup.py`. The focus was to identify legacy component patterns, specifically `isinstance` checks, direct attribute access, and type-based logic.

**Status**:
- `battle_ui.py`: **Changes Required** (Legacy attribute access in debug overlay).
- `rendering.py`: **Minor Fix Required** (Legacy `type_str` check).
- `battle_panels.py`: **Clean** (Correctly uses `has_ability` for logic, generic HP bars for others).
- `battle_setup.py`: **Clean** (No component-level logic found).

---

## Detailed Findings

### 1. Direct Attribute Access (Debug Overlay)
The debug overlay tracks weapon ranges and firing arcs using legacy `comp.range` and `comp.firing_arc` attributes, which should now be accessed via `WeaponAbility`.

*   **File**: `c:\Dev\Starship Battles\battle_ui.py`
*   **Line**: 135
*   **Code**: `if comp.range > max_range:`
*   **Visual Impact**: Debug overlay range circles will be incorrect (0) or crash if legacy attributes are removed.
*   **Fix Recommendation**:
    ```python
    weapon_ability = comp.get_ability('WeaponAbility')
    if weapon_ability.range > max_range:
        # ...
    ```

*   **File**: `c:\Dev\Starship Battles\battle_ui.py`
*   **Line**: 136
*   **Code**: `max_range = comp.range`
*   **Fix Recommendation**: `max_range = weapon_ability.range`

*   **File**: `c:\Dev\Starship Battles\battle_ui.py`
*   **Line**: 161
*   **Code**: `arc = comp.firing_arc`
*   **Visual Impact**: Debug overlay firing arc cone will be missing or incorrect.
*   **Fix Recommendation**: `arc = comp.get_ability('WeaponAbility').firing_arc`

*   **File**: `c:\Dev\Starship Battles\battle_ui.py`
*   **Line**: 162
*   **Code**: `rng = comp.range * camera.zoom`
*   **Fix Recommendation**: `rng = comp.get_ability('WeaponAbility').range * camera.zoom`

### 2. Type-Based Visual Selection
The renderer uses a legacy `type_str` check to assign a gray color to armor components. While functional, this relies on the legacy `type_str` string.

*   **File**: `c:\Dev\Starship Battles\rendering.py`
*   **Line**: 123
*   **Code**: `elif comp.type_str == 'Armor': color = (100, 100, 100)`
*   **Visual Impact**: Armor components draw as grey dots. If `type_str` is deprecated, this logic fails.
*   **Fix Recommendation**:
    - If `ArmorAbility` exists: `elif comp.has_ability('ArmorAbility'): ...`
    - Or if using tags: `elif 'armor' in comp.tags: ...`
    - Alternatively (low priority): Leave as is if `type_str` remains as a descriptive fallback.

### 3. Other Observations

*   **Battle Panels (`battle_panels.py`)**:
    *   Correctly uses `comp.has_ability('WeaponAbility')` (Lines 240, 303) to distinguish weapons from other components.
    *   No explicit `isinstance` checks found for `Engine` or `Shield`.
    *   Engine/Shield status displays seem to have been replaced by a generic component list that shows HP/Status colors. This is "Clean" regarding legacy crashes, though potentially less informative than a dedicated UI (which is a design choice, not a legacy bug).

*   **Battle Setup (`battle_setup.py`)**:
    *   Operates on `Ship` objects and JSON data structures.
    *   No component-level inspection or legacy type checks found.

## Summary Checklist status

1.  `isinstance(comp, Weapon)` for weapon status display: **CLEAN** (Referenced `has_ability`).
2.  `isinstance(comp, Engine/Shield)` for status panels: **CLEAN** (Removed/Replaced by generic loop).
3.  Direct attribute access for UI values: **FOUND** (`battle_ui.py`).
4.  Color/visual selection based on component type: **FOUND** (`rendering.py`).
5.  Weapon tooltips reading legacy attributes: **NOT FOUND** (No tooltips implemented in reviewed files).
6.  Debug overlays using isinstance checks: **CLEAN** (Uses `has_ability`), but **FOUND** legacy attribute access within the block.
7.  Battle setup using legacy component types: **CLEAN**.
