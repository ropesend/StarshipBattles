# Duplication & Fragmentation Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 71
- **Total Issues Found:** 8
- **Critical:** 0 | **Major:** 3 | **Minor:** 4 | **Info:** 1

## Findings

#### MAJOR: Serialization to_dict/from_dict Pattern Repetition in BattleState
**ID:** DUP-SIM-001
**Location:** `game/simulation/battle_state.py:40-59` (ComponentState), `game/simulation/battle_state.py:118-174` (ShipState), `game/simulation/battle_state.py:344-385` (ProjectileState), `game/simulation/battle_state.py:499-548` (BattleState), `game/simulation/battle_state.py:658-695` (BattleResults)
**Issue:** Five dataclasses all implement identical `to_dict()` and `from_dict()` serialization patterns with manual field-by-field conversion. Each class has 15-50 lines of boilerplate for dict conversion.
**Impact:** High maintenance burden - adding new fields requires updates in multiple places (dataclass definition, to_dict, from_dict). Bug risk if field added in one place but not others.
**Recommendation:** Create a generic serialization mixin or use `dataclasses.asdict()` with custom handlers for nested types. Consider a `Serializable` base class with automatic serialization via introspection.
**Effort:** Medium

#### MAJOR: Resource Ability Classes Share Identical Structure
**ID:** DUP-SIM-002
**Location:** `game/simulation/components/abilities/resources.py:9-150` (ResourceConsumption), `game/simulation/components/abilities/resources.py:152-189` (ResourceStorage), `game/simulation/components/abilities/resources.py:192-229` (ResourceGeneration)
**Issue:** Three ability classes have nearly identical structure: all have `resource_type/name` field, numeric `amount/rate/max_amount` field, `_base_X` backing field, and identical patterns for `sync_data()`, `recalculate()`, and `get_ui_rows()`. The `sync_data` method is copy-pasted with minor field name changes.
**Impact:** Adding new resource-related abilities requires copying ~40 lines of boilerplate. Changes to pattern must be replicated in all three classes.
**Recommendation:** Extract a `ResourceAbilityBase` class that handles the common `resource_type`, amount field with base value, sync_data pattern, and recalculate pattern. Subclasses only override UI text and specific behavior.
**Effort:** Simple

#### MAJOR: Team Iteration Pattern Duplicated in Battle Logic
**ID:** DUP-SIM-003
**Location:** `game/simulation/systems/battle_engine.py:515-525` (is_battle_over), `game/simulation/systems/battle_engine.py:630-636` (get_winner), `game/simulation/battle_state.py:620-631` (get_ships_by_team, get_alive_ships, etc.)
**Issue:** Multiple places iterate over ships filtering by team_id and is_alive status with sum() or list comprehensions. The pattern `sum(1 for s in self.ships if s.team_id == X and s.is_alive)` appears 4 times across files.
**Impact:** Low bug risk but cognitive overhead. If "alive" definition changes (e.g., to include escaped ships), multiple locations need updates.
**Recommendation:** Add `get_alive_ships_by_team(team_id)` method to BattleEngine that all callers use. This centralizes the alive-ship-by-team concept.
**Effort:** Simple

#### MINOR: Vector2 Conversion Pattern in ProjectileManager
**ID:** DUP-SIM-004
**Location:** `game/simulation/projectile_manager.py:47-48`, `game/simulation/projectile_manager.py:92-94`
**Issue:** Manual conversion of position/velocity to local Vector2 appears twice to handle pygame Vector2 from mocks: `p_pos = Vector2(p.position.x, p.position.y)`. Same pattern for ship velocity conversion.
**Impact:** Low - isolated to one file. But if Vector2 types need unified handling, this is a code smell.
**Recommendation:** Consider a utility function `ensure_vector2(v)` that handles conversion from any vector-like object. Or ensure all game objects use the same Vector2 type.
**Effort:** Simple

#### MINOR: get_ui_rows Color Mapping Pattern in Resource Abilities
**ID:** DUP-SIM-005
**Location:** `game/simulation/components/abilities/resources.py:131-138`, `game/simulation/components/abilities/resources.py:181-184`, `game/simulation/components/abilities/resources.py:221-224`
**Issue:** Resource color mapping (fuel->orange, energy->light blue/yellow, etc.) is hardcoded in each ability's `get_ui_rows()` method. Same colors with slight variations defined in each class.
**Impact:** If resource colors need standardization, changes must happen in multiple places. UI consistency risk.
**Recommendation:** Create a `ResourceColors` constant mapping or utility function `get_resource_color(resource_type)` used by all resource abilities.
**Effort:** Simple

#### MINOR: ship_id_map Pattern Repeated in RetreatManager
**ID:** DUP-SIM-006
**Location:** `game/simulation/managers/retreat_manager.py:64-108`, `game/simulation/managers/retreat_manager.py:110-130`, `game/simulation/managers/retreat_manager.py:230-246`, `game/simulation/managers/retreat_manager.py:248-266`
**Issue:** Four methods all have the same pattern: accept ship and ship_id_map, look up `ship_id = ship_id_map.get(id(ship))`, then use ship_id for internal operations. Each repeats the lookup pattern.
**Impact:** Low - contained within one class. But if lookup logic changes, four methods need updates.
**Recommendation:** Create private method `_get_ship_id(ship, ship_id_map) -> Optional[str]` that centralizes the lookup and returns None with consistent handling.
**Effort:** Simple

#### MINOR: Validation Pattern in modifier_schema.py
**ID:** DUP-SIM-007
**Location:** `game/simulation/components/modifier_schema.py:57-107` (validate_effect_v2), `game/simulation/components/modifier_schema.py:129-165` (validate_param_v2), `game/simulation/components/modifier_schema.py:168-207` (validate_restrictions_v2)
**Issue:** Three validation functions follow the same pattern: check isinstance(x, dict), check required fields exist, validate field types, validate optional fields. Each has ~30-40 lines of similar validation logic.
**Impact:** Low - validation code naturally has similarity. Adding new schema types requires copying pattern.
**Recommendation:** Consider a declarative schema validation approach where field requirements are defined as data rather than code. However, current explicit validation is readable and testable.
**Effort:** Medium (and may not be worth it)

#### INFO: Natural Similarity in Dataclass State Classes
**ID:** DUP-SIM-008
**Location:** `game/simulation/battle_state.py` - ComponentState, ShipState, ProjectileState
**Issue:** Multiple state classes have naturally similar structure as they represent different entity snapshots. Each has position tuples, health values, and to_dict/from_dict methods.
**Impact:** This is expected architectural similarity rather than problematic duplication. The classes model different entities and should remain separate.
**Recommendation:** No action needed. This is appropriate domain modeling where different entity types have similar attributes but distinct semantics.
**Effort:** N/A

## Top 5 Priority Issues

1. **DUP-SIM-001 (MAJOR)**: Serialization boilerplate in BattleState dataclasses - highest line count of duplicated code (~200 lines across 5 classes), high maintenance burden when adding state fields.

2. **DUP-SIM-002 (MAJOR)**: Resource ability classes share identical structure - affects three core ability types, easy to consolidate with a base class.

3. **DUP-SIM-003 (MAJOR)**: Team iteration pattern scattered across battle logic - affects core game logic, could lead to inconsistencies if "alive" definition evolves.

4. **DUP-SIM-005 (MINOR)**: Resource color mapping duplicated - UI consistency issue, simple fix with a constant mapping.

5. **DUP-SIM-006 (MINOR)**: ship_id_map lookup pattern in RetreatManager - four methods repeat same lookup, simple private method extraction.
