# Phase 10: Documentation sync (CLAUDE.md Rule 2)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 10`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** LOW (documentation-only)
**Depends On:** Phases 6-9 should land first so docs reflect final state
**Objective:** Close the CLAUDE.md Rule 2 gap — docs and code out of sync after PROJ-269/270/271. Documentation skeptic audit (2026-04-13) identified 5 specific gaps plus missing patterns that are load-bearing for future contributors.

## Context

Doc skeptic findings:
1. `Ability.get_effective_stat` external-stats composition (PROJ-270 Phase 9) is undocumented outside code comments. `docs/guides/adding_abilities.md` Step 5 still describes a 3-tier lookup, missing the 4th step (compose with `ship.external_stats`, `_mult` multiply / `_add` sum).
2. Two docs still say "pending PROJ-271": `docs/systems/combat_simulation.md:432` and `docs/systems/strategy_layer.md:756-758`.
3. `SHIELD_BONUS_ADD` missing from additive stat_keys table in `docs/systems/ability_reference.md:1538-1545`.
4. `docs/02_PATTERNS.md` has no entries for (a) external-stats bridge; (b) scope-driven team routing.
5. Stale reference: `docs/01_ARCHITECTURE.md:162` lists `BattleFactories` in `game/ui/services/` — file does not exist (deleted in PROJ-270).

## Tasks

### Task 10.1: Document external-stats bridge in `adding_abilities.md` [Medium]
**File:** `docs/guides/adding_abilities.md`

- [ ] Add Step 5 (or update existing Step 5) to describe the 4-tier lookup: `ability_stats` → `component.stats` → `ship.external_stats` composition → default.
- [ ] Show worked example: `get_effective_stat('shield_capacity_mult', 1.0)` with both a local 0.8 and external 0.5 → returns 0.4 (MULT composition).
- [ ] Show worked example: `get_effective_stat('shield_bonus_add', 0.0)` — but note this is SHIP-LEVEL, not per-ability. Reference Phase 10.2 below for the ship-level pattern.

### Task 10.2: Add external-stats bridge + ship-level plumbing to `02_PATTERNS.md` [Complex]
**File:** `docs/02_PATTERNS.md`

- [ ] Add new pattern entry: "External-Stats Bridge (PROJ-270 Phase 9)" describing the ModifierStack → FleetAuraManager → ship.external_stats → get_effective_stat chain + the composition rules.
- [ ] Add new pattern entry: "Ship-level vs Per-Ability Stat Keys" explaining when to use each. `SHIELD_BONUS_ADD` example with the "virtual extra shield component" semantic. Pipeline ordering `(base + flat) × mult` locked at `ship_stats.py::_apply_aggregated_stats`.
- [ ] Add new pattern entry: "Scope-Driven Team Routing (PROJ-271)" describing `_route_team_for_scope` / `_OPPONENT_SCOPES` idiom in both spec compilers.

### Task 10.3: Add SHIELD_BONUS_ADD to ability reference [Simple]
**File:** `docs/systems/ability_reference.md:1538-1545`

- [ ] Add entry to additive stat_keys table: `shield_bonus_add` | operation=add | default=0.0 | Ship-level addition to max_shields, scaled by external shield_capacity_mult.

### Task 10.4: Clear "pending PROJ-271" stale references [Simple]
**File:** `docs/systems/combat_simulation.md`, `docs/systems/strategy_layer.md`

- [ ] Line 432 of combat_simulation.md — remove "pending PROJ-271" language; describe the now-landed behavior.
- [ ] Lines 756-758 of strategy_layer.md — same.
- [ ] Grep for other "pending PROJ-271" / "deferred to PROJ-271" — none should remain.

### Task 10.5: Fix stale BattleFactories reference [Simple]
**File:** `docs/01_ARCHITECTURE.md:162`

- [ ] Delete or update the line. `BattleFactories` module was deleted in PROJ-270 Phase 8.2.
- [ ] Grep for any other references — same fate.

### Task 10.6: Regression — docs consistency [Simple]

- [ ] Grep `docs/` for references to other deleted APIs: `BattleConfig.map_bounds`, `BattleState.mode`, `battle_mode_handler`, `battle_factories`, `BattleController.run_headless`, scenario `setup(battle_engine)`, etc.
- [ ] Fix every stale reference found.
- [ ] Verify guide examples still compile (eyeball only, no test runner).

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] Doc grep clean for stale API references
- [ ] New patterns documented in `02_PATTERNS.md`
- [ ] Adding-abilities guide covers the external-stats bridge
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
