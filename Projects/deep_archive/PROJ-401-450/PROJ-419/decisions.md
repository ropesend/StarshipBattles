# PROJ-419: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-13 | Project initialized | Starting point for Legacy removal — light cleanup of stale comments and dead imports (2026-05-13) |
| 2026-05-13 | Bundled findings from `2026-05-13_194106_legacy-audit` by removal cluster `light_cleanup` per user direction | Bundling driven by removal cluster (one project per system being eradicated) rather than severity to maximize deletion-PR coherence; full bundling discussion in findings/bundling_decisions.md |
| 2026-05-14 | PROJ-XX placeholder → PROJ-231, reworded to `PROJ-231 star image variant support` | Codex consult confirmed PROJ-231 via `star_image_registry.py:8` label and introducing commit 4fa6b08bc. "Star Expansion" wording dropped in favour of precise phrase matching code reality. |
| 2026-05-14 | pygame_gui local imports confirmed dead despite no module-level counterpart | Codex verified none of the three function bodies use any pygame_gui name. Other pygame_gui calls in the file use separate `import pygame_gui.windows` statements unaffected by this deletion. |
| 2026-05-14 | screen_router.py:438-439 RaceSetupScreen shim import excluded from this PR | Codex identified it as a real caller migration (not a dead import), with test monkeypatching the legacy path. Belongs in a separate shim-retirement task. |
