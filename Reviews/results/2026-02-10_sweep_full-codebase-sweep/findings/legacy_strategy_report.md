# Legacy System Holdovers Sweep: Strategy

## Summary
- **Shard:** Strategy
- **Files Scanned:** 94
- **Total Issues Found:** 14
- **Critical:** 2 | **Major:** 5 | **Minor:** 5 | **Info:** 2

## Findings

#### CRITICAL: Save Game Format Backward Compatibility Layer
**ID:** LEG-STR-001
**Location:** `game/strategy/systems/save_game_service.py:30-32, 165, 382-421`
**Issue:** SaveGameService maintains MIGRATABLE_VERSIONS list and _is_compatible_version() / _can_migrate_version() methods that accept old save formats (1.0.0, 1.1.0, 1.2.0, 1.9.0). Comment says "no backward compatibility" but code accepts old versions.
**Impact:** Violates project policy. Creates confusion about which save format is authoritative. May accept old versions but not deserialize correctly, creating silent failures.
**Recommendation:** Remove migration logic and enforce strict current version only. Old saves are disposable per project policy.
**Effort:** Medium

#### CRITICAL: Global Registry Fallback in Simulation Adapter
**ID:** LEG-STR-002
**Location:** `game/strategy/adapters/simulation_adapter.py:52-53` AND `game/strategy/data/fleet_battle_adapter.py:52-53`
**Issue:** Multiple places document "If None, uses global fallback (transitional - will be required in Phase 6)". Backward compatibility shim allowing code without proper DI.
**Impact:** Code can silently fail when registry is None. Creates inconsistent state. Phase 6 promise not tracked.
**Recommendation:** Make registries parameter mandatory, eliminate fallback entirely.
**Effort:** Medium

#### MAJOR: Deprecated Parameter Support in GameSession
**ID:** LEG-STR-003
**Location:** `game/strategy/engine/game_session.py:66-84`
**Issue:** Constructor accepts deprecated galaxy_radius and system_count parameters with DeprecationWarning. These override config immutability.
**Impact:** Tests and legacy code paths can bypass configuration system.
**Recommendation:** Remove both parameters entirely. Update all callers to use GameConfig().
**Effort:** Simple

#### MAJOR: hasattr() Defensive Checks for Fleet Properties
**ID:** LEG-STR-004
**Location:** `game/strategy/services/fleet_navigation_service.py:94` AND `game/strategy/engine/game_session.py:184` AND `game/strategy/data/pathfinding.py:178, 317`
**Issue:** Multiple locations check hasattr(fleet, 'can_use_warp') before calling. Since Fleet.can_use_warp() is a defined public method, these checks are dead code.
**Impact:** Dead code path - else branch never executes. Creates false impression of optional functionality.
**Recommendation:** Remove hasattr checks, call method directly.
**Effort:** Simple

#### MAJOR: Facility.construction_queue Defensive Check
**ID:** LEG-STR-005
**Location:** `game/strategy/engine/production_engine.py:120`
**Issue:** Uses hasattr(facility, 'construction_queue') before accessing. PlanetaryFacility dataclass defines construction_queue with default factory, so attribute always exists.
**Impact:** Dead code path. Creates unnecessary branch.
**Recommendation:** Remove hasattr check.
**Effort:** Simple

#### MAJOR: Legacy Mass Field in DesignMetadata
**ID:** LEG-STR-006
**Location:** `game/strategy/data/design_metadata.py:90-92`
**Issue:** Comment states "Mass is stored in expected_stats (saved designs) or top-level (legacy)". Code checks both locations to support old format.
**Impact:** Maintains compatibility with legacy design files that might not exist anymore.
**Recommendation:** Standardize on expected_stats location. Verify no legacy design files remain.
**Effort:** Medium

#### MAJOR: Fleet Order Serialization Format Multiplicity
**ID:** LEG-STR-007
**Location:** `game/strategy/data/fleet.py:369-407`
**Issue:** FleetOrder.from_dict() accepts 6 different serialization formats for backward compatibility with save files (lines 384-407). Comments reference PROJ-42 and PROJ-68.
**Impact:** Large conditional chain that must be maintained. Multiple code paths to test.
**Recommendation:** Migrate all saves to current format on load, then support only one format.
**Effort:** Complex

#### MINOR: Unused "legacy" Comment in RaceConfig
**ID:** LEG-STR-008
**Location:** `game/strategy/data/race_config.py:83`
**Issue:** Field name: str = "" has comment "Display name (legacy, used as faction_name fallback)". Suggests field should be deprecated.
**Impact:** Redundant field, confusion about which name is authoritative.
**Recommendation:** Verify faction_name is used everywhere. Delete name field if unused.
**Effort:** Simple

#### MINOR: Migration Guide Documentation Without Code
**ID:** LEG-STR-009
**Location:** `game/strategy/services/fleet_navigation_service.py:5-33`
**Issue:** Extensive "Migration Guide" for deleted FleetMovementSimulator still in comments. Documentation references completed migration.
**Impact:** Confuses developers searching for old system.
**Recommendation:** Move to migration history document. Keep only current API docs.
**Effort:** Simple

#### MINOR: Convenience References for Backward Compatibility
**ID:** LEG-STR-010
**Location:** `game/strategy/engine/game_session.py:108-110`
**Issue:** Properties player_empire and enemy_empire documented as "Convenience references for backward compatibility".
**Impact:** Dual access patterns.
**Recommendation:** Verify actually needed. Delete if unused.
**Effort:** Simple

#### MINOR: Design Metadata Backward-Compatible Defaults
**ID:** LEG-STR-011
**Location:** `game/strategy/data/design_metadata.py:55-72`
**Issue:** from_dict() uses many .get() calls with default fallbacks for fields that may not exist in old saves.
**Impact:** Silent defaults hide missing data. Old save format not validated.
**Recommendation:** Make all fields required. Fail fast with clear error.
**Effort:** Medium

#### MINOR: Empire Serialization Legacy Visual Identity
**ID:** LEG-STR-012
**Location:** `game/strategy/data/empire.py:155-158`
**Issue:** Comment "Include race visual identity if set (backwards compatibility)". Optional fields flag_id and portrait_id only written if set.
**Impact:** Save files inconsistently contain these fields.
**Recommendation:** Audit if fields are actually used. Document or remove.
**Effort:** Simple

#### INFO: Classification Config Backward Compatibility
**ID:** LEG-STR-013
**Location:** `game/strategy/data/classification_config.py:16, 20`
**Issue:** Defaults "ensure backward compatibility if JSON loading fails". Provides hardcoded fallback if config file missing.
**Impact:** Silent fallback masks missing data files.
**Recommendation:** Fail fast with clear error if config missing.
**Effort:** Simple

#### INFO: Registry Fallback Pattern in Facade
**ID:** LEG-STR-014
**Location:** `game/strategy/facade/strategy_session_facade.py:432-436`
**Issue:** Try/except returns empty dict as "legacy behavior" when registry unavailable.
**Impact:** Silent failure. Cannot distinguish "no pods" from "registry error".
**Recommendation:** Raise clear exception instead of returning empty.
**Effort:** Simple

## Top 5 Priority Issues
1. **LEG-STR-001** (CRITICAL): Save game migration layer - decide: reject old saves per project policy
2. **LEG-STR-002** (CRITICAL): Global registry fallback - make DI mandatory
3. **LEG-STR-003** (MAJOR): Deprecated GameSession parameters - remove entirely
4. **LEG-STR-007** (MAJOR): Fleet order format multiplicity - migrate to single format
5. **LEG-STR-004** (MAJOR): hasattr() defensive checks - dead code branches
