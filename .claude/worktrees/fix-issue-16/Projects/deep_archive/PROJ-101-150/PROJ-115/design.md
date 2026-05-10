# PROJ-115: Design Document

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
- **Critical:** 9
- **Major:** 26
- **Selected for remediation:** 59

## Selected Findings Summary

### DUP-FND-001: Duplicated Resource Loading Logic (`load
- **Severity:** Critical
- **Location:** `game/core/resources.py:55-98`
- **Effort:** Simple

### UNK-01: Physics formula duplication between Ship
- **Severity:** Critical
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-10: Two parallel ability aggregation systems
- **Severity:** Critical
- **Location:** `Unknown`
- **Effort:** Unknown

### DUP-STR-001: Mission Command Handlers are Copy-Paste
- **Severity:** Critical
- **Location:** `game/strategy/engine/superweap`
- **Effort:** Simple

### DUP-STR-002: _calculate_maintenance_cost Duplicated A
- **Severity:** Critical
- **Location:** `game/strategy/engine/maintenan`
- **Effort:** Simple

### DUP-UI2-001: Portrait Loading Logic Duplicated in 5+
- **Severity:** Critical
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Medium

### DUP-UI2-002: Ship Image Scaling Pipeline Duplicated B
- **Severity:** Critical
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### DUP-UI1-001: BuildQueueScreen instantiation duplicate
- **Severity:** Critical
- **Location:** `game/ui/screens/strategy_scree`
- **Effort:** Simple

### DUP-UI1-002: Two separate ColumnManager classes with
- **Severity:** Critical
- **Location:** `game/ui/screens/column_manager`
- **Effort:** Medium

### DUP-FND-002: StrategyMetadataService Uses Hand-Rolled
- **Severity:** Major
- **Location:** `game/core/strategy_metadata.py`
- **Effort:** Simple

### DUP-FND-003: Repeated "Flee Away" Vector Pattern Acro
- **Severity:** Major
- **Location:** `game/ai/behaviors.py:95-101`
- **Effort:** Simple

### DUP-FND-004: Repeated Entity ID Fallback Pattern in A
- **Severity:** Major
- **Location:** `game/ai/combat_utils.py:65`
- **Effort:** Simple

### DUP-FND-005: Inline Angle Difference Calculation Inst
- **Severity:** Major
- **Location:** `game/ai/controller.py:462`
- **Effort:** Simple

### UNK-02: Hull auto-equip code duplicated between
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-03: Modifier application duplicated between
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-04: Superweapon ability classes are nearly i
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-05: Turret arc lookup logic duplicated in Mo
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-06: BeamWeaponAbility.get_damage() duplicate
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-11: Two independent formula evaluation syste
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-12: Duplicate default stats dictionaries
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-14: WeaponAbility.__init__ formula parsing r
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-15: Missile type checking uses inconsistent
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-18: Ship stat recalculation scattered across
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-19: Component data loading spread across 4 f
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Unknown

### DUP-STR-003: _find_system_at_location Duplicated in V
- **Severity:** Major
- **Location:** `game/strategy/validation/super`
- **Effort:** Simple

### DUP-STR-004: _get_harvester_info / _lookup_harvester_
- **Severity:** Major
- **Location:** `game/strategy/engine/harvestin`
- **Effort:** Simple

### DUP-STR-005: _get_storage_info / _lookup_storage_in_r
- **Severity:** Major
- **Location:** `game/strategy/engine/harvestin`
- **Effort:** Medium

### DUP-STR-006: _spawn_complex Duplicated Between Colony
- **Severity:** Major
- **Location:** `game/strategy/engine/productio`
- **Effort:** Simple

### DUP-UI2-003: Layer Color Constants Duplicated with Dr
- **Severity:** Major
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### DUP-UI2-004: BattleUIService get_engine() Null-Check
- **Severity:** Major
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Simple

### DUP-UI2-005: ShipThemeManager Internal Methods Repeat
- **Severity:** Major
- **Location:** `game/ui/assets/ship_theme_mana`
- **Effort:** Simple

### DUP-UI1-003: Screenshot capture and toast notificatio
- **Severity:** Major
- **Location:** `game/ui/screens/build_queue_sc`
- **Effort:** Simple

### DUP-UI1-004: Resource display formatting duplicated b
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_ui.py`
- **Effort:** Simple

### DUP-UI1-005: Star system/star formatting duplicated b
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_detai`
- **Effort:** Simple

### DUP-UI1-006: Event log window open methods duplicated
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_windo`
- **Effort:** Simple

### DUP-FND-006: `_resolve_resource_path` Reimplements Pr
- **Severity:** Minor
- **Location:** `game/core/resources.py:31-52`
- **Effort:** Simple

### DUP-FND-007: Repeated Zero-Vector Guard Pattern in AI
- **Severity:** Minor
- **Location:** `game/ai/behaviors.py:97-98`
- **Effort:** Simple

### DUP-FND-008: AIController._get_hp_percent and _is_in_
- **Severity:** Minor
- **Location:** `game/ai/controller.py:269-273`
- **Effort:** Simple

### DUP-FND-009: `load_data` Duplication Between Strategy
- **Severity:** Minor
- **Location:** `game/ai/strategy_manager.py:83`
- **Effort:** Medium

### UNK-07: Ability constructor data-extraction patt
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-08: Propulsion sync_data methods are near-id
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-09: ShipValidatorHelper calls validate_desig
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-13: get_total_sensor_score and get_total_ecm
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-16: Resource endurance calculations in comba
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-17: apply_modifier_effects partially duplica
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Unknown

### UNK-20: Validation result handling duplicated be
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Unknown

### DUP-STR-007: Direct Superweapon Command Handlers Foll
- **Severity:** Minor
- **Location:** `game/strategy/engine/superweap`
- **Effort:** Medium

### DUP-STR-008: Fleet Lookup Pattern Duplicated in Colon
- **Severity:** Minor
- **Location:** `game/strategy/engine/command_h`
- **Effort:** Simple

### DUP-STR-009: Superweapon Order Processing Has Repeate
- **Severity:** Minor
- **Location:** `game/strategy/engine/superweap`
- **Effort:** Simple

### DUP-UI2-006: Lazy DI Provider Pattern in Services
- **Severity:** Minor
- **Location:** `game/ui/services/component_ser`
- **Effort:** Simple

### DUP-UI2-007: Topdown Thumbnail Loading Reimplements B
- **Severity:** Minor
- **Location:** `game/ui/screens/design_image_h`
- **Effort:** Simple

### DUP-UI1-007: Thin wrapper/proxy methods in StrategyUI
- **Severity:** Minor
- **Location:** `game/ui/screens/strategy_ui.py`
- **Effort:** Simple

### DUP-UI1-008: Population count formatting (K/M suffixe
- **Severity:** Minor
- **Location:** `game/ui/screens/strategy_detai`
- **Effort:** Simple

### DUP-UI1-009: Window centering pattern repeated ~15 ti
- **Severity:** Minor
- **Location:** `game/ui/screens/strategy_scree`
- **Effort:** Simple

### DUP-FND-010: Paths Class Maintains Both String and Pa
- **Severity:** Info
- **Location:** `game/core/paths.py:46-134`
- **Effort:** Medium

### UNK-21: Persistence layer uses old Ship.from_dic
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Unknown

### DUP-STR-010: Design Data Layer Iteration Pattern Used
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Medium

### DUP-UI2-008: Hardcoded Magic Color Tuples Throughout
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** Medium

### DUP-UI1-010: StrategyDetailFormatter._format_star_sys
- **Severity:** Info
- **Location:** `game/ui/screens/strategy_detai`
- **Effort:** N


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
