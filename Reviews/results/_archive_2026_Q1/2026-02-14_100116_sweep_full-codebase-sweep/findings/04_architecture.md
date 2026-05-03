# Architecture Drift Sweep: Antigravity

## Summary
- **Shard:** Antigravity (Full Sweep)
- **Files Scanned:** 370+
- **Total Issues Found:** 2
- **Critical:** 0 | **Major:** 1 | **Minor:** 1 | **Info:** 0

## Findings

#### MAJOR: God Class in Strategy Layer
**ID:** ADR-AG-001
**Location:** `game/strategy/engine/production_engine.py`
**Issue:** `ProductionEngine` is a large class (~30KB) handling complex production logic.
**Impact:** High cognitive load, difficulty in testing specific production rules isolation.
**Recommendation:** Refactor into smaller sub-engines or rule handlers (e.g., `QueueManager`, `ResourceConsumer`, `ProgressCalculator`).
**Effort:** Complex

#### MINOR: UI Data in Simulation/Strategy
**ID:** ADR-AG-002
**Location:** `game/simulation/entities/ship.py`
**Issue:** `Ship` entity stores `color` and `theme_id`.
**Impact:** Minor coupling of visual presentation data with simulation state.
**Recommendation:** Acceptable for now as data-only, but verify no `pygame` objects are stored.
**Effort:** Simple

## Top Priority Issues
1. **Refactor `ProductionEngine`**: Decomposition will improve maintainability and testability of the strategy layer.
