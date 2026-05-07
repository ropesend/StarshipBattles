# PROJ-348: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Starting point for Closeout Sprint 6 - Controller boundary cleanup from PROJ-329C review |
| 2026-05-04 | T5.2 declined: not-a-defect | OpenCode b3 (single reviewer, MAJOR) flagged "scene.facade reach in Stage 1". The current code at `cargo_quick_dialog.py:235` reads `scene.facade` (a property — O(1) attribute fetch) and stores the reference. No facade method is called; no I/O happens. Lines 233-234 contain an explicit comment from the prior arc declaring this intentional. Pattern §33 Stage-1 contract is "no facade I/O" — a property read of an already-bound facade reference is not I/O. Construction of the controller with `facade=self.facade` is also cheap (controller `__init__` just stores references; no method call). No fix applied. |
| 2026-05-04 | T5.1 fix shape: dialog resolves slider values; controller takes resolved_items | The controller's docstring promised "does NOT touch pygame_gui widgets" but `issue_orders` violated this. Moving slider reads into the dialog and changing the controller signature from `cargo_items: List[Dict]` (with widget references) to `resolved_items: List[Dict]` (with pre-resolved 'amount' field) restores the contract. New characterization test at `test_cargo_quick_dialog_controller_widget_purity.py` asserts the contract by passing items WITHOUT a 'slider' key — KeyError-fails if the controller regresses. |
