# PROJ-316: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis
The remediation source-of-truth is the audit report at
[findings/proj_313_audit_findings.md](findings/proj_313_audit_findings.md).
Three independent verification agents confirmed the reviewer's claims
against the merged PROJ-313 code. Of the 5 claims:

- **P1.1, P1.3, P2.5** are uncomplicated factual gaps (checklists not
  updated; test uses MagicMock; doc claims don't match code). Pure
  remediation.
- **P1.2** is a documented scope deviation: PROJ-313 explicitly chose
  to keep the slot fields and `_handle_window_close` as caller-
  convenience pointers because removing them would require refactoring
  every caller of `wm.X_window` (`strategy_screen.rebuild_list()`,
  `handle_global_event` forwarding, "kill before re-open" idioms).
  This project codifies that deviation — does NOT execute the full
  demolition.
- **P2.4** is a real structural-guarantee gap. The `= None` defaults
  on strategy-screen-only windows undermine the "forgotten registration
  is impossible" goal of PROJ-313. Phase 2 closes it.

## Architecture

### Why R3a (codify deviation) over R3b (demolish)
Considered during initial remediation planning:
- **R3b would touch every `wm.X_window` caller in the codebase.** Audit
  in PROJ-313 Phase 8 noted callers in `strategy_screen.py`,
  `strategy_event_router.handle_global_event`, registrar
  "kill-before-re-open" idioms, and likely others. Estimating 30+ call
  sites across the UI layer.
- **R3a's risk is bounded.** It changes documentation and adds
  `Deferred:` notes. No code touched (in Phase 1).
- **The structural fix is already achieved.** All 21 modal-tracking
  bugs are gated on `iter_live_modals`, not on the slot fields. The
  slots are now caller-convenience pointers serving a different
  concern (rebuild_list, kill-before-reopen).
- **Pattern #30 + Pattern #31 coexistence is sustainable.** The
  superseded banner on Pattern #30 is correctable (Task 1.4) to make
  the relationship clear: Pattern #30 governs slot-cleanup for
  caller-convenience pointers; Pattern #31 governs modal tracking.

If a future maintainer wants to pursue R3b (full demolition), it
should be a separate project with its own scope assessment.

### Why Phase 2 keeps `Optional[StrategyWindowManager]` typing
The base class typing stays `"StrategyWindowManager | None"` so
`PlanetSelectionWindow` (the legitimate dual-caller, also opened from
`BuildQueueScreen`) can pass `None` explicitly. What changes is
**removing the default**: callers MUST pass the keyword (with either
a real manager or `None`). This makes "I forgot it" impossible without
forcing an unnatural required-non-None on the cross-screen window.

### Why Phase 3 uses three independent test types
- **Subclass test** (Task 3.1) catches removal of the
  `StrategyModalWindow` parent class.
- **Registration-on-construct test** (Task 3.2) catches removal of
  `register_modal(self)` from the base class.
- **Spawn-site assertion test** (Task 3.3) catches removal of
  `window_manager=ui.window_manager` from `_open_*_editor` methods.

Each test fails for a distinct mutation, so the three together cover
every way a future commit could break the structural guarantee. The
manual mutation test in Task 3.5 is the proof that the suite has
teeth.

## Key Patterns to Reuse
- **`__new__` + patched `pygame_gui.elements.UIWindow.__init__`** —
  established in `tests/unit/ui/screens/test_strategy_modal_window.py`
  and `test_planet_abilities_window_lifecycle.py`. Phase 3 Task 3.2
  uses this pattern to construct editors without booting pygame_gui.
- **`unittest.mock.patch` on the editor class at the spawn site** —
  established in `test_strategy_window_manager.py` for
  `MoveChoiceWindow` mocking. Phase 3 Task 3.3 mirrors.
- **Pattern #31 (Strategy Modal Window Base Class)** — the structural
  contract this project tightens.

## Dependencies & Risks
1. **Phase 2 likely surfaces test-only callers** that need to pass
   `window_manager=None` explicitly. Mitigation: run
   `pytest tests/unit/ui/screens/` after each window's signature
   change; address surfaced TypeErrors immediately.
2. **PROJ-315 test failures may obscure regressions** in the sharded
   suite. Mitigation: at PROJ-316 kick-off, record the exact set of
   PROJ-315 failures so the Phase 4 verification can subtract them
   precisely.
3. **`validate_audit_ready.py PROJ-313` may have errors beyond what
   Task 1.1 closes.** Mitigation: run the script after Task 1.1, fix
   any remaining errors iteratively. Document any genuinely
   un-closeable errors in `decisions.md` with reasoning.
4. **Editor classes have non-trivial `__init__` bodies** (resource
   catalog lookups, registry calls). The `__new__`-bypass pattern in
   Phase 3 Task 3.2 sidesteps this; if it doesn't work for a
   particular editor, fall back to constructing with real fixtures
   (mirrors `tests/unit/ui/screens/test_food_allocation_editor.py`).

## Opportunities Discovered
- The reviewer's audit script `validate_audit_ready.py` is a useful
  contract enforcement mechanism that PROJ-313 didn't run during
  closeout. Future projects should run it as part of their
  closeout checklist (recommend documenting this in
  `Tracking/protocols/`).
- The Phase 7 "MagicMock-only test" anti-pattern is worth flagging
  as a code review red flag — a regression test parametrised by
  string identifiers without importing the classes is almost always
  not actually testing what it claims to test.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
