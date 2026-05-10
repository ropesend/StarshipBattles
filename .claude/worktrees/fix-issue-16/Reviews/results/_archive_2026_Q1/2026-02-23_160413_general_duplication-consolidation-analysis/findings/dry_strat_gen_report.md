# DRY-STRAT-GEN: Strategy Generation, Formulas & Data Report

## Summary
- **Total duplication findings:** 8
- **Critical:** 1, **Major:** 3, **Minor:** 3, **Info:** 1

## Findings

### CRITICAL: Inconsistent Cartesian Conversion Constants
**ID:** CQ-001
**Location:** All 6 density primitives vs `region_classifier.py`
**Issue:** Two different precision levels: `math.sqrt(3.0) / 2.0` (computed) vs `0.8660254037844386` (hardcoded literal). Could cause subtle numerical divergence.
**Impact:** Region classification may disagree with density evaluation at galaxy edges.
**Recommendation:** Extract `HEX_Y_SCALE = math.sqrt(3.0) / 2.0` constant to shared hex utilities.
**Effort:** Simple

### MAJOR: Cartesian Conversion Code Duplication (5 locations)
**ID:** CQ-002
**Location:** `geometric.py:53-58`, `linear.py:50-55`, `spiral_arm.py:52-58`, `region_classifier.py:173-178`, `noise.py:93-94`
**Issue:** Hex-to-Cartesian conversion pattern appears 5 times with identical math.
**Impact:** Core coordinate math duplicated; changes require 5 updates.
**Recommendation:** Create `hex_to_cartesian(q, r, center_q, center_r)` in `hex_utilities.py`.
**Effort:** Simple

### MAJOR: Angle Normalization Algorithm Duplication
**ID:** CQ-003
**Location:** `spiral_arm.py:91-94` (while loop), `region_classifier.py:198` (modulo)
**Issue:** Two different implementations of angle normalization. While-loop version is O(n), modulo is O(1).
**Impact:** Performance difference; algorithm divergence risk.
**Recommendation:** Consolidate to modulo version in `hex_utilities.py`.
**Effort:** Simple

### MAJOR: Hex Distance Calculation Duplication (4 locations)
**ID:** CQ-004
**Location:** `radial.py:51`, `ring.py:51`, `region_classifier.py:167,222`
**Issue:** `dq * dq + dr * dr + dq * dr` hex distance metric repeated 4 times.
**Recommendation:** Extract `hex_distance_sq(q1, r1, q2, r2)` to `hex_utilities.py`.
**Effort:** Simple

### Minor: Gaussian Falloff Calculation (5 locations)
**ID:** CQ-005
**Location:** RadialPrimitive, RingPrimitive, LinearPrimitive, SpiralArmPrimitive, GeometricPrimitive
**Issue:** Similar `math.exp(-(dist^2)/(2*sigma^2))` patterns in 5 primitives.
**Recommendation:** Create `gaussian_falloff(distance, sigma)` in `density_functions.py`.
**Effort:** Simple

### Minor: RNG Initialization Pattern (2 locations)
**ID:** CQ-006
**Location:** Both placement strategies (~lines 88-95, 161-174)
**Issue:** Identical null-check and SpatialIndex setup duplicated.
**Recommendation:** Extract `_ensure_rng()` and `_ensure_spatial_index()` helpers.
**Effort:** Simple

### Minor: Loader Configuration Pattern (3 loaders)
**ID:** CQ-007
**Location:** AstrophysicsLoader, SystemBlueprintsLoader, GalaxyLayoutsLoader
**Issue:** All 3 loaders follow identical structure: `__init__()`, `load()`, `_validate_schema()`.
**Recommendation:** Create abstract base loader class.
**Effort:** Medium

### Info: Habitability Factor Functions
**ID:** CQ-008
**Issue:** The `_gaussian_factor()` helper in habitability module is a good consolidation example. Same pattern should be used in generation subsystem.
**Effort:** N/A

## Top 5 Priority Consolidation Opportunities
1. **Create hex_utilities.py** (CQ-001, CQ-002, CQ-003, CQ-004) - 4 findings consolidated, 7 files fixed, Simple
2. **Gaussian falloff helper** (CQ-005) - 5 primitives, Simple
3. **RNG initialization helper** (CQ-006) - 2 strategies, Simple
4. **Abstract base loader** (CQ-007) - 3 loaders, Medium
5. **Habitability pattern reuse** (CQ-008) - Apply proven pattern to generation
