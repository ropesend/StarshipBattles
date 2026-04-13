# PROJ-269/270/271 Code Architecture Skeptic — Post-Implementation Audit

**Date:** 2026-04-13
**Auditor:** Code-level skeptic (source grep + layer trace; no test execution)
**Verdict:** PROJ-271 is substantively correct but **one of its signature hardening fixes is applied to the wrong function** and ships without reaching the live production path. PROJ-270 carries several "deferred / scope-trimmed" items that remain live in the tree.

---

## Executive Summary

1. **CRITICAL — Phase 5 `capture_battle_state` hardening misses the live path.** Narrowing `except Exception → except OSError` was applied only to the module-level `capture_battle_state()` function. Production (`test_executor.py:247`) uses `BattleStateCapture` (the context-manager class); its `_capture_state` method (line 289) still has `except Exception` and will silently swallow the very programming errors Phase 5 claimed to surface.
2. **HIGH — `BattleScreen.start(team0, team1)` + `_build_fallback_outcome` are still live** despite `findings/goal_integrity.md` confirming zero test callers. Two-layer shim with no consumer.
3. **HIGH — `_entries_from_modifier_source` still emits `stat_key="placeholder"`** in the strategy compiler. The decisions.md "out of scope" rationalization is defensible for planning but remains a silent-drop risk if any code ever populates `sector.modifiers`/`system.modifiers`.
4. **MEDIUM — Shield pipeline semantic drift:** the flat `shield_bonus_add` is scaled only by `shield_capacity_mult`, not by the general `capacity_mult`. Decisions.md claims "exactly the same as if the ship had an extra shield component" — an extra component's capacity would be scaled by BOTH.
5. **LOW — Several dead artifacts:** 4 unused imports in `ship_stats.py`, dead `_noop_hook` in strategy compiler, dead `getattr(comp_def, "abilities", ...)` Component-object fallback in Battle Setup compiler (registry never returns Component objects).

---

## CRITICAL Findings

### C1. Phase 5 hardening applied to a dead function; live path is still broad-catch

**Evidence:**
- `combat_lab/battle_state_capture.py:98` — module-level `capture_battle_state()` caught `except OSError` (Phase 5 fix).
- `combat_lab/battle_state_capture.py:289` — `BattleStateCapture._capture_state` still has `except Exception as e` with `logger.warning("Failed to capture {state_type} state: {e}")`.
- `game/ui/screens/test_lab/test_executor.py:247` — live production code uses `BattleStateCapture(engine=None, test_id=test_id, seed=seed)` and drives `__enter__`/`__exit__` manually. This calls `_capture_state`, **not** the module-level function.
- `tests/unit/combat_lab/test_battle_state_capture_no_mode_kwarg.py:65-120` — Phase 5 regression tests only exercise the module-level function. No test covers `BattleStateCapture._capture_state`.

**Impact:** The originating symptom (silent `mode=` TypeError warnings for months) would recur identically in the class-based path. Any future API drift on `BattleState.capture_from_engine` will continue to be swallowed in production runs.

**Fix:** Narrow `_capture_state` to `except OSError` mirroring the module-level change. Add a regression test covering the class's `_capture_state` with a broken engine — should raise AttributeError/TypeError, not return None.

**New PROJ-270 phase?** No — this is PROJ-271 Phase 5 scope, under-delivered. File as PROJ-271 phase 5.4 (or a follow-up).

---

## HIGH Findings

### H1. `_build_fallback_outcome` is live but has zero callers

**Evidence:**
- `game/ui/screens/battle_screen.py:227-261` — `BattleScreen.start(team0_ships, team1_ships, ...)`.
- `game/ui/screens/battle_screen.py:494-496` — `_build_fallback_outcome()` helper.
- `tests/*/screen.start(` grep — zero matches for BattleScreen usage with ship args (only tests for `SetupScreen.start()`).
- `Projects/active_projects/PROJ-270/findings/goal_integrity.md:57` — prior audit explicitly verified "ZERO callers actually exist today."

**Impact:** System Migration Policy violation (CLAUDE.md Rule 3). Two compat shims (the `start(team0, team1)` entry + `_build_fallback_outcome` synthesizer + `_get_or_build_outcome` selector) exist to support a test API that no test uses.

**Fix:** Delete `BattleScreen.start(team0, team1)`, `_build_fallback_outcome`, and the fallback branch of `_get_or_build_outcome`. Remove the acceptance-audit caveat in `findings/acceptance_audit.md` §Criterion (c).

**New PROJ-270 phase?** Yes — this would genuinely close criterion (c) in spirit as well as letter.

### H2. `_entries_from_modifier_source` still emits placeholder entries

**Evidence:**
- `game/strategy/combat/spec_compiler.py:461-502` — `_entries_from_modifier_source(source_obj, ...)` emits `stat_key="placeholder"` for any `sector.modifiers` / `system.modifiers` / `empire.combat_modifiers` entries.
- `game/strategy/adapters/simulation_adapter.py:190-196` — production call passes `sector=None, system=None, empires={}`, so the function **never** receives data in production today.
- `game/strategy/combat/spec_compiler.py:320, 324, 339` — still called unconditionally with these sources wired through.

**Impact:** Dead-with-a-landmine. The moment any feature populates `sector.modifiers` (a natural-looking data-model addition), strategic modifiers silently evaporate at battle time — the same class of bug as the PROJ-269 → PROJ-270 regression. PROJ-271 decisions.md (row 5) explicitly declares this "out of scope," but the code still emits broken ModifierEntries rather than logging + skipping.

**Fix (either):** (a) delete the call sites entirely while no production caller populates these attributes; the function becomes dead and deletable. Or (b) replace placeholder emission with an explicit `logger.error("Unmapped sector/system/empire modifier %s — would be silently ignored")` + return `[]`, so a future content author trips the log instead of the engine.

**New PROJ-270 phase?** Yes, recommend option (a) as a small sub-phase under "dead code eradication" — safer than option (b) for the System Migration Policy.

### H3. PROJ-271 Phase 5 guard tests don't guard the live path

**Evidence:** Same as C1; the tests only probe the module-level function. Compounding C1.

**Impact:** If a future refactor breaks the BattleStateCapture class, the guards green-light it.

**Fix:** Add class-level parallel tests asserting `BattleStateCapture.__enter__()` on a `BrokenEngine` propagates instead of silently returning None.

---

## MEDIUM Findings

### M1. Shield pipeline semantic drift: flat bonus only composes with one of two mults

**Evidence:**
- `game/simulation/components/abilities/defense.py:42-46` — `ShieldProjection.recalculate()` applies BOTH `capacity_mult` AND `shield_capacity_mult` to each component's capacity: `self.capacity = self.base_capacity * capacity_mult * shield_capacity_mult`.
- `game/simulation/entities/ship_stats.py:464-469` — ship-level flat bonus only applies `shield_capacity_mult`: `ship.max_shields += flat_shield_bonus * shield_cap_mult`.
- PROJ-271 `decisions.md` (2026-04-13, row 1): design intent is "exactly the same as if the ship had an extra shield component providing the ability."

**Impact:** An external `capacity_mult` modifier (rare today, but a valid stat_key in the enum) will scale real shield component capacities but **not** the flat bonus. Divergence from the stated user semantic. Ship-level flat bonus + `capacity_mult=2.0` + `shield_capacity_mult=1.0` gives `base*2 + flat*1`, while a "virtual extra shield component" would give `(base+flat)*2*1`.

**Fix:** Apply both multipliers to the flat bonus: `ship.max_shields += flat_shield_bonus * shield_cap_mult * cap_mult`. Or, cleaner, redesign so the flat bonus enters the aggregation loop as a virtual ShieldProjection contribution (single source of truth for the multiplier chain).

**New PROJ-270 phase?** Optional — `capacity_mult` is not currently used as an external aura, so this is a latent-semantic issue, not a live gameplay break. Flag for next content cycle.

### M2. Dead Component-object fallback in Battle Setup compiler

**Evidence:**
- `game/ui/screens/battle_setup/spec_compiler.py:343-347` — compiler supports both `isinstance(comp_def, dict)` and `getattr(comp_def, "abilities", ...)` for Component objects.
- `game/core/registry.py:212-213` — `RegistryManager.hydrate()` stores only the raw dicts: `self.components.update(components_data)`. Nothing anywhere converts them to Component objects in the registry.
- `game/simulation/components/component.py:132` — Component is only constructed via `Ship.add_component`, never placed into the registry.

**Impact:** Branch is never taken in production. Extra complexity that a casual reader might assume is load-bearing.

**Fix:** Collapse to the dict branch, or add a comment explicitly documenting the branch as defensive futureproofing (if intentional).

### M3. Layer boundary self-audit: PROJ-271 code clean

**Evidence:**
- `game/ui/screens/battle_setup/spec_compiler.py:34-63` — imports only from `game/core/*` and `game/simulation/*`. No strategy/ui-cross dependencies.
- `game/simulation/entities/ship_stats.py` — imports unchanged by PROJ-271 additions; stays within core/simulation.
- `game/simulation/combat/fleet_aura_manager.py` — external_stats write is in simulation layer, consumer in abilities/base.py is also simulation. No boundary violation.

**No finding** — layer compliance verified.

### M4. Acceptance guard whitelist is accurate

**Evidence:**
- `BattleEngine(` constructions in `game/`: `battle_engine.py` (own module), `battle_runner.py:153`, `battle_service.py:86`. All in whitelist.
- `combat_lab/` — only comments/docstrings contain the literal. No live construction.
- `.engine.update(` / `.engine.start(` regex tested via `TestNoDirectEngineTickLoop` — whitelist of `battle_runner.py` / `battle_service.py` / `battle_engine.py` covers all live call sites.

**No finding** — guard whitelist is not fig-leafing anything new.

---

## LOW Findings

### L1. Unused imports in `ship_stats.py:62-65`

**Evidence:** `IResourceStorageAbility`, `IResourceGenerationAbility`, `IResourceConsumptionAbility`, `IWarpJumpAbility` are imported but only the `is_*` helper functions on the same lines are used. Grep confirms only `IWarpJumpAbility` appears once in a comment (line 396).

**Fix:** Delete these four imports.

### L2. Dead `_noop_hook` in strategy compiler

**Evidence:**
- `game/strategy/combat/spec_compiler.py:510-518` — `_noop_hook` defined.
- Grep for `_noop_hook` across `game/` returns only the definition. The real hook comes from `_build_strategy_post_battle_hook`.

**Fix:** Delete.

### L3. `_NUM_TEAMS = 2` assumption not enforced

**Evidence:**
- `game/ui/screens/battle_setup/spec_compiler.py:92` — `_NUM_TEAMS = 2` with explanatory comment.
- `_route_team_for_scope` uses `1 - owner_team` assuming two-sided battle.
- `build_manual_battle_spec` hard-codes `teams=(team0, team1)` at line 148. So 3+ teams cannot reach this compiler today.

**No bug today**, but: the routing is opaque for a future audit. Consider deleting `_NUM_TEAMS` (it's unused) and adding an assertion: `assert len(ui_state.sides_iter()) == 2` at the top of `build_manual_battle_spec` so a future extension trips loudly.

### L4. `_build_fallback_outcome` docstring claims "71 test callers" — factually wrong

**Evidence:** See H1. Prior skeptic audit (`goal_integrity.md:57`) already recorded zero callers exist. The claim in `NEXT_AGENT_PROMPT.md:212` and in phase_10_checklist.md (retained as rationale for the deferral) survives the cleanup unchallenged.

**Fix:** When H1 is closed, delete the misleading docstring.

---

## No-Finding Sections (Audited and clean)

### Phase 9 `external_stats` bridge usage pattern

- `Ability.get_effective_stat` (base.py:227) is consistently used by ability subclasses; `weapons.py` has 13 call sites, `defense.py`/`crew.py`/`resources.py` all use it. The only raw `self.component.stats.get(...)` call is `weapons.py:175` for an unrelated `properties` dict lookup — not a stat_key.
- `ship.external_stats` is only written by `FleetAuraManager._apply_bonuses:347`. Never mutated externally.
- `isinstance(external_stats, dict)` guard is present in both `base.py:281` AND `ship_stats.py:465`.

### Battle Setup compiler complex-design walking

- `_iter_components` walks all layer lists via `layers.values()` — catches CORE, INNER, OUTER, ARMOR uniformly.
- `_extract_scope` handles both primitive (`int/float`) and dict shapes for `ability_data`.
- `_extract_ability_value` handles primitive / dict / int+float paths.
- `load_json_required` errors caught as `(OSError, ValueError)` with `logger.warning`; compile continues with empty list.
- `_ABILITY_TO_STAT_KEY` keys (`ShieldProjection`, `ShieldModifier`, `DamageModifier`) match the JSON-ability-name exports from `game/simulation/components/abilities/__init__.py:127-128` and the raw strings in `data/components.json`.

### Strategy compiler emits real stat_keys

- `_entries_from_environmental_effects` emits `shield_capacity_mult` (no placeholder).
- `_entries_from_fleet_combat_modifiers` emits `shield_capacity_mult`, `damage_mult`, `shield_bonus_add`. All three placeholder-free per the behavioral guard at `test_unified_entry_guard.py:586-624`.

### Scope-driven team routing

- `_OPPONENT_SCOPES = {"enemy_sector", "enemy_system"}`. Matches the only two `enemy_*` scope values in `AbilityScope` enum.
- `PLANET`, `EMPIRE`, `ALLIED_EMPIRE`, `ALLIED_SECTOR`, `ALLIED_SYSTEM`, `PLAYER_SECTOR`, `PLAYER_SYSTEM`, `FLEET`, `SECTOR`, `SYSTEM` → all route to owner team, which is correct (these are same-team-benefit scopes).

### System Migration Policy — `Legacy-compatible` grep

- PROJ-271 added no "Legacy-compatible" / "retained for" markers.
- PROJ-270 guard in `test_unified_entry_guard.py::TestNoLegacyCompatibleComments` remains effective for the six idioms it encodes.

---

## Summary Table

| # | Severity | Title | File | New Phase? |
|---|---|---|---|---|
| C1 | CRITICAL | Phase 5 hardening missed the live `BattleStateCapture._capture_state` | combat_lab/battle_state_capture.py:289 | PROJ-271 Phase 5.4 (or PROJ-270 follow-up) |
| H1 | HIGH | `BattleScreen.start(team0, team1)` + `_build_fallback_outcome` dead but live | game/ui/screens/battle_screen.py:227, 494 | PROJ-270 follow-up |
| H2 | HIGH | `_entries_from_modifier_source` still emits `stat_key="placeholder"` | game/strategy/combat/spec_compiler.py:461 | PROJ-270 follow-up |
| H3 | HIGH | Phase 5 tests don't cover the live path | tests/unit/combat_lab/test_battle_state_capture_no_mode_kwarg.py | Part of C1 fix |
| M1 | MEDIUM | Flat shield bonus only scales with `shield_capacity_mult`, not `capacity_mult` | game/simulation/entities/ship_stats.py:464-469 | Latent; flag for next content cycle |
| M2 | MEDIUM | Dead Component-object fallback branch | game/ui/screens/battle_setup/spec_compiler.py:343-347 | Optional cleanup |
| L1 | LOW | Unused imports | game/simulation/entities/ship_stats.py:62-65 | Trivial |
| L2 | LOW | Dead `_noop_hook` | game/strategy/combat/spec_compiler.py:510 | Trivial |
| L3 | LOW | `_NUM_TEAMS = 2` unused | game/ui/screens/battle_setup/spec_compiler.py:92 | Trivial |
| L4 | LOW | Misleading "71 test callers" docstring | game/ui/screens/battle_screen.py | Resolves with H1 |

---

## Recommendation

**PROJ-271 should NOT archive until C1 is closed.** The signature deliverable of Phase 5 ("narrow the broad catch so programming errors propagate") is applied to the wrong code path — the live production path retains the exact broad catch the phase was supposed to fix. That's the kind of gap PROJ-270 Phase 9 originally surfaced in Track A (claim green, reality broken).

**PROJ-270 should stay open for H1 + H2 as a small follow-up phase** (or be archived with an explicit note that these are tracked in a successor project). Both are Rule-3 System Migration Policy violations that the acceptance audit already flagged in spirit.

Everything else is either cosmetic or latent-semantic; none blocks a content release.
