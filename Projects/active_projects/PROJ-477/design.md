# PROJ-477: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source / gating
Deferred render/read-model tail of **PROJ-475** (planned, GATED, NOT yet executed). PROJ-475
closes the small `.session` reader tail, retires three narrow pass-throughs, and privatizes
`FacadeSessionState.session`. PROJ-477 closes the boundary by deleting the three BROAD
pass-throughs `galaxy`/`empires`/`systems`, the renderer re-exporters, and the `session` getter.
See `Projects/active_projects/PROJ-475/{plan,design,decisions}.md`, the pre-flesh consult
`AgentCoordination/Scratchpad/Consult/proj477_preflesh/advice.md`, and the post-flesh consult
`.../proj477_postflesh/advice.md`.

## Initial Analysis (verified live 2026-05-22)
The two PROJ-472 guards measure two syntactic surfaces under `game/ui/`: the
`.session`/`._session`/`.facade_state.session` chain (session guard) and runtime
`game.strategy.*` imports (import guard). Neither measures the `StrategyScreen` pass-through
*properties* `scene.galaxy`/`scene.empires`/`scene.systems`, because those reads go through a
property, not a `.session` chain. So those three remain a broad raw-domain bus, completely
unmeasured. Closing them needs (a) a THIRD guard for the property surface, and (b) a principled
access boundary that does not regress render performance.

### Consumer inventory (verified live; pre-flesh consult §1)
**RENDER-HOT (per-frame `draw()` loop via the renderer re-exporters `r.galaxy`/`r.empires`/`r.systems`):**
- `strategy_render/fleets.py:16-20` — `r.empires` → every empire's fleets.
- `strategy_render/hex_outlines.py:30-86` — `r.galaxy.state.global_hex_planets/zones/warp_points` + `r.empires`. Data rebuild turn-keyed (`:80-86`) but on the draw path.
- `strategy_render/systems.py:28-58,96-102` — `r.galaxy.systems.values()` + `r.empires`.
- `strategy_render/warp_lanes.py:23-54` — `r.galaxy.systems.values()` + `r.galaxy.get_system_by_name()`.
- `strategy_render/planets.py:33-54`, `dyson_spheres.py:42-45,92-113` — `r.empires` owner lookup.
- `strategy_renderer.py:124-134` re-exporters; `draw()` `:226-249`.

**COLD (event/menu/window-open/navigation/state-sync):**
- Menu builders: `strategy_ui.py:197-200,236-237` pass raw `galaxy` into `fleet_menu_items.py:89-142` / `planet_menu_items.py:59-97` (which traverse `galaxy.get_planets_at_global_hex`, `galaxy.empires`, `galaxy.systems`).
- List windows: `list_windows.py:41-74,100-123` pass raw `galaxy`/`empires` into `planet_list_window.py:90-111,383-389` / `star_list_window.py:188-200,507-523` (stored as `self.galaxy`/`self.empires`).
- Build-queue chain: `build_queue_windows.py:59-82`, `strategy_build_queue_manager.py:141-142,181-182,211-212,309-317` → `build_queue_screen.py:111,237,357` → `build_queue_controller.py:104-107,456-460,491-493,553-554` (`get_planets_at_global_hex`).
- `strategy_colonization.py:40-41,83-88,170-176,257,270-272`; `strategy_superweapons.py:72-86,109-110,213-221,362-367`; `strategy_camera_nav.py:44-45,91-93,108-113,160-163`; `strategy_click_dispatcher.py:560-563,594-598`; `strategy_event_router.py:397-401`.
- `strategy_screen_assets.py:29-51`; `strategy_screen_selection.py:33-35,80-83`; `strategy_game_state_manager.py:144-146,160-164`; `strategy_fleet_ops.py:65-66` (wrapper-only).
- `strategy_screen.py:201-210` (`current_empire` reads `self.empires` internally); `:547-555` (`self.galaxy._pathfinder.*`, the screen's OWN composition-root helpers — legitimate, stay allowlisted in guard #3).

**Stub UNDERCOUNTED.** The pre-flesh consult added: `strategy_build_queue_manager`,
`strategy_game_state_manager`, `strategy_screen_assets`, `strategy_screen_selection`,
`strategy_screen.current_empire`, the wrapper-only `strategy_fleet_ops`/`strategy_superweapons`
reads, AND the transitive raw-domain fan-out (menu builders → helpers; list windows →
windows; build-queue manager → screen → controller). These transitive consumers MUST migrate
or the property delete breaks them at runtime.

**Session getter consumers (live, PRE-475):** `strategy_event_router.py:223,368`,
`strategy_game_state_manager.py:164,397`, `strategy_screen_selection.py:93`,
`strategy_screen_order_editing.py:42,66,92`, `strategy_screen_lifecycle.py:49-53,155`,
`transfer_controller.py:159-176`, `strategy_windows/empire_panel_ctrl.py:51-63`,
`system_tree_panel.py:414-426` (dynamic `getattr(scene,'session')` — bypasses the AST guard).
**RE-SCAN after PROJ-475 lands** — it migrates several of these (event_router, lifecycle,
transfer_controller, empire_panel_ctrl) so the getter tail shrinks before deletion.

## Access boundary design (pre-flesh consult §2 — hybrid)
**Two seams, by access shape:**

1. **`StrategyWorldAccess` (scene-owned, live raw-domain traversal) — for render-hot + raw-window handoffs.**
   A new object constructed by `StrategyScreen` (composition root) and exposed as `scene.world`,
   handed to `StrategyRenderer` and to the few windows/helpers that genuinely need live-domain
   traversal. Allocation-light methods that hand back the UNDERLYING live collections / O(1) map
   lookups — **NO per-frame DTO allocation**:
   - `iter_systems()` → live `galaxy.systems.values()`
   - `iter_empires()` → live empires
   - `system_by_name(name)`, `system_for_object(obj)`
   - `system_at_map_hex(hex, radius=50)` (pathfinder/system-radius semantics)
   - `planets_at_exact_hex(hex)`, `zones_at_hex(hex)`, `warp_points_at_hex(hex)`
   - accessors for `global_hex_planets`/`global_hex_zones`/`global_hex_warp_points`
   This is the SINGLE raw-domain seam, so guard #3 has ONE allowlist entry for it instead of
   scattered `scene.galaxy` reads. Render migration becomes mechanical: swap the renderer's
   `r.galaxy`/`r.empires`/`r.systems` source from the deleted scene property to `scene.world`.

2. **New cold facade queries (DTO/scalar projection acceptable) — for callers needing small summaries.**
   - `facade.systems.by_name(name) -> SystemInfo | None`
   - `facade.systems.of_object(obj) -> SystemInfo | None`
   - `facade.systems.at_map_hex(hex, radius=50) -> SystemInfo | None` (NOT `near_hex(max_dist=8)`)
   - `facade.spatial.contents_at_hex(hex)` (grouped planet/zone/warp membership, preserving
     multi-hex zone membership — new `spatial` namespace, since zones/warp-points fit neither
     `planets` nor `systems`).

**Rejected:** a `facade.render.*` DTO namespace. `facade.systems.all()` / `facade.empires.all()`
allocate DTO lists per call (`grouped_namespaces.py:200-202,240-246`); `EmpireInfo.from_empire`
rebuilds `ResourceCatalog.from_json()` per call (`empire_dto.py:102-110`) — categorically wrong
per-frame. `FacadeSessionState` stays a kept-by-design per-turn cache holder
(`_facade_state.py:49-61`, pinned by `test_game_session_projection_boundary.py:111-134`), NOT a
public raw-domain render API.

## Session-getter retirement design (consult §6)
- `system_tree_panel._get_empire_context` (`system_tree_panel.py:414-426`) needs only the acting
  empire id + registries: rewire to `scene.active_empire_id` (`strategy_screen.py:225-235`) +
  `scene.registries` (`:213-222`) — drop the dynamic `getattr(scene,'session')` entirely.
- The Category B WRITE seams go through a NARROW scene-owned write handle, NOT the facade and NOT
  a reopened getter: expose `screen.order_writes` (or similar) with exactly:
  - "set active empire" (`strategy_game_state_manager.py:160-164`)
  - "set fleet path" (`strategy_screen_order_editing.py:56-67`)
  - "pop fleet order" (`strategy_screen_order_editing.py:89-92`)
  internally backed by `_session.active_empire` / `_session.fleet_mutator`.
- After migrations, retire the GETTER by making it raise `AttributeError` (message pointing to
  `screen.facade` / `screen.registries` / `screen.active_empire_id` / the write handle). Keep the
  SETTER (`strategy_screen.py:294-311`) so `screen.session = mock` still works (split-brain guard).

## Third static guard design (consult §4)
Mirror `test_facade_read_path_session_guard.py`: AST walk over `game/ui/**/*.py`, ignore
`if TYPE_CHECKING:`, exact `(file, attr_path)` allowlist (green at introduction, ratcheted down
as migrations land), positive-control matcher pin. **Match Load-context property reads only, on
the SCOPED shapes that reach the pass-through seam:**
- `<expr>.scene.galaxy|empires|systems`
- `<expr>._screen.galaxy|empires|systems`
- `screen.galaxy|empires|systems` in the `strategy_screen_*` helper modules
- `r.galaxy|empires|systems`
- optionally `self.galaxy` ONLY in `strategy_screen.py` (the pathfinder helpers `:547-555`)

**Do NOT match generic `self.galaxy`/`self.empires`/`self.systems`** — false-positives on the
constructor-injected LOCAL attrs in `build_queue_screen.py:111,357`,
`build_queue_controller.py:104-107,456-460`, `planet_list_window.py:90-111,383-389`,
`star_list_window.py:188-200,507-523`, `planet_list_helpers.py:188-190`. Match `Load` context
only so a store like `x.galaxy = scene.galaxy` flags only the RHS read.

Also harden the SESSION guard for dynamic `getattr(obj, "session")` extraction
(`system_tree_panel.py:418-425` bypasses the current matcher).

## Dependencies & Risks (consult §7)
1. **Render performance (PRIMARY).** Regression mode = replacing live map iteration with
   DTO/list allocation in the draw path. Mitigation: `StrategyWorldAccess` hands back live
   collections/O(1) lookups; render shape is unchanged (just the source of `galaxy`/`empires`).
   Verify `draw_systems`/`draw_fleets`/`hex_outlines` keep their iteration shape.
2. **System/hex-ownership SEMANTIC drift (next-biggest).** `facade.systems.near_hex(max_dist=8)`
   ≠ `galaxy._pathfinder.get_system_at_hex(radius=50)` — different ownership semantics; add the
   NEW `at_map_hex(radius=50)` rather than reusing `near_hex`. `facade.planets.at_hex` is
   exact-center only (`planet_slice.py:83-89`) — does NOT cover multi-hex zone membership; use
   `facade.spatial.contents_at_hex` / `zones_at_hex` for Dyson-Sphere zone reads.
3. **Save-compat: LOW.** UI/read-boundary work only; no schema change. Only risk is rerouting a
   save action away from the exact session object `SaveGameService` serializes — but the save
   seams are PROJ-475's, not retouched here.
4. **Determinism: LOW.** No turn-engine/simulation semantics change. Real risk is user-visible
   targeting/selection drift, not battle/turn determinism.
5. **Hot-seat viewing-vs-acting anchors must stay explicit.** Session-tree/effects/order-editing
   auth preserves `active_empire`; build/design/catalog views preserve `current_empire`/viewing
   anchor. Do not collapse them while removing the pass-throughs.
6. **Gating + re-scan.** Do not start until PROJ-475 lands; the session-getter tail shrinks
   post-475, so re-run the consumer scan before deleting the getter.
7. **TDD bottleneck.** Each property delete surfaces missed callers as `AttributeError` in tests
   immediately — delete only AFTER the guard is green and the suite passes with the property still
   present-but-unused.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
