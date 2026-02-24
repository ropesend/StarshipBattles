# Review Scope: Registry Consolidation Migration Plan

## Metadata
- **Date:** 2026-02-23 18:58
- **Type:** Focused Question Review
- **Description:** Complete migration plan to consolidate all registry access onto IRegistryProvider DI

## Question
**Primary:** What is the complete migration plan to consolidate all registry access onto a single canonical pattern (IRegistryProvider DI), and what would break?

## Question Classification
- **Type:** Impact + Architecture (hybrid)
- **Complexity:** High — cross-cutting concern affecting entire codebase
- **Output:** Project-ready migration plan

## Known Context
- Source review: `Reviews/results/2026-02-23_160923_general_deliberate-design-debt-audit/`
- Key finding: MOD-CORE-001 (Critical) — Three different registry access patterns
- Prior refactoring: PROJ-27, PROJ-38, PROJ-50, PROJ-58
- Current registry.py: game/core/registry.py
- IRegistryProvider protocol: game/core/protocols.py:46

## Scope Definition

### Target
- [x] Entire codebase (cross-cutting concern)

### Priorities
1. Complete inventory of all registry access call sites
2. Dependency chain analysis (who passes to whom)
3. Test infrastructure impact
4. Phased migration plan with risk assessment
5. Related cleanup items (MOD-CORE-002/004/005/006/007)

### Exclusions
- None — all files potentially affected

## Agent Configuration
**Confirmed Agent Count:** 6

### Selected Agents
| # | Agent | Role | Prefix | Output File |
|---|-------|------|--------|-------------|
| 1 | Call Site Mapper | Inventory all registry access patterns by file | CSM | csm_report.md |
| 2 | Dependency Chain Analyzer | Map registry propagation chains and composition roots | DCA | dca_report.md |
| 3 | Test Infrastructure Analyst | Test setup patterns, fixtures, isolation strategy | TIA | tia_report.md |
| 4 | Target Architecture Designer | Design end-state, migration phases | TAD | tad_report.md |
| 5 | Breaking Change Analyzer | Risk assessment per pattern change | BCA | bca_report.md |
| 6 | Related Cleanup Cataloguer | MOD-CORE-002/004/005/006/007 audit | RCC | rcc_report.md |
