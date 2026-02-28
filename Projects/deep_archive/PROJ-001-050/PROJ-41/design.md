# PROJ-41: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

This project originated from the 2026-01-27 Documentation Health Audit which reviewed all 34 documents in `docs/`. The audit used 6 parallel analysis agents to compare documentation against the actual codebase.

**Audit Results:**
- 21 documents (60%) - CURRENT, accurate, keep as-is
- 10 documents (29%) - PARTIALLY OUTDATED, need updates
- 4 documents (11%) - OBSOLETE, should be archived

## Swarm Findings Summary

Combined analysis from individual agent reports in `Reviews/results/2026-01-27_general_docs-health-audit/findings/`.

### Critical Issues (Phase 1)

| Document | Issue | Impact |
|----------|-------|--------|
| `adding_abilities.md` | Documents non-existent `apply_stat_bindings()` method | Devs write broken code |
| `adding_abilities.md` | Wrong parameter names in examples | Code fails at runtime |
| `adding_modifiers.md` | Missing PROJECTILE_STEALTH stat keys | Incomplete reference |
| `SERVICES.md` | ShipBuilderService renamed to VehicleDesignService | Confusion |
| `simulation_testing_principles.md` | References non-existent verify_themes.py | Confusion |
| `UI_STYLE_GUIDE.md` | References non-existent ui/colors.py | Confusion |

### Medium Issues (Phase 2)

| Document | Issue |
|----------|-------|
| `PATTERNS.md` | Event Bus signature mismatch in example |
| `reorg_proposal_ui.md` | Phase completion status unclear |
| `bug_tracker.md` | Example bug may be placeholder |
| `workshop_refactoring_plan.md` | Status says "Ready" but work is done |
| `LARGE_FILE_SPLIT_PLAN.md` | Implementation status scattered |

### Archive Candidates (Phase 3)

| Document | Reason |
|----------|--------|
| `phase1_completion_report.md` | Redundant with summaries |
| `phase2_completion_report.md` | Redundant with summaries |
| `phase3_completion_report.md` | Redundant with summaries |
| `test_baseline_results.md` | Very brief, historical only |
| `resource_system_refactor.md` | All phases completed |

### Key Patterns to Reuse

- **Ability Base Class**: `game/simulation/components/abilities/base.py` - Reference for correct method signatures
- **Stat Bindings**: `game/simulation/components/abilities/stat_keys.py:121-124` - Correct parameter names
- **Event Bus**: `game/ui/screens/builder/event_bus.py` - Actual emit() signature
- **VehicleDesignService**: `game/simulation/services/vehicle_design_service.py` - Renamed service

### Dependencies & Risks

1. **Cross-references** - Some documents reference each other; moving files may break links
   - Mitigation: Search for references before moving, update as needed

2. **Git history** - Moving files to archive may affect git blame
   - Mitigation: Use `git mv` to preserve history

3. **External references** - Unknown if any external tools/docs reference these paths
   - Mitigation: Accept risk; internal docs only

### Opportunities Discovered

- The refactoring documentation is exceptional and tells a great story of the project's evolution
- Consider creating a `docs/architecture/RESOURCE_SYSTEM.md` extracting current patterns from completed refactor
- May want to establish periodic documentation audits (quarterly?)

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

**Key Decisions:**
1. Fix critical issues first (Phase 1) to minimize developer confusion
2. Archive rather than delete obsolete docs to preserve history
3. Create archive structure to keep docs folder clean
