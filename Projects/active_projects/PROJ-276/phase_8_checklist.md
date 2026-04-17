# Phase 8: Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 8`

**Status:** Not Started
**Objective:** Update docs to reflect `components` as sole source of truth. Remove `component_damage` references.

---

## Tasks

### Task 8.1: Update `strategy_layer.md` [Medium]
**File:** `docs/systems/strategy_layer.md`
**Tests:** Manual review

- [ ] Find sections referencing `component_damage` as "authoritative legacy" or "transitional"
- [ ] Rewrite: `ShipInstance.components` is the authoritative per-instance HP store. Key format `{component_id}#{instance_index}`. Stat calculation, bridge, and serialization all read it.
- [ ] Remove any "PROJ-269 transition" phrasing — replace with "Closed in PROJ-276"

**Notes:**

### Task 8.2: Update `04_SERVICES.md` [Simple]
**File:** `docs/04_SERVICES.md`
**Tests:** Manual review

- [ ] Update `ShipStatsCalculator` doc — if it mentioned `component_damage`, replace with `components`
- [ ] Verify the service list is current

**Notes:**

### Task 8.3: Update `combat_simulation.md` [Simple]
**File:** `docs/systems/combat_simulation.md`
**Tests:** Manual review

- [ ] Find the PROJ-269 Phase 2 discussion around L220-255
- [ ] Add a note: "PROJ-269 Phase 2 closed by PROJ-276. Legacy `component_damage` field removed."
- [ ] Update any references to "dual-tracking" or "legacy field coexists" — those are now inaccurate

**Notes:**

### Task 8.4: Full-repo docs sweep [Simple]
**File:** N/A
**Tests:** Grep

- [ ] Run `grep -rn "component_damage" docs/` — every remaining result reviewed and fixed or removed
- [ ] Run `grep -rn "component_damage" CLAUDE.md` — if present, update
- [ ] Archived project references (Projects/archived_projects/) — leave alone; historical record

**Notes:**

### Task 8.5: Memory update [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md`
**Tests:** Manual

- [ ] Add: "PROJ-276 eradicated `ShipInstance.component_damage` (legacy single-instance lossy dict); `components: Dict[str, ComponentState]` is sole source of truth; PROJ-269 Phase 2 now closed"
- [ ] Remove any stale references to dual-tracking

**Notes:**

### Task 8.6: Final regression sweep [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py` + `python -m combat_lab.run_tests`

- [ ] Full pytest suite green
- [ ] Combat Lab suite green
- [ ] Perf regression check — `pytest tests/performance/ -n 1`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md — mark project COMPLETE
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-276 8`
- [ ] User verification: manual multi-instance damage scenario (3-seeker ship, partial damage, save/reload)
