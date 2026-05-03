# PROJ-XXX: Architecture and Consistency Standardization

## Project Goal
Clarify architectural relationships, address circular import risks, monitor god class indicators, and standardize consistency patterns across the codebase.

## Current State
- game.engine role unclear (is it below or above simulation?)
- Ship/ModifierService circular import requires runtime workaround
- Ship (810 LOC), Component (723 LOC), Galaxy classes are large
- Inconsistent naming (clear vs reset, get_ vs load_)
- Incomplete __all__ exports and error codes

## Target State
- Clear architecture document defining layer relationships
- Circular imports resolved or documented as acceptable
- God class monitoring with decomposition thresholds
- Consistent naming conventions documented and enforced
- Complete module exports

---

## Phase 1: Architecture Documentation
**Status:** Not Started

### Tasks
- [ ] 1.1 Create `docs/architecture/layer_dependencies.md`
- [ ] 1.2 Document game.engine as "Core-adjacent infrastructure"
- [ ] 1.3 Document acceptable TYPE_CHECKING cross-layer patterns
- [ ] 1.4 Document why Strategy imports AI (permitted per current analysis)
- [ ] 1.5 Add diagram showing layer dependencies
- [ ] 1.6 Review and update existing `docs/README.md`

### Files Created
- `docs/architecture/layer_dependencies.md`

---

## Phase 2: Circular Import Remediation
**Status:** Not Started

### Tasks
- [ ] 2.1 Analyze Ship/ModifierService circular import
- [ ] 2.2 Design solution using event/callback pattern
- [ ] 2.3 Implement modifier event emitter in Ship
- [ ] 2.4 Have ModifierService subscribe to events
- [ ] 2.5 Remove late imports from ship.py
- [ ] 2.6 Review Ship/ShipSerializer pattern
- [ ] 2.7 Document if acceptable (serialization patterns are common)
- [ ] 2.8 Run test suite

### Files Affected
- `game/simulation/entities/ship.py`
- `game/simulation/services/modifier_service.py`
- `game/simulation/entities/ship_serialization.py`

---

## Phase 3: God Class Monitoring
**Status:** Not Started

### Tasks
- [ ] 3.1 Create `Projects/scripts/loc_monitor.py` for LOC tracking
- [ ] 3.2 Define thresholds (1000 LOC = warning, 1200 LOC = critical)
- [ ] 3.3 Add current sizes to baseline
- [ ] 3.4 Document decomposition strategy for Ship if needed
- [ ] 3.5 Document decomposition strategy for Component if needed
- [ ] 3.6 Review Galaxy class for extraction opportunities
- [ ] 3.7 Run LOC check as part of PR template

### Files Created
- `Projects/scripts/loc_monitor.py`
- `docs/architecture/class_size_policy.md`

---

## Phase 4: Consistency Standardization
**Status:** Not Started

### Tasks
- [ ] 4.1 Standardize on clear() for singleton reset (vs reset())
- [ ] 4.2 Update registry.py method names if needed
- [ ] 4.3 Complete __all__ exports in game/core/constants.py
- [ ] 4.4 Review error_codes.py for missing codes
- [ ] 4.5 Extract magic numbers from ship_physics.py to constants
- [ ] 4.6 Document get_ vs load_ naming convention
- [ ] 4.7 Standardize Component type checking (string vs isinstance)
- [ ] 4.8 Run full test suite
- [ ] 4.9 Final consistency audit

### Files Affected
- `game/core/registry.py`
- `game/core/constants.py`
- `game/core/error_codes.py`
- `game/simulation/entities/ship_physics.py`

---

## Success Metrics
- [ ] Architecture document complete
- [ ] Circular imports resolved or documented
- [ ] LOC monitoring in place
- [ ] Naming conventions documented
- [ ] __all__ exports complete
- [ ] All tests passing
