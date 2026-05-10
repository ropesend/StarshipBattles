# PROJ-390 — Verification Report

**Source audit:** `Reviews/results/2026-05-07_220621_legacy-audit/`
**Run date:** 2026-05-08
**Cluster:** `log_event` module-level compat shim retirement
**Batch summary:** 1 verified (dedup) / 0 rejected / 0 uncertain / 0 INFO / 2 out-of-scope (other singleton patterns)

## Verified

| ID | File | Symbol | Replaces | Call sites | Recommendation | Severity |
|---|---|---|---|---|---|---|
| LEG-02-016 / LEG-03-021 (dedup) | `game/core/event_logging.py:57-88` | module-level `log_event`, `set_event_handler`, `get_event_handler`, `_event_handler` global | injected `EventBus` (Pattern 1 / ApplicationContext) | ~12 prod | migrate_callers_then_delete | MAJOR |

## Rejected

None — Sonnet confirmed against current source. The pattern doc itself confesses to the shim status.

## Uncertain (resolved)

None for this bundle.

## INFO (resolved)

None for this bundle.

## Out of Scope

| ID | Reason |
|---|---|
| LEG-04-014 (`policy_manager` auto-create singleton) | User excluded during Phase D Step 4 — large scope, separate project. Same shape (module-level singleton) but different module. |
| LEG-04-015 (`registry.py` module-level singleton) | Same as LEG-04-014. |

## Already Done by PROJ-382 (deferred-during-implementation)

PROJ-382 Phase 2 ("Pattern #10 — Cross-Layer Mediator / event-logger injection")
already migrated the bulk of the audit's "~12 production callers" to use injected
`EventBus` instances or callable `event_logger=` parameters. Confirmed via fresh
re-grep on 2026-05-08:

| Caller | PROJ-382 outcome |
|---|---|
| `game/strategy/data/empire.py` | Migrated — `event_bus.log_event(...)` (line 109). No module-level import remains. |
| `game/strategy/data/fleet.py` | Migrated — `event_bus.log_event(...)` (lines 408, 427). No module-level import remains. |
| `game/strategy/engine/conflict_resolution_engine.py` | Migrated — `self._event_bus.log_event(...)` (line 158). |
| `game/strategy/engine/superweapon_order_processor.py` | Migrated — `self._event_bus.log_event(...)` (lines 134, 309). |
| `game/strategy/engine/order_handlers/base.py` | Migrated — `self._event_bus.log_event(...)` (line 139). |
| `game/strategy/engine/production_spawner.py` | Migrated — `self._event_bus.log_event(...)` (3 sites). |
| `game/strategy/engine/production_engine.py` | Migrated — `self._event_bus.log_event(...)` (line 568). |
| `game/strategy/engine/planet_energy_engine.py` | Migrated — `self._event_bus.log_event(...)` (line 302). |
| `game/strategy/engine/planet_action_engine.py` | Migrated — `self._event_bus.log_event(...)` (3 sites). |
| `game/simulation/entities/projectile.py` | **Partially** migrated — constructor takes injected `event_logger=` callable (PROJ-382 Phase 2 Pattern #10), BUT the default still lazy-imports the module-level `log_event`. PROJ-390 finishes the job. |

**Net production sites remaining for PROJ-390 to retire:** **1**
(the `_default_event_logger` fallback in `projectile.py`).

## ApplicationContext wiring

Plan called for "wire `EventBus` into `ApplicationContext` if not already there
(Pattern 1)". On inspection, EventBus is intentionally **session-scoped** (each
`GameSession` holds its own to avoid process-global state — PROJ-252). Putting
it on `ApplicationContext` (which is process-scoped) would re-introduce the
exact isolation problem the shim is being deleted to fix. The canonical
pattern remains: `GameSession` constructs the bus and threads it through
constructor injection to the engines/handlers/data classes that need it.
Task 1.2 is therefore a no-op — already correctly wired by PROJ-252 / PROJ-382.
