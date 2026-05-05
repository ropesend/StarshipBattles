# PROJ-329A Phase 0 — Disposition docs

**Status:** Complete
**Goal:** Document the two UIWindow-retrofit deferrals the audit exposed so future audits don't re-litigate.

## Tasks

### Task 0.1: Add "UIWindow retrofit deferrals" section to `docs/known-issues.md` [Simple]

- [x] Add new section after "Tool Bugs" (or before "See Also"), titled "UIWindow retrofit deferrals (PROJ-329A)". _(Landed before "See Also".)_
- [x] DesignWorkshopScreen entry: cite `game/ui/screens/workshop_screen.py` (648 LOC), explain it's NOT a UIWindow subclass — uses factory pattern via `app.py`. Audit (PROJ-322 Task 5.10) miscategorized it. A retrofit would be a separate factory-pattern project, not in PROJ-329 scope. Cross-reference PROJ-322 plan.md Task 5.10 ACCEPTED-DEFERRED entry.
- [x] SettingsWindow entry: cite `game/ui/screens/settings_window.py` (109 LOC), raw `pygame_gui.elements.UIWindow`, no tests found. Defer until characterization tests exist or until the class is shown to be live-wired in production. Reassess when coverage exists.
- [x] Cross-reference `Projects/active_projects/PROJ-329A/findings/uiwindow_inventory.md` (will land in Phase 1).

### Task 0.2: Verify additions don't conflict with existing content [Simple]

- [x] Section title doesn't duplicate an existing one. _(Verified — no other "UIWindow retrofit deferrals" header.)_
- [x] Cross-references resolve (the `findings/uiwindow_inventory.md` path will exist after Phase 1). _(Path-relative; landing in Phase 1.)_
- [x] Markdown lint clean if there's a linter (none currently). _(N/A.)_

## Verification

- [x] `git diff docs/known-issues.md` — only the new section added; no other content modified.
- [x] Read the file end-to-end to verify the new section flows. _(Done — section sits cleanly between "Test runtime improvements" and "See Also".)_

## Phase Completion

- [x] All Task 0.X complete.
- [ ] Commit as `docs(329A): document UIWindow retrofit deferrals (DesignWorkshopScreen, SettingsWindow)`. _(Combined with Phase 1 commit per per-class commit discipline; setup docs land together.)_
