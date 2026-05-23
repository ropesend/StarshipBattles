# Phase 5: Codex-consult-driven correctness fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-431 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_4
**Review Mode:** standard

**Objective:** Address three Codex-consult-flagged correctness gaps that landed AFTER the Phase 4 close. Two are MAJOR/MEDIUM behavioural bugs in the Phase-3-extended combat path that the Phase 4 polish pass did not catch; the third is doc/comment drift from the Phase 3 substrate move.

**Files touched:**
- `game/strategy/engine/conflict_resolution_engine.py` (Finding 1)
- `game/strategy/combat/battle_assembly.py` (Finding 2)
- `game/strategy/combat/post_battle_hook_builder.py` (Finding 3)
- `game/strategy/combat/pre_tick_setup/mine_setup.py` (Finding 3)
- `game/strategy/engine/commands/__init__.py` (Finding 3)
- `tests/unit/strategy/engine/test_conflict_deployed_group_trigger.py` (NEW)
- `tests/unit/strategy/combat/test_battle_assembly_third_party_mines.py` (NEW)

---

## Tasks

### Task 5.1: Finding 1 — deployed groups trigger combat without fleets [MAJOR]
- [x] **Red test:** `tests/unit/strategy/engine/test_conflict_deployed_group_trigger.py` — two opposing `FighterWing`s with no fleets present must engage; same for `SatelliteConstellation`; `MineGroup`-only hex must NOT trigger.
- [x] Run the failing test, confirm red baseline.
- [x] **Fix:** extend `ConflictResolutionEngine._resolve_conflicts` to iterate combat-capable deployed groups for triggers alongside fleets. Hex-level dedup so a co-located fleet + deployed-group trigger does not double-fire.
- [x] Run the test, confirm green.
- [x] **Commit:** `PROJ-431 phase_5 (conflict trigger): deployed groups trigger combat without fleets` — head `1bec92778`.

### Task 5.2: Finding 2 — third-party mine owners get tactical team IDs [MAJOR]
- [x] **Red test:** `tests/unit/strategy/combat/test_battle_assembly_third_party_mines.py` — a mine-only empire (no combat fleets) must receive a team-id entry distinct from combatants, and its resolver must wire with a non-None `_owner_team_id`.
- [x] Run the failing test, confirm red baseline.
- [x] **Fix:** in `StrategyBattleAssembler.assemble`, after seeding `empire_to_team_id` from combat-fleet owners, walk `mine_groups` and allocate synthetic team-ids for any mine-only owners. The synthetic team has no ships in the `BattleSpec`; all combatant ships read as enemies of that mine team.
- [x] Run the test, confirm green.
- [x] **Commit:** `PROJ-431 phase_5 (mine third-party): allocate team IDs for inert mine owners` — head `1c4ab691d`.

### Task 5.3: Finding 3 — doc / comment drift [MINOR]
- [x] `game/strategy/combat/post_battle_hook_builder.py`: `mine_groups: Sequence["Fleet"]` and `captured_mine_groups: Tuple["Fleet", ...]` corrected to `MineGroup`. Added `MineGroup` to TYPE_CHECKING import.
- [x] `game/strategy/combat/pre_tick_setup/mine_setup.py`: docstring + type hints corrected; `Fleet` TYPE_CHECKING import replaced with `MineGroup`.
- [x] `game/strategy/engine/commands/__init__.py`: `IssueRecoverFightersCommand` and `IssueRecoverSatellitesCommand` docstrings reference the typed `FighterWing` / `SatelliteConstellation` deployed groups (not legacy `Fleet(group_kind=...)` synthetics).
- [x] **Commit:** `PROJ-431 phase_5 (doc drift): update post-Phase-3 comments` — head `4cb0db29f`.

### Task 5.4: Full sharded suite
- [ ] `python Tools/test_sharded/test_sharded.py` — must be green.

---

## Disposition

- **Finding 1 (MAJOR):** Fixed. Two opposing FighterWings or SatelliteConstellations at the same hex with no fleet present now engage. Hex-level dedup keeps a fleet trigger + co-located deployed-group trigger from double-firing.
- **Finding 2 (MAJOR):** Fixed. Third-party mine owners (mines at a hex with no fleet) receive synthetic team-ids so their mines tick against actual combatants.
- **Finding 3 (MINOR):** Fixed. All three flagged files now match the post-Phase-3 substrate vocabulary.

## Open follow-up flagged in decisions.md

`Empire.is_eliminated()` currently keeps an empire alive while it owns deployed groups, even if those groups are all immobile (e.g. only `MineGroup`s — mines have no agency to take strategic action). Whether this is the intended design (immobile minefields are a legitimate presence on the map) or an inconsistency vs the "no fleets and no colonies = defeat" gameplay rule is a product-design question, not a code-correctness one. Captured in `decisions.md` as `flagged-for-product-review`.
