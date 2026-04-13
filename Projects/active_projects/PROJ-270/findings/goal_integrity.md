# PROJ-269 + PROJ-270 Goal-Level Integrity Audit

Audit date: 2026-04-12. Verdict is based on code/doc/test evidence as-read,
not on the PROJ checklists' self-reported state. Scope excludes PROJ-271
(flat_shield_bonus, suppressors, Battle Setup toggle mapping) and items
already surfaced by the previous skeptic round (battle_math, unified
entry/exit, test_docs, clean_sheet).

## PROJ-269 Goals

### Goal: Single entry contract — every battle enters via `run_battle(spec: BattleSpec) -> BattleOutcome`
**Verdict:** Mostly met (visual mode is spec-consumed, not run_battle-called)
**Evidence:**
- `game/simulation/battle_runner.py:166` — `run_battle(spec, ai_factory, ship_builder)`.
- Strategy path: `game/strategy/adapters/simulation_adapter.py:135` calls `run_battle(...)`.
- Combat Lab headless: `combat_lab/services/scenario_run_helper.py` + `combat_lab/runner.py` drive `run_battle`.
- Battle Setup / manual / visual: route through `BattleController.start_from_spec` → `start_engine_from_spec` (same materialization path as `run_battle`). Visual-mode is an explicit design decision (decisions.md Decision 3) because `run_battle` is blocking.
- `pytest tests/unit/simulation/test_unified_entry_guard.py` — 16/16 green, enforces no direct `BattleEngine(...)` construction, no `engine.start()` outside whitelist, no `setup(battle_engine)` scenarios, no `engine_ref` closures.
**Gap (if any):** `BattleController.start_from_spec` is a parallel entry surface to `run_battle`, not a consumer. From a "one canonical way" view, there are TWO documented entries (`run_battle` for headless, `start_from_spec` for visual). This is intentional but deserves surfacing in docs.
**Recommended Phase 13+ task:** None warranted — the dual entry is architecturally sound per Decision 3. However `docs/systems/combat_simulation.md` §1 should explicitly document the two entries as a single contract with two drivers (blocking vs per-frame).

### Goal: Fully specified initial/final conditions (BattleSpec / BattleOutcome)
**Verdict:** Met
**Evidence:** `game/simulation/battle_spec.py` + `battle_outcome.py` are frozen dataclasses carrying boundary, end condition, modifier stack, telemetry level, per-team fleet hierarchy, poses, entry vectors, formations (spec) and per-ship poses, per-component HP, survival-annotated hierarchy, weapon totals, hit log, end-reason (outcome). `battle_outcome.py:156` TaskForceOutcome is still a placeholder DTO (only `task_force_id`), but the Phase-1 docstring acknowledges future enrichment.
**Gap:** Minor — `TaskForceOutcome` has no field beyond id; zero consumers. The skeptic round already flagged this as YAGNI scaffolding (finding 16). Not a goal miss because the hierarchy-roll-up was explicitly deferred in PROJ-269 plan.

### Goal: Component-level damage persistence
**Verdict:** Met
**Evidence:** `ShipInstance.components: Dict[component_id, ComponentState]` exists and round-trips through `extract_outcome` into `apply_outcome_to_fleets` (see `game/strategy/data/fleet_battle_adapter.py:193` invoked via PostBattleHook).

### Goal: Formation system, N-team support, Boundary as first-class, Graduated telemetry
**Verdict:** Met — all four are landed with test coverage (`test_battle_engine_n_teams.py`, `test_exit_policy.py`, `test_battle_engine_boundary.py`, `test_ai_n_team_targeting.py`).

### Goal: Kill the mode switch (BattleMode + BattleModeHandler + half-factories deleted)
**Verdict:** Met
**Evidence:** No production hits for `BattleMode`/`BattleModeHandler`/`create_*_battle` in `game/` (only docstring removal notes in docs). Files `battle_factories.py` and `battle_mode_handler.py` deleted in Phase 8.2 of PROJ-270.

### Goal: Engine is context-blind
**Verdict:** Met
**Evidence:** Grep of `game/simulation/systems/battle_engine.py` for `combat_lab|test_lab|battle_setup|TestScenario|isinstance.*Scenario|if mode ==|if scenario` → zero hits. The entire `game/simulation/` subtree has no imports of `combat_lab`, `test_lab`, or `battle_setup`. Engine is genuinely context-blind.

## PROJ-270 Goals

### Goal: Every battle in production enters via `run_battle(spec)` and exits via `BattleOutcome`
**Verdict:** Met (with Decision-3 caveat on visual mode)
**Evidence:** 5 production entry sites verified — `game/app.py:585` (manual), `game/ui/screens/battle_setup_screen.py:1049` (Battle Setup → `build_manual_battle_spec`), `game/strategy/adapters/simulation_adapter.py:190` (strategy), `combat_lab/services/test_execution_service.py:92` (Combat Lab visual), `game/ui/screens/test_lab/screen.py:450` (test lab visual). All five either call `run_battle(spec)` (headless) or `BattleController.start_from_spec(spec)` (visual, which internally calls `start_engine_from_spec`). Zero production callers of `BattleScreen.start(team0, team1)` confirmed (grep yields only docstrings and one test-side regression guard). Acceptance-criteria guard test (`test_unified_entry_guard.py`) passes 16/16.

### Goal: Combat Lab validators consume BattleOutcome rather than live engine
**Verdict:** Met
**Evidence:** All `validate()` methods across `combat_lab/scenarios/*_scenarios.py` use signature `validate(self, outcome, telemetry=None)`. Base class `_run_validation(self, outcome, telemetry=None)` at `combat_lab/scenarios/base.py:561` confirms contract. `engine_ref` closure trick is gone (guard test `TestNoEngineRefClosure` green). Residual `engine.tick_counter` / `engine.projectiles` reads exist only in per-tick `update()` and `per_tick()` callbacks (legitimate forensic telemetry capture, not validators) and in deprecated `TEMPLATE_MIGRATION_GUIDE.md` / `QUICK_START.md` example doc blocks.
**Gap:** `combat_lab/scenarios/QUICK_START.md` still shows `def validate(self, engine) -> list:` stale example at lines 18, 94. Minor doc drift.
**Recommended Phase 13 task:** Update `combat_lab/scenarios/QUICK_START.md` to match the new `validate(self, outcome, telemetry=None)` signature.

### Goal: Visual-mode UI reads from BattleOutcome
**Verdict:** Mostly met
**Evidence:** `BattleScreen._on_battle_ended` (battle_screen.py:453) calls `extract_battle_results(outcome, ...)`. `BattleController.get_outcome()` returns the spec-extracted outcome. `extract_battle_results` module `game/ui/screens/battle_results_data.py` does not import BattleEngine.
**Gap:** `BattleScreen._build_fallback_outcome` (lines 496–550) still synthesizes a fake outcome with `seed=0` / hardcoded `end_reason` for the legacy `BattleScreen.start(team0, team1)` test-convenience path. Docstring claims "71 test callers" — I verified ZERO callers actually exist today (grep `tests/` for `battle_screen.start(` or `BattleScreen().start(` with team args finds nothing). The fallback is live but unreachable.
**Recommended Phase 13 task:** Delete `BattleScreen._build_fallback_outcome`, `_get_or_build_outcome`'s fallback branch, and `BattleController.configure(..., spec=None)` support. The "71 test callers" claim in the docstring is factually wrong — no test exercises this path today.

### Goal: Strategic modifiers apply to battle math (storm / shield_mult / damage_mult, Track A)
**Verdict:** Met
**Evidence:** `game/strategy/combat/spec_compiler.py:374` emits `stat_key="shield_capacity_mult"` for storm interference; lines 406/418 emit `shield_capacity_mult` and `damage_mult` for fleet multipliers. Phase 9 delivered the `FleetAuraManager._apply_bonuses` → `ship.external_stats` → `Ability.get_effective_stat` bridge. 42 strategy-modifier tests pass. Track B (`flat_shield_bonus`, suppressors) correctly deferred to PROJ-271 per Decision 2, spec_compiler.py:423 comment.

### Goal: Legacy-compatible / retained-for dead code eradicated
**Verdict:** Mostly met
**Evidence:** `TestNoLegacyCompatibleComments` guard green. Stub modules `battle_factories.py` and `battle_mode_handler.py` deleted. `BattleMode`, `BattleModeHandler`, `create_*_battle` factories, `update_from_battle_results` all gone.
**Gap:**
1. `AIPolicy` is a zero-field `pass` dataclass (battle_spec.py:67) with zero attribute reads — textbook YAGNI. Skeptic round flagged this; Phase 12 documented it as "retained scaffolding." Per Rule 3 / CLAUDE.md System Migration Policy, scaffolding-without-fields is clean-sheet wrong.
2. `TaskForceOutcome` (battle_outcome.py:156) — one-field placeholder DTO, zero consumers.
3. `BattleController.configure(config, spec=None)` retains optional-spec path solely for non-existent legacy callers.
4. `ComponentStateSpec.is_active` — skeptic finding 18 (half-wired: read path exists, write path broken). Phase 12 deferred.
5. `UnboundedRegion.closest_edge_point` raises rather than being a type-model split — skeptic finding 17.
**Recommended Phase 13 task:**
- Delete `AIPolicy` (zero-field). Delete `TaskForceOutcome` (placeholder). Delete `BattleController.configure(spec=None)` branch + `_build_fallback_outcome`. Fix or remove `ComponentStateSpec.is_active`. Split `BoundaryRegion` into `Region` / `BoundedRegion` protocols so `UnboundedRegion` doesn't need a raising method. Phase 12 of PROJ-270 explicitly scope-trimmed these — they are residual goal-miss items.

### Goal: Acceptance-criteria grep audit runs as pytest guard
**Verdict:** Met
**Evidence:** `tests/unit/simulation/test_unified_entry_guard.py` — 16 tests covering all 5 acceptance criteria (a–e) plus behavioral strategy-compiler tests, green.

### Goal: Test coverage backfills genuine gaps
**Verdict:** Met
**Evidence:** `test_outcome_emission.py` (4 tests), `test_apply_outcome_to_fleets_invalidates_stats_cache`, 16-test `test_battle_config.py` forbidden-field guard, `test_template_no_legacy_setup.py`, `TestCircleBoundaryOriginConvention`, `TestRectBoundaryCenterDeterminism`, `TestNoDirectEngineTickLoop`, behavioral strategy-compiler tests. Phase 7.3 self-flagged as low-ROI defer.

### Goal: Docs updated — `01_ARCHITECTURE.md`, `02_PATTERNS.md`, `combat_simulation.md` reflect unified flow
**Verdict:** Mostly met
**Evidence:** All three docs describe `run_battle(spec)` + spec compiler pattern; only historical/deletion references to `BattleMode` / `BattleModeHandler` remain.
**Gap:** `combat_lab/scenarios/QUICK_START.md` + `combat_lab/scenarios/TEMPLATE_MIGRATION_GUIDE.md` + `docs/guides/simulation_testing.md` carry stale `validate(self, engine)` examples. The skeptic round flagged simulation_testing.md — it was fixed. QUICK_START.md and TEMPLATE_MIGRATION_GUIDE.md were not swept. TEMPLATE_MIGRATION_GUIDE.md's banner marks it "historical"; QUICK_START.md has no such marker and is linked from README.
**Recommended Phase 13 task:** Sweep `combat_lab/scenarios/QUICK_START.md` to match current `validate(outcome, telemetry)` contract, or explicitly mark it historical.

## Summary

- Goals genuinely met: **10** of 14 (PROJ-269 goals 1–6 except single-entry caveat; PROJ-270 goals 1, 3, 4, 7)
- Goals mostly met (acceptable, minor gaps): **3** (single-entry contract, visual-mode outcome, docs updated)
- Goals with material gaps → new PROJ-270 Phase 13 recommended: **1** (legacy-eradicated — AIPolicy/TaskForceOutcome/fallback synthesizer/is_active/UnboundedRegion type-split)
- Goals properly scoped out to PROJ-271: **2** (Track B battle math: flat_shield_bonus + suppressors; Battle Setup complex-toggle content mapping)

### Recommended Phase 13 (single consolidated cleanup phase)

1. **Delete zero-field scaffolding:** `AIPolicy`, `TaskForceOutcome`, `BattleController.configure(spec=None)`, `_build_fallback_outcome`, `_get_or_build_outcome` fallback branch. Verify the "71 test callers" claim — grep shows zero; if confirmed, the docstring itself is misinformation that justifies the feature.
2. **Fix or delete `ComponentStateSpec.is_active`** half-wired write-path (skeptic finding 18).
3. **Type-model split `BoundaryRegion`** — introduce `Region` / `BoundedRegion` protocols so `UnboundedRegion.closest_edge_point` doesn't need to raise (skeptic finding 17).
4. **Doc sweep:** `combat_lab/scenarios/QUICK_START.md` validator examples; explicit "two entries, one contract" note in `docs/systems/combat_simulation.md` §1.

None of these are large; together they are <1 day of work. After this Phase 13, both PROJ-269 and PROJ-270 can genuinely be archived against their stated goals.
