# Review Scope: 2026-01-28_general_full-codebase-legacy-consistency-audit

## Metadata
- **Date:** 2026-01-28 16:05
- **Type:** General Review (Extensive)
- **Description:** Full codebase audit for legacy patterns, backward compatibility code, and naming consistency

## Scope Definition

### Target
- [x] Entire codebase including tests and documentation
- Excluding: archived_projects/, node_modules/, dist/, build/, .git/

### Codebase Size
| Category | Files | Lines |
|----------|-------|-------|
| Source (game/) | 237 | 62,724 |
| Tests (tests/) | 411 | 99,262 |
| Simulation Tests | 25 | 10,814 |
| Documentation | 258 | N/A |
| **Total** | **931** | **~172k** |

### Priorities
1. **Historical/Legacy Patterns** - Old API patterns, deprecated approaches, data format migrations, architectural transitions still present
2. **Backward Compatibility Layers** - Wrappers, shims, compatibility code that should be eliminated
3. **Naming Consistency** - Terminology consistency when referring to concepts/systems across the codebase

### Exclusions
- archived_projects/
- node_modules/
- dist/
- build/
- .git/
- Any generated files

## Agent Configuration
**Recommended Agents:** 15
**Confirmed Agent Count:** 15

### Selected Agents

#### Group 1: Primary Focus Agents
| Agent | Role | Prefix | Scope | Status |
|-------|------|--------|-------|--------|
| 1 | Legacy Pattern Hunter | LPH | All source | Pending |
| 2 | Backward Compat Detector | BCD | All source | Pending |
| 3 | Naming Consistency Analyst | NCA | All source + docs | Pending |

#### Group 2: Domain Specialists
| Agent | Role | Prefix | Scope | Status |
|-------|------|--------|-------|--------|
| 4 | UI System Reviewer | UI | game/ui/ | Pending |
| 5 | Simulation Engine Reviewer | SIM | game/simulation/ | Pending |
| 6 | Strategy System Reviewer | STR | game/strategy/ + game/ai/ | Pending |
| 7 | Core Infrastructure Reviewer | CORE | game/core/ + game/engine/ | Pending |

#### Group 3: Quality Agents
| Agent | Role | Prefix | Scope | Status |
|-------|------|--------|-------|--------|
| 8 | Dead Code Hunter | DC | All source | Pending |
| 9 | Architecture Reviewer | AR | All source | Pending |
| 10 | Code Quality Analyst | CQ | All source | Pending |

#### Group 4: Test & Documentation Agents
| Agent | Role | Prefix | Scope | Status |
|-------|------|--------|-------|--------|
| 11 | Test Suite Reviewer | TSR | tests/ | Pending |
| 12 | Test Naming Consistency | TNC | tests/ | Pending |
| 13 | Documentation Reviewer | DOC | docs/ | Pending |

#### Group 5: Cross-Cutting Agents
| Agent | Role | Prefix | Scope | Status |
|-------|------|--------|-------|--------|
| 14 | Data Pattern Analyst | DPA | All source | Pending |
| 15 | Error Handling Auditor | ERR | All source | Pending |

## Launch Strategy
Agents will be launched in 3 batches of 5 (synchronous) for reliability:
- **Batch 1:** Agents 1-5 (Primary Focus + UI/Sim)
- **Batch 2:** Agents 6-10 (Strategy/Core + Quality)
- **Batch 3:** Agents 11-15 (Test/Doc + Cross-Cutting)

## Notes
- User requested extensive multi-agent swarm for full code coverage
- Focus on finding any systems/patterns that provide backward compatibility - these should be eliminated
- Naming should be consistent when describing/referring to a concept/system
- Legacy focus includes: old APIs, deprecated patterns, data migrations, architectural transitions
