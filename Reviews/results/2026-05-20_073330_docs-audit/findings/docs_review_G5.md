# Documentation Review: Project Protocols (G5)
## Summary
- Group: Project Protocols (G5)
- Docs in Scope: 24
- Docs Actually Read: 24
- Total Findings: 24
- Critical: 0 | Major: 2 | Minor: 22

## Dead Reference Findings

All dead file references in protocol docs are **example/template references** — they appear inside code blocks, example task descriptions, or verification checklist templates illustrating what a finding looks like. None reference real infrastructure that moved. Severity: MINOR (category: intentional example).

| Doc File | Line | Dead Reference | Context |
|----------|------|---------------|---------|
| `01_initialize_project.md` | 282 | `tests/path/to/test.py` | Plan template example |
| `02_plan_protocol.md` | 94,96,112 | `tests/path/to/test.py` | TDD workflow example |
| `02_plan_protocol.md` | 136 | `tests/unit/test_feature.py` | "Adding Notes" example |
| `02_plan_protocol.md` | 179 | `tests/unit/test_user_preferences.py` | Current State example |
| `03a_continue_working.md` | 122,125,137 | `tests/path/to/test.py` | TDD cycle example |
| `03a_continue_working.md` | 218 | `tests/unit/test_cache.py` | Handoff example |
| `03b_parallel_projects.md` | 42 | `game/ui/panels/fleet_report.py` | FILES_IN_USE example |
| `09_review_project.md` | 423 | `game/strategy/old_module.py` | Agent prompt example |
| `12_create_from_test_review.md` | 401 | `tests/_helpers/ship_factory.py` | Checklist example |
| `12_create_from_test_review.md` | 425 | `game/_helpers/` | Manifest example |
| `16_create_from_legacy_audit.md` | 80 | `game/strategy/legacy/foo_manager_alias.py` | Normalization table example |
| `16_create_from_legacy_audit.md` | 264 | `game/strategy/legacy/foo_manager.py` | Verify example |
| `16_create_from_legacy_audit.md` | 325 | `game/strategy/legacy/foo_manager_alias.py` | Checklist example |
| `17_create_from_docs_audit.md` | 82,86,295 | `game/strategy/old_module.py`, `game/strategy/new_module.py` | Doc-update example |
| `17_create_from_docs_audit.md` | 245 | `game/simulation/combat/damage.py` | Verifier note example |
| `18_create_from_pattern_audit.md` | 295 | `game/ui/screens/strategy/strategy_window_manager.py` | Verifier note example |
| `18_create_from_pattern_audit.md` | 349 | `game/simulation/abilities/aggregator.py` | Checklist example |
| `19_create_from_state_audit.md` | 90 | `game/strategy/services/race_registry.py` | Normalization table example |
| `20_create_from_testcoverage_audit.md` | 152,383 | `game/strategy/treasury/treasury_engine.py` | Normalization + verifier example |

## Stale PROJ Reference Findings

All PROJ IDs referenced in protocol docs are **intentional examples** used in templates, normalization tables, or verification-check examples. Their status is irrelevant — they illustrate protocol structure, not real project status. Severity: MINOR (category: intentional example).

| Doc File | Line | PROJ Ref | Context |
|----------|------|----------|---------|
| `12_create_from_test_review.md` | 298 | PROJ-320, PROJ-321, PROJ-322 | Example project IDs from `create_project.py` output |
| `14_create_from_error_audit.md` | 115 | PROJ-308 | "bare except" history reference example |
| `15_refinement_feedback.md` | 38 | PROJ-312, PROJ-313 | Handoff example project IDs |
| `16_create_from_legacy_audit.md` | 151 | PROJ-258 | Superseded-pattern history reference |
| `17_create_from_docs_audit.md` | 83,296 | PROJ-298 | Stale PROJ reference example |
| `18_create_from_pattern_audit.md` | 102,330,351,364 | PROJ-306 | Registry DI history reference (prior cleanup project) |

## Content Accuracy Findings

### MAJOR: `14_create_from_error_audit.md` — Wrong path for json_utils.py (line 124)
- **Claim:** "If the file is `game/services/json_utils.py` itself → `OUT_OF_SCOPE` (canonical implementation)"
- **Reality:** `json_utils.py` lives at `game/core/json_utils.py`, not `game/services/json_utils.py`. The `game/services/json_utils.py` path does not exist.
- **Impact:** A verifier agent following this checklist would waste time looking for a file at the wrong path. The protocol's guidance (skip json_utils itself) remains correct, but the path is wrong.
- **Fix:** Change to `game/core/json_utils.py` (line 124). Also review line 122 which references `game/services/json_utils.py` in the `# I/O pattern` comment — same path error.

### MAJOR: All 24 protocol docs — Missing `Last verified:` line
- **Claim:** None of the protocol docs contain a `> **Last verified:** YYYY-MM-DD` line (all show `last_verified: null` in `doc_staleness.json`).
- **Impact:** No staleness tracking for procedural docs. Protocol docs can drift just as documentation docs can — if tool paths, branch strategies, or phase conventions change, stale protocol docs misdirect agents.
- **Recommendation:** Add `> **Last verified:** YYYY-MM-DD` line to each protocol doc. For protocols carrying a "Status" banner (08, 10, WORKER_TEMPLATE), the banner timestamp serves a similar purpose and may suffice.

### MINOR: `08_automated_loop_protocol.md` — Retired protocol preserved as reference (line 7–11)
- **Banner:** Status note says the three CLI loops were retired and staged at `_marked_for_deletion_2026-05-29/`. The protocol is preserved as reference.
- **Impact:** If an agent naively follows this protocol, it would try to execute retired workflows (loop_runner.ps1, refactor_plan.md). The banner is clear, but agents may not always read status banners.
- **Recommendation:** Consider moving to `Projects/protocols/archived/` or prefixing filename with `_RETIRED_` to make status visible in directory listings.

### MINOR: `10_manage_refactor_plan.md` — Retired protocol preserved as reference (line 3–6)
- **Banner:** Status note says `refactor_loop` was retired and staged at `_marked_for_deletion_2026-05-29/`. This protocol is preserved for reference.
- **Impact:** Same as above — the protocol describes managing a master refactor plan that no longer exists.
- **Recommendation:** Same as above — consider archiving.

### MINOR: `WORKER_TEMPLATE.md` — References retired Protocol 08 (line 37, 189)
- **Content:** Line 37 says "Follow Protocol 08 (Automated Loop Protocol) strictly" and line 189 says the primary protocol is `08_automated_loop_protocol.md` with a note that it is retired.
- **Impact:** The template still treats Protocol 08 as the primary execution protocol despite its retired status. The line-189 note clarifies, but the main instruction at line 37 doesn't.
- **Fix:** Update line 37 to reflect current workflow (Protocol 03a).

### MINOR: `03b_parallel_projects.md` — Example `fleet_report.py` in FILES_IN_USE example (line 42)
- **Claim:** Example shows `game/ui/panels/fleet_report.py` as a file locked by PROJ-86. This file does not exist.
- **Impact:** Minimal — clear example in a code block illustrating the registry format.
- **Recommendation:** Replace with a real file path from an actual project manifest for realism.

### MINOR: `context_config.md` — CONTEXT_WINDOW_TOKENS value (line 11)
- **Claim:** `CONTEXT_WINDOW_TOKENS: 1000000` (1M tokens). This may be outdated depending on the current model's actual context window.
- **Impact:** If the actual window is smaller, agents would NOT stop at 80% (because tokens_used / 1000000 would undercount). If larger, agents would stop earlier than necessary. The `check_context.py` script uses whatever value is here, so accuracy matters.
- **Recommendation:** Verify that 1,000,000 is current for the model in use.

## Missing Documentation

No missing documentation identified within the G5 group. All 24 protocol files listed in the scope exist and are populated.

## Doc File Coverage Verification

| Doc File | Status | Findings |
|----------|--------|----------|
| `01_initialize_project.md` | Read | 1 MINOR: template ref `tests/path/to/test.py` (line 282) |
| `02_plan_protocol.md` | Read | 4 MINOR: example refs `tests/path/to/test.py`, `tests/unit/test_feature.py`, `tests/unit/test_user_preferences.py` |
| `03a_continue_working.md` | Read | 4 MINOR: example refs `tests/path/to/test.py`, `tests/unit/test_cache.py` |
| `03b_parallel_projects.md` | Read | 1 MINOR: example ref `game/ui/panels/fleet_report.py` (line 42) |
| `03c_phase_aware_execution.md` | Read | No issues found |
| `04_audit_project.md` | Read | No issues found |
| `05_close_project.md` | Read | No issues found |
| `06_revise_project.md` | Read | No issues found |
| `07_extract_phase.md` | Read | No issues found |
| `08_automated_loop_protocol.md` | Read | 1 MINOR: retired protocol preserved as reference |
| `09_review_project.md` | Read | 1 MINOR: example ref `game/strategy/old_module.py` (line 423) |
| `10_manage_refactor_plan.md` | Read | 1 MINOR: retired protocol preserved as reference |
| `11_create_from_shrink_audit.md` | Read | No issues found |
| `12_create_from_test_review.md` | Read | 2 MINOR: example refs `tests/_helpers/ship_factory.py`, `game/_helpers/`; 3 MINOR: example PROJ-320/321/322 |
| `13_create_from_type_audit.md` | Read | No issues found |
| `14_create_from_error_audit.md` | Read | 1 MAJOR: wrong path `game/services/json_utils.py` should be `game/core/json_utils.py` (line 124); 1 MINOR: example PROJ-308 |
| `15_refinement_feedback.md` | Read | 2 MINOR: example PROJ-312, PROJ-313 |
| `16_create_from_legacy_audit.md` | Read | 3 MINOR: example refs `foo_manager_alias.py`, `foo_manager.py`; 1 MINOR: example PROJ-258 |
| `17_create_from_docs_audit.md` | Read | 5 MINOR: example refs `old_module.py`, `new_module.py`, `damage.py`; 2 MINOR: example PROJ-298 (two lines) |
| `18_create_from_pattern_audit.md` | Read | 2 MINOR: example refs `strategy_window_manager.py`, `aggregator.py`; 4 MINOR: example PROJ-306 |
| `19_create_from_state_audit.md` | Read | 1 MINOR: example ref `race_registry.py` (line 90) |
| `20_create_from_testcoverage_audit.md` | Read | 2 MINOR: example ref `treasury_engine.py` (lines 152, 383) |
| `WORKER_TEMPLATE.md` | Read | 1 MINOR: references retired Protocol 08 at line 37 |
| `context_config.md` | Read | 1 MINOR: CONTEXT_WINDOW_TOKENS may be outdated (1M) |
