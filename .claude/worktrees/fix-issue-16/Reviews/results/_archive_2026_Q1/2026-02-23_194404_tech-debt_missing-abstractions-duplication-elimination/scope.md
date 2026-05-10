# Review Scope: Missing Abstractions & Duplication Elimination

## Metadata
- **Date:** 2026-02-23 19:44
- **Type:** Technical Debt Review
- **Description:** missing-abstractions-duplication-elimination

## Scope Definition

### Target
- [x] Entire codebase (game/ and tests/)

### Focus
Follow-up to Deliberate Design Debt Audit (Theme 4: "Missing Abstractions / Duplication").
Deep investigation of 7 primary + 4 secondary duplication clusters to produce concrete abstraction
designs with API signatures, exact call site counts, and actionable extraction plans.

### Prior Art (Agents MUST read these)
- `Reviews/results/2026-02-23_160923_general_deliberate-design-debt-audit/report.md`
- `Reviews/results/2026-02-23_160413_general_duplication-consolidation-analysis/report.md`

### Priorities
1. Quick wins first: Clusters 3, 5 (Ability._extract_value, ValidationResult factories)
2. Critical clusters: Clusters 1, 2 (UITheme, DrawingUtils) — highest line savings
3. Core infrastructure: Clusters 6, 7 (BaseCommandHandler, BaseJSONLoader)
4. Simulation-touching: Cluster 4 (SimpleMultiplierAbility) — highest risk
5. Secondary clusters: 8-11 — assess effort/benefit ratio

### Exclusions
- Test fixture duplication (Cluster 11) — assess but defer to separate effort
- No actual code changes — design and census only

## Agent Configuration
**Confirmed Agent Count:** 7

### Selected Agents
| Agent | Role | Finding Prefix | Status |
|-------|------|----------------|--------|
| ABS-SIM | Simulation Abstraction Designer (Clusters 3, 4) | ABS-SIM | Pending |
| ABS-VAL | Validation & Command Abstraction Designer (Clusters 5, 6, 10) | ABS-VAL | Pending |
| ABS-UI | UI Abstraction Designer (Clusters 1, 2, 9) | ABS-UI | Pending |
| ABS-LOAD | Loader & Serialization Abstraction Designer (Clusters 7, 8) | ABS-LOAD | Pending |
| CENSUS | Call Site Census Agent (exact counts all clusters) | CENSUS | Pending |
| DESIGN | Cross-Cutting Design Principles Agent | DESIGN | Pending |
| PRIORITY | Prioritization & Roadmap Agent | PRIORITY | Pending |

## Target Clusters
1. UI Font/Color Initialization Boilerplate (DUP-001) — 10+ files
2. Pygame Drawing Boilerplate (DUP-002) — 86+ files
3. Ability Value Extraction (DUP-003/012) — 10 ability files
4. Ability recalculate()/get_ui_rows() Boilerplate (DUP-004) — 7 ability files
5. ValidationResult Factory Methods (DUP-005) — 6 files
6. Command Handler Structure (DUP-006) — 20+ handler classes
7. JSON Loader Template (PC-015) — 9 loader classes
8. DTO to_dict/from_dict (PC-013) — 18 files (secondary)
9. Pygame Event Handling (DUP-009) — 16 files (secondary)
10. Validator Structure (PC-014) — 7 validators (secondary)
11. Test Fixture Duplication (DUP-007) — 347 files (secondary, separate effort)
