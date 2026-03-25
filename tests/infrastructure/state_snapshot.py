"""State snapshot and verification utilities for QA sessions (PROJ-223 Phase 6).

Provides tools to snapshot game state, compare snapshots, and verify
save/load round-trip fidelity during live QA sessions.
"""

import copy
import os
import time
from dataclasses import dataclass
from typing import List, Optional, Set

from tests.infrastructure.deep_compare import ComparisonResult, deep_compare


@dataclass
class VerificationReport:
    """Result of a save/load round-trip verification."""
    passed: bool
    differences: List[ComparisonResult]
    save_time_ms: float = 0.0
    load_time_ms: float = 0.0
    save_size_bytes: int = 0


def snapshot_game_state(game_session) -> dict:
    """Take a deep-copy snapshot of the game session's serialized state.

    Args:
        game_session: GameSession instance.

    Returns:
        Deep copy of game_session.to_dict().
    """
    return copy.deepcopy(game_session.to_dict())


def compare_game_states(
    before: dict,
    after: dict,
    ignore_fields: Optional[Set[str]] = None,
) -> List[ComparisonResult]:
    """Compare two game state snapshots and return differences.

    Automatically ignores known non-deterministic fields (storm hex_offsets).

    Args:
        before: Snapshot before operation.
        after: Snapshot after operation.
        ignore_fields: Additional dot-separated paths to skip.

    Returns:
        List of ComparisonResult for each difference.
    """
    all_ignore = set(ignore_fields) if ignore_fields else set()

    # Auto-ignore save_path (changes on each save)
    all_ignore.add("save_path")

    # Auto-ignore storm hex_offsets (frozenset → list ordering)
    for i, sys_entry in enumerate(before.get('galaxy', {}).get('systems', [])):
        system = sys_entry.get('system', {})
        for j, _ in enumerate(system.get('storms', [])):
            all_ignore.add(f"galaxy.systems[{i}].system.storms[{j}].hex_offsets")

    return deep_compare(before, after, ignore_fields=all_ignore)


class SaveLoadVerifier:
    """Verifies save/load round-trip fidelity for QA sessions."""

    def verify_round_trip(
        self,
        game_session,
        save_path: str,
        ignore_fields: Optional[Set[str]] = None,
    ) -> VerificationReport:
        """Perform a full save/load/compare cycle.

        1. Snapshot pre-save state
        2. Save via SaveGameService
        3. Load via SaveGameService
        4. Snapshot post-load state
        5. Compare and return report

        Args:
            game_session: GameSession to verify.
            save_path: Directory for save files.
            ignore_fields: Extra fields to ignore in comparison.

        Returns:
            VerificationReport with pass/fail, differences, and stats.
        """
        from game.strategy.systems.save_game_service import SaveGameService

        # 1. Snapshot before
        before = snapshot_game_state(game_session)

        # 2. Save with timing
        game_session.save_path = os.path.join(save_path, "verify_roundtrip")
        t0 = time.perf_counter()
        success, msg, actual_save_path = SaveGameService.save_game(game_session)
        save_time_ms = (time.perf_counter() - t0) * 1000

        if not success:
            return VerificationReport(
                passed=False,
                differences=[ComparisonResult("save", None, None, f"Save failed: {msg}")],
                save_time_ms=save_time_ms,
            )

        # Measure save size
        save_size = 0
        for root, dirs, files in os.walk(actual_save_path):
            for f in files:
                save_size += os.path.getsize(os.path.join(root, f))

        # 3. Load with timing
        t1 = time.perf_counter()
        loaded, msg = SaveGameService.load_game(actual_save_path)
        load_time_ms = (time.perf_counter() - t1) * 1000

        if loaded is None:
            return VerificationReport(
                passed=False,
                differences=[ComparisonResult("load", None, None, f"Load failed: {msg}")],
                save_time_ms=save_time_ms,
                load_time_ms=load_time_ms,
                save_size_bytes=save_size,
            )

        # 4. Snapshot after
        after = snapshot_game_state(loaded)

        # 5. Compare
        diffs = compare_game_states(before, after, ignore_fields=ignore_fields)

        return VerificationReport(
            passed=(len(diffs) == 0),
            differences=diffs,
            save_time_ms=save_time_ms,
            load_time_ms=load_time_ms,
            save_size_bytes=save_size,
        )
