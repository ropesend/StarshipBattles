# PROJ-311: Return Type Annotation Backfill and Convention

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-311` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-311 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Establish convention in CLAUDE.md | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. mypy/pyright baseline | In Progress | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Backfill annotations (per layer) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. CI enforcement | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-26
**Active Phase:** Planning (approved, ready for implementation)
**Last Action:** Project created. Verified annotation coverage: **1408 unannotated functions of 4930 total = 71.4% annotated** (NOT 59.5%/2145 as in original review). Dunder methods excluded from the denominator
**Next Action:** Begin Phase 1 — add the convention to CLAUDE.md so the rule is in place before backfill starts
**Blockers:** None — depends on no other project. Can run in parallel with everything except code that's actively being moved by PROJ-309
**Context for Next Agent:** Python 3.13+ baseline (per PROJ-295) means PEP 604 union types (`int | None`) are available; no need for `Optional[int]`. Use modern syntax in new annotations.

## Overview
Bring return-type annotation coverage from 71.4% to ≥95% across `game/`. Establish CLAUDE.md convention requiring return annotations on every public function. Optionally add a CI check (`mypy --strict-equality` or `pyright`) to prevent regression.

## Goals
- Annotate the **1408 unannotated** non-dunder functions in `game/`
- Update CLAUDE.md "Code Quality" to require return annotations on every new public function
- Optionally land a CI step that fails if annotation coverage drops below the post-backfill baseline

## Scope

**In:**
- All `game/**/*.py` non-dunder functions/methods missing a return annotation
- `__init__` methods exempt (PEP 484: implicitly return None, annotation optional)
- Other dunder methods (`__str__`, `__repr__`, `__eq__`, ...) annotated where useful but not required
- Convention update in CLAUDE.md and `docs/03_CONVENTIONS.md`
- Optional Phase 4: a CI gate

**Out:**
- Test files — annotations are encouraged but not blocking; test fixtures often resist simple annotation
- Type-checker-clean code — this project adds annotations but does NOT promise the codebase passes `mypy --strict`. That's a separate, much larger effort
- Per-parameter annotations — only return types in this project (parameter coverage is a separate cleanup if desired)

## Key Files
| Component | File Path |
|-----------|-----------|
| Convention update | `CLAUDE.md` ("Code Quality" section) |
| Conventions doc | `docs/03_CONVENTIONS.md` (§Type Annotations or similar) |
| Inventory script | `Projects/active_projects/PROJ-311/findings/annotation_audit.py` (NEW) |
| Inventory CSV | `Projects/active_projects/PROJ-311/findings/unannotated.csv` (NEW) |

## Related Documents
- [design.md](design.md) - Methodology
- [decisions.md](decisions.md) - Decisions log

## Verification
- [ ] All phase checklists complete
- [ ] Post-backfill annotation coverage ≥ 95% (verified via the AST script)
- [ ] CLAUDE.md and `docs/03_CONVENTIONS.md` document the convention
- [ ] Full sharded suite passes (15389+ baseline)
- [ ] `mypy game/` (or `pyright`) does not introduce a flood of new errors caused by bad annotations
- [ ] User verified
