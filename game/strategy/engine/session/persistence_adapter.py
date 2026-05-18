"""PROJ-423 Phase 3: SessionPersistenceAdapter — save / load split.

`serialize(session)` returns the on-disk dict shape `GameSession.to_dict()`
historically produced, byte-for-byte. `rehydrate_state(data, ai_factory=...)`
performs the two-phase galaxy/empire deserialisation plus the four
load-only operations (galaxy back-refs, fleet registration, order
reference resolution, pursuer-tracker rebuild) and returns a
`SessionBootstrapState`.

The save schema is intentionally unchanged: `{turn_number, save_path,
config, galaxy, empires, human_player_ids, event_log}`. The
`human_player_ids` `[0, 1]` fallback for missing keys is preserved
exactly.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from game.core.error_codes import ErrorCode
from game.core.exceptions import PersistenceException
from game.strategy.engine.game_config import GameConfig
from game.strategy.engine.session.runtime_services import (
    SessionBootstrapState,
)
from game.strategy.events import EventLog

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


class SessionPersistenceAdapter:
    """Save/load adapter for `GameSession`."""

    @staticmethod
    def serialize(session: "GameSession") -> dict[str, Any]:
        """Return the canonical save-dict shape for `session`.

        Pinned by `test_serialize_preserves_existing_save_schema`. The
        returned shape is:

            {
                'turn_number': int,
                'save_path': str | None,
                'config': dict,
                'galaxy': dict,
                'empires': list[dict],
                'human_player_ids': list[int],
                'event_log': dict,
            }
        """
        return {
            "turn_number": session.turn_number,
            "save_path": session.save_path,
            "config": session.config.to_dict(),
            "galaxy": session.galaxy.to_dict(),
            "empires": [e.to_dict() for e in session.empires],
            "human_player_ids": session.human_player_ids.copy(),
            "event_log": session.services.event_log.to_dict(),
        }

    @staticmethod
    def rehydrate_state(
        data: dict[str, Any],
        *,
        ai_factory: Any | None = None,
        turn_number_provider: Callable[[], int] | None = None,
        race_registry_provider: Callable[[], Any] | None = None,
    ) -> SessionBootstrapState:
        """Reconstruct a `SessionBootstrapState` from a save dict.

        Performs the two-phase load (galaxy first, empires second so they
        can resolve planet references via the galaxy registry) followed
        by the four load-only operations:

        - Galaxy back-references on each empire (PROJ-219 pre-req).
        - Fleet registration with the galaxy fleet registry (PROJ-219).
        - Fleet order reference resolution (PROJ-207).
        - Pursuer tracker rebuild from resolved targets (PROJ-222).

        Preserves the current `human_player_ids` `[0, 1]` fallback when
        the key is missing from `data`. Returns a `SessionBootstrapState`
        — never a `GameSession`. The caller (`GameSession.from_dict`)
        wraps the state in a fresh session via `_state=` kwarg.

        Raises:
            PersistenceException: If required save fields are missing or
                corrupt.
        """
        # Lazy imports avoid top-level cycles with game_session.py.
        from game.strategy.data.empire import Empire
        from game.strategy.data.galaxy import Galaxy
        from game.strategy.engine.game_session import GameSession
        from game.strategy.engine.session.bootstrap import SessionBootstrap
        from game.strategy.engine.session.graph_restoration import (
            restore_graph_wiring,
        )

        # Restore config with context on error.
        try:
            config = GameConfig.from_dict(data["config"])
        except KeyError as e:
            raise PersistenceException(
                f"Missing required config field: {e}",
                code=ErrorCode.SAVE_FAILED.value,
                context={"section": "config", "missing_field": str(e)},
            ) from e

        turn_number = data.get("turn_number", 1)
        save_path = data.get("save_path")

        registries = GameSession._resolve_registries()

        # Restore event log (PROJ-77) before wiring services so the
        # bootstrap reuses the deserialized log (PROJ-252).
        restored_event_log = EventLog.from_dict(
            data.get("event_log", {"events": []})
        )

        # The event-handler closure needs a live turn-number source so
        # events stamp the *post-load* turn even though `from_dict`
        # builds the state before the session is fully constructed. The
        # caller (`GameSession.from_dict`) passes a provider that points
        # at the bare session's `turn_number` slot, which
        # `_apply_bootstrap_state` populates from `state.turn_number`
        # below.
        if turn_number_provider is None:
            turn_number_provider = lambda: turn_number  # noqa: E731

        # Race registry: rehydrate-only callers can pass their own
        # provider so the bootstrap shares the same cached
        # `CachedRaceRegistry` instance as the session's `race_registry`
        # property. When None, the bootstrap falls back to its own
        # eager construction.
        from game.strategy.engine.session.bootstrap import build_event_handler

        services = SessionBootstrap._build_services(
            registries=registries,
            event_log=restored_event_log,
            ai_factory=ai_factory,
            race_registry_provider=race_registry_provider,
            event_handler_factory=lambda log: build_event_handler(
                log, turn_number_provider
            ),
        )

        # Two-phase deserialisation.
        try:
            galaxy = Galaxy.from_dict(data["galaxy"])
        except KeyError as e:
            raise PersistenceException(
                f"Missing required galaxy field: {e}",
                code=ErrorCode.LOAD_FAILED.value,
                context={"section": "galaxy", "missing_field": str(e)},
            ) from e

        try:
            empires = [
                Empire.from_dict(
                    emp_data, galaxy=galaxy, registries=registries
                )
                for emp_data in data.get("empires", [])
            ]
        except KeyError as e:
            raise PersistenceException(
                f"Missing required empire field: {e}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={"section": "empires", "missing_field": str(e)},
            ) from e

        # Human player IDs — preserve the existing [0, 1] fallback exactly.
        human_player_ids = data.get("human_player_ids", [0, 1])

        # PROJ-438 Phase 1: four canonical post-deserialize wiring steps
        # (galaxy back-refs, fleet registration, order-target resolve,
        # pursuer-tracker rebuild). Shared with TurnStateSnapshot.restore.
        restore_graph_wiring(galaxy, empires)

        # PROJ-427 Phase 2: build per-empire DesignCatalog map now that
        # empires are restored. Catalogs are populated from each
        # empire's DesignRepository scan (the save folder is the
        # canonical source). The frozen services dataclass is re-
        # wrapped via dataclasses.replace so the anti-drift contract
        # (test_init_and_from_dict_use_identical_service_classes) sees
        # identical shape between fresh and loaded sessions.
        #
        # PROJ-438 Phase 1 Task 1.3 — INTENTIONAL ASYMMETRY: this block
        # runs on the save-load path ONLY. TurnStateSnapshot.restore()
        # deliberately does not rebuild the catalog map because a
        # rollback never crosses a process boundary; the in-memory map
        # built at session start (or refreshed at the last save-load)
        # is still valid through a turn rollback. Pinned by
        # test_restore_path_parity.py::test_documented_design_catalog_
        # asymmetry. Do not collapse this block into the shared
        # graph-restoration collaborator without changing that test.
        from dataclasses import replace as _dc_replace
        from game.strategy.systems.design_catalog import DesignCatalog
        from game.strategy.systems.design_repository import DesignRepository

        catalogs_by_empire: dict[int, DesignCatalog] = {}
        for emp in empires:
            cat = DesignCatalog(empire_id=emp.id)
            per_empire_repo = DesignRepository(save_path, empire_id=emp.id)
            cat.repopulate_from(per_empire_repo)
            catalogs_by_empire[emp.id] = cat
        services = _dc_replace(
            services,
            design_catalogs_by_empire=catalogs_by_empire,
        )

        # PROJ-427 Phase 3: forward catalog map into the ProductionEngine
        # spawner so runtime spawn paths resolve designs without disk I/O.
        setter = getattr(
            services.turn_engine.production_engine,
            'set_design_catalogs_by_empire', None,
        )
        if setter is not None:
            setter(catalogs_by_empire)

        return SessionBootstrapState(
            config=config,
            services=services,
            galaxy=galaxy,
            empires=empires,
            turn_number=turn_number,
            save_path=save_path,
            human_player_ids=human_player_ids,
        )
