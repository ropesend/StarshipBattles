# PROJ-143: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-13_223809_sweep_full-codebase-sweep](../../Reviews/results/2026-02-13_223809_sweep_full-codebase-sweep/)
- **Type:** Review
- **Date:** 2026-02-13
- **Report:** [View Full Report](../../Reviews/results/2026-02-13_223809_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 145 total findings identified.
- **Critical:** 2
- **Major:** 7
- **Selected for remediation:** 28

## Selected Findings Summary

### TCG-FND-001: AIController Integration with StrategyMa
- **Severity:** Critical
- **Location:** `game/ai/controller.py`
- **Effort:** Medium

### TCG-STR-001: Commands Module Has No Dedicated Unit Te
- **Severity:** Critical
- **Location:** `game/strategy/engine/commands.`
- **Effort:** Simple

### TCG-FND-002: TargetEvaluator Rule Types Missing Compr
- **Severity:** Major
- **Location:** `game/ai/target_evaluator.py`
- **Effort:** Medium

### TCG-FND-004: TechTree.validate_requirements() Return
- **Severity:** Major
- **Location:** `game/research/data/tech_tree.p`
- **Effort:** Simple

### UNK-01: Missing integration tests for component
- **Severity:** Major
- **Location:** `game/simulation/combat/damage_`
- **Effort:** Unknown

### UNK-04: Resource consumption during combat tick
- **Severity:** Major
- **Location:** `game/simulation/systems/resour`
- **Effort:** Unknown

### TCG-STR-004: FleetNavigationService Unit Tests Are Th
- **Severity:** Major
- **Location:** `game/strategy/services/fleet_n`
- **Effort:** Medium

### TCG-STR-005: ShipStatsCalculator Edge Cases Untested
- **Severity:** Major
- **Location:** `game/strategy/services/ship_st`
- **Effort:** Medium

### TCG-STR-006: Superweapon Command Handlers Have Limite
- **Severity:** Major
- **Location:** `game/strategy/engine/superweap`
- **Effort:** Medium

### TCG-FND-007: Resources Module (game/core/resources.py
- **Severity:** Minor
- **Location:** `game/core/resources.py`
- **Effort:** Simple

### TCG-FND-008: ResearchService.estimate_turns_to_breakt
- **Severity:** Minor
- **Location:** `game/research/systems/research`
- **Effort:** Simple

### TCG-FND-009: Profiler Test Coverage Could Be Enhanced
- **Severity:** Minor
- **Location:** `game/core/profiling.py`
- **Effort:** Simple

### TCG-FND-010: Controllable Interface Adapter Test Enha
- **Severity:** Minor
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** Simple

### UNK-02: Defense ability classes undertested in i
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Unknown

### UNK-03: Crew ability classes have minimal test c
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Unknown

### UNK-05: BattleLogger tests exist but outside sim
- **Severity:** Minor
- **Location:** `tests/unit/combat/test_battle_`
- **Effort:** Unknown

### UNK-06: Formula system exception handling edge c
- **Severity:** Minor
- **Location:** `game/simulation/formula_system`
- **Effort:** Unknown

### UNK-07: ShipStatQuerier class lacks dedicated te
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Unknown

### UNK-08: ship_serialization module could use erro
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Unknown

### TCG-STR-009: DesignMetadata Tests Are Sparse
- **Severity:** Minor
- **Location:** `game/strategy/data/design_meta`
- **Effort:** Simple

### TCG-STR-010: FleetResourceAggregator Edge Cases
- **Severity:** Minor
- **Location:** `game/strategy/data/fleet_resou`
- **Effort:** Simple

### TCG-STR-011: PlacementStrategies Lack Regression Test
- **Severity:** Minor
- **Location:** `game/strategy/generation/place`
- **Effort:** Simple

### TCG-STR-012: RegionClassifier Tests Thin
- **Severity:** Minor
- **Location:** `game/strategy/generation/regio`
- **Effort:** Simple

### TCG-STR-013: TransferValidator Missing Specific Edge
- **Severity:** Minor
- **Location:** `game/strategy/validation/trans`
- **Effort:** Simple

### TCG-STR-014: ColonizeValidator "Any Planet" Logic Com
- **Severity:** Minor
- **Location:** `game/strategy/validation/colon`
- **Effort:** Medium

### TCG-FND-012: TechRequirement Negation Logic Test Enha
- **Severity:** Info
- **Location:** `game/research/data/tech_node.p`
- **Effort:** Simple

### TCG-STR-015: Test Organization Inconsistency
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Complex

### TCG-STR-016: Mock-Heavy Tests May Miss Integration Bu
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Complex


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
