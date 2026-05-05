# PROJ-335 — Strategy data layer batch (characterization tests)

**Project:** PROJ-335
**Arc:** Test-coverage projects PROJ-331..340 (master at `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md`)
**Risk tier:** MED
**Mode:** Characterization-only (no TDD, no bugfixes, no refactors)
**Reference shape:** `Projects/active_projects/PROJ-329A/`
**Estimated sessions:** ~0.5

---

## Quick Status

| Phase | Name | State |
|---|---|---|
| 1 | Characterization tests for 5 strategy data files | Not started |

---

## Goals

Pin current behavior of five small data-model files in `game/strategy/data/`:

- `planetary_facility.py`
- `species_population.py`
- `squadron.py`
- `order_types.py`
- `group_policy_registry.py`

Capture the present semantics — including any apparent quirks (e.g. asymmetric
serialization branches) — as executable assertions. **Do not fix bugs**;
record them as observations in `decisions.md`.

Avoid duplicating existing coverage. Several of the in-scope files already have
partial test files under `tests/unit/strategy/data/`; Phase 1 begins with a
verify-existing-coverage micro-task.

---

## Scope

### IN

- 4–5 new test files under `tests/unit/strategy/data/` named
  `test_<file>_characterization.py` (one per production file, possibly
  skipping `species_population` if existing class is complete).
- Behavior pins drawn from the per-file behavior list in `phase_1_checklist.md`
  (~30–45 new tests total, midpoint ~38).
- Per-file commit discipline.

### OUT

- Refactors of any production file in scope.
- Bug fixes (including any quirks discovered — log only).
- New mocks or fixtures beyond `types.SimpleNamespace` stubs and existing
  `tests/fixtures/` utilities.
- Tests for parent class `FleetHierarchyNode` (covered elsewhere) or sibling
  `task_force.py` (out of scope).
- Tests that require importing real `Planet` / `Fleet` objects — use stubs.

---

## Success Criteria

- All new tests pass when run in isolation.
- Full sharded suite green: `python Tools/test_sharded/test_sharded.py`.
- Lint clean on all touched files.
- Per-file commits, each containing the production file (read-only) and its
  paired test file.
- `decisions.md` records any observed quirks as observations, not action items.

---

## Source Documents

- `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md` — arc master plan (PROJ-331..340).
- `C:\Users\rossr\.claude\plans\noble-stirring-galaxy-agent-ab4633efcf5dfbb98.md` — pre-flight findings and per-file behavior matrix used to populate this plan.
- `AGENTS.md` — testing philosophy, characterization-mode discipline, the 500-LOC ceiling.
- `Projects/active_projects/PROJ-329A/` — reference shape.
