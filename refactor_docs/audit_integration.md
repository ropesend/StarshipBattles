# Audit: Main Entry Points and Integration

## Executive Summary
The main entry point `main.py` and the active builder `builder_gui.py` are largely modernized, but `builder.py` exists as a completely legacy artifact that should be removed. `builder_gui.py` retains some legacy imports and string-based type checks that should be cleaned up.

## Detailed Findings

### 1. Game Initialization & Main Loop
**File:** `c:\Dev\Starship Battles\main.py`
- **Status:** PASS
- **Notes:** `main.py` correctly uses `load_components` and `initialize_ship_data`. It delegates scene creation to modernized classes (`BuilderSceneGUI`, `BattleScene`). No legacy `isinstance` checks found in the main loop. Initialization seems consistent with the V2 architecture.

### 2. Legacy Builder Artifact (`builder.py`)
**File:** `c:\Dev\Starship Battles\builder.py`
- **Line:** Entire File
- **Code:** `class BuilderScene:` (and whole file)
- **Runtime Impact:** None (Dead Code). This file is **not imported** by `main.py` or any other module (verified via grep). `main.py` uses `builder_gui.py`.
- **Legacy Patterns:**
    - Uses `tkinter` directly for dialogs (blocking).
    - Hardcoded legacy component subclass imports (`Engine`, `Thruster`, etc.).
    - Legacy `comp.type_str` logic.
- **Fix Priority:** **CRITICAL** (Delete file to avoid confusion).

### 3. Builder GUI Legacy Imports
**File:** `c:\Dev\Starship Battles\builder_gui.py`
- **Line:** 18-22
- **Code:**
```python
from components import (
    get_all_components, MODIFIER_REGISTRY, Bridge, Weapon, 
    BeamWeapon, ProjectileWeapon, SeekerWeapon, Engine, Thruster, Armor, Tank, Generator,
    CrewQuarters, LifeSupport
)
```
- **Runtime Impact:** Low, but implies coupling to legacy class structure. If these classes are removed/renamed, this file breaks.
- **Legacy Patterns:** Unnecessary imports of `BeamWeapon`, `ProjectileWeapon`, `SeekerWeapon`, `Engine`, `Thruster` etc.
- **Fix Priority:** **HIGH** (Remove unused imports).

### 4. Component String Typing in Builder
**File:** `c:\Dev\Starship Battles\builder_gui.py`
- **Line:** 417, 746
- **Code:**
```python
if 'allow_types' in mod_def.restrictions and c.type_str not in mod_def.restrictions['allow_types']:
    allow = False
```
- **Runtime Impact:** Functional relying on `type_str`.
- **Legacy Patterns:** Relies on `type_str` property returning legacy strings (e.g. "Engine").
- **Analysis:** This is an Acceptable Shim for now, as `Component.type_str` exists. However, data files must ensure `allow_types` lists match the mocked/actual `type_str`.
- **Fix Priority:** MEDIUM (Ensure `type_str` aligns with data).

### 5. Formation Editor
**File:** `c:\Dev\Starship Battles\formation_editor.py`
- **Status:** PASS
- **Notes:** The formation editor operates on abstract points ("arrows") and does not interact with Component classes or legacy Engine/Thruster logic. It is purely a coordinate editor.

## Recommendations
1. **DELETE** `c:\Dev\Starship Battles\builder.py` immediately.
2. **CLEANUP** `c:\Dev\Starship Battles\builder_gui.py` imports to remove unused legacy subclasses.
3. **VERIFY** all `c.type_str` usages in `builder_gui.py` align with the new Component Ability System (e.g. if an Engine is just a Component with `thrust` ability, does it still report `type_str="Engine"`? Yes, via the `type` field in JSON/Legacy Shim).
