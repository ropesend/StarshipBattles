# Performance Review Report

## Summary
- **Total issues found:** 10
- **Critical:** 3
- **Major:** 5
- **Minor:** 2
- **Info:** 0

---

## Findings

### CRITICAL: Nested Component Iteration in Hot Path
**ID:** PERF-01
**Location:** `game/simulation/systems/battle_engine.py:515`, `game/simulation/entities/ship_stats.py:89-90`
**Issue:** `get_all_components()` called repeatedly in hot combat loops. Each call rebuilds a list by iterating all layers.
**Impact:** O(n) list construction multiple times per tick per ship. With 100+ ships, thousands of unnecessary iterations.
**Recommendation:** Cache component list on ship or use generator for immutable iteration.
**Effort:** Medium

### CRITICAL: Projectile List Reconstruction Every Tick
**ID:** PERF-02
**Location:** `game/simulation/projectile_manager.py:138`
**Issue:** `self.projectiles = [p for p in self.projectiles if i not in projectiles_to_remove]` rebuilds entire list every tick.
**Impact:** O(n) memory churn every tick.
**Recommendation:** Use index-based removal or mark dead projectiles for batch cleanup.
**Effort:** Medium

### CRITICAL: O(n²) Targeting Evaluation
**ID:** PERF-03
**Location:** `game/ai/controller.py:124-141`
**Issue:** `_score_and_sort_enemies()` sorts all candidates every tick. Evaluator scans all components for each target.
**Impact:** With 50+ targets, creates O(n²) component scans per frame.
**Recommendation:** Cache weapon/ability availability per ship.
**Effort:** Medium

### MAJOR: Repeated Deep Copies on Initialization
**ID:** PERF-04
**Location:** `game/simulation/components/component.py:91, 134, 543`
**Issue:** Three `deepcopy()` calls during component init: data, abilities, base_abilities.
**Impact:** Expensive for complex components. Happens for every component in every ship.
**Recommendation:** Use shallow copies where mutation isn't needed.
**Effort:** Simple

### MAJOR: Inefficient Ability Lookup with MRO Fallback
**ID:** PERF-05
**Location:** `game/simulation/components/component.py:182-209`
**Issue:** `get_abilities()` uses fallback isinstance/MRO walking on every lookup.
**Impact:** O(n) method resolution order walk per ability query.
**Recommendation:** Build ability name index during instantiation.
**Effort:** Simple

### MAJOR: Spatial Grid Cleared Every Tick
**ID:** PERF-06
**Location:** `game/simulation/systems/battle_engine.py:344-351`
**Issue:** Entire spatial grid cleared and rebuilt with all ships/projectiles every tick.
**Impact:** Unnecessary O(n) churn. Could use incremental updates.
**Recommendation:** Use quad-tree or incremental grid updates.
**Effort:** Complex

### MAJOR: Beam Targeting Multiple Raycasts
**ID:** PERF-07
**Location:** `game/engine/collision.py:64-137`
**Issue:** Each beam recalculates sphere-ray intersection even for same target.
**Impact:** Multiple beams vs same target = repeated expensive math.
**Recommendation:** Cache intersection results per target per tick.
**Effort:** Medium

### MAJOR: Component Status Checks on Every Damage Frame
**ID:** PERF-08
**Location:** `game/simulation/entities/ship_stats.py:145-153`
**Issue:** Damage threshold checks iterated for all components during `calculate()` which runs frequently.
**Impact:** Repeated HP ratio calculations (division is expensive).
**Recommendation:** Cache damage status with dirty flag system.
**Effort:** Medium

### MINOR: Repeated Vector2 Conversions
**ID:** PERF-09
**Location:** `game/simulation/projectile_manager.py:47-48, 63-64`
**Issue:** Creates new Vector2 objects from existing ones for type safety.
**Impact:** Unnecessary allocations in tight collision loop.
**Recommendation:** Accept duck-typed vectors or use type hints.
**Effort:** Simple

### MINOR: Sorted Enemies Multiple Times
**ID:** PERF-10
**Location:** `game/ai/target_evaluator.py:97-140`
**Issue:** Distance calculations repeated for same targets across rules.
**Impact:** Multiple distance.length() calls per target.
**Recommendation:** Pre-calculate sorted distances once.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **PERF-01: Nested Component Iteration** - Hot path inefficiency affecting every tick

2. **PERF-02: Projectile List Reconstruction** - Memory churn every tick

3. **PERF-03: O(n²) Targeting Evaluation** - Scales poorly with fleet size

4. **PERF-06: Spatial Grid Rebuild** - Could use incremental updates

5. **PERF-04: Repeated Deep Copies** - Expensive initialization pattern
