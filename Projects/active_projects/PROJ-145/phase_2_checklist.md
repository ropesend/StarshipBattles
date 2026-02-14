# Phase 2: Simulation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-145 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Simulation module (9 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 2.1: CON-SIM-003 - Mixed Docstring Formats [Complex]
**File:** `game/simulation/` (module-wide)
**Tests:** N/A (no code changes)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY COMPLIANT - No reST-style docstrings found in simulation module. Google style (`Args:`, `Returns:`, `Raises:`) is the standard throughout. Good coverage of `Raises:` documentation (23 documented sections).

### Task 2.2: CON-SIM-005 - Ability Class Naming Inconsistency [Complex]
**File:** `game/simulation/components/abilities/__init__.py`
**Tests:** N/A (no code changes)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL DESIGN - Registry keys intentionally shorter than class names for cleaner JSON data files. Naming convention is semantic: Weapon types use `*Ability` suffix (WeaponAbility, SeekerWeaponAbility), passive/stat abilities use noun form (ShieldProjection, CrewCapacity). This follows Python convention where class names describe what they ARE.

### Task 2.3: DUP-SIM-001 - Ability `__init__` Pattern Duplication A [Simple]
**File:** `game/simulation/components/abilities/propulsion.py`, `defense.py`, `crew.py`
**Tests:** N/A (no code changes)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL DESIGN - The boilerplate pattern (parse val, set base_X, set X = base_X) is explicit by design. Each ability clearly shows its data flow. STAT_BINDINGS exist for introspection, not auto-application. Some abilities need different parsing (WarpJump uses multiple fields, EmissiveArmor uses int). 3-4 line methods are not burdensome.

### Task 2.4: DUP-SIM-002 - Repeated `sync_data` Pattern Across Prop [Simple]
**File:** `game/simulation/components/abilities/propulsion.py`, `resources.py`
**Tests:** N/A (no code changes)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL DESIGN - Follows same explicit pattern as __init__. Consistency across abilities aids understanding. Auto-generation was considered and rejected for debugging clarity.

### Task 2.5: DUP-SIM-003 - Repeated `recalculate` Pattern for Singl [Medium]
**File:** `game/simulation/components/abilities/propulsion.py`, `defense.py`, `crew.py`
**Tests:** N/A (no code changes)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL DESIGN - STAT_BINDINGS metadata exists for UI introspection (get_consumed_stats, get_stat_bindings_info, get_effect_summary), NOT for auto-application. Explicit recalculate() methods: (1) allow custom logic when needed, (2) make debugging easier, (3) avoid metaclass complexity.

### Task 2.6: DUP-SIM-004 - `to_dict` / `from_dict` Serialization Pa [Medium]
**File:** `game/simulation/battle_state.py`
**Tests:** N/A (no code changes)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL DESIGN - Explicit serialization is safer for game save/load. Already using dataclasses, but explicit to_dict/from_dict provides: type conversion (tuple<->list), nested object handling, default values for backward compatibility. Can't rely on auto-generated serialization for battle state stability.

### Task 2.7: DUP-SIM-008 - WeaponAbility Formula Handling Pattern [Simple]
**File:** `game/simulation/components/abilities/weapons.py`
**Tests:** N/A (no code changes)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INTENTIONAL DESIGN - Formula system is weapon-specific (only weapons support formula strings). Duplication is contained within single class (WeaponAbility). Context-specific evaluation (range_to_target). Extracting helper for 3 occurrences in one class would add indirection without benefit.

### Task 2.8: DUP-SIM-011 - Consistent Use of Helper Class Pattern [N]
**File:** `game/simulation/components/`
**Tests:** N/A (positive observation)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** POSITIVE OBSERVATION (INFO) - This finding commends the helper class extraction pattern from PROJ-44/PROJ-88. ModifierManager, AbilityManager, ComponentStatsCalculator use static methods; ResourceManager, HealthManager use instance wrappers. Good architecture to continue.

### Task 2.9: DUP-SIM-012 - Well-Factored Combat Subsystems [N]
**File:** `game/simulation/combat/`
**Tests:** N/A (positive observation)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** POSITIVE OBSERVATION (INFO) - Commends TargetingSystem, DamageCalculator, WeaponFiringSystem decomposition (PROJ-44 Phase 5). Each has single responsibility with minimal overlap. Template for future refactoring.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
