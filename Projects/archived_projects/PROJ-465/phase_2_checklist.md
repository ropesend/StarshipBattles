# Phase 2: Codex-Audit Remediation

**Status:** Complete
**Revision Reason:** A one-round Codex audit of the Phase 1 implementation
(`AgentCoordination/Scratchpad/Consult/proj465_audit/audit.md.invalid-output-*.txt`)
found NO code regressions but raised 3 process/coverage findings. Each was
verified against live code and classified.

> Determinism check: Codex independently confirmed Cluster 8 (battle launch),
> DUP-X-5 (serialization), and the absence of any accidental Cluster 2 change
> are behaviour-preserving. No RNG/ordering/payload regressions found.

---

## Verified findings + remediation

### Task 2.1: Characterize the satellite half of Cluster 19's shared helper [Simple] — VERIFIED
**File:** `tests/unit/simulation/entities/stat_contributors/test_launch.py`
**Finding (Codex #2, Medium):** the shared `_contribute_launch` made the
satellite path string-parameterized, but no test asserted the satellite field
set (`satellite_capacity`, `satellites_per_wave`, `satellite_launch_cycle`,
`satellite_launch_rate_tons_per_sec`). Fighter side was covered; satellite side
was not.

- [x] Added `TestAggregateSatelliteHangar` (5 tests) mirroring the fighter
  coverage: no-op gating, single-bay population, sum/max aggregation across
  components, storage-without-launch ignored, and fighter/satellite path
  independence.
- [x] Verify: `pytest tests/unit/simulation/entities/stat_contributors/test_launch.py` -> 10 passed.

**Notes:** Tests pass against the post-refactor code (they pin current
behaviour — the refactor was already behaviour-preserving, this just closes the
characterization gap the decision log implied existed).

### Task 2.2: Reconcile project artifacts with what actually landed [Simple] — VERIFIED
**File:** `Projects/active_projects/PROJ-465/{plan.md, phase_1_checklist.md}`
**Finding (Codex #1, Major):** plan.md still said "Not Started"; implemented
task blocks were unchecked; the DUP-X-5 checklist text described a
`_populate_ships_from_payload`/MineGroup approach not actually used.

- [x] Updated plan.md Quick Status + Current State to reflect 7 implemented /
  10 deferred and the audit remediation.
- [x] Checked off + annotated the implemented Phase 1 task blocks
  (DUP-X-1, DUP-X-7, DUP-X-5) and corrected the DUP-X-5 description to the
  shared-`_from_dict_payload` approach actually used (MineGroup excluded).

**Notes:** decisions.md already carried the full implemented/deferred record;
this task aligned the plan/checklist views with it.

### Task 2.3: Codex finding #3 (untracked test file) — REJECTED (not a defect)
**Finding (Codex #3, Medium):** `tests/unit/ui/screens/test_dismissable_dialog.py`
is untracked, so it is absent from `git diff HEAD`.

- [x] Classified REJECTED: this is expected. Per the project ground rules the
  orchestrator commits (this agent does not commit). The file exists, passes,
  and will be included when the orchestrator stages the change. No code or test
  defect.

---

## Phase Completion Checklist
- [x] All VERIFIED findings remediated (2.1, 2.2)
- [x] REJECTED finding documented with rationale (2.3)
- [x] Combat + strategy validation re-run green after remediation
