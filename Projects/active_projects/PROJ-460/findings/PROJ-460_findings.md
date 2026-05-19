# PROJ-460 Findings — Simulation clean-cut LOC extractions

Consolidated findings carried verbatim from `Projects/archived_projects/PROJ-447/findings/bucket_d_simulation_ai_research_engine_docs_scan.md` (the original 2026-05-18 supplemental bucket-D scan), with current status as of 2026-05-19 (after Codex r4 redesign closed PROJ-444..447 and respun the work into 12 job-oriented projects per `AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md`).

This project carries two findings:
- **F-D-028** — `battle_state.py` 832 LOC; extract serde into `battle_state_serde.py`. **Closes here in Phase 1.**
- **F-D-011 (partial)** — 13 simulation files over the 500 LOC ceiling. This project takes the **actionable slice** (battle_state.py via F-D-028, battle_controller.py spec-in extraction, replay_serialization.py split) and **explicitly defers** the other 10 files as next-touch entries per Codex r4 discipline rule.

---

## F-D-011 — Largest simulation files exceed the 500-LOC ceiling (cluster of 13)

- **Severity (original)**: medium
- **Category**: polish
- **File**: see table below
- **Symbol**: module-level
- **Source refactor**: cumulative
- **What survived (verbatim from original 2026-05-18 bucket-D scan)**: 13 simulation-layer files exceed the 500-LOC ceiling:
  - `game/simulation/battle_state.py` (832 LOC) — **in scope, Phase 1**
  - `game/simulation/battle_controller.py` (831 LOC) — **in scope, Phase 2**
  - `game/simulation/systems/battle_engine.py` (758 LOC) — OUT OF SCOPE (next-touch)
  - `game/simulation/battle_runner.py` (735 LOC) — OUT OF SCOPE (next-touch)
  - `game/simulation/replay/replay_serialization.py` (634 LOC) — **in scope, Phase 3**
  - `game/simulation/entities/ship.py` (607 LOC) — OUT OF SCOPE (next-touch)
  - `game/simulation/systems/tactical_mine_resolver.py` (597 LOC) — OUT OF SCOPE (next-touch)
  - `game/simulation/entities/stat_contributors/registry.py` (570 LOC) — OUT OF SCOPE (next-touch)
  - `game/simulation/entities/ship_stats.py` (559 LOC) — OUT OF SCOPE (next-touch)
  - `game/simulation/components/abilities/base.py` (535 LOC) — OUT OF SCOPE (next-touch)
  - `game/simulation/systems/battle_end_conditions.py` (532 LOC) — OUT OF SCOPE (next-touch)
  - `game/simulation/services/vehicle_design_service.py` (516 LOC) — OUT OF SCOPE (next-touch)
  - `game/simulation/combat/fleet_aura_manager.py` (515 LOC) — OUT OF SCOPE (next-touch)
- **Why it's a problem**: Same convention as Bucket C F-C-027 / F-C-028 / F-A-007 / F-A-008. The two worst offenders (`battle_state.py`, `battle_controller.py`) are nearly 70% over.
- **Suggested action (original)**: `battle_state.py` is a serialization + result-DTO module — extract `BattleState` / `ShipState` / `BattleResults` to-dict/from-dict into `battle_state_serde.py` (PROJ-372-style split, ~250 LOC drop). `battle_controller.py` is largely orchestration; extract the spec-in `start_from_spec` flow into a sibling. Same pattern at `replay_serialization.py` (split capture vs replay paths). Defer the rest to next-touch.
- **Effort (original)**: medium per file

### Status as of 2026-05-19
- **Disposition in this project: actionable slice closed via Phase 1+2+3. 10 next-touch files documented in `decisions.md` per Phase 4.**
- Codex r4 explicitly carved this finding into "actionable slice" + "next-touch ledger" to avoid the "structural omnibus" risk. PROJ-460 enforces that boundary.
- The 10 next-touch files remain F-D-011 residue. A future project may take any one of them when it's next touched for a behavior change; until then, they are documented but not addressed.
- **2026-05-19 LOC drift (Group 3 pre-execution review):** Re-measurement shows the three in-scope files have shrunk since the original 2026-05-18 scan: `battle_state.py` 832 → 715, `battle_controller.py` 831 → 682, `replay_serialization.py` 634 → 516. Cited symbol lines still resolve to the same offsets (the shrinkage came from elsewhere in each file), so plan.md's `:48 / :149 / :222 / :242 / :460 / :542 / :628` references are still accurate. The practical consequence is on Phase 3's spec/outcome split boundary: the originally-cited "line 407" is stale; the actual `def battle_outcome_to_dict(...)` boundary is now near line 540-542. Phase 3 Task 3.0 (added in this same review pass) re-derives the boundary before splitting. Phase 1's "drop battle_state.py to ~530-580 LOC" target is also re-derived from the 715 baseline to ~430-470 LOC.

---

## F-D-028 — `game/simulation/battle_state.py` carries no module-level provenance, but `BattleState`, `BattleResults`, `ShipState` cumulatively serialize the entire battle outcome surface in one 832-LOC file

- **Severity (original)**: medium
- **Category**: polish
- **File**: `game/simulation/battle_state.py:1` (file-level; 832 LOC at original 2026-05-18 scan)
- **Symbol**: module-level
- **Source refactor**: cumulative (predates PROJ-269 unified outcome / PROJ-436 typed substrates)
- **What survived**: The file is the largest in `game/simulation/` outside the systems. Contains the BattleState dataclass, ComponentState, ShipState, ProjectileState, BattleResults — five serialization-heavy dataclasses + matching to_dict/from_dict methods. Natural extraction targets per the `planet_serde.py` precedent (Bucket A F-A-006 / F-A-008).
- **Why it's a problem**: Sibling of F-D-011 (file-LOC ceiling) but flagged separately because the split target is clean — to_dict/from_dict logic is ~250-300 LOC and lives in 5 paired places.
- **Suggested action (original)**: Extract serialization to `battle_state_serde.py` (PROJ-372-style). Would drop battle_state.py to roughly 530-580 LOC, still over but tractable; next pass extracts the BattleResults dataclass to a sibling.
- **Effort (original)**: medium

### Status as of 2026-05-19
- **Disposition in this project: Phase 1 closes this finding.**
- **2026-05-19 LOC drift (Group 3 pre-execution review):** Re-measurement shows battle_state.py is now 715 LOC (was 832 at original drafting); cited symbol lines below still resolve correctly. The Phase 1 LOC target was re-derived from the 715 baseline to ~430-470 LOC (was "~530-580" from the now-stale 832 baseline).
- The 10 paired to_dict/from_dict methods are at:
  - `ComponentState.to_dict` (battle_state.py:48), `ComponentState.from_dict` (:59)
  - `ShipState.to_dict` (:149), `ShipState.from_dict` (:179)
  - `ProjectileState.to_dict` (:460), `ProjectileState.from_dict` (:482)
  - `BattleState.to_dict` (:628), `BattleState.from_dict` (:647)
  - `BattleResults.to_dict` (:787), `BattleResults.from_dict` (:805)
- Together these are ~250-300 LOC. Extracting them lands battle_state.py at the projected ~430-470 LOC (post-2026-05-19 re-derivation from the 715 baseline; the original "~530-580" target was based on the now-stale 832 baseline) — at or just under the 500 ceiling, depending on how the dataclass facade lines shake out. Matches Codex r4's "clean cut" definition (the cut is obvious and well-shaped, not a forced bad cut).
- Note: this is a multi-dataclass serde, unlike planet_serde.py which is single-class. The serde module ends up with 5 paired functions, OR with the classmethods remaining on the dataclasses but delegating to module-level functions. Decide in Phase 1.

---

## Open follow-up criteria (the 10 next-touch files)

Per Codex r4 discipline rule: these are NOT addressed in this project. They are documented in `decisions.md` Phase 4 entries (one line each) so that the next time any of these files is touched for a behavior change, the LOC residue is visible to the touching agent.

Each next-touch entry records:
- File path
- Current LOC (2026-05-19 baseline)
- "no clean cut identified in PROJ-460 scope; revisit on next touch"

A future agent may scaffold a separate "<file> LOC reduction" project for any one of these when they touch it. That is OUT of PROJ-460's scope.

The full list of next-touch files is in `decisions.md` after Phase 4 lands. Until then, see `plan.md` "Out of Scope" table.
