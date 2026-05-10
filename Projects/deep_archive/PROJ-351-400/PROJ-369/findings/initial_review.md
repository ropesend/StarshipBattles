# PROJ-369 Initial Review — Top 5 Surprises

> One-page report; surprises ranked by "shifted the plan shape."

## 1. PROJ-365 already did most of the per-tick descriptor work — but explicitly excluded the end-of-turn block

The review report frames PROJ-369 as continuing PROJ-259, but the actual mid-stage of the work was **PROJ-365** (active_projects/PROJ-365), which landed `DEFAULT_TICK_PHASE_LIST` (15 entries at `turn_phase_registry.py:174-297`) and replaced `_process_tick`'s 80-line imperative body with a 14-line descriptor iteration loop (`turn_engine.py:691-760`). PROJ-365's plan.md:42-49 explicitly out-of-scoped the end-of-turn block — the 6 calls at `turn_engine.py:587-620` "keep their imperative form for now."

**Plan implication:** PROJ-369 phase 1 is mechanically the same shape as PROJ-365 phase 2 (extract a descriptor list + golden test). The "unfinished work" the review describes is more accurately "PROJ-365 was scoped tightly; PROJ-369 finishes the descriptor migration AND tackles the lazy-init issue PROJ-365 deferred."

## 2. `_NullBattleResolver` is a band-aid that becomes deletable after Phase 3

`turn_engine.py:109-122` defines `_NullBattleResolver`, used at line 360 inside `conflict_engine`'s lazy property when both `battle_resolver` and `ai_factory` are None. It exists to mute combat construction during non-combat tests. After Phase 3's `TurnEngineConfig.create_default(ai_factory=...)`, the default battle_resolver is always `SimulationBattleResolver` (when `ai_factory` is provided) or explicitly `None` (when caller opted out). The Null shim's only purpose was lazy-fallback noise reduction; with eager construction it has no role. **Phase 3 deletes the symbol** — and `test_turn_engine_lazy_properties.py:18` imports it explicitly, so the test file needs an explicit migration too.

## 3. The 3 "non-injectable" engines (Quality / Atmosphere / Water) have function-local imports INSIDE `process_turn`

I expected these to be locally constructed at module top, lazy-init style. They're worse: the `from game.strategy.engine.quality_engine import QualityEngine` lines literally live INSIDE the `process_turn` method body (around lines 607, 612, 617). This is why `test_turn_engine_end_of_turn_order.py` resorts to `patch('game.strategy.engine.quality_engine.QualityEngine')` patching the source modules — there is no other seam.

**Plan implication:** Phase 2 of PROJ-369 not only adds protocols and config fields, it also rewrites the existing `test_turn_engine_end_of_turn_order.py` to use clean constructor injection, eliminating one of the tests' explicit "D-004 OBSERVATION" workarounds.

## 4. Two production call sites only — both in `game_session.py`

I expected to find scattered TurnEngine construction across screens, AI, and replay subsystems. Reality: only `game/strategy/engine/game_session.py:102` (init) and `:386` (from_dict). Both already pass exactly the same kwargs (`registries=`, `ai_factory=`, `event_bus=`, `race_registry=`). Phase 3's production migration is a 2-site mechanical edit; the test surface is where the work lives (≥35 test sites — re-grepped at task start — construct TurnEngine directly).

**Plan implication:** Phase 3 risk is concentrated in test migration, not production migration. The fixture at `tests/unit/strategy/turn_engine/conftest.py:24-26` is the single highest-leverage change — most test files indirect through it.

## 5. `interfaces/engines.py` is already 714 LOC and over the 500-LOC ceiling

Phase 2 adds 3 protocols (`IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine`), bringing the file to ~830 LOC. docs/03_CONVENTIONS.md §6 enforces 500 LOC for production files. Reading the file, it is interfaces-only — every entry is an `ABC` with one or two `@abstractmethod` decorators. There is no logic to split.

**Plan implication:** Decisions.md flags this for the user. Two options: (a) accept the overage as documented (interfaces-only file is exempt from the spirit of the rule), or (b) split into `engines_core.py` (movement/production/orders/combat — 8 protocols) + `engines_terraforming.py` (population/happiness/quality/atmosphere/water — 5 protocols). If the user prefers (b), Phase 2 absorbs a small additional refactor task. **Phase 2 task list flags this for explicit decision before code lands.**

---

## Quantified summary

- 13 sub-engines wired through 15 phases (15 tick + 6 end-of-turn = 21 timing buckets, but only 15 lazy properties — the 6 end-of-turn engines map to 5 lazy properties since `population_engine`/`organics_consumption_engine`/`happiness_engine` already exist; only Quality/Atmosphere/Water are missing)
- 18 sub-engines after Phase 2 adds 3 (15 + 3)
- Constructor: 20 kwargs → 8 kwargs (Phase 3, –60%)
- LOC removed from `turn_engine.py`: ~155 from lazy fallback bodies + ~14 from `_NullBattleResolver` + ~39 from `create_default_turn_engine` (if deleted) = **~210 LOC removed** from the 802-LOC file → target ~590 LOC, well under the 500-LOC ceiling after we factor that ~90 LOC of those removals are docstrings/blank lines
- Test files touched: 17 in `tests/unit/strategy/turn_engine/` + 5+ integration test files = ~22 files
- AST guard tests added: 4+ (Phase 3) + 3 (Phase 5 hardening) = 7 invariants encoded
