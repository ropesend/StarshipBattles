# Phase 1: Critical Architecture Fixes

**Status:** Not Started
**Estimated Effort:** 6-8 hours
**Priority:** Highest - These issues break architectural principles

## Overview
Address the 3 critical layer violations that undermine the architectural integrity of the codebase.

---

## Tasks

### 1.1 Fix Core → Strategy Layer Violation (NEW-CORE-001)
**Location:** `game/core/protocols.py:37`
**Issue:** Core module imports HexCoord from strategy layer, violating dependency direction.

- [ ] Create `ICoordinate` protocol in `game/core/protocols.py`
- [ ] Define minimal coordinate interface (x, y, distance methods)
- [ ] Update `game/core/protocols.py` to use forward reference or new protocol
- [ ] Remove `from game.strategy.data.hex_math import HexCoord` import
- [ ] Verify strategy layer still works with new protocol
- [ ] Run tests: `pytest tests/unit/strategy/ -v`

**Acceptance:** Core module has no imports from strategy layer

---

### 1.2 Fix Duplicate Attribute Initialization (NEW-SIM-001)
**Location:** `game/simulation/entities/ship.py:92, 135`
**Issue:** `total_defense_score` initialized twice with different values (0.0 then 1.0).

- [ ] Identify correct initial value for `total_defense_score`
- [ ] Remove duplicate assignment (keep line 135 with value 1.0 based on usage)
- [ ] Add comment explaining why default is 1.0 (not 0.0)
- [ ] Search for any code that depends on 0.0 default
- [ ] Run tests: `pytest tests/unit/entities/test_ship.py -v`

**Acceptance:** Single initialization with documented rationale

---

### 1.3 Fix UI → Internal Layer Violations (NEW-UI-001)
**Location:** 37 instances across UI layer
**Issue:** UI layer directly imports from simulation, strategy, and AI layers.

#### Phase 1.3a: Analyze and Plan (2 hours)
- [ ] Document all 37 violation instances
- [ ] Group by type: entity access, service calls, type hints
- [ ] Identify which need facades vs. which can use interfaces
- [ ] Create `game/ui/services/__init__.py` for UI-facing services

#### Phase 1.3b: Create Service Interfaces (2 hours)
- [ ] Create `IShipDataProvider` interface for ship display data
- [ ] Create `IBattleStateProvider` interface for battle state
- [ ] Create `IDesignService` interface for design operations
- [ ] Add interfaces to `game/core/protocols.py` or `game/ui/interfaces.py`

#### Phase 1.3c: Implement Adapters (2 hours)
- [ ] Create adapter classes that wrap simulation/strategy entities
- [ ] Wire adapters in screen initialization
- [ ] Update imports in UI screens to use adapters

#### Phase 1.3d: Migrate Critical Files (2 hours)
Priority files (highest violation count):
- [ ] `battle_scene.py` - Remove AIController import
- [ ] `workshop_screen.py` - Create facade for simulation access
- [ ] `build_queue_screen.py` - Use interfaces for strategy/simulation
- [ ] `panels/ship_stats_renderer.py` - Use data transfer objects

**Acceptance:** UI layer only imports from core, ui services, and dedicated interfaces

---

## Verification

- [ ] Run full test suite: `pytest`
- [ ] Verify no circular imports: `python -c "import game.core; import game.simulation; import game.strategy; import game.ui"`
- [ ] Check import graph for violations (optional: use pydeps or similar)

---

## Notes
- Phase 1.3 (UI violations) is the most complex and may extend into multiple sessions
- Consider creating a separate PROJ for comprehensive UI layer refactoring if scope grows
- Document all architectural decisions in `decisions.md`
