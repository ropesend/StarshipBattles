# PROJ-382 Pattern Conformance Review — Final Report

**Review Type:** code (delegated by Claude Code)
**Request ID:** req_20260508_235748_8c0ea0
**Review Directory:** Reviews/results/2026-05-08_235750_code_proj-382-pattern-conformance-facade-integrity-even_req-req_20260508_235748_8c0ea0/
**Completed:** 2026-05-08T23:59:00Z
**Review Mode:** normal (5-agent parallel swarm)
**Scope:** 30+ files across 5 phases, 7 commits on `feat/03c-phase-aware-execution` (2b22b5e8b → d605157aa)
**Limitations:** No validation pass executed (normal compile mode). Cross-cutting agent found one out-of-narrow-scope finding (FIND-001 — save/load mutator gap) that predates PROJ-382 but is triggered by Phase 3 proximity to game_session.py.

---

## Verification Summary

| Focus Area | Instruction # | Verdict |
|---|---|---|
| Static-guard genuinely closes Pattern #5 escape routes | 1 | **Partial** — catches `.session.handle_command(...)` but misses `._session.handle_command(...)` and cannot detect non-dispatch session reads |
| `portrait_session=` kwarg — legitimate narrow handle or backdoor? | 2 | **Backdoor** — full GameSession renamed, only needs `empire_theme_id: str` |
| EventBus→WorkshopEventBus rename completeness | 3 | **Complete** — all 16 files updated, zero missed imports |
| `registries=` required kwarg on ProductionSpawner | 4 | **Complete** — Python-level required, all 26+ call sites compliant, eager injection safe |
| Phase 5 splits — real decomposition vs cosmetic | 5 | **Real decomposition** — all 4 splits are semantically cohesive; planetary decomposition is genuine but has cleanup issues |
| Deferred Task 5.4 — honest rationale? | 6 | **Weak rationale** — same explicit-parameter pattern used everywhere else in Phase 5 would work; not an architectural block |
| Pattern #36 documentation quality + facade-bypass guard | 7 | **MAJOR gap** — "when not to use" missing explicit Pattern #5 facade-bypass prohibition |
| PROJ-381 cross-impact on game_session.py | 8 | **No conflict** — tautology guard removal and null-object init are independent code sections |

---

## Aggregate Findings

| Severity | Count |
|---|---|
| CRITICAL | 2 |
| MAJOR | 9 |
| MINOR | 14 |
| INFO | 24 |
| **Total** | **49** |

---

## CRITICAL Findings

### CRIT-001: Static guard has syntactic blind spot for `._session.handle_command(...)`

**File:** `tests/static_guards/test_facade_bypass_guard.py:58-68`
**Agent:** agent_facade_bypass_report.md — FINDING-01

The guard matches attribute name `"session"` exactly. After Phase 1 privatized `self.session` → `self._session`, code inside `strategy_screen.py` (or any file with a reference) could call `screen._session.handle_command(...)` and the guard would **decline to fire**. The fix is trivial: extend `_is_session_handle_command` to match both `"session"` and `"_session"`.

**Recommendation:** Add `"_session"` to the attribute name check in the AST guard. Add a targeted check for `self._session.handle_command(...)` within `strategy_screen.py` specifically.

---

### CRIT-002: GameSession.from_dict() does not restore mutator services

**File:** `game/strategy/engine/game_session.py:475-490`
**Agent:** agent_crosscutting_sweep_report.md — FIND-001

`from_dict()` constructs `TurnEngineConfig.create_default()` without passing `fleet_mutator`, `planet_mutator`, `empire_mutator`, or `ship_mutator`. The private mutator fields are never assigned in `from_dict()`. Any command handler that calls `session.fleet_mutator.set_path()` (via `add_move_order_if_needed`) after deserialization will raise `AttributeError`. This is a Pattern #2 (Protocol + TypeGuard) boundary violation — the session should function identically whether constructed or deserialized.

**Recommendation:** Add mutator service construction in `from_dict()` mirroring `__init__` lines 104-123, and pass them to `TurnEngineConfig.create_default()`.

---

## MAJOR Findings

### MAJ-001: `session` property setter allows reassignment without facade rebuild

**File:** `game/ui/screens/strategy_screen.py:231-234`
**Agent:** agent_facade_bypass_report.md — FINDING-02

The setter updates `self._session` but does not rebuild `self._facade`. After `screen.session = new_session`, the facade dispatches through the old session (split-brain) while the screen's other properties read from the new one. The setter is documented as "test session swap" but has no guardrail.

### MAJ-002: `portrait_session=` kwarg is a renamed full-session backdoor

**File:** `game/ui/screens/build_queue_screen.py:62,96,121` → `game/ui/panels/build_queue_portraits.py:77-86`
**Agent:** agent_facade_bypass_report.md — FINDING-03

The actual data needed is `empire_theme_id` (a single string). Instead, the entire `GameSession` is passed, renamed `portrait_session` at the call site but stored as `self.session` inside `BuildQueuePortraitLoader`. The static guard misses this because: (a) the kwarg is named `portrait_session`, not `session`, and (b) the loader accesses `session.active_empire.empire_theme_id`, not `session.handle_command(...)`.

### MAJ-003: BuildQueuePanelFactory receives raw session and bypasses facade for registries, empire, turn

**File:** `game/ui/screens/build_queue_panel_factory.py:96,121,233,543,556`
**Agent:** agent_facade_bypass_report.md — FINDING-04

Three distinct read paths bypass the facade: `self.session.registries`, `self.session.current_empire`, `self.session.turn`. The factory receives both `session` and `facade` parameters but uses session directly for all three.

### MAJ-004: StrategyBuildQueueManager accesses session for domain data through screen property

**File:** `game/ui/screens/strategy_build_queue_manager.py:111,129,148,155,255,279`
**Agent:** agent_facade_bypass_report.md — FINDING-05

Five access sites through `self._screen.session` extract `save_path`, `galaxy`, and forward the full session as `portrait_session`. These read-accesses bypass the facade's query surface.

### MAJ-005: Deferral rationale for superweapon_order_processor.py is weak

**File:** `game/strategy/engine/superweapon_order_processor.py:1-723` (223 over ceiling)
**Agent:** agent_loc_splits_report.md — FINDING-08

The stated rationale ("extracting closures requires a state-bag type") does not withstand scrutiny. The same explicit-parameter pattern was successfully used by all other Phase 5 splits (battle_setup.py, boundary_enforcement.py, attack_processor.py). The 5 process methods close over `self` — not engine state — and can be extracted as free functions receiving the processor as an explicit parameter. This is a mechanical extraction, not an architectural deferral.

### MAJ-006: Pattern #36 "when not to use" missing Pattern #5 facade-bypass prohibition

**File:** `docs/02_PATTERNS.md:761-769`
**Agent:** agent_docs_crossimpact_report.md — DOC-01-P36

The section lists three prohibitions but none mention Facade bypass. PROJ-382 Phase 1 specifically eradicated facade-bypass violations; without an explicit cross-reference in Pattern #36, the re-export shim pattern could be cited as justification for reintroducing facade-bypass through a differently-named shim.

### MAJ-007: Dead `_STORM_SCOPES` duplicate in planetary shields.py

**File:** `game/simulation/components/abilities/planetary/shields.py:139-144`
**Agent:** agent_loc_splits_report.md — FINDING-02

Untreated split artifact from the original 913-LOC `planetary.py`. The canonical copy lives in `_shared.py:12-17`. The duplicate is never referenced by `PlanetaryShieldAbility` or `RadiationShieldAbility`.

### MAJ-008: planet_command_handlers.py uses legacy BaseCommandHandler import

**File:** `game/strategy/engine/planet_command_handlers.py:55,127,149,185`
**Agent:** agent_crosscutting_sweep_report.md — FIND-002

Four late-import sites use the legacy shim path instead of the canonical `game.strategy.engine.handlers.base`. This is a Pattern #7 violation — `superweapon_command_handlers.py` was properly migrated but its sibling was left behind.

### MAJ-009: 3 test files import BaseCommandHandler from legacy shim path

**File:** `tests/unit/strategy/test_command_handlers.py`, `tests/unit/strategy/engine/test_command_ownership.py`, `tests/unit/strategy/engine/test_base_command_handler.py`
**Agent:** agent_crosscutting_sweep_report.md — FIND-003

Pattern #7 violation. Tests should exercise the canonical import path to catch regressions when the shim is retired.

---

## MINOR Findings (representative selection)

14 minor findings across all 5 agent reports. Key items:

- MIN-001: `session` property on StrategyScreen is an "audit-residue delegate" masking true access patterns (`agent_facade_bypass_report.md` — FINDING-06)
- MIN-002: `BuildQueuePortraitLoader` stores session under public attribute `self.session` (`agent_facade_bypass_report.md` — FINDING-07)
- MIN-003: Dead `if self._registries:` guard in `_spawn_to_staging_yard` (`agent_eventbus_spawner_report.md` — FINDING-07)
- MIN-004: `_get_planet_mutator()` thin wrapper retained post-eager conversion (`agent_eventbus_spawner_report.md` — FINDING-06)
- MIN-005: ProductionEngine doesn't thread `planet_mutator` to ProductionSpawner (`agent_eventbus_spawner_report.md` — FINDING-08)
- MIN-006: Dead UI color imports in 6 planetary sub-modules (`agent_loc_splits_report.md` — FINDING-03)
- MIN-007: Misplaced `logger` assignment in battle_engine.py (`agent_loc_splits_report.md` — FINDING-09)
- MIN-008: `_shared.py` naming overly generic for single-constant module (`agent_loc_splits_report.md` — FINDING-10)
- MIN-009: Pattern #36 structure diverges from neighboring templates (`agent_docs_crossimpact_report.md` — DOC-02-P36)
- MIN-010: Two shim sites lack retirement migration projects (`agent_docs_crossimpact_report.md` — DOC-03-P36)
- MIN-011: `from_dict` has no null-object recovery equivalent (`agent_docs_crossimpact_report.md` — CROSS-02-GS)
- MIN-012: design_selector_window.py hardcoded ship class/vehicle type lists (`agent_crosscutting_sweep_report.md` — FIND-004)
- MIN-013: `_SUPERWEAPON_LABELS` mapping duplicates registry knowledge (`agent_crosscutting_sweep_report.md` — FIND-005)
- MIN-014: design_selector_window test doesn't thread window_manager= kwarg (`agent_crosscutting_sweep_report.md` — FIND-006)

---

## INFO Findings (notable confirmations)

24 info-level findings confirming correct implementation:

- `get_registries()` on StrategySessionFacade is canonical and correct
- EventBus → WorkshopEventBus rename is complete across all 16 files
- `registries=` required kwarg enforced at 2 levels, all 26+ call sites compliant
- All 4 LOC splits (battle_engine, fleet_navigation, conflict_resolution, planetary) are semantically cohesive
- Pattern #23 lists 6 phases correctly (doc drift already fixed or never present)
- Pattern #7 canonical path and shim reference are accurate
- Pattern #12 third variant properly documented with justification
- PROJ-381 tautology guard removal and null-object init are independent — no conflict
- All three bare `json` imports pass audit legitimacy check (exception type only, or non-persistence `json.dumps`)
- Pattern #2 TypeGuard in galaxy_spatial_index.py correctly implemented
- Pattern #10 dual-path event logging correctly collapsed in empire.py/fleet.py
- EventBus injection in projectile.py follows Pattern #10 with lazy-default fallback
- superweapon_command_handlers.py uses canonical BaseCommandHandler import path
- simulation/components/__init__.py is intentionally empty (namespace marker) — no pattern violations
- stat_rows_dynamic.py correctly derives superweapon names from registry
- design_selector_window.py correctly subclasses StrategyModalWindow
- TurnEngine correctly publics turn_number/save_path in EnginePhaseError context

---

## Deferred During Implementation

**Task 5.4 (superweapon_order_processor.py, 723 LOC):** Deferral rationale is WEAK (see MAJ-005). The same explicit-parameter extraction pattern used for battle_setup.py, boundary_enforcement.py, and attack_processor.py also works here. Schedule for next LOC sweep.

---

## Detailed Agent Reports

- `findings/agent_facade_bypass_report.md` — 9 findings (Facade bypass + PortraitLoader)
- `findings/agent_eventbus_spawner_report.md` — 8 findings (EventBus rename + production_spawner)
- `findings/agent_loc_splits_report.md` — 10 findings (Phase 5 splits + deferred task)
- `findings/agent_docs_crossimpact_report.md` — 11 findings (Pattern docs + PROJ-381 cross-impact)
- `findings/agent_crosscutting_sweep_report.md` — 11 findings (Cross-cutting sweep)
