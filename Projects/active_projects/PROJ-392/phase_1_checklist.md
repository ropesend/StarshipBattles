# Phase 1: Critical — zero-call-site quick deletions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-392 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete 3 zero-call-site legacy placeholders/aliases in a single PR. No migration needed; nothing breaks.

---

## Tasks

### Task 1.1: Delete the 3 zero-call-site legacy artifacts in one pass
**File:** Three files (one task to keep them in one PR)
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Delete `_priority_sort_key` helper at `game/simulation/entities/ship_stats.py:503-505` (LEG-01-001) (0 call sites — single-PR deletion)
- [ ] Delete `self.name_input = None  # legacy attr (Identity panel replaced this)` at `game/ui/screens/race_setup/screen.py:261` (LEG-02-007) (0 call sites — single-PR deletion)
- [ ] Delete `self.expanded_ships = self._expanded_ids` backward-compat alias at `game/ui/panels/battle_panels.py:92`; also rename any read of `self.expanded_ships` (audit reports zero — confirm via grep first) to `self._expanded_ids` or expose a public `expanded_ids` property if needed (LEG-03-025) (0 call sites — single-PR deletion)
- [ ] Verify: `grep -rn "_priority_sort_key" game/ tests/ combat_lab/` returns zero hits
- [ ] Verify: `grep -rn "screen.name_input" game/ tests/ combat_lab/` returns zero hits
- [ ] Verify: `grep -rn "\.expanded_ships" game/ tests/ combat_lab/` returns zero hits in the deleted-name form
- [ ] Verify: full sharded suite passes

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
