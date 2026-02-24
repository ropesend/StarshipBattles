# Review Scope: Protocol Gap — hasattr/getattr to Protocol Migration

## Metadata
- **Date:** 2026-02-23 19:36
- **Type:** Technical Debt Review
- **Description:** Comprehensive inventory and migration plan for 600+ hasattr/getattr calls

## Scope Definition

### Target
- [x] Specific directory: `game/` (primary), `tests/` and `simulation_tests/` (catalog only)

### Focus
All `hasattr()` and `getattr()` calls in the codebase, categorized as:
- **Category A:** Protocol candidates (interface checks → Protocol)
- **Category B:** Optional attribute access (getattr with defaults → Optional typing)
- **Category C:** Dynamic dispatch (legitimate reflection → keep, document)
- **Category D:** Legacy/transitional (backwards compat → remove)
- **Category E:** Test code (lower priority)

### Priorities
1. Complete inventory of all hasattr/getattr call sites with categorization
2. Protocol extraction plan (which new Protocols to create)
3. Per-file migration effort estimates
4. Phased implementation plan suitable for PROJ-XX conversion

### Exclusions
- Standard library / third-party code
- hasattr/getattr within Python builtins

## Agent Configuration
**Confirmed Agent Count:** 6

### Selected Agents
| Agent | Role | Finding Prefix | Status |
|-------|------|----------------|--------|
| Simulation Layer Analyst | hasattr/getattr in game/simulation/ + game/core/ | SIM | Pending |
| Strategy Layer Analyst | hasattr/getattr in game/strategy/ | STRAT | Pending |
| UI Layer Analyst | hasattr/getattr in game/ui/ | UI | Pending |
| AI Layer Analyst | hasattr/getattr in game/ai/ | AI | Pending |
| Protocol Architect | Existing protocols analysis + new protocol design | PROTO | Pending |
| Test Code Cataloguer | hasattr/getattr in tests/ + simulation_tests/ | TEST | Pending |

## Notes
- Existing protocols: 17 classes in game/core/protocols.py (580 lines)
- Prior findings: PC-003 (Major), DD-017 (Major) from Deliberate Design Debt Audit
- Active PROJ-86/87/88/89 god class decomposition creates urgency
