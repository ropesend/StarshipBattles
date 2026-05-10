# PROJ-270: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to `decisions.md`.

---

## Initial Analysis — Audit Findings (2026-04-12)

Three independent Explore agents plus direct file inspection confirmed the PROJ-269 wrap-up claim ("every battle enters via `run_battle(spec)`") is overstated. The agents rated findings across three dimensions: single-entry compliance (SIGNIFICANT GAPS), strategic-modifier battle-math regression (real, bounded, 20–35 engineer hours), and test coverage (MINOR GAPS).

### Confirmed CRITICAL/HIGH findings (production bypasses of `run_battle`)

| # | Site | Evidence | Severity |
|---|------|----------|----------|
| 1 | `combat_lab/services/test_execution_service.py::run_headless` | Lines 120–227: calls `battle_engine.start([], [])` (line 158), `scenario.setup(battle_engine)` (line 162), manual tick loop (lines 173–188). Live Combat Lab UI "Run Headless" button wires here via `TestLabUIController.handle_run_headless`. | HIGH |
| 2 | `game/app.py::start_battle` | Lines 543–571: inline `BattleController` construction. Docstring (line 548) explicitly acknowledges Task 6.9 deferral. `build_manual_battle_spec` is defined but has **zero production callers**. | HIGH |
| 3 | Visual-mode path produces no `BattleOutcome` | `BattleController` drives `BattleService.update()` per-frame; `BattleResultsScreen` reads live engine state. `extract_outcome()` is never called for visual battles. | HIGH |
| 4 | `BattleController.run_headless()` still live | Line 232 — called from `test_executor.py::_run_scenario_internal`. Contradicts "thin per-frame driver" claim. | HIGH |
| 5 | Scenario template `setup(battle_engine)` methods | `combat_lab/scenarios/templates.py` at lines 145, 357, 553, 801, 1042 — all 5 templates; `propulsion_scenarios.py:941–943` also. Comments say "Legacy-compatible… retained for anything still driving setup() directly." **System Migration Policy violation** per CLAUDE.md Rule 3. | HIGH |

### Confirmed MEDIUM findings

| # | Site | Evidence | Severity |
|---|------|----------|----------|
| 6 | Combat Lab validators discard `BattleOutcome` | `combat_lab/runner.py:175, 217, 228` + `test_executor.py:271, 303, 313` — `engine_ref["engine"] = engine` closure trick; `scenario._run_validation(engine)` consumes live engine, not outcome. **New finding A:** this is the architectural reason visual-mode adoption is hard; outcome contract must land in Combat Lab first. | MEDIUM-HIGH |
| 7 | Storm/fleet-modifier/complex-toggle battle math silently skipped | 4 compiler sites emit `stat_key="placeholder"`; `FleetAuraManager._append_external_from_entry` filters them. Pre-PROJ-269 these effects applied to ship stats; post-PROJ-269 they do nothing. Documented as "scope consequence" but nobody is tracking it as follow-up. | MEDIUM-HIGH gameplay |
| 8 | Unused spec fields | `AIPolicy` is empty; `CombatPolicies` on `TaskForceSpec`/`SquadronSpec` never read; `ComponentStateSpec.is_active` read by `_extract_component_states` but never written by compilers; `TaskForceOutcome` only carries `task_force_id` while `design.md` promised more. | MEDIUM |
| 9 | Visual-mode UI tests use `teams=()` Mock specs | `tests/fixtures/test_scenarios.py:152–159` explicitly documents the short-circuit. `materialize_spec_ships` processes zero ships, so the real visual path is never exercised on realistic input. | MEDIUM |

### Confirmed LOW findings (cleanup)

| # | Site | Severity |
|---|------|----------|
| 10 | `BattleConfig.test_scenario: Optional[Any]` (line 66) — Combat-Lab-only field on simulation-layer DTO | LOW |
| 11 | `ReturnDestination` enum in `game/simulation/battle_config.py:25` — names UI/strategy from simulation layer | LOW |
| 12 | `BattleState.mode = "manual"` (line 607) — zombie field from deleted enum | LOW |
| 13 | `BattleConfig.map_bounds` (line 69) duplicates `BattleSpec.boundary` | LOW |
| 14 | No explicit regression test for `_is_started=True` hack removal | LOW |
| 15 | `test_update_from_battle_results_triggers_speed_recalc` dropped without replacement in `test_post_battle_hook.py` | LOW |
| 16 | 7 docstring-only stub test files retained "for git history" — should be deleted | LOW |
| 17 | `tests/unit/strategy/conflict_resolution/conftest.py` + `test_engine_event_emission.py` retain `update_from_battle_results = MagicMock()` stale assignments | LOW |

### New findings (not in original hypothesis)

- **New Finding A (MEDIUM):** Visual-mode cannot adopt `BattleOutcome` cleanly until Combat Lab validators are migrated off the live-engine closure pattern. Phase ordering must put Combat Lab outcome adoption (Phase 2) before visual-mode adoption (Phase 4).
- **New Finding B (LOW):** The `engine_ref["engine"] = engine` closure pattern appears in 3 places. Once Phase 2 lands, this plumbing becomes dead.
- **New Finding C (LOW):** `_apply_spec_components_to_ship` (`battle_runner.py` line 428) silently ignores spec-component entries that don't match a ship component — "design drift" is allowed. If the design library changes between save and reload, damage vanishes silently. Track separately.

### Claims PROJ-269 got right (audit confirmed)

- Engine is truly context-blind (zero `if mode==` branches, zero imports from UI/strategy).
- Strategy combat fully migrated to `build_strategy_battle_spec` + `run_battle` + `PostBattleHook`.
- Combat Lab CLI / headless-via-test-executor migrated (`combat_lab/runner.py` uses `run_battle`; the bypass is the *service-layer* sibling `test_execution_service.py`).
- `test_damage_persistence.py` is a genuine end-to-end test (lines 71–166).
- DTOs are frozen and layered correctly.
- `BattleMode` / `BattleModeHandler` / `create_*_battle` factories actually deleted.
- Spec compilers have realistic fixtures + tests.

### False hypotheses from the PROJ-270 prompt

- The prompt listed `BattleController.run_headless` as "HIGH if any caller still uses it; MEDIUM if dead but undeleted." Audit confirmed it is **live** — it is therefore HIGH, not MEDIUM.
- The prompt claimed the 4 audit reports existed at `.agent_reports/proj-269-skeptical-audit/`. They did not — that folder does not exist on disk. PROJ-270 performed its own audit from scratch.

---

## Architecture

### Target architecture (post-PROJ-270)

Every battle follows this flow:

```
caller → spec compiler → run_battle(spec)
                               |
                               v
                   start_engine_from_spec (materializes ships)
                               |
                               v
                         BattleEngine ticks
                               |
                               v
                    extract_outcome(engine, spec)
                               |
                               v
                         BattleOutcome
                               |
                               +---> post_battle_hook (strategy mutation)
                               +---> Combat Lab validator (passes/fails)
                               +---> BattleResultsScreen (renders)
```

**Visual-mode extension:** `BattleController` becomes a spec-consuming adapter. It calls `start_engine_from_spec(spec, ...)` internally, runs the per-frame tick loop (driven by the Pygame event loop), then calls `extract_outcome(engine, spec)` in its end-of-battle handler. `BattleResultsScreen` reads the outcome. This keeps the UI's per-frame shape intact while honouring the unified contract.

### Key patterns to reuse

- **Spec compiler pattern** ([docs/02_PATTERNS.md §13](../../../docs/02_PATTERNS.md)): each caller owns a `build_*_battle_spec(...)` function that translates its domain inputs into a `BattleSpec`. Engine entry is one call. Three exist today; PROJ-270 makes all three actually used on live paths.
- **PostBattleHook closure** ([game/simulation/battle_spec.py](../../../game/simulation/battle_spec.py)): strategy's authoritative path for outcome → fleet mutation. Visual mode doesn't attach a hook (UI renders results); Combat Lab doesn't either (validator reads outcome directly).
- **`materialize_spec_ships`** ([game/simulation/battle_runner.py:91](../../../game/simulation/battle_runner.py)): already shared between `run_battle` and visual-mode UI callers. Phase 4's `BattleController` refactor uses this same helper.
- **Two-phase ability aggregation** (intra-group MAX, inter-group SUM): Phase 6's stat_key mapping reuses the existing `ExternalModifier` pipeline in `FleetAuraManager`.
- **Strict TDD** (CLAUDE.md Rule 1): every Phase 1–8 task starts with a failing test.

### Validator-to-Outcome Field Mapping (Phase 2 Task 2.1 — COMPLETE)

Combat Lab scenarios today read these live-engine fields. The PROJ-270 Phase 2 audit produced this inventory:

| Live-engine access | Post-PROJ-270-Phase-2 equivalent | Resolution |
|--------------------|----------------------------------|-----------|
| `engine.tick_counter` | `outcome.duration_ticks` | **14 sites migrated** by batch script |
| `engine.projectiles` (in `_collect_weapon_stats`) | `telemetry.in_flight_for(role)` | **1 site migrated** — `CombatLabTelemetry` stores in-flight count per role, captured in helper via per-tick callback |
| `engine.ships` / `engine.teams` | Only in docstring examples | Not live; flagged for Phase 8.5 docs rewrite |
| `engine.aura_manager` | Only referenced in tohit_attack_fleet docstrings | Not live |
| `engine.retreated_ships` | Not read by Combat Lab validators | N/A |
| `ship.*` (current_hp, is_alive, components, x/y/angle/velocity, shots_fired/hit, etc.) | Same — wired as `self.attacker` / `self.target` during `wire_ships`; no migration needed | Unchanged — wired ship refs persist through the battle; validators read directly |
| `self.target.layers[LayerType.ARMOR].components[i].current_hp` | Unchanged — accessed via wired ship refs | Unchanged |
| `component.shots_fired`, `component.shots_hit` | Unchanged — accessed via wired ship refs | Unchanged |

**Key insight:** the vast majority of the 190 method-signature occurrences were signature renames (`def validate(self, engine)` → `def validate(self, outcome, telemetry=None)`) because the body of most validators reads from `self.*` (wired ship refs), not from `engine.*`. Only 14 `engine.tick_counter` sites + 1 `engine.projectiles` site were genuine engine reads.

**Phase 2 design decision (locked):** Option B — Combat-Lab-specific `CombatLabTelemetry` bundle carries forensic data (in-flight projectile counts). Simulation-layer `BattleOutcome` stays lean.
- **`CombatLabTelemetry`** lives at [combat_lab/telemetry.py](../../../combat_lab/telemetry.py)
- **Helper [combat_lab/services/scenario_run_helper.py](../../../combat_lab/services/scenario_run_helper.py)** captures it during per-tick callback and returns `(outcome, telemetry)` to callers
- **`TestScenario._run_validation(outcome, telemetry)`** is the new contract
- **`_collect_weapon_stats(ship, role, *, telemetry=None)`** reads from telemetry

**Future additions to `CombatLabTelemetry` (deferred — add when a scenario genuinely needs them):**
- Per-tick position tracks (currently implemented via `self._track_tick` + `self.tracked_positions` on templates — no migration needed today)
- Per-hit event logs beyond what `ShipOutcome.hits_taken` provides

### Dependencies & Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Phase 4 visual-mode refactor breaks the 2v2 start button | HIGH | Phase 2 proves the outcome-consumption pattern with 162 Combat Lab scenarios first; Phase 4 uses the proven pattern. Manual launcher smoke at end of Phase 4. |
| Phase 6 re-enables effects that change battle-balance — existing Combat Lab scenarios might start failing | MEDIUM | Phase 6.1/6.2 touch only the strategy compiler; Combat Lab scenarios don't use fleet combat modifiers or storm effects, so 162/162 should stay green. Verify per-step. |
| Phase 2 validator rewrites introduce per-scenario bugs | MEDIUM | Strict TDD — migrate 1 template at a time (StaticTarget first), verify the 30+ StaticTarget scenarios still pass, then move to the next template. |
| Phase 5 `ReturnDestination` move changes import paths across UI | LOW | Grep audit; each rename is atomic. |
| Phase 6 scope creep (flat-shield-bonus, suppressors) blows budget | MEDIUM | **Trim point locked** (decisions.md Decision 1): if Phase 6.1–6.3 plus 6.5 exceed 3 days, flat-bonus + suppressors carve out to PROJ-271. Decision at start of Phase 6. |

### Opportunities Discovered

- Phase 4's outcome contract unlocks a non-blocking `run_battle_ticks(spec)` variant in a future project (would replace `BattleController` entirely). Out of scope here — PROJ-270 keeps the controller as a per-frame adapter.
- Phase 6.5's "log unknown stat_keys instead of silent skip" gives future compiler authors immediate feedback when they add a new modifier source with no stat_key mapping yet — prevents the Phase 5.5 regression from repeating.
- Phase 8.3's pytest guard test (grep forbidden symbols) establishes a general pattern for locking architectural contracts. Can be reused for future refactors.

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale. Three decisions are load-bearing for scope:

1. **Phase 6 scope trim point:** bounded strategic-modifier restoration (multipliers only) — flat-bonus and suppressors deferred to PROJ-271 if Phase 6 exceeds 3 days.
2. **Visual-mode approach:** `BattleController` becomes a spec-consuming per-frame adapter; emits `BattleOutcome` at battle end. Visual mode does NOT call `run_battle` (blocking) directly.
3. **Acceptance criterion:** zero `engine.start*()` calls outside whitelist, zero `BattleEngine(...)` constructions outside whitelist, zero `setup(battle_engine)` methods on templates, zero `"Legacy-compatible"` comments in live code. Enforced via Phase 8.3 pytest guard test.
