# PROJ-234 Phase 4: Final Cleanup & Verification [Simple]

**Objective:** Update docstrings, run full test suite, verify no regressions.
**Status:** Not Started

---

#### Task 4.1: Update module docstring [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** N/A (documentation only)
- [ ] Update module docstring (lines 1-13) to mention all 5 delegates:
  - ShipResourceManager (resource tracking)
  - ShipCargoManager (cargo management)
  - ShipDisplayFormatter (display formatting)
  - ShipInstanceBridge (simulation bridge)
  - ShipInstanceSerializer (serialization)
**Notes:**

#### Task 4.2: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] Run full test suite
- [ ] Verify same baseline: 13904 passed, 17 pre-existing failures (star color mapping + assets)
- [ ] Verify no new failures or skips
**Notes:**

#### Task 4.3: Run integration verification [Simple]
**Tests:** Various
- [ ] `pytest tests/integration/save_load/ -v` — save/load round-trips work
- [ ] `pytest tests/unit/strategy/fleet/ -x` — fleet battle adapter works
- [ ] `pytest tests/unit/strategy/ship_instance/test_serialization.py -v` — serialization round-trip
**Notes:**

#### Task 4.4: Verify line count [Simple]
- [ ] Run `wc -l game/strategy/data/ship_instance.py` — target: ~540 lines (down from 756)
- [ ] Run `wc -l game/strategy/data/ship_instance_bridge.py` — expect ~75 lines
- [ ] Run `wc -l game/strategy/data/ship_instance_serializer.py` — expect ~95 lines

---

**Phase 4 Complete When:**
- [ ] All 4 tasks checked off
- [ ] Full test suite baseline maintained
- [ ] ShipInstance line count reduced by ~28%
