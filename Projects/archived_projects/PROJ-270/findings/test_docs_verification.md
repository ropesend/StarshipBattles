# Test Quality + Doc Consistency — Round 2 Verification

## Verdict

**Tests mostly solid — some doc drift remains → 1-2 new PROJ-270 phases warranted.**

Phase 11/12 empirically did most of what it claimed. The AST rewrite is real, the
behavioral compiler tests are real, `TestOutcomeContentAssertions` uses no mocks
and would fail on `teams=()`. The boundary tests exist but one locks implementation
rather than convention. The doc "banner then legacy examples" strategy is weak —
contributors reading Step 4 of the how-to guide still see `def setup(self,
battle_engine)` as the canonical shape. One architecture doc is still internally
inconsistent with another.

All 85 of the guard + outcome + boundary + battle-config + battle-results tests
ran green (`pytest … --tb=short -q` → 85 passed).

---

## Verified Claims

- **Phase 11.1 (outcome content assertions):** `TestOutcomeContentAssertions.test_outcome_has_populated_teams_after_real_run` at `tests/unit/simulation/battle_controller/test_outcome_emission.py:241-327` uses a real `run_battle` with a real `BattleSpec` + real `ShipSerializer` + a real `AIControllerFactory`. No MagicMock of `BattleOutcome`. Asserts `len(outcome.teams)==2`, `duration_ticks>0`, `end_reason is not None`, `seed==1`, per-ship `instance_id` and `status is not None`. A regression to `BattleOutcome(teams=())` would fail on the first assert.
- **Phase 11.2 (AST-based scenario setup guard):** `tests/unit/simulation/test_unified_entry_guard.py:105-132` uses `ast.walk` + `isinstance(node, (FunctionDef, AsyncFunctionDef))` + `node.name == "setup"`. Catches any `def setup(...)` regardless of parameter name — robust to `battle_engine → engine` rename.
- **Phase 11.4 (behavioral stat_keys):** `TestStrategyCompilerBehavioralStatKeys` (lines 362-414) calls `_entries_from_environmental_effects(EnvironmentalEffects(shield_capacity_mult=0.5))` and `_entries_from_fleet_combat_modifiers(FleetCombatModifiers(...))` directly. Asserts enum string values, not text patterns. Kept alongside the regex guard (both run green).
- **Phase 11.7 CircleBoundary:** `test_origin_returns_plus_x_direction` at `tests/unit/simulation/combat/test_boundary.py:298-313` locks the documented `+x` convention from `boundary.py:177` ("Ambiguous — pick +x direction by convention"). Genuine convention-lock.
- **Phase 12.5 (test_executor.py docstring):** corrected to "compiles the spec, drives `BattleController.start_from_spec`, and wires the scenario's initial_state + custom_setup".
- **NOQA hygiene:** only 2 production-code uses (`ability_manager.py:287`, `battle_screen.py:116`), both with narrative context. No proliferation.
- **Guard duplication:** `TestNoLegacyScenarioSetup` (AST over `combat_lab/scenarios/*.py`) and `test_template_no_legacy_setup.py` (`hasattr` over 5 template classes + `TestScenario`) scan different surfaces. Not redundant.
- **`extract_outcome` called once:** `test_get_outcome_extracted_only_once` enforces the invariant.
- **test_battle_results_data.py:** zero MagicMock, 35 real asserts across 227 lines — builds real `BattleOutcome` / `ShipOutcome` / `TeamOutcome` DTOs. Solid.
- **Pre-existing failures:** skeptic's inventory matches reality; none attributable to PROJ-270.
- **`test_simulation_adapter_storms.py`:** the "nonexistent file" claim is **wrong** — `tests/unit/strategy/adapters/test_simulation_adapter_storms.py` exists (6971 bytes, 118 lines). Phase 11.11's deferral of "fix the nonexistent reference" was resolving a non-problem. Residual-only: `phase_11_checklist.md:99` still lists the removal as TODO.

---

## Failed / Partial Claims

### Claim: Phase 11.8 — simulation_testing.md "banner warns readers, legacy examples kept as historical reference"
**Severity:** High
**Applies to:** New PROJ-270 phase
**Evidence:** The banner at lines 5-22 announces the new API. But lines 164-202 (section 3, "TestScenario Class") still show `def setup(self, battle_engine)` + `def update(self, battle_engine)` as the canonical class shape with no inline deprecation flag. **Section 4 "Writing Simulation Tests" step 4 ("Create the scenario class in the appropriate file") implicitly points back at the legacy example.** A new contributor reading top-down will see the banner, then 3 sections later see an unmarked canonical shape and use it — the banner is a weaker signal than "rewrite the example". The skeptic's original recommended fix was to rewrite the section, not flag it.
**Recommended Phase 13 task:** rewrite §3 "TestScenario Class" to show `to_spec` / `wire_ships` / `custom_setup` / `validate(outcome, telemetry)` and delete the legacy 164-202 block (or move it to a collapsed historical appendix). Banner can then shrink to a one-line historical pointer.

### Claim: Phase 11.9 — COMBAT_LAB_DOCUMENTATION.md base-class updated
**Severity:** High
**Applies to:** New PROJ-270 phase
**Evidence:** Line 283-299 (base class section) **is correctly updated** to show `to_spec` / `wire_ships` / `custom_setup` / `validate(outcome, telemetry)`. But line 668 (in a later "Writing a New Test" section) still shows a full `def setup(self, battle_engine)` example — 9 lines of deleted-API usage with `battle_engine.start([self.attacker], [self.target], seed=...)`. Same banner-vs-example dichotomy as simulation_testing.md.
**Recommended Phase 13 task:** rewrite the "Writing a New Test" example block at lines 651-710 (approx) to match the current base-class API.

### Claim: Phase 11.10 — combat_simulation.md "already updated in prior session — spot-check confirms current"
**Severity:** Medium
**Applies to:** New PROJ-270 phase
**Evidence:** `docs/systems/combat_simulation.md:316-323` still describes the wrapper as "configure → set_spec → add_ships → start → tick-from-game-loop → get_outcome" and the PROJ-270 Phase 4 annotation covers `set_spec` but NOT the Phase 10 `start_from_spec` unified entry. Contradicts `docs/01_ARCHITECTURE.md:373-379` which correctly describes `controller.start_from_spec(spec, ai_factory, ship_builder)`. Phase 11.10's claim "spot-check confirms current" is inaccurate — the doc was not updated for Phase 10.
**Recommended Phase 13 task:** align `combat_simulation.md` Visual-mode section with `01_ARCHITECTURE.md` Battle Flow (single-call `start_from_spec`, get_outcome at end).

### Claim: Phase 11.3 — legacy-compatible pattern widened
**Severity:** Medium
**Applies to:** New PROJ-270 phase (small) or acceptable trim with explicit scope note
**Evidence:** Pattern NARROWED, not widened. Phase 11 pattern: `legacy-compatible | legacy state — kept | retained for [the] transition | kept for transition | deprecated-but-live`. Skeptic recommended: `(?i)(legacy[-\s]?(compat|shim|state)|retained (for|while)|backward[-\s]?compat(ibility)?|deprecated[-\s]?but|kept for (transition|backward|legacy))`. A new agent writing `# backward compat shim for X` or `# retained while we migrate` would slip past. Scope WAS expanded to all of `game` + `combat_lab` (skeptic wanted that, confirmed on line 153-154). The rationale for narrowing (avoid PROJ-238/210 noise) is defensible if documented in the plan's closing notes as an explicit scope decision — but the checklist framed it as "widened" which is inaccurate.
**Recommended Phase 13 task (if any):** either (a) widen the pattern per skeptic and NOQA-annotate the ~pre-existing offenders found in the expanded pattern (1-hour sweep), or (b) rename the checklist entry from "widened" to "focused on PROJ-269/270-specific idioms" for accurate bookkeeping.

### Claim: Phase 11.7 — RectBoundary "convention" locked
**Severity:** Low
**Applies to:** Acceptable / trivial
**Evidence:** `TestRectBoundaryCenterDeterminism.test_center_of_square_returns_left_edge` locks "left wins at center" — but `boundary.py` has no code-docstring commitment to this order. The test docstring says "Documenting this so future refactors don't silently change behavior" which is implementation-locking, not contract-locking. Acceptable as a regression guard, but mislabeled as a "documented convention" lock. If a future refactor changes the `min(...)` check order to `(top, right, bottom, left)`, this test would fail for no good reason.
**Recommended Phase 13 task:** either add a `boundary.py` docstring clause to RectBoundary saying "equidistant returns left-edge by convention" (making it a real contract), or loosen the test to just assert edge.x**2 + edge.y**2 is one of 4 valid equidistant points.

### Claim: Phase 12.6 — FORBIDDEN_FIELDS sunset dates enforced
**Severity:** Low
**Applies to:** Acceptable / trivial
**Evidence:** `FORBIDDEN_FIELDS_WITH_SUNSET` at `test_battle_config.py:77-86` carries dates but nothing in test code reads them. The `test_no_forbidden_fields` method uses `FORBIDDEN_FIELDS = frozenset(FORBIDDEN_FIELDS_WITH_SUNSET.keys())` — sunset dates are pure documentation. The "sunset" concept is a future-agent-will-notice convention, not a programmatic trigger. That's fine — but calling it "enforced" overstates it. No failure mode exists today; a 2027-dated agent won't see any warning.
**Recommended Phase 13 task:** optional — add a `test_sunset_dates_not_passed` assertion that warns (not fails) when today > sunset, so CI surfaces the cleanup reminder.

### Claim: `23 design patterns` hardcoded
**Severity:** Low
**Applies to:** Acceptable / trivial
**Evidence:** `docs/README.md:17` and `:66` still show hardcoded "23 design patterns". Phase 11.11 explicitly deferred this.

### Claim: 37 `PROJ-270 Phase` markers in production code
**Severity:** Low
**Applies to:** Acceptable pre-archival / optional cleanup
**Evidence:** 18 production files carry 37 `PROJ-270 Phase N` inline comments. They document the history of why a method exists; harmless as long as the phase checklists are archived alongside. If PROJ-270 is archived to `deep_archive/`, a few agents reading the markers will hit broken links when they cross-reference `PROJ-270/phase_X_checklist.md`. Not a test/doc bug but noted.

### Claim: `.agent_reports/proj-269-270-skeptic-review/` preserved into findings
**Severity:** Low
**Applies to:** Acceptable
**Evidence:** The skeptic reports at `.agent_reports/proj-269-270-skeptic-review/` are not referenced by plan.md or the phase checklists — they'll be deleted along with the rest of `.agent_reports/`. The key findings ARE captured in Phase 11 checklist Notes (narrowed pattern rationale, legacy banner decision, etc.). Skeptic report isn't load-bearing for future reference. Could optionally copy into `PROJ-270/findings/` before archival per-protocol, but not strictly required.

---

## Summary

- **Tests:** genuinely hardened. AST walker, behavioral compiler tests, and real-spec outcome integration test all hold up under adversarial inspection. Guard + boundary + battle-config + battle-results suites (85 tests) all green.
- **Docs:** partially hardened. Banner-based fixes in `simulation_testing.md` and `COMBAT_LAB_DOCUMENTATION.md` leave the canonical example blocks below the banner untouched — a new reader following the natural top-down path still lands on the deleted API. `combat_simulation.md` wasn't actually updated for Phase 10 despite the checklist claiming it was current.
- **Recommended:** one focused Phase 13 that rewrites the two how-to example blocks + aligns `combat_simulation.md:316-323` with the Phase 10 `start_from_spec` reality. All other residuals are cosmetic/acceptable.
