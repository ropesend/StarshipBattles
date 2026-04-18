# PROJ-279: Combat Lab Spec Compiler — Explicit Composition (delete to_spec monkey-patch)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-279` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-279 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Audit & migrate all `scenario.to_spec()` callers to `build_test_battle_spec(scenario)` | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Delete the monkey-patch in `combat_lab/spec_compiler.py` | Not Started | TBD |
| 3. Documentation update | Not Started | TBD |

## Current State
**Last Updated:** 2026-04-17
**Active Phase:** Planning (awaiting user approval)
**Last Action:** Project shell created with agreed scope
**Next Action:** User approval, then Phase B deep-dive swarm review and detailed task breakdown
**Blockers:** **PROJ-278 must complete first** — that project changes the Combat Lab role-tagging story (`scenario_role` field on ShipSpec) which both the compiler AND any updated callers will use. Sequencing this AFTER PROJ-278 prevents two churns of the compiler

## Overview
Delete the module-import-time monkey-patch at the bottom of [combat_lab/spec_compiler.py:474](../../../combat_lab/spec_compiler.py#L474) that attaches `to_spec()` to `TestScenario`. Replace it with explicit calls to `build_test_battle_spec(scenario, registries)` everywhere `scenario.to_spec()` is currently used. Brings Combat Lab in line with how Battle Setup already works (no `to_spec` on `BattleSetupState` — the compiler is called explicitly).

## Goals
- Zero `setattr` / monkey-patch attached to `TestScenario` at module import time
- All callers explicitly import and call `build_test_battle_spec`
- IDE jump-to-definition works for the compiler call from any caller
- Easier to discover for new contributors reading scenario code
- Tests cannot accidentally shadow or stub `to_spec` in confusing ways

## Scope
**In:**
- Audit every caller of `scenario.to_spec()` (production + tests)
- Replace each with `build_test_battle_spec(scenario, registries)` — explicit import where needed
- Delete the monkey-patch block at [combat_lab/spec_compiler.py:474](../../../combat_lab/spec_compiler.py#L474)
- Update [combat_lab/scenarios/base.py](../../../combat_lab/scenarios/base.py) to remove the `to_spec()` stub method (currently a placeholder before the monkey-patch overwrites it)
- Update Combat Lab documentation: [combat_lab/README.md](../../../combat_lab/README.md), [combat_lab/COMBAT_LAB_DOCUMENTATION.md](../../../combat_lab/COMBAT_LAB_DOCUMENTATION.md), [docs/guides/simulation_testing.md](../../../docs/guides/simulation_testing.md)
- Add an authoring rule: "scenarios must not have `to_spec` — call `build_test_battle_spec(scenario)` explicitly"

**Out:**
- Any change to the compiler's internal logic (template dispatch, ship loading, etc.)
- Any change to `TestScenario` base class beyond removing the `to_spec` stub
- Any reorganization of compiler files

## Key Files
| Component | File Path |
|-----------|-----------|
| Monkey-patch source | `combat_lab/spec_compiler.py` (line ~474) |
| TestScenario base (has `to_spec` stub) | `combat_lab/scenarios/base.py` |
| TestRunner (likely caller) | `combat_lab/runner.py` |
| Visual run service (likely caller) | `combat_lab/services/test_execution_service.py` |
| AB battle runner (likely caller) | `combat_lab/services/ab_battle_runner.py` |
| Combat Lab UI screen | `game/ui/screens/test_lab/screen.py` |
| Documentation | `combat_lab/README.md`, `docs/guides/simulation_testing.md` |

## Decisions Log
See [decisions.md](decisions.md) for full rationale.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Approach: delete `to_spec` entirely (Option A, not late-import method or DI) | User chose "Delete to_spec entirely (Recommended)". Scenarios should describe a setup; spec construction is the runner's responsibility. Matches Battle Setup pattern (BattleSetupState has no to_spec) |
| 2026-04-17 | Sequencing: AFTER PROJ-278 | PROJ-278 changes the role-tagging shape on ShipSpec. Doing this project first means we'd touch the same file twice and risk merge churn |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed (grep for `to_spec` returns no Combat Lab production hits)
- [ ] User verified
