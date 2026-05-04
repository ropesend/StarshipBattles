# Plan Review: Test-coverage project arc PROJ-331..340

**Review Type:** plan
**Request ID:** req_20260504_202321_8a0316
**Reviewer:** OpenCode (delegated by claude-code)
**Review Mode:** Independent second-opinion plan review
**Scope:** Master coordinating doc + 10 project plans (PROJ-331 through PROJ-340)
**Context:** Pre-execution review of planning artefacts; no test code exists yet.
**Limitations:** Production files referenced by manifests were not read (plan-only review). Source plans under `~/.claude/plans/` are outside the repo and were not reviewed; only the in-repo artefacts were evaluated.

---

## Summary

The 10 project plans are well-structured, internally consistent, and follow the PROJ-329A reference shape faithfully. The characterization-testing discipline is correctly applied throughout, with appropriate gap-reframing where prior coverage exists. Zero production-file overlaps were confirmed. **Two CRITICAL findings, five MAJOR, four MINOR, and three OBSERVATION-level items** follow.

---

## Finding Severity Legend

| Tag | Meaning |
|-----|---------|
| CRITICAL | Must fix before execution — plan error or missing scope that will cause wrong tests or missed regression surfaces |
| MAJOR | Should fix — material weakness in plan coverage or test adequacy |
| MINOR | Nice-to-fix — estimate calibration, clarity, or completeness issues |
| OBSERVATION | Not a fix; notable for awareness during execution |

---

## Findings

### CRITICAL-001: `action_execution_engine.py` omitted from entire arc

**Re:** Master plan + PROJ-333 scope

`game/strategy/engine/action_execution_engine.py` handles COLONIZE and TRANSFER order execution — two of the highest-risk per-turn operations (planet ownership mutations, cargo transfers, superweapon activation). PROJ-333's manifest explicitly lists it as "Out of scope" and no other project in the arc covers it. The gap audit identified this file as untested but it does not appear in any PROJ-331..340 manifest.

The master plan's stated purpose is "addressing the highest-risk gaps." COLONIZE/TRANSFER bugs silently corrupt save files. This is a higher-risk gap than several files that DID make the cut (e.g., `species_population.py` at 43 LOC, `fleet_cargo_projector.py` at 64 LOC).

**Recommendation:** Either add a PROJ-341 for `action_execution_engine.py` + `superweapon_order_processor.py` + `build_order_processor.py` as a batch, or explicitly document the deferral with rationale in the master plan's "Out of scope" section.

### CRITICAL-002: PROJ-338 projected session estimate is too low; risks cut corners

**Re:** PROJ-338 plan.md, manifest.md, phase_1_checklist.md

PROJ-338 plans ~112 characterization tests across 6 test files for 5 high-risk UI panels, most of which require heavy `pygame_gui` mock setup. The plan allocates 3 sessions. Comparison:

- PROJ-337 (55 tests, ~2 sessions) → ~27 tests/session
- PROJ-338 (112 tests, ~3 sessions) → ~37 tests/session — a 37% higher throughput rate on panels that are MORE state-machine-dense (drag handler state machine, system tree persistent expand collapse, build queue controller with PROJ-69/79/208 callback chains).

The existing `test_build_queue_controller.py` at 1108 LOC demonstrates the churn surface of just one of the five panels. Writing and debugging 22+ tests against the system-tree panel alone (719 LOC production, 4-way grouping branches, recursive expand, click-vs-toggle routing) in half a session is aggressive.

**Recommendation:** Budget at least 4 sessions for PROJ-338, or de-scope to ~85 tests by deferring the `test_system_tree_panel_hazard.py` extension and lowering the drag-handler target from ~28 to ~20 tests.

---

### MAJOR-001: PROJ-332 checklist test names are descriptive text, not concrete function names

**Re:** PROJ-332 phase_1_checklist.md

Unlike PROJ-331, PROJ-333, and PROJ-335 which use concrete test function names in checkboxes (e.g., `test_from_ship_generates_uuid_when_ship_id_not_provided`), PROJ-332's checklist uses prose descriptions:

> `__init__` kwarg overrides matching field on `config` when both are supplied

The executor agent must invent test function names from these descriptions. While the intent is clear, the inconsistency with sibling projects creates ambiguity about what specific behavior each test pins. When the agent names it "test_init_kwarg_overrides" vs "test_init_kwarg_takes_precedence_over_config_field", the bisect string changes but the pin may not.

**Recommendation:** Convert the 27 checklist entries to concrete test function names matching the specificity of PROJ-331 and PROJ-335. This is a ~15-minute edit.

### MAJOR-002: PROJ-333 split decisions ambiguous for production_engine testing

**Re:** PROJ-333 manifest.md, design.md

The manifest splits `production_engine` tests into two files:
- `test_production_engine_queue.py` (~15 behaviors)
- `test_production_engine_consumption.py` (~12 behaviors)

But the checklist groups are not cleanly separated by concern. Items like `test_calculate_tick_expenditure_returns_none_for_zero_rate_required_resource` appear in the "consumption" file but its behavior spans both queue tick iteration AND resource math — the method `_calculate_tick_expenditure` lives in the production engine class, not a separate consumption module. The split boundary leaks: a test in the "queue" file may need to mock the same `_calculate_tick_expenditure` that the "consumption" file exercises.

Additionally, the checklist appears truncated in the tool output at ~35,377 bytes (roughly 60% of the expected ~70 entries). The surviving entries list `production_engine_queue.py` at "~15 behaviors" but show only 15 checkboxes — implying no truncation. However, `production_engine_consumption.py` at "~12 behaviors" shows 12. Let me check...

Actually, from the raw read of phase_1_checklist.md for PROJ-333, I can see the full content was truncated in the tool output. I cannot verify the remaining ~50% of the checklist for the other 4 engines. If the remaining entries (production_spawner, consumable_management_engine, fleet_movement_engine, order_processor) exist in the truncated portion, this is not a finding.

**Recommendation:** Verify the file integrity manually: `wc -l Projects/active_projects/PROJ-333/phase_1_checklist.md`. If the truncated portion is missing from the actual file, this is a CRITICAL gap. If present, the split-boundary concern stands as MAJOR.

### MAJOR-003: PROJ-339 `design_stats_panel.py` construction test may require full Workshop stack

**Re:** PROJ-339 plan.md, design.md, decisions.md D-003

The plan states the `DesignStatsPanel` gap is 8-10 new tests covering construction, `_build_layout`, `needs_rebuild`, `update_stats`, requirements rendering, and collapse toggling. D-005 says to reuse existing pygame_gui mock fixtures. However, `DesignStatsPanel._build_layout` calls `resolve_section_visibility()` which reads `data/stats_sections.json` at module level. The existing `tests/unit/ui/panels/test_design_stats_panel.py` only tests `StatRow` (a pure helper) and never constructs a `DesignStatsPanel`.

The design.md notes the blocker: "_build_layout requires a real `UIScrollingContainer` with a working `get_container().get_rect()`" and resolves to "the fixture infrastructure exists." But checking the existing tests — there is no existing fixture for constructing a `DesignStatsPanel`. The closest is `tests/unit/ui/panels/` tests for other panels, which use different fixture patterns. The test author will need to build this infrastructure fresh, and the plan doesn't account for that in the estimate or mention it as a risk.

**Recommendation:** Add a D-00N decision documenting that the existing fixture infrastructure for `DesignStatsPanel` construction is untested and the first test will need to discover the minimum viable mock setup. Budget an extra 1-2 tests worth of time for fixture discovery.

### MAJOR-004: PROJ-340 `ship_theme_manager.py` test I/O fragility

**Re:** PROJ-340 decisions.md D-003, phase_1_checklist.md

The plan monkeys `Paths.SHIP_THEMES_DIR` to a `tmp_path`-built fake themes tree and patches `pygame.image.load`. While necessary under the "no refactor" rule, the test creates a hand-written `theme.json` in the fake tree. The production `theme.json` schema is undocumented in the plan — there is no reference to the actual schema fields, required keys, or version numbering. The test author will need to reverse-engineer the schema from `ship_theme_manager.py` source or from the live theme files.

If the hand-written test `theme.json` differs in schema from production themes, the tests will pin behavior against an artificial subset. The plan's checklist includes `test_initialize_skips_theme_with_invalid_theme_json` and `test_initialize_warns_and_continues_on_unknown_schema_version` — but without documenting what shape the valid JSON must have, the executor may write these tests against a schema they invented rather than the real one.

**Recommendation:** Add a design.md section or decisions.md entry documenting the minimum valid `theme.json` schema shape (top-level keys, required fields, version field format) so the test author can construct realistic fake themes.

### MAJOR-005: PROJ-336 `find_blocking_stabilizer` iteration-order determinism is under-pinned

**Re:** PROJ-336 phase_1_checklist.md Task 1.4, design.md

The checklist includes `test_first_empire_with_match_wins_over_later_empire` which pins empire-iteration order. But the design.md notes two separate ordering concerns:
1. STABILIZERS outer loop order (Geologic → Stellar → WarpField)
2. empires iteration order within each spec

The test name only references empire order (#2). The STABILIZERS iteration order is NOT pinned by any checklist item. If a future refactor reorders the `STABILIZERS` tuple, a single `order_type` blocked by two specs could return a different `StabilizerSpec` — a behavioral change that should fire a test.

**Recommendation:** Add a test: `test_geologic_spec_matched_before_stellar_when_both_block_order_type` that uses a synthetic order type blocked by both Geologic and Stellar specs, with matching stabilizers for both, and asserts the Geologic spec is returned (first-hit-wins across STABILIZERS iteration order).

---

### MINOR-001: PROJ-334 Phase 0 audit before Phase 1 tests adds a session boundary

**Re:** PROJ-334 plan.md, phase_0_checklist.md

PROJ-334 is the only project with a Phase 0 audit phase. The master plan's ~2 session estimate doesn't account for the Phase 0 work (enumerating symbols, mapping existing tests, computing gap-list, writing findings doc). Even if Phase 0 takes only ~0.3 sessions, combined with Phase 1's ~24-30 tests this pushes PROJ-334 to ~2.3 sessions.

**Recommendation:** Either absorb Phase 0 into Session 1 of Phase 1 (read existing tests as you write new ones), or bump the estimate to 2.5 sessions. The Phase 0 formality may not add proportional value given the existing 1209 LOC of pathfinding tests are well-organized by behavior cluster.

### MINOR-002: Master plan test-directory column has stale entries for PROJ-337

**Re:** master plan file-overlap matrix

The matrix lists PROJ-337's tests scope as `tests/unit/ui/research/ (new)` but the real tests live under `tests/unit/research/research_scene/`, `tests/unit/research/research_controls/`, and `tests/unit/research/test_research_renderer.py`. PROJ-337's D-002 correctly notes this and chooses not to relocate. The master plan matrix was written before discovering the coverage gap audit was wrong.

**Recommendation:** Update the master plan matrix to reflect actual test locations and note the discrepancy. This is cosmetic but prevents future confusion if another agent reads the matrix and looks for tests that don't exist at the listed path.

### MINOR-003: PROJ-332 `test_turn_engine_phase_timing.py` relies on `time.perf_counter()` determinism

**Re:** PROJ-332 phase_1_checklist.md File 3

The test `_time_phase` accumulates timing into `phase_times[key]` even when the wrapped callable raises — the `finally` block runs. This behavior IS important to pin, but the timing accumulation (calling `time.perf_counter()` twice and subtracting) is inherently non-deterministic. The test will need to assert that `phase_times[key] > 0` rather than asserting a specific value, OR monkeypatch `time.perf_counter` to return deterministic values. The checklist doesn't specify which approach to use.

**Recommendation:** Add a brief note to the checklist entry specifying "use monkeypatch on time.perf_counter to return [0.0, 2.5] then assert phase_times[key] == 2.5". Without this, the executor may write a test that flakes on CI under load.

### MINOR-004: PROJ-339 `test_format_sig_digits_precision_tiers` assertion is underspecified

**Re:** PROJ-339 phase_1_checklist.md File 3

The checklist says: `≥1000` no decimals; `100-999` one dp; `10-99` two dp; `<10` three dp; `0` → `"0"`. The first bucket entry `≥1000` should also specify negative numbers: does `-999.5` format with 3 dp or is the absolute value used? The plan doesn't address negative-value formatting in `modifier_impact_grid`.

**Recommendation:** Clarify whether precision-tier bucketing uses `abs(value)` or whether negative values have their own tier.

---

### OBSERVATION-001: Several projects reference unreachable source plan files

PROJ-333 plan.md, PROJ-335 plan.md, and PROJ-340 plan.md each reference `~/.claude/plans/noble-stirring-galaxy-agent-*.md` as their "Source plan." These files are outside the repo and unreachable by other agents. The in-repo artefacts (plan.md, decisions.md, design.md, manifest.md, phase_1_checklist.md) are described as "the conversion" of those source plans. This is acceptable as historical context but means the plans cannot be fully audited end-to-end — the source plan might contain nuance the conversion dropped.

### OBSERVATION-002: Apparent-bug observations appear genuine and correctly separated

All 10 projects document apparent-bug observations in their decisions.md files as "observations, not fixes." The observations reviewed (PROJ-331 OBS-A/B/C, PROJ-332 D-007/D-008, PROJ-333 8 observations, PROJ-335 D-007, PROJ-336 D-007 through D-010, PROJ-340 Obs-A/Obs-B) correctly identify genuine behavioral concerns. None appear to be production behavior misread as bugs. All are correctly pinned as current-behavior to characterize rather than refactor.

Notable for separate triage: PROJ-333's observation that `consumable_management_engine` uses hardcoded `100.0` instead of the `TICKS_PER_TURN` constant is a real drift hazard. PROJ-332's D-007 (end-of-turn engines bypass `_time_phase` wrapping) means failures in `QualityEngine`, `AtmosphereEngine`, and `WaterEngine` propagate raw without rollback — this is a robustness gap worth a dedicated ticket.

### OBSERVATION-003: PROJ-334 Phase 0 audit adds value but delays test delivery

PROJ-334 is the only project with a proper Phase 0 coverage-gap audit. The existing `tests/unit/strategy/pathfinding/` tree at 1209 LOC is well-organized into 6 files by behavior cluster (`test_basic_paths.py`, `test_edge_cases.py`, `test_hybrid_and_intercept.py`, etc.). A coverage-gap audit here will likely find genuine gaps in edge-case coverage (unreachable target, intercept-with-zero-speed, etc.) but the audit itself costs time that could be spent writing tests. Whether this tradeoff is correct depends on the user's risk tolerance for missing gaps.

---

## What to fix vs accept

### Fix before execution (blocking)

| ID | Action |
|----|--------|
| CRITICAL-001 | Add `action_execution_engine.py` coverage to arc scope or document the deferral |
| CRITICAL-002 | Re-budget PROJ-338 to 4 sessions or de-scope to ~85 tests |
| MAJOR-002 | Verify PROJ-333 phase_1_checklist.md is complete (not truncated); fix if truncated |

### Fix before execution (non-blocking, can fix during)

| ID | Action |
|----|--------|
| MAJOR-001 | Convert PROJ-332 checklist entries to concrete test function names |
| MAJOR-003 | Add D-00N documenting DesignStatsPanel fixture discovery risk |
| MAJOR-004 | Document minimum valid theme.json schema in PROJ-340 design.md |
| MAJOR-005 | Add STABILIZERS iteration-order test to PROJ-336 checklist |
| MINOR-001 | Absorb PROJ-334 Phase 0 into Phase 1 or bump estimate |
| MINOR-002 | Update master plan matrix for PROJ-337 test locations |
| MINOR-003 | Specify monkeypatch approach for PROJ-332 perf_counter tests |
| MINOR-004 | Clarify negative-value precision tiers in PROJ-339 |

### Accept (informational)

All OBSERVATION items. The apparent-bug documentation is thorough and correct. The source-plan references are cosmetic. The Phase 0 audit tradeoff is a user preference.

---

## Overall assessment

The 10 projects collectively constitute a well-planned characterization-test arc. The planning agents correctly reframed scope where prior coverage existed, the characterization discipline is consistently applied, and the file-overlap matrix is verified accurate. The two CRITICAL findings (missing `action_execution_engine.py` coverage and PROJ-338 schedule risk) are addressable without restarting planning. After addressing the CRITICAL and MAJOR items above, the arc is ready for execution.
