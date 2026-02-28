# Review Scope: 2026-02-27_141504_general_legacy-code-audit

## Metadata
- **Date:** 2026-02-27 14:15
- **Type:** General Review (Legacy Code Focus)
- **Description:** Legacy code elimination audit

## Scope Definition

### Target
- [x] Entire production codebase: `game/` (418 files, ~87K lines)

### Priorities
1. Legacy systems still present - old implementations replaced but not fully removed
2. Backward compatibility shims - code kept "just in case"
3. Dead code paths - unreachable code, unused functions/classes, orphaned modules
4. Deprecated patterns - old patterns still in use that should have been migrated
5. Superseded implementations - parallel systems where old one should have been eradicated
6. TODO/FIXME/DEPRECATED markers still present
7. Commented-out code blocks

### Exclusions
- All test code (`tests/`, `simulation_tests/`)
- Project/review infrastructure (`Projects/`, `Reviews/`)
- Test quality concerns
- New feature suggestions
- Performance optimization
- Security review

## Agent Configuration
**Recommended Agents:** 8
**Confirmed Agent Count:** 8

### Selected Agents
| Agent | Role | Status |
|-------|------|--------|
| core_engine_legacy | Core & Engine Legacy Hunter | Pending |
| simulation_legacy | Simulation Legacy Hunter | Pending |
| strategy_legacy | Strategy Legacy Hunter | Pending |
| ui_screens_legacy | UI Screens Legacy Hunter | Pending |
| ui_infra_legacy | UI Infrastructure Legacy Hunter | Pending |
| ai_research_legacy | AI & Research Legacy Hunter | Pending |
| cross_cutting_imports | Cross-Cutting Import Analyst | Pending |
| deprecation_shim_hunter | Deprecation & Shim Hunter | Pending |

## Notes
- User's CLAUDE.md has explicit "eradicate old systems" policy
- PROJ-58 (Eradicate Backward Compat Shims) was completed previously
- God Class Decomposition projects (PROJ-86/87/88/89) are planned but not yet executed
- Looking for anything that slipped through previous cleanup efforts
- Production code only - no test code concerns
