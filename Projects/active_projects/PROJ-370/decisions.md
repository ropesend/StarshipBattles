# PROJ-370: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

## Bounding decisions (made at planning time)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-05 | Project initialized | Starting point for Strategy: Data Layer Boundary Protocols (separate model from mutation). |
| 2026-05-05 | Scope bounded to **four data classes**: Fleet, Planet, Empire, ShipInstance | Tech-debt review #3 names these as the high-traffic write surface. Galaxy is structurally different (already routed through `GalaxyEntityRegistry` + `GalaxySpatialIndex`) and is the premise of PROJ-372; pulling it in re-litigates that project. Star/StarSystem/WarpPoint/Storm have generation-time writes only — no engine writes them after galaxy build, so the protocol carries no leverage. |
| 2026-05-05 | **Five phases**: 1 = foundation + AST harness; 2 = Fleet; 3 = Planet; 4 = Empire (depends on Fleet + Planet); 5 = ShipInstance (depends on Fleet — the post-battle hook prunes fleets) | Each phase is one bundled effort per data type, satisfying the CLAUDE.md "one bundled effort per data type, not many small PRs" rule. Phase 1 ships the harness ahead of any boundary work so the AST tests are green-but-empty before Phase 2 makes the first real boundary. Phases 2 + 3 are independent (Fleet and Planet do not share write surface); 03c parallel execution can run them concurrently. |
| 2026-05-05 | Read protocols **kept**, write protocols **added** as siblings | `game/core/protocols/strategy_entities.py` already defines `IFleet`, `IPlanet`, etc. They are working contracts. The gap is the write side. New module `game/core/protocols/strategy_mutators.py` mirrors the pattern. |
| 2026-05-05 | **No `IEmpire` read protocol** added in this project | Empire has no read protocol today; the mutator does not require its read-side twin. Adding `IEmpire` is a 1-hour follow-up and would expand scope. |
| 2026-05-05 | Owner service per data class is **named in the design doc**, not deferred | The review explicitly calls out "only one or two service classes own writes" as the success criterion. Deferring the name to implementation invites name churn during phase work. |
| 2026-05-05 | **Fleet has two co-owner services**: `FleetNavigationService` (location + path slice — already exists) + `FleetWriteService` (everything else — new). They both implement `IFleetMutator`; ApplicationContext composes them. | `FleetNavigationService` already proves the "mutation bridge" pattern at `services/fleet_navigation_service.py:716-759`. Folding it into a new service would duplicate the navigation pure functions and collide with PROJ-369's TurnEngine work. Two co-owners is the natural seam. |
| 2026-05-05 | **Sequencing**: PROJ-368 (OrderProcessor decomp) lands **before** PROJ-370 Phase 3 (Planet) | PROJ-368 rewrites the biggest writer of Planet's mutation surface. Targeting the new `order_handlers/` structure is much less code change than rewriting the monolith and then refactoring the rewrite. |
| 2026-05-05 | **Sequencing**: PROJ-370 lands **before** PROJ-372 (Galaxy/Planet god-class) | PROJ-372 will extract calculators/services that mutate Planet state; the mutator protocol PROJ-370 introduces is the seam they target. PROJ-372 *uses* the protocol; it doesn't re-design it. |
| 2026-05-05 | **AST guard policy**: fail per-file (one offender = test fail), use `ast.parse` not regex, allowlist is path-based | Review explicitly calls out "no compiler error; runtime crash in production" as the #1 risk. AST guard is the compiler we don't have. Per-file fail is non-negotiable; warning-only would be ignored in practice. The harness is unit-tested with synthetic in-memory fixtures so it is itself robust. |
| 2026-05-05 | **No invariant validation in the mutator** in v1 (capacity ≥ current, population ≥ 0, etc.) | The review's Phase 3 of its remediation suggests adding invariants. PROJ-370 is the *seam* layer. Adding validation simultaneously triples the blast radius and pulls in non-mutator concerns. Follow-up project: "Mutator Invariants". |
| 2026-05-05 | Mutators are **pass-through wrappers** over existing data-class methods where they exist (`fleet.add_ship`, `planet.add_to_stockpile`, `empire.add_fleet`) | Re-implementing `add_ship` to bypass `trigger_speed_recalculation` would silently break fleet speed. Mutators delegate to the existing public methods; they do not duplicate semantics. |
| 2026-05-05 | **Performance budget**: ≤ 5 % wall-time regression on the 3-empire end-turn smoke | Estimated overhead: ~50 K extra Python frames per turn for ~100 fleets × 100 ticks × 5 mutator calls. CPython ≈ 50 ns/frame on modern Windows box → ~2.5 ms wall-time. Below smoke-test noise floor. Budget formalized to catch unforeseen regressions (e.g., a hot-path mutator that does work it shouldn't). |
| 2026-05-05 | **Save format unchanged.** `to_dict`/`from_dict` are reads, not writes from the perspective of the mutator boundary | The data class itself owns its serialization. Mutators are for write-from-outside. Explicit out-of-scope item; verified by a regression test that loads a pre-PROJ-370 savegame on a post-PROJ-370 build (in the user-smoke checklist). |
| 2026-05-05 | **No facade exposure** of the new write services. Engines get them via constructor kwargs only. UI continues to emit commands | UI today does not write through engines; it emits commands. Re-exposing the mutators on the facade would re-open the boundary this project closes. |

## Open questions (to resolve at user-approval time)

| # | Question | Architect recommendation |
|---|----------|--------------------------|
| 1 | Service granularity for Fleet — split into Nav + Write or fold? | Split. See decision above. |
| 2 | Should `IShipInstanceMutator` cover `cargo_contents` / `consumable_levels` even though `ShipCargoManager` / `ShipConsumableManager` encapsulate them? | Yes, via 1-line delegation. The AST guard then catches **all** ShipInstance writes, including manager-internal. Two seams, one rule. |
| 3 | AST-guard granularity — fail per-file or warning-only? | Fail per-file. Warning-only gets ignored. |
| 4 | Add `IEmpire` read protocol in this project? | Out of scope. 1-hour follow-up. |
| 5 | Ship in 4 PRs (one per phase) or 1 PR? | 03c per-phase branches. Cumulative review at each boundary. |
| 6 | Final-verification step that loads a pre-PROJ-370 savegame? | Yes, add to user-smoke checklist. |
| 7 | Performance budget — 5 % or stricter? | 5 %. |
| 8 | Expose mutators on `StrategySessionFacade`? | No. Engines via ctor kwargs only; UI continues to emit commands. |

## Decision log (filled during implementation)

| Date | Decision | Rationale |
|------|----------|-----------|
| | | |
