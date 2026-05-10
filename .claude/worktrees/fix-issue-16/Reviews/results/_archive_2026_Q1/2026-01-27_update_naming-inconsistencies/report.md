# Update Review Report: Naming Inconsistencies

## Metadata
- **Date:** 2026-01-27
- **Type:** Update Review
- **Original Review:** [2026-01-26_consistency_naming-inconsistencies](../2026-01-26_consistency_naming-inconsistencies/)
- **Original Date:** 2026-01-26
- **Days Since Original:** 1
- **Update Chain:** 1st update

---

## Executive Summary

### Progress Overview
| Metric | Count | Percentage |
|--------|-------|------------|
| Original Findings | 14 | 100% |
| Fixed | 4 | 29% |
| Partially Fixed | 6 | 43% |
| Still Present | 1 | 7% |
| Worse | 0 | 0% |
| Obsolete | 0 | 0% |
| Cannot Verify | 3 | 21% |

### Severity Progress
| Severity | Original | Fixed | Partial | Remaining | Fix Rate |
|----------|----------|-------|---------|-----------|----------|
| Critical | 1 | 0 | 0 | 1 | 0% |
| Major | 4 | 1 | 3 | 3 | 25% |
| Minor | 5 | 3 | 2 | 2 | 60% |
| Info | 4 | 0 | 1 | 0 | N/A |

### Alerts
- **1 Critical finding NOT fixed** - duplicate BattleScene class
- **5 regressions/incomplete items** detected
- **6 NEW issues** found (2 Critical, 4 Major)

---

## Progress Visualization

```
Progress: 29% Fixed, 43% Partial, 28% Remaining
[████████░░░░░░░░░░░░░░░░░░░░░░] 29% Complete

Critical:  [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]  0%
Major:     [███████░░░░░░░░░░░░░░░░░░░░░░░] 25%
Minor:     [██████████████████░░░░░░░░░░░░] 60%
```

---

## Detailed Finding Status

### Fixed Findings (4)

| ID | Severity | Title | Evidence |
|----|----------|-------|----------|
| NC-03 | Major | ShipBuilderService shim | `ship_builder_service.py` deleted |
| NC-09 | Minor | Singleton pattern inconsistency | All singletons use `instance()` |
| NC-10 | Minor | Method aliases | Most aliases removed |
| NC-12 | Info | Component vs Module vs Part | No action needed, already standard |

### Partially Fixed Findings (6)

| ID | Severity | Title | Progress |
|----|----------|-------|----------|
| NC-02 | Major | Builder vs Workshop terminology | Workshop files created, builder_* files remain |
| NC-04 | Major | Documentation old terminology | Partially updated, still has references |
| NC-05 | Major | Battle vs Combat distinction | Exists but not documented |
| NC-06 | Minor | Screen vs Scene terminology | Pattern exists, not documented |
| NC-07 | Minor | Fleet vs Team terminology | Pattern exists, not documented |
| NC-08 | Minor | Turn vs Tick vs Phase | Pattern exists, not documented |

### Still Present Findings (1)

| ID | Severity | Title | Status |
|----|----------|-------|--------|
| NC-01 | **Critical** | Duplicate BattleScene class | Both `battle.py` and `battle_scene.py` still exist |

### Cannot Verify Findings (3)

| ID | Severity | Title | Notes |
|----|----------|-------|-------|
| NC-11 | Info | Design vs Template vs Blueprint | No formal documentation |
| NC-13 | Info | AI Controller vs Strategy Manager | No formal documentation |
| NC-14 | Info | Modifier vs Effect | No formal documentation |

---

## Regressions Found (5)

| ID | Related | Severity | Title |
|----|---------|----------|-------|
| REG-01 | NC-02 | Major | Builder/Workshop terminology incomplete |
| REG-02 | NC-02 | Major | Workshop imports from Builder directory |
| REG-03 | NC-02 | Minor | Builder method names in app.py |
| REG-04 | NC-10 | Minor | to_hit_profile alias still present |
| REG-05 | NC-01 | Critical | Duplicate BattleScene not removed |

**Details:** See [regression_report.md](findings/regression_report.md)

---

## New Issues Found (6)

| ID | Severity | Title | Location |
|----|----------|-------|----------|
| NEW-01 | **Critical** | Duplicate ProjectileManager class | `projectile_manager.py` (2 files) |
| NEW-02 | **Critical** | Legacy classes in system.py | `game/ai/core/system.py` |
| NEW-03 | Major | Duplicate InputHandler class | `input_handler.py` (2 files) |
| NEW-04 | Major | Duplicate StrategyManager class | `strategy_manager.py` + `system.py` |
| NEW-05 | Major | Duplicate Ability classes | `abilities.py` + `abilities/*.py` |
| NEW-06 | Major | Duplicate ValidationRule class | `base.py` + `validator.py` |

**Details:** See [new_issues_report.md](findings/new_issues_report.md)

---

## Recommendations

### Immediate Actions (Critical/Major)

1. **Delete `game/ui/screens/battle.py`**
   - Removes duplicate BattleScene class (NC-01)
   - Effort: Simple

2. **Complete Builder → Workshop migration**
   - Rename `builder_utils.py` → `workshop_utils.py`
   - Rename `builder_selection.py` → `workshop_selection.py`
   - Rename `builder_widgets.py` → `workshop_widgets.py`
   - Rename `builder/` → `workshop/`
   - Update all imports
   - Effort: Medium

3. **Address NEW duplicate classes**
   - Delete or consolidate duplicate ProjectileManager (NEW-01)
   - Delete `game/ai/core/system.py` (NEW-02)
   - Effort: Medium

### Short-Term Actions

4. **Update documentation terminology** (NC-04)
   - Remove "ShipBuilderService" references from docs
   - Effort: Simple

5. **Create `docs/NAMING_CONVENTIONS.md`**
   - Document Battle vs Combat distinction
   - Document Screen vs Scene patterns
   - Document Fleet vs Team layers
   - Document Turn vs Tick vs Phase timing
   - Effort: Simple

### Backlog

6. Consolidate remaining duplicate classes (NEW-03 through NEW-06)
7. Document remaining intentional distinctions

---

## Next Update Recommendation

**Recommended next update:** After completing the immediate actions above (builder→workshop migration and duplicate class cleanup)

**Focus areas for next update:**
- Verify builder terminology fully removed
- Verify new duplicate classes consolidated
- Check documentation updates completed

---

## Agent Reports
- [Validation Report](findings/validation_report.md)
- [Progress Report](findings/progress_report.md)
- [Regression Report](findings/regression_report.md)
- [New Issues Report](findings/new_issues_report.md)

## Links
- [Original Review](../2026-01-26_consistency_naming-inconsistencies/)

---

*Report generated: 2026-01-27*
*Update Review #1 for naming-inconsistencies*
