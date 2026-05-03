# Review Report: 2026-02-27_153151_general_fleet-order-systems

## Metadata
- **Date:** 2026-02-27 15:31
- **Type:** General Review (focused deep-dive)
- **Description:** Fleet order systems — how orders are given, stored, and executed
- **Agents Used:** 25

## Executive Summary
- **Total Findings:** 21
- **Critical:** 1 | **Major:** 4 | **Minor:** 11 | **Info:** 5
- **Overall Assessment:** Requires Immediate Attention

### Validation Summary
- **Original Findings:** 22
- **Confirmed:** 21 | **Downgraded:** 8 | **Rejected:** 1
- **Rejection Rate:** 4.5%
- **Findings Without Verdict:** 0

## Priority Findings (Top 10)

### 1. CRITICAL: Unresolved `_fleet_ref` and `_planet_ref
**ID:** ODM-001
**Agent:** Validated
**Location:** `game/strategy/data/fleet.py:45`
**Effort:** Medium

**Location:** `game/strategy/data/fleet.py:45`

---

### 2. MAJOR: JOIN_FLEET Processed in Two Execution Pa
**ID:** EP-001
**Agent:** Validated
**Location:** `game/strategy/data/fleet.py:49`
**Effort:** Simple

**Location:** `game/strategy/data/fleet.py:49`

---

### 3. MAJOR: `complete_order()` and `cancel_order()`
**ID:** EP-002
**Agent:** Validated
**Location:** `game/strategy/engine/fleet_ord`
**Effort:** Medium

**Location:** `game/strategy/engine/fleet_ord`

---

### 4. MAJOR: Inconsistent Error Handling Across Execu
**ID:** EP-005
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Medium

**Location:** `Unknown`

---

### 5. MAJOR: Planet Target Serializes as Full Planet
**ID:** ODM-003
**Agent:** Validated
**Location:** `game/strategy/data/fleet.py:97`
**Effort:** Simple

**Location:** `game/strategy/data/fleet.py:97`

---

### 6. MINOR: SuperweaponOrderProcessor Instantiated F
**ID:** EP-003
**Agent:** Validated
**Location:** `game/strategy/engine/fleet_ord`
**Effort:** Simple

**Location:** `game/strategy/engine/fleet_ord`

---

### 7. MINOR: Duplicate BUILD Order Auto-Pop Logic
**ID:** EP-004
**Agent:** Validated
**Location:** `game/strategy/engine/action_ex`
**Effort:** Simple

**Location:** `game/strategy/engine/action_ex`

---

### 8. MINOR: Untyped Polymorphic `target` Field - 8+
**ID:** ODM-002
**Agent:** Validated
**Location:** `game/strategy/data/fleet.py:64`
**Effort:** Complex

**Location:** `game/strategy/data/fleet.py:64`

---

### 9. MINOR: `from_dict()` Silently Drops Unrecognize
**ID:** ODM-007
**Agent:** Validated
**Location:** `game/strategy/data/fleet.py:45`
**Effort:** Simple

**Location:** `game/strategy/data/fleet.py:45`

---

### 10. MINOR: `ClearOrdersCommandHandler` Bypasses `Fl
**ID:** ODM-011
**Agent:** Validated
**Location:** `game/strategy/engine/command_h`
**Effort:** Simple

**Location:** `game/strategy/engine/command_h`

---


## Findings by Severity

### Critical (1)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ODM-001 | Unresolved `_fleet_ref` and `_planet_ref | `game/strategy/data/fleet.py:45` | Medium |

### Major (4)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| EP-001 | JOIN_FLEET Processed in Two Execution Pa | `game/strategy/data/fleet.py:49` | Simple |
| EP-002 | `complete_order()` and `cancel_order()` | `game/strategy/engine/fleet_ord` | Medium |
| EP-005 | Inconsistent Error Handling Across Execu | `Unknown` | Medium |
| ODM-003 | Planet Target Serializes as Full Planet | `game/strategy/data/fleet.py:97` | Simple |

### Minor (11)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| EP-003 | SuperweaponOrderProcessor Instantiated F | `game/strategy/engine/fleet_ord` | Simple |
| EP-004 | Duplicate BUILD Order Auto-Pop Logic | `game/strategy/engine/action_ex` | Simple |
| ODM-002 | Untyped Polymorphic `target` Field - 8+ | `game/strategy/data/fleet.py:64` | Complex |
| ODM-007 | `from_dict()` Silently Drops Unrecognize | `game/strategy/data/fleet.py:45` | Simple |
| ODM-011 | `ClearOrdersCommandHandler` Bypasses `Fl | `game/strategy/engine/command_h` | Simple |
| EP-006 | `process_end_turn_orders` Name Is Mislea | `game/strategy/engine/fleet_ord` | Simple |
| EP-007 | ActionTimeResolver Returns 0 for Movemen | `game/strategy/services/action_` | Simple |
| EP-008 | WARP Order Type Not in ActionTimeResolve | `game/strategy/services/action_` | Simple |
| ODM-004 | Serialization Uses Both Order-Type and i | `game/strategy/data/fleet.py:81` | Medium |
| ODM-005 | BUILD OrderType Falls Outside Both Categ | `game/strategy/data/fleet.py:41` | Simple |
| ODM-008 | `CLOSE_WARP_POINT` Target Is a Raw Strin | `game/strategy/engine/superweap` | Simple |

### Info (5)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ODM-009 | Command and FleetOrder Carry Overlapping | `game/strategy/engine/commands.` | N |
| ODM-012 | `pop_order()` Uses `list.pop(0)` - O(n) | `game/strategy/data/fleet.py:34` | Simple |
| EP-009 | Turn Engine Phase Ordering Is Well-Docum | `game/strategy/engine/turn_engi` | N |
| ODM-006 | Categorization Is Used Consistently Acro | `Unknown` | N |
| ODM-010 | Command -> FleetOrder Mapping Is Clean a | `game/strategy/engine/command_h` | N |


## Agent Reports

- [Architecture Unification Report](findings/architecture_unification_report.md)
- [Command Pipeline Report](findings/command_pipeline_report.md)
- [Execution Paths Report](findings/execution_paths_report.md)
- [Order Data Model Report](findings/order_data_model_report.md)
- [Validation Consistency Report](findings/validation_consistency_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 21 |
| Critical | 1 |
| Major | 4 |
| Minor | 11 |
| Info | 5 |
| Agents Used | 25 |

---
*Report generated: 2026-02-27 17:17*
