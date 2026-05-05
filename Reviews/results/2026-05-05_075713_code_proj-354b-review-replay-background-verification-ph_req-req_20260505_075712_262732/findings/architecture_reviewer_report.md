# Architecture Review Report — PROJ-354B Replay Verification System

**Reviewer:** Architecture Reviewer (AR)
**Date:** 2026-05-05
**Scope:** Layer cleanliness, Pattern #28 conformance, DI compliance

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| MAJOR    | 1 |
| MINOR    | 2 |
| INFO     | 2 |
| **Total**| **6** |

Overall the replay verification system is well-architected. All five scope files respect layer dependency direction (Strategy → Simulation → Core) with one exception in `replay_player.py`. Pattern #28 is faithfully mirrored. The DI/ApplicationContext pattern is consistently applied — `ai_factory` and `registry_provider` are injected at construction, never resolved from module-level globals. No scope file imports from UI or AI layers.

---

## Findings

#### CRITICAL: Simulation layer imports from Strategy layer (upward dependency)

**ID:** AR-001
**Location:** `game/simulation/replay/replay_player.py:72-73`
**Issue:** The deferred import `from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer` inside the `_builder` closure of `build_replay_ship_builder()` violates the fundamental architecture rule that no lower layer may import from a higher layer. `game/simulation/replay/` is in the Simulation layer; `game/strategy/data/` is in the Strategy layer. The dependency direction mandated by `docs/01_ARCHITECTURE.md` is `Simulation → Core/Engine/Services` and `Strategy → Simulation/Core/Engine/Services` — the reverse is prohibited.

The import is deferred (inside a closure, not at module level), which prevents an import-time circular dependency but does **not** eliminate the runtime layer violation. When `run_battle` (simulation) invokes the `_builder` closure during headless replay execution, it indirectly triggers execution of Strategy-layer code from within the Simulation layer's battle pipeline.

**Fix:** Move `build_replay_ship_builder` (or the `ShipInstanceSerializer`-dependent portion) to `game/strategy/services/`. The coordinator already constructs the builder in the Strategy layer and passes it to `run_replay_headless` via DI. The builder factory itself should reside in the layer that owns the `ShipInstanceSerializer` dependency. An alternative is to define an `IShipBuilderFactory` protocol in Core and inject the factory from the Strategy composition root, keeping `replay_player.py` free of Strategy imports entirely.

---

#### MAJOR: Multiple cross-class accesses to ReplayStore private methods

**ID:** AR-002
**Location:**
- `game/strategy/services/replay_verification_coordinator.py:276,339` — `self._store._replay_dir()  # noqa: SLF001`
- `game/strategy/services/replay_resolver.py:98,136` — `self._store._replay_dir()  # noqa: SLF001`
- `game/strategy/services/replay_resolver.py:106` — `self._store._safe_load(replay_path)  # noqa: SLF001`

**Issue:** Three call sites across two different classes (`ReplayVerificationCoordinator`, `ReplayResolver`) access private (`_`-prefixed) methods of `ReplayStore`. While these are same-package (`game.strategy.services`) accesses, the pattern indicates `ReplayStore` has an insufficient public API:

1. `_replay_dir()` is a trivial property (`self._save_root / self.REPLAY_SUBDIR`) — the store should expose it as a public `replay_dir` property (matching the existing public `save_root` property).
2. `_safe_load(Path)` is used by `ReplayResolver` to distinguish "corrupt JSON" from "missing file" from "schema version mismatch", granularity the public `load(replay_id)` intentionally collapses into `None`. The store's public API lacks a `load_with_error_detail` or equivalent.

The `# noqa: SLF001 — package-internal` comments acknowledge the encapsulation breach. The access in `ReplayResolver._store_replay_dir()` wraps `_replay_dir()` redundantly — both methods do the same thing.

**Fix:**
- Promote `_replay_dir` to a public `replay_dir` property on `ReplayStore`.
- Add a public `load_or_error(replay_id) -> tuple[ReplayRecord | None, str | None]` method to `ReplayStore` so `ReplayResolver` doesn't need `_safe_load`.
- Remove the `_store_replay_dir()` wrapper on `ReplayResolver` — call `store.replay_dir` directly.

---

#### MINOR: Race window between worker start and listener registration

**ID:** AR-003
**Location:** `game/strategy/services/replay_verification_coordinator.py:177-178`
**Issue:** `start()` spawns the worker thread at line 172-177, then registers the `ReplayStore` listener at line 178:

```python
self._worker.start()                                            # line 177
self._store.add_on_record_persisted_listener(...)               # line 178
```

If a replay is persisted between worker start and listener registration (i.e., the listener is not yet attached), the record is silently dropped — the worker thread is alive but its queue is empty, and no callback fires. The probability is low in production but non-zero under concurrent capture workloads (e.g., simultaneous auto-resolve in multiple sectors).

**Fix:** Reorder — register the listener before spawning the worker. Since the worker loop polls the queue first and the queue starts empty, the ordering is safe:
```python
self._store.add_on_record_persisted_listener(self._on_record_persisted)
self._worker.start()
```
This guarantees zero gap between the listener being active and the worker being able to process.

---

#### MINOR: shutdown docstring claims queue is dropped, but worker drains it

**ID:** AR-004
**Location:** `game/strategy/services/replay_verification_coordinator.py:186-188` (docstring) vs lines 250-268 (implementation)
**Issue:** The `shutdown()` docstring states:

> Records still in the queue at shutdown time are dropped — the worker terminates on the next iteration once the shutdown event is observed.

But the implementation at lines 250-268 **drains** the queue after shutdown is signaled. The condition at line 253 exits immediately when `_shutdown_event.is_set()` (regardless of queue state), and the return guard at line 255 only fires when the queue is empty. If records remain in the queue, the worker pops and processes each one before eventually returning.

This is a docstring bug — the implementation semantics (drain-and-terminate) are actually the more desirable behavior for a background verification service (in-flight verifications complete, yielding sidecars rather than orphaned records). The docstring should be updated to match.

**Fix:** Correct the docstring to: "The worker drains any remaining records in the queue before terminating, so verification sidecars are written for queued-but-unprocessed replays."

---

#### INFO: ReplayStore depends on verification sidecar for lifecycle management

**ID:** AR-005
**Location:**
- `game/strategy/services/replay_store.py:47-50` — imports `SIDECAR_FILE_SUFFIX`, `sidecar_path_for_replay`
- `game/strategy/services/replay_store.py:390-391` — `_iter_replay_files` filters sidecars by suffix
- `game/strategy/services/replay_store.py:406-418` — `_unlink_sidecar` deletes sidecar with replay

**Issue:** `ReplayStore` imports from `replay_verification_sidecar`, creating a dependency from general replay persistence to verification-specific concerns. This is architecturally defensible because the store must:
1. Filter `replay_*.verification.json` files from file enumeration (otherwise eviction miscounts them as replay records)
2. Delete sidecars when their replay records are deleted/evicted (required lifecycle binding)

Both integrations are limited to `@staticmethod` utility imports (`SIDECAR_FILE_SUFFIX`, `sidecar_path_for_replay`) which are pure path helpers with no behavioral dependency. No architectural action required — this is documented for visibility.

---

#### INFO: ReplayVerificationCoordinator faithfully mirrors Pattern #28

**ID:** AR-006
**Location:** `game/strategy/services/replay_verification_coordinator.py:67-93` and `background.py:345-376`
**Issue:** Positive observation — the coordinator's threading model correctly mirrors `LLMBackgroundCall` / `shutdown_all_calls` (Pattern #28, Background Service Call):

| Feature | LLMBackgroundCall | ReplayVerificationCoordinator |
|---------|-------------------|-------------------------------|
| Module-level active set | `_active_workers` + `_in_flight_lock` | `_active_coordinators` + `_coordinator_lock` |
| Module-level shutdown | `shutdown_all_calls(timeout)` | `shutdown_all_coordinators(timeout)` |
| Snapshot-under-lock | Yes | Yes |
| Shared deadline per worker | Yes | Yes |
| Worker threads non-daemon | `daemon=False` | `daemon=False` |
| Per-instance state lock | `_state_lock` | `_state_lock` |
| Termination signal | `_cancel_event` (threading.Event) | `_shutdown_event` (threading.Event) |
| Abandonment warning | `logger.warning(...)` | `logger.warning(...)` |

The coordinator extends the pattern with a FIFO queue + Condition variable (appropriate for its persistent-worker design vs. LLM's one-shot execution) and an `_idle_event` for test synchronization. These extensions are fit-for-purpose and do not deviate from Pattern #28's core contract.

---

## Layer Dependency Summary

| File | Layer | Imports from Core | Imports from Simulation | Imports from Strategy | Imports from UI/AI |
|------|-------|-------------------|------------------------|----------------------|--------------------|
| `replay_verifier.py` | Simulation | — | battle_outcome, replay_record, replay_serialization | — | — |
| `replay_player.py` | Simulation | — | battle_outcome, battle_runner, battle_spec, replay_record | **ShipInstanceSerializer (VIOLATION)** | — |
| `replay_verification_coordinator.py` | Strategy | — | replay_player, replay_record, replay_verifier | replay_store, verification_sidecar | — |
| `replay_verification_sidecar.py` | Strategy | json_utils | — | — | — |
| `replay_store.py` | Strategy | json_utils, paths | replay (DTOs) | verification_sidecar (utilities) | — |
| `replay_resolver.py` | Strategy | — | replay (DTOs + hash) | replay_store, verification_sidecar | — |

---

## Top 5 Priority Issues

1. **AR-001 (CRITICAL):** `replay_player.py` imports `ShipInstanceSerializer` from Strategy layer. Move builder factory to Strategy layer or inject via protocol. Breaks the fundamental "no upward dependency" rule.
2. **AR-002 (MAJOR):** `ReplayStore` private methods accessed by sibling classes. Promote `_replay_dir` to public; add `load_or_error()` to public API.
3. **AR-003 (MINOR):** Race window in `start()` — register listener before spawning worker thread.
4. **AR-004 (MINOR):** `shutdown()` docstring contradicts implementation — says queue is dropped, actually drains.
5. **AR-005 (INFO):** `ReplayStore` depends on sidecar utilities for lifecycle management. Acceptable, documented for visibility.

---

## Design Strengths (Noted)

- The `replay_verifier.py` module is a pure, layer-agnostic equality oracle with zero dependencies outside Simulation/Core. This is exactly the right decomposition for the "pure verifier" contract described in the PROJ-354B design.
- All APIs use DI injection (`ai_factory`, `registry_provider`) rather than module-level globals — consistent with Pattern #1 (ApplicationContext).
- The listener pattern on `ReplayStore` (`add_on_record_persisted_listener`) is clean pub-sub — the store knows nothing about verification; the coordinator subscribes at arm's length.
- The sidecar pattern (`.verification.json` alongside `.json`) keeps verification lifecycle independent from replay record immutability — exactly as described in the design doc.
- `shutdown_all_coordinators` is a line-for-line mirror of `shutdown_all_calls` — Pattern #28 conformance is obvious and correct.
- Module-level coordinator registry ensures all coordinators are joined during game shutdown, preventing thread leaks.
