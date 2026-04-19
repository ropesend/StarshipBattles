# PROJ-283..290 Skeptical Audit — Executive Summary

**Date:** 2026-04-18
**Reviewer pattern:** 5 parallel Explore subagents, each with a distinct skeptical lens (see `proj-269-270-skeptic-review/` for the format this borrows from).
**Scope:** PROJ-283 through PROJ-290 — Strategy-layer demographics + economy UI rework. 8 projects, 78 unique files, all at `Awaiting Verification`.
**Constraint honoured:** Zero code changes. Read-only audit. Reports are the output.

---

## Top-line verdict

**Do NOT sign off yet.** Three genuine **Critical** runtime bugs and four **Major** concerns surfaced. Two of the three Criticals are user-visible gameplay defects introduced or exposed by PROJ-283..290; one is a pre-existing bug rediscovered during the audit.

| Severity | Count |
|---|---|
| **Critical** | 3 |
| **Major** | 4 |
| **Minor** | 5 |
| **False positives (cleared)** | 12 |

The parallel PROJ-289 ↔ PROJ-290 merge is semantically sound (merge-hazards audit returned no bugs, only minor-documentation asymmetry). The registry pattern (PROJ-283), formula-equivalence test (PROJ-288), and multi-resource MIN aggregation (PROJ-286) are well-defended. Recommend fixing the 3 Criticals before sign-off, triaging the 4 Majors, and deferring the Minors.

---

## Findings table (ordered by severity)

| # | Theme | Title | Severity | Location | Action |
|---|---|---|---|---|---|
| C1 | Pipeline | Treasury Total excludes Population Upkeep | **Critical** | [empire_economy_calculator.py:147-150](game/strategy/engine/empire_economy_calculator.py#L147-L150) | Add one term to the `total_expenses` sum |
| C2 | Architecture | FoodAllocationEditor reads deleted `food_per_pop_per_turn` | **Critical** | [food_allocation_editor.py:258](game/ui/screens/food_allocation_editor.py#L258) | Orphaned handoff — needs scope owner |
| C3 | State | HappinessEngine returns empire race_config for mismatched race_ids | **Critical** | [happiness_engine.py:90-95](game/strategy/engine/happiness_engine.py#L90-L95) | Return None on mismatch, or wire registry |
| M1 | Architecture | Direct UI→engine import (layer violation, pre-existing) | Major | [empire_treasury_panel.py:19](game/ui/panels/empire_treasury_panel.py#L19), [empire_panel_window.py:18](game/ui/screens/empire_panel_window.py#L18) | Introduce `empire_economy_service.py` facade |
| M2 | State | `CachedRaceRegistry` has no mtime fallback | Major | [race_library.py:265-294](game/strategy/systems/race_library.py#L265-L294) | Add optional mtime check OR document the manual-invalidate constraint |
| M3 | State | Planet per-turn cache rollback uncertain under PROJ-251 error boundary | Major | [planet.py:146-151](game/strategy/data/planet.py#L146-L151) + [turn_engine.py:540-554](game/strategy/engine/turn_engine.py#L540-L554) | Verify `TurnStateSnapshot.restore()` resets cache fields |
| M4 | Tests | Treasury Upkeep row not end-to-end tested | Major | [test_empire_treasury_panel.py](tests/unit/ui/panels/test_empire_treasury_panel.py) | Add integration test from calculator → `_get_expense_rows` → row presence |
| M5 | Tests | `CachedRaceRegistry` invalidation not tested | Major | no test file | Add cache-invalidation scenario test |
| m1 | Merge | Asymmetric fallback in `update_planet` (view unconditional, empire/registry sentinel) | Minor | [planet_report_panel.py:273-281](game/ui/panels/planet_report_panel.py#L273-L281) | Document the contract in the docstring |
| m2 | Merge | `view` kwarg latent for PROJ-290's PlanetListWindow path | Minor | [planet_list_window.py:511-521](game/ui/screens/planet_list_window.py#L511-L521) | Non-issue; by design |
| m3 | Architecture | FoodAllocationEditor migration ownership ambiguous in PROJ-289 decisions | Minor | PROJ-289/decisions.md | Add explicit acceptance or deferral |
| m4 | Tests | `population_food_resource` shim still used by `food_allocation_editor.py` | Minor | [food_allocation_editor.py](game/ui/screens/food_allocation_editor.py) | Same fix as C2 retires this |
| m5 | Tests | Growth-rate docs claim `format_signed_float(rate * 100, 1)` pattern not found verbatim | Minor | [docs/systems/strategy_layer.md](docs/systems/strategy_layer.md) | Re-grep and align docs to real code |

---

## Critical findings — detail

### C1. Treasury Total excludes Population Upkeep

**PROJ-269-270 bug rhyme:** data is correctly computed, correctly displayed as one row, but **silently dropped from the summary aggregation** — identical shape to PROJ-269-270's `_team_bonuses` / `_apply_bonuses` bug that that earlier audit caught.

`EmpireEconomyCalculator.calculate(empire)`:
- Line 142 → `snapshot.total_population_upkeep = {"organics": 10.0, ...}` ✓
- Lines 147-150 → `snapshot.total_expenses[r] = tributes + ships_construction + complexes_construction` — **does NOT include `total_population_upkeep`**.

`EmpireTreasuryPanel._get_expense_rows()`:
- Correctly inserts a "Population Upkeep" row with negated cells.
- "Total" row reads `snapshot.total_expenses` — shows the wrong number.

User-visible symptom:
```
Tributes: 0
Construction (Ships): 2
Construction (Complexes): 3
Population Upkeep: -10
Total: -5     <- WRONG. Should be -15.
```

**Fix (one line):** in `calculate()`, change the `total_expenses[r]` sum to include `snapshot.total_population_upkeep.get(r, 0.0)`.

**Test coverage gap (M4):** no existing test runs `calculate()` on an empire with populations and then asserts `snapshot.total_expenses` includes the upkeep. The 7 `TestPopulationUpkeepAggregation` tests only assert `total_population_upkeep` itself, not the aggregation. This is how C1 shipped undetected.

### C2. FoodAllocationEditor AttributeError on open

`food_allocation_editor.py:258` calls `compute_consumption_preview(pop, allocation, self._economy.food_per_pop_per_turn)`. PROJ-286 **deleted** `food_per_pop_per_turn` from `EconomyConfig` and replaced it with `population_consumption: Dict[str, float]`. The shim kept only `population_food_resource` (a string), not the float rate the editor needs.

PROJ-286's plan.md deferred the fix to "PROJ-289's UI migration". PROJ-289's decisions.md does not list the editor migration in scope. Orphaned handoff. The editor will AttributeError the first time a player opens it post-PROJ-286.

**Fix options:**
1. Add a temporary `food_per_pop_per_turn` computed property on `EconomyConfig` returning `population_consumption[primary_resource]` — mirrors the existing `population_food_resource` shim.
2. Migrate the editor to iterate `population_consumption` and show per-resource previews (proper fix — likely what "PROJ-289 UI migration" meant).

Both are bandaid vs. proper-fix per CLAUDE.md Rule 3. User decision needed.

**Related Minor (m3):** PROJ-289's decisions.md should document either acceptance or explicit re-deferral.

### C3. HappinessEngine returns wrong race_config for multi-species colonies

`HappinessEngine._get_race_config(empire, race_id)`:
- Reads `empire.race_config` (the empire's PRIMARY race) and returns it **regardless of whether `race_id` matches**.
- Impact: on a multi-species colony (say, humans + voidari both in one empire), `happiness = base_happiness * last_food_ratio * habitability` uses the WRONG `base_happiness` for the non-primary species. Voidari get computed against human `base_happiness`.

**Pre-existing vs. PROJ-28X regression:** PROJ-287's decisions.md explicitly deferred migrating `HappinessEngine._get_race_config` and `PopulationEngine._get_race_config` to the `IRaceRegistry` facade. That decision was not a bug introduction — but it left an existing bug in place under PROJ-284's new multi-species demographic loop, which makes the bug reachable in production for the first time. In single-species empires, the bug is invisible. PROJ-286 + PROJ-287 + PROJ-289 together make multi-species colonies a real gameplay state.

**Fix:** In `_get_race_config`, return `None` when `race_id != empire.race_config.race_id` (and rely on the existing graceful-skip path), or wire the registry lookup that PROJ-287 built.

**User decision needed:** is fixing C3 in-scope for closing PROJ-283..290, or does it open a new ticket?

---

## Major findings — summary

- **M1 (layer violation):** `EmpireTreasuryPanel` and `EmpirePanelWindow` import `EmpireEconomyCalculator` directly from `game.strategy.engine.*`. Pre-dates these projects but the audit surfaces that PROJ-283..290 didn't take the opportunity to fix it while adding new Treasury functionality. Facade-ize into `game/strategy/services/empire_economy_service.py`.

- **M2 (stale race cache):** `CachedRaceRegistry` has no mtime/file-watch fallback. If any code path mutates a race file without calling `registry.invalidate(race_id)`, stale configs linger until process restart. The race-editor UI does call invalidate; external edits, modder CLI tools, or any future code path that bypasses the editor won't.

- **M3 (cache vs. error-boundary):** `Planet._cached_habitability_multiplier` is `init=False, repr=False, compare=False` — intentionally excluded from `to_dict()` and pickling. BUT `TurnStateSnapshot.restore()` (PROJ-251 error boundary) restores empire state from a pre-turn snapshot; it is not verified whether the `init=False` cache fields are reset by restore, so a stale multiplier could survive an error rollback. The state-cache agent flagged this as "VULNERABILITY UNCERTAIN" — needs a targeted integration test or 15 minutes of reading `turn_state_snapshot.py` to confirm.

- **M4 (treasury UI untested):** see C1 discussion above.

- **M5 (race-registry cache untested):** see M2 discussion above. PROJ-269 audit called out this exact pattern as "the #1 failure mode for lazy caches"; PROJ-287's tests did not cover it.

---

## Minor findings — summary

- **m1** Asymmetric `update_planet` semantics (view unconditional, empire/registry sentinel). Not a bug; document the contract.
- **m2** `view=None` never wired for uncolonized-planet path. By design; PROJ-290 doesn't need it. Non-issue.
- **m3** Scope-boundary documentation gap (see C2).
- **m4** Shim still in use (will be retired by fixing C2).
- **m5** Docstring/code drift on growth-rate formatting. Minor; re-grep and align.

---

## False positives cleared (12)

- Multi-resource starvation → happiness label pipeline (Pipeline A): verified end-to-end ✓
- Projection grid math sign-convention (Pipeline C): net computed once + frozen ✓
- Uncolonized habitability empire-resolution (Pipeline D): explicitly `self.scene.current_empire` ✓
- Hardcoded factor lists post-PROJ-283: none found; registry truly drives calculation ✓
- `last_food_ratio` staleness: engine clears dict every turn ✓
- Test fixture drift (PROJ-289 ↔ PROJ-290): fixtures correctly scoped ✓
- Test singleton pollution of `set_default_economy_config`: autouse fixture resets ✓
- Positional-argument hazard in `format_planet_info`: grep found zero unsafe callers ✓
- Equivalence test coverage in PROJ-288: 12-cell matrix sufficient ✓
- Docs coherence (PROJ-289 + PROJ-290 subsections): both present, correct order ✓
- Resource-grid routing: legacy stockpile grid intentional for uncolonized ✓
- Numerical drift in `last_consumption_ratios.values()`: realistic and correct ✓

---

## Items requiring user decision

1. **C2 fix approach:** temporary `food_per_pop_per_turn` shim (bandaid, violates Rule 3) vs. migrate the editor to iterate `population_consumption` (proper fix, extends PROJ-289 or opens a new ticket).

2. **C3 scope:** treat as in-scope for PROJ-287 closure (re-open for a Phase 5), or open a new ticket (PROJ-291 "HappinessEngine multi-species race_config")? The bug predates PROJ-287, but PROJ-287 deferred migrating the resolver that would have fixed it, and PROJ-284/286 made the bug reachable.

3. **M3 verification:** is 15-20 minutes of reading `turn_state_snapshot.py` enough to downgrade M3 to "verified safe"/"Minor", or do you want a targeted integration test?

4. **Sign-off gating:** do we sign off PROJ-283..290 with C1-C3 + M1-M5 as blockers, or sign off with a punch list? C1 is a one-line fix; C2 is larger; C3 is a design decision.

---

## Where to go from here

- The individual skeptic reports live alongside this file under `.agent_reports/proj-283-290-skeptic-review/`:
  - [pipeline_reachability_skeptic.md](pipeline_reachability_skeptic.md)
  - [architecture_shims_skeptic.md](architecture_shims_skeptic.md)
  - [state_cache_skeptic.md](state_cache_skeptic.md)
  - [merge_hazards_skeptic.md](merge_hazards_skeptic.md)
  - [tests_docs_skeptic.md](tests_docs_skeptic.md)
- Per `CLAUDE.md § Subagent Report Output`, this directory is ephemeral. If you want durable audit records (recommended given the Critical findings), move/copy the directory to `Projects/archived_projects/PROJ-###/findings/` before deletion.
- No code changes proposed or applied. Per user request and Plan Mode discipline.
