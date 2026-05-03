# Deliberate Design Debt Audit — Unified Report

**Date:** 2026-02-23
**Type:** General Code Review (14-agent comprehensive)
**Scope:** Entire codebase (1,234 files, ~312K lines)

---

## Executive Summary

### Overall Health Score: **B+ (7.5/10)**

The Starship Battles codebase is in **good shape** with clear evidence of ongoing improvement through systematic refactoring projects (PROJ-38, PROJ-44, PROJ-49, PROJ-50, PROJ-54, PROJ-58, PROJ-86/87/88/89). The codebase demonstrates mature engineering practices in many areas — particularly performance optimization, layer separation, and the registry/DI patterns. However, several systemic issues warrant attention, primarily around god class proliferation, pattern inconsistency, and the gap between established guidelines and older code.

### By The Numbers

| Metric | Value |
|--------|-------|
| Total findings across all agents | **244** |
| Critical | 21 |
| Major | 63 |
| Minor | 73 |
| Info | 47 |
| Positive findings noted | ~40 |
| Agents deployed | 14 |

### Agent Summary Table

| Agent | Prefix | Findings | Crit/Maj/Min/Info | Health |
|-------|--------|----------|-------------------|--------|
| Code Quality Analyst | CQ | 89 | 8/12/11/5 | — |
| Architecture Reviewer | AR | 23 | 2/10/8/3 | — |
| Test Coverage Analyst | TC | 18 | 2/6/7/3 | — |
| Error Handling Auditor | ERR | 15 | 2/5/6/2 | — |
| Dead Code Hunter | DC | 27 | 3/9/10/5 | — |
| Pattern Cataloguer | PC | 17 | 1/4/6/6 | — |
| Inconsistency Hunter | IH | 20 | 1/2/12/5 | B+ |
| Performance Profiler | PERF | 10 | 0/0/3/7 | **EXCELLENT** |
| Duplication Analyst | DUP | 15 | 2/5/4/4 | — |
| Deliberate Design Reviewer | DD | 38 | 0/5/15/18 | — |
| Module: Simulation | MOD-SIM | 18 | 3/7/6/2 | 7.5/10 |
| Module: Strategy | MOD-STR | 22 | 3/8/7/4 | 7/10 |
| Module: UI | MOD-UI | 24 | 5/10/6/3 | 6.5/10 |
| Module: Core | MOD-CORE | 17 | 2/5/7/3 | B+ |

---

## Key Strengths (What's Working Well)

### 1. Performance Engineering — EXEMPLARY
The performance profiler found **zero critical or major issues**. The codebase demonstrates:
- Documented PERF-ANALYSIS comments justifying trade-offs (PERF-001)
- Sophisticated caching with dirty flags (PROJ-49)
- O(n*m) → O(n) pre-computation in AI targeting (PERF-006, PERF-007)
- O(1) ability index with MRO support (PERF-008)
- Mark-and-sweep projectile removal (PERF-010)

### 2. Layer Separation — ZERO Violations
Architecture review confirmed **no layer violations**. The simulation layer has zero pygame imports. AI depends only on simulation/strategy. Core has no upward dependencies. This is exceptional for a codebase of this size.

### 3. Registry & DI Patterns — Mature
7 registry implementations with excellent consistency. Thread-safe SingletonMeta. DI via GameRegistries with both production and test providers. Active migration from singletons to injection (PROJ-38/50).

### 4. Test Infrastructure — Strong
7,353 tests passing with 2.2:1 test:production ratio. Comprehensive simulation test framework with template-based scenarios. Good fixture organization.

### 5. Active Refactoring Cadence
Evidence of continuous improvement: PROJ-44 (god class decomposition), PROJ-49 (performance), PROJ-54 (quality cleanup), PROJ-58 (backward compat eradication), PROJ-86/87/88/89 (god class decomposition series). Extraction documentation with PROJ-XX comments throughout.

---

## Systemic Issues (Cross-Cutting Themes)

### Theme 1: God Class Proliferation
**Agents flagging:** CQ, DD, MOD-UI, MOD-STR, AR
**Severity:** Critical
**Status:** Active remediation (PROJ-86/87/88/89)

10+ files over 800 lines, with 5 exceeding 1,000:

| File | Lines | Module |
|------|-------|--------|
| test_lab/screen.py | 1,906 | UI |
| fleet_report_window.py | 1,108 | UI |
| build_queue_screen.py | 1,084 | UI |
| weapons_panel.py | 1,037 | UI |
| race_setup_screen.py | 946 | UI |
| formation_editor.py | 941 | UI |
| galaxy.py | 928 | Strategy |
| strategy_input_handler.py | 898 | UI |
| empire_build_queue_window.py | 863 | UI |
| ship.py | 810 | Simulation |

**Assessment:** PROJ-86/87/88/89 are actively addressing this. The facade/delegate extraction pattern is proven. UI module (6.5/10 health) is the primary hotspot.

**Grouping:** Candidate for **deep-dive UI decomposition review**.

---

### Theme 2: Inconsistent Exception Handling
**Agents flagging:** IH, ERR, MOD-CORE
**Severity:** Critical
**IDs:** IH-005, ERR-001, ERR-002

Despite a well-designed exception hierarchy (PROJ-45), much code still raises generic Python exceptions:
- 50 `ValueError` raises vs 26 custom exception raises
- 4 `RuntimeError` uses
- Missing input validation in core constructors

**Assessment:** Guidelines established later; older code not updated. Clear gap between intent and reality.

**Grouping:** Candidate for **exception migration sweep** (50 occurrences, ~1 day effort).

---

### Theme 3: Dual/Triple Registry Access Patterns
**Agents flagging:** MOD-CORE, AR, DD
**Severity:** Critical
**IDs:** MOD-CORE-001, AR-002, DD-035

Three competing access patterns:
1. Direct singleton: `RegistryManager.instance().components` (30+ files)
2. Service locator: `get_default_registries()` (module-level global)
3. DI provider: `get_default_registry_provider()` (recommended but less used)

**Assessment:** Transitional state from PROJ-50. DI provider is the intended target. Migration incomplete.

**Grouping:** Candidate for **DI migration completion review**.

---

### Theme 4: Missing Abstractions / Duplication
**Agents flagging:** DUP, PC, IH
**Severity:** Major
**Estimated:** 1,500-2,000 duplicate lines

Key missing abstractions:
| Abstraction | Occurrences | Effort |
|-------------|-------------|--------|
| UITheme (font/color initialization) | 10+ files | Medium |
| DrawingUtils (pygame primitives) | 810+ Rect, 300+ blit calls | Medium |
| Ability._extract_value() | 14 instances | Simple |
| ValidationResult factory methods | 42 instances | Simple |
| BaseCommandHandler | 20+ handler classes | Medium |
| BaseJSONLoader template | 9 loaders | Medium |
| BaseDTOConverter | 57 to_dict/from_dict methods | Major |

**Grouping:** Candidate for **abstraction extraction review** (prioritize quick wins first).

---

### Theme 5: Protocol Gap (hasattr/getattr Overuse)
**Agents flagging:** PC, DD, IH
**Severity:** Major
**IDs:** PC-003, DD-017

606 `hasattr`/`getattr` calls across 131 files, but only 15 protocols defined. Suggests 50+ Protocol candidates needed. Heavy duck typing hides missing attributes from IDE and type checker.

**Grouping:** Candidate for **Protocol extraction review**.

---

### Theme 6: Logger/JSON Inconsistency
**Agents flagging:** IH, MOD-CORE
**Severity:** Major
**IDs:** IH-001, IH-010

- **Logging:** 3 competing patterns — 118 files use custom Logger, 6 use standard logging, 4 use test lab logger
- **JSON:** 18 direct `json.load/dump` vs 101 `load_json/save_json` utility calls

**Grouping:** Candidate for **standardization sweep** (JSON is quick win — 18 occurrences).

---

### Theme 7: Dead Code Accumulation
**Agents flagging:** DC
**Severity:** Major
**IDs:** DC-001, DC-002, DC-003, DC-007

| Item | Size | Action |
|------|------|--------|
| Legacy migration scripts | ~35KB | Delete |
| Duplicate formatimg.py | 5 copies | Delete 4 |
| Orphaned test_framework/ | ~338KB | Delete |
| 176 __pycache__ dirs in repo | Unknown | Add to .gitignore |

**Grouping:** Candidate for **cleanup sweep** (simple, low-risk).

---

## Deliberate Design Decisions (Accept & Document)

The Deliberate Design Reviewer identified **22 items rated "likely deliberate"**. These should be accepted and documented:

| ID | Decision | Rationale |
|----|----------|-----------|
| DD-001 | RegistryManager Singleton | Documented migration path |
| DD-008 | Deep Copy with PERF-ANALYSIS | Performance vs correctness trade-off |
| DD-010 | O(1) Ability Index | Performance critical path |
| DD-011 | INTENTIONAL LATE IMPORT | Documented in ARCHITECTURE.md |
| DD-013 | Broad exception catches (3 instances) | All commented with rationale |
| DD-023 | No save migration | Explicit policy in CLAUDE.md |
| DD-026 | Protocol over inheritance | PROJ-40 decision |
| DD-028 | Adapter pattern | Clean layer separation |
| DD-034 | Public mutable attributes | Python convention |
| MOD-SIM-005 | Dead components retain mass | Balance decision |
| MOD-SIM-012 | Crystalline armor recharges shields | Unique game mechanic |
| MOD-SIM-013 | Damage weighted by current HP | Anti-alpha-strike balance |
| MOD-STR-008 | Strict save versioning | "Saves are disposable" policy |
| MOD-STR-021 | Intentional late imports | ARCHITECTURE.md documented |

---

## "Could Go Either Way" Items (Investigate)

These need human judgment to determine if they're intentional:

| ID | Item | Severity |
|----|------|----------|
| DD-006 | StrategyScreen facade bypass (6 properties expose domain objects) | Major |
| DD-018 | StrategySessionFacade private methods return domain objects | Major |
| DD-003 | TestLabScreen 1906 lines | Major |
| DD-032 | Galaxy class 928 lines | Major |
| DD-017 | 365 getattr calls (duck typing) | Major |
| DD-012 | Pygame imports in simulation (Vector2 only?) | Minor |
| DD-015 | Zero type:ignore comments | Minor |
| MOD-SIM-011 | Emissive armor creates hard immunity at low damage | Major |
| MOD-STR-011 | Fleet warp consumes both warp + movement resources | Major |
| MOD-STR-016 | Deep space pathfinding fallback bypasses chokepoints | Major |

---

## Top 10 Priority Issues (Across All Agents)

### Tier 1: Critical (Fix Soon)

1. **MOD-STR-001 / MOD-STR-003:** Fleet registry desync + order reference resolution fragility — **data corruption risk** in strategy layer
2. **IH-005 / ERR-002:** Exception handling inconsistency — 50 ValueError should be custom exceptions
3. **MOD-CORE-001:** Dual registry access pattern — consolidate on DI provider

### Tier 2: Major (Plan & Schedule)

4. **CQ-001 / MOD-UI-001:** TestLabScreen 1,906 lines — largest god class
5. **DUP-001 / DUP-002:** UI boilerplate duplication — UITheme + DrawingUtils needed
6. **PC-003 / DD-017:** Protocol gap — 600+ hasattr calls need 50+ Protocol definitions
7. **PC-012:** Missing domain events — EventBus only in UI, not generalized
8. **MOD-CORE-003:** Logger import-time side effects — separate construction from initialization

### Tier 3: Quick Wins (Do Anytime)

9. **DUP-005:** ValidationResult factory methods — `.error()`, `.success()` (1 day)
10. **DC-001/002/003:** Dead code cleanup — delete legacy scripts, duplicate files, orphaned dirs

---

## Recommended Follow-Up Reviews

Based on the groupings above, I recommend these focused deep-dive reviews:

| Review | Scope | Key IDs | Est. Effort |
|--------|-------|---------|-------------|
| **UI God Class Decomposition** | 10 files >800 lines in game/ui/ | CQ-001, MOD-UI-001-005 | 2-3 weeks |
| **Exception Migration Sweep** | 50 ValueError, 4 RuntimeError | IH-005, ERR-001/002 | 2-3 days |
| **DI Migration Completion** | 30+ direct singleton access sites | MOD-CORE-001, AR-002 | 1 week |
| **Abstraction Extraction** | UITheme, DrawingUtils, BaseCommandHandler | DUP-001/002/005/006 | 1-2 weeks |
| **Protocol Extraction** | 600+ hasattr/getattr audit | PC-003, DD-017 | 2-3 weeks |
| **Dead Code Cleanup** | Legacy scripts, duplicates, caches | DC-001/002/003/007 | 1 day |
| **Strategy Data Integrity** | Fleet registry, order refs, zone sync | MOD-STR-001/002/003 | 3-5 days |

---

## Individual Agent Reports

All detailed findings are in the [findings/](findings/) directory:

| Report | File |
|--------|------|
| Code Quality | [code_quality_report.md](findings/code_quality_report.md) |
| Architecture | [architecture_report.md](findings/architecture_report.md) |
| Test Coverage | [test_coverage_report.md](findings/test_coverage_report.md) |
| Error Handling | [error_handling_report.md](findings/error_handling_report.md) |
| Dead Code | [dead_code_report.md](findings/dead_code_report.md) |
| Pattern Cataloguer | [pattern_cataloguer_report.md](findings/pattern_cataloguer_report.md) |
| Inconsistency Hunter | [inconsistency_hunter_report.md](findings/inconsistency_hunter_report.md) |
| Performance | [performance_report.md](findings/performance_report.md) |
| Duplication | [duplication_report.md](findings/duplication_report.md) |
| Deliberate Design | [deliberate_design_report.md](findings/deliberate_design_report.md) |
| Module: Simulation | [module_simulation_report.md](findings/module_simulation_report.md) |
| Module: Strategy | [module_strategy_report.md](findings/module_strategy_report.md) |
| Module: UI | [module_ui_report.md](findings/module_ui_report.md) |
| Module: Core | [module_core_report.md](findings/module_core_report.md) |
