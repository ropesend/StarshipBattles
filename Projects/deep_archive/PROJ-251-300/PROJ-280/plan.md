# PROJ-280: Combat Lab Template Deduplication + Authoring Rules

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-280` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-280 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Audit duplication across the 5 templates | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract shared helpers into TestScenario base | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Add base-class enforcement (runtime sentinel) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate the 5 templates to use the helpers | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Author guidelines doc + new-template checklist | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Awaiting archival
**Last Action:** All 5 phases complete. Phase 1 audit delegated to Explore agent (zero main-agent context cost). Phase 2 added 3 helpers to `TestScenario` base. Phase 3 wired runtime sentinel into `_run_validation`. Phase 4 migrated 5 templates (10 method changes). Phase 5 added 80-line authoring-rules doc. Final regression: 3627 PROJ-280 scope + 162 Combat Lab simulation, all green.
**Next Action:** Archive via `python Projects/scripts/archive_project.py PROJ-280 --force`
**Blockers:** None

---

## Closure Summary

### Project arc (2026-04-18)
- **Goal achieved:** Extracted shared template boilerplate into `TestScenario` base helpers. Added runtime sentinel that refuses to silently drop the universal "Simulation Ran" precondition if a future template forgets to call the base. Documented authoring rules.
- **5 phases, all complete and validated.**

### What shipped

**Base-class additions** ([combat_lab/scenarios/base.py](../../../combat_lab/scenarios/base.py)):
- `_common_preconditions() -> List[Check]` — universal "ticks > 0" assertion; sets `_preconditions_base_called` sentinel
- `_template_preconditions() -> List[Check]` — default returns `_common_preconditions()`
- `_snapshot_initial_state(ships_by_role, initial_state) -> None` — base no-op hook
- `_run_validation()` enforcement: resets sentinel before `validate()`, raises `RuntimeError` if subclass override forgot to call base

**Template migrations** ([combat_lab/scenarios/templates.py](../../../combat_lab/scenarios/templates.py)):
- All 5 templates' `_template_preconditions` call `_common_preconditions()`:
  - Static/Duel/Resource: simple delegation
  - Propulsion: `checks = self._common_preconditions()` + conditional movement/rotation
  - Comparison: `checks = self._common_preconditions()` + existing A/B validation
- All 5 templates' `wire_ships` split into `_snapshot_initial_state(...)` + template-specific policy assignment

**Docs** ([docs/guides/simulation_testing.md](../../../docs/guides/simulation_testing.md)):
- New §2.4 "Template Authoring Rules (PROJ-280)":
  - 2.4.1: `_template_preconditions` must include `_common_preconditions` (canonical + extension patterns + enforcement details)
  - 2.4.2: `wire_ships` should use `_snapshot_initial_state` (canonical pattern)
  - 2.4.3: Anti-rebloat checklist for new templates (5 items)

**Test fix:**
- [tests/unit/combat_lab/test_comparison_visual_baseline.py](../../../tests/unit/combat_lab/test_comparison_visual_baseline.py): `_make_scenario` populates `results['ticks_run'] = 10` so new universal check passes when tests bypass `collect_results`

### Tests (final)
- **PROJ-280 scope:** 3627 passed
- **Combat Lab simulation:** 162 passed / 0 failed / 0 skipped

### Key design decisions
- **Phase 1 delegated to Explore agent** — protected main-agent context entirely; audit of 5 templates × ~200 lines each would have been heavy
- **Option B runtime sentinel** (not AST inspection, not composition API): zero invasiveness, first-run detection, clear failure message
- **`_template_preconditions` default calls `_common_preconditions`**: subclasses that don't override get base behavior free; enforcement only applies when they DO override — avoids false positives
- **`_snapshot_initial_state` is OPT-IN**: 2 concrete overrides that bypass template wire_ships (`ExternalBattleConditionApplied`, `PropThrustMassRatioScenario`) remain unaffected
- **ComparisonScenario redundantly includes `_common_preconditions`**: makes sentinel contract uniform across all 5 templates

### Future opportunities (NOT in scope for PROJ-280)
1. **Update hook extraction:** `update()` in most templates just calls `self._track_tick()`. Modest savings, deferred.
2. **Declarative preconditions:** PropulsionScenario's conditional checks could be class attrs rather than imperative code. Out of scope.

## Overview
The 5 canonical templates in [combat_lab/scenarios/templates.py](../../../combat_lab/scenarios/templates.py) (StaticTargetScenario, PropulsionScenario, ResourceScenario, DuelScenario, ComparisonScenario) carry near-identical `_template_preconditions()` and `wire_ships()` boilerplate. Extract the shared shape into `TestScenario` base class so each template overrides only what genuinely differs. Add base-class enforcement (e.g. methods that raise if subclass forgets to call super) so templates can't drift back into duplication. Document authoring rules so new templates land cleanly.

## Goals
- Each template implementation is shorter and clearer — only template-specific logic remains
- Boilerplate (initial state snapshot, weapon stat collection, common preconditions) lives in one place
- Base class actively prevents drift via runtime checks (e.g. `__init_subclass__` validation, mandatory super() calls, or abstract-method enforcement)
- Documented rules in [docs/guides/simulation_testing.md](../../../docs/guides/simulation_testing.md) for adding new templates
- New-template checklist makes it impossible to ship a template that re-bloats the duplication

## Scope
**In:**
- Audit and quantify duplication across the 5 templates (line-by-line comparison)
- Extract shared `_template_preconditions()` body into base
- Extract shared `wire_ships()` boilerplate (initial state snapshot, weapon stat collection) into base
- Add `__init_subclass__` or similar enforcement to catch templates that skip the base setup
- Migrate all 5 templates to the new base
- Add doc section "Authoring a new TestScenario template" to [docs/guides/simulation_testing.md](../../../docs/guides/simulation_testing.md)
- Add a new-template checklist (probably as a comment block at the top of [combat_lab/scenarios/templates.py](../../../combat_lab/scenarios/templates.py) and in the doc)
- Tests covering the base-class enforcement (a malformed subclass that skips required super() should fail loudly)

**Out:**
- Adding new templates (this is consolidation, not expansion)
- Refactoring scenarios (the concrete classes that USE templates) — those keep their per-test logic
- Anything outside `combat_lab/scenarios/`

## Key Files
| Component | File Path |
|-----------|-----------|
| TestScenario base | `combat_lab/scenarios/base.py` |
| All 5 templates | `combat_lab/scenarios/templates.py` |
| Concrete scenarios using templates | `combat_lab/scenarios/*_scenarios.py` (~30 files) |
| Authoring guide | `docs/guides/simulation_testing.md` |

## Decisions Log
See [decisions.md](decisions.md) for full rationale.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Approach: Authoring rules + base-class enforcement | User chose "Authoring rules + base-class enforcement (Recommended)". Hard guardrails prevent re-drift. Doc-only would rely on author discipline; light enforcement leaves no signal when drift occurs |
| 2026-04-17 | Sequencing: AFTER PROJ-279 | PROJ-279 simplifies TestScenario base (removes the `to_spec` stub). Working with the cleaner base avoids touching the same code twice |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Combat Lab full suite passes (`python -m combat_lab.run_tests --fast`)
- [ ] Audit passed (no template re-introduces duplicated boilerplate)
- [ ] User verified
