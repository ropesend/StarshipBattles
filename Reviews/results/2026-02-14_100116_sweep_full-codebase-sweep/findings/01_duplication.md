# Duplication & Fragmentation Sweep: Antigravity

## Summary
- **Shard:** Antigravity (Full Sweep)
- **Files Scanned:** 370+
- **Total Issues Found:** 1
- **Critical:** 0 | **Major:** 0 | **Minor:** 1 | **Info:** 0

## Findings

#### MINOR: AI vs Simulation Targeting Logic Overlap
**ID:** DUP-AG-001
**Location:** `game/ai/combat_utils.py` AND `game/simulation/combat/targeting_system.py`
**Issue:** `is_in_pdc_arc` in `combat_utils.py` replicates logic found in `TargetingSystem.find_valid_target` (arc checks, distance checks).
**Impact:** Low. AI needs fast utility checks without invoking full simulation systems, but changes to firing arc logic in simulation might not propagate to AI utils.
**Recommendation:** Expose `TargetingSystem` helper methods for arc validation that `combat_utils` can consume, or ensure `TargetingSystem` is accessible to AI for these checks.
**Effort:** Low

## Top Priority Issues
1. **AI/Sim Targeting Drift**: Risk of AI thinking it can fire when Simulation says it can't (or vice versa) due to duplicated arc math.
