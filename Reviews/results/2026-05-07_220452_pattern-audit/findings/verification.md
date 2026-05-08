# Verification Report: Pattern Audit 2026-05-07

## Summary
- Critical claims reviewed: 4
- Confirmed: 2 | Disputed: 1 | Inconclusive: 1

---

## Individual Verification

### VER-001: GameSession calls `get_default_registry_provider()` — Registry DI Bypass

**Source Report:** `pattern_review_02.md`
**Finding ID:** PAT-02-001
**Claim:** "`GameSession._resolve_registries()` (line 176-190) calls `get_default_registry_provider()` at line 183 to resolve `GameRegistries`. Per Pattern #3, 'Simulation code must not call `get_default_registry_provider()`' — and per `docs/01_ARCHITECTURE.md`, 'Prefer constructor injection. Module-level defaults are for composition roots, decorators, convenience functions, and established leaf code.' GameSession is a strategy-layer class (not a composition root) and should receive registries via constructor injection or through its TurnEngineConfig."

**Source Code Reviewed:**
- `game/strategy/engine/game_session.py:60` — imports `get_default_registry_provider`
- `game/strategy/engine/game_session.py:175-190` — `_resolve_registries()` calls `get_default_registry_provider()` at line 183
- `game/strategy/engine/game_session.py:91` — called from `__init__`
- `game/strategy/engine/game_session.py:441` — called from `from_dict` (save/load path)

**Verification Result:** DISPUTED

**Evidence:**
Pattern #3 explicitly limits the prohibition to **simulation** code:
- `docs/02_PATTERNS.md` line 12: "Simulation code must not call `get_default_registry_provider()`; inject registries or use `Ship._registries` / a passed provider."
- `docs/02_PATTERNS.md` line 98: "Leaf factory access may use `get_default_registry_provider()` **outside simulation**."
- `docs/02_PATTERNS.md` line 104: "In UI code, use `get_default_registry_provider()` when needed."

GameSession lives in `game/strategy/engine/` — the **strategy** layer, not simulation. Strategy-layer code is explicitly permitted to use the global accessor per Pattern #3. Multiple docs (`docs/04_SERVICES.md`, `docs/systems/combat_simulation.md`) reinforce that the restriction is simulation-scoped.

GameSession is the top-level game state container; it constructs and owns all other strategy objects (Galaxy, Empires, TurnEngine). The `from_dict()` save/load path at line 441 also calls the same resolver — a save-loaded session has no upstream DI context, so self-resolution is the only practical option without a separate bootstrapping injector.

The finding's severity assessment that GameSession is "not a composition root" is incorrect — it creates the entire game state graph and serves the same role within the strategy layer that `app_bootstrap.py` serves at the application level.

**Severity Assessment:** Should be MINOR — the finding correctly observes the call exists but misapplies the simulation-scoped restriction to a strategy-layer class. Constructor injection would be a minor improvement, not a pattern violation.

**Notes:** If the project intends to extend the DI restriction to strategy-layer code, Pattern #3 should be updated to say so explicitly. As written, only simulation code is restricted.

---

### VER-002: Facade Bypass — `build_queue_screen.py` dual-dispatch with session fallback

**Source Report:** `pattern_hunter_cross_shard.md`
**Finding ID:** Cross-Shard Facade Integrity (CRITICAL #1)
**Claim:** "`build_queue_screen.py` and `empire_build_queue_window.py` bypass the facade with session fallback... Both screens hold `self.session` AND `self.facade`, with a dual-dispatch pattern: `if self.facade: self.facade.handle_command(cmd) else: self.session.handle_command(cmd)` ... The fallback is flagged as `# PROJ-208 Phase 3` — but the pattern doc is clear: UI must go through Facade; GameSession should never be touched directly."

**Source Code Reviewed:**
- `game/ui/screens/build_queue_screen.py:88-89` — `self.session = session` and `self.facade = facade`
- `game/ui/screens/build_queue_screen.py:425-429` — `if self.facade: self.facade.handle_command(cmd) else: self.session.handle_command(cmd)` + PROJ-208 comment
- `game/ui/screens/build_queue_screen.py:462-466` — same fallback for remove command
- `game/ui/screens/build_queue_screen.py:498-501` — same fallback for toggle-pause command
- `game/ui/screens/empire_build_queue_window.py:179-180` — `self._session = session` and `self._facade = facade`
- `game/ui/screens/empire_build_queue_window.py:422-426` — `if facade: facade.handle_command(cmd) else: session.handle_command(cmd)` + PROJ-208 comment

**Verification Result:** CONFIRMED

**Evidence:**
Three separate command-dispatch sites in `build_queue_screen.py` (lines 425-429, 462-466, 498-501) and one in `empire_build_queue_window.py` (lines 422-426) all branch on facade presence with a direct `session.handle_command(cmd)` fallback. Pattern #5 (Facade/Delegate) designates `StrategySessionFacade` as the "only UI-to-strategy entry point" and Pattern #6 (CQRS-lite) routes all writes through `facade.handle_command()`.

The `# PROJ-208 Phase 3` comments confirm this is acknowledged technical debt — the fallback exists because not all callers supply a facade (the `facade=` parameter has no default, but is passed as `None` in some test paths where `session=` is also `None`).

The fallback is not theoretical dead code: `build_queue_screen.py` line 507 reads `registries=self.session.registries` directly, bypassing the facade entirely for registry access (the facade doesn't expose registries per Pattern #3).

**Severity Assessment:** CRITICAL is justified. The dual-dispatch creates two divergent command paths (facade-present vs facade-absent). The facade is the sole CQRS write channel for UI code; any code that can reach `session.handle_command()` directly circumvents the entire CQRS-lite path and risks mutation-before-validation or double-dispatch bugs.

**Notes:** The root cause is session leakage from StrategyScreen (see VER-003). Fixing this requires removing `session=` from both screens' constructors, making `facade=` required, and eliminating the `else: session.handle_command(cmd)` branches. The `registries=self.session.registries` direct access at `build_queue_screen.py:507` should route through the facade or the `galaxy` reference that is already available.

---

### VER-003: StrategyScreen exposes `self.session` to child screens, enabling facade bypass

**Source Report:** `pattern_hunter_cross_shard.md`
**Finding ID:** Cross-Shard Facade Integrity (CRITICAL #2)
**Claim:** "`StrategyScreen.__init__` directly constructs `GameSession` without facade mediation... The screen holds `self.session` (line 83) and passes it to downstream screens (BuildQueueScreen line 88, EmpireBuildQueueWindow line 163), which creates the session-bypass chains documented above. The screen should only expose `self._facade` and inject facade — not session — into child screens."

**Source Code Reviewed:**
- `game/ui/screens/strategy_screen.py:78-83` — `self.session = GameSession(ai_factory=AIControllerFactory())` with public `self.session`
- `game/ui/screens/strategy_screen.py:86` — `self._facade = StrategySessionFacade(self.session)` (private)
- `game/ui/screens/strategy_screen.py:155-182` — public properties reading from `self.session` (galaxy, empires, systems, active_empire, enemy_empire, human_player_ids)
- `game/ui/screens/strategy_build_queue_manager.py:98` — passes `session=self._screen.session` to `BuildQueueScreen`
- `game/ui/screens/strategy_windows/build_queue_windows.py:73-74` — passes `session=c.scene.session` and `facade=c.scene.facade` to `EmpireBuildQueueWindow`

**Verification Result:** CONFIRMED (with nuance)

**Evidence:**
The claim bundles two distinct sub-claims:

1. **Direct GameSession construction**: `strategy_screen.py:81-83` constructs `GameSession(ai_factory=AIControllerFactory())`. This is a valid composition root action — StrategyScreen sits at the UI/composition layer where constructing domain objects is architecturally expected. `app_bootstrap.py` (the primary composition root) doesn't create a session because sessions are per-game, not per-launch. `StrategyScreen` is the right place to create one. This sub-claim is not itself a violation.

2. **Session propagation to child screens**: `self.session` is a **public** attribute (vs `self._facade` which is private). It is passed directly to `BuildQueueScreen` (`session=self._screen.session` at `strategy_build_queue_manager.py:98`) and `EmpireBuildQueueWindow` (`session=c.scene.session` at `build_queue_windows.py:73`). Both child screens also receive `facade=`, giving them two command-dispatch paths — the precise mechanism that enables the facade bypass confirmed in VER-002. This sub-claim is the genuine CRITICAL violation.

The asymmetry is telling: `_facade` is private (`self._facade`) but accessed externally as `c.scene.facade` through the composition object; `session` is fully public. If session were made private and child screens received only facade, the VER-002 bypass would be impossible.

**Severity Assessment:** CRITICAL is justified for the session-propagation sub-claim. The public `self.session` is the root cause of two facade-bypass screens. Making it private and removing session from child-screen constructors would eliminate the bypass at its source.

**Notes:** The public properties at lines 155-182 (e.g., `galaxy`, `empires`) that delegate to `self.session` are convenience read-accessors within StrategyScreen, not violations per se. But they should delegate through the facade if the facade exposes equivalent DTO reads. The real fix is: (a) remove `session=` from `BuildQueueScreen` and `EmpireBuildQueueWindow` constructors, (b) make `facade=` required in both, (c) remove the `else: session.handle_command(cmd)` fallback branches, (d) optionally make `self.session` private.

---

### VER-004: (Claim conflated into VER-002 + VER-003 above — no separate finding)

The cross-shard report lists two CRITICAL items under "Facade Integrity" plus two more in "Prioritized Architectural Recommendations." The two CRITICAL items have been verified as VER-002 and VER-003. The recommendations section (items #1-2) restates the same issues for action tracking and does not introduce new claims.

---

## CRITICAL Severity Reassessment

| VER | Original Severity | Verified Severity | Rationale |
|-----|-------------------|-------------------|-----------|
| VER-001 (PAT-02-001) | CRITICAL | **MINOR** | Strategy-layer code is explicitly permitted to call `get_default_registry_provider()` per Pattern #3. Only simulation-layer code is restricted. Single call site, trivial to fix if desired. |
| VER-002 (Facade bypass — dual dispatch) | CRITICAL | **CRITICAL** | Three fallback sites in build_queue_screen.py + one in empire_build_queue_window.py directly circumvent the single UI-to-strategy write channel. PROJ-208 comments confirm acknowledged debt. |
| VER-003 (Session leakage from StrategyScreen) | CRITICAL | **CRITICAL** | Public `self.session` propagated to child screens is the root cause of VER-002. Making session private and facade required would eliminate the bypass chain. |

---

## Verification Methodology

Each CRITICAL finding was verified by:
1. Reading the citing source files in full (init methods, dispatch methods, call sites)
2. Cross-referencing against the pattern documentation (Patterns #3, #5, #6)
3. Tracing data flow: where `session` originates, how it reaches child screens, which fallback branches exist
4. Comparing the finding's characterization against the documented pattern scopes

All file paths and line numbers were confirmed accurate against the current working tree.
