# PROJ-374 — Originating profile evidence

**Captured:** 2026-05-05 — pyinstrument 5.1.2, sampling interval 1ms.
**Repro:** Launched the game under `python Tools/profile_game/profile_game.py`,
opened the build queue for the home planet 3 times in a row, then quit
normally. The strategy-screen grid was visible throughout the 58s session.
**Session:** 57.80s wall, 38,673 samples.

The original HTML report (22 MB) lives in
`AgentCoordination/Scratchpad/reports/profiles/profile_20260505T191424.html`
(gitignored). The session JSON was extracted to
`AgentCoordination/Scratchpad/tmp/session.json` for analysis.

---

## Side-finding from the build-queue profile

This project is a side-finding, not the original target of the profile run.

`_draw_grid` in [strategy_renderer.py:193](../../../../game/ui/screens/strategy_renderer.py#L193) → `draw_grid` in
[strategy_render/grid.py:12](../../../../game/ui/screens/strategy_render/grid.py#L12) consumed:

| Function | Cumulative time | % of session |
|----------|----------------:|-------------:|
| `_draw_grid` | 9.14s | 15.8% |
| `draw_grid` | 9.14s | 15.8% |

The grid is rasterized **every frame** from the strategy renderer's `draw`
([strategy_renderer.py:260](../../../../game/ui/screens/strategy_renderer.py#L260)), even while a modal overlay (the build queue)
is open and the underlying camera/zoom does not change. Geometry is a pure
function of camera offset, zoom, and viewport size — none of which changed
during the session — so the bitmap is regenerable from the same inputs every
frame.

This is the textbook "cache the render output, invalidate on input change"
pattern. Implementing it should reclaim most of those 9.14s, dropping
per-frame cost on the strategy screen and any overlay that doesn't fully
occlude it.

---

## What this profile does NOT cover

- Whether the grid is the ONLY per-frame cost in the strategy renderer that
  bears caching. Other elements (system markers, ship icons) may also be
  re-drawn unnecessarily — out of scope for this project.
- Whether visual regressions are likely under caching: needs explicit
  enumeration of every input that affects the grid bitmap.

---

## Success criterion

After landing the cache, a follow-up pyinstrument capture of a similar 58s
strategy-screen session should show `_draw_grid` cumulative time drop by
≥80% (i.e. from ~9.14s to under ~1.8s, dominated by the rare camera-move
re-renders).
