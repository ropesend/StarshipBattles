# Phase 9: `_CarriedItemsProxy` final cutover

**Status:** Not Started
**Depends on:** phase_8
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_9.planned_files

**Objective:** Delete the test-only `_CarriedItemsProxy` shim at `game/strategy/data/ship_instance.py` (currently lines 92-95 + 371-396). PROJ-431 kept the proxy because 51 test files still poked `ship.carried_items.append({...})` directly; by this phase, production code path no longer references `carried_items` at all. The proxy and its supporting test fixtures get audited and rewritten to the typed `Container` API. This is the final substrate-cutover commit of the project.

---

## Tasks

To be authored at phase start. Expected sub-phase shape (PROJ-431 audit estimated ~51 test files):
- 9a — full grep audit of `ship.carried_items` and `_CarriedItemsProxy` references; scope sub-phases.
- 9b through 9X — sweep test files in tractable batches (e.g., 10 files per sub-phase), each batch its own commit with focused tests green.
- 9Z (final) — delete `_CarriedItemsProxy` class + `carried_items` property from `ship_instance.py`; AST guard `test_no_carried_items_proxy.py` pins absence; grep gate returns zero hits in `game/` AND `tests/`.

---

## Phase Completion Checklist
- [ ] All sub-phases complete
- [ ] `tests/static_guards/test_no_carried_items_proxy.py` green
- [ ] `grep -r '_CarriedItemsProxy' game/ tests/` returns zero
- [ ] `grep -rn 'ship\.carried_items\|\.carried_items\.' game/ tests/` returns zero
- [ ] Full sharded suite green
- [ ] Update status to Complete; update plan.md + phase_state.json
