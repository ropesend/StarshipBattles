"""
Turn State Snapshot - Pre-turn state capture for rollback.

PROJ-251 Phase 4: Captures empire and galaxy state before a turn begins.
If the turn fails partway through, the snapshot is used to restore state.

Uses to_dict()/from_dict() round-trip for serialization, reusing the
existing tested infrastructure.
"""
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from game.core.exceptions import PersistenceException
from game.core.error_codes import ErrorCode
from game.core.json_utils import save_json

logger = logging.getLogger(__name__)


@dataclass
class TurnStateSnapshot:
    """Pre-turn state capture for rollback on failure.

    Attributes:
        turn_number: Which turn this snapshot was taken before.
        empire_dicts: Serialized empire state (list of dicts).
        galaxy_dict: Serialized galaxy state (dict).
        timestamp: time.time() when snapshot was captured.
    """
    turn_number: int
    empire_dicts: List[dict] = field(default_factory=list)
    galaxy_dict: dict = field(default_factory=dict)
    timestamp: float = 0.0

    @classmethod
    def capture(cls, turn_number: int, empires: List[Any], galaxy: Any) -> 'TurnStateSnapshot':
        """Serialize current state into a snapshot.

        Args:
            turn_number: Current turn number.
            empires: List of Empire objects to serialize.
            galaxy: Galaxy object to serialize.

        Returns:
            TurnStateSnapshot with serialized state.

        Raises:
            PersistenceException: If serialization fails (code=SNAPSHOT_FAILED).
        """
        try:
            empire_dicts = [e.to_dict() for e in empires]
            galaxy_dict = galaxy.to_dict()
        except Exception as e:  # Intentional broad catch: any to_dict() failure must become SNAPSHOT_FAILED PersistenceException for the turn rollback contract.
            raise PersistenceException(
                f"Failed to capture turn state snapshot: {e}",
                code=ErrorCode.SNAPSHOT_FAILED.value,
                context={"turn_number": turn_number, "original_error": str(e)}
            ) from e

        return cls(
            turn_number=turn_number,
            empire_dicts=empire_dicts,
            galaxy_dict=galaxy_dict,
            timestamp=time.time(),
        )

    def restore(self, session: Any) -> None:
        """Restore game state from this snapshot.

        Replaces session.galaxy and session.empires with deserialized
        objects from the snapshot data. Re-registers fleets with galaxy
        and resolves order references.

        Args:
            session: GameSession-like object with .galaxy, .empires, and
                .services.registries (public services accessor).
        """
        from game.strategy.data.galaxy import Galaxy
        from game.strategy.data.empire import Empire

        session.galaxy = Galaxy.from_dict(self.galaxy_dict)
        session.empires = [
            Empire.from_dict(
                d, galaxy=session.galaxy, registries=session.services.registries
            )
            for d in self.empire_dicts
        ]

        # Re-register fleets with galaxy
        for empire in session.empires:
            for fleet in empire.fleets:
                session.galaxy.register_fleet(fleet)

        # Resolve order references (fleet/planet targets)
        for empire in session.empires:
            for fleet in empire.fleets:
                fleet.resolve_order_references(session.galaxy, session.empires)

        logger.info(f"Turn {self.turn_number} state restored from snapshot.")

    def dump_crash_snapshot(
        self,
        save_path: str,
        error_info: Dict[str, Any],
    ) -> None:
        """Write crash snapshot to disk for debugging.

        Args:
            save_path: Directory to write crash file into.
            error_info: Dict with phase_name, tick, error details.
        """
        filename = (
            f"crash_turn{self.turn_number}"
            f"_tick{error_info.get('tick', '?')}"
            f"_phase_{error_info.get('phase_name', 'unknown')}.json"
        )
        filepath = os.path.join(save_path, filename)

        crash_data = {
            "turn_number": self.turn_number,
            "timestamp": self.timestamp,
            "error": error_info,
            "empire_count": len(self.empire_dicts),
            "system_count": len(self.galaxy_dict.get("systems", [])),
        }

        # PROJ-381 Phase 3 (ERR-02-005): route through save_json so the
        # write is atomic (temp file + rename) — a crash mid-write no
        # longer leaves a partial snapshot file on disk. save_json
        # handles parent-directory creation internally so the prior
        # os.makedirs call is redundant.
        if save_json(filepath, crash_data, indent=2):
            logger.info(f"Crash snapshot written to {filepath}")
        else:
            logger.error(f"Failed to write crash snapshot to {filepath}")
