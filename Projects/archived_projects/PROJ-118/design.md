# PROJ-118: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-11_sweep_full-codebase-sweep](../../Reviews/results/2026-02-11_sweep_full-codebase-sweep/)
- **Type:** Sweep Review (automated parallel analysis)
- **Date:** 2026-02-11
- **Report:** [View Full Report](../../Reviews/results/2026-02-11_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 396 total findings identified.
- **Critical:** 8
- **Major:** 22
- **Selected for remediation:** 51

## Selected Findings Summary

### TCG-FND-001: PhysicsBody.apply_force() and forward_ve
- **Severity:** Critical
- **Location:** `game/engine/physics.py`
- **Effort:** Simple

### TCG-FND-002: AIController.update() Integration Path N
- **Severity:** Critical
- **Location:** `game/ai/controller.py`
- **Effort:** Medium

### TCG-FND-003: CollisionSystem.process_beam_attack() Hi
- **Severity:** Critical
- **Location:** `game/engine/collision.py`
- **Effort:** Medium

### TCG-SIM-001: BattleService has no unit tests
- **Severity:** Critical
- **Location:** `game/simulation/services/battl`
- **Effort:** Medium

### TCG-SIM-002: ProjectileManager has no unit tests
- **Severity:** Critical
- **Location:** `game/simulation/projectile_man`
- **Effort:** Complex

### TCG-SIM-003: AbilityAggregator has no unit tests
- **Severity:** Critical
- **Location:** `game/simulation/entities/abili`
- **Effort:** Medium

### TCG-SIM-004: ShipPhysicsMixin has no unit tests
- **Severity:** Critical
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Medium

### TCG-SIM-005: ShipFormation has no unit tests
- **Severity:** Critical
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### TCG-FND-004: SpatialGrid.query_radius() Boundary and
- **Severity:** Major
- **Location:** `game/engine/spatial.py`
- **Effort:** Simple

### TCG-FND-005: AIController._handle_formation_master()
- **Severity:** Major
- **Location:** `game/ai/controller.py`
- **Effort:** Medium

### TCG-FND-006: AIController._check_formation_integrity(
- **Severity:** Major
- **Location:** `game/ai/controller.py`
- **Effort:** Simple

### TCG-FND-007: AIController.check_avoidance() Collision
- **Severity:** Major
- **Location:** `game/ai/controller.py`
- **Effort:** Medium

### TCG-FND-008: AIController.navigate_to() Core Navigati
- **Severity:** Major
- **Location:** `game/ai/controller.py`
- **Effort:** Simple

### TCG-FND-009: ResearchService.process_turn() Leaky Buc
- **Severity:** Major
- **Location:** `game/research/systems/research`
- **Effort:** Simple

### TCG-FND-010: TechNode.get_effective_price() Only Part
- **Severity:** Major
- **Location:** `game/research/data/tech_node.p`
- **Effort:** Simple

### TCG-FND-011: ResearchRenderer Test Coverage is Minima
- **Severity:** Major
- **Location:** `game/research/ui/research_rend`
- **Effort:** Simple

### TCG-FND-012: ResearchControlPanel.handle_event() Lack
- **Severity:** Major
- **Location:** `game/research/ui/research_cont`
- **Effort:** Medium

### TCG-FND-024: No Integration Test for AI Controller +
- **Severity:** Major
- **Location:** `tests/integration/ai_strategy/`
- **Effort:** Medium

### TCG-SIM-006: ShipSerializer has no dedicated unit tes
- **Severity:** Major
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Medium

### TCG-SIM-007: VehicleDesignService has no unit tests
- **Severity:** Major
- **Location:** `game/simulation/services/vehic`
- **Effort:** Medium

### TCG-SIM-008: ModifierService has no unit tests
- **Severity:** Major
- **Location:** `game/simulation/services/modif`
- **Effort:** Medium

### TCG-SIM-009: CombatEndurance calculations have no uni
- **Severity:** Major
- **Location:** `game/simulation/entities/comba`
- **Effort:** Simple

### TCG-SIM-010: ShipStatQuerier has no unit tests
- **Severity:** Major
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### TCG-SIM-011: ShipLoader functions have no dedicated u
- **Severity:** Major
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### TCG-SIM-012: DamageCalculator _damage_layer weighted
- **Severity:** Major
- **Location:** `game/simulation/combat/damage_`
- **Effort:** Simple

### TCG-SIM-013: BattleState serialization round-trip not
- **Severity:** Major
- **Location:** `game/simulation/battle_state.p`
- **Effort:** Medium

### TCG-SIM-024: No tests for BattleEngine.update tick pr
- **Severity:** Major
- **Location:** `game/simulation/systems/battle`
- **Effort:** Complex

### TCG-SIM-025: No boundary tests for physics formula ca
- **Severity:** Major
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### TCG-SIM-026: No tests for resource consumption during
- **Severity:** Major
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### TCG-SIM-027: ShipCombatEngine combat cooldowns only p
- **Severity:** Major
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### TCG-FND-013: StrategyManager.resolve_strategy() Defau
- **Severity:** Minor
- **Location:** `game/ai/strategy_manager.py`
- **Effort:** Simple

### TCG-FND-014: HexCoord Arithmetic with Non-HexCoord Ty
- **Severity:** Minor
- **Location:** `game/core/hex_math.py`
- **Effort:** Simple

### TCG-FND-015: pixel_to_hex() Rounding Edge Cases at Ce
- **Severity:** Minor
- **Location:** `game/core/hex_math.py`
- **Effort:** Simple

### TCG-FND-016: RegistryManager.hydrate() Partial Resour
- **Severity:** Minor
- **Location:** `game/core/registry.py`
- **Effort:** Simple

### TCG-FND-017: combat_utils.is_in_pdc_arc() Missing Tes
- **Severity:** Minor
- **Location:** `game/ai/combat_utils.py`
- **Effort:** Simple

### TCG-FND-018: TargetEvaluator._eval_speed_rule() Slowe
- **Severity:** Minor
- **Location:** `game/ai/target_evaluator.py`
- **Effort:** Simple

### TCG-FND-019: ResearchTracker.spread_rp_evenly() Does
- **Severity:** Minor
- **Location:** `game/research/data/research_tr`
- **Effort:** Simple

### TCG-SIM-014: Abilities base class (Ability) has no is
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### TCG-SIM-015: ColonizeAbility and HarvesterAbility hav
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### TCG-SIM-016: ModifierIntrospection has no unit tests
- **Severity:** Minor
- **Location:** `game/simulation/components/mod`
- **Effort:** Simple

### TCG-SIM-017: ComponentHealthManager has no unit tests
- **Severity:** Minor
- **Location:** `game/simulation/components/com`
- **Effort:** Simple

### TCG-SIM-018: ComponentResourceManager has no unit tes
- **Severity:** Minor
- **Location:** `game/simulation/components/com`
- **Effort:** Simple

### TCG-SIM-019: TechPresetLoader has no unit tests
- **Severity:** Minor
- **Location:** `game/simulation/systems/tech_p`
- **Effort:** Simple

### TCG-SIM-020: LayerData has no unit tests
- **Severity:** Minor
- **Location:** `game/simulation/entities/layer`
- **Effort:** Simple

### TCG-FND-020: Collision Edge Case Tests Use Heavy Mock
- **Severity:** Info
- **Location:** `tests/unit/engine/collision_ed`
- **Effort:** Complex

### TCG-FND-021: ScreenshotManager Tests Are Fragile Due
- **Severity:** Info
- **Location:** `tests/unit/core/test_screensho`
- **Effort:** Simple

### TCG-FND-022: StrategyMetadataService Uses Legacy Sing
- **Severity:** Info
- **Location:** `game/core/strategy_metadata.py`
- **Effort:** Simple

### TCG-FND-023: ErraticBehavior Uses `import random` Ins
- **Severity:** Info
- **Location:** `game/ai/behaviors.py`
- **Effort:** Simple

### TCG-SIM-021: Weapon ability classes tested primarily
- **Severity:** Info
- **Location:** `game/simulation/components/abi`
- **Effort:** Medium

### TCG-SIM-022: Defense ability classes tested primarily
- **Severity:** Info
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### TCG-SIM-023: ShipIO (persistence.py) inherently diffi
- **Severity:** Info
- **Location:** `game/simulation/systems/persis`
- **Effort:** N


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
