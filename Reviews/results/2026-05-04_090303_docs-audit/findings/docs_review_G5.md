# Documentation Review: Reviews Protocols
## Summary
- Group: Reviews Protocols
- Docs in Scope: 11
- Docs Actually Read: 11
- Total Findings: 13
- Critical: 0 | Major: 0 | Minor: 13

## Dead Reference Findings
None. All 9 script references, 6 doc references, 4 cross-file references, and all directory paths referenced in these protocols resolve correctly.

| Reference | Type | Referenced By | Status |
|-----------|------|---------------|--------|
| `Reviews/scripts/create_review.py` | Script | 00_review_core.md | Exists |
| `Reviews/scripts/calculate_agents.py` | Script | 00_review_core.md | Exists |
| `Reviews/scripts/compile_findings.py` | Script | 00_review_core.md | Exists |
| `Reviews/scripts/validate_findings.py` | Script | 00_review_core.md, 09_update_review.md | Exists |
| `Reviews/scripts/filter_validated_findings.py` | Script | 00_review_core.md | Exists |
| `Reviews/scripts/review_to_project.py` | Script | 00_review_core.md, 10_review_to_project.md | Exists |
| `Reviews/scripts/compile_update_findings.py` | Script | 09_update_review.md | Exists |
| `Projects/scripts/current_task.py` | Script | 10_review_to_project.md | Exists (accepts PROJ-XX) |
| `Projects/scripts/utils/index_manager.py` | Script | 10_review_to_project.md | Exists |
| `docs/README.md` | Doc | 00_review_core.md | Exists |
| `docs/01_ARCHITECTURE.md` | Doc | 00_review_core.md | Exists |
| `docs/02_PATTERNS.md` | Doc | 00_review_core.md | Exists |
| `docs/03_CONVENTIONS.md` | Doc | 00_review_core.md | Exists |
| `docs/systems/` | Dir | 00_review_core.md | Exists (8 files) |
| `docs/guides/` | Dir | 00_review_core.md | Exists (9 files) |
| `docs/guides/testing_infrastructure.md` | Doc | 02_test_coverage_review.md:40 | Exists |
| `Reviews/reviews_index.md` | Index | 00,01,02,03,04,05,06,07,08,09,10 | Exists ("Update Reviews" section at line 75) |
| `Projects/protocols/01_initialize_project.md` | Protocol | 00_review_core.md:332 | Exists |

## Protocol Currency Findings

### MINOR: Missing "Last verified" dates (all 11 files)
All 11 protocol files lack a "Last verified" date metadata line. This is a standard convention used across all `docs/` files (every one of 23+ tracked docs files carries a `> **Last verified:** YYYY-MM-DD` line). The protocol files should adopt the same convention so stale-protocol detection can be automated the same way stale-doc detection works.

**Affected files:**
| File | Lines |
|------|-------|
| `00_review_core.md` | 615 |
| `01_general_review.md` | 232 |
| `02_test_coverage_review.md` | 249 |
| `03_focused_question_review.md` | 317 |
| `04_migration_review.md` | 412 |
| `05_security_review.md` | 469 |
| `06_performance_review.md` | 455 |
| `07_technical_debt_review.md` | 449 |
| `08_consistency_review.md` | 492 |
| `09_update_review.md` | 517 |
| `10_review_to_project.md` | 299 |

**Recommendation:** Add `> **Last verified:** 2026-05-04` after the header block in each protocol (matching the convention in `docs/` files). Consider adding "Last verified" to the template in `00_review_core.md` at line 7 (after `## Common Phases`) as a canonical expectation.

### MINOR: Agent Role Catalog missing two roles
The Agent Role Catalog in `00_review_core.md` (lines 342-380) lists 28 agent roles, but two roles are referenced by other protocols without being catalogued:

| Role | Referenced In | Where Used |
|------|--------------|------------|
| Dependency Mapper | 03_focused_question_review.md:33, 04_migration_review.md:27-28 | "What would break" questions, migration dependency analysis |
| Test Impact Analyst | 03_focused_question_review.md:33, 04_migration_review.md:30-31 | "What would break" questions, migration test planning |

These roles are adequately described inline within the protocols that use them (04 lines 192-246), so this does not break any workflow. However, their absence from the canonical catalog in 00 makes them harder to discover and reuse across review types.

**Recommendation:** Add "Dependency Mapper" and "Test Impact Analyst" to the "Additional Specialized Agents" table in `00_review_core.md` (after line 380).

## Cross-Reference Validation
All cross-references validated successfully:
- `00_review_core.md` → `Projects/protocols/01_initialize_project.md` (line 332): Valid
- `00_review_core.md` → `Reviews/reviews_index.md` (line 32): Valid. Index has "Update Reviews" section at line 75.
- `02_test_coverage_review.md` → `docs/guides/testing_infrastructure.md` (line 40): Valid
- `09_update_review.md` → `reviews_index.md` "Update Reviews" section (lines 28, 511): Valid. Section exists in index.
- `10_review_to_project.md` → `Projects/scripts/current_task.py` (line 239): Valid. Script exists and accepts PROJ-XX argument.
- `10_review_to_project.md` → `Projects/scripts/utils/index_manager.py`, `config.py` (line 294): Valid. Both files exist.
- All inter-protocol `**Extends:** 00_review_core.md` references (protocols 01-09): Valid.

## Stale PROJ References
None. Zero PROJ-XX references found across all 11 protocol files. The protocols reference review workflows and scripts generically without coupling to specific project IDs.

## Doc File Coverage Verification
| Doc File | Status | Findings |
|----------|--------|----------|
| `00_review_core.md` | Current | MINOR: Missing "Last verified"; 2 uncatalogued agent roles (Dependency Mapper, Test Impact Analyst) |
| `01_general_review.md` | Current | MINOR: Missing "Last verified" |
| `02_test_coverage_review.md` | Current | MINOR: Missing "Last verified" |
| `03_focused_question_review.md` | Current | MINOR: Missing "Last verified" |
| `04_migration_review.md` | Current | MINOR: Missing "Last verified" |
| `05_security_review.md` | Current | MINOR: Missing "Last verified" |
| `06_performance_review.md` | Current | MINOR: Missing "Last verified" |
| `07_technical_debt_review.md` | Current | MINOR: Missing "Last verified" |
| `08_consistency_review.md` | Current | MINOR: Missing "Last verified" |
| `09_update_review.md` | Current | MINOR: Missing "Last verified" |
| `10_review_to_project.md` | Current | MINOR: Missing "Last verified" |

## Additional Observations
1. The Sweep Review workflow referenced in `reviews_index.md` as "retired 2026-04-29" is correctly excluded from all 11 protocols — no protocol references the retired Sweep review type. The index note about Sweep retirement (line 12) is consistent with the protocols listing only 8 active review types (general, test-coverage, focused-question, migration, security, performance, technical-debt, consistency) plus update.
2. Two extra scripts exist in `Reviews/scripts/` that are not referenced by any protocol: `generate_prospective_projects.py` and `approve_prospective_projects.py`. These are not dead references (nothing points to them) but forward-looking additions not yet documented in protocols.
3. All 11 protocols follow the same structural pattern (`# PROTOCOL NN: Name`, `**Role:**`, `**Extends:**`), creating a clean, navigable protocol hierarchy.
