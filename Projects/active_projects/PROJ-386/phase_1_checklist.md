# Phase 1: Delete save-format migration code (banned by CLAUDE.md Rule 3)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-386 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete 4 save-format migration code blocks across 4 files. **CLAUDE.md Rule 3 ("Root Cause Fixes — No save-file migration. Old saves are disposable.") prohibits these in-place fixes; they are non-negotiable deletions.**

---

## Tasks

### Task 1.1: Delete `_complex_toggles` legacy migration
**File:** `game/ui/screens/battle_setup/controller.py`
**Tests:** `pytest tests/ -k battle_setup`

- [ ] Delete `_complex_toggles` legacy migration code at lines 548-568 in `_load_from_path` (LEG-03-008) [banned by CLAUDE.md Rule 3]
- [ ] Verify: file no longer references `_complex_toggles` top-level key

### Task 1.2: Delete `{'active': bool}` old-format branch
**File:** `game/strategy/data/component_activation_state.py`
**Tests:** `pytest tests/ -k component_activation`

- [ ] Delete legacy-format branch at lines 144-149 of `from_dict` (the `if 'phase' not in data` branch handling `{'active': bool}`) (LEG-03-017) [banned by CLAUDE.md Rule 3]
- [ ] Verify: `from_dict` requires `phase` field unconditionally

### Task 1.3: Delete silent-ignore + graceful-degrade compat paths
**File:** `game/strategy/data/ship_instance_serializer.py`
**Tests:** `pytest tests/ -k ship_instance`

- [ ] Delete silent-ignore branch for legacy `component_damage` key at lines 100-102 (LEG-03-018) [banned by CLAUDE.md Rule 3]
- [ ] Delete graceful-degrade branch for missing `components` key at lines 127-138 (LEG-03-018) [banned by CLAUDE.md Rule 3]
- [ ] Verify: deserialization raises if either field is missing/legacy

### Task 1.4: Delete `side_0`/`side_1` legacy emit + read
**File:** `game/ui/screens/battle_setup_state.py`
**Tests:** `pytest tests/ -k battle_setup_state`

- [ ] Delete legacy `side_0`/`side_1` emit at lines 265-269 in `to_dict()` (LEG-04-005) [banned by CLAUDE.md Rule 3]
- [ ] Delete legacy fallback read at lines 290-300 in `from_dict()` (LEG-04-005) [banned by CLAUDE.md Rule 3]
- [ ] Verify: `to_dict()` only emits `sides` list; `from_dict()` only reads `sides` list

### Task 1.5: Final regression
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite — confirm baseline preserved
- [ ] Verify: pytest passes; `grep -rn -E "(_complex_toggles|side_0|side_1|component_damage)" game/` shows no remaining legacy-format handling
- [ ] Verify: any tests that fed legacy save fixtures into deserialization either pass (because they migrated) or are deleted (because they tested only the legacy path)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
