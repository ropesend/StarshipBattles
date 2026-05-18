# PROJ-438: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-18 | Project initialized | Starting point for Strategy State Surface and Intent Lifecycle Consolidation |
| 2026-05-18 | **Assume PROJ-436 and PROJ-437 land as designed before implementation starts** | Explicit user instruction for this planning task. This project is chartered as **post-container** work and must not reopen storage or transfer-UI scope. |
| 2026-05-18 | **Leave original concern #2 (temporal scheduler / 100-tick model) out entirely** | Explicit user instruction. The temporal-model rethink remains a future project and does not belong in PROJ-438. |
| 2026-05-18 | **PROJ-438 is a combined residual-#1 + residual-#3 project, not two sibling projects** | After PROJ-423/424/425/429 and the assumed 436/437 outcomes, the remaining work is tightly coupled: persistence-shaped state surfaces and strategic intent lifecycle seams touch the same protocols, DTOs, façade surfaces, and tests. Splitting would create avoidable overlap. |
| 2026-05-18 | **Do not chase the 910-caller `ShipInstance` entry-point shim sweep here** | The retained thin shims were an intentional cost-control choice in PROJ-425. PROJ-438 may narrow `ShipInstance` further where it directly affects residual state surfaces, but it should not expand into a wholesale caller-sweep unless that falls out naturally from a narrower change. |
| 2026-05-18 | **Planet strategic intents are the primary residual #3 target** | The remaining order/intent fracture is no longer the command metadata stack. It is the stringly `IssuePlanetOrderCommand` path, the separate `PlanetActionEngine` lifecycle, and the planet-FMS/private-dispatch graft. That is the highest-value residual to clean up. |
| 2026-05-18 | **Verification gate decision is Phase 0 work** | Because `tests/unit/strategy/data/` may still be invisible to the canonical full suite, the project must explicitly decide whether to fix the collection gate or to budget direct-run verification commands. Do not assume the sharded runner alone protects this area. |
| 2026-05-18 | **No worktrees** | Standing user preference. Serial execution in the main checkout. |
| 2026-05-18 | **D1 settled in option (a) on disk before PROJ-438 began.** | PROJ-443 Phase 4 (`e12603992`) flipped `pytest.ini norecursedirs` to drop `data`, surfacing +1953 tests. Verified: `pytest.ini:6` now reads `norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv ShipThemes`. Canonical sharded suite is the verification gate for PROJ-438; no supplemental direct-run matrix required. |
| 2026-05-18 | **Re-pin `project_baseline_sha` at Phase 0** | Recorded baseline `4177fef36` pre-dated the PROJ-436 Phase 8/9 merges. Re-pinned to current `main` HEAD `eb8da3d85` so phase-base diffs are honest. PROJ-436 plan.md / phase_state.json on this checkout are *stale artifacts* (other-machine ownership); only the code state matters here. |
| 2026-05-18 | **Phase 0 baseline accepted "green-except-2 sprite quirks" by user direction** | Sharded suite: 23,207 passed / 2 failed / 2 skipped (23,211 total). The 2 failures are `tests/unit/ui/test_sprites.py::TestSprites::test_load_sprites` and `TestSpriteManagerThreadSafety::test_concurrent_load_sprites_no_corruption`. Both root-cause to `os.path.exists()` returning False at runtime on `C:\Dev2\StarshipBattles\assets\Images\Components\Components 64`, even though the directory is on disk with ~467 PNGs. Repo-wide baseline at `AgentCoordination/generated/test_baseline.json` (recorded `2026-05-18T13:47:20Z` with `failed: 0`) shows the suite is green elsewhere at this code state — confirming the failures are a checkout-local environment/path-resolution quirk in `c:\Dev2\StarshipBattles`, NOT a PROJ-438 regression. Out of scope for this project; do not address as part of PROJ-438 unless later phases discover an actual related dependency. **Per-phase verification gate for PROJ-438 = sharded suite "no NEW failures vs. this Phase 0 baseline."** |
| 2026-05-18 | **Phase 1 Task 1.3: resolve DesignCatalog asymmetry as option (b) "document"** | Empirical probe (rehydrate vs snapshot.restore on the same fixture) confirms the asymmetry is load-bearing, not drift. The save-load path MUST rebuild per-empire `DesignCatalog` instances from each empire's on-disk `DesignRepository` because it crosses a process boundary (in-memory catalog state is not preserved across a save). The snapshot/rollback path MUST NOT rebuild because rollback never crosses a process boundary — the in-memory map is still valid and an unnecessary rebuild would only waste disk I/O. Pinned by `tests/unit/strategy/engine/test_restore_path_parity.py::TestDocumentedDesignCatalogAsymmetry::test_documented_design_catalog_asymmetry`. Inline comment added to `persistence_adapter.py` explaining the intentional asymmetry and pointing at the test. Do NOT collapse the DesignCatalog block into the shared `restore_graph_wiring` collaborator. |
| 2026-05-18 | **Phase 2 collapsed to a documentation + invariant pass (no holder/sweep)** | Audit of the named concerns' blast radius (`session.save_path` 7 files, `session.human_player_ids` 28, `session.active_empire`/`enemy_empire` 68, `race_registry` 31) showed a holder-extraction + sweep approach would cost 60+ caller-file updates for marginal clarity gain. The kickoff prompt's Phase 2 scope reminder ("commit to the named concerns from plan.md:84-85. Don't expand into a façade API redesign") was binding. **Engineering decision: narrow in place.** Phase 2 adds (i) a categorical class docstring on `GameSession` grouping every attribute by ownership purpose — Owned domain state / Owned UI-rotation state / Owned UI configuration / Owned persistence metadata / Lazy-init owned services / Service-bag delegation — and (ii) matching inline category comments in `_apply_bootstrap_state`. `FacadeSessionState` docstring now explicitly marks the per-turn cache as an "intentional performance boundary" (not compensation debt). All categories + the perf boundary contract are ratcheted by `tests/unit/strategy/engine/test_game_session_projection_boundary.py` (8 tests). Substrate-then-sweep convention is satisfied because the substrate (`_apply_bootstrap_state` as the canonical assignment site, `services` property as the bag accessor) already exists from PROJ-423 — Phase 2's "narrowing" is in documentation that makes the implicit explicit. Specifically NOT done: `active_empire`/`enemy_empire` were NOT moved to a projection holder because BUG-125 establishes them as mutable owned UI-rotation state (rotated by `StrategyGameStateManager.advance_turn`), not derivable projections. Note for future projects: an actual extraction sweep would only become worthwhile if a larger pattern (e.g., a new UI session-state object emerging from another driver) creates a natural home for these attributes. Docstring kept terse (498 LOC < 500 budget) to satisfy `test_game_session_file_loc_budget`. |
| 2026-05-18 | **Phase 4 collapsed: PROJ-436 already absorbed every bounded-scope target** | Audit confirmed all three Phase 4 bounded-scope items are already handled. (i) **Planet save-schema breadth + directly-owned adjunct state** — PROJ-436 Phase 4f deleted `Planet.stockpile`/`max_stockpile`/`staging_yard` dataclass fields and replaced with backward-compat properties over private fields. The 47 declared Planet fields are intentionally preserved per PROJ-372 Risk R1 (save-format compatibility). (ii) **Fleet/Empire persistence-facing aggregate behavior** — PROJ-436 Phase 5 deleted `Empire._fleet_resource_pool` durable storage; `resource_pool` is now a pure aggregation property over `self.colonies[*].stockpile`. Fleet's 677 LOC is mostly post-storage-clean. (iii) **`galaxy_protocols.py` read contracts** — PROJ-436 Phase 6 explicitly audited and chose "leave as-is" for both `IStockpileHolder` and `IStagingYardHolder` (writers route through `IPlanetMutator`); shape is pinned by `tests/static_guards/test_no_legacy_protocol_names.py`. The decisions.md Phase 4 bounded-scope reminder authorized this collapse: "If the Phase 0 audit shows no meaningful high-ROI extractions beyond that list, Phase 4 should shrink rather than expanding into a generic entity-polish pass." **Phase 4 work product**: a 6-test ratchet at `tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py` pinning the post-PROJ-436 contract so future regressions surface immediately as Phase-4-named failures. No production code change. |
| 2026-05-18 | **Phase 3 collapsed to documentation + invariant pass (no holder/sweep)** | Post-PROJ-436 Phase 9 audit found the ship_instance.py shape is mostly already cleaned up; the remaining residue is intentional. D2 default (a) keeps `design_data` inline (rejecting design-lookup-by-id which would trigger the 910-caller sweep). The retained shim entry points (`to_dict`/`from_dict`/`to_json`/`from_json`/`clone`, `to_ship`/`update_from_ship`, resource-manager forwarders) are explicitly kept per PROJ-425 Phase 5d/5e "TD-06 Weak-LLM Guardrail #1 high-value entry points" — ~28 production callers + extensive test usage; migrating in one batch exceeds the slimming benefit. `IShipInstance.cargo_contents` removal was considered but rejected: 30+ files reference `cargo_contents` (production + test), and the protocol docstring already explicitly marks it as a backward-compat dict view pointing readers at `ShipCargoManager` / `cargo_container()`. DTOs (`fleet_dto.py`, `fleet_hierarchy_dto.py`) read concrete attributes directly (`ship.design_data.get("ship_class", ...)`) rather than going through the protocol, so no DTO-side narrowing was justified either. **Phase 3 work product**: (i) categorical class docstring on `ShipInstance` enumerating post-Phase-9 attribute/method categories (Owned identity / Owned durable state / Owned runtime state / Status flags / Cached & DI / Delegate-manager slots / Protocol-alias properties / Retained-shim entry points); (ii) 10 invariant tests at `tests/unit/strategy/ship_instance/test_post_container_surface.py` pinning the categorical shape, the legacy-shim documentation contracts on `consumable_levels` / `cargo_contents` properties, and the `IShipInstance` protocol minimum surface + cargo_contents docstring future-removal pointer. No production behavior change. |

## Deferred questions to resolve in Phase 0

### D1: Verification gate strategy — **SETTLED, OPTION (a)**

Problem:
- `pytest.ini` previously excluded any directory named `data`, which hid high-signal ratchets under `tests/unit/strategy/data/`.

Resolution (Phase 0, 2026-05-18):
- Settled in **option (a)**. PROJ-443 Phase 4 flipped `pytest.ini norecursedirs` ahead of PROJ-438 start; the line now excludes only `.* build dist CVS _darcs {arch} *.egg venv env .venv ShipThemes`. The previously-hidden ~1953 tests under `tests/unit/strategy/data/` are now collected by the canonical sharded suite. No PROJ-438 code change required. Verification gate per phase = `python Tools/test_sharded/test_sharded.py` green.

### D2: `ShipInstance` persistence boundary target

Problem:
- After PROJ-436 lands, `ShipInstance` still likely embeds broad `design_data` plus serializer/bridge shims.

Options:
- **(a) Narrow the public/protocol/serializer surface but keep inline `design_data` as durable state for now.**
- **(b) Push further toward design lookup by id plus runtime delta state.**

Default:
- **(a)** for this project. It reduces surface area without forcing another huge caller and save-shape sweep.

### D3: `JOIN_FLEET` and mission decomposition

Problem:
- These may still be explicit lifecycle special cases after the higher-value planet-intent cleanup.

Options:
- **(a) Treat them as acceptable specialized behavior if contract boundaries are otherwise clean.**
- **(b) Pull them into deeper lifecycle convergence in Phase 7.**

Default:
- **(a)** unless the implementation audit shows they still leak across contracts in a way that blocks the main cleanup.

### Bounded scope reminder for Phase 4

Phase 4 is intentionally limited to:
- `Planet` save-schema breadth and directly-owned adjunct state,
- `Fleet` / `Empire` persistence-facing aggregate behavior,
- matching read-contract cleanup in `galaxy_protocols.py`.

If the Phase 0 audit shows no meaningful high-ROI extractions beyond that list, Phase 4 should shrink rather than expanding into a generic entity-polish pass.
