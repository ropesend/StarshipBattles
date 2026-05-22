# Phase 5: Introduce `StrategyWorldAccess` + migrate the render-hot stack

> **BEFORE MARKING COMPLETE:** `python Projects/scripts/validate_phase.py PROJ-477 5`; update plan.md.

**Status:** Complete
**Objective:** Build the scene-owned `StrategyWorldAccess` live-traversal seam and migrate the
render-hot stack (`StrategyRenderer` + `strategy_render/*`) to read galaxy/empires/systems through
it — with **NO per-frame DTO allocation** (hand back live collections / O(1) map lookups).

> **SEQUENCING (POST-FLESH B2/§2.72 — PREREQUISITE, not just a note):** Task 5.1 (introduce
> `scene.world`) is a hard PREREQUISITE for Phase 4's world-handle cold consumers (4.1, 4.2, 4.3,
> 4.4, 4.5, 4.6). **Execute Task 5.1 FIRST — before Phase 4** — so cold + render consumers share
> one seam. Phases 4 and 5.2/5.3 then proceed; the property deletions wait for Phase 6.
> This is the documented CAP cut line: if a single execution pass
> is too long, STOP after Phase 4, extract Phases 5-6 to a new stub
> (`python Projects/scripts/create_project.py "PROJ-477 tail: render-hot world-access + pass-through deletion"`),
> and FLAG it. Record the new stub id in decisions.md.

---

## Tasks

### Task 5.1: `StrategyWorldAccess` object + `scene.world` [Complex]
**File:** `game/ui/screens/strategy_world_access.py` (NEW), `strategy_screen.py`
**Tests:** `pytest tests/ -k world_access`

- [x] Failing test: `StrategyWorldAccess(session_or_galaxy_provider)` exposes `iter_systems()`, `iter_empires()`, `system_by_name(name)`, `system_for_object(obj)`, `system_at_map_hex(hex, radius=50)`, `planets_at_exact_hex(hex)`, `zones_at_hex(hex)`, `warp_points_at_hex(hex)`, `planet_by_id(id)` (POST-FLESH B3 — for `_resolve_live_yard`), and accessors for `global_hex_planets`/`global_hex_zones`/`global_hex_warp_points`.
- [x] Test pins NO DTO allocation: the objects yielded by `iter_systems()` are the SAME live `StarSystem` instances as in `galaxy.systems.values()` (**element identity** — `is` on each system object, NOT on the `dict_values` view, which is fresh per call). POST-FLESH B1 nuance.
- [x] Implement `StrategyWorldAccess` reading the live galaxy/empires via the screen's composition-root `_session` (NOT a pass-through property). Hand back live collections / O(1) map lookups.
- [x] Construct it in `StrategyScreen.__init__`; expose `scene.world` property.
- [x] Verify: tests GREEN.

**Notes:** DONE as the PREREQUISITE (executed before Phase 3/4). `strategy_world_access.py`
(provider-callable backed by `_session`, lazy resolve). 11 unit tests in
`test_strategy_world_access.py`. Also added `r.world` accessor on `StrategyRenderer` (delegates to
`scene.world`) so Phase 5.3 render migration can read `r.world`. Tasks 5.2/5.3 still REMAINING. This is the single raw-domain seam. Guard #3's end-state allowlist permits `_session.*` reads inside THIS module only (composition root).

---

### Task 5.2: Renderer reads via `scene.world` [Complex]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/ -k "renderer or strategy_render"`

- [x] Failing test: `StrategyRenderer` exposes `r.galaxy`/`r.empires`/`r.systems` (or replacement accessors) sourcing from `scene.world`, not the deleted scene pass-throughs. Keep the public `r.*` names if render modules read them, but back them with `scene.world`.
- [x] Repoint the re-exporter property bodies (`:124-134`) to `self.scene.world.*` — temporarily; they are DELETED in Phase 6 once render modules read `r.world` directly. (Decide: keep `r.galaxy` shim through Phase 5, or migrate render modules to `r.world` here. Prefer migrating render modules to `r.world` so Phase 6 is a clean delete.)
- [x] Verify: tests GREEN; per-frame `draw()` shape unchanged.

**Notes:**

---

### Task 5.3: Migrate `strategy_render/*` modules to `r.world` [Complex]
**Files:** `strategy_render/{fleets,hex_outlines,systems,warp_lanes,planets,dyson_spheres}.py`
**Tests:** `pytest tests/ -k "strategy_render or hex_outline or draw_systems or draw_fleets"`

- [x] Failing/updated tests for each render module against the `r.world` seam.
- [x] `fleets.py:18` `r.empires` → `r.world.iter_empires()`.
- [x] `hex_outlines.py:40,51,63` `r.galaxy.state.global_hex_*` → `r.world.global_hex_planets/zones/warp_points`; `:68` `r.empires` → `r.world.iter_empires()`. Turn-keyed cache rebuild unchanged.
- [x] `systems.py:37` `r.galaxy.systems.values()` → `r.world.iter_systems()`; `:101` `r.empires` → `iter_empires`.
- [x] `warp_lanes.py:24` `r.galaxy.systems.values()` → `iter_systems`; `:29` `r.galaxy.get_system_by_name` → `r.world.system_by_name`.
- [x] `planets.py:35` / `dyson_spheres.py:94` `r.empires` → `iter_empires`.
- [x] Verify: tests GREEN; **NO per-frame DTO allocation introduced** (iteration shape preserved — spot-check the diff for any `from_*`/list-comprehension DTO build in the draw path).

**Notes:** This is the perf-critical step (design.md risk 1). The migration is a source-swap, not a logic rewrite.

---

## Phase Completion Checklist
- [x] All task checkboxes checked
- [x] Render stack reads `scene.world`; no per-frame DTO allocation (verified by diff + identity test)
- [x] Sharded suite green; render/animation tests green
- [x] Update status `Complete`; update plan.md table + Current State → Phase 6
