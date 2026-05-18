# PROJ-408: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-09 | Project initialized | Starting point for Tier 4: coverage gaps from PROJ-380..399 review (C-01..C-06) |
| 2026-05-09 | Effective scope reduced from 6 → 3 items (C-01, C-02, C-04) | C-05 and C-06 already shipped in Wave 1 (PROJ-404 and PROJ-401 respectively); cross-check confirmed both still pass. C-03 is the same item as MAJ-014 (an architectural decision about the UI catching raw `EnginePhaseError`) and is deferred to Wave 5 PROJ-409. |
| 2026-05-09 | C-01: replaced introspection-only test instead of supplementing it | The pre-existing `test_constructor_requires_facade` asserted `inspect.signature` shape without ever constructing the class. Per CLAUDE.md "test the production code path, not the type signature," this is bug-shaped. Deleted and replaced with `test_add_item_to_source_routes_command_through_facade` which exercises the real production path through `_facade.handle_command`. |
| 2026-05-09 | C-02: 5 tests (not 1) for the conversion site | The conversion has multiple invariants — class identity, message+code+context preservation, `__cause__` chaining, error-path skipping `invalidate_all`, and non-EnginePhaseError pass-through. Each invariant is its own assertion target so a regression that breaks one (e.g., reverts `from e`) gives a focused failure rather than a single tangled one. |
| 2026-05-09 | C-04: patch `PlanetReportPanel` + asset manager rather than fully construct | The facade-threading branch in `update()` constructs `PlanetReportPanel` after the facade call. To exercise the facade-call path without standing up a real pygame display we patch the panel constructor and assert `view=` was passed correctly. This is `direct unit coverage` of the production code, not introspection — the `update()` body actually runs. |
| 2026-05-09 | C-04: set `window._rect` after `bypass_init` instead of skipping panel-creation branch | Other tests in the module (`TestUpdateButtonDispatch`) skip the panel-creation branch by pre-seeding `current_selection_name`/`selected_planet`. For C-04 we need the branch to fire, so we set `_rect` directly (bypass_init does not run `UIWindow.__init__`, leaving the underlying sprite `_rect` slot unset). Documented in-test so future maintainers see why. |
| 2026-05-09 | No production changes | Hard rule from project plan. All three coverage gaps were testable as-is; no production class was too tangled to construct under existing fixtures. |
