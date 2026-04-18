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
| 1. Design A/B runner + DTO + failing tests | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Implement ABBattleRunner | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Refactor ComparisonScenario | Partial (validate signature migrated; deletion waits on Phase 4) | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Update scenario_run_helper dispatch | Deferred to follow-up | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Migrate existing comparison tests | Mostly Complete (validate-signature migrated; attribute cleanup in Phase 4) | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Docs | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-04-17
**Active Phase:** Phases 1, 2, 3 (partial), 5 (mostly), 6 complete. Phase 4 DEFERRED as follow-up.
**Last Action:** Phase 6 done. Updated `docs/guides/simulation_testing.md` (Pattern 3 + ComparisonScenario engine-decisions section) with `validate(self, ab)` contract + spec hooks. Added memory at `memory/project_proj277_ab_runner.md`. Full suite 14,657 passed (+30 over PROJ-276 baseline); Combat Lab 170 passed.
**Next Action:** Project is at a clean, shippable state. Phase 4 (dispatch flip + scaffolding deletion + `render_mode`) is filed as a follow-up.
**Blockers:** None

### What shipped vs what was deferred

**Shipped (user-facing):**
- `ABBattleRunner` + `ABBattleOutcome` — first-class A/B runner service and DTO.
- `ComparisonScenario.validate(self, ab: ABBattleOutcome)` is the contract. 102 subclasses migrated.
- Additive `build_baseline_spec()` / `build_variant_spec()` hooks available on the base class.
- Telemetry no longer role-remaps for validator access — `ab.baseline_telemetry` / `ab.variant_telemetry` live side-by-side with identical role key spaces.
- `_run_validation` builds `ab` from stashed baseline + current variant; validators never see the stash directly.

**Deferred (architectural cleanup, tracked in Phase 4 checklist + memory):**
- `_run_baseline_battle` + `_build_baseline_battle_spec` scaffolding deletion.
- Runner-driven dispatch (vs scenario-embedded `run_battle` call).
- `render_mode` on `ABBattleRunner` to make visual-baseline rendering orthogonal to validation (Task 3.6).
- `collect_results(ab)` rewrite to read from `ab` directly instead of live `self.target` state.

### Phase 3.1 audit findings (still relevant if Phase 4 is picked up)

102 ComparisonScenario descendants across 21 scenario files; no multi-level chains. Subclass bodies are mostly `self.baseline_*` / `self.variant_*` attribute reads + `check_*` calls — they don't care whether those attrs were populated via `_run_baseline_battle` stash or directly from an `ABBattleOutcome`. Phase 4 flips the population source.
**Context for Next Agent:** Today `ComparisonScenario` (`combat_lab/scenarios/templates.py:827-920`) calls `run_battle()` from within its own `before_run_battle()` method to produce a "baseline" run, then stashes results on `self._baseline_*` attributes. This inverts orchestration: scenarios should be INPUT to a runner, not callers of it. Consequences: telemetry role-remapping hack (`"baseline_attacker"` vs `"attacker"` at L915-920); `_run_validation()` override at L1120-1166 skips `validate()` in visual-baseline mode — a silent contract violation. This project makes A/B a first-class orchestration pattern.

**Phase 2 implementation notes:**
- `_run_one` needs per-tick role-tracking (ships_by_role / in_flight_by_role) to populate `CombatLabTelemetry.in_flight_by_role`. The pattern lives in `combat_lab/services/scenario_run_helper.py:70-115` (`pre_tick_loop` + `per_tick` closures + final `CombatLabTelemetry(...)` construction).
- Decision point for Phase 3: ship_builder currently lives on the scenario. The cleanest cut is for the runner to OWN the role-tracking ship_builder (identical across baseline/variant → roles match), and accept a pass-through scenario hook for any per-scenario customization. But Phase 2 should preserve the current structure — just invoke `run_battle` twice using the ship_builder passed in at construction time.
- Tests already assert: `run_battle` called exactly twice, baseline-first order, identical ai_factory/ship_builder forwarded, distinct telemetry instances, immutable outcome.

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
