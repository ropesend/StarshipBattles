# Phase 14: UI-Strategy Layer Remediation

**Status:** Complete
**Estimated Effort:** 4-5 hours
**Priority:** Low - Cleanup phase for remaining cross-layer imports

## Overview

Address remaining UI files that import from the Strategy layer. Focus on:
- Moving type-hint-only imports to TYPE_CHECKING blocks
- Documenting acceptable runtime imports (coordination between UI and strategy)
- Using dependency injection where feasible

---

## Tier 1: Design and Race Configuration (2 files)

### 14.1 design_selector_window.py ✅
**Location:** `game/ui/screens/design_selector_window.py`
**Violations:**
- `DesignLibrary` from strategy - runtime (required for design selection)
- `DesignMetadata` from strategy - type hints

- [x] Move `DesignMetadata` to TYPE_CHECKING block
- [x] Document DesignLibrary as acceptable runtime dependency (file I/O)
- [x] Consider DI for DesignLibrary if feasible - Kept: injected via constructor
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 14.2 race_setup_screen.py ✅
**Location:** `game/ui/screens/race_setup_screen.py`
**Violations:**
- `RaceConfig` from strategy - runtime (callback data)
- `RaceLibrary` from strategy - runtime (save/load)

- [x] Evaluate if RaceConfig can use TYPE_CHECKING - Kept: used at runtime
- [x] Document RaceLibrary as acceptable runtime dependency (file I/O)
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

## Tier 2: Fleet and Order Management (3 files)

### 14.3 fleet_orders_window.py ✅
**Location:** `game/ui/screens/fleet_orders_window.py`
**Violations:**
- `OrderType` from strategy - runtime (order display logic)

- [x] Document OrderType as acceptable runtime dependency
- [x] Verify no other strategy layer violations
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 14.4 strategy_detail_fmt.py ✅
**Location:** `game/ui/screens/strategy_detail_fmt.py`
**Violations:**
- `OrderType` from strategy - runtime (order type checking)
- Protocol imports from core - acceptable

- [x] Document OrderType as acceptable runtime dependency
- [x] Verify protocol-based design is working correctly
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 14.5 strategy_screen.py ✅
**Location:** `game/ui/screens/strategy_screen.py`
**Violations:**
- `OrderType` from strategy - runtime (order formatting)

- [x] Document OrderType as acceptable runtime dependency
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

## Tier 3: Strategy Coordination Files (4 files)

These files coordinate between UI and strategy layer for gameplay.

### 14.6 strategy_camera_nav.py ✅
**Location:** `game/ui/screens/strategy_camera_nav.py`
**Violations:**
- `hex_to_pixel`, `HexCoord` from strategy - runtime (coordinate conversions)
- `StarSystem` from strategy - type checking/inheritance

- [x] Verify StarSystem is in TYPE_CHECKING if only used for type hints - Kept: isinstance check
- [x] Document hex utilities as acceptable runtime dependencies
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 14.7 strategy_colonization.py ✅
**Location:** `game/ui/screens/strategy_colonization.py`
**Violations:**
- `IssueColonizeCommand`, `QueueColonizeMissionCommand` from strategy - runtime
- `pixel_to_hex` from strategy - runtime
- `StrategySessionFacade` - already TYPE_CHECKING ✓

- [x] Document command imports as acceptable (UI must issue commands)
- [x] Verify StrategySessionFacade is properly TYPE_CHECKING guarded
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 14.8 strategy_fleet_ops.py ✅
**Location:** `game/ui/screens/strategy_fleet_ops.py`
**Violations:**
- `pixel_to_hex` from strategy - runtime
- `IssueMoveCommand`, `IssueInterceptCommand`, `IssueJoinFleetCommand` from strategy - runtime
- `StrategySessionFacade` - already TYPE_CHECKING ✓

- [x] Document command imports as acceptable (UI must issue commands)
- [x] Verify StrategySessionFacade is properly TYPE_CHECKING guarded
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

### 14.9 strategy_renderer.py ✅
**Location:** `game/ui/screens/strategy_renderer.py`
**Violations:**
- `hex_to_pixel`, `pixel_to_hex`, `HexCoord` from strategy - runtime
- `OrderType` from strategy - runtime (move preview logic)

- [x] Document hex utilities as acceptable runtime dependencies
- [x] Document OrderType as acceptable for rendering
- [x] Run: `pytest tests/unit/ui/ -q` - passed

---

## Verification

- [x] Run all UI tests: `pytest tests/unit/ui/ -v` - passed
- [x] Run all strategy tests: `pytest tests/unit/strategy/ -v` - passed
- [x] Verify no circular imports: `python -c "import game.ui"` - SUCCESS
- [x] Verify no regressions: `pytest tests/ -q --tb=no` - 5199 passed, 3 skipped

---

## Notes

- Strategy layer imports are necessary for UI coordination with game logic
- Command imports (IssueMoveCommand, etc.) are acceptable - UI must issue commands
- Hex utilities (hex_to_pixel, pixel_to_hex) are acceptable for map rendering
- OrderType enum is acceptable for displaying fleet order status
- TYPE_CHECKING guards already in place for StrategySessionFacade (good pattern)
- Consider extracting hex utilities to game.core if they're truly UI-agnostic
