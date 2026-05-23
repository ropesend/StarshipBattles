# PROJ-449: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Architecture analysis

The two legacy-kwarg constructor wrappers (`_planet_init_with_legacy_kwargs`, `_ship_instance_init_with_legacy_kwargs`) and the five `@property`/`@setter` clusters they support are coupled shims left over from PROJ-436 Phase 3f / 4f's dataclass-field rename. The shims trade one form of debt (per-test fixture migration) for another (every reader has two write paths to the same field, every refactor has to maintain two shapes). PROJ-443 Phase 5b confirmed the ShipInstance footprint (18 test files) and chose to keep the wrapper rather than do a wide sweep at that moment. PROJ-449 reopens the deletion because Codex r4's redesign re-bundles the wrapper retirement with the catalog-of-callers sweep as a single job — the per-project sequencing makes the sweep cost amortize across both shim clusters simultaneously rather than incurring it once for each.

## Sequencing rationale

The Codex r4 redesign rows specify:
> 1. `Strategy entity wrapper retirement` - Retire the `Planet`/`ShipInstance` legacy kwarg translators and property shims, migrate `tests/fixtures/strategy_entities.py` and `planet_serde`, then drop the `IShipInstance.cargo_contents` caveat. Closes `F-A-002/003/004/005`, `F-C-020`, completes `F-C-014`. Sequential. Depends on: none. Size: large.
> 2. `Typed staging-yard substrate completion` - ... Depends on: 1 (shared `planet.py` / serde surface).

The 6-phase breakdown:
- **Phase 0 — audit-gate.** Verify counts before committing to effort (PROJ-443 5b found a 2.5× under-estimate; mitigate by re-running the audit at HEAD).
- **Phase 1 — fixture file isolated.** `tests/fixtures/strategy_entities.py` is the largest single migration site (F-C-020). Land it in its own commit so the diff is reviewable.
- **Phase 2 — sweep + serde.** Spread the per-test-file mechanical migrations across one phase, plus the load-bearing `planet_from_dict_kwargs` rewrite. Wrapper bodies still alive — phase is independently green.
- **Phase 3 — delete Planet wrapper + property cluster.** This unblocks PROJ-450.
- **Phase 4 — delete ShipInstance wrapper + property cluster.** Closes PROJ-443 Phase 5b's deferred deletion.
- **Phase 5 — protocol docstring cleanup.** Completes F-C-014.
- **Phase 6 — profile `Empire.resource_pool`.** Independent profiling-gated decision; can run in parallel.

## Key patterns reused

- **PROJ-372 planet split** (Planet → Planet + planet_serde + planet_gen) — Phase 3's `planet_to_dict` rewrite mirrors the serde-extraction pattern.
- **PROJ-293 cached-with-invalidation** — Phase 6's optional cache mirrors the `FacadeSessionState` cached planet/fleet indices pattern.
- **Static guard sibling pattern** — `tests/static_guards/test_no_legacy_storage_fields.py` is the precedent for Phases 3/4's new "absence of property" guards.

## Dependencies & Risks

1. **PROJ-450 depends on Phase 3.** The gate is **direct code inspection** in PROJ-450 Phase 0 (the SHA-signal mechanism was removed in Bucket A fix per `decisions.md` 2026-05-19). PROJ-450 Phase 0 Task 0.1 greps for `_planet_init_with_legacy_kwargs` and `@staging_yard.setter` in `game/strategy/data/`; both must be absent before PROJ-450 Phase 1 starts. Risk: PROJ-450 starts before Phase 3 lands and hits the property shims — mitigation: PROJ-450's Phase 0 verifies the precondition explicitly.
2. **F-A-007 (ship_instance.py 839 LOC) is OUT of scope.** Codex r4 explicitly named this: "F-A-007 should not be smuggled in as a side quest; if it still sits at 839 LOC after job 1, spin it as its own next-touch project." Phase 4 Task 4.5 captures the post-deletion LOC so the follow-up decision is well-informed.
3. **PROJ-443 Phase 5b regression risk.** When the wrapper was deleted in May 2026, 19 failures + 16 errors surfaced across 18 test files. PROJ-449's mitigation is reverse ordering — sweep first (Phases 1+2 with wrappers alive), then delete (Phases 3+4 with wrappers unreached). Phase 2 Task 2.4 adds optional instrumentation to confirm zero wrapper triggers BEFORE Phase 3 / 4 delete.
4. **Phase 6 profiling fixture risk.** If no save in `tests/fixtures/saves/` is representative of late-game scale, profiling won't surface a real signal. Mitigation: Phase 6 Task 6.1 explicitly allows building a synthetic 100+-colony fixture.

## Opportunities discovered

- **F-A-025 free-rider in Phase 2.** While rewriting `planet_from_dict_kwargs`, the same hunk carries the `data.get("resources", {})` legacy alias removal (per CLAUDE.md "saves are disposable"). Zero added cost.
- **F-A-022 / F-A-024 free-riders out of scope.** Other "saves are disposable" cleanups in `stars.py` / `storm.py` are not in scope; they belong to Codex r4 job 5 (engine/service surface polish).

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
