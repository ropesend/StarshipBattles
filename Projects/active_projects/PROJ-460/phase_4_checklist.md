# Phase 4: Document the 10 remaining over-ceiling simulation files as next-touch

**Status:** Not Started
**Depends on:** Phase 3 complete
**Review Mode:** lightweight (docs only; no code touched)
**Files:**
- `Projects/active_projects/PROJ-460/decisions.md` (docs; add 10 next-touch entries)
- `Projects/active_projects/PROJ-460/findings/PROJ-460_findings.md` (docs; finalize F-D-011 status)

**Objective:** Discipline phase. Document the 10 OTHER over-ceiling simulation files (the F-D-011 residue) as next-touch entries — explicitly not addressed in this project. **No code changes.**

**Codex r4 risk callout:** "If Job 12 absorbs the other 10 F-D-011 files, you are back to a jumbled structural omnibus." This phase is what keeps the project's scope from creeping.

---

## Tasks

### Task 4.1: Re-measure the 10 next-touch files [Simple]

```powershell
$files = @(
  'game/simulation/systems/battle_engine.py',
  'game/simulation/battle_runner.py',
  'game/simulation/entities/ship.py',
  'game/simulation/systems/tactical_mine_resolver.py',
  'game/simulation/entities/stat_contributors/registry.py',
  'game/simulation/entities/ship_stats.py',
  'game/simulation/components/abilities/base.py',
  'game/simulation/systems/battle_end_conditions.py',
  'game/simulation/services/vehicle_design_service.py',
  'game/simulation/combat/fleet_aura_manager.py'
)
foreach ($f in $files) { '{0,5}  {1}' -f (Get-Content $f | Measure-Object -Line).Lines, $f }
```

- [ ] Record the current LOC. Compare against the 2026-05-19 baseline (in `plan.md` "Out of Scope" table). Drift is expected if any phases touched call sites incidentally.
- [ ] Note if any file dropped below 500 LOC — possibly Phase 1 / Phase 2 / Phase 3 changes propagated. If so, document the drop and remove that file from the next-touch list.

### Task 4.2: Add 10 next-touch entries to `decisions.md` [Simple]

**File:** `Projects/active_projects/PROJ-460/decisions.md`

- [ ] Append the following entries (one per remaining over-ceiling file):

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-MM-DD | `battle_engine.py` next-touch (758 LOC) | Core tick-loop orchestrator; no clean cut identified in PROJ-460 scope; revisit on next touch. |
| 2026-MM-DD | `battle_runner.py` next-touch (735 LOC) | Headless run entry point; tight coupling to engine + outcome extraction; no clean cut identified; revisit on next touch. |
| 2026-MM-DD | `ship.py` next-touch (607 LOC) | Facade over many delegates; structural split needs separate analysis; revisit on next touch. |
| 2026-MM-DD | `tactical_mine_resolver.py` next-touch (597 LOC) | Single-responsibility mine resolution; finer-grained resolver split is a separate decision; revisit on next touch. |
| 2026-MM-DD | `stat_contributors/registry.py` next-touch (570 LOC) | Registry pattern with many contributors inline; per-contributor split is a separate project scope; revisit on next touch. |
| 2026-MM-DD | `ship_stats.py` next-touch (559 LOC) | Tight to Ship facade; no obvious internal split; revisit on next touch. |
| 2026-MM-DD | `components/abilities/base.py` next-touch (535 LOC) | Base classes for the ability hierarchy; structural sensitivity high; revisit on next touch. |
| 2026-MM-DD | `battle_end_conditions.py` next-touch (532 LOC) | Multiple end-condition classes in one file; per-class split is a separate decision; revisit on next touch. |
| 2026-MM-DD | `vehicle_design_service.py` next-touch (516 LOC) | Service-level; modest ceiling overage; revisit on next touch. |
| 2026-MM-DD | `combat/fleet_aura_manager.py` next-touch (515 LOC) | Aura manager with mixed responsibilities; needs separate scope analysis; revisit on next touch. |

- [ ] Update LOC numbers from Task 4.1 if drift occurred.
- [ ] Replace `2026-MM-DD` with today's actual date.

### Task 4.3: Finalize F-D-011 status in findings [Simple]

**File:** `Projects/active_projects/PROJ-460/findings/PROJ-460_findings.md`

- [ ] Update the F-D-011 entry's "Status as of 2026-05-19" section to note final disposition:
  - "Actionable slice closed in PROJ-460: battle_state.py Phase 1, battle_controller.py Phase 2, replay_serialization.py Phase 3."
  - "10 next-touch files documented in `decisions.md` per Codex r4 discipline rule. Each carries a one-line entry with current LOC and rationale for not splitting in this project."
  - "Any future work on any of these 10 files should be a separate scope decision driven by the next touch on that file."

### Task 4.4: Verify discipline [Simple]

- [ ] Confirm NO production code changes happened in Phase 4. `git status --short` should show only `decisions.md` and `findings/PROJ-460_findings.md`.
- [ ] If anything else is modified: stop. Review whether the change actually belongs in Phase 4 or is scope creep that should be in a separate project.

### Task 4.5: Commit [Simple]

- [ ] Commit message: `PROJ-460 Phase 4: document 10 over-ceiling simulation files as next-touch (Codex r4 discipline rule)`
- [ ] Update `plan.md` Current State to: "All phases complete; ready for verification."

---

## Phase Completion Checklist
- [ ] 10 next-touch entries added to `decisions.md` with current LOC values
- [ ] F-D-011 status finalized in `findings/PROJ-460_findings.md`
- [ ] No production code touched in Phase 4
- [ ] Sharded suite green (from Phase 3; no new code in Phase 4)
- [ ] `plan.md` Current State updated to "All phases complete"
