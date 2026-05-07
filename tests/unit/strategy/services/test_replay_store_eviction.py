"""Unit tests for ReplayStore eviction edge cases."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from game.strategy.services.replay_store import ReplaySettings, ReplayStore


def _write_replay(path: Path, mtime: int) -> None:
    path.write_text("{}", encoding="utf-8")
    os.utime(path, (mtime, mtime))


class TestReplayStoreEviction:
    """Tests for ReplayStore._evict_excess error handling."""

    def test_evict_excess_continues_after_unlink_oserror(
        self, tmp_path, monkeypatch, caplog
    ):
        """A failed unlink logs the error and later excess files are still evicted."""
        store = ReplayStore(
            settings=ReplaySettings(max_replays_per_save=1),
            save_root=tmp_path,
        )
        replay_dir = tmp_path / "replays"
        replay_dir.mkdir()
        doomed = replay_dir / "replay_doomed.json"
        evictable = replay_dir / "replay_evictable.json"
        newest = replay_dir / "replay_newest.json"
        _write_replay(doomed, 1)
        _write_replay(evictable, 2)
        _write_replay(newest, 3)
        original_unlink = Path.unlink

        def flaky_unlink(path: Path, *args, **kwargs):
            if path == doomed:
                raise OSError("locked")
            return original_unlink(path, *args, **kwargs)

        monkeypatch.setattr(Path, "unlink", flaky_unlink)

        with caplog.at_level(
            logging.ERROR,
            logger="game.strategy.services.replay_store",
        ):
            deleted = store._evict_excess()

        assert deleted == 1
        assert doomed.exists()
        assert not evictable.exists()
        assert newest.exists()
        assert any(
            "ring buffer eviction failed" in record.getMessage()
            for record in caplog.records
        )
