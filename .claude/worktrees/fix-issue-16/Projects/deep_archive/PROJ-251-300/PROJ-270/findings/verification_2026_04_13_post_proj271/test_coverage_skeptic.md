# PROJ-269/270/271 Test Coverage Skeptic Audit — 2026-04-13

**Auditor role:** senior test engineer, skeptical lens.
**Scope:** regression guards, ship plumbing, aura bridge, compiler behavior, integration tests, capture hardening — post-PROJ-271 closure.
**Verdict:** green suite is real but shallow. Integration tests prove the happy path end-to-end; the unit layer is load-bearing in ways the audit below exposes. Nothing blocks archival, but 3 HIGH and several MEDIUM coverage gaps would let plausible regressions ship.

---

## Executive summary

- Good: integration tests (`test_storm_shield_interference.py`, `test_flat_shield_bonus.py`, `test_suppressor_effects.py`) are real end-to-end — they construct `BattleSpec`, run `run_battle`, and assert on `BattleOutcome.max_shields`. Those are the tests that would catch the empirical Track A regression PROJ-270 Phase 9 fixed.
- Bad: the "survey" test over every `qs_*_complex` design has a hardcoded 10-design list — new complexes added to `data/designs/` will not be exercised unless a human remembers to append the list.
- Bad: key invariants (mid-battle recalc after external_stats change, destroyed provider removes aura, negative/overflow sanitization, pipeline with 3+ teams) are not tested at all.
- Bad: the `TestNoDirectBattleEngineConstruction` whitelist silently permits future regressions in 3 files and does not actually ban the pattern — it bans the pattern *outside the whitelist*. Whitelist hygiene drift is the real risk.
- Two "mock-heavy" tests do not prove real behavior because `SimpleNamespace` shims skip the `recalculate_stats()` chain. The ship-level path is separately tested, but the wiring between them (`_apply_bonuses` invokes `recalc`) has no test with a real Ship.

---

## CRITICAL findings

**None.** No finding below rises to "blocks archival". The green suite reflects genuine (if narrow) end-to-end correctness. Archive PROJ-270/271 after manual smoke.

---

## HIGH findings (real regression risk)

### H1. Survey test `test_no_placeholder_from_any_real_complex` is a hardcoded list, not a glob over `data/designs/`
**File:** `tests/unit/simulation/test_unified_entry_guard.py:540-563`
**Problem:** The loop iterates 10 known `qs_*_complex` IDs. When a content author adds (e.g.) `qs_sector_thrust_booster_complex.json` carrying a `ThrustModifier` ability that isn't in `_ABILITY_TO_STAT_KEY`, the compiler will either emit nothing (silent drop) or a placeholder entry — the survey test never touches that design, so the check passes vacuously.
**What's missing:** Glob `data/designs/qs_*_complex.json`, iterate every matching design, assert no placeholders emitted. This is the survivorship control the phase 2.5 notes claim but the code does not deliver.
**Failing test you'd write:**
```python
def test_no_placeholder_from_any_complex_on_disk(self):
    designs_dir = REPO_ROOT / "data" / "designs"
    for path in designs_dir.glob("qs_*_complex.json"):
        design_id = path.stem
        scope = "system" if "system" in design_id else "sector"
        spec = self._compile(design_id, scope, 0)
        for entries in spec.modifier_stack.per_team.values():
            placeholders = [e for e in entries if e.effect.stat_key == "placeholder"]
            assert not placeholders, f"{design_id} emitted placeholder"
```
**Phase?** PROJ-271 follow-up task (low effort, high value). Does NOT block archival — list currently matches disk — but guard integrity is load-bearing.

### H2. No test proves destroyed complex / dead provider stops providing its aura in a battle setup context
**File:** no test file exists.
**Problem:** PROJ-253 added `_providers_dirty` so aura recalculation tracks provider-component destruction. But the Battle Setup compiler path produces ModifierStack entries that live in `_external` (not `_providers`). External entries are immutable across the battle — they are added once in `initialize()` and never dropped. The decisions.md says "a booster complex gives you +25% shields for the whole battle" is correct per-design, but that design choice is nowhere stated in a test. If a future change adds per-tick dirty-check to external entries (e.g., because a complex gets destroyed mid-battle in some future feature), nothing will catch a regression in the invariant.
**What's missing:** A "lock the invariant" test asserting external entries persist across an entire battle simulation, AND a complementary test that physical-complex destruction (when/if that becomes a feature) correctly routes through the dirty flag.
**Failing test you'd write:** `test_external_modifier_entries_persist_across_many_ticks` — build a battle with a suppressor, step 100 ticks, assert `_external` list unchanged and `ship.external_stats['shield_capacity_mult']` stable.
**Phase?** Document as invariant; file a test-debt ticket. Not blocking.

### H3. `TestNoDirectBattleEngineConstruction` whitelist grows silently
**File:** `tests/unit/simulation/test_unified_entry_guard.py:64-68`
**Problem:** Whitelist is hardcoded. Acceptable for current 3 files. BUT: a new file appearing in the whitelist (say someone adds a "legacy adapter" module) is just as invisible as a real regression — there is no meta-test asserting the whitelist stays at 3 entries, nor any test that the whitelisted files are the *only* callers of `BattleEngine(...)`. A PR that adds a 4th whitelist entry will pass review more easily than a PR that deletes one.
**Failing test you'd write:** `assert len(self.WHITELIST_FILES) == 3` with a comment pointing to this audit. Forces whitelist growth to become a deliberate, reviewed act.
**Phase?** Part of a test-hygiene ticket. Low effort.

---

## MEDIUM findings (maintainability / invariant coverage)

### M1. Ship plumbing tests omit real-ship edge cases
**File:** `tests/unit/simulation/entities/test_ship_shield_bonus_add.py`
Missing edges from the skeptic brief:
- **Negative `shield_bonus_add`**: `test_flat_bonus_raises_max_shields` asserts +50; nothing asserts behavior when the external bridge accidentally emits `-50` (e.g., a suppressor future authoring mistake). Currently the code `ship.max_shields += -50` would yield 450 — probably intentional, but undefined. Lock the contract either way.
- **Very large bonus** (overflow): N/A in Python (no int overflow) but test of `1e18` would prove `max_shields` stays a float and no divide-by-zero in downstream pipeline.
- **Mid-battle recalc after damage**: `ship.current_shields == ship.max_shields` on first recalc, but if `ship.current_shields = 100` (post-damage) and the bonus is applied for the first time via `recalculate_stats`, does `current_shields` correctly bump by the delta (`ship_stats.py:621`), or does it stay at 100 while max jumps to 550? The code path exists but no test exercises it with `shield_bonus_add` specifically.
- **Component destruction then recalc with flat bonus still active**: shield generator destroyed → `acc['max_shields']` drops → flat bonus added on top → is this (0 + 50) × mult or (0 base + 50 × mult)? This is exactly the "virtual shield component" semantic from decisions.md, and it's the most likely place semantic drift will be introduced.
- **Per-component `capacity_mult` + ship-level `shield_capacity_mult` + `shield_bonus_add`** triple-stacking. The decisions.md locks (base + flat) × mult, but no test has all three concurrent.
**Failing tests you'd write:** one per edge listed above (5 tests, all ~15 lines).
**Phase?** PROJ-271 Phase 1 backfill or PROJ-272 scope.

### M2. FleetAuraManager additive tests never exercise stack_groups
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`
**Problem:** `_recalculate` runs two-phase aggregation (same-group MAX, different-group SUM) for `_providers`, but `_external` entries at lines 299-309 just `+=`. The skeptic brief's suspicion is correct: external entries ignore `stack_group`. That MAY be intentional (planet auras are a single source), but it's nowhere tested nor asserted. A future change wiring `stack_group` into external aggregation would either silently break 3 existing tests (likely) or silently pass while behavior changes. Add: test that two external entries with the same stack_group SUM (current behavior, locks it) — today.
**Failing test you'd write:** `test_two_external_entries_same_stack_group_sum` — two `shield_bonus_add` entries both `stack_group="planet_shield"`, assert result is +50+30=+80 (not MAX 50). This locks the current behavior. If semantics change later, the test has to be explicitly updated.

### M3. 3+ team battles not covered
**Problem:** `FleetAuraManager._recalculate` iterates `team_ids = {s.team_id for s in ships}` — handles N teams. Battle Setup is hardcoded 2 teams (`_NUM_TEAMS = 2` in spec_compiler.py), but the strategy layer presumably supports more. The `_route_team_for_scope` function uses `1 - owner_team` — if Battle Setup expands to 3+ teams, suppressors route wrong. Nothing catches this.
**What's missing:** A test at `tests/unit/simulation/combat/` with 3 teams, per_team[0]=buff, per_team[1]=debuff, per_team[2]=empty — verify all three are isolated. Additionally, an explicit future-guard test `assert _NUM_TEAMS == 2, "Extending Battle Setup to 3 teams requires rewriting _route_team_for_scope"`.

### M4. `register_ship` / `unregister_ship` bypass external_stats propagation
**File:** `game/simulation/combat/fleet_aura_manager.py:183-211`
**Problem:** `register_ship` calls `_recalculate(all_ships)` which DOES call `_apply_bonuses` (line 311), so a late-arriving ship should get the external aura. BUT: the brief asks whether `register_ship` correctly applies existing aura. The test file `test_fleet_aura_register.py` doesn't check `external_stats`. No test proves a ship added mid-battle gets `shield_bonus_add` on its external_stats.
**Failing test you'd write:** `test_register_ship_receives_existing_external_modifier` — build mgr with shield_bonus_add=50 on team 0, register a new team-0 ship, assert its external_stats contains the bonus.

### M5. Compiler coverage gaps — malformed input
**File:** `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`
Missing from the skeptic brief:
- Complex `design_id` not in `data/designs/` — `_load_complex_design` returns None and `_complex_to_entries` returns `[]`. No test asserts graceful skip (no crash, no log spam beyond the existing warning).
- Complex with component ID not in registry — `components_registry.get(comp_id)` returns None, loop `continue`s. No test.
- `ability_data` as a malformed string — `_extract_scope` handles non-dict by returning "self"; `_extract_ability_value` returns 0.0 or 1.0. No test.
- Two complexes on the same side with mixed booster+suppressor — no test that both land in the correct per_team buckets simultaneously.
- Same complex toggled on BOTH side 0 AND side 1 — no test that entries emit to distinct per_team[0] + per_team[1] buckets (and that scope routing is re-evaluated per owner).
**Failing tests:** 5 tests at ~10 lines each.

### M6. `test_flat_shield_bonus.py` and `test_suppressor_effects.py` lack triple-stack + routing-together coverage
**Files:** the two integration files
Missing:
- Both flat bonus + shield_capacity_mult + damage_mult active concurrently — the pipeline-ordering test uses flat+shield_cap only.
- Booster on side 0 + suppressor on side 0 targeting team 1 — single side emits entries to both `per_team[0]` (booster) and `per_team[1]` (suppressor) in the same battle.
- Ship with NO shield components receiving flat bonus through a real battle (unit test covers this at `test_ship_shield_bonus_add.py`, but not integration — flat bonus should still appear as max_shields in ShipOutcome). Proves serialization path.
**Failing tests:** 3 tests, ~20 lines each.

### M7. `capture_battle_state` hardening omits concurrency + battle_id drift
**File:** `tests/unit/combat_lab/test_battle_state_capture_no_mode_kwarg.py`
**Problem:** 5 tests cover mode-kwarg deletion + narrowed except. Uncovered:
- Race: two tests with the same `test_id` writing initial + final files concurrently — filename collision behavior is unspecified. Batch runners could hit this.
- Battle_id drift: initial-state capture uses pre-battle `engine`, final uses post-battle `engine` — no test asserts that both files carry the same `battle_id` (so the UI can pair them).
- Empty `test_id` / None — graceful skip or path traversal?
**Failing tests:** 3 tests.

### M8. Strategy compiler placeholder still exists in `_entries_from_modifier_source`
**File:** `game/strategy/combat/spec_compiler.py` (per decisions.md + Phase 4.4 note)
**Problem:** The phase note says this remaining placeholder path is "explicitly out of PROJ-271 scope". Acceptable, but no pytest skip marker documents this. Future contributors reading `TestNoPlaceholderStatKeyInStrategyCompiler` will assume placeholder is fully eradicated when it is not. The unified-entry guard should either cover the remaining path or carry a `# pragma: known-gap` with a ticket reference.

---

## LOW findings (style / documentation)

### L1. `TestNoPlaceholderStatKeyInBattleSetupCompiler` regex is brittle to helper extraction
**File:** `tests/unit/simulation/test_unified_entry_guard.py:472-487`
**Problem:** Regex scans the body of `_complex_to_entries`. If someone factors `_make_effect()` out to a sibling helper, the placeholder literal could live outside the function body and the text guard passes while behavior regresses. The behavioral tests in `TestBattleSetupCompilerBehavioralStatKeys` compensate, so this is LOW. Document that the pair of text-guard + behavioral survey is the contract, and that either can stand alone.

### L2. `TestNoLegacyCompatibleComments` regex explicitly narrow
**File:** `tests/unit/simulation/test_unified_entry_guard.py:135-184`
**Problem:** Comment says "`deprecated` is NOT banned broadly" — correct (preserves `@deprecated` decorator, etc.). But the narrowed regex means `# kept for legacy callers` is now uncaught. The scope narrowing is intentional per the test's docstring. LOW because the narrowing is documented in the test itself.

### L3. `TestNoLegacyScenarioSetup` AST excludes `base.py` and `__init__.py`
**File:** `tests/unit/simulation/test_unified_entry_guard.py:111-115`
**Problem:** If someone adds `def setup(engine):` to `base.py`, the guard misses it. The comment in the test acknowledges this is intentional (docstring examples show legacy signature). LOW — `base.py` is reviewed tightly, but one-line belt-and-braces: after the exclusion, add a targeted assertion that `base.py` contains `def custom_setup` (the replacement pattern) and does NOT contain `def setup(self, battle_engine)` as a non-docstring method.

### L4. `test_battle_setup_shield_suppressor_targets_opponent_team` builds test teams, not UI-state teams
**File:** `tests/integration/strategy/combat/test_suppressor_effects.py:120-147`
**Problem:** The test compiles the modifier stack from `BattleSetupState`, then uses that stack with hand-built `TeamSpec`s (not the UI state's teams, which are empty in the minimal fixture). This is honest — the test comments explain it — but it means the "test_battle_setup_*" name is misleading; it's really testing the modifier-lift path, not the full UI-to-battle flow. Rename or add a second test that uses real UI fleets.

---

## Missing coverage entirely (skeptic brief Section 7 items)

### N1. No UI-level test that Battle Results screen renders modifier numbers
**Problem:** The brief asks "does the flat bonus's NUMBERS actually render on Battle Results?" — no test in `tests/unit/ui/screens/` inspects a rendered or data-layer Battle Results screen with a suppressor/booster/flat-bonus active. `extract_battle_results(outcome)` tests confirm the data flows, but no test confirms the UI shows the modified `max_shields` rather than the pre-modifier value. Practical impact: low (the numbers are baked into `ShipOutcome.max_shields` which the UI reads), but worth a defensive assertion.

### N2. No save/load roundtrip with external_stats
**Problem:** Per PROJ-270 Goals, "ships enter unmutated" — external_stats is composed fresh at battle start and discarded at battle end. The save format should NOT serialize external_stats. There is NO test asserting this. If someone adds external_stats to ship serialization, the in-game ship outside-of-battle would carry phantom bonuses. This is the exact class of bug Rule 3 (clean-sheet design) warns against.
**Failing test:**
```python
def test_ship_external_stats_not_serialized_to_json():
    ship = ShipSerializer.from_dict(_design_with_shields(), registries=fresh_registries)
    ship.external_stats = {"shield_bonus_add": 50.0}
    data = ShipSerializer.to_dict(ship)
    # external_stats is battle-scoped; must not leak into save
    assert "external_stats" not in data
```
**Phase?** New ticket — this guards a real invariant that docs assume but no test enforces.

### N3. Mock-heavy FleetAuraManager tests don't prove the recalculate_stats chain fires
**File:** `test_fleet_aura_manager_modifier_stack.py` uses `SimpleNamespace` ships. The `_apply_bonuses` method at line 352-354 guards `recalc = getattr(ship, 'recalculate_stats', None)` — SimpleNamespace returns None → recalc is skipped. So these tests prove external_stats is WRITTEN but NOT that the downstream ship recomputes max_shields.
**Where the chain IS proven:** integration tests `test_flat_shield_bonus_appears_in_outcome` — real Ship, real run_battle, real max_shields=575. That's sufficient, but the gap in the unit layer is worth documenting: `SimpleNamespace` + `external_stats=...` does NOT mean the bridge is end-to-end correct. A two-line unit test with a MagicMock `recalculate_stats` + `assert_called_once` would lock "bridge invokes recalc when stats change" deterministically. Currently this lives inside the integration test; it would take a long time to diagnose a regression via integration-test failure.
**Failing test:**
```python
def test_apply_bonuses_invokes_recalc_on_real_ship_stand_in():
    mock_recalc = MagicMock()
    ship = SimpleNamespace(team_id=0, is_alive=True, is_derelict=False,
        fleet_attack_bonus=0.0, fleet_defense_bonus=0.0,
        external_stats={}, get_all_components=lambda: [],
        recalculate_stats=mock_recalc)
    stack = ModifierStack(per_team={0: (_add_entry("s", "shield_bonus_add", 50.0),)}, global_=())
    FleetAuraManager().initialize([ship], modifier_stack=stack)
    mock_recalc.assert_called_once()
```

---

## "Audit found nothing" — sections with genuinely solid coverage

- **`SHIELD_BONUS_ADD` enum wiring** — 4 tests in `test_stat_key.py` cover exists/value/default/dict inclusion. Complete.
- **Pipeline ordering `(base + flat) × mult`** — locked at 3 layers: ship-level unit test, FleetAuraManager unit test, integration test. Solid coverage.
- **Scope routing for current 2-team Battle Setup** — 4 behavioral tests + survey test + integration tests. For the 2-team case, coverage is thorough.
- **`capture_battle_state` mode-kwarg deletion** — 2 text guards + 1 OSError-narrowing guard + 1 propagation guard + 1 graceful-OSError guard. Forensic coverage.
- **`_placeholder_warned_sources` dedupe logic** — `test_shield_bonus_add_does_not_log_placeholder_warning` uses caplog. Correct.
- **`extract_battle_results` signature guard** — `TestExtractBattleResultsConsumesOutcome` asserts `params[0] == "outcome"` + no engine import. Exactly the right test.
- **`BattleController.get_outcome` + `set_spec` existence** — regex guards in `TestBattleControllerEmitsOutcome`. Sufficient.

---

## Recommended follow-up ticket (NOT a PROJ-270 or 271 phase)

Create PROJ-272 or a test-debt ticket covering:
- H1 (glob-based survey)
- M1 (real-ship edge cases)
- M4 (register_ship external_stats)
- M5 (compiler malformed input)
- M6 (triple-stack integration)
- N2 (external_stats save/load)
- N3 (unit test for recalc invocation)

Estimate: 1 day of TDD work. No architectural changes. All tests over currently-working code — no production fixes expected.

---

## Archival recommendation

PROJ-271 ready to archive after manual smoke. PROJ-270 ready to archive after manual smoke. Neither should block on findings above; but the H-section items should become a filed ticket before archival, so they don't evaporate into tribal knowledge.
