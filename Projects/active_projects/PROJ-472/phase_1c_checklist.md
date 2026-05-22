# Phase 1C: StrategyScreen.session read-consumer cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-472 1c`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate the obvious read-only `.session.<attr>` /
`facade_state.session.<attr>` consumers onto facade-fed accessors, then remove
their TEMPORARY session-read-guard allowlist entries so the guard enforces them.
The migrated set is: `strategy_detail_formatter`, `list_windows`, `hex_outlines`,
`strategy_build_queue_manager` (session read), and `strategy_render/fleets`
(path-projection). A small set of live session READERS is **explicitly deferred
to PROJ-475** and stays allowlisted-with-reason (see Task 1C.7) — 1C does NOT
claim to fully close the read path. Keep the `StrategyScreen` pass-through
properties as documented transitional surfaces (deprecation = PROJ-475). Do NOT
add per-frame DTO allocation on the render hot path.

**Gate:** Phase 1A guards landed; Phase 1B done (so
`strategy_build_queue_manager.py` BQS usage is already DTO-based).

---

## Tasks

### Task 1C.1: Add facade-fed scene accessors [Complex]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add narrow scene accessors that source from the facade so consumers stop
      reading `screen.session.<x>` directly: registries (via
      `facade.session_meta.registries()`), active-empire id (via
      `facade.empires` / a viewing-empire accessor), turn (via
      `facade.session_meta.turn_number()`), empires list as needed
- [ ] KEEP the existing pass-through properties (`:160-189`) and the `session`
      property/setter (`:242-276`) — they remain documented transitional surfaces
      and stay on the session-read-guard allowlist (do NOT remove; PROJ-475 owns
      their deprecation)
- [ ] Verify no behavior change: the new accessors return the same objects the
      old `.session.<x>` reads returned

### Task 1C.2: Migrate strategy_detail_formatter [Medium]
**File:** `game/ui/screens/strategy_detail_formatter.py`
**Tests:** `pytest tests/ --testmon` + session-read guard

- [ ] `.session.registries` (`:112`, `:278`) → facade registries accessor
- [ ] `.session.turn_engine` (`:395-396`) → facade validation accessor
      (`facade.validation.can_colonize(...)` projects the colonize check without
      exposing `turn_engine`); confirm the validation namespace covers this read,
      else add the smallest facade method needed
- [ ] Remove this file's TEMPORARY session-guard allowlist entries

### Task 1C.3: Migrate list_windows [Medium]
**File:** `game/ui/screens/strategy_windows/list_windows.py`
**Tests:** `pytest tests/ --testmon` + session-read guard

- [ ] `.session.empires` (`:69`) → facade/scene accessor
- [ ] `.session.registries` (`:70`) → facade registries accessor
- [ ] Remove this file's TEMPORARY allowlist entry

### Task 1C.4: Migrate hex_outlines (render-hot — caution) [Medium]
**File:** `game/ui/screens/strategy_render/hex_outlines.py`
**Tests:** `pytest tests/ --testmon` + session-read guard

- [ ] `r.scene.session.active_empire` (`:30`) → scene/facade active-empire accessor
- [ ] KEEP the turn-keyed `_hex_outline_cache` (`:74-80`); do NOT introduce
      per-frame DTO allocation — read the active-empire id once per cache rebuild,
      exactly as today
- [ ] Confirm the turn read (`:76-79`) routes through the same accessor or stays
      on an allowlisted scene field if it is the cache key
- [ ] Remove this file's TEMPORARY allowlist entry

### Task 1C.5: Migrate strategy_build_queue_manager session read [Medium]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Tests:** `pytest tests/ --testmon` + session-read guard

- [ ] `self._screen.facade.facade_state.session.services.design_catalogs_by_empire`
      (`:82-84`) → a facade accessor for per-empire design catalogs (note
      `FacadeSessionState.get_designs_for_empire(empire_id)` already exists at
      `_facade_state.py:139-157`; expose/route through it rather than reaching
      `facade_state.session.services`)
- [ ] Remove this file's TEMPORARY allowlist entry

### Task 1C.6: Migrate strategy_render/fleets.py path-projection read [Medium]
**File:** `game/ui/screens/strategy_render/fleets.py`
**Tests:** `pytest tests/ --testmon` + session-read guard
**Failing test first:** add/extend a render unit test asserting `draw_fleet_path`
sources its segments from `facade.fleets.path_projection(fleet.id, max_turns=50)`
(monkeypatch the facade method; assert the session reader is NOT called) — confirm
it fails before the migration.

- [ ] `r.scene.session.get_fleet_path_projection(fleet, max_turns=50)` (`:85`) →
      `<facade>.fleets.path_projection(fleet.id, max_turns=50)`. Verified live
      2026-05-21: the facade method exists (`grouped_namespaces.py:141-145` →
      `fleet_slice.py:96-103`) and returns the same `List[dict]` segment shape.
      NOTE the signature difference — the facade takes a `fleet_id` (int), the
      live session call passes a `fleet` object; pass `fleet.id`, not `fleet`.
- [ ] This is a render-hot path: do NOT introduce per-frame DTO allocation.
      `path_projection` returns the same plain `List[dict]` the session call
      returned (no new DTO), so this is a one-for-one swap; keep any existing
      per-fleet caching unchanged.
- [ ] Resolve the facade reference from the existing render scene/facade handle
      (the same surface 1C.1's accessors expose); do NOT reach back through
      `r.scene.session`.
- [ ] Remove this file's TEMPORARY session-guard allowlist entry; guard passes.

### Task 1C.7: Record the deferred-to-PROJ-475 session readers [Simple]
**File:** n/a (allowlist + cross-project bookkeeping)
**Tests:** session-read guard (must stay green with these entries present)

The following live session readers are verified present (2026-05-21) but are
NOT migrated in PROJ-472. They stay **allowlisted-with-reason** in the
session-read guard and are deferred to **PROJ-475** (recorded in PROJ-475's
plan.md "Deferred from PROJ-472 Phase 1C" section). Do NOT silently leave them
unallowlisted — the guard must explicitly cover each:

- [ ] `game/ui/screens/strategy_event_router.py:223`, `:368` —
      `scene.session.get_empire(planet.owner_id)` (race-config lookup for the
      species-ideal button / `_get_race_config`). Reason: needs a facade
      empire/race-config accessor that does not yet exist; defer to PROJ-475.
- [ ] `game/ui/screens/strategy_screen_selection.py:93` —
      `screen.session.active_empire` (BUG-125 active-empire gate in
      `request_colonize_order`). Reason: paired with `strategy_screen.py`'s
      `active_empire` pass-through which PROJ-475 owns deprecating; defer.
- [ ] `game/ui/screens/strategy_windows/empire_panel_ctrl.py:62` —
      `c.scene.session.registries` (DI of registries into `EmpirePanelWindow`).
      Reason: registries DI seam tied to the pass-through surface; defer to
      PROJ-475 alongside the registries-accessor rollout.
- [ ] `game/ui/screens/strategy_screen_order_editing.py:42` —
      `screen.session.active_empire` (BUG-125 active-empire gate in
      `start_edit_move`). Reason: same active-empire pass-through dependency as
      `strategy_screen_selection.py:93`; defer to PROJ-475. NOTE `:66` and `:92`
      in this file are mutator WRITES (`session.fleet_mutator.set_path` /
      `.pop_order`) — they are mutator write seams, NOT session reads, and stay
      allowlisted under the documented write-seam reason.
- [ ] Verify each entry above is present in the guard's file+attribute-path
      allowlist with its deferral reason; positive control still trips on a
      net-new, non-allowlisted session read.

### Task 1C.8: Phase 1C verification [Medium]
**File:** n/a
**Tests:** `pytest tests/static_guards/ && pytest tests/ --testmon` then `python Tools/test_sharded/test_sharded.py`

- [ ] Session-read guard passes. The migrated consumers (1C.2–1C.6:
      `strategy_detail_formatter`, `list_windows`, `hex_outlines`,
      `strategy_build_queue_manager`, `strategy_render/fleets`) have their
      TEMPORARY allowlist entries REMOVED. The remaining allowlist is exactly:
      (a) the documented `strategy_screen.py` transitional pass-throughs
      (`:160-189`) + `session` property/setter (`:242-276`);
      (b) the explicitly-deferred-to-PROJ-475 session READERS recorded in 1C.7
      (`strategy_event_router.py:223/368`, `strategy_screen_selection.py:93`,
      `empire_panel_ctrl.py:62`, `strategy_screen_order_editing.py:42`);
      (c) mutator WRITE seams (`strategy_game_state_manager.py:164`,
      `strategy_screen_order_editing.py:66/92`).
      Nothing else is allowlisted.
- [ ] Confirm the guard matcher catches the full attribute-chain forms — verified
      2026-05-21 the live bypasses it MUST catch/allowlist include
      `self._screen.facade.facade_state.session.services...`
      (`strategy_build_queue_manager.py:82-84`) and `scene.session.get_empire(...)`
      (`strategy_event_router.py:223`, `:368`); a narrow `session.<attr>`-only
      matcher would miss the `facade_state.session.<...>` chain.
- [ ] `python Tools/test_sharded/test_sharded.py` green (full validation)
- [ ] Re-run pattern audit; confirm Pattern #5 facade-bypass count drops for the
      migrated slice; record the remaining tail as PROJ-474/475/476
- [ ] plan.md Current State honestly notes the read path is tightened (net-new
      bypasses blocked) but NOT fully closed (pass-throughs + the explicitly
      deferred PROJ-475 readers + mutator write seams remain)

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row 1C to `Complete`
- [ ] Update plan.md Current State; project ready for user verification + handoff
      to PROJ-474/475/476

_Consult §3 (session-consumer batch), §5 (corrected citations), render-hot risk.
Post-flesh Codex review Blocker 1: added `strategy_render/fleets.py` migration
(1C.6), the explicit PROJ-475 deferral of remaining live session readers (1C.7),
and an honest verification claim (1C.8). All sites verified against live code
2026-05-21._
