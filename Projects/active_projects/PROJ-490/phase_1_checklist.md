# Phase 1: Remove / tighten 9 stale comments

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-490 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update or remove 9 stale comments so the code's narrative reflects current reality. No behavior changes.

---

## Tasks

### Task 1.1: Update `ship_instance.py` `carried_items` doc comments
**File:** `game/strategy/data/ship_instance.py`
**Tests:** none (comment-only)

- [ ] Update or remove the comment at line 170 `# legacy ``carried_items: List[Dict[str, Any]]`` mixed-shape list.` — clarify the field/property was deleted in PROJ-436 Phase 9 (per the existing note at lines 572-574). LEG-01-002.
- [ ] Update or remove the comment at line 180 `# legacy dict-list shape — see ``carried_items`` property.` — referenced property no longer exists. LEG-01-003.
- [ ] Update or remove the broader doc comments at lines 170-180 and 549-552 (A-05) — they imply `carried_items` is current; the property was deleted in PROJ-436 Phase 9. Either delete the comments or rewrite to past tense.

### Task 1.2: Update `ship_instance_serializer.py:62` (optional)
**File:** `game/strategy/data/ship_instance_serializer.py`
**Tests:** none (comment-only)

- [ ] LEG-01-004 — comment at line 62 `# legacy ``carried_items`` dict-list shape is no longer the` is factually accurate (verifier: "acceptable to keep as-is"). Optionally add a date or PROJ reference for clarity (e.g. "Removed in PROJ-436 Phase 9").

### Task 1.3: Remove "legacy projection" comment in `strategy_detail_fmt.py:564`
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** none

- [ ] D-01 — Comment at line 564 `# legacy projection).` is misleading. The code reads from the canonical PROJ-431/436 `bay_inventory` substrate. Remove the misleading reference; if a comment is needed, replace with one that accurately describes the data origin.

### Task 1.4: Add dated TODO or remove fallback in `mine_group_service.py:130`
**File:** `game/strategy/services/mine_group_service.py`
**Tests:** `pytest tests/unit/strategy/services/test_mine_group_service.py`

- [ ] LEG-02-002 — Comment `# legacy test stub that still uses ``fleets``.` near the fallback `for attr in ("deployed_groups", "fleets")` at line 130. Decide: (a) add a dated TODO with a PROJ reference for when the `fleets` fallback can be removed, OR (b) audit + migrate the test stubs that still use `fleets` and remove the fallback in this PR. Option (b) is cleaner if the test scope is small.

### Task 1.5: Remove stale PROJ-225 comment
**File:** `game/simulation/entities/ship_stat_querier.py`
**Tests:** none

- [ ] LEG-02-009 — Remove or shorten the historical comment at lines 144-145 `# PROJ-225: Removed redundant cached_summary property (DUP-SIM-007). # Use Ship.cached_summary instead.` PROJ-225 is in deep_archive. Replace with the minimal hint `# Use Ship.cached_summary` if the call-site context benefits from it; otherwise delete.

### Task 1.6: Remove PROJ-67 reference in `build_context.py` docstring
**File:** `game/strategy/data/build_context.py`
**Tests:** none

- [ ] LEG-02-010 — Update the module docstring at lines 1-4. PROJ-67 is archived (2026-02-10). Replace with a generic module description that does not reference the historical project.

### Task 1.7: Remove stale PROJ-218 comment
**File:** `game/strategy/data/design_metadata.py`
**Tests:** none

- [ ] LEG-02-011 — Remove the comment at lines 253-254 `PROJ-218: Fixed field name from 'cost' to 'resource_cost' for consistency.` PROJ-218 is archived (2026-03-14).

### Phase Verification
- [ ] `pytest tests/ --testmon` passes (comment-only changes — pass should be unaffected)
- [ ] `grep -rn "PROJ-225\|PROJ-67\|PROJ-218" .` returns only matches inside archived material — none in active production code
- [ ] No reference to `carried_items` as a present-tense feature remains in `ship_instance.py` or `ship_instance_serializer.py`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to mark project complete

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
