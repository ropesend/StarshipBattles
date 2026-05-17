"""PROJ-423: internal collaborators that own the GameSession lifecycle.

This package houses the three internal value objects / helpers that absorb
`GameSession`'s former composition-root and rehydration responsibilities:

- `runtime_services.SessionRuntimeServices` — frozen dataclass holding the
  wired mutator + registry + event-bus + turn-engine + command-registry bag.
- `runtime_services.SessionBootstrapState` — frozen dataclass that is the
  single internal payload `GameSession.__init__` and `GameSession.from_dict`
  both consume via `_apply_bootstrap_state(...)`.
- `bootstrap.SessionBootstrap` (Phase 2) — canonical construction.
- `persistence_adapter.SessionPersistenceAdapter` (Phase 3) — serialize +
  rehydrate.

The public API (`GameSession(...)`, `GameSession.from_dict(...)`,
`GameSession.to_dict()`) and the on-disk save schema are unchanged.
"""
from game.strategy.engine.session.runtime_services import (
    SessionBootstrapState,
    SessionRuntimeServices,
)

__all__ = [
    "SessionBootstrapState",
    "SessionRuntimeServices",
]
