"""PROJ-354B Phase 4 — Replay verification coordinator.

A single-worker FIFO background service that drives the replay
verification pipeline:

    1. Subscribe to ``ReplayStore``'s post-persist listener.
    2. On callback, enqueue the record (or write a
       ``SKIPPED_QUEUE_FULL`` sidecar if the queue is at cap).
    3. Worker thread pops records FIFO, materializes the ship builder,
       runs ``run_replay_headless`` (which forces ``capture_context=None``
       so verification cannot recursively trigger capture), runs the
       pure verifier, and writes a sidecar (PASSED/FAILED/ERROR).

Threading model mirrors :class:`LLMBackgroundCall`
(``game/services/llm/background.py``): a per-instance state lock,
shutdown event, queue list, and a module-level set of active
coordinators with a shared ``shutdown_all_coordinators`` join helper.

Dependencies are DI-injected at construction time per Pattern #1
(ApplicationContext): ``ai_factory`` and ``registry_provider`` come from
the composition root, never module-level globals. The ``replay_runner``
and ``ship_builder_factory`` parameters exist primarily to let tests
substitute pure stubs without requiring a full ``run_battle`` call.

The coordinator does NOT terminate hostile/runaway verifier code —
Python threads cannot be hard-killed without a process boundary.
The queue cap + drop-on-full provides bounded mitigation; if the
worker stalls on a malicious mod, subsequent records are dropped to
``SKIPPED_QUEUE_FULL`` sidecars rather than queuing indefinitely.
"""
from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Set

from game.simulation.replay.replay_player import (
    build_replay_ship_builder,
    run_replay_headless,
)
from game.simulation.replay.replay_record import ReplayRecord
from game.simulation.replay.replay_verifier import (
    Difference,
    verify_replay_outcome,
)
from game.strategy.services.replay_store import ReplaySettings, ReplayStore
from game.strategy.services.replay_verification_sidecar import (
    REPLAY_VERIFICATION_SCHEMA_VERSION,
    VerificationSidecar,
    VerificationSource,
    VerificationStatus,
    write_verification_sidecar,
)

if TYPE_CHECKING:
    from game.simulation.battle_outcome import BattleOutcome
    from game.simulation.battle_spec import ShipSpec
    from game.simulation.entities.ship import Ship


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Module-level coordinator registry
# ---------------------------------------------------------------------------


_coordinator_lock = threading.Lock()
_active_coordinators: Set["ReplayVerificationCoordinator"] = set()


def shutdown_all_coordinators(timeout: float = 5.0) -> None:
    """Join all active coordinators with a shared deadline.

    Mirrors ``shutdown_all_calls`` in
    ``game/services/llm/background.py``. Called from the run-loop
    shutdown hook so verification work drains before pygame teardown.
    Workers that don't finish within ``timeout`` are abandoned with a
    warning rather than hanging shutdown.
    """
    with _coordinator_lock:
        coordinators = list(_active_coordinators)
    if not coordinators:
        return
    deadline = time.monotonic() + timeout
    for coord in coordinators:
        remaining = max(0.0, deadline - time.monotonic())
        coord.shutdown(timeout=remaining)


# ---------------------------------------------------------------------------
# Coordinator
# ---------------------------------------------------------------------------


# Default poll interval (s). Worker uses a condition variable so this
# is only the maximum wait between shutdown checks when the queue is
# empty; non-empty queue dispatches immediately.
_WORKER_IDLE_POLL_SECONDS = 0.05


def _difference_to_dict(d: Difference) -> dict:
    return {
        "path": list(d.path),
        "expected": d.expected,
        "actual": d.actual,
    }


# Type alias for the callable a test or the production wiring can
# substitute for ``run_replay_headless``. Production passes the real
# function; tests pass stubs.
ReplayRunner = Callable[..., "BattleOutcome"]
ShipBuilderFactory = Callable[..., Optional[Callable[["ShipSpec", int], "Ship"]]]


class ReplayVerificationCoordinator:
    """Background service that verifies persisted replay records.

    Construct in the composition root, register on the production
    ``ReplayStore`` via :meth:`start`, and join via :meth:`shutdown`
    (or ``shutdown_all_coordinators``) on exit.
    """

    def __init__(
        self,
        *,
        replay_store: ReplayStore,
        ai_factory: Any,
        registry_provider: Any,
        settings: ReplaySettings,
        fallback_ship_builder: Optional[
            Callable[["ShipSpec", int], "Ship"]
        ] = None,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        # Test-injection points: production code uses the defaults.
        replay_runner: ReplayRunner = run_replay_headless,
        ship_builder_factory: ShipBuilderFactory = build_replay_ship_builder,
    ) -> None:
        self._store = replay_store
        self._ai_factory = ai_factory
        self._registry_provider = registry_provider
        self._settings = settings
        self._fallback_ship_builder = fallback_ship_builder
        self._clock = clock
        self._replay_runner = replay_runner
        self._ship_builder_factory = ship_builder_factory

        # State (queue + worker + shutdown signal).
        self._state_lock = threading.Lock()
        self._queue: List[ReplayRecord] = []
        self._queue_signal = threading.Condition(self._state_lock)
        self._shutdown_event = threading.Event()
        self._worker: Optional[threading.Thread] = None
        self._listener_registered = False
        self._busy = False  # True while worker is mid-record
        self._idle_event = threading.Event()
        self._idle_event.set()

    # -- Lifecycle ----------------------------------------------------------

    def start(self) -> None:
        """Register the listener and spawn the worker. Idempotent."""
        with self._state_lock:
            if self._worker is not None:
                return
            self._shutdown_event.clear()
            self._worker = threading.Thread(
                target=self._worker_loop,
                name=f"ReplayVerifier-{id(self):x}",
                daemon=False,
            )
            self._worker.start()
        self._store.add_on_record_persisted_listener(self._on_record_persisted)
        self._listener_registered = True
        with _coordinator_lock:
            _active_coordinators.add(self)

    def shutdown(self, timeout: float = 5.0) -> None:
        """Signal shutdown, deregister, and join the worker.

        Idempotent. Records still in the queue at shutdown time are
        dropped — the worker terminates on the next iteration once the
        shutdown event is observed.
        """
        # Deregister first so a race between persist and shutdown
        # cannot enqueue a new record after we've stopped servicing.
        if self._listener_registered:
            self._store.remove_on_record_persisted_listener(
                self._on_record_persisted
            )
            self._listener_registered = False
        self._shutdown_event.set()
        with self._queue_signal:
            self._queue_signal.notify_all()
        worker = self._worker
        if worker is not None:
            worker.join(timeout=timeout)
            if worker.is_alive():
                logger.warning(
                    "PROJ-354B verification worker %s did not finish within %.1fs",
                    worker.name, timeout,
                )
            self._worker = None
        with _coordinator_lock:
            _active_coordinators.discard(self)

    # -- Listener callback --------------------------------------------------

    def _on_record_persisted(self, record: ReplayRecord, path: Path) -> None:
        """Listener registered on ``ReplayStore``.

        Disabled-setting and queue-full cases write their sidecars
        synchronously here so the user always sees a sidecar for every
        captured replay (no silent drops).
        """
        if self._shutdown_event.is_set():
            return
        # Disabled toggle: write SKIPPED_DISABLED sidecar inline.
        if not self._settings.verification_enabled:
            self._write_sidecar(
                record,
                status=VerificationStatus.SKIPPED_DISABLED,
                duration_ms=0,
            )
            return
        # Queue cap check.
        with self._queue_signal:
            if len(self._queue) >= self._settings.verification_queue_cap:
                # Full — write the skipped sidecar and return.
                full = True
            else:
                full = False
                self._queue.append(record)
                self._idle_event.clear()
                self._queue_signal.notify()
        if full:
            self._write_sidecar(
                record,
                status=VerificationStatus.SKIPPED_QUEUE_FULL,
                duration_ms=0,
            )

    # -- Worker -------------------------------------------------------------

    def _worker_loop(self) -> None:
        while True:
            with self._queue_signal:
                while not self._queue and not self._shutdown_event.is_set():
                    self._queue_signal.wait(timeout=_WORKER_IDLE_POLL_SECONDS)
                if self._shutdown_event.is_set() and not self._queue:
                    return
                if not self._queue:
                    continue
                record = self._queue.pop(0)
                self._busy = True
            try:
                self._verify_one(record)
            finally:
                with self._queue_signal:
                    self._busy = False
                    if not self._queue:
                        self._idle_event.set()

    def _verify_one(self, record: ReplayRecord) -> None:
        """Run the headless replay, verify, and persist the sidecar.

        Defensive against the save root being cleared mid-verification
        (R6): we re-check the replay dir before writing the sidecar so
        a deleted save doesn't leak a sidecar into a stale folder.
        """
        rd = self._store._replay_dir()  # noqa: SLF001 — package-internal
        if rd is None:
            logger.debug(
                "PROJ-354B verification dropped — save root cleared "
                "before sidecar write: %s",
                record.replay_id,
            )
            return
        start = time.monotonic()
        try:
            ship_builder = self._ship_builder_factory(
                record,
                registry_provider=self._registry_provider,
                fallback_builder=self._fallback_ship_builder,
            )
            replayed_outcome = self._replay_runner(
                record,
                ai_factory=self._ai_factory,
                ship_builder=ship_builder,
                registry_provider=self._registry_provider,
            )
            result = verify_replay_outcome(record, replayed_outcome)
            duration_ms = int((time.monotonic() - start) * 1000)
            status = (
                VerificationStatus.PASSED
                if result.passed
                else VerificationStatus.FAILED
            )
            diff_payload = (
                [_difference_to_dict(d) for d in result.diff]
                if not result.passed
                else None
            )
            self._write_sidecar(
                record,
                status=status,
                duration_ms=duration_ms,
                diff=diff_payload,
            )
        except Exception as exc:  # Intentional broad catch: worker must continue past one bad record
            duration_ms = int((time.monotonic() - start) * 1000)
            logger.exception(
                "PROJ-354B verification ERROR for replay_id=%s",
                record.replay_id,
            )
            self._write_sidecar(
                record,
                status=VerificationStatus.ERROR,
                duration_ms=duration_ms,
                error={"type": type(exc).__name__, "message": str(exc)},
            )

    # -- Sidecar helper -----------------------------------------------------

    def _write_sidecar(
        self,
        record: ReplayRecord,
        *,
        status: VerificationStatus,
        duration_ms: Optional[int],
        diff: Optional[List[dict]] = None,
        error: Optional[dict] = None,
    ) -> None:
        rd = self._store._replay_dir()  # noqa: SLF001 — package-internal
        if rd is None:
            return
        sidecar = VerificationSidecar(
            replay_id=record.replay_id,
            schema_version=REPLAY_VERIFICATION_SCHEMA_VERSION,
            status=status.name,
            source=VerificationSource.BACKGROUND.name,
            verified_at=self._clock().isoformat(),
            duration_ms=duration_ms,
            diff=diff,
            error=error,
        )
        write_verification_sidecar(rd, sidecar)

    # -- Test / introspection helpers --------------------------------------

    def wait_for_idle(self, timeout: float = 5.0) -> bool:
        """Block until the queue is empty AND the worker is not mid-record.

        Returns True if idle within ``timeout``, False on timeout.
        Useful for tests; the listener-driven contract makes
        synchronous waits awkward without this.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._idle_event.wait(
                timeout=max(0.0, deadline - time.monotonic())
            ):
                # Recheck under lock to defend against the worker
                # having signalled idle right before another enqueue
                # arrived.
                with self._queue_signal:
                    if not self._queue and not self._busy:
                        return True
        return False

    def _is_worker_busy(self) -> bool:
        with self._queue_signal:
            return self._busy


__all__ = [
    "ReplayVerificationCoordinator",
    "shutdown_all_coordinators",
]
