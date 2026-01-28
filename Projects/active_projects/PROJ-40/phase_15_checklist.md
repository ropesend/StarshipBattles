# Phase 15: UI-AI Layer Remediation

**Status:** Complete
**Estimated Effort:** 2-3 hours
**Priority:** Low - Cleanup phase for remaining cross-layer imports

## Overview

Address remaining UI files that import from the AI layer. Focus on:
- Moving type-hint-only imports to TYPE_CHECKING blocks
- Documenting acceptable runtime imports (battle orchestration)
- Understanding why AI layer access is needed from UI

---

## Tier 1: Battle Orchestration (1 file)

### 15.1 orchestration/battle_orchestrator.py ✅
**Location:** `game/ui/orchestration/battle_orchestrator.py`
**Violations:**
- `AIController` from AI - runtime (core functionality)
- `ShipControllableAdapter` from AI - runtime (adapter pattern)
- `SpatialGrid` from simulation - runtime (dependency injection)
- `Ship` from simulation - TYPE_CHECKING ✓

- [x] Verify `Ship` is properly in TYPE_CHECKING block
- [x] Document AIController and ShipControllableAdapter as acceptable
  (orchestrator bridges UI-AI-Simulation layers by design)
- [x] Document SpatialGrid as acceptable (injected dependency)
- [x] Add module docstring explaining architectural role
- [x] Run: `pytest tests/unit/ui/ -q` - passed

**Architecture Note:**
The battle_orchestrator.py is intentionally a boundary-crossing module that
coordinates between UI, AI, and Simulation layers. It should document this
role clearly rather than trying to eliminate the cross-layer dependencies.

---

## Tier 2: Setup Rendering (1 file)

### 15.2 setup_renderer.py ✅
**Location:** `game/ui/screens/setup_renderer.py`
**Violations:**
- `StrategyManager` from AI - runtime (dropdown rendering)

- [x] Document StrategyManager as acceptable (displays AI strategy options)
- [x] Verify no other AI layer violations
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

## Verification

- [x] Run all UI tests: `pytest tests/unit/ui/ -v` - passed
- [x] Verify no circular imports: `python -c "import game.ui"` - SUCCESS
- [x] Verify no regressions: `pytest tests/ -q --tb=no` - 5199 passed, 3 skipped

---

## Notes

- AI layer imports from UI are minimal (2 files)
- `battle_orchestrator.py` is an intentional boundary module
- `setup_renderer.py` needs StrategyManager for UI dropdowns
- These are acceptable architectural dependencies - document, don't eliminate
