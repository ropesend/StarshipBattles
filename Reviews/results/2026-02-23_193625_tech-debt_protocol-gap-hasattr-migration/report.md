# Technical Debt Review: Protocol Gap — hasattr/getattr to Protocol Migration

## Metadata
- **Date:** 2026-02-23
- **Type:** Technical Debt Review
- **Scope:** All `hasattr()` and `getattr()` calls in `game/` (primary) + `tests/`/`simulation_tests/` (catalog)
- **Agents Used:** 6 (Simulation/Core Analyst, Strategy Analyst, UI Analyst, AI/Engine Analyst, Protocol Architect, Test Cataloguer)
- **Prior Findings:** PC-003 (Major), DD-017 (Major) from Deliberate Design Debt Audit

## Executive Summary

- **Total Findings in game/:** 665 occurrences (293 hasattr + 372 getattr) across 131 files
- **Total Findings in tests/:** ~600 occurrences across 864 test files (lower priority)
- **Overall Debt Level:** High
- **Existing Protocols:** 17 in `game/core/protocols.py` + 11 scattered = 28 total
- **Existing ABCs:** 14 (strategy engine interfaces, etc.)
- **Estimated New Protocols Needed:** 20-25 to eliminate ~70% of duck-typing calls
- **Estimated Total Effort:** 3-4 weeks (phased, incremental)

### Category Breakdown (game/ directory only)

| Category | Count | Description |
|----------|-------|-------------|
| **A: Protocol Candidates** | ~60 | Interface checks → should become Protocol isinstance() |
| **B: Optional Attribute Access** | ~450 | Defensive getattr with defaults → typed Optional or Protocol |
| **C: Dynamic Dispatch** | ~40 | Legitimate reflection → keep, document |
| **D: Legacy/Transitional** | ~25 | Backwards compat → remove |
| **B-Event: UI Event Checks** | ~20 | pygame_gui event attrs → use event typing |
| **B-Internal: Lazy Init** | ~42 | hasattr(self, widget) → init in __init__ |

### Layer Distribution

| Layer | hasattr | getattr | Total | Files |
|-------|---------|---------|-------|-------|
| **UI (game/ui/)** | 195 | 182 | 377 | 78 |
| **Simulation + Core** | 35 | 51 | 86 | 27 |
| **Strategy** | 45 | 62 | 107 | 25 |
| **AI + Engine + App** | 15 | 16 | 31 | 5 |
| **Total game/** | 293 | 372 | 665 | 131* |

*Some files counted in multiple categories.

---

## Priority Findings (Top 10)

### 1. CRITICAL: IEmpire/IPlanet/IFleet Defensive Access Pattern
**ID:** STRAT-01
**Agent:** Strategy Layer Analyst
**Location:** `game/strategy/engine/` (6 files: empire_economy_calculator.py, harvesting_engine.py, population_engine.py, superweapon_order_processor.py, fleet_order_processor.py, command_handlers.py)
**Issue:** 30+ getattr calls defensively accessing core domain collections: `empire.colonies`, `planet.facilities`, `fleet.ships`, `empire.resource_pool`. These are fundamental domain object properties that should be guaranteed.
**Impact:** Every strategy engine file uses defensive access for properties that always exist. This hides real bugs (if a property were actually missing, the default would silently produce wrong results).
**Recommendation:** Strengthen IEmpire, IPlanet, IFleet protocols with all required collection properties. Define new IFacility protocol.
**Effort:** Medium (define protocols + update 30+ call sites across 6 files)
**Protocols Needed:** IEmpire (strengthen), IPlanet (strengthen), IFacility (new), IRaceConfig (new)
**getattr eliminated:** ~30

---

### 2. CRITICAL: empire_panel_window.py Has 28 getattr Calls
**ID:** UI-01
**Agent:** UI Layer Analyst
**Location:** `game/ui/screens/empire_panel_window.py` (28 getattr calls)
**Issue:** Single file with highest concentration of defensive access. All accessing empire/session properties with defaults.
**Impact:** Worst single-file offender. If empire interface changes, 28 silent failures.
**Recommendation:** Define clear IEmpireView protocol for UI layer empire access.
**Effort:** Medium
**getattr eliminated:** 28

---

### 3. HIGH: IComponentWithAbilities Protocol Missing
**ID:** SIM-01
**Agent:** Simulation/Core Analyst
**Location:** `game/simulation/entities/ship_stats.py`, `ability_aggregator.py`, `combat_endurance.py`, `component.py`, `base.py` (6 files)
**Issue:** 15+ getattr calls checking `ability_instances` and `abilities` on components. This is the core ability system pattern used everywhere.
**Impact:** Core to the simulation engine. Every ability aggregation path uses defensive access for what should be a guaranteed property.
**Recommendation:** Create IComponentWithAbilities protocol with `ability_instances: List` and `abilities: Dict`.
**Effort:** Simple (2 properties, update 6 files)
**Protocols Needed:** IComponentWithAbilities (new)
**getattr eliminated:** ~15

---

### 4. HIGH: Component Attribute Duck-Typing in Strategy Layer
**ID:** STRAT-02
**Agent:** Strategy Layer Analyst
**Location:** `game/strategy/data/design_metadata.py`, `game/strategy/services/ship_stats_calculator.py`, `game/strategy/services/component_inspector.py`, `game/strategy/engine/harvesting_engine.py` (4+ files)
**Issue:** 16+ getattr calls for `abilities`, `category`, `damage`, `rate_of_fire`, `hp`, `cost`, `type_str`, `damage_threshold` on component definitions.
**Impact:** Strategy layer cannot rely on component structure. Schema changes would silently break these files.
**Recommendation:** Create comprehensive IComponentDef protocol for strategy layer's view of components.
**Effort:** Medium
**getattr eliminated:** ~16

---

### 5. HIGH: ICombatant/Targeting Defensive Checks
**ID:** SIM-02
**Agent:** Simulation/Core Analyst + AI/Engine Analyst
**Location:** `game/simulation/combat/targeting_system.py` (7 calls), `game/ai/combat_utils.py` (11 calls), `game/ai/controller.py` (7 calls)
**Issue:** 25 total getattr/hasattr calls checking `is_alive`, `team_id`, `velocity`, `position`, `mass`, `type` on combat entities. ICombatant protocol exists but is not enforced.
**Impact:** Targeting system makes silent assumptions about entity structure. Wrong defaults could cause incorrect targeting decisions.
**Recommendation:** Strengthen ICombatant protocol. Ensure all targetable entities (ships, projectiles) implement it. Replace getattr with direct access.
**Effort:** Medium
**Protocols Needed:** ICombatant (strengthen), IKinematic (new: velocity, position, mass)
**getattr eliminated:** ~25

---

### 6. HIGH: battle_panels.py Projectile Rendering (21 getattr calls)
**ID:** UI-02
**Agent:** UI Layer Analyst
**Location:** `game/ui/panels/battle_panels.py` (21 total: 3 hasattr + 18 getattr)
**Issue:** Projectile state rendering uses 18 getattr calls for properties like `max_speed`, `hp`, `max_hp`, `endurance`, `target`, `status`.
**Impact:** UI rendering silently falls back to defaults if projectile interface changes.
**Recommendation:** Define IProjectile protocol with all rendering-required properties.
**Effort:** Medium
**Protocols Needed:** IProjectile (new)
**getattr eliminated:** ~18

---

### 7. HIGH: Lazy Widget Initialization Pattern (42 occurrences)
**ID:** UI-03
**Agent:** UI Layer Analyst
**Location:** Scattered across `game/ui/panels/` and `game/ui/screens/` (42 hasattr(self, 'widget') calls)
**Issue:** UI panels check `hasattr(self, 'name_label')`, `hasattr(self, 'panel')` etc. instead of initializing widgets in `__init__`.
**Impact:** Fragile initialization order. If a method is called before a widget is created, hasattr silently skips it instead of raising an error.
**Recommendation:** Initialize all widgets in `__init__` as `Optional[Type] = None`, use `if self.widget is not None:` instead.
**Effort:** Medium (mechanical, 42 call sites across ~15 files)
**getattr eliminated:** 42 hasattr → proper Optional typing

---

### 8. MEDIUM: Zone Occupancy API Inconsistency
**ID:** STRAT-03
**Agent:** Strategy Layer Analyst
**Location:** `game/strategy/data/galaxy.py` (9 hasattr + 1 getattr)
**Issue:** Mixed optional/required checks for `location`, `diameter_hexes`, `occupied_hexes` on zone-occupying entities. IZoneOccupant protocol exists but is not consistently used.
**Impact:** Zone system behaves differently depending on which code path checks which attributes. PROJ-139 multi-hex support is partially optional.
**Recommendation:** Enforce IZoneOccupant protocol consistently. Use `is_zone_occupant()` TypeGuard.
**Effort:** Simple
**hasattr eliminated:** ~10

---

### 9. MEDIUM: IResourceConsumption Protocol Missing
**ID:** SIM-03
**Agent:** Simulation/Core Analyst
**Location:** `game/simulation/entities/combat_endurance.py`, `game/simulation/components/component_resource_manager.py`, `game/simulation/components/component.py` (3 files)
**Issue:** 8 getattr calls checking `trigger`, `resource_type`, `amount`, `check_available` on abilities. Resource consumption system relies on duck typing.
**Impact:** Resource simulation silently falls back to defaults if ability interface changes.
**Recommendation:** Create IResourceConsumption protocol.
**Effort:** Simple
**getattr eliminated:** ~8

---

### 10. MEDIUM: App.py State Management (11 hasattr + 1 getattr)
**ID:** AI-01
**Agent:** AI/Engine Analyst
**Location:** `game/app.py` (10 hasattr + 1 getattr)
**Issue:** Application entry point checks for existence of scenes, state flags, and private attributes instead of properly initializing them.
**Impact:** Startup/transition bugs could silently fail. Private attribute access (`_ui`, `_apply_tooltips`) indicates tight coupling.
**Recommendation:** Initialize all state in `__init__`. Remove private attribute access across scene boundaries.
**Effort:** Medium
**hasattr eliminated:** ~11

---

## Protocol Architecture Recommendations

### Current State
- **17 protocols** in `game/core/protocols.py` (580 lines)
- **11 protocols** scattered across other files
- **14 ABCs** in `game/strategy/interfaces/engines.py` and elsewhere
- **Naming:** I-prefix convention (IFleet, IScene, etc.) with some exceptions (BuildContext, DropTarget)

### File Organization Recommendation

**Hybrid approach — keep core hub, add layer-specific files:**

1. **`game/core/protocols.py`** (existing, expand to ~700-800 lines max)
   - Cross-layer boundary protocols (IPostBattleShip, IResourceReader)
   - Base composable protocols (ILocatable, INamed, IOwnable, IIdentifiable)
   - Strategy entity protocols (IStarSystem, IPlanet, IFleet, IEmpire)
   - Combat entity protocols (ICombatant, IDamageable, IKinematic)

2. **`game/simulation/protocols.py`** (NEW, ~150-200 lines)
   - IComponentWithAbilities
   - IComponentDef (strategy layer's view of components)
   - IResourceConsumption
   - IWeaponAbility, IStorageAbility
   - IProjectile (for battle state serialization + UI rendering)
   - IFormationMember

3. **`game/ui/protocols.py`** (NEW, ~100-150 lines)
   - ITreeNode (system tree panel)
   - ISortableColumn (fleet report, planet list)
   - IDropTarget (builder drag-and-drop)

4. **`game/strategy/protocols.py`** (NEW, ~150-200 lines)
   - IFacility
   - IRaceConfig
   - ICargoHolder
   - IGalaxy (expand for zone/system methods)
   - Consider migrating strategy engine ABCs to Protocols

### Naming Convention
Standardize on **I-prefix** for all protocols. Rename:
- `BuildContext` → `IBuildContext`
- `DropTarget` → `IDropTarget`
- `DensityPrimitive` → `IDensityPrimitive`
- `GroupingStrategy` → `IGroupingStrategy`

### Performance Assessment
- `@runtime_checkable` isinstance checks are O(1) attribute lookups
- NOT used in hot loops (60fps battle tick)
- Safe to add freely — no performance risk

---

## New Protocols Needed (Ranked by Impact)

| Rank | Protocol | Layer | Attributes/Methods | getattr/hasattr Eliminated | Files Impacted |
|------|----------|-------|-------------------|---------------------------|----------------|
| 1 | **IEmpire** (strengthen) | Core | colonies, race_config, resource_pool, max_storage, fleets | ~30 | 6+ strategy files |
| 2 | **IComponentWithAbilities** | Simulation | ability_instances, abilities | ~15 | 6 simulation files |
| 3 | **IProjectile** | Simulation | hp, max_hp, endurance, target, type, velocity, team_id | ~18 | 3 files (battle_panels, battle_state, targeting) |
| 4 | **IComponentDef** | Strategy | abilities, category, damage, cost, type_str, hp | ~16 | 4 strategy files |
| 5 | **IFacility** | Strategy | is_operational, design_data | ~18 | 3 strategy engine files |
| 6 | **IPlanet** (strengthen) | Core | facilities, populations, max_population, resources | ~10 | 4 files |
| 7 | **IKinematic** | Simulation | velocity, position, mass, angle | ~10 | 3 AI/targeting files |
| 8 | **IRaceConfig** | Strategy | race_id, aptitude_population_growth | ~6 | 2 files |
| 9 | **IResourceConsumption** | Simulation | trigger, resource_type, amount | ~8 | 3 simulation files |
| 10 | **IWeaponAbility** | Simulation | reload_time, range, damage | ~6 | 3 files |
| 11 | **IFormationMember** | Simulation | formation property | ~4 | 2 files |
| 12 | **ITreeNode** | UI | is_group, group_key, handle_event | ~5 | 2 UI files |
| 13 | **ISortableColumn** | UI | col_ref, sort_col_ref, direction | ~4 | 2 UI files |
| 14 | **IVector2Like** | Core | x, y, distance_to, length | ~6 | 2 files (math.py, combat_utils.py) |
| 15 | **IStorageAbility** | Simulation | resource_type, max_amount | ~4 | 2 files |

**Total estimated elimination: ~160 hasattr/getattr calls** (24% of 665 total) from 15 new/strengthened protocols.

---

## Phased Implementation Plan (PROJ-XX Ready)

### Phase 1: Define Core Protocols (No Call-Site Changes) — 2-3 days
- [ ] Create `game/simulation/protocols.py` with IComponentWithAbilities, IProjectile, IResourceConsumption, IWeaponAbility, IStorageAbility, IFormationMember
- [ ] Create `game/strategy/protocols.py` with IFacility, IRaceConfig, ICargoHolder, IGalaxy
- [ ] Create `game/ui/protocols.py` with ITreeNode, ISortableColumn, IDropTarget
- [ ] Strengthen IEmpire in core/protocols.py (add colonies, race_config, resource_pool, fleets)
- [ ] Strengthen IPlanet in core/protocols.py (add facilities, populations, resources)
- [ ] Add IKinematic, IVector2Like, IIdentifiable to core/protocols.py
- [ ] Add TypeGuard functions for all new protocols
- [ ] Standardize naming (rename BuildContext → IBuildContext, etc.)
- [ ] Run full test suite — zero regressions expected (no call-site changes)

### Phase 2: Migrate Category A — High-Value Protocol Checks — 3-4 days
- [ ] Replace `hasattr(obj, 'ability_instances')` → `isinstance(obj, IComponentWithAbilities)` (15 sites)
- [ ] Replace `hasattr(obj, 'is_alive')` / `getattr(obj, 'team_id', -1)` → ICombatant isinstance (8 sites)
- [ ] Replace galaxy.py zone hasattr checks → `is_zone_occupant()` TypeGuard (10 sites)
- [ ] Replace `hasattr(scene, 'handle_event')` etc. → IScene isinstance (4 sites in app.py)
- [ ] Replace fleet_dto.py hasattr checks → INamed/ILocatable/IIdentifiable (3 sites)
- [ ] Replace combat_utils.py Vector2 hasattr → IVector2Like isinstance (3 sites)
- [ ] Run full test suite after each file group

### Phase 3: Migrate Category B — Defensive getattr → Direct Access — 5-7 days
**Batch 3a: Strategy Engine (highest density)**
- [ ] empire_economy_calculator.py (14 getattr → direct) using IEmpire, IFacility
- [ ] harvesting_engine.py (12 getattr → direct) using IEmpire, IFacility
- [ ] superweapon_order_processor.py (10 getattr → direct) using IEmpire
- [ ] population_engine.py (6 getattr → direct) using IEmpire, IRaceConfig
- [ ] fleet_order_processor.py (4 getattr → direct) using IFleet

**Batch 3b: Simulation Core**
- [ ] ship_stats.py (16 getattr → direct) using IComponentWithAbilities, IWeaponAbility
- [ ] targeting_system.py (7 getattr → direct) using ICombatant, IKinematic
- [ ] combat_endurance.py (5 getattr → direct) using IResourceConsumption
- [ ] ability_aggregator.py (4 getattr → direct) using IComponentWithAbilities
- [ ] battle_state.py (8 getattr → direct) using IProjectile

**Batch 3c: UI Layer (selective — highest-value files)**
- [ ] empire_panel_window.py (28 getattr → direct) using IEmpire
- [ ] battle_panels.py (18 getattr → direct) using IProjectile
- [ ] ship_stats_renderer.py (9 getattr → direct) using IComponentDef
- [ ] stats_config.py (13 getattr → direct) using IComponentWithAbilities

### Phase 4: Clean Up Category D — Remove Legacy Checks — 1-2 days
- [ ] Remove `hasattr(self.galaxy, 'get_system_of_object')` in game_session.py (method always exists)
- [ ] Remove `hasattr(galaxy, 'unregister_fleet')` in superweapon_order_processor.py
- [ ] Remove `hasattr(self, 'builder_scene')` etc. in app.py — init all state in __init__
- [ ] Remove lazy init patterns: `if not hasattr(self, '_combat_engine')` in ship.py
- [ ] Remove `if not hasattr(comp, 'shots_fired')` in weapon_firing_system.py — init in __init__
- [ ] Remove 7 legacy UI transitional checks (test_mode, build_queue_screen, etc.)
- [ ] Convert 42 hasattr(self, widget) → Optional[Type] = None pattern in UI panels

### Phase 5: Audit Category C — Document Intentional Reflection — 1 day
- [ ] Document formula_system.py builtins lookup as intentional
- [ ] Document stat_keys.py binding resolution as intentional
- [ ] Document race_config.py validation reflection as intentional
- [ ] Document ship_stats_calculator.py dynamic attribute loop as intentional
- [ ] Document app.py keybindings state lookup as intentional
- [ ] Add # INTENTIONAL: dynamic dispatch comments to all Category C sites
- [ ] Final count verification: confirm remaining hasattr/getattr is documented

---

## Test Code Impact Assessment (Lower Priority)

| Directory | hasattr | getattr | Total | Key Pattern |
|-----------|---------|---------|-------|-------------|
| tests/ | 488 | 53 | 541 | Protocol compliance assertions, ABC method checks |
| simulation_tests/ | 46 | 13 | 59 | Template hooks, ability extraction, validation |
| **Total** | **534** | **66** | **600** | |

**Key finding:** 41 hasattr calls in UI tests are redundant (already checking isinstance(scene, IScene)). 12+ hasattr calls in simulation_tests are intentional template hook infrastructure. No test migration needed in Phase 1-4; revisit after production protocols are hardened.

---

## Debt Heat Map (by module)

| Module | Debt Score | Change Freq | Priority |
|--------|------------|-------------|----------|
| game/ui/screens/ | Very High (250+) | High | P1 (empire_panel, strategy_*) |
| game/strategy/engine/ | High (60+) | High | P1 (economy, harvesting, fleet) |
| game/simulation/entities/ | High (40+) | Medium | P2 (ship_stats, combat_endurance) |
| game/ui/panels/ | Medium (80+) | Medium | P2 (battle_panels, planet_report) |
| game/simulation/components/ | Medium (20+) | Medium | P3 (ability system) |
| game/ai/ | Medium (25+) | Low | P3 (combat_utils, controller) |
| game/strategy/data/ | Low (15+) | Medium | P4 (galaxy, design_metadata) |
| game/core/ | Low (3) | Low | P5 (math.py only) |

---

## Prevention Recommendations

1. **Add a CI lint rule** that warns on new `hasattr()` / `getattr()` in `game/` — force developers to use Protocol isinstance checks
2. **Document protocol locations** in `docs/PROTOCOLS.md` so developers know what's available
3. **Mypy adoption** (future) — once protocols are defined, mypy can catch duck-typing at compile time
4. **Code review checklist item:** "Does this new code use hasattr/getattr? If so, should a Protocol exist?"

---

## Agent Reports

Reports were generated in-memory by the following agents:
- **Simulation/Core Layer Analyst** — 86 occurrences across 27 files, 10 proposed protocols
- **Strategy Layer Analyst** — 107 occurrences across 25 files, 7 proposed protocols
- **UI Layer Analyst** — 377 occurrences across 78 files, 4 proposed protocols
- **AI/Engine Analyst** — 31 occurrences across 5 files, 4 proposed protocols
- **Protocol Architect** — 28 existing protocols/ABCs analyzed, file org recommendation
- **Test Cataloguer** — 600 occurrences across 864 test files, 5 patterns identified
