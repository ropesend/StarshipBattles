# PROJ-41: Documentation Health Remediation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-41` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-41 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical Fixes | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. High Priority Updates | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Medium Priority & Archival | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-01-27 18:40
**Active Phase:** Planning
**Last Action:** Project created from documentation health audit
**Next Action:** Begin Phase 1 - Critical fixes to adding_abilities.md
**Blockers:** None

## Overview
Address all issues identified in the 2026-01-27 documentation health audit. The audit reviewed 34 documents in `docs/` and found 21 current (60%), 10 partially outdated (29%), and 4 obsolete (11%). This project systematically updates outdated docs and archives obsolete ones.

## Goals
- Fix URGENT documentation issues that cause developer confusion or broken code
- Update all HIGH priority documentation to reflect current codebase
- Archive completed/obsolete documents to reduce noise
- Improve documentation accuracy from 60% to 90%+

## Scope
**In:**
- All 10 documents marked for UPDATE in the audit
- All 4 documents marked for ARCHIVE
- Creation of `docs/archive/` organizational structure
- Creation of new `RESOURCE_SYSTEM.md` (extract from completed refactor doc)

**Out:**
- Rewriting documents that are already accurate (the 21 KEEP docs)
- Adding new documentation not identified in the audit
- Changing documentation format/structure beyond necessary fixes

## Key Files
| Component | File Path |
|-----------|-----------|
| Audit Report | `Reviews/results/2026-01-27_general_docs-health-audit/report.md` |
| Adding Abilities Guide | `docs/adding_abilities.md` |
| Adding Modifiers Guide | `docs/adding_modifiers.md` |
| Services Documentation | `docs/architecture/SERVICES.md` |
| Patterns Documentation | `docs/architecture/PATTERNS.md` |
| UI Style Guide | `docs/UI_STYLE_GUIDE.md` |
| Testing Principles | `docs/simulation_testing_principles.md` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [Reviews/results/2026-01-27_general_docs-health-audit/report.md](../../Reviews/results/2026-01-27_general_docs-health-audit/report.md) - Source audit

## Verification
- [ ] All phase checklists complete
- [ ] Documentation accuracy improved (spot-check 3 random updated docs)
- [ ] No broken references in updated documents
- [ ] Archive folder created and populated
- [ ] User verified
