# Phase 1: Remove / tighten 9 stale comments

**Status:** Complete
**Objective:** Update or remove 9 stale comments so the code's narrative reflects current reality. No behavior changes.

---

## Tasks

### Task 1.1: Update `ship_instance.py` `carried_items` doc comments
**File:** `game/strategy/data/ship_instance.py`

- [x] Replaced the block at lines 169-180 (LEG-01-002 + LEG-01-003 + A-05 head) — dropped the historical PROJ-431 framing and references to the deleted `carried_items` property; kept a tight summary of the typed `bay_inventory` shape.
- [x] Replaced the block at lines 534-545 (A-05 tail) — dropped the false "what remains here is a backward-compatible property/setter exposing the legacy dict-list shape" wording; kept the genuine `set_bay_inventory` description. Also deleted the now-redundant `# PROJ-436 Phase 9: carried_items property... deleted` comment immediately after `set_bay_inventory`.

### Task 1.2: Tighten `ship_instance_serializer.py:62` (LEG-01-004)
**File:** `game/strategy/data/ship_instance_serializer.py`

- [x] Dropped the "PROJ-431 Phase 1f: ... legacy ``carried_items`` dict-list shape is no longer the storage surface" preamble; kept the schema description.

### Task 1.3: Drop misleading "legacy projection" in `strategy_detail_fmt.py:564` (D-01)
**File:** `game/ui/screens/strategy_detail_fmt.py`

- [x] Dropped the "(set by the legacy projection)" parenthetical. The pod payload is set normally; there is no projection.

### Task 1.4: Tighten the fallback comment in `mine_group_service.py:130` (LEG-02-002)
**File:** `game/strategy/services/mine_group_service.py`

- [x] Dropped the "PROJ-431 Phase 2" preamble; kept the "fall back to fleets for older test stubs" rationale. The fallback itself is retained — no behavior change.

### Task 1.5: Drop stale PROJ-225 comment in `ship_stat_querier.py:144-145` (LEG-02-009)
**File:** `game/simulation/entities/ship_stat_querier.py`

- [x] Deleted the 2-line "PROJ-225: Removed redundant cached_summary property" comment. It was at end-of-class with no following code to anchor.

### Task 1.6: Drop PROJ-67 reference in `build_context.py` (LEG-02-010)
**File:** `game/strategy/data/build_context.py`

- [x] Replaced "Created as part of PROJ-67 Phase 4 to allow BuildQueueScreen..." with a generic timeless description.

### Task 1.7: Drop stale PROJ-218 comment in `design_metadata.py:254` (LEG-02-011)
**File:** `game/strategy/data/design_metadata.py`

- [x] Deleted the "PROJ-218: Fixed field name from 'cost' to 'resource_cost' for consistency." line.

### Phase Verification
- [x] All 7 target modules import cleanly (`python -c "import ..."` for each)
- [x] `pytest tests/unit/strategy/services/test_mine_group_service.py` 10 passed
- [x] Comment-only edits — no behavioral risk

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to mark project complete

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
