# PROJ-496 File Manifest

> Used by /proj-parallel for conflict detection.
> All paths re-verified against the live tree on 2026-05-23.
> No production-code changes expected; this project edits test files only.

## Files

| File | Type | Notes |
|------|------|-------|
| tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py | Test | Phase 1 — RISKY. PROJ-480 T3.29 (18 isinstance parametrize) + T5.14 (AST + inspect.getsource guards still present per audit_verification.md F1). |
| tests/unit/strategy/engine/session/test_persistence_adapter.py | Test | Phase 1 — RISKY. PROJ-480 T4.1 (50-line literal dict equality at `:113` / `:150` per Codex spot-check). Path retargeted from `tests/unit/strategy/persistence/`. |
| tests/unit/regressions/test_bug_regressions_2026_01.py | Test | Phase 1 — RISKY. PROJ-480 T4.11 (opaque `assert ab.amount == 25` at `:60` per Codex spot-check). Path retargeted from `tests/unit/regression/`. |
| tests/unit/simulation/systems/test_battle_engine_tick.py | Test | Phase 1 — RISKY (per Codex). PROJ-480 T5.4 (parametrize loop tests) + T5.5 (strict AI-before-ship invariant — assertion adjusted from review's weaker suggestion). |
| tests/unit/strategy/planet_atmosphere/test_generation.py | Test | Phase 1 — RISKY (per Codex). PROJ-480 T5.9 (stochastic `for _ in range(20) + if "CO2" in composition` → seeded RNG + deterministic). |
| tests/unit/strategy/formulas/test_colony_output.py | Test | Phase 1 — RISKY (per Codex). PROJ-480 T5.17 (happiness rate re-derivation → pre-computed expected value). |
| tests/regression/test_generator_crew_requirement_design.py | Test | Phase 1 — RISKY. PROJ-480 T5.8 (defensive `if layer_key is None` branches + debug print to remove — fail-fast). |
| tests/integration/resource_system/test_resource_pipeline.py | Test | Phase 2 — INTEGRATION. PROJ-480 T2.2 (73-line monolithic test → split at intermediate assertions). |
| tests/integration/strategy/test_deterministic_generation.py | Test | Phase 2 — INTEGRATION. PROJ-480 T3.31 (4 tests parametrize). |
| tests/integration/research_workflow/test_workflow.py | Test | Phase 2 — INTEGRATION. PROJ-480 T5.11 (RNG-driven conditional branches → seeded force). |
| tests/integration/gameplay_loop/test_commands_colonization.py | Test | Phase 2 — INTEGRATION. PROJ-480 T5.12 (manual retry loop → deterministic completion ticks). |
| tests/integration/test_complex_workflow.py | Test | Phase 2 — INTEGRATION. PROJ-480 T5.13 (2+ explicit retry guards → deterministic setup). |
| tests/conftest.py | Test infra | READ-ONLY |
| tests/integration/**/conftest.py | Test infra | READ-ONLY — verify before adding helpers |

## Dropped from PROJ-480 deferred list

| Task | File | Reason |
|------|------|--------|
| (none at scaffold time) | — | Codex spot-checked T4.1, T4.11, T5.14 — all live work after path retarget. Phase 0 may surface additional drops. |

## Risky-file rationale

Codex's response.md F1 named 6 files as "easy to mis-handle"; I additionally route `test_generator_crew_requirement_design.py` here because PROJ-480 T5.8 ("Remove defensive `if layer_key is None` branches + debug print. Failing fast on real bugs is better than silently skipping.") is a high-judgment task whose mistake mode is masking a real regression. Keeping all judgment-heavy single-test-body rewrites in one project lets the executor maintain the focused mindset.
