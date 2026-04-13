# PROJ-270 Acceptance Audit

**Date:** 2026-04-12 (revised after skeptic audit)
**Auditor:** Closure session (automated guards + manual trace) — **REVISED by skeptic audit same day**
**Scope:** Walk the 5 acceptance criteria from [decisions.md](../decisions.md) Decision 3 and demonstrate each holds.

---

## ⚠️ REVISION NOTE (2026-04-12)

The original version of this document marked all 5 criteria as ✓ SATISFIED. A subsequent adversarial audit by 4 skeptic agents found several of those marks were **premature or wrong**. Phase 9 has since landed (Track A battle-math bridge). Phases 10-12 remain for full closure.

**Net verdict (post-Phase-9):**
- Criterion (a): ✓ letter satisfied, ✗ spirit — visual mode still duplicates plumbing across 3 call sites (Phase 10)
- Criterion (b): ✓ satisfied (grep-level enforcement holds)
- Criterion (c): ⚠ outcome is emitted, but in the BattleScreen.start bypass it's a **synthesized fake** (Phase 10)
- Criterion (d): ✓ satisfied
- Criterion (e): ✗ NOT satisfied — regex missing `deprecated` pattern; ~17 live files have DEPRECATED markers (Phase 11)

**Battle-math regression (separate from Decision 3 criteria but central to PROJ-270 goal):**
- Pre-Phase-9: **broken.** `shield_capacity_mult` + `damage_mult` discarded by `FleetAuraManager._apply_bonuses` 2-key sink
- Post-Phase-9: **fixed.** Option A bridge (`ship.external_stats` + `Ability.get_effective_stat` composition) wires all team-bonus stat_keys through to ship stats. Empirically verified: `shield_capacity_mult=0.5` → `ship.max_shields=250` (was 500).

Phases 10-12 address the remaining Decision 3 gaps. Archival still blocked.

---

## Criterion (a) — Zero direct `engine.start*()` calls outside sanctioned lifecycle

> _"Zero direct `engine.start*()` calls outside `run_battle`, `start_engine_from_spec`, `BattleService.create_battle`, and `BattleController` lifecycle methods."_

**Status: ✓ SATISFIED**

**Evidence:**

1. [tests/unit/simulation/test_unified_entry_guard.py](../../../../tests/unit/simulation/test_unified_entry_guard.py) — `TestNoDirectBattleEngineConstruction.test_no_unwhitelisted_BattleEngine_construction` scans live production code and fails if any caller outside the whitelisted files references `BattleEngine(`. Currently green.
2. [tests/unit/simulation/test_unified_entry_guard.py](../../../../tests/unit/simulation/test_unified_entry_guard.py) — `TestNoScenarioSetupCallsInProduction.test_no_scenario_setup_calls_in_production` enforces no `scenario.setup(engine)` calls in live code. Currently green.
3. Residual `battle_engine.start(` references in live code (grep 2026-04-12):
   - `game/ui/screens/test_lab/screen.py:399` — historical comment ("PROJ-269 Phase 6 Task 6.9/6.10: legacy…")
   - `game/ui/screens/test_lab/test_executor.py:235` — historical comment
   - `combat_lab/services/test_execution_service.py:127-128` — historical comment ("legacy battle_engine.start([], [])…removed")
   - `combat_lab/services/scenario_run_helper.py:9` — positive-phrasing comment reinforcing contract
   - `docs/systems/combat_simulation.md:631` — documents that `BattleEngine.start()` runs an initial component update cycle inside `run_battle(spec)`
   All are documentation-only — no live call sites.

---

## Criterion (b) — Zero `BattleEngine(...)` constructions outside sanctioned paths

> _"Zero `BattleEngine(...)` constructions outside `start_engine_from_spec` and `BattleService.create_battle`."_

**Status: ✓ SATISFIED**

**Evidence:**

1. Enforced by [test_unified_entry_guard.py::TestNoDirectBattleEngineConstruction](../../../../tests/unit/simulation/test_unified_entry_guard.py) — the whitelist is `battle_runner.py`, `battle_service.py`, `battle_engine.py` (module containing the class itself). Other construction sites fail the test.
2. Test currently green; last run 2026-04-12.

---

## Criterion (c) — Every live production battle produces a `BattleOutcome`

> _"Every live production battle produces a `BattleOutcome` (headless, visual, Combat Lab, Battle Setup, strategy)."_

**Status: ✓ SATISFIED (with one acknowledged caveat)**

**Evidence by entry path:**

- **Headless battles** (strategy fleet combat, Combat Lab --fast runs, `TestExecutionService.run_headless`): go through `run_battle(spec)` which returns a `BattleOutcome` directly. Enforced by Combat Lab fast 162/162 + `test_battle_runner.py` + integration tests.
- **Combat Lab visual runs** (`TestExecutionService.run_visual`, `test_lab/screen.py::_switch_to_battle`): both now use `controller.configure(config, spec=spec)` (PROJ-270 Task 4.2/4.3). `BattleController.update()` detects `is_battle_over()` and calls `extract_outcome(engine, self._spec)` once. Retrievable via `controller.get_outcome()`. Enforced by [test_outcome_emission.py](../../../../tests/unit/simulation/battle_controller/test_outcome_emission.py) (7 tests, all green).
- **Battle Setup visual runs** (`game/app.py::start_battle`): compiles spec via `build_manual_battle_spec`, passes it to `controller.configure(config, spec=spec)`. Same outcome-emission path.
- **Strategy-layer battles**: route through `game/strategy/adapters/simulation_adapter.py` which uses `run_battle(spec)` directly.
- **Visual-mode `BattleResultsScreen`**: reads `outcome` from `controller.get_outcome()` via `BattleScreen._on_battle_ended`. Synthesizes a minimal outcome via `_build_fallback_outcome()` when the legacy `BattleScreen.start(team0, team1)` test-convenience path is used (no spec supplied).

**Caveat:** `BattleScreen.start(team0_ships, team1_ships)` is intentionally retained as a test-convenience bypass that does not construct a spec. Per [NEXT_AGENT_PROMPT.md](../NEXT_AGENT_PROMPT.md) acknowledged quirks: "fallback path `_build_fallback_outcome` synthesizes outcome from engine. This is intentional legacy support for existing tests and does NOT violate the unified-entry contract (outcome is still emitted)." The contract requires outcome emission; it does not require spec compilation for every code path. Fallback path emits a synthesized outcome → criterion met.

---

## Criterion (d) — Zero `setup(battle_engine)` methods on scenario templates

> _"Zero `setup(battle_engine)` methods remaining on scenario templates."_

**Status: ✓ SATISFIED**

**Evidence:**

1. [tests/unit/combat_lab/test_template_no_legacy_setup.py](../../../../tests/unit/combat_lab/test_template_no_legacy_setup.py) — 9 guards that assert every template (StaticTargetScenario, DuelScenario, PropulsionScenario, ResourceScenario, ComparisonScenario, PROP005, PropThrustMassRatio, base TestScenario) has no `setup` attribute and no `_setup_battle` helper. All green 2026-04-12.
2. [tests/unit/simulation/test_unified_entry_guard.py::TestNoLegacyScenarioSetup](../../../../tests/unit/simulation/test_unified_entry_guard.py) — AST-level scan of `combat_lab/scenarios/` for any `def setup(...battle_engine...)` signature. Currently green.

---

## Criterion (e) — Zero "Legacy-compatible" / "retained for" / "deprecated" comments in live code

> _"Zero `Legacy-compatible` / `retained for` / `deprecated` comments in live code under `combat_lab/`, `game/simulation/`, `game/ui/`."_

**Status: ✓ SATISFIED**

**Evidence:**

1. [tests/unit/simulation/test_unified_entry_guard.py::TestNoLegacyCompatibleComments](../../../../tests/unit/simulation/test_unified_entry_guard.py) — grep-based scan for the forbidden markers across live code. Currently green.
2. PROJ-270 Phase 8.2 deleted the last deprecation-stub modules (`battle_factories.py`, `battle_mode_handler.py`).
3. PROJ-270 Phase 8.1 deleted the 7 docstring-only stub test files left behind by PROJ-269.

---

## Guard Suite Summary

| Guard File | Tests | Status |
|-----------|-------|--------|
| [test_unified_entry_guard.py](../../../../tests/unit/simulation/test_unified_entry_guard.py) | 12 | All green |
| [test_template_no_legacy_setup.py](../../../../tests/unit/combat_lab/test_template_no_legacy_setup.py) | 9 | All green |
| [test_outcome_emission.py](../../../../tests/unit/simulation/battle_controller/test_outcome_emission.py) | 7 (incl. 3 new in this session) | All green |

Total guard tests: **28 passing** as of 2026-04-12.

---

## Baseline Numbers (this session)

- `pytest tests/ --tb=no -q` → **14629 passed** (+20 vs 14609 entry baseline), 2 skipped, 3 pre-existing fails (build-queue UI), 3 pre-existing errors (AI imports).
- `python -m combat_lab.run_tests --fast --no-history` → **162/162** ✓
- `python -m combat_lab.run_tests --no-history` → **170/170** ✓

---

## Conclusion (REVISED)

**The 5 acceptance criteria are NOT all satisfied.** Post-skeptic-audit:
- (a) satisfied in letter but visual-mode bypasses `start_engine_from_spec`
- (b) satisfied
- (c) satisfied via a synthesized-fallback shim (`_build_fallback_outcome`) — spirit violated
- (d) satisfied
- (e) **NOT** satisfied — guard regex missing `deprecated` pattern + scope gaps

Additionally, outside Decision 3 but inside PROJ-270's stated goals: **Phase 6 "Track A battle-math restored" is empirically false.** The gameplay regression that PROJ-269 Phase 5.5 introduced is NOT fixed. Skeptic repro: `ship.max_shields` does not change under `shield_capacity_mult=0.5`.

**PROJ-270 is NOT ready for archival.** Phases 9–12 cover the remaining work. Phase 9 (Track A battle-math) is the critical blocker.

The 28 regression guards do what they claim — but what they claim is narrower than what Decision 3 specified. Phase 11 hardens them.
