"""PROJ-312 Phase 6 — Replay resolution service for the Event Log UI.

The Event Log surfaces a "Replay" button on each battle event row. Clicking
it calls into this resolver, which wraps ``ReplayStore`` with the
graceful-degradation contract described in ``decisions.md``:

    * Missing on disk     → ``ReplayLookup(found=False, reason="missing")``
    * Corrupt JSON        → ``ReplayLookup(found=False, reason="corrupt")``
    * Version mismatch    → ``ReplayLookup(found=False, reason="version_drift")``
    * Registry-hash drift → ``ReplayLookup(found=True, registry_drift=True)``
    * Healthy             → ``ReplayLookup(found=True, registry_drift=False)``

The UI dispatches based on these flags: disabled/tooltip for not-found,
confirmation dialog for registry drift, direct launch otherwise. This
module's only dependency is ``ReplayStore`` (and the simulation replay
package); it must not import pygame_gui.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from game.simulation.replay import (
    REPLAY_SCHEMA_VERSION,
    ReplayRecord,
    compute_components_registry_hash,
)
from game.strategy.services.replay_store import ReplayStore
from game.strategy.services.replay_verification_sidecar import (
    read_verification_sidecar,
)


@dataclass(frozen=True)
class ReplayLookup:
    """Result of ``ReplayResolver.resolve(replay_id)``.

    ``record`` is populated only when ``found`` is True. ``reason`` is
    populated only when ``found`` is False — one of ``"missing"``,
    ``"corrupt"``, ``"version_drift"``. ``registry_drift`` is True when
    the captured components-registry hash differs from the running hash;
    the UI surfaces a confirmation dialog before launching playback.

    PROJ-354B Phase 3.2: ``verification_status`` exposes the sidecar
    status (``"PASSED"``, ``"FAILED"``, ``"ERROR"``,
    ``"SKIPPED_QUEUE_FULL"``, ``"SKIPPED_DISABLED"``) when a sidecar
    exists, or ``None`` when verification has not yet completed for
    this replay.
    """

    found: bool
    record: Optional[ReplayRecord] = None
    reason: Optional[str] = None
    registry_drift: bool = False
    verification_status: Optional[str] = None


class ReplayResolver:
    """Service that the Event Log UI calls to resolve a ``replay_id``.

    Bound to one ``ReplayStore`` (the production-wired sink). The
    ``current_components_registry_hash`` is computed once at construction
    time (Phase 6 considers this acceptable — registries don't reload
    mid-session in production).
    """

    def __init__(
        self,
        store: ReplayStore,
        *,
        current_components_registry_hash: str = "sha256:unknown",
    ) -> None:
        self._store = store
        self._current_hash = current_components_registry_hash

    @classmethod
    def from_registries(
        cls,
        store: ReplayStore,
        registries,
    ) -> "ReplayResolver":
        """Build a resolver that derives the current components hash from
        a live ``GameRegistries`` bundle."""
        return cls(
            store,
            current_components_registry_hash=compute_components_registry_hash(registries),
        )

    def resolve(self, replay_id: str) -> ReplayLookup:
        """Resolve a replay_id to a ``ReplayLookup`` result.

        Never raises — corrupt/missing/version-drift are reported via
        ``ReplayLookup.reason`` so the UI can render an appropriate
        affordance (greyed button, tooltip, banner).
        """
        if not replay_id:
            return ReplayLookup(found=False, reason="missing")

        # PROJ-354B audit AR-002: use the public ``load_or_error`` API
        # instead of reaching into ``_safe_load``. ``replay_dir`` is
        # the public property the sidecar reader still needs.
        rd = self._store.replay_dir
        if rd is None:
            return ReplayLookup(found=False, reason="missing")

        record, reason = self._store.load_or_error(replay_id)
        if record is None:
            return ReplayLookup(found=False, reason=reason or "missing")

        # Components-registry drift: still loadable, but UI surfaces a
        # confirmation dialog.
        registry_drift = (
            bool(record.components_registry_hash)
            and bool(self._current_hash)
            and record.components_registry_hash != self._current_hash
        )
        # PROJ-354B Phase 3.2: surface sidecar verification status if
        # present. Missing/corrupt sidecars yield ``None`` (the absence
        # is normal pre-verification state).
        sidecar = read_verification_sidecar(rd, replay_id)
        verification_status = sidecar.status if sidecar is not None else None
        return ReplayLookup(
            found=True,
            record=record,
            registry_drift=registry_drift,
            verification_status=verification_status,
        )


__all__ = ["ReplayLookup", "ReplayResolver"]
