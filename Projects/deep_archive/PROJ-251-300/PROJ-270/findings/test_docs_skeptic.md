# Test Quality + Documentation Rigor — Skeptical Audit

## Verdict

**Tests solid-but-gameable, docs materially drifting.** The 28 regression guards
mostly do what they claim, but several are grep-based and defeatable by trivial
paraphrase, one outcome-plumbing test has zero content assertions, integration
coverage is thinner than claimed, and the CircleBoundary origin-ambiguity path
documented in code has no test. Documentation has two concrete drift cases
(one in a Step-4 how-to guide, one in Combat Lab reference) plus an undocumented
API shape (`configure(config, spec=...)`). The three "pre-existing" test failures
are genuinely pre-existing — not rebranded.

---

## Test-Quality Findings

### Finding: `test_outcome_emission.py` asserts plumbing, not outcome content
**Severity:** High
**Location:** `c:/Dev/Starship Battles/tests/unit/simulation/battle_controller/test_outcome_emission.py`

**What's wrong:** Every positive test uses `MagicMock(name="BattleOutcome")` as the fake outcome and asserts `controller.get_outcome() is mock_outcome`. Zero assertions on `.teams`, `.end_reason`, `.duration_ticks`, `ShipStatus`, or any real field.

**Evidence:** `grep -c "assert.*outcome.teams\|outcome\.end_reason\|outcome\.duration_ticks" → 0`. A regression where `extract_outcome` returns `BattleOutcome(teams=(), duration_ticks=0)` would pass every test in this file. The controller-side plumbing is verified; the contract the docs advertise ("every battle produces a real outcome with team results") is not.

**Recommended fix:** Add one end-to-end test with a real (not mocked) engine running a short battle via `configure(config, spec=spec)` + `start()` + `update()`-loop, and assert `outcome.teams` is non-empty and `ship_outcome.status in {SURVIVED, DESTROYED, RETREATED}`.

---

### Finding: `TestNoLegacyCompatibleComments` scope gap + paraphrase-gameable
**Severity:** Medium
**Location:** `tests/unit/simulation/test_unified_entry_guard.py:119-133`

**What's wrong:** (1) Regex is literal `Legacy-compatible|retained for` — trivially defeated by "legacy compat", "retained while", "kept for backwards-compat", "deprecated-but-live", etc. (2) Scope is only `game/simulation`, `game/ui`, `combat_lab` — does NOT cover `game/strategy`, `game/ai`, `game/core`. A regression in the strategy compiler or AI layer escapes the guard entirely.

**Evidence:** Pattern `re.compile(r"Legacy-compatible|retained for")`. Scope: `_iter_py_files("game/simulation", "game/ui", "combat_lab", ...)`. No coverage of `game/strategy`, `game/ai`, `game/core`.

**Recommended fix:** Extend scope to all of `game/` and `combat_lab/`. Broaden pattern to `(?i)legacy[-\s]?(compat|shim)|retained (for|while)|backward[-\s]?compat|deprecated[-\s]?but`. Better: convert to AST-based — scan module docstrings for `# PROJ-xxx: retained` style decorations. Grep alone is fragile by design.

---

### Finding: `TestNoLegacyScenarioSetup` defeatable by parameter rename
**Severity:** Medium
**Location:** `tests/unit/simulation/test_unified_entry_guard.py:105-116`

**What's wrong:** Regex is `^\s*def\s+setup\s*\(\s*self\s*,\s*battle_engine\b`. A developer can reintroduce the method as `def setup(self, engine):` or `def setup(self, eng):` and slip past — the legacy code pattern is re-enabled without the guard firing. The companion `test_template_no_legacy_setup.py` uses `hasattr(Class, 'setup')` which IS robust, but the unified-entry-guard version is redundantly weaker than its sibling.

**Recommended fix:** Replace the regex with an AST walker that finds any `def setup(self, *anything*)` in scenario modules — or simply delete the redundant guard and rely on `test_template_no_legacy_setup.py::test_*_has_no_setup` which uses `hasattr`.

---

### Finding: CircleBoundary origin-ambiguity convention has no test
**Severity:** Medium
**Location:** `game/simulation/combat/boundary.py:158-165`

**What's wrong:** The code documents "Ambiguous — pick +x direction by convention" returning `Vector2(self.radius, 0.0)` when `pos=origin`. `tests/unit/simulation/combat/test_boundary.py::TestCircleBoundaryClosestEdgePoint` has 3 cases (outside/inside/on-perimeter) but NONE at origin. Anyone refactoring the ambiguity resolution to e.g. `(0, radius)` or `raise ValueError` would silently break the contract the docstring advertises. Same gap exists for `RectBoundary` at origin (equidistant from all 4 edges) — no test pins the deterministic choice.

**Recommended fix:** Add `test_closest_edge_point_at_origin_returns_plus_x` for CircleBoundary and a similar determinism-pin test for RectBoundary.

---

### Finding: `configure(config, spec=spec)` has only 3 unit tests; no multi-shape coverage
**Severity:** Low-Medium
**Location:** `tests/unit/simulation/battle_controller/test_outcome_emission.py::TestBattleControllerConfigureAcceptsSpec`

**What's wrong:** The PROJ-270 Task 4.2/4.3 tighten introduces a new two-shape API: `configure(config)` and `configure(config, spec=spec)`. Only 3 tests exercise it. No test covers: (a) reconfiguring with a different spec after a previous spec was set (should spec be replaced or cleared?); (b) `configure(config, spec=None)` passing `spec=None` explicitly vs omitting; (c) calling `set_spec(spec2)` after `configure(config, spec=spec1)` — does spec1 survive? The docstring doesn't specify. If a caller chains these unexpectedly, behavior is undefined.

**Recommended fix:** Add tests for the reconfigure-with-new-spec path and the explicit-None path.

---

### Finding: Integration coverage for spec compilers is asymmetric
**Severity:** Medium
**Location:** `tests/integration/`

**What's wrong:** `build_strategy_battle_spec` is integration-tested end-to-end via `tests/integration/strategy/combat/test_damage_persistence.py`. `build_manual_battle_spec` (Battle Setup production path) and `build_test_battle_spec` (Combat Lab) have NO integration coverage — only unit-tested compilers. The acceptance-audit claim "every production battle produces an outcome" is not exercised by any integration test that runs Battle Setup's or Combat Lab's compiler through `run_battle` end-to-end. PROJ-270 Phase 6.5 end-to-end storm/modifier integration test was explicitly deferred to PROJ-271. Also: the initiating prompt mentioned `test_simulation_adapter_storms.py` — no such file exists.

**Recommended fix:** Add `tests/integration/simulation/test_entry_points_emit_outcome.py` with one test per production compiler — each compiles a real-fixture spec, runs `run_battle`, asserts `outcome.teams` populated and `end_reason` set. Would catch "extract_outcome regresses to empty teams" bugs that all 28 guards currently miss.

---

### Finding: `test_unified_entry_guard.py::TestNoPlaceholderStatKeyInStrategyCompiler` is regex-on-source-text
**Severity:** Low
**Location:** `test_unified_entry_guard.py:258-306`

**What's wrong:** The test reads the compiler file as text and regex-searches function bodies for `"placeholder"` within blocks bounded by `if shield_mult != 1.0:` ... `if damage_mult`. If someone reformats the code or renames the variables, the lookbehind anchor breaks and the test silently loses its guard value (asserting on empty body). Robust version would import the function, call it with a synthetic fleet-modifier fixture, and assert `entry.stat_key == StatKey.SHIELD_CAPACITY_MULT`.

**Recommended fix:** Replace text-regex with a behavioral test: call `_entries_from_fleet_combat_modifiers(FleetCombatModifiers(shield_mult=0.5, damage_mult=0.5, ...))` and assert the resulting `ModifierEntry.stat_key` values.

---

## Documentation Findings

### Finding: `docs/guides/simulation_testing.md` teaches the deleted API
**Severity:** Critical
**Location:** `c:/Dev/Starship Battles/docs/guides/simulation_testing.md:167-174`

**What's wrong:** The Step-4 how-to guide linked from `docs/README.md` shows `def setup(self, battle_engine):` and `def update(self, battle_engine):` as the canonical scenario pattern. This is exactly the signature PROJ-270 Phase 1.3 deleted. No "historical" banner. A new contributor following the doc would write code that violates the unified-entry guard. The top-of-doc sentence "Both environments use the exact same `BattleEngine` code" also reads as if the old world still applies.

**Evidence:** Lines 167-174 contain the verbatim deleted method signature with no migration note. Contrast with `combat_lab/scenarios/TEMPLATE_MIGRATION_GUIDE.md` which IS marked historical (lines 1-10).

**Recommended fix:** Rewrite the "TestScenario Class" section to show `to_spec(registries)` + `wire_ships(ships_by_role, engine, initial_state)` + `custom_setup(...)` + `validate(outcome, telemetry)`. Cross-link to the canonical example scenario.

---

### Finding: `combat_lab/COMBAT_LAB_DOCUMENTATION.md` base-class description is out of sync
**Severity:** High
**Location:** `c:/Dev/Starship Battles/combat_lab/COMBAT_LAB_DOCUMENTATION.md:283-289`

**What's wrong:** Although the top-of-file banner says the code migrated to `to_spec()`, the "base class" section still lists `def setup(self, battle_engine): raise NotImplementedError` as the canonical method. A reader who lands on the base-class section (without reading the banner) is directly misled about the API.

**Recommended fix:** Update the base-class snippet to match the current `TestScenario` API, or delete it and reference the authoritative `docs/systems/combat_simulation.md`.

---

### Finding: `docs/01_ARCHITECTURE.md` Battle Flow describes old two-step API
**Severity:** Medium
**Location:** `c:/Dev/Starship Battles/docs/01_ARCHITECTURE.md:375-378`; also `docs/systems/combat_simulation.md:319`

**What's wrong:** Both docs describe the visual-mode flow as `controller.set_spec(spec)` — the pre-Task-4.2/4.3 API. The tightened PROJ-270 API is `controller.configure(config, spec=spec)` as a single call. `set_spec` still exists but is no longer the production entry shape. Production call sites (`app.py`, `test_lab/screen.py`, `test_execution_service.py`) all use `configure(config, spec=...)` per the Closure-session notes.

**Recommended fix:** Update both occurrences to describe `configure(config, spec=spec)` as primary, `set_spec(spec)` as the alternate for unit tests.

---

### Finding: `docs/README.md` "Last verified" is accurate but "23 design patterns" count drift-risk
**Severity:** Low
**Location:** `c:/Dev/Starship Battles/docs/README.md:17`, `63`

**What's wrong:** "23 design patterns" appears twice. The file `02_PATTERNS.md` lists pattern 23 at the ToC. The TOC entry for §13 reads "Spec Compiler + run_battle" (correct). No immediate wrongness, but the hardcoded count will drift the next time a pattern is added. Not a PROJ-270 bug, noted for cleanliness.

**Recommended fix:** Replace "23 design patterns" with "design patterns" or derive the count programmatically.

---

### Finding: `plan.md` references a nonexistent test file
**Severity:** Low
**Location:** The initiating prompt + PROJ-270 plan context mentions `tests/integration/simulation/test_simulation_adapter_storms.py`.

**What's wrong:** That file does not exist. Only `tests/unit/strategy/conflict_resolution/test_storm_integration.py` (pure mocks) and `tests/integration/strategy/test_turn_storms.py` exist. Claim about "the only integration test for Track A is X and Y" misidentifies Y.

**Recommended fix:** Either create the promised integration test or remove the claim from the plan's Current-State section.

---

## Pre-existing Failures — Actually Pre-existing?

Verified against git history. All six are legitimately pre-existing, **not** PROJ-269/270 fallout:

| Failure | Origin | Pre-existing? |
|---|---|---|
| `test_bug_15_screenshot_strategy.py::test_build_queue_f12_event_calls_take_screenshot` | Build-queue UI regression, unrelated to run_battle / spec compilers | Yes |
| `test_build_queue_formatting.py::test_actions_header_uses_textbox` | Build-queue UI regression | Yes |
| `test_build_queue_queue_data_source.py::TestBuildQueueColumns::test_expected_columns_present` | Build-queue UI regression | Yes |
| `test_ai_protocols.py` ImportError (`IFormationMaster` from `game.ai.protocols`) | Test file from PROJ-192 Phase 1; protocol renamed/deleted in later AI refactor unrelated to battle flow | Yes |
| `test_behavior_units.py` ImportError | Same AI refactor lineage | Yes |
| `test_build_order_command_handler.py` ImportError | Build-order refactor (PROJ-207/212), pre-dates PROJ-269 | Yes |

None reference `run_battle`, `BattleSpec`, `BattleOutcome`, `BattleController`, spec compilers, or RetreatManager. They would have failed at any point in the last several months of main-branch history. **Verdict:** not rebranded — genuinely pre-existing, correctly excluded from PROJ-270 scope.

---

## Summary

- **28 guards run, 28 green** — but at least 3 are regex-fragile and 1 (outcome-emission) asserts plumbing only. An AST-based rewrite would strengthen the contract meaningfully.
- **Integration coverage is real but asymmetric** — `build_strategy_battle_spec` is integrated-tested; the other two compilers aren't.
- **Two production docs still teach the deleted `setup(battle_engine)` API** (`docs/guides/simulation_testing.md` and `combat_lab/COMBAT_LAB_DOCUMENTATION.md` base-class section) — this is the most user-facing drift.
- **Two architecture docs describe the pre-tighten `set_spec` flow** instead of the current `configure(config, spec=...)` — minor but real.
- **Pre-existing failures are legitimately pre-existing** — no funny business.
- **CircleBoundary origin-ambiguity has zero test coverage** despite being a documented convention.

The "spirit of the refactor" is largely achieved in the code. The "specific goals" claim that tests + docs are locked is mostly true but has measurable gaps, especially in the two user-facing how-to docs that the README itself points readers to.
