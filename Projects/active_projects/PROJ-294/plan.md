# PROJ-294: QA Observer Path Bootstrap (ModuleNotFoundError fix)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-294` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-294 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Bootstrap sys.path in observer.py | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-04-26 06:30
**Active Phase:** Planning Complete — awaiting user approval
**Last Action:** Plan drafted; research findings written to findings/research.md
**Next Action:** User reviews plan; on approval, implement Phase 1
**Blockers:** None — straightforward ~4-line fix
**Context for Next Agent:** See [findings/research.md](findings/research.md). The fix follows an established pattern already used by 13 other Tools/ scripts.

## Overview

[Tools/qa_observer/observer.py:222](../../../Tools/qa_observer/observer.py#L222) does `from game.core.paths import Paths` inside a `finally` block. When [qa_launcher.py:32](../../../qa_launcher.py#L32) spawns observer with `cwd=observer_dir` (so the local `.env` loads), the project root isn't on `sys.path` and the import crashes with `ModuleNotFoundError: No module named 'game'` after the user quits the game.

**Fix:** Add a `sys.path.insert(0, project_root)` bootstrap at the top of `observer.py`, mirroring the pattern already used by 13 other Tools/ scripts.

## Goals

- Eliminate the `ModuleNotFoundError` traceback at the end of every QA observer session
- Ensure observer's log-copy step (lines 219-235) actually runs to completion
- Don't break existing `.env` loading behavior

## Scope

**In:**
- Modify [Tools/qa_observer/observer.py](../../../Tools/qa_observer/observer.py) to bootstrap `sys.path`
- Manual smoke verification via `qa_launcher.py`

**Out:**
- Touching [qa_launcher.py](../../../qa_launcher.py) (its `cwd=observer_dir` is correct for `.env` resolution)
- Refactoring `.env` resolution to be file-relative (working as intended)
- Adding tests for the QA observer (it's a developer tool — no existing tests)
- The other 12 Tools/ scripts that import `game.*` (already use the bootstrap or run from project root — unaffected)

## Key Files

| Component | File Path |
|-----------|-----------|
| QA Observer entrypoint | [Tools/qa_observer/observer.py](../../../Tools/qa_observer/observer.py) |
| Launcher (read-only) | [qa_launcher.py](../../../qa_launcher.py) |
| Reference pattern | [Tools/visual_test_galaxy/visual_test_galaxy.py:17](../../../Tools/visual_test_galaxy/visual_test_galaxy.py#L17) |
| Reference pattern | [Tools/analyze_dependency_graph/analyze_dependency_graph.py:26](../../../Tools/analyze_dependency_graph/analyze_dependency_graph.py#L26) |

## Related Documents

- [design.md](design.md) - Design rationale (why sys.path.insert vs cwd change)
- [decisions.md](decisions.md) - Decision log
- [findings/research.md](findings/research.md) - Tools/ patterns + .env behavior

## Verification

- [ ] Phase 1 checklist complete
- [ ] Manual smoke: `python qa_launcher.py` launches game, exits cleanly, no `ModuleNotFoundError` traceback
- [ ] User verified
