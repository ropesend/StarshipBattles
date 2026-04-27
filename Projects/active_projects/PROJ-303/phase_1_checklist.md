# Phase 1: Warp point types data registry

**Status:** Complete (2026-04-27)
**Objective:** Confirm the warp_point type taxonomy. Create `data/warp_point_types.json` with intrinsic ability templates.

---

## Tasks

### Task 1.1: Confirm warp_point taxonomy [Simple]
- [ ] Read `game/strategy/data/galaxy.py` and any warp_point definition files. Identify how warp points are typed today.
- [ ] If only one type exists, surface to the user: "Existing codebase has only N warp point types. Should this project introduce additional types (`unstable`, `dimensional_rift`, `precursor_gateway`) or just register the framework path with the current taxonomy?"

**Notes:**

### Task 1.2: Create `data/warp_point_types.json` [Simple]
**File:** `data/warp_point_types.json` (NEW)

- [ ] Write registry per [design.md](design.md) — only types that exist or were approved in 1.1.
- [ ] Add `Paths.WARP_POINT_TYPES_FILE` to `game/core/paths.py`.

**Notes:**

### Task 1.3: Validation test [Simple]
**File:** `tests/integration/data/test_warp_point_types_registry.py` (NEW)
- [ ] Every generated warp_point_type has a registry entry.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
