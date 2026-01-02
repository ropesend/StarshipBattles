# AI System Legacy Audit

## Overview
Files reviewed:
- `c:\Dev\Starship Battles\ai.py`
- `c:\Dev\Starship Battles\ai_behaviors.py`

## Findings

### 1. Legacy Weapon Detection in TargetEvaluator
- **File**: `c:\Dev\Starship Battles\ai.py`
- **Line**: 188
- **Code**: 
  ```python
  has_wpns = any(hasattr(c, 'damage') for layer in getattr(candidate, 'layers', {}).values() 
                     for c in layer.get('components', []))
  ```
- **Impact**: AI determines if a target is armed by checking for a legacy `damage` attribute. If the `damage` shim is removed from components, this check will fail (return False), causing the AI to potentially ignore armed threats or fail to prioritize armed targets (via 'has_weapons' rule).
- **Fix Priority**: **HIGH**
- **Recommended Fix**: Replace with `c.has_ability('WeaponAbility')`.

### 2. Direct Access to Legacy Weapon Attributes (Range)
- **File**: `c:\Dev\Starship Battles\ai.py`
- **Line**: 372
- **Code**: `if dist > comp.range: continue`
- **Impact**: Checks `comp.range` directly inside `_stat_is_in_pdc_arc`. If the `range` property shim is removed from the Component class, this will raise an AttributeError, crashing the AI during PDC evaluations.
- **Fix Priority**: **MEDIUM**
- **Recommended Fix**: Access range via the ability: `comp.get_ability('WeaponAbility').range`.

### 3. Direct Access to Legacy Weapon Attributes (Firing Arc)
- **File**: `c:\Dev\Starship Battles\ai.py`
- **Line**: 383
- **Code**: `if abs(diff) <= (comp.firing_arc / 2):`
- **Impact**: Checks `comp.firing_arc`. Similar to range, this relies on a legacy shim. Removal of the shim will crash the AI.
- **Fix Priority**: **MEDIUM**
- **Recommended Fix**: Access firing arc via the ability: `comp.get_ability('WeaponAbility').firing_arc` (or equivalent data dictionary lookup).

### 4. Legacy Component Import
- **File**: `c:\Dev\Starship Battles\ai.py`
- **Line**: 365
- **Code**: `from components import Weapon`
- **Impact**: Imports the legacy `Weapon` subclass. While not immediately breaking, it encourages legacy type checking and creates unnecessary dependencies on the legacy class structure.
- **Fix Priority**: **LOW**
- **Recommended Fix**: Remove import. The code at line 370 uses `has_ability` correctly, so strictly speaking this import might be unused or easily removable.

## Summary
`ai_behaviors.py` appears to be clean of legacy component patterns, relying on `AIController` and standard `Ship` properties (like `ship.max_weapon_range`) which have already been refactored. The primary issues are localized within `ai.py` in the `TargetEvaluator` and `_stat_is_in_pdc_arc` static methods.
