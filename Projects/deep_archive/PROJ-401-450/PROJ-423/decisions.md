# PROJ-423 Decisions Log

Project-local decisions made during the GameSession lifecycle extraction. See [`design.md`](design.md) for the verified findings and target shape, and the source plan [`TD-02_game_session_lifecycle.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-02_game_session_lifecycle.md) for the canonical specification.

## 2026-05-16 — Project scaffolded

Source: [`TD-02_game_session_lifecycle.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-02_game_session_lifecycle.md). Execution rank 2 of 10 in [`EXECUTION_ORDER.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md).

The decisions below are pre-committed by the source plan; they are recorded here so phase workers can find them without re-reading the source. Implementation-time decisions get appended as new entries.

## Pre-committed design decisions

| Decision | Rationale |
|----------|-----------|
| `race_registry` stays **outside** `SessionRuntimeServices` and remains lazy on `GameSession`. | It is not part of the `__init__` / `from_dict` drift problem. Changing its lifetime would introduce unnecessary behavior risk in a refactor whose value is structural. Source plan, "Required collaborators" section. |
| The save schema is **unchanged**. `SessionPersistenceAdapter.serialize()` must return `{turn_number, save_path, config, galaxy, empires, human_player_ids, event_log}` byte-for-byte. | This is a structural split, not a behavior-cleanup pass. Old saves are disposable per project rules but round-trip tests should stay green. Source plan, "Save schema constraint" and "Save compatibility statement". |
| A single `SessionBootstrapState` payload backs **both** fresh-construction and rehydration paths. | This is the entire point of the remediation: eliminate the duplicated mutator-service / turn-engine / event-bus construction currently mirrored by hand between `__init__` and `from_dict` (PROJ-396 CRIT-002). Source plan, "Required `GameSession` structure". |
| The single assignment path is a private `_apply_bootstrap_state(...)` method. **Do not** use `self.__dict__.update(...)`, and **do not** keep `cls.__new__(cls)` reconstruction in `from_dict`. | Both shortcuts re-introduce drift surfaces. `_apply_bootstrap_state(...)` is the only place that copies state from `SessionBootstrapState` onto the session. Source plan, "Required `GameSession` structure" + "Risks & Mitigations". |
| Public API stays `GameSession(...)`, `GameSession.from_dict(...)`, `GameSession.to_dict()`. **No** mass-migration of call sites to a new factory in this plan. | The codebase has many `GameSession(...)` and `GameSession.from_dict(...)` call sites; rewriting them is out of scope and would broaden the blast radius unnecessarily. Source plan, "Executor Guardrails" + "Risks & Mitigations". |
| The current `human_player_ids` load fallback (`[0, 1]` when missing from the dict) is preserved exactly. | This refactor is structural; do not "clean up" the fallback semantics. A dedicated future plan can revisit it if needed. Source plan, "Implementation rules" for Phase 3. |
| The current `SessionInitializationError` null-object substitution applies only to the **new-game** path. The load path's existing exception behavior is unchanged. | Same structural-vs-behavioral boundary. Source plan, "Implementation rules" for Phase 2 + Phase 3. |
| The new package lives at `game/strategy/engine/session/` with `runtime_services.py`, `bootstrap.py`, and `persistence_adapter.py`. The package does not exist yet — creating it is part of the plan. | Source plan, "Target package layout" + "Executor Guardrails". |
| `game_session.py` must no longer import `FleetNavigationService`, `FleetWriteService`, `PlanetWriteService`, `EmpireWriteService`, `ShipInstanceWriteService`, `TurnEngineConfig`, `TurnEngine`, `GameInitializer`, `EventBus`, or `create_default_registry` once Phase 4 lands. | This is the structural verification that the split is complete. Source plan, "Completion Criteria". |
| **TD-05 coupling:** if PROJ-427 (TD-05) has already shipped when this project starts, `SessionRuntimeServices` (or `SessionBootstrapState` for per-empire catalogs) **must** absorb the `DesignRepository` and per-empire `DesignCatalog` that TD-05 placed on `GameSession`. If TD-05 has not yet landed, no action is required here. | Avoids creating a second service-injection convention that future plans would have to bridge. Source plan, "Cross-plan coupling with TD-05". |

## Implementation decisions

### 2026-05-17 — Phase 6 added from Codex consult

A post-merge Codex consult on the shipped PROJ-423 work surfaced three findings. Two are landed here as Phase 6; the third is tracked as a separate project (PROJ-432).

| Decision | Rationale |
|----------|-----------|
| Migrate the two **production** underscore-alias readers (`persistence_adapter.py`'s `session._event_log` and `turn_state_snapshot.py`'s `session._registries`) to the public `session.services.<accessor>` form. | These were the last production-side readers of the PROJ-423 backwards-compat underscore aliases. The migration is mechanical (one read per file). Codex consult finding #1. |
| **Keep** the underscore-aliased properties on `GameSession` itself (`_event_log`, `_registries`, `_event_bus`, `_fleet_mutator`, `_planet_mutator`, `_empire_mutator`, `_ship_mutator`). | Test code still depends on them; removing them is a separate, larger cleanup with its own blast radius. PROJ-423 was a structural extraction, not an alias-removal pass. Codex consult finding #1, scope decision. |
| Replace the self-delegating `test_serialize_matches_to_dict_output` companion with `test_serialize_matches_frozen_schema_fixture`. The new test builds a deterministic minimal session (empty `Galaxy`, no empires, `asset_base_path=""`) and asserts `SessionPersistenceAdapter.serialize()` equals a hardcoded reference-dict literal. The earlier test was retained for documentation, since it still pins the `to_dict()` → `serialize()` delegate. | Post-PROJ-423, `GameSession.to_dict()` is a one-line forward to `serialize()`, so the original assertion `adapter_data == session.to_dict()` was a tautology. The intent (guarding the save schema's exact shape, key ordering, optional-field handling) needed a frozen literal. Codex consult finding #2. |
| Land the `TurnStateSnapshot.restore()` rehydrate-path-alignment work as a **separate project (PROJ-432)**, not as a PROJ-423 phase. | Codex's explicit recommendation. The asymmetry between `TurnStateSnapshot.restore()` and `SessionPersistenceAdapter.rehydrate_state()` (missing `empire.set_galaxy(...)` + pursuer-tracker rebuild) is a real risk but a behavioral change of its own, not a structural follow-up to the lifecycle extraction. Keeping the scopes separate keeps each project's blast radius and review surface coherent. Codex consult finding #3. |
