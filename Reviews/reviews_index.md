# Reviews Index

This index tracks all code reviews conducted on the Starship Battles codebase.

## Status Legend
- **In Progress** - Review currently being conducted (must be updated or closed within 60 days)
- **Completed** - Review finished, findings documented
- **Archived** - Review findings addressed or superseded
- **Abandoned (>60d)** - Review marked In Progress for >60 days with no recent activity. Bulk-closed on 2026-04-29. Result folders under `results/` remain as research archive.
- **Led to Project** - Review resulted in a PROJ-XX project

> **Sweep Reviews (retired 2026-04-29):** "Sweep" was an experimental codebase-wide multi-agent review type (see prior entries below). The 8 Sweep prompts were staged for deletion at `_marked_for_deletion_2026-05-29/Reviews/prompts/` and were never paired with a formal protocol in `Reviews/protocols/`. Existing Sweep Review entries are kept as historical record. Do not start new Sweep reviews; use the documented review types (general, test-coverage, focused-question, migration, security, performance, technical-debt, consistency, update) instead.

---

## Active Reviews
| Date | Type | Description | Status | Link |
|------|------|-------------|--------|------|
| 2026-04-05 | General Review | strategy-layer-health | In Progress | [2026-04-05_110710_general_strategy-layer-health](results/2026-04-05_110710_general_strategy-layer-health/) |
| 2026-03-24 | General Review | duplication-consolidation-full-codebase | Led to Project | [2026-03-24_200858_general_duplication-consolidation-full-codebase](results/2026-03-24_200858_general_duplication-consolidation-full-codebase/) → PROJ-224 through PROJ-228 |
| 2026-03-13 | Consistency Review | full-codebase-all-patterns | In Progress | [2026-03-13_182542_consistency_full-codebase-all-patterns](results/2026-03-13_182542_consistency_full-codebase-all-patterns/) |
| 2026-03-13 | Consistency Review | all-patterns-game-codebase | In Progress | [2026-03-13_180002_consistency_all-patterns-game-codebase](results/2026-03-13_180002_consistency_all-patterns-game-codebase/) |
| 2026-03-13 | Consistency Review | all-patterns-game-codebase | In Progress | [2026-03-13_173626_consistency_all-patterns-game-codebase](results/2026-03-13_173626_consistency_all-patterns-game-codebase/) |
| 2026-02-27 | General Review | strategy-god-classes | Abandoned (>60d) | [2026-02-27_211327_general_strategy-god-classes](results/2026-02-27_211327_general_strategy-god-classes/) |
| 2026-02-27 | General Review | circular-dependency-deferred-imports | Abandoned (>60d) | [2026-02-27_211243_general_circular-dependency-deferred-imports](results/2026-02-27_211243_general_circular-dependency-deferred-imports/) |
| 2026-02-27 | General Review | di-inconsistency-strategy | Led to Project | [2026-02-27_211222_general_di-inconsistency-strategy](results/2026-02-27_211222_general_di-inconsistency-strategy/) |
| 2026-02-27 | General Review | cyclomatic-complexity-deep-dive | Abandoned (>60d) | [2026-02-27_211154_general_cyclomatic-complexity-deep-dive](results/2026-02-27_211154_general_cyclomatic-complexity-deep-dive/) |
| 2026-02-27 | General Review | facade-bypass-layering-violations | Abandoned (>60d) | [2026-02-27_211111_general_facade-bypass-layering-violations](results/2026-02-27_211111_general_facade-bypass-layering-violations/) |
| 2026-02-27 | General Review | fleet-order-systems | Abandoned (>60d) | [2026-02-27_153151_general_fleet-order-systems](results/2026-02-27_153151_general_fleet-order-systems/) |
| 2026-02-27 | General Review | legacy-code-audit | Abandoned (>60d) | [2026-02-27_141504_general_legacy-code-audit](results/2026-02-27_141504_general_legacy-code-audit/) |
| 2026-02-27 | General Review | dead-code-elimination | Abandoned (>60d) | [2026-02-27_141459_general_dead-code-elimination](results/2026-02-27_141459_general_dead-code-elimination/) |
| 2026-02-27 | General Review | strategy-workshop-duplication | Abandoned (>60d) | [2026-02-27_141256_general_strategy-workshop-duplication](results/2026-02-27_141256_general_strategy-workshop-duplication/) |
| 2026-02-23 | Consistency Review | logger-json-pattern-standardization | Led to Project | [2026-02-23_195305_consistency_logger-json-pattern-standardization](results/2026-02-23_195305_consistency_logger-json-pattern-standardization/) |
| 2026-02-23 | Technical Debt Review | missing-abstractions-duplication-elimination | Completed | [2026-02-23_194404_tech-debt_missing-abstractions-duplication-elimination](results/2026-02-23_194404_tech-debt_missing-abstractions-duplication-elimination/) |
| 2026-02-23 | Technical Debt Review | protocol-gap-hasattr-migration | Abandoned (>60d) | [2026-02-23_193625_tech-debt_protocol-gap-hasattr-migration](results/2026-02-23_193625_tech-debt_protocol-gap-hasattr-migration/) |
| 2026-02-23 | Focused Question Review | registry-consolidation-migration | Abandoned (>60d) | [2026-02-23_185804_focused_registry-consolidation-migration](results/2026-02-23_185804_focused_registry-consolidation-migration/) |
| 2026-02-23 | Technical Debt Review | god-class-decomposition-planning | Abandoned (>60d) | [2026-02-23_182728_tech-debt_god-class-decomposition-planning](results/2026-02-23_182728_tech-debt_god-class-decomposition-planning/) |
| 2026-02-23 | Focused Question Review | exception-handling-migration-audit | Abandoned (>60d) | [2026-02-23_180421_focused_exception-handling-migration-audit](results/2026-02-23_180421_focused_exception-handling-migration-audit/) |
| 2026-02-23 | Focused Question Review | dead-code-cleanup-audit | Abandoned (>60d) | [2026-02-23_180329_focused_dead-code-cleanup-audit](results/2026-02-23_180329_focused_dead-code-cleanup-audit/) |
| 2026-02-23 | General Review | deliberate-design-debt-audit | Completed | [2026-02-23_160923_general_deliberate-design-debt-audit](results/2026-02-23_160923_general_deliberate-design-debt-audit/) |
| 2026-02-23 | General Review | duplication-consolidation-analysis | Abandoned (>60d) | [2026-02-23_160413_general_duplication-consolidation-analysis](results/2026-02-23_160413_general_duplication-consolidation-analysis/) |
| 2026-02-16 | General Review | test-suite-cleanup-v3 | Abandoned (>60d) | [2026-02-16_105410_general_test-suite-cleanup-v3](results/2026-02-16_105410_general_test-suite-cleanup-v3/) |
| 2026-02-16 | General Review | test-suite-cleanup | Abandoned (>60d) | [2026-02-16_075913_general_test-suite-cleanup](results/2026-02-16_075913_general_test-suite-cleanup/) |
| 2026-02-16 | General Review | test-suite-cleanup | Abandoned (>60d) | [2026-02-16_071059_general_test-suite-cleanup](results/2026-02-16_071059_general_test-suite-cleanup/) |
| 2026-02-14 | Sweep Review | full-codebase-sweep | Abandoned (>60d) | [2026-02-14_100116_sweep_full-codebase-sweep](results/2026-02-14_100116_sweep_full-codebase-sweep/) |
| 2026-02-14 | Sweep Review | full-codebase-sweep | Abandoned (>60d) | [2026-02-14_031258_sweep_full-codebase-sweep](results/2026-02-14_031258_sweep_full-codebase-sweep/) |
| 2026-02-13 | Sweep Review | full-codebase-sweep | Abandoned (>60d) | [2026-02-13_223809_sweep_full-codebase-sweep](results/2026-02-13_223809_sweep_full-codebase-sweep/) |
| 2026-02-13 | Sweep Review | full-codebase-sweep | Abandoned (>60d) | [2026-02-13_215604_sweep_full-codebase-sweep](results/2026-02-13_215604_sweep_full-codebase-sweep/) |
| 2026-02-13 | Sweep Review | full-codebase-sweep | Abandoned (>60d) | [2026-02-13_134059_sweep_full-codebase-sweep](results/2026-02-13_134059_sweep_full-codebase-sweep/) |
| 2026-02-13 | Sweep Review | full-codebase-sweep | Abandoned (>60d) | [2026-02-13_092036_sweep_full-codebase-sweep](results/2026-02-13_092036_sweep_full-codebase-sweep/) |
| 2026-02-13 | Sweep Review | full-codebase-sweep | Abandoned (>60d) | [2026-02-13_sweep_full-codebase-sweep](results/2026-02-13_sweep_full-codebase-sweep/) |
| 2026-02-13 | Sweep Review | full-codebase-sweep | Abandoned (>60d) | [2026-02-13_sweep_full-codebase-sweep](results/2026-02-13_sweep_full-codebase-sweep/) |
| 2026-02-11 | Sweep Review | full-codebase-sweep | Abandoned (>60d) | [2026-02-11_sweep_full-codebase-sweep](results/2026-02-11_sweep_full-codebase-sweep/) |
| 2026-02-11 | Sweep Review | full-codebase-sweep | Abandoned (>60d) | [2026-02-11_sweep_full-codebase-sweep](results/2026-02-11_sweep_full-codebase-sweep/) |
| 2026-02-10 | Sweep Review | full-codebase-sweep | Led to Project | [2026-02-10_sweep_full-codebase-sweep](results/2026-02-10_sweep_full-codebase-sweep/) |
| 2026-02-10 | General Review | resource-state-duplication-audit | Abandoned (>60d) | [2026-02-10_general_resource-state-duplication-audit](results/2026-02-10_general_resource-state-duplication-audit/) |
| 2026-02-07 | General Review | rust-bevy-migration-feasibility | Abandoned (>60d) | [2026-02-07_general_rust-bevy-migration-feasibility](results/2026-02-07_general_rust-bevy-migration-feasibility/) |
| 2026-02-01 | General Review | Full Codebase Health Check | Abandoned (>60d) | [2026-02-01_general_full-codebase-health-check](results/2026-02-01_general_full-codebase-health-check/) |
| 2026-01-31 | General Review | resource-system-legacy-audit | Abandoned (>60d) | [2026-01-31_general_resource-system-legacy-audit](results/2026-01-31_general_resource-system-legacy-audit/) |
| 2026-01-28 | General Review | maintainability-extensibility | Abandoned (>60d) | [2026-01-28_general_maintainability-extensibility](results/2026-01-28_general_maintainability-extensibility/) |
| 2026-01-28 | General Review | full-codebase-legacy-consistency-audit | Abandoned (>60d) | [2026-01-28_general_full-codebase-legacy-consistency-audit](results/2026-01-28_general_full-codebase-legacy-consistency-audit/) |
| 2026-01-28 | Consistency Review | full-codebase-patterns | Abandoned (>60d) | [2026-01-28_consistency_full-codebase-patterns](results/2026-01-28_consistency_full-codebase-patterns/) |
| 2026-01-27 | General Review | docs-health-audit | Abandoned (>60d) | [2026-01-27_general_docs-health-audit](results/2026-01-27_general_docs-health-audit/) |
| 2026-01-27 | General Review | self-contained-systems | Abandoned (>60d) | [2026-01-27_general_self-contained-systems](results/2026-01-27_general_self-contained-systems/) |
| 2026-01-27 | General Review | path-centralization | Led to Project | [2026-01-27_general_path-centralization](results/2026-01-27_general_path-centralization/) |
| 2026-01-27 | General Review | legacy-directory-assessment | Abandoned (>60d) | [2026-01-27_general_legacy-directory-assessment](results/2026-01-27_general_legacy-directory-assessment/) |
| 2026-01-27 | General Review | legacy-cleanup-verification | Abandoned (>60d) | [2026-01-27_general_legacy-cleanup-verification](results/2026-01-27_general_legacy-cleanup-verification/) |
| 2026-01-26 | Consistency Review | naming-inconsistencies | Abandoned (>60d) | [2026-01-26_consistency_naming-inconsistencies](results/2026-01-26_consistency_naming-inconsistencies/) |
| 2026-01-24 | General Review | maintainability-extensibility-health | Abandoned (>60d) | [2026-01-24_general_maintainability-extensibility-health](results/2026-01-24_general_maintainability-extensibility-health/) |
| 2026-01-23 | Test Coverage Review | full-codebase-coverage-gaps | Abandoned (>60d) | [2026-01-23_test-coverage_full-codebase-coverage-gaps](results/2026-01-23_test-coverage_full-codebase-coverage-gaps/) |

---

## Update Reviews
| Update Date | Original Review | Original Date | Progress | Link |
|-------------|-----------------|---------------|----------|------|
| 2026-01-31 | [2026-01-31_general_resource-system-legacy-audit](results/2026-01-31_general_resource-system-legacy-audit/) | 2026-01-31 | Abandoned (>60d) | [2026-01-31_update_resource-system-legacy-audit](results/2026-01-31_update_resource-system-legacy-audit/) |
| 2026-01-27 | [2026-01-26_consistency_naming-inconsistencies](results/2026-01-26_consistency_naming-inconsistencies/) | 2026-01-26 | 29% Fixed (4/14) + 6 NEW | [2026-01-27_update_naming-inconsistencies](results/2026-01-27_update_naming-inconsistencies/) |

---

## Completed Reviews
| Date | Type | Description | Key Findings | Link |
|------|------|-------------|--------------|------|
| 2026-01-24 | General Review | full-codebase-maintainability | 161 findings → **PROJ-10, 11, 12, 13** | [2026-01-24_general_full-codebase-maintainability](results/2026-01-24_general_full-codebase-maintainability/) |

---

## Reviews Leading to Projects
| Review | Project | Description |
|--------|---------|-------------|
| 2026-01-24_general_full-codebase-maintainability | PROJ-10 | Error Handling & Logging Remediation (47 findings) |
| 2026-01-24_general_full-codebase-maintainability | PROJ-11 | Architecture Layer Separation (13+ findings) |
| 2026-01-24_general_full-codebase-maintainability | PROJ-12 | God Class Decomposition (Ship, TurnEngine, RaceSetupScreen) |
| 2026-01-24_general_full-codebase-maintainability | PROJ-13 | Code Quality & Documentation (remaining findings) |
| 2026-01-27_general_path-centralization | PROJ-39 | Path Centralization (47+ hardcoded paths → single source of truth) |
| 2026-02-10_sweep_full-codebase-sweep | PROJ-106 | Architecture Layer Violations (15 findings) |
| 2026-02-10_sweep_full-codebase-sweep | PROJ-107 | Consistency & API Standardization (85 findings) |
| 2026-02-10_sweep_full-codebase-sweep | PROJ-108 | Duplication Elimination (40 findings) |
| 2026-02-10_sweep_full-codebase-sweep | PROJ-109 | Legacy Cleanup (48 findings) |
| 2026-02-10_sweep_full-codebase-sweep | PROJ-110 | Test Coverage - Core Systems (54 findings) |
| 2026-02-10_sweep_full-codebase-sweep | PROJ-111 | Test Coverage - UI & Framework (41 findings) |
| 2026-02-23_195305_consistency_logger-json-pattern-standardization | PROJ-175 | Logger & JSON Pattern Standardization (15 findings) |
| 2026-02-27_211222_general_di-inconsistency-strategy | PROJ-211 | Eradicate DI Fallback Anti-Pattern (5 phases, 13 production files) |

---

## Review Types Available

| Type | Protocol | Description |
|------|----------|-------------|
| General | [01_general_review.md](protocols/01_general_review.md) | Broad codebase health check |
| Test Coverage | [02_test_coverage_review.md](protocols/02_test_coverage_review.md) | Test completeness and quality |
| Focused Question | [03_focused_question_review.md](protocols/03_focused_question_review.md) | Answer specific questions |
| Migration | [04_migration_review.md](protocols/04_migration_review.md) | System conversion analysis |
| Security | [05_security_review.md](protocols/05_security_review.md) | Security audit |
| Performance | [06_performance_review.md](protocols/06_performance_review.md) | Performance analysis |
| Technical Debt | [07_technical_debt_review.md](protocols/07_technical_debt_review.md) | Debt assessment |
| Consistency | [08_consistency_review.md](protocols/08_consistency_review.md) | Pattern consistency |
| Update | [09_update_review.md](protocols/09_update_review.md) | Validate progress on previous review |

---

## Quick Start

1. Choose a review type from the prompts in `Reviews/prompts/`
2. Run the prompt to start the review
3. Results will be saved to `Reviews/results/<timestamp>_<type>_<description>/`

### Scripts Available

| Script | Purpose |
|--------|---------|
| `create_review.py` | Create new review folder (use `--original` for update reviews) |
| `calculate_agents.py` | Recommend agent count for scope |
| `compile_findings.py` | Generate report from agent findings |
| `compile_update_findings.py` | Generate progress report for update reviews |
| `validate_findings.py` | Extract findings from original review for validation |
| `review_to_project.py` | Create project from findings (or handoff with `--no-create-project`) |

---

*Next Review ID: Determined by timestamp*
