# Phase 13: UI-Simulation Layer Remediation

**Status:** Complete
**Estimated Effort:** 4-6 hours
**Priority:** Low - Cleanup phase for remaining cross-layer imports

## Overview

Address remaining UI files that import from the Simulation layer. Focus on:
- Moving type-hint-only imports to TYPE_CHECKING blocks
- Documenting acceptable runtime imports (e.g., LayerType enum)
- Using canonical import locations (game.core.constants for LayerType)

---

## Tier 1: LayerType Canonical Imports (6 files)

These files import LayerType from simulation layer - should use canonical location.

### 13.1 hud/panels.py
**Location:** `game/ui/hud/panels.py`
**Violations:**
- `ComponentStatus` from simulation - runtime (acceptable for status display)
- `LayerType` from simulation - should use canonical
- `StrategyManager` from AI - runtime (acceptable for name display)

- [x] Import `LayerType` from `game.core.constants` instead of simulation
- [x] Document acceptable runtime imports in docstring
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 13.2 panels/design_report_panel.py
**Location:** `game/ui/panels/design_report_panel.py`
**Violations:**
- `Ship` from simulation - type hints only
- `LayerType` from simulation - runtime

- [x] Move `Ship` to TYPE_CHECKING block
- [x] Import `LayerType` from `game.core.constants`
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 13.3 panels/ship_detail_panel.py
**Location:** `game/ui/panels/ship_detail_panel.py`
**Violations:**
- `ShipInstance` from strategy - type hints only
- `LayerType` from simulation - runtime

- [x] Verify `ShipInstance` is in TYPE_CHECKING block
- [x] Import `LayerType` from `game.core.constants`
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 13.4 renderer/game_renderer.py ✅
**Location:** `game/ui/renderer/game_renderer.py`
**Violations:**
- `LayerType` from simulation - runtime
- `LayerDefaults` from core - acceptable

- [x] Import `LayerType` from `game.core.constants`
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 13.5 renderer/renderer.py ✅
**Location:** `game/ui/renderer/renderer.py`
**Violations:**
- `LayerType` from simulation - runtime

- [x] Import `LayerType` from `game.core.constants`
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 13.6 workshop_event_router.py ✅
**Location:** `game/ui/screens/workshop_event_router.py`
**Violations:**
- `LayerType` from simulation - runtime

- [x] Import `LayerType` from `game.core.constants`
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

## Tier 2: Builder Panel Files (6 files)

These builder UI files have simulation layer dependencies for component display.

### 13.7 builder/detail_panel.py ✅
**Location:** `game/ui/screens/builder/detail_panel.py`
**Violations:**
- `LayerType` from simulation - runtime
- `ABILITY_REGISTRY` from simulation - runtime (acceptable for ability display)

- [x] Import `LayerType` from `game.core.constants`
- [x] Document ABILITY_REGISTRY as acceptable runtime dependency
- [x] Run: `pytest tests/unit/builder/ -q` - passed

---

### 13.8 builder/layer_panel.py ✅
**Location:** `game/ui/screens/builder/layer_panel.py`
**Violations:**
- `LayerType` from simulation - runtime
- `VALIDATOR` from simulation - runtime (acceptable for validation display)

- [x] Import `LayerType` from `game.core.constants`
- [x] Document VALIDATOR as acceptable runtime dependency
- [x] Run: `pytest tests/unit/builder/ -q` - passed

---

### 13.9 builder/legacy_components.py ✅
**Location:** `game/ui/screens/builder/legacy_components.py`
**Violations:**
- `MODIFIER_REGISTRY` from simulation - runtime

- [x] Document as acceptable runtime dependency for component editing
- [x] Consider deprecation note if this is truly legacy
- [x] Run: `pytest tests/unit/builder/ -q` - passed

---

### 13.10 builder/modifier_logic.py ✅
**Location:** `game/ui/screens/builder/modifier_logic.py`
**Violations:**
- `MODIFIER_REGISTRY` from simulation - runtime

- [x] Document as acceptable runtime dependency for modifier operations
- [x] Run: `pytest tests/unit/builder/ -q` - passed

---

### 13.11 builder/right_panel.py ✅
**Location:** `game/ui/screens/builder/right_panel.py`
**Violations:**
- `VEHICLE_CLASSES` from simulation - runtime
- `StrategyManager` from AI - runtime
- `LayerType` from simulation - runtime

- [x] Import `LayerType` from `game.core.constants`
- [x] Document VEHICLE_CLASSES and StrategyManager as acceptable runtime dependencies
- [x] Run: `pytest tests/unit/builder/ -q` - passed

---

### 13.12 builder/stats_config.py ✅
**Location:** `game/ui/screens/builder/stats_config.py`
**Violations:**
- `LayerType` from simulation - runtime
- `ResourceConsumption` from simulation - runtime

- [x] Import `LayerType` from `game.core.constants`
- [x] Document ResourceConsumption as acceptable runtime dependency
- [x] Run: `pytest tests/unit/builder/ -q` - passed

---

## Tier 3: Setup Files (4 files)

These files handle battle setup and require Ship/StrategyManager access.

### 13.13 setup.py ✅
**Location:** `game/ui/screens/setup.py`
**Violations:**
- `Ship` from simulation - runtime
- `StrategyManager` from AI - runtime

- [x] Evaluate if Ship can be replaced with protocol/interface - Kept: UI creates Ship instances
- [x] Document acceptable runtime dependencies if kept
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 13.14 setup_data_io.py ✅
**Location:** `game/ui/screens/setup_data_io.py`
**Violations:**
- `Ship` from simulation - runtime

- [x] Evaluate if Ship can be replaced with protocol/interface - Kept: UI creates Ship instances
- [x] Document acceptable runtime dependency if kept
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 13.15 setup_screen.py ✅
**Location:** `game/ui/screens/setup_screen.py`
**Violations:**
- `Ship` from simulation - runtime
- `StrategyManager` from AI - runtime

- [x] Evaluate if dependencies can be injected - Kept: UI creates Ship instances
- [x] Document acceptable runtime dependencies if kept
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 13.16 builder/schematic_view.py ✅
**Location:** `game/ui/screens/builder/schematic_view.py`
**Violations:**
- `VEHICLE_CLASSES` from simulation - runtime
- `LayerType` from simulation - runtime

- [x] Import `LayerType` from `game.core.constants`
- [x] Document VEHICLE_CLASSES as acceptable runtime dependency
- [x] Run: `pytest tests/unit/builder/ -q` - passed

---

## Verification

- [x] Run all UI tests: `pytest tests/unit/ui/ -v` - passed
- [x] Run all builder tests: `pytest tests/unit/builder/ -v` - passed
- [x] Verify no circular imports: `python -c "import game.ui"` - SUCCESS
- [x] Verify no regressions: `pytest tests/ -q --tb=no` - 5199 passed, 3 skipped

---

## Notes

- Primary fix pattern: Import `LayerType` from `game.core.constants` (canonical)
- Many simulation imports are acceptable for UI display purposes
- Runtime access to VEHICLE_CLASSES, ABILITY_REGISTRY, MODIFIER_REGISTRY is
  necessary for the builder UI to function
- Ship imports may be replaceable with protocols in future work
