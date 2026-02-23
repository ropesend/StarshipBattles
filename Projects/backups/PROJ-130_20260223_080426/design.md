# PROJ-130: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-13_sweep_full-codebase-sweep](../../Reviews/results/2026-02-13_sweep_full-codebase-sweep/)
- **Type:** Review
- **Date:** 2026-02-13
- **Report:** [View Full Report](../../Reviews/results/2026-02-13_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 245 total findings identified.
- **Critical:** 2
- **Major:** 13
- **Selected for remediation:** 31

## Selected Findings Summary

### TCG-FND-001: CollisionSystem raycasting edge cases un
- **Severity:** Critical
- **Location:** `game/engine/collision.py`
- **Effort:** Medium

### TCG-FND-002: ResearchService leaky bucket algorithm e
- **Severity:** Critical
- **Location:** `game/research/systems/research`
- **Effort:** Medium

### TCG-FND-003: AIController navigation and avoidance al
- **Severity:** Major
- **Location:** `game/ai/controller.py`
- **Effort:** Medium

### TCG-FND-004: TargetEvaluator rule evaluation missing
- **Severity:** Major
- **Location:** `game/ai/target_evaluator.py`
- **Effort:** Simple

### TCG-FND-005: Behavior classes missing state transitio
- **Severity:** Major
- **Location:** `game/ai/behaviors.py`
- **Effort:** Medium

### TCG-FND-006: TechTree validation methods lack test co
- **Severity:** Major
- **Location:** `game/research/data/tech_tree.p`
- **Effort:** Simple

### TCG-FND-007: TechRequirement fuzzy resolution edge ca
- **Severity:** Major
- **Location:** `game/research/data/tech_node.p`
- **Effort:** Simple

### TCG-FND-009: SpatialGrid query_radius does not filter
- **Severity:** Major
- **Location:** `game/engine/spatial.py`
- **Effort:** Simple

### TCG-SIM-004: designs.py Lacks Any Test Coverage
- **Severity:** Major
- **Location:** `game/simulation/designs.py`
- **Effort:** Simple

### TCG-SIM-005: resource_manager.py (ResourceRegistry) M
- **Severity:** Major
- **Location:** `game/simulation/systems/resour`
- **Effort:** Medium

### TCG-SIM-006: battle_controller.py Missing State Trans
- **Severity:** Major
- **Location:** `game/simulation/battle_control`
- **Effort:** Medium

### TCG-SIM-007: formula_system.py Edge Cases Not Tested
- **Severity:** Major
- **Location:** `game/simulation/formula_system`
- **Effort:** Simple

### TCG-SIM-008: projectile_manager.py Missing Guidance S
- **Severity:** Major
- **Location:** `game/simulation/projectile_man`
- **Effort:** Medium

### TCG-SIM-009: battle_state.py Serialization Round-Trip
- **Severity:** Major
- **Location:** `game/simulation/battle_state.p`
- **Effort:** Medium

### TCG-SIM-010: combat/damage_calculator.py Missing Armo
- **Severity:** Major
- **Location:** `game/simulation/combat/damage_`
- **Effort:** Medium

### TCG-FND-010: PhysicsBody x/y property setters not tes
- **Severity:** Minor
- **Location:** `game/engine/physics.py`
- **Effort:** Simple

### TCG-FND-011: ShipControllableAdapter formation method
- **Severity:** Minor
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** Simple

### TCG-FND-012: Logger module singleton behavior not ful
- **Severity:** Minor
- **Location:** `game/core/logger.py`
- **Effort:** Simple

### TCG-FND-013: Config module edge cases for clamp value
- **Severity:** Minor
- **Location:** `game/core/config.py`
- **Effort:** Simple

### TCG-FND-014: Error code enum completeness not verifie
- **Severity:** Minor
- **Location:** `game/core/error_codes.py`
- **Effort:** Simple

### TCG-FND-015: Profiling decorator edge cases not teste
- **Severity:** Minor
- **Location:** `game/core/profiling.py`
- **Effort:** Simple

### TCG-FND-016: hex_ring negative radius input not teste
- **Severity:** Minor
- **Location:** `game/core/hex_math.py`
- **Effort:** Simple

### TCG-SIM-011: components/abilities/weapons.py Tests Sp
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### TCG-SIM-012: components/abilities/defense.py Tests La
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### TCG-SIM-013: components/abilities/propulsion.py Missi
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### TCG-SIM-015: interfaces/ai_controller.py Interface Te
- **Severity:** Minor
- **Location:** `game/simulation/interfaces/ai_`
- **Effort:** Simple

### TCG-SIM-016: validation/ship_validator.py Missing Com
- **Severity:** Minor
- **Location:** `game/simulation/validation/shi`
- **Effort:** Simple

### TCG-FND-017: Research system UI rendering tests use m
- **Severity:** Info
- **Location:** `game/research/ui/research_rend`
- **Effort:** N

### TCG-FND-018: Test file organization follows productio
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### TCG-SIM-017: Test Organization Could Use Consolidatio
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### TCG-SIM-018: No Performance/Load Tests for Simulation
- **Severity:** Info
- **Location:** `game/simulation/systems/battle`
- **Effort:** N


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
