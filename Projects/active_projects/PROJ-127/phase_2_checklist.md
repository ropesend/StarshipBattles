# Phase 2: Simulation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-127 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Simulation module (8 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 2.1: DUP-SIM-001 - Serialization to_dict/from_dict Pattern [Medium]
**File:** `game/simulation/battle_state.py`
**Resolution:** ACCEPTABLE

- [x] Investigate the issue at the specified location
- [N/A] Write test to verify the fix
- [N/A] Implement the fix
- [N/A] Verify: tests pass, no regressions

**Notes:** Dataclass to_dict/from_dict is necessary boilerplate for serialization. Each class (ComponentState, ShipState, ProjectileState, BattleState, BattleResults) has unique fields with specific serialization needs. Alternative solutions (dataclasses-json, custom mixin) add dependencies or complexity. Pattern is consistent and readable.

### Task 2.2: DUP-SIM-002 - Resource Ability Classes Share Identical [Simple]
**File:** `game/simulation/components/abilities/resources.py`
**Resolution:** ACCEPTABLE

- [x] Investigate the issue at the specified location
- [N/A] Write test to verify the fix
- [N/A] Implement the fix
- [N/A] Verify: tests pass, no regressions

**Notes:** ResourceConsumption, ResourceStorage, and ResourceGeneration are semantically different abilities. They have different stat bindings, different logic (consume vs. store vs. generate), different update() behaviors, and different UI display formats. The structural similarity exists because they're all resource-related, but each handles a fundamentally different concept.

### Task 2.3: DUP-SIM-003 - Team Iteration Pattern Duplicated in Bat [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Resolution:** ACCEPTABLE

- [x] Investigate the issue at the specified location
- [N/A] Write test to verify the fix
- [N/A] Implement the fix
- [N/A] Verify: tests pass, no regressions

**Notes:** Team iteration pattern (`sum(1 for s in self.ships if s.team_id == X and s.is_alive...)`) is a simple list comprehension. Each use has slightly different conditions (e.g., derelict check). Extracting would add complexity for minimal gain.

### Task 2.4: DUP-SIM-004 - Vector2 Conversion Pattern in Projectile [Simple]
**File:** `game/simulation/projectile_manager.py`
**Resolution:** ACCEPTABLE

- [x] Investigate the issue at the specified location
- [N/A] Write test to verify the fix
- [N/A] Implement the fix
- [N/A] Verify: tests pass, no regressions

**Notes:** Vector2 conversions (`Vector2(obj.x, obj.y)`) are necessary defensive code to handle pygame Vector2 vs game Vector2 interoperability. Tests may use pygame's Vector2, and the code needs to work with both implementations.

### Task 2.5: DUP-SIM-005 - get_ui_rows Color Mapping Pattern in Res [Simple]
**File:** `game/simulation/components/abilities/resources.py`
**Resolution:** ACCEPTABLE

- [x] Investigate the issue at the specified location
- [N/A] Write test to verify the fix
- [N/A] Implement the fix
- [N/A] Verify: tests pass, no regressions

**Notes:** Color mapping exists in resources.py (maps resource types to colors) and weapons.py (uses colors for specific stat display). Colors are used semantically in different contexts. Centralizing to a constant file is low priority and carries risk of breaking UI consistency.

### Task 2.6: DUP-SIM-006 - ship_id_map Pattern Repeated in RetreatM [Simple]
**File:** `game/simulation/managers/retreat_manager.py`
**Resolution:** ACCEPTABLE

- [x] Investigate the issue at the specified location
- [N/A] Write test to verify the fix
- [N/A] Implement the fix
- [N/A] Verify: tests pass, no regressions

**Notes:** ship_id_map is passed around to several methods for maintaining identity between Python object IDs and persistent string IDs. This is necessary for serialization/deserialization - each method needs the map to translate between live objects and stored IDs.

### Task 2.7: DUP-SIM-007 - Validation Pattern in modifier_schema.py [Medium]
**File:** `game/simulation/components/modifier_schema.py`
**Resolution:** ACCEPTABLE

- [x] Investigate the issue at the specified location
- [N/A] Write test to verify the fix
- [N/A] Implement the fix
- [N/A] Verify: tests pass, no regressions

**Notes:** Validation functions (validate_effect_v2, validate_param_v2, validate_restrictions_v2, validate_modifier_v2) share a common pattern (check dict, check required fields, validate types) because they all do schema validation. Each validator has different requirements and different field structures. Extracting a shared helper would reduce readability without meaningful benefit.

### Task 2.8: DUP-SIM-008 - Natural Similarity in Dataclass State Cl [N]
**File:** `game/simulation/battle_state.py`
**Resolution:** INFO - acknowledged

- [x] Investigate the issue at the specified location
- [N/A] Write test to verify the fix
- [N/A] Implement the fix
- [N/A] Verify: tests pass, no regressions

**Notes:** Finding was marked INFO severity - observation only. Dataclass state classes (ComponentState, ShipState, ProjectileState, BattleState, BattleResults) naturally have similar structures because they represent similar concepts (serializable state). No action required.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
