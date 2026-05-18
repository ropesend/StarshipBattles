# Phase 0: Preflight and contract freeze

**Status:** Complete
**Depends on:** none
**Review Mode:** lightweight
**Files (planned):** (none — baseline grep + behavioral inventory only)
**Objective:** Capture the external API and current semantics before extracting internals. Produce a current call-site inventory and explicitly record the behaviors this refactor must preserve.

---

## Tasks

### Task 0.1: Run the guardrail `rg` baselines [Simple]

- [x] `rg -n "GameSession\(|GameSession\.from_dict\(|SessionBootstrap|SessionPersistenceAdapter|SessionRuntimeServices" game tests docs`
- [x] `rg -n "fleet_mutator|planet_mutator|empire_mutator|ship_mutator|TurnEngineConfig\.create_default|create_default_registry|GameInitializer\.initialize" game/strategy/engine/game_session.py`
- [x] Save both outputs into `findings/` for reference at every phase boundary.

### Task 0.2: Confirm production callers still use the public API [Simple]

- [x] From the first `rg` output, scan production call sites under `game/`.
- [x] Confirm every production caller still uses `GameSession(...)` or `GameSession.from_dict(...)` directly (no new factories already exist).

### Task 0.3: Record behaviors to preserve [Simple]

- [x] Note the current `human_player_ids` load fallback: `__init__` (line 188-190) derives `[i for i, p in enumerate(config.players) if p.is_human]`; `from_dict` (line 563) falls back to `[0, 1]`. This semantic asymmetry is preserved by this refactor.
- [x] Note the current `race_registry` laziness: `_race_registry = None` on construction, populated on first access. Preserved.
- [x] Note the current `SessionInitializationError` null-object substitution exists in `__init__` only; `from_dict` has no parallel safety net. Preserved.

---

## Exit criteria

- [x] Baseline `rg` outputs captured in `findings/`.
- [x] Call-site inventory confirms public API stability is realistic.
- [x] Behaviors-to-preserve list recorded (either in `decisions.md` under a Phase 0 entry, or in `findings/`).
