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
| 1. Typed `BayInventory` on `ShipInstance` | In Progress (sub-phase 1a complete) | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. `MineGroup` extraction (DeployedGroup family 1) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `FighterWing` + `SatelliteConstellation` (families 2 & 3) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Polish + docs + dead-code sweep | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** Phase 1 (in progress — sub-phases 1a + 1b complete)
**Last Action:** Sub-phase 1b complete. `minefield_resolver.py`, `MineGroupService` (`game/strategy/services/mine_group_service.py`), and `FleetShipIssuerAdapter` in `game/strategy/engine/issuer_adapter.py` migrated off `carried_items` / `CarriedVehicle.from_any()`. Reads now route through `ship.bay_inventory`; writes use `ship.set_bay_inventory(...)`. Mine consumption in the resolver was reworked to consume by index within a single fetched mine list (the previous identity-match-then-re-fetch pattern relied on a shared mutable list reference that no longer exists once `_iter_mines` returns a dict projection of the typed bay). Added AST regression guard at `tests/unit/strategy/engine/test_minefield_resolver_no_legacy_substrate.py` (smoke import + 2 RED→GREEN AST checks). FMS handler test stubs (`test_lay_mines_handler.py`, `test_launch_fighters_handler.py`, `test_launch_satellites_handler.py`) gained a `bay_inventory` / `set_bay_inventory` view-over-`carried_items` so the now-migrated `IssuerAdapter` works against them without migrating the handlers themselves (1c scope). All 4754 strategy unit tests pass. The planet-staging-yard branch of `IssuerAdapter` is intentionally left on the legacy substrate (out of scope for 1b).
**Next Action:** Sub-phase 1c — migrate FMS order handlers: `lay_mines.py`, `launch_fighters.py`, `launch_satellites.py`, `recover_fighters.py`, `recover_satellites.py`.
**Blockers:** None. Phase 1 still requires sub-phases 1c–1f and the final delete-substrate commit per decisions.md.

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
- [ ] `ShipInstance` no longer stores mixed drop-pod and deployable entries in one ambiguous list (`carried_items` field removed; `bay_inventory` field present).
- [ ] No synthetic mine-carrier `ShipInstance` anywhere in the tree — final grep for `mine_carrier_synthetic` and `_seed_mine_group_carrier` returns zero hits.
- [ ] No `Fleet.group_kind` string branching remains — final grep for `group_kind` returns zero semantic hits.
- [ ] `_reject_if_non_fleet_group` is deleted from `handlers/base.py` and no caller references it.
- [ ] `_split_mine_groups_from_fleets` is deleted from `spec_compiler.py`.
- [ ] `CarriedVehicle.from_any()` is deleted (bay is a homogeneous typed list; no discriminator needed).
- [ ] Combat assembly and minefield resolution consume `empire.deployed_groups` (typed subsets) correctly.
- [ ] Focused minefield, launch/recover, cargo/bay, and deployed-group suites are green before the sharded run.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
- [ ] Docs (`strategy_layer.md`, `minefields.md`, `fighters.md`, `satellites.md`, `01_ARCHITECTURE.md` if applicable) reflect the new model.
- [ ] User verified.
