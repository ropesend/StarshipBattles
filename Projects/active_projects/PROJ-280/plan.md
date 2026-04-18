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
| 1. Audit duplication across the 5 templates | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract shared helpers into TestScenario base | Not Started | TBD |
| 3. Add base-class enforcement (super() calls / abstract method shape) | Not Started | TBD |
| 4. Migrate the 5 templates to use the helpers | Not Started | TBD |
| 5. Author guidelines doc + new-template checklist | Not Started | TBD |

## Current State
**Last Updated:** 2026-04-17
**Active Phase:** Planning (awaiting user approval)
**Last Action:** Project shell created with agreed scope
**Next Action:** User approval, then Phase B deep-dive swarm review and detailed task breakdown
**Blockers:** Sequenced AFTER PROJ-279. PROJ-279 simplifies the TestScenario surface (removes `to_spec`); doing this project after that means the deduplication targets a cleaner base class

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
