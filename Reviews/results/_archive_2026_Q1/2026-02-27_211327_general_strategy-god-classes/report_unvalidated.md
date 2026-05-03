# Review Report: 2026-02-27_211327_general_strategy-god-classes

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review
- **Description:** God class accumulation in strategy domain models (Fleet, Planet)
- **Agents Used:** 1

## Executive Summary
- **Total Findings:** 18
- **Critical:** 3 | **Major:** 8 | **Minor:** 5 | **Info:** 2
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: AR-001
**ID:** AR-001
**Agent:** Architecture Reviewer
**Location:** `game/strategy/data/fleet.py:7-9`
**Effort:** Complex

**ID:** AR-001
**Location:** `game/strategy/data/fleet.py:7-9`, `game/strategy/data/fleet.py:138-144`, `game/strategy/data/fleet_resource_aggregator.py:30`, `game/strategy/data/fleet_capability_calculator.py:52`, `game/strategy/data/fleet_battle_adapter.py:36`

**Issue:** The "delegates" (FleetResourceAggregator, FleetCapabilityCalculator, FleetBattleAdapter) are not true delegation - they are **tightly coupled pseudo-facades** that still reach back into Fleet internals. Each delegate stores a r...

---

### 2. CRITICAL: AR-002
**ID:** AR-002
**Agent:** Architecture Reviewer
**Location:** `game/strategy/data/fleet.py:485-540`
**Effort:** Complex

**ID:** AR-002
**Location:** `game/strategy/data/fleet.py:485-540`, `game/strategy/data/planet.py:405-499`, `game/strategy/data/ship_instance.py:662-715`

**Issue:** **Serialization responsibilities violate Single Responsibility Principle.** Each data model class (Fleet, Planet, ShipInstance) handles its own persistence logic with complex reference resolution (`resolve_order_references`, `from_dict` with galaxy/empire lookups). This mixes domain logic with infrastructure concerns, making classes...

---

### 3. CRITICAL: AR-003
**ID:** AR-003
**Agent:** Architecture Reviewer
**Location:** `game/strategy/engine/fleet_order_processor.py:59-648`
**Effort:** Complex

**ID:** AR-003
**Location:** `game/strategy/engine/fleet_order_processor.py:59-648`

**Issue:** **FleetOrderProcessor is a new god class** (648 lines) that violates Command-Query Separation and has too many responsibilities:
- Order lifecycle (completion, cancellation)
- JOIN_FLEET execution
- COLONIZE validation + execution + population transfer
- TRANSFER validation + execution (fleet-to-planet, fleet-to-fleet)
- Superweapon delegation
- Founding population logic

The class mixes command execu...

---

### 4. MAJOR: AR-004
**ID:** AR-004
**Agent:** Architecture Reviewer
**Location:** `game/strategy/data/fleet.py:191-192`
**Effort:** Medium

**ID:** AR-004
**Location:** `game/strategy/data/fleet.py:191-192`, `game/strategy/data/ship_instance.py:255-264`, `game/strategy/data/fleet_capability_calculator.py:116-125`

**Issue:** **Data classes reach into service layer** via "intentional late imports". Fleet.trigger_speed_recalculation() imports FleetSpeedCalculator, ShipInstance.get_calculated_stats() imports ShipStatsCalculator. This creates **hidden circular dependencies** where data models depend on services that depend on data model...

---

### 5. MAJOR: AR-005
**ID:** AR-005
**Agent:** Architecture Reviewer
**Location:** `game/strategy/engine/fleet_movement_engine.py:72-93`
**Effort:** Medium

**ID:** AR-005
**Location:** `game/strategy/engine/fleet_movement_engine.py:72-93`, `game/strategy/services/fleet_navigation_service.py:610-653`

**Issue:** **FleetMovementEngine and FleetNavigationService have unclear boundaries.** FleetMovementEngine.calculate_next_hex() immediately delegates to FleetNavigationService, making FleetMovementEngine a thin wrapper. The division of responsibility is artificial:
- FleetNavigationService: path calculation, next hex logic
- FleetMovementEngine: resour...

---

### 6. MAJOR: AR-006
**ID:** AR-006
**Agent:** Architecture Reviewer
**Location:** `game/strategy/data/planet.py:70-127`
**Effort:** Medium

**ID:** AR-006
**Location:** `game/strategy/data/planet.py:70-127`, `game/strategy/data/build_queue_source.py:80-111`

**Issue:** **PlanetaryFacility has leaky abstractions.** The `get_fuel_storage()`, `get_max_fuel_storage()`, `add_fuel()`, `withdraw_fuel()` methods directly iterate over `design_data` components and inspect ResourceStorage abilities. This violates **Information Hiding** - the facility shouldn't know the internal structure of component abilities.

Meanwhile, `build_queue_source....

---

### 7. MAJOR: AR-007
**ID:** AR-007
**Agent:** Architecture Reviewer
**Location:** `game/strategy/data/ship_instance.py:239-271`
**Effort:** Medium

**ID:** AR-007
**Location:** `game/strategy/data/ship_instance.py:239-271`, `game/strategy/services/ship_stats_calculator.py` (not shown, but referenced)

**Issue:** **ShipInstance.get_calculated_stats() performs hidden global registry access.** Line 258-264 shows ShipInstance directly importing and calling `get_default_registry_provider()` to construct GameRegistries on the fly. This is a **Service Locator anti-pattern** that:
- Hides dependencies (can't see from signature that registries are n...

---

### 8. MAJOR: AR-008
**ID:** AR-008
**Agent:** Architecture Reviewer
**Location:** `game/strategy/data/fleet.py:64-113`
**Effort:** Complex

**ID:** AR-008
**Location:** `game/strategy/data/fleet.py:64-113`, `game/strategy/engine/fleet_order_processor.py:443-478`

**Issue:** **FleetOrder serialization uses type markers but lacks polymorphism.** The `to_dict()` and `from_dict()` methods use discriminator dicts (`{'type': 'fleet_ref', 'id': xxx}`, `{'type': 'planet_ref', ...}`) to encode different target types. This is a **manual type system** that should be handled by proper object-oriented polymorphism.

Additionally, `from_dict()` h...

---

### 9. MAJOR: AR-009
**ID:** AR-009
**Agent:** Architecture Reviewer
**Location:** `game/strategy/data/empire.py:26-27`
**Effort:** Medium

**ID:** AR-009
**Location:** `game/strategy/data/empire.py:26-27`, `game/strategy/data/build_queue_source.py:196-227`

**Issue:** **Empire holds raw collections of Planets and Fleets instead of managed collections.** `Empire.colonies` and `Empire.fleets` are plain Python lists that other code directly appends to, removes from, and iterates over. This violates **Encapsulation** and prevents:
- Enforcement of invariants (e.g., fleet.owner_id must match empire.id)
- Notification of changes (for obs...

---

### 10. MAJOR: AR-010
**ID:** AR-010
**Agent:** Architecture Reviewer
**Location:** `game/strategy/facade/dto/fleet_dto.py:93-179`
**Effort:** Simple

**ID:** AR-010
**Location:** `game/strategy/facade/dto/fleet_dto.py:93-179`

**Issue:** **FleetInfo.from_fleet() performs complex business logic in DTO conversion.** Lines 120-161 show order target resolution logic embedded in DTO creation:
- Checking if order.target is HexCoord, Planet, Fleet, or dict
- Formatting display strings ("Load 10 passengers")
- Handling different order types with conditional branches

This violates **Single Responsibility** - a DTO factory should transform data struct...

---


## Findings by Severity

### Critical (3)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-001 | AR-001 | `game/strategy/data/fleet.py:7-` | Complex |
| AR-002 | AR-002 | `game/strategy/data/fleet.py:48` | Complex |
| AR-003 | AR-003 | `game/strategy/engine/fleet_ord` | Complex |

### Major (8)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-004 | AR-004 | `game/strategy/data/fleet.py:19` | Medium |
| AR-005 | AR-005 | `game/strategy/engine/fleet_mov` | Medium |
| AR-006 | AR-006 | `game/strategy/data/planet.py:7` | Medium |
| AR-007 | AR-007 | `game/strategy/data/ship_instan` | Medium |
| AR-008 | AR-008 | `game/strategy/data/fleet.py:64` | Complex |
| AR-009 | AR-009 | `game/strategy/data/empire.py:2` | Medium |
| AR-010 | AR-010 | `game/strategy/facade/dto/fleet` | Simple |
| AR-011 | AR-011 | `game/strategy/services/cargo_t` | Medium |

### Minor (5)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-012 | AR-012 | `game/strategy/data/fleet.py:29` | Simple |
| AR-013 | AR-013 | `game/strategy/data/ship_instan` | Trivial |
| AR-014 | AR-014 | `game/strategy/data/fleet_resou` | Simple |
| AR-015 | AR-015 | `game/strategy/data/planet.py:3` | Simple |
| AR-016 | AR-016 | `game/strategy/data/ship_instan` | Simple |

### Info (2)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-017 | AR-017 | `game/strategy/engine/fleet_ord` | Info |
| AR-018 | AR-018 | `game/strategy/data/fleet.py:1-` | Complex |


## Agent Reports

- [Architecture Reviewer Report](findings/architecture_reviewer_report.md)
- [Code Quality Analyst Report](findings/code_quality_analyst_report.md)
- [Complexity Analyst Report](findings/complexity_analyst_report.md)
- [Dead Code Hunter Report](findings/dead_code_hunter_report.md)
- [Refactoring Opportunity Finder Report](findings/refactoring_opportunity_finder_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 18 |
| Critical | 3 |
| Major | 8 |
| Minor | 5 |
| Info | 2 |
| Agents Used | 1 |

---
*Report generated: 2026-02-27 21:26*
