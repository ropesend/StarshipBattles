# Module Review: game/simulation/

**Module Specialist:** MOD-SIM
**Review Date:** 2026-02-23
**Scope:** Internal architecture, component system, combat calculations, battle engine

---

## Summary

**Total Findings:** 18
**Severity Distribution:**
- Critical: 3
- Major: 7
- Minor: 6
- Info: 2

**Overall Module Health Rating: 7.5/10**

The simulation module demonstrates solid architectural foundations with clear layer separation and well-organized subsystems. The recent god class decomposition (PROJ-44, PROJ-88) has significantly improved modularity. However, several edge cases in damage calculations, physics formulas, and ability aggregation present risks for correctness issues.

---

## Findings

### MOD-SIM-001: Boolean Type Confusion in Ability Aggregation
**Location:** `game/simulation/entities/ability_aggregator.py:40-45`
**Severity:** Critical
**Deliberate:** Likely Accidental

**Description:**
The `_aggregate_ability_groups` function filters numeric values with `isinstance(v, (int, float)) and not isinstance(v, bool)`, but this check relies on evaluation order. In Python, `bool` is a subclass of `int`, so `isinstance(True, int)` returns `True`. The explicit `not isinstance(v, bool)` only works because it's evaluated second.

If the boolean check is removed or reordered, `True/False` values would be treated as 1/0 in numeric aggregations, causing silent calculation errors.

**Impact:**
- Marker abilities (CommandAndControl, Armor) could be incorrectly summed as 1.0 instead of treated as boolean flags
- Silent failures in ability totals for mixed boolean/numeric abilities

**Recommendation:**
Use explicit type checking: `nums = [v for v in values if type(v) in (int, float)]`

---

### MOD-SIM-002: Potential Division by Zero in Projectile Guidance
**Location:** `game/simulation/entities/projectile.py:99`
**Severity:** Major
**Deliberate:** Accidental (missing guard)

**Description:**
The projectile guidance system's lead calculation has a zero-division guard at line 104, but the subsequent calculation at line 109 divides by `dv_sq` without checking if it's near zero (epsilon comparison). For very slow relative velocities, this could cause numerical instability.

**Recommendation:**
Add epsilon comparison: `if abs(dv_sq) < 1e-6: # Handle near-zero case`

---

### MOD-SIM-003: Unchecked Formula Evaluation in Weapon Damage
**Location:** `game/simulation/components/abilities/weapons.py:189-206`
**Severity:** Major
**Deliberate:** Deliberate (but risky)

**Description:**
The `get_damage()` method evaluates damage formulas with `range_to_target` as context, but there's no validation that the formula actually uses this variable. If a formula has syntax errors, it falls back to the static damage value via `safe_evaluate_math_formula`, but the error is only logged, not surfaced.

**Recommendation:**
Add formula validation during component instantiation — fail loudly during loading, not at runtime.

---

### MOD-SIM-004: Damage Pipeline Order Not Enforced
**Location:** `game/simulation/combat/damage_calculator.py:29-91`
**Severity:** Major
**Deliberate:** Deliberate

**Description:**
The damage pipeline (EmissiveArmor -> Crystalline -> Shields -> Hull) is implemented as sequential if-statements with only a comment documenting the order. No architectural enforcement prevents accidental reordering during refactoring.

**Recommendation:**
Extract pipeline stages into an ordered list or strategy pattern for self-documenting enforcement.

---

### MOD-SIM-005: Mass Calculation Ignores Dead Components
**Location:** `game/simulation/entities/ship_stats.py:83-86`
**Severity:** Major
**Deliberate:** Deliberate (but questionable)

**Description:**
Mass calculation sums all components regardless of `current_hp`. Comment says "Mass never changes due to damage/status in this model, dead weight remains". Ships don't get lighter when components are destroyed, so physics calculations (acceleration, turn speed) don't improve as ship loses mass.

**Assessment:** Likely deliberate for balance (prevents destroyed ships from becoming super-agile).

**Recommendation:**
Document as explicit game design choice.

---

### MOD-SIM-006: Projectile Removal Mark-and-Sweep vs List Comprehension
**Location:** `game/simulation/projectile_manager.py:68-74`
**Severity:** Minor
**Deliberate:** Deliberate (optimization)

**Description:**
Uses mark-and-sweep with in-place compaction instead of `self.projectiles = [p for p in self.projectiles if p.is_alive]`. Trades readability for marginal performance gain.

**Recommendation:**
Add comment explaining the optimization rationale.

---

### MOD-SIM-007: Missing Max Capacity Guards in Resource Initialization
**Location:** `game/simulation/entities/ship_stats.py:494-536`
**Severity:** Minor
**Deliberate:** Deliberate (handled by registry)

**Description:**
`_initialize_resources()` adds resource capacity deltas without explicit clamping. Safety depends on whether ResourceRegistry.modify_value() clamps internally.

**Recommendation:**
Verify ResourceRegistry has internal clamping, or add explicit guards.

---

### MOD-SIM-008: Ability Index Staleness Risk
**Location:** `game/simulation/components/component.py:156, 290-300`
**Severity:** Minor
**Deliberate:** Deliberate (performance optimization)

**Description:**
The ability index (`_ability_index`) is built during `_instantiate_abilities()` but has no invalidation mechanism. If abilities change at runtime, the index could become stale. Currently safe because abilities don't change post-instantiation.

**Recommendation:**
Document that ability lists are immutable post-creation, or add invalidation mechanism.

---

### MOD-SIM-009: Turn Commitment Threshold Hardcoded
**Location:** `game/simulation/entities/projectile.py:11`
**Severity:** Minor
**Deliberate:** Deliberate (but should be configurable)

**Description:**
Missile guidance turn commitment threshold hardcoded to 45 degrees. All missiles use same oscillation prevention logic regardless of maneuverability.

**Recommendation:**
Move to missile weapon ability as optional parameter, with 45 degrees as default.

---

### MOD-SIM-010: Battle Engine Tick Counter Overflow Risk
**Location:** `game/simulation/systems/battle_engine.py:188, 379`
**Severity:** Info
**Deliberate:** Accidental (unlikely edge case)

**Description:**
`tick_counter` incremented indefinitely without overflow protection. Python ints don't overflow, but `absolute_max_ticks` provides safety net. Not a practical concern.

---

### MOD-SIM-011: Emissive Armor Creates Invulnerability at Low Damage
**Location:** `game/simulation/combat/damage_calculator.py:46-51`
**Severity:** Major
**Deliberate:** Deliberate (game design)

**Description:**
Emissive armor uses flat reduction: `damage_amount = max(0, damage_amount - ea)`. This creates a hard immunity threshold where high emissive armor completely negates low-damage weapons. Creates binary rock-paper-scissors rather than soft counters.

**Recommendation:**
Consider diminishing returns or minimum damage passthrough (at least 10% always penetrates).

---

### MOD-SIM-012: Crystalline Armor Recharges Shields While Taking Damage
**Location:** `game/simulation/combat/damage_calculator.py:53-67`
**Severity:** Minor
**Deliberate:** Deliberate (interesting mechanic)

**Description:**
Crystalline armor absorbs damage AND recharges shields by the absorbed amount. This creates a positive feedback loop where being shot makes shields stronger. Counter-intuitive but appears intentional as unique defensive mechanic.

**Recommendation:**
Document as intended behavior. Consider if recharge should be limited (e.g., 50% of absorbed damage).

---

### MOD-SIM-013: Component Damage Weighted by Current HP
**Location:** `game/simulation/combat/damage_calculator.py:100-126`
**Severity:** Minor
**Deliberate:** Deliberate (gameplay design)

**Description:**
Target component selection weighted by current HP — components with more HP are MORE likely to be hit. This spreads damage evenly instead of focusing on weak points. Makes it hard to "finish off" critical systems.

**Assessment:** Deliberate design to prevent alpha-strike eliminating critical components.

---

### MOD-SIM-014: Shield Regen Cost Divided by 100
**Location:** `game/simulation/entities/ship_combat_engine.py:176-178`
**Severity:** Minor
**Deliberate:** Likely Deliberate (scaling)

**Description:**
Shield regeneration rate and cost both divided by 100. Magic number suggests values are "per 100 ticks" or percentages, but there's no documentation explaining why.

**Recommendation:**
Add named constant: `TICKS_PER_SECOND = 100`

---

### MOD-SIM-015: Quadratic Formula Without Catastrophic Cancellation Protection
**Location:** `game/simulation/combat/targeting_system.py:31-78`
**Severity:** Minor
**Deliberate:** Accidental (missing numerical analysis)

**Description:**
Lead solving uses standard quadratic formula vulnerable to catastrophic cancellation when `b` and `sqrt_disc` are nearly equal.

**Recommendation:**
Use numerically stable quadratic formula variant.

---

### MOD-SIM-016: Ship Stats Calculator 5-Phase Design
**Location:** `game/simulation/entities/ship_stats.py:68-150`
**Severity:** Info
**Deliberate:** Deliberate (architecture)

**Description:**
5-phase pipeline with strict dependencies. Well-documented, creates coupling (can't calculate physics without running crew allocation first), but correct for data dependencies.

---

### MOD-SIM-017: No Automated Layer Boundary Enforcement
**Location:** `game/simulation/__init__.py`
**Severity:** Info (Positive finding)
**Deliberate:** Deliberate

**Description:**
No pygame imports in simulation layer (verified). However, no automated enforcement exists.

**Recommendation:**
Add `test_layer_boundaries.py` that asserts simulation has no pygame/ui imports.

---

### MOD-SIM-018: Eval() Security Properly Sandboxed But No Input Validation
**Location:** `game/simulation/formula_system.py:94-144`, `game/simulation/components/modifier_effects.py:116-183`
**Severity:** Major
**Deliberate:** Deliberate (but could be hardened)

**Description:**
Both formula evaluators use `eval()` with proper sandboxing (`{"__builtins__": {}}`) preventing code execution attacks. However, no AST whitelist validation prevents DoS via infinite loops or memory exhaustion. Currently mitigated by trusted-source-only policy.

**Recommendation:**
Add AST validation layer if modding support is planned.

---

## Top 5 Priority Issues

1. **MOD-SIM-001 (Critical):** Boolean type confusion in ability aggregation
2. **MOD-SIM-003 (Major):** Unchecked formula evaluation in weapon damage
3. **MOD-SIM-018 (Major):** Eval() lacks input validation for DoS risk
4. **MOD-SIM-004 (Major):** Damage pipeline order not enforced
5. **MOD-SIM-011 (Major):** Emissive armor creates hard immunity

## Architecture Strengths
- Clean layer separation: No pygame imports in simulation layer
- God class decomposition: Recent PROJ-44/PROJ-88 improvements
- Dependency injection: Strict DI pattern enforced throughout
- Two-stage aggregation: Ability stacking well-designed
- Formula system: Data-driven damage/range formulas
- Caching strategy: Component caching (PROJ-49)
