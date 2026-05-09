# Phase 1: Critical — zero-call-site quick deletions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-392 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete 3 zero-call-site legacy placeholders/aliases in a single PR. No migration needed; nothing breaks.

---

## Tasks

### Task 1.1: Delete the 3 zero-call-site legacy artifacts in one pass
**File:** Three files (one task to keep them in one PR)
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Delete `_priority_sort_key` helper at `game/simulation/entities/ship_stats.py:503-505` (LEG-01-001) (0 call sites — single-PR deletion)
- [x] Delete `self.name_input = None  # legacy attr (Identity panel replaced this)` at `game/ui/screens/race_setup/screen.py:261` (LEG-02-007) (0 call sites — single-PR deletion). Also cleaned 2 test fixtures (`tests/fixtures/race_setup_ui_builders.py`, `tests/fixtures/test_race_setup_ui_builders.py`) that mocked/asserted the legacy attribute.
- [x] Delete `self.expanded_ships = self._expanded_ids` backward-compat alias at `game/ui/panels/battle_panels.py:92`. Audit's "0 readers" claim was wrong: 14 test usages migrated `panel.expanded_ships` → `panel._expanded_ids` across `test_battle_panels.py`, `test_battle_panels_extended.py`, `test_battle_panels_characterization.py` (LEG-03-025).
- [x] Verify: `grep -rn "_priority_sort_key" game/ tests/ combat_lab/` returns zero hits
- [x] Verify: `grep -rn "screen.name_input" game/ tests/ combat_lab/` returns zero hits
- [x] Verify: `grep -rn "\.expanded_ships" game/ tests/ combat_lab/` returns zero hits in the deleted-name form (only `BattleUI.expanded_ships` mock setup remains in `test_battle_screen_simulation.py`, which is unrelated to `ShipStatsPanel`)
- [x] Verify: focused suite passes (69/69 in `tests/unit/ui/test_battle_panels*.py` + `tests/fixtures/test_race_setup_ui_builders.py`)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
