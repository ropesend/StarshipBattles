# PROJ-105: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Project initialized | Starting point for Visual Regression Testing for UI Panels |
| 2026-02-10 | Panel-level snapshots (not full-screen) | Lightweight, fast, catches most UI regressions. Full-screen requires more complex mocking. |
| 2026-02-10 | Pre/post refactor script (not CI suite) | Purpose-built for the refactoring workflow. No baselines to maintain in CI. |
| 2026-02-10 | Tests live in `tests/visual_regression/` | New top-level directory, parallel to `tests/regression/`. Clean separation from existing tests. |
| 2026-02-10 | Baselines committed to git | Small PNGs (~5-50KB each). Ensures consistency on the same machine. No external storage needed. |
| 2026-02-10 | `--update-baselines` in local conftest only | Root conftest has no custom options currently. Local conftest keeps the flag scoped to visual tests. |
| 2026-02-10 | Use Pillow for image comparison (not numpy) | Already installed (v9.5.0). PIL.ImageChops.difference() sufficient. Avoids adding numpy dependency. |
| 2026-02-10 | Pixel threshold=2, change threshold=0.1% | Tolerates minor font antialiasing. 0.1% of 450x600=270,000 pixels = 270 allowed changed pixels. |
| 2026-02-10 | Collapsed view uses ShipDTO, expanded uses MagicMock | ship_stats_renderer.py expects domain objects for expanded view (resources.get_all_resources(), layers.get(), etc.). DTOs lack these methods. |
| 2026-02-10 | Accept `pygame.mouse.get_pos()` returning (0,0) in headless | Deterministic — always returns (0,0). SeekerMonitorPanel button renders in non-hover state consistently. |
| 2026-02-10 | Require `-n 1` for baseline updates | pytest.ini defaults to `-n 4`. Parallel writes to baseline directory would cause corruption. |
| 2026-02-10 | Start with 3 battle panels (5 snapshots) only | ShipStatsPanel (collapsed+expanded), SeekerMonitorPanel, BattleControlPanel (ongoing+victory). pygame_gui panels deferred. |
| 2026-02-10 | Add `Pillow>=9.0` to requirements.txt | Document the dependency even though already installed. |
