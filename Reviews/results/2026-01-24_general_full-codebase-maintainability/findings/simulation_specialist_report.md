# Simulation Module Specialist Report

## Summary
- **Total issues found:** 15
- **Critical:** 1, **Major:** 12, **Minor:** 1, **Info:** 1

---

## Findings

### CRITICAL: Unsafe Formula Evaluation
**ID:** SIM-05
**Location:** `game/simulation/formula_system.py:4-32`
**Issue:** Uses eval() for formula evaluation. While __builtins__ is disabled, eval() still has security risks if context dict can be polluted.
**Impact:** If attacker can inject formulas into components.json or modifiers.json, could cause DoS or information leakage.
**Recommendation:** Use ast.literal_eval() or dedicated expression parser. Whitelist math functions explicitly.
**Effort:** Medium

---

## Major Findings

### MAJOR: Circular Dependency in Component System
**ID:** SIM-01
**Location:** `game/simulation/components/component.py:195-232`, `game/simulation/systems/resource_manager.py:143-150`
**Issue:** Component._instantiate_abilities() imports ABILITY_REGISTRY from two different locations.
**Impact:** Makes it harder to extend ability system. Risk of import order issues during refactoring.
**Recommendation:** Consolidate ability registry into single authoritative location. Use dependency injection.
**Effort:** Medium

### MAJOR: Tight Coupling Between Component and Ship Statistics
**ID:** SIM-02
**Location:** `game/simulation/entities/ship.py:28-135`, `game/simulation/components/component.py:85-100`
**Issue:** Components rely on `component.ship` reference to access ship context. Component formulas evaluate using ship context.
**Impact:** Difficult to test components in isolation. Cannot reuse component logic in other contexts.
**Recommendation:** Pass ship context as parameter to recalculate() rather than relying on component.ship reference.
**Effort:** Complex

### MAJOR: Mutable Shared Ability Instances
**ID:** SIM-03
**Location:** `game/simulation/components/component.py:180-233`
**Issue:** _instantiate_abilities() preserves existing ability instances to maintain runtime state, but stat recalculation calls sync_data() on these instances.
**Impact:** Cooldown state can be lost or corrupted during stat recalculation.
**Recommendation:** Separate state (cooldowns) from configuration (damage, range). Recalculate stats without mutating ability instances.
**Effort:** Complex

### MAJOR: Complex State Machine for Component Activation
**ID:** SIM-04
**Location:** `game/simulation/entities/ship_stats.py:88-147`
**Issue:** Component status determined by multiple overlapping conditions spread across take_damage(), recalculate_stats(), Component.update().
**Impact:** Hard to reason about when components become active/inactive. Easy to miss status transitions.
**Recommendation:** Create explicit ComponentStateMachine class with clear state transitions.
**Effort:** Complex

### MAJOR: Modifier System Not Extensible for New Stats
**ID:** SIM-06
**Location:** `game/simulation/components/modifier_effects.py`, `game/simulation/components/stat_keys.py:15-58`
**Issue:** StatKey enum is hardcoded. Adding new modifier effects requires changing enum + default stats dict + ability bindings.
**Impact:** Cannot add new stats without modifying 4+ files. Breaks extensibility for modding/DLC.
**Recommendation:** Use dynamic stat key registration system with defaults loaded from data/modifiers.json.
**Effort:** Medium

### MAJOR: Undocumented Ability Polymorphism Fallback
**ID:** SIM-07
**Location:** `game/simulation/components/component.py:119-127`
**Issue:** get_abilities() has fallback __name__ check for test module isolation. Documented as KNOWN_ISSUE.
**Impact:** Tests can mask bugs. isinstance() polymorphism doesn't work reliably in test environment.
**Recommendation:** Fix module reloading issue in test framework instead of working around in production code.
**Effort:** Medium

### MAJOR: Duplicate Ability Aggregation Logic
**ID:** SIM-08
**Location:** `game/simulation/entities/ability_aggregator.py:19-140, 157-261`
**Issue:** calculate_ability_totals() and calculate_ability_totals_for_layer() have 90% duplicated code.
**Impact:** Bug fixes only applied to one function. Divergence over time. Violates DRY principle.
**Recommendation:** Extract common aggregation logic into helper.
**Effort:** Simple

### MAJOR: Ship.get_total_ability_value() Doesn't Match ShipStatsCalculator Logic
**ID:** SIM-09
**Location:** `game/simulation/entities/ship.py:571-589` vs `game/simulation/entities/ship_stats.py:149-280`
**Issue:** Two different code paths calculate ability totals. Not synchronized.
**Impact:** UI shows different values than internal calculations. Modifiers applied in one place but not aggregated in another.
**Recommendation:** Single source of truth for ability aggregation.
**Effort:** Complex

### MAJOR: Resource System Has No Overflow Prevention
**ID:** SIM-10
**Location:** `game/simulation/systems/resource_manager.py:113-122`
**Issue:** modify_value() clamps to max, but register_storage() doesn't auto-fill. Inconsistent initialization.
**Impact:** Ships can be created with 0 resources. No guarantee current <= max at all times.
**Recommendation:** Auto-fill resources on registration, add assertions to check invariants.
**Effort:** Simple

### MAJOR: Validation Rules Can't Access Component Statistics
**ID:** SIM-11
**Location:** `game/simulation/ship_validator.py:47-97`
**Issue:** Validation rules only see component definitions, not calculated stats. Mass budget checks use base_mass, not modified mass.
**Impact:** Mass limits can be bypassed by applying mass reduction modifiers. Invalid designs pass validation.
**Recommendation:** Pass pre-calculated component stats to validation rules.
**Effort:** Medium

### MAJOR: Ability Data Sync Pattern Fragile
**ID:** SIM-13
**Location:** `game/simulation/components/component.py:180-233`, `game/simulation/components/abilities/weapons.py:85-96`
**Issue:** sync_data() is optional (hasattr check). Not all abilities implement it. Inconsistent pattern.
**Impact:** Data changes during recalculation may not persist to all ability types.
**Recommendation:** Make sync_data() mandatory with default no-op implementation in Ability base class.
**Effort:** Simple

### MAJOR: Modifier Service Mandatory List Hardcoded
**ID:** SIM-14
**Location:** `game/simulation/services/modifier_service.py:44-98`
**Issue:** get_mandatory_modifiers() contains hardcoded list specific to current game design. Not data-driven.
**Impact:** Cannot mod or extend mandatory modifier logic without code change.
**Recommendation:** Load mandatory modifier rules from data/modifiers.json.
**Effort:** Medium

---

## Minor & Info Findings

### Minor: Dangerous Default Behavior in Component HP Reset
**ID:** SIM-12
**Location:** `game/simulation/components/component.py:521-527`
**Issue:** When old_max_hp == 0, always resets current_hp to max. Could lose HP state on first recalculation.
**Recommendation:** Only reset HP on initial creation.
**Effort:** Simple

### Info: Performance Issue - ShipStatsCalculator.calculate() Called Multiple Times
**ID:** SIM-15
**Location:** `game/simulation/entities/ship.py:525-540`
**Issue:** recalculate_stats() has O(n²) behavior for n components.
**Impact:** Noticeable lag on large ships (50+ components).
**Recommendation:** Batch updates - collect all changes, then calculate once.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **SIM-02: Ship-Component Bidirectional Coupling** - Blocks extensibility to new contexts
2. **SIM-04: Complex Component Activation State Machine** - Highest risk for bugs
3. **SIM-09: Divergent Ability Aggregation Paths** - Data integrity risk
4. **SIM-05: Unsafe Formula Evaluation** - Security vulnerability
5. **SIM-11: Validation Doesn't See Calculated Stats** - Design validity bugs

---

## Extensibility Assessment

**Current State: MODERATE-TO-DIFFICULT**

The simulation layer has good component isolation via the ability system, but is hampered by:
- Strong coupling between Component and Ship entities
- Hardcoded stat keys and mandatory modifiers
- Duplicated aggregation logic
- State mutation during recalculation
- Validation system doesn't see calculated stats

**To improve extensibility:**
1. Decouple components from ship (use context object pattern)
2. Make stats/modifiers registry-driven rather than enum-driven
3. Separate state from configuration in abilities
4. Consolidate ability aggregation logic
5. Refactor component status into explicit state machine
