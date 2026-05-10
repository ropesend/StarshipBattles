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
| 2. mypy/pyright baseline | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Backfill annotations (per layer) | Ready for parallel waves | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. CI enforcement | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-27
**Active Phase:** Phase 1+2 complete; Phase 3 ready for parallel waves
**Last Action:** Phase 1 landed convention in CLAUDE.md "Code Quality" + new §8 Type Annotations in `docs/03_CONVENTIONS.md` (renumbered Documentation Freshness to §9). Phase 2 built `findings/annotation_audit.py`, ran on `game/`, produced `inventory.csv` (5349 rows) and `unannotated.csv` (1408 rows). Confirmed baseline: **1408 unannotated of 4933 non-dunder = 71.46% coverage**, exact match to design.md.
**Next Action:** Phase 3 — six parallel waves per `findings/wave_order.md`. Wave A (core+ai+other, 88 funcs), Wave B (simulation, 109), Wave C (strategy, 57), Wave D1 (ui non-screens, 188), Wave D2 (ui/screens A–M, ~480), Wave D3 (ui/screens N–Z, ~480).
**Blockers:** None for the audit. Phase 3 must coordinate with PROJ-309 (file decomposition) on overlapping files.
**Context for Next Agent:** Python 3.13+ baseline (per PROJ-295) means PEP 604 union types (`int | None`) are available; no need for `Optional[int]`. Use modern syntax in new annotations. The audit script is reusable — re-run after each wave to confirm coverage drops to 0 in that subsystem.

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
