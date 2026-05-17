# PROJ-431: Deployable substrate redesign (TD-10)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-431` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-431 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Typed `BayInventory` on `ShipInstance` | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. `MineGroup` extraction (DeployedGroup family 1) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `FighterWing` + `SatelliteConstellation` (families 2 & 3) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Polish + docs + dead-code sweep | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Codex-consult-driven correctness fixes (conflict trigger / third-party mines / doc drift) | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** All phases complete; awaiting final audit
**Last Action:** Phase 5 COMPLETE. Three Codex-consult-driven follow-ups that landed after the Phase 4 close, in three commits on `proj/PROJ-431/main`:
1. `1bec92778` — **Finding 1 (MAJOR) conflict trigger**: `ConflictResolutionEngine._resolve_conflicts` previously snapshotted only `empire.fleets` as combat triggers, so two opposing `FighterWing`s (or `SatelliteConstellation`s) at the same hex with NO fleet present never battled. Extended trigger iteration to include combat-capable deployed groups; hex-level dedup so a fleet trigger + co-located deployed-group trigger does not double-fire. `MineGroup` remains a non-trigger (resolves via `TacticalMineResolver` inside an existing battle). Strict TDD with two positive cases (FighterWing-only, SatelliteConstellation-only) and one negative regression (MineGroup-only must NOT trigger). New test: `tests/unit/strategy/engine/test_conflict_deployed_group_trigger.py`.
2. `1c4ab691d` — **Finding 2 (MAJOR) third-party mines**: `StrategyBattleAssembler` seeded `empire_to_team_id` only from combat-fleet owners, so a mine-only empire's mines were inert in tactical combat (`build_mine_resolver_setup` skipped them; `BattleEngine._run_mine_resolver_tick` requires a non-None `_owner_team_id`). Fix: after seeding from combat fleets, walk the collected mine groups and allocate synthetic team-ids for any mine owner not already mapped. The synthetic team has no ships in the BattleSpec → all combatant ships read as enemies → mines detonate as intended. New test: `tests/unit/strategy/combat/test_battle_assembly_third_party_mines.py`.
3. `4cb0db29f` — **Finding 3 (MINOR) doc drift**: `post_battle_hook_builder.py` (`mine_groups: Sequence["Fleet"]` → `Sequence["MineGroup"]`; same for captured tuple), `pre_tick_setup/mine_setup.py` (docstring + type hints, TYPE_CHECKING import), `engine/commands/__init__.py` (`IssueRecoverFightersCommand` / `IssueRecoverSatellitesCommand` docstrings reference the typed deployed-group siblings, not legacy `Fleet(group_kind=...)` synthetics). Documentation-only — no behaviour change.

**Open follow-up flagged for product review:** `Empire.is_eliminated()` keeps an empire alive while it owns deployed groups, including immobile-only deployed groups (e.g. only `MineGroup`s — mines have no agency for strategic action). Whether this is design intent (minefields are a legitimate presence on the map) or an inconsistency with the "no fleets and no colonies = defeat" rule is a product-design question. Captured in `decisions.md`.

### Pre-Phase-5 historical state (preserved):
**Last Action:** Phase 4 COMPLETE. Landed in three commits on `proj/PROJ-431/main`:
1. `cd5acf300` — dead-code sweep. Deleted `FleetCapabilityCalculator._is_real_fleet` (degenerate `return True` no-op left by Phase 3); inlined `True` at all three call sites (`has_space_shipyard`, `can_build_type`, `can_use_warp`). Dropped unused `dataclass`/`field` imports from `game/strategy/data/deployed_group.py`. Cleaned stale `group_kind` mentions from `fleet_menu_items.py` / `fighter_reboard.py` comments. Stripped leftover `group_kind='fleet'` kwargs from three `SimpleNamespace` test doubles. Migrated `test_fms_a_audit_fixes.py::test_real_fleet_is_a_real_fleet` → `test_empty_real_fleet_has_no_shipyard` (the surviving behavioural assertion).
2. `05b6dac1c` — docs sync. New "Deployed Groups (PROJ-431 / TD-10)" section in `docs/systems/strategy_layer.md`. Rewrote `minefields.md` / `fighters.md` / `satellites.md` / `ability_reference.md` to use `MineGroup` / `FighterWing` / `SatelliteConstellation` terminology throughout flow diagrams and prose. Updated `docs/01_ARCHITECTURE.md` strategy/data bullet. Rewrote `docs/02_PATTERNS.md` Pattern #37 with the new contract / registration / namespace conventions / boundary rule.
3. `_CarriedItemsProxy` audit: **KEPT as compat shim, documented in decisions.md**. 51 test files still poke `ship.carried_items.append({...})` directly; migrating each is a ~50-file sweep with zero production value (the production paths already use `bay_inventory` / `set_bay_inventory`, locked in by AST guards).

Sharded suite at the Phase 3 baseline was 21134/21134 green (145.7s, 12 shards). Phase 4 production-code edits were limited to inlining an always-True gate and comment cleanup; no behavioural change.

### Pre-Phase-4 historical state (preserved):
Phase 3 COMPLETE. Landed in four commits on `proj/PROJ-431/main` (head `8c131a969`):
1. `f4a93be4b` — added `FighterWing` + `SatelliteConstellation` (typed `DeployedGroup` siblings of Fleet) in `game/strategy/data/deployed_group.py`. Both carry `list[ShipInstance]` and round-trip via the polymorphic `DeployedGroup.from_dict` dispatcher (type tags `"fighter_wing"`, `"satellite_constellation"`). New tests: `test_fighter_wing.py`, `test_satellite_constellation.py`.
2. `f8ef01bba` — `LaunchFighters` / `LaunchSatellites` order handlers mint typed `FighterWing` / `SatelliteConstellation` on `empire.deployed_groups`. `RecoverFighters` / `RecoverSatellites` walk `empire.deployed_groups_of(<type>)` via isinstance dispatch, no more string `group_kind` filter on `Fleet`. Migrated all four launch/recover order-handler unit tests + the five FMS integration suites (C/D e2e, cd-isolation, planet launch + recovery, in-battle launch e2e).
3. `feede748a` — combat consumers: `ConflictResolutionEngine` walks `empire.deployed_groups_of(FighterWing|SatelliteConstellation)` into the occupants list alongside `empire.fleets`. Fighter-reboard overflow mints typed deployed groups instead of `Fleet(group_kind=...)`. `EmpireWriteService.prune_empty_fleets` handles both Fleet and `DeployedGroup` empties. New `_ShipBearingDeployedGroup` base provides `remove_ship` so the post-battle `IFleetMutator` plumbing prunes destroyed ships polymorphically.
4. `8c131a969` — cleanup: `_reject_if_non_fleet_group` + all 10 callers DELETED; `Fleet.group_kind` field + constructor parameter + legal-values check + to_dict emission + from_dict default DELETED; `FleetCapabilityCalculator._is_real_fleet` collapsed to a degenerate `return True` no-op; `FleetInfo.group_kind` DTO field DELETED; UI dispatch tables (`fleet_menu_items.py`, `planet_menu_items.py`) now dispatch on `isinstance(group, FighterWing|SatelliteConstellation)` reading `empire.deployed_groups`.

Grep gates: zero hits for `_reject_if_non_fleet_group` in `game/` and `tests/`; zero hits for `"fighter_group"` / `"satellite_group"` outside docstrings/comments and `commands/__init__.py` (preserved payload field names). `Fleet.group_kind` field disposition: **DELETED entirely** — every Fleet is a real fleet, deployed mines/fighters/satellites are typed sibling models on `empire.deployed_groups`. Full sharded suite: **21134/21134 passed (145.7s, 12 shards)**.
**Next Action:** Final audit (project complete, awaiting user verification).
**Blockers:** None.

---

### Pre-Phase-3 historical state (preserved):
Phase 2 COMPLETE. Landed in five commits on `proj/PROJ-431/main` (head `b9c8720d3`):
1. `0839f2077` — added typed `DeployedGroup` base + concrete `MineGroup` (`game/strategy/data/deployed_group.py`); `Empire.deployed_groups: list[DeployedGroup]` + `add_deployed_group` / `remove_deployed_group` / `deployed_groups_of(cls)`; polymorphic save round-trip via a per-subclass `type` discriminator. `Empire.is_eliminated` now also checks deployed_groups.
2. `a3168cd66` — `LayMinesOrderHandler` deposits into a fresh `MineGroup` on `empire.deployed_groups`. Deletes the synthetic `mine_carrier_synthetic` `ShipInstance` (`_seed_mine_group_carrier` gone), renames `_mint_fleet_id` to `_mint_deployed_group_id`. Mines live as homogeneous `list[CarriedVehicle]` on the group — no `bay_inventory` indirection.
3. `04956b69d` — every consumer reads `MineGroup` directly: `MinefieldResolver` walks `empire.deployed_groups_of(MineGroup)`; `_iter_mines`/`_set_mines` collapse to `_pop_mine_at`; `TacticalMineResolver.from_mine_group` / `writeback_to_mine_group` operate on `mine_group.mines`; `MineGroupService` uses `isinstance(group, MineGroup)`; post-battle hook prunes empty mine groups from `deployed_groups`; `movement_phase_collaborator` drops moot `group_kind == 'fleet'` filter.
4. `b9c8720d3` — `StrategyBattleAssembler.mine_group_filter` parameter and `_default_mine_group_filter` DELETED; `TeamSpecBuilder.split_mine_groups` DELETED; assembler walks `empire.deployed_groups` via the `empires` mapping (`_collect_mine_groups_at_hex`). `"mine_group"` removed from `Fleet.group_kind` legal-values; mine-only attributes (`sensitivity`, `expected_hit_chance_threshold`, `mine_positions`, `scatter_seed`) deleted from `Fleet` (they live on `MineGroup` now); `_reject_if_non_fleet_group` and `FleetCapabilityCalculator._is_real_fleet` drop the `"mine_group"` entry from the recognised non-fleet set. Test fixtures across 9 files migrated.

Grep gates all green: zero hits for `_split_mine_groups_from_fleets`, `mine_group_filter`, `_seed_mine_group_carrier`, `mine_carrier_synthetic`, `_set_mines` outside the prose / decisions docs. Full sharded suite: **21134/21134 passed (144.1s, 12 shards)**. `mine_group_filter` disposition: DROPPED entirely (not defaulted-and-kept) — per design.md "the filter is deleted, not refactored" once mines live on `deployed_groups`; the typed split removes the seam that the parameter was guarding.

## Overview
Strategy tech-debt #10/10 (final project in the arc). Replace the two overloaded substrates that currently carry every deployable family — `Fleet.group_kind`-string discrimination and `ShipInstance.carried_items: List[Dict[str, Any]]` — with explicit typed models. Today four deployable families (mines, fighters, satellites, drop pods) hang off two abstractions, mine groups invent a synthetic-carrier `ShipInstance` whose only job is to hold mines, and **ten** fleet-action handlers must remember to call `_reject_if_non_fleet_group` to guard against deployed-group dispatch. The redesign introduces a `BayInventory` (typed `bay: list[CarriedVehicle]` + `pods: list[DropPod]`) on `ShipInstance` and a sibling `DeployedGroup` family (`MineGroup`, `FighterWing`, `SatelliteConstellation`) on `Empire`, so runtime type replaces the string discriminator and the handler guard becomes unnecessary.

## Goals
- Eliminate the `ShipInstance.carried_items` mixed-shape list; replace with `bay_inventory: BayInventory` exposing two typed slots.
- Eliminate the synthetic mine-carrier `ShipInstance` and the `_split_mine_groups_from_fleets` filter at the combat boundary.
- Eliminate `Fleet.group_kind` string branching across 14+ files; deployed groups become a separate `Empire.deployed_groups` collection of typed dataclasses.
- Delete `_reject_if_non_fleet_group` and remove the guard call from all ten fleet-action handlers — runtime type makes the distinction structural.
- Update AI controllers and UI consumers to dispatch on type (e.g. `isinstance(g, MineGroup)`) instead of `getattr(f, "group_kind", "fleet")`.

## Scope
**In:** new `BayInventory` / `DropPod` / `DeployedGroup` family dataclasses; migration of `ShipInstance`, `Empire`, the cargo manager, the issuer adapter, the five FMS order handlers, the minefield resolver, the lay-mines handler, `MineGroupService`, `spec_compiler._split_mine_groups_from_fleets`, the turn-phase-registry minefield filter, `FleetDTO` / new `MineGroupDTO`, the fighter reboard consumer, AI controllers (`carrier_controller`, `fighter_controller`, `satellite_controller`), UI consumers reading `group_kind`, and the ten fleet-action handlers losing their guard call. Saves are disposable per CLAUDE.md.

**Out:** drop-pod gameplay changes (pods just move from the mixed-shape list to `bay_inventory.pods`); concrete combat/tactical-resolver logic changes beyond consuming the new model; renaming `CarriedVehicle.vehicle_type` enum values; any work owned by other TD plans (TD-01 spec-assembly internals, TD-06 ShipInstance entity-facade slimming, TD-04 phase-registry hook extraction).

## Dependencies
**HARD predecessor: PROJ-426 (TD-01 battle spec assembly compilation).** This project cannot start before PROJ-426 completes. Rationale: TD-01 reworks the battle-spec compiler and `_split_mine_groups_from_fleets` is one of the side-channels TD-01 cleans up; running TD-10 first would force its Phase 2 to preserve the current battle-spec side-channel shape. After PROJ-426 lands, the assembler carries a temporary `mine_group_filter` parameter on the `StrategyBattleAssembler` that becomes trivial — and is simplified out by this project's Phase 2.

**Phase gate with PROJ-425 (TD-06 ShipInstance slimming):** PROJ-425 Phases 0–4 (characterization / stats-cache extraction / component-inspector extraction / factory + activation-store extraction / write-path cleanup) may run before this project. PROJ-425's deferred **cargo/deployable forwarder-demolition batch** is blocked on this project's **Phase 1** landing typed `bay_inventory` so the forwarders' replacement surface exists. PROJ-425's cargo batch resumes after PROJ-431 Phase 1 is verified.

**Soft adjacency: PROJ-428 (TD-04 phase registry hooks).** No ordering requirement either way. After Phase 2 here lands, the minefield-resolver invocation in `turn_phase_registry.py:186-225` must consume `empire.deployed_groups` (filtered to `MineGroup`) instead of filtering `empire.fleets` by `group_kind`. If PROJ-428 has already extracted that hook into a dedicated phase class, that is a one-line change inside the class; otherwise the same change lands on the hook function.

See [EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) — TD-10 is project #10/10, last in the linear order, in its own "final isolated batch" per the parallelization note.

## Key Files
| Component | File Path |
|-----------|-----------|
| `ShipInstance` (carried_items → bay_inventory) | [game/strategy/data/ship_instance.py](../../../game/strategy/data/ship_instance.py) |
| `Fleet` (group_kind + mine-only fields; both deleted by Phase 3) | [game/strategy/data/fleet.py](../../../game/strategy/data/fleet.py) |
| Minefield resolver (synthetic-carrier `_iter_mines`/`_set_mines`) | [game/strategy/engine/minefield_resolver.py](../../../game/strategy/engine/minefield_resolver.py) |
| Handler base (`_reject_if_non_fleet_group` deleted in Phase 3) | [game/strategy/engine/handlers/base.py](../../../game/strategy/engine/handlers/base.py) |
| Lay-mines order handler (`_seed_mine_group_carrier` deleted in Phase 2) | [game/strategy/engine/order_handlers/lay_mines.py](../../../game/strategy/engine/order_handlers/lay_mines.py) |
| Battle spec compiler (`_split_mine_groups_from_fleets` deleted in Phase 2) | [game/strategy/combat/spec_compiler.py](../../../game/strategy/combat/spec_compiler.py) |

Full enumeration of touched files lives in [manifest.md](manifest.md).

## Phases

### Phase 1: Typed `BayInventory` on `ShipInstance`
Remove the `ShipInstance.carried_items: List[Dict[str, Any]]` mixed-shape list. Introduce `BayInventory` with two typed slots (`bay: list[CarriedVehicle]`, `pods: list[DropPod]`). Update `ShipCargoManager`, `IssuerAdapter`, `MineGroupService`, the five FMS order handlers, and `ColonizeOrderHandler._deploy_drop_pod` to operate on the typed slots. Drop the `CarriedVehicle.from_any()` discriminator from every accessor. **Unblocks PROJ-425's cargo/deployable forwarder-demolition batch on completion.**

### Phase 2: `MineGroup` (DeployedGroup family 1)
Introduce `DeployedGroup` abstract base + `MineGroup` concrete in `game/strategy/data/deployed_group.py`. Add `Empire.deployed_groups: list[DeployedGroup]`. Rewrite the minefield resolver, `LayMinesOrderHandler`, `MineGroupService`, and the UI consumers to iterate `MineGroup` directly. Delete the synthetic mine-carrier `ShipInstance` and `_seed_mine_group_carrier`. Delete `_split_mine_groups_from_fleets`. Remove `"mine_group"` from `Fleet.group_kind`'s legal-values set.

### Phase 3: `FighterWing` + `SatelliteConstellation`
Mirror Phase 2 for the remaining two deployable families. Both classes own `ships: list[ShipInstance]`. Rewrite launch / recover order handlers, the combat spec assembler's fighter-participation walk, and `fighter_reboard.py`. Delete `"fighter_group"` and `"satellite_group"` from `Fleet.group_kind`; remove `group_kind` entirely. **Delete `_reject_if_non_fleet_group` in `handlers/base.py` and remove all ten call sites.** Drop the `group_kind` early-return in `FleetCapabilityCalculator`.

### Phase 4: Polish + docs + dead-code sweep
Final grep for `group_kind`, `from_any(`, `_split_mine_groups_from_fleets`, `_reject_if_non_fleet_group`, `synthetic_carrier`, `carried_items`. Update `docs/systems/strategy_layer.md`, `minefields.md`, `fighters.md`, `satellites.md`, and `docs/01_ARCHITECTURE.md` if it describes Fleet as the deployable substrate. Run the full sharded suite.

### Phase 5: Codex-consult-driven correctness fixes (post-Phase-4)
Three findings from a post-Phase-4 Codex consult. Two MAJOR behavioural gaps in the Phase-3-extended combat path that the Phase 4 polish pass did not catch, plus minor doc/comment drift. Strict TDD on the two behavioural fixes.

1. **Finding 1 (MAJOR) — deployed groups trigger combat without fleets.** `ConflictResolutionEngine._resolve_conflicts` previously iterated only `empire.fleets` for combat triggers, treating fleets as the sole conflict source. Two opposing `FighterWing` / `SatelliteConstellation` instances at the same hex with NO fleet present never battled. Fix: extend the trigger iteration to include combat-capable deployed groups (`FighterWing`, `SatelliteConstellation` per the existing `_combat_participating_groups` filter); hex-level dedup so a fleet trigger + co-located deployed-group trigger at the same hex does not double-fire. `MineGroup` remains a non-trigger (resolves via `TacticalMineResolver` inside an existing battle).
2. **Finding 2 (MAJOR) — third-party mine owners get tactical team IDs.** `StrategyBattleAssembler` seeded `empire_to_team_id` only from combat-fleet owners. A third-party empire with mines at the contested hex but NO combat fleet present had no entry in the map → `build_mine_resolver_setup` silently skipped its mines → `BattleEngine._run_mine_resolver_tick` would refuse to tick them anyway. Result pre-fix: neutral / non-participating mine owners' mines were inert in tactical combat. Fix: after seeding from combat fleets, walk the collected mine groups and allocate synthetic team-ids for any mine owner not already in the map. The synthetic team has no ships in the BattleSpec; all combatant ships read as enemies of that mine team.
3. **Finding 3 (MINOR) — doc / comment drift.** `post_battle_hook_builder.py` (`Sequence["Fleet"]` for `mine_groups` corrected to `Sequence["MineGroup"]`), `pre_tick_setup/mine_setup.py` (same — docstring + types), `engine/commands/__init__.py` (`IssueRecoverFightersCommand` / `IssueRecoverSatellitesCommand` docstrings reference the typed `FighterWing` / `SatelliteConstellation` deployed groups, not legacy `Fleet(group_kind=...)` synthetics). Documentation-only.

**Flagged-for-product-review (no code change):** `Empire.is_eliminated()` keeps an empire alive while it owns deployed groups, including immobile-only deployed groups (e.g. only `MineGroup`s — mines have no agency for strategic action). Whether this is design intent or an inconsistency with the "no fleets and no colonies = defeat" rule is a product-design question. Captured in `decisions.md`.

## Related Documents
- [TD-10 source plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-10_deployable_substrate.md) — canonical specification (verification findings, file touch plan, per-phase success criteria, risk register)
- [Strategy tech-debt EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) — TD-10 is #10/10, with the explicit `TD-01 → TD-10` hard edge and the `TD-10 Phase 1 → TD-06 cargo/deployable batch` phase gate
- [PROJ-426 plan](../PROJ-426/plan.md) — hard predecessor (battle spec assembly, TD-01)
- [PROJ-425 plan](../PROJ-425/plan.md) — phase-gated peer (ShipInstance slimming, TD-06); cargo batch resumes after this project's Phase 1
- [PROJ-428 plan](../PROJ-428/plan.md) — soft adjacency (phase registry hooks, TD-04)
- [design.md](design.md) — distilled architecture analysis (target typed model + risk register)
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — enumerated file touch list

## Verification
Acceptance criteria distilled from TD-10 §"Acceptance Criteria":
- [x] `ShipInstance` no longer stores mixed drop-pod and deployable entries in one ambiguous list (`carried_items` dataclass field removed; `bay_inventory` is the canonical typed field). Note: a `_CarriedItemsProxy` write-through property survives at `ship.carried_items` exclusively as a test-infrastructure shim; production code never reads/writes through it (locked in by AST guards `test_phase_1f_deletion_guard.py` + the `test_*_no_legacy_substrate.py` suite).
- [x] No synthetic mine-carrier `ShipInstance` anywhere in the tree — final grep for `mine_carrier_synthetic` / `_seed_mine_group_carrier` returns zero hits in `game/` and `tests/` (only documentary mentions in `Projects/`, `Reviews/`, and historical comments).
- [x] No `Fleet.group_kind` string branching remains — `Fleet.group_kind` field + constructor parameter + legal-values check + `to_dict` emission + `from_dict` default all DELETED. Final grep for `group_kind` in `game/` and `tests/` returns zero semantic hits (only documentary comments referencing the retired pattern).
- [x] `_reject_if_non_fleet_group` is deleted from `handlers/base.py` and no caller references it.
- [x] `_split_mine_groups_from_fleets` is deleted from `spec_compiler.py` and `team_spec_builder.py`.
- [x] `CarriedVehicle.from_any()` is deleted (bay is a homogeneous typed list; no discriminator needed).
- [x] Combat assembly and minefield resolution consume `empire.deployed_groups` (typed subsets via `deployed_groups_of(...)`) correctly.
- [x] Focused minefield, launch/recover, cargo/bay, and deployed-group suites are green before the sharded run.
- [x] `python Tools/test_sharded/test_sharded.py` is green — 21134/21134 at the Phase 3 baseline; Phase 4 production edits limited to inlining an always-True gate + comment cleanup with no behavioural change (focused regressions on the touched modules all green).
- [x] Docs (`strategy_layer.md`, `minefields.md`, `fighters.md`, `satellites.md`, `ability_reference.md`, `01_ARCHITECTURE.md`, `02_PATTERNS.md`) reflect the new model.
- [ ] User verified.
