# PROJ-460 File Manifest

Generated 2026-05-19 during charter creation. Sourced from Codex r4 redesign Job 12 plus the archived `Projects/archived_projects/PROJ-447/findings/bucket_d_simulation_ai_research_engine_docs_scan.md` (F-D-011 partial, F-D-028).

## Files by phase

### Phase 1 — F-D-028 battle_state.py serde extraction (Production + Test)

| File | Type | Notes |
|------|------|-------|
| `game/simulation/battle_state.py` | Production | Replace `ComponentState.to_dict` (battle_state.py:48), `ComponentState.from_dict` (:59), `ShipState.to_dict` (:149), `ShipState.from_dict` (:179), `ProjectileState.to_dict` (:460), `ProjectileState.from_dict` (:482), `BattleState.to_dict` (:628), `BattleState.from_dict` (:647), `BattleResults.to_dict` (:787), `BattleResults.from_dict` (:805) — each body replaced with 1-line facade calling into `battle_state_serde.py`. |
| `game/simulation/battle_state_serde.py` | Production (new) | New module modeled on `planet_serde.py` (and `fleet_serde.py` if PROJ-459 has landed). Free-function `*_to_dict` / `*_from_dict` pairs for ComponentState, ShipState, ProjectileState, BattleState, BattleResults. The `capture_from_engine` classmethod and the `from_*` factory methods (`from_component`, `from_ship`, `from_projectile`) stay on the dataclasses since they're construction-from-runtime, not save-load. |
| `tests/integration/save_load/test_battle_state_serde_roundtrip.py` | Test (new) | TDD-first: byte-identical save output before and after extraction. |
| `tests/integration/replay/` (all) | Test (existing) | Critical regression gate. Replay capture/playback exercises BattleState round-trip. |
| `tests/integration/save_load/` (all) | Test (existing) | Critical regression gate. |
| `tests/unit/simulation/` (relevant) | Test (existing) | Verify still green. |

### Phase 2 — F-D-011 partial: battle_controller spec-in extraction (Production + Test)

| File | Type | Notes |
|------|------|-------|
| `game/simulation/battle_controller.py` | Production | Replace `BattleController.start_from_spec` body (battle_controller.py:242-368) with 1-line facade calling into `battle_controller_spec.py` (or whichever name is picked). Decision: keep on the class or move to free function — captured in `decisions.md`. |
| `game/simulation/battle_controller_spec.py` | Production (new, name TBD) | New sibling module holding the spec-in startup orchestration. Proposed name: `battle_controller_spec.py`. Alternative: `battle_spec_loader.py`. Final name decided in Phase 2. |
| `tests/unit/simulation/battle_controller/test_start_from_spec.py` | Test (existing) | Verify still green post-extraction. |
| `tests/integration/replay/` (all) | Test (existing) | Replay tests exercise the spec-in entry path. |
| Manual smoke test | Manual | Start a battle via BattleSetupScreen, confirm no visual-mode regression. |

### Phase 3 — F-D-011 partial: replay_serialization split (Production + Test)

**File naming note:** `game/simulation/replay/replay_capture.py` already exists in the package and owns the runtime capture-sink hook (`IReplayCaptureSink`, `NullCaptureSink`, `ReplayCaptureContext`). The new serialization modules use `_serde` suffixed names to avoid collision: `replay_capture_serde.py` + `replay_outcome_serde.py` + `replay_serde_helpers.py`. Verified at `game/simulation/replay/__init__.py:25-32`.

| File | Type | Notes |
|------|------|-------|
| `game/simulation/replay/replay_serialization.py` | Production (delete) | Delete after migrating callers AND updating `__init__.py` re-exports. Do NOT keep as re-export shim (CLAUDE.md "no compat shims"). |
| `game/simulation/replay/replay_capture_serde.py` | Production (new) | Holds spec-side serialization (currently lines 78-407 of replay_serialization.py): Boundary, ModifierStack, ModifierEntry, EntryVector, CombatPolicies, ShipSpec, SquadronSpec, TaskForceSpec, TeamSpec, BattleSpec — plus REPLAY_SCHEMA_VERSION constant. Imports shared helpers from `replay_serde_helpers.py`. Target: ~310 LOC after helper extraction. |
| `game/simulation/replay/replay_outcome_serde.py` | Production (new) | Holds outcome-side serialization (currently lines 407-634): ModifierApplication, HitRecord, WeaponSummary, ShipStats, ShipOutcome, TeamOutcome, BattleOutcome, plus `compute_components_registry_hash`. Imports shared helpers from `replay_serde_helpers.py`. Target: ~210 LOC after helper extraction. |
| `game/simulation/replay/replay_serde_helpers.py` | Production (new) | Shared helpers used by both serde halves: `_vec_to_list`, `_list_to_vec` (from replay_serialization.py:78-85), `_component_state_to_dict`, `_component_state_from_dict` (from :222-240). Outcome-side ship_outcome serde at :481-518 uses both pairs. Per audit feedback (Bucket D, response.md), Option A (extract to shared module) was chosen over Option B (duplicate per-half) and Option C (leader-follower) for cleanest separation. Target: ~30 LOC. |
| `game/simulation/replay/__init__.py` | Production (edit) | Update re-exports at lines 33-45 (`from game.simulation.replay.replay_serialization import ...`) to point at the new modules. Many production + test callers use `from game.simulation.replay import ...` (the package-root form) which resolves through this file; updating `__init__.py` keeps those callers working without touching them. |
| All callers of `from game.simulation.replay.replay_serialization import ...` | Production | Migrate direct imports to the appropriate new module (`replay_capture_serde` for spec-side, `replay_outcome_serde` for outcome-side). Per audit feedback: enumeration must include BOTH `rg -n "from game.simulation.replay.replay_serialization import"` (direct) AND `rg -n "from game.simulation.replay import"` (package-root) — the package-root form resolves via `__init__.py` re-exports. Known direct + indirect callers include `game/strategy/services/replay_store.py`, `game/strategy/services/replay_resolver.py`, `game/simulation/battle_runner.py`, `game/simulation/battle_controller.py`, `game/strategy/adapters/simulation_adapter.py`, `tests/integration/replay/*`, `tests/unit/simulation/replay/*`. |
| `tests/integration/replay/` (all) | Test (existing) | Critical regression gate; replay capture / playback / verification round-trip. |
| `tests/unit/simulation/replay/` (all) | Test (existing) | Verify still green. |

### Phase 4 — Document 10 next-touch simulation files (Docs only)

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-460/decisions.md` | Docs | Add 10 entries, one per next-touch file (see plan.md "Out of Scope" table). |
| `Projects/active_projects/PROJ-460/findings/PROJ-460_findings.md` | Findings | Update F-D-011 status: "actionable slice closed (battle_controller spec-in + replay_serialization split); 10 next-touch files documented in decisions.md per Codex r4 discipline rule." |

The 10 next-touch files themselves are NOT touched in this project:

| File | Current LOC (2026-05-19) |
|------|--------------------------|
| `game/simulation/systems/battle_engine.py` | 758 |
| `game/simulation/battle_runner.py` | 735 |
| `game/simulation/entities/ship.py` | 607 |
| `game/simulation/systems/tactical_mine_resolver.py` | 597 |
| `game/simulation/entities/stat_contributors/registry.py` | 570 |
| `game/simulation/entities/ship_stats.py` | 559 |
| `game/simulation/components/abilities/base.py` | 535 |
| `game/simulation/systems/battle_end_conditions.py` | 532 |
| `game/simulation/services/vehicle_design_service.py` | 516 |
| `game/simulation/combat/fleet_aura_manager.py` | 515 |

### Docs touched (likely)

| File | Type | Notes |
|------|------|-------|
| `docs/02_PATTERNS.md` | Docs | Phase 1: extend the serde pattern entry to cover the simulation-side variant (multiple paired functions for a multi-dataclass module). Phase 3: split-by-direction pattern (capture vs load) — may be a new pattern entry. |
| `docs/01_ARCHITECTURE.md` | Docs | Phase 1 + Phase 3: update the simulation-layer file listing to reflect battle_state_serde.py, replay_capture_serde.py, replay_outcome_serde.py, replay_serde_helpers.py. |

## Notes
- All phases run on `main` per user's standing no-worktrees preference.
- Phase 1 carries the most save-format risk; byte-identical save output AND replay round-trip are both gates.
- Phase 2 is the only phase requiring manual UI smoke verification.
- Phase 3 deletes the old `replay_serialization.py` entirely — must migrate all imports first.
- Phase 4 is the discipline phase. Per Codex r4: do not let it slide into "let me just look at battle_engine.py while I'm here". The 10 files are explicitly out of scope.
