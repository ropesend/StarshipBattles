# Phase 5: Reduce `spec_compiler.py` to a thin public facade and update docs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-426 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_4
**Review Mode:** standard
**Files (planned):**
- `game/strategy/combat/spec_compiler.py` (edit — reduce to thin facade, target `<= 120 LOC`)
- `docs/systems/strategy_layer.md` (edit)
- `docs/01_ARCHITECTURE.md` (edit)
- `docs/02_PATTERNS.md` (edit)

**Objective:** Finish the maintainability payoff without breaking imports. `spec_compiler.py` becomes orchestration only: instantiate `StrategyBattleAssembler`, call `assemble`, return `assembly.spec`. Public import path is preserved. Docs sync to describe the assembler pipeline rather than spec mutation. Final sharded run + `--testmon` run.

---

## Reading

- [ ] Re-read [TD-01 source plan §"Phase 5"](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-01_battle_spec_compilation.md).
- [ ] `git ls-files game/strategy/combat/` and `wc -l game/strategy/combat/*.py` — confirm no file is > 500 LOC post-extraction.
- [ ] Identify any doc text that still describes `spec._mine_groups` / side-channels / "spec compiler builds setup callbacks". Grep:
  ```bash
  rg "_mine_groups|_owner_to_team_id|_combat_fleets|_engine_ref|object\.__setattr__\(spec" docs
  ```

---

## Tasks

### Task 5.1: Reduce `spec_compiler.py` to thin facade [Medium]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/ tests/unit/strategy/adapters/test_simulation_adapter.py -x`

- [ ] Body of `build_strategy_battle_spec(...)` becomes orchestration only: instantiate `StrategyBattleAssembler`, call `assemble`, and `return assembly.spec`.
- [ ] Optionally re-export `build_strategy_battle_assembly(...)` for callers that want the full assembly.
- [ ] Remove now-dead imports.
- [ ] Remove stale module-doc text that still describes side-channels or embedded setup builders.
- [ ] `wc -l game/strategy/combat/spec_compiler.py` should report `<= 120` LOC.
- [ ] Run focused suite; confirm green.

**Notes:**

### Task 5.2: Confirm no `game/strategy/combat/` file exceeds 500 LOC [Simple]
**File:** N/A
**Tests:** N/A

- [ ] `wc -l game/strategy/combat/*.py game/strategy/combat/pre_tick_setup/*.py`.
- [ ] Every file `<= 500` LOC per AGENTS.md production-file ceiling.
- [ ] If any file is over, split by responsibility before continuing.

**Notes:**

### Task 5.3: Docs sync [Medium]
**File:** `docs/systems/strategy_layer.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`
**Tests:** N/A (docs)

- [ ] Update `docs/systems/strategy_layer.md` to describe the assembly pipeline (`build_strategy_battle_spec` → `StrategyBattleAssembler.assemble` → `StrategyBattleAssembly{spec, extensions, pre_tick_setup}`) rather than spec mutation.
- [ ] Update `docs/01_ARCHITECTURE.md` to reflect the strategy-to-simulation boundary now being the typed `StrategyBattleAssembly` (extensions live in strategy, `BattleSpec` stays frozen in simulation).
- [ ] Update `docs/02_PATTERNS.md` with the typed-sidecar-extensions pattern and the named-setup-registry pattern. Remove any prior description of `object.__setattr__` on frozen DTOs as an accepted pattern.
- [ ] Skip `docs/_ignore/` per AGENTS.md.

**Notes:**

### Task 5.4: Final validation gates [Complex]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py` + `pytest tests/ --testmon`

- [ ] Run `python Tools/test_sharded/test_sharded.py`; confirm green.
- [ ] Run `pytest tests/ --testmon`; confirm green.
- [ ] Final grep gates:
  - `rg "object\.__setattr__\(spec" game tests` → zero hits.
  - `rg "getattr\(spec, ['\"]_" game tests` → zero hits.
  - `rg "_mine_groups|_owner_to_team_id|_combat_fleets|_engine_ref" docs` → zero hits in non-historical text.

**Notes:**

### Task 5.5: Commit Phase 5 [Simple]
**File:** N/A
**Tests:** N/A

- [ ] `git status --short` confirms only Phase 5 files dirty.
- [ ] Commit: `PROJ-426 phase 5: reduce spec_compiler.py to thin facade + docs sync`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All Phase 5 task checkboxes checked.
- [ ] `game/strategy/combat/spec_compiler.py` `<= 120 LOC` and is orchestration only.
- [ ] No `game/strategy/combat/` file exceeds 500 LOC.
- [ ] `docs/systems/strategy_layer.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md` describe the assembler pipeline.
- [ ] Full sharded suite green; `--testmon` green.
- [ ] All final grep gates pass.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to indicate project ready for final audit.
