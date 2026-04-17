# PROJ-277: First-Class A/B Comparison Runner

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-277` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-277 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Design A/B runner + DTO + failing tests | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Implement ABBattleRunner | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Refactor ComparisonScenario | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Update scenario_run_helper dispatch | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Migrate existing comparison tests | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Docs | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-04-16
**Active Phase:** Planning (ready to start Phase 1)
**Last Action:** Project created with full plan
**Next Action:** Begin Phase 1 — design A/B runner API, write failing tests
**Blockers:** None (independent of other combat-review projects)
**Context for Next Agent:** Today `ComparisonScenario` (`combat_lab/scenarios/templates.py:827-920`) calls `run_battle()` from within its own `before_run_battle()` method to produce a "baseline" run, then stashes results on `self._baseline_*` attributes. This inverts orchestration: scenarios should be INPUT to a runner, not callers of it. Consequences: telemetry role-remapping hack (`"baseline_attacker"` vs `"attacker"` at L915-920); `_run_validation()` override at L1120-1166 skips `validate()` in visual-baseline mode — a silent contract violation. This project makes A/B a first-class orchestration pattern.

## Overview

Refactor `ComparisonScenario` into a first-class A/B runner service. A new `ABBattleRunner` takes two `BattleSpec`s (baseline + variant), runs both, and hands both outcomes + telemetry to a single `validate()` call. Eliminates the `_baseline_*` stashing, telemetry role-remapping, and visual-baseline validate bypass.

## Goals

- New service: `ABBattleRunner` in `combat_lab/services/`.
- New DTO: `ABBattleOutcome` carrying `(baseline: BattleOutcome, variant: BattleOutcome, baseline_telemetry, variant_telemetry)`.
- `ComparisonScenario` no longer calls `run_battle()` directly.
- Telemetry role naming unified (no baseline-prefix remapping).
- `validate()` runs in both normal and visual-baseline modes — no silent bypass.
- `ComparisonScenario.before_run_battle()` (if retained) returns only spec modifications, not battle results.

## Scope

**In:**
- New: `combat_lab/services/ab_battle_runner.py`
- New: `combat_lab/scenarios/ab_outcome.py` — `ABBattleOutcome` DTO
- Refactor: `combat_lab/scenarios/templates.py::ComparisonScenario` (L827-920, L1120-1166)
- Delete: `_run_baseline_battle()` method (L827) and `_run_validation()` override (L1120) — unified back into base contract
- Migrate all existing ComparisonScenario-derived tests
- Docs: `docs/guides/simulation_testing.md` section on A/B scenarios

**Out:**
- Refactoring non-comparison scenarios
- Changes to `run_battle` or `BattleSpec`
- Changes to PROJ-274's ship_materializer story (ComparisonScenario's role-tracking ship_builder is refactored here — its materialization doesn't need PROJ-274 integration)

## Key Files

| Component | File Path |
|-----------|-----------|
| New A/B runner | `combat_lab/services/ab_battle_runner.py` |
| New A/B outcome DTO | `combat_lab/scenarios/ab_outcome.py` |
| Comparison template | `combat_lab/scenarios/templates.py` |
| Run helper | `combat_lab/services/scenario_run_helper.py` |
| Existing comparison scenarios | `combat_lab/scenarios/*_scenarios.py` (ComparisonScenario subclasses — enumerate in Phase 5) |
| Docs | `docs/guides/simulation_testing.md` |

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [manifest.md](manifest.md)

## Verification
- [ ] All phase checklists complete
- [ ] All ComparisonScenario-derived tests pass with new `ABBattleOutcome` signature
- [ ] `python -m combat_lab.run_tests` — full Combat Lab suite green
- [ ] Visual-baseline mode: launch any ComparisonScenario in Combat Lab UI with `--visual-baseline`; verify `validate()` actually runs
- [ ] Full suite: `python Tools/test_sharded/test_sharded.py`
- [ ] Audit passed
- [ ] User verified
