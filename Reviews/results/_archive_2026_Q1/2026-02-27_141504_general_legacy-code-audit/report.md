# Review Report: 2026-02-27_141504_general_legacy-code-audit

## Metadata
- **Date:** 2026-02-27 14:15
- **Type:** General Review (Legacy Code Focus)
- **Description:** Legacy code elimination audit
- **Agents Used:** 8 review agents + 4 verification agents
- **Scope:** Entire `game/` production codebase (418 files, ~87K lines)

## Executive Summary
- **Original Findings:** 34 across 8 agents
- **After Verification:** 7 confirmed actionable | 10 disputed/false positives | 17 minor/info/keep
- **Overall Assessment:** HEALTHY - Codebase is well-maintained. PROJ-58 cleanup verified complete.

---

## Verification Process

Four skeptical verification agents independently examined all Critical and Major findings by reading actual source code, tracing all callers, and checking all usages. The verification significantly reduced the actionable finding count.

### Verification Disposition Summary

| Original ID | Original Severity | Verification Result | Revised Action |
|-------------|-------------------|---------------------|----------------|
| SIM-001 | Critical | CONFIRMED | FIX (restructure branching) |
| UIS-001 | Critical | PARTIALLY CONFIRMED | FIX (column_mgr only; scroll_bar is production code) |
| SIM-002 | Major | DISPUTED | KEEP (intentional two-tier design) |
| SIM-003 | Major | CONFIRMED | FIX (move import to module level) |
| SIM-004 | Major | DISPUTED (false positive) | KEEP (reset IS called via wrapper in conftest) |
| UIS-002 | Major | DISPUTED | KEEP (legitimate defensive UI, not compat) |
| UIS-003 | Major | DISPUTED | KEEP (different purposes: pure functions vs stateful class) |
| UIS-004 | Major | Duplicate of UIS-001 | N/A |
| STR-001 | Major | CONFIRMED | FIX (field is never used, never saved to disk) |
| STR-002 | Major | CONFIRMED | FIX (legacy path never reached in production) |
| AIR-001 | Major | DISPUTED | KEEP (behaviors are production-used, rename misleading comment) |
| AIR-002 | Major | CONFIRMED but NOT ACTIONABLE | KEEP (102-line file, standard Pygame pattern) |
| AIR-003 | Major | PARTIALLY CONFIRMED | FIX (3 of 4 unused; is_projectile IS used) |
| AIR-007 | Minor | DISPUTED (false positive) | KEEP (called internally by get_position()) |
| LEG-001 | Minor | DISPUTED | KEEP (valid base class for exception hierarchy) |
| STR-003 | Minor | CONFIRMED but NOT ACTIONABLE | KEEP (rendered in UI, removing causes crashes) |
| AIR-006 | Minor | DISPUTED | KEEP (standalone feature like Combat Lab, accessible from menu) |
| SIM-005 | Minor | DISPUTED (false positive) | KEEP (no dead code found) |

---

## Confirmed Actionable Findings (Post-Verification)

### 1. STR-002: Legacy Colonization Dual Code Path
**Severity:** Major | **Effort:** Medium
**Location:** `game/strategy/engine/fleet_order_processor.py:242-278`
**Verified By:** Backward compat agent

The colonization method has a legacy path when `component_registry is None` that removes the entire fleet instead of just the colony ship. In production, `component_registry` is always provided via `TurnEngine._registries.components`. The legacy path is only reachable through ~6 tests that skip providing a registry.

**Action:** Remove legacy path, make `component_registry` required, update ~6 tests.

---

### 2. STR-001: Dead sprite_preview Placeholder Field
**Severity:** Major | **Effort:** Simple
**Location:** `game/strategy/data/design_metadata.py:36-41`
**Verified By:** Backward compat agent

The field is always `None`. Neither `from_design_file()` nor `from_ship()` sets it. No UI code reads it. Most importantly, `DesignMetadata` is never saved to disk by the save game system - it's a runtime cache only. The "save file compatibility" justification in the comment is unfounded.

**Action:** Delete field, remove from `to_dict()`/`from_dict()`, update 3-4 tests.

---

### 3. SIM-001: AbilityManager Module Identity Drift Branching
**Severity:** Major (downgraded from Critical) | **Effort:** Medium
**Location:** `game/simulation/components/ability_manager.py:58-66`
**Verified By:** Legacy patterns agent

The `[KNOWN_ISSUE]` fallback is documented tech debt. The current if/else structure causes the MRO name-walk to run for every non-matching ability in production, not just during test module reloading. The fix should restructure the branching so the MRO fallback only fires when `target_class is None`.

**Action:** Restructure branching so MRO fallback is last-resort only.

---

### 4. UIS-001: Test-Only column_mgr Alias
**Severity:** Minor (downgraded from Critical) | **Effort:** Simple
**Location:** `game/ui/screens/empire_build_queue_window.py:155`
**Verified By:** Backward compat agent

**Partially confirmed.** The original claim incorrectly groups two attributes:
- `self.scroll_bar` is **NOT test-only** - production code uses it at 4 call sites for scroll wheel handling. The misleading comment should be fixed.
- `self.column_mgr` IS genuinely test-only - production code uses `self._column_manager` exclusively.

**Action:** Remove `column_mgr` alias, update ~6 test references. Fix misleading comment on `scroll_bar`.

---

### 5. SIM-003: Runtime Import in ComponentStatsCalculator
**Severity:** Minor (downgraded from Major) | **Effort:** Simple
**Location:** `game/simulation/components/component_stats_calculator.py:50`
**Verified By:** Simulation agent

The runtime import is real but the original reasoning was wrong - there is no circular import to avoid. `modifiers.py` imports only `logging`. The import is a historical artifact from PROJ-44 extraction. Moving to module level is trivial and matches convention.

**Action:** Move import to module level.

---

### 6. AIR-003: Unused TypeGuard Functions (3 of 4)
**Severity:** Minor | **Effort:** Simple
**Location:** `game/ai/protocols.py:169-187`
**Verified By:** Dead code agent

**Partially confirmed.** `is_projectile` IS actively used in `controller.py:127` and `target_evaluator.py:202`. The other three (`is_grid_entity`, `is_formation_master`, `is_component_health`) are genuinely unused in production.

**Action:** Remove 3 unused guards. Keep `is_projectile`.

---

### 7. AIR-001: Misleading "TEST-SPECIFIC" Comment on AI Behaviors
**Severity:** Info | **Effort:** Simple
**Location:** `game/ai/behaviors.py:405`
**Verified By:** Legacy patterns agent

These behaviors are instantiated in every `AIController` and selectable via strategy data. They have legitimate gameplay uses. The section header "TEST-SPECIFIC BEHAVIORS" is misleading.

**Action:** Rename comment section to "UTILITY BEHAVIORS" or similar.

---

## Disputed Findings (No Action Required)

| ID | Why Disputed |
|----|-------------|
| SIM-002 | Intentional two-tier design (pure DI core + convenience wrapper), not inconsistency |
| SIM-004 | `reset()` IS called via `reset_component_caches()` wrapper in root conftest |
| SIM-005 | No dead code found - all lines reachable, comments are accurate |
| UIS-002 | Standard defensive UI for missing assets, not backward compat |
| UIS-003 | Different modules: pure function library vs stateful UI class (~20 lines overlap) |
| AIR-002 | 102-line utility file, standard Pygame immediate-mode pattern, refactoring = churn |
| AIR-006 | Research is a standalone sandbox feature (like Combat Lab), accessible from main menu |
| AIR-007 | `is_vector2_like()` IS called by `get_position()` on line 88 of same file |
| LEG-001 | `SimulationException` is a valid hierarchy base class for catch-all exception handling |
| STR-003 | Economy placeholders are rendered in `empire_treasury_panel.py`, removing causes crashes |

---

## Agent Reports

### Review Agents
- [AI Research Legacy Report](findings/ai_research_legacy_report.md)
- [Core Engine Legacy Report](findings/core_engine_legacy_report.md)
- [Cross Cutting Imports Report](findings/cross_cutting_imports_report.md)
- [Deprecation Shim Hunter Report](findings/deprecation_shim_hunter_report.md)
- [Simulation Legacy Report](findings/simulation_legacy_report.md)
- [Strategy Legacy Report](findings/strategy_legacy_report.md)
- [UI Infra Legacy Report](findings/ui_infra_legacy_report.md)
- [UI Screens Legacy Report](findings/ui_screens_legacy_report.md)

### Verification Reports
- [Backward Compatibility Verification](findings/verification_backward_compat.md)
- [Dead Code Verification](findings/verification_dead_code.md)
- [Legacy Patterns Verification](findings/verification_legacy_patterns.md)
- [Simulation Verification](findings/verification_simulation.md)

---

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Original Findings | 34 |
| Confirmed Actionable | 7 |
| Disputed / False Positives | 10 |
| Minor / Info / Keep | 17 |
| Review Agents | 8 |
| Verification Agents | 4 |

---
*Report generated: 2026-02-27 14:49*
*Updated with verification results: 2026-02-27 15:30*
