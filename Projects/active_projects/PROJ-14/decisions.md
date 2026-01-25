# PROJ-14: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-25 | Project initialized | Starting point for Legacy Cleanup Phase 1 - Delete Dead Code |
| 2026-01-25 | Delete logs AND add to .gitignore | User preference: Prevent future tracking of regenerated logs. Log files are actively created by app on every run. |
| 2026-01-25 | Include Button migration in Phase 1 | User preference: Keep cleanup comprehensive as originally planned in PHASE_1_DELETE_DEAD_CODE.md. |
| 2026-01-25 | Skip missing items silently | User preference: `Debugging/Marked_for_Deletion_2026-01-20/` directory doesn't exist (already cleaned). `game/core/logger.py` line 38 commented code not found (file refactored). Don't treat as blockers. |
| 2026-01-25 | Delete test_ui_widgets.py rather than migrate tests | Tests become obsolete when Button/Label/Slider classes are deleted. Integration tests cover menu behavior. Saves effort vs. rewriting 11 tests. |
| 2026-01-25 | Keep tool-specific Button classes | `Tools/component_manager.py` and `Tools/component_graphic_picker.py` have their own Button classes. These are standalone tools, not part of main codebase. Do NOT migrate. |
| 2026-01-25 | Use callback mapping dict for pygame_gui events | Pattern: `self._menu_button_callbacks = {btn: callback}` allows clean event handling without massive if/elif chains. Matches existing patterns in codebase. |
| 2026-01-25 | Keep migration/refactor tools for reference | `migrate_data.py`, `migrate_legacy_components.py`, `refactor_phase*.py`, `audit_components.py` may be useful for future phases. Only delete clearly dead debug scripts. |

---

## Detailed Decision Records

### Decision: Log File Handling
**Date:** 2026-01-25
**Context:** Log files (`battle.log`, `combat_lab.log`, `crash_log.txt`, `collect_log*.txt`) exist in repo root but are actively created by the application on every run.
**Options Considered:**
1. Delete files only - They'll be tracked again if re-committed
2. Delete files AND add to .gitignore - Prevent future tracking
3. Skip deletion entirely - Leave as-is
**Decision:** Option 2 - Delete AND add to .gitignore
**Rationale:** Prevents continuous noise in git status. Files are transient output, not source.

### Decision: Button Migration Scope
**Date:** 2026-01-25
**Context:** Original PHASE_1_DELETE_DEAD_CODE.md includes Button migration. Could be deferred to separate project.
**Options Considered:**
1. Include in Phase 1 - Complete full cleanup as planned
2. Defer to separate project - Reduce Phase 1 scope
3. Skip Button migration entirely - Keep legacy class
**Decision:** Option 1 - Include in Phase 1
**Rationale:** User confirmed: keep cleanup comprehensive. Button class is only used in 2 files (14 instances total). Not complex enough to warrant separate project.

### Decision: Widget Test Handling
**Date:** 2026-01-25
**Context:** `tests/unit/ui/test_ui_widgets.py` has 11 tests for Button/Label/Slider classes being deleted.
**Options Considered:**
1. Delete test file - Tests become obsolete
2. Migrate tests to pygame_gui - More work but maintains coverage
**Decision:** Option 1 - Delete test file
**Rationale:** Tests specifically test legacy widget interfaces (hover detection, callback firing). After migration, these interfaces no longer exist. Integration tests (`test_app_integration.py`) cover actual menu behavior. Cost of rewriting 11 tests > value provided.
