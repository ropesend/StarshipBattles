# PROJ-294: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

The QA observer is a developer/QA-only tool spawned as a subprocess by [qa_launcher.py](../../../qa_launcher.py). It records audio + screenshots during a play session, then in its `finally` block (after the user quits the game) copies the game's log files into the session output directory.

**The bug:** The `from game.core.paths import Paths` happens at line 222, inside the `finally` block — meaning the import error only manifests *after* the player quits the game, hidden from view during normal play. The `finally` block silently fails: no log files get copied, but the launcher exits 0 because the failure isn't propagated.

**Root cause:** [qa_launcher.py:32](../../../qa_launcher.py#L32) launches observer with `cwd=observer_dir` (`Tools/qa_observer/`) so that observer's local `.env` resolves correctly. Python doesn't put the project root on `sys.path` automatically — and the project root is two parents up from the observer.

## Swarm Findings Summary

Single Explore agent's findings, full report in [findings/research.md](findings/research.md). Highlights:

### Architecture

- 22 scripts under `Tools/` import from `game.*`. 13 of them already use a project-root `sys.path.insert` bootstrap.
- `observer.py` is the only Tools script that crashes — it's also the only one launched with cwd ≠ project root.

### Key Patterns to Reuse

- **Project-root sys.path bootstrap**: [Tools/visual_test_galaxy/visual_test_galaxy.py:17](../../../Tools/visual_test_galaxy/visual_test_galaxy.py#L17) and [Tools/analyze_dependency_graph/analyze_dependency_graph.py:26](../../../Tools/analyze_dependency_graph/analyze_dependency_graph.py#L26) — both use `Path(__file__).resolve().parents[N]` to compute root, then `sys.path.insert(0, ...)`.

### Dependencies & Risks

1. **Risk: silently breaking `.env` loading** — `load_dotenv('.env')` (line 19) is cwd-relative. Mitigation: do NOT change cwd in the launcher. Add the bootstrap inside observer.py instead, where it touches only `sys.path`.
2. **Risk: stale `_PROJECT_ROOT` if Tools/qa_observer/ is moved** — `parents[2]` assumes the file lives at `<root>/Tools/qa_observer/observer.py`. Mitigation: add a brief comment indicating the assumed depth so a future mover catches it.

### Opportunities Discovered

- The other 12 Tools/ scripts importing `game.*` could be audited for the same latent bug — but per research, only this one is reached via a `cwd != project_root` launcher. **Out of scope** for this project; no urgent need.

## Design Decisions

See [decisions.md](decisions.md) for full rationale. Key choice: **bootstrap inside observer.py**, not inside the launcher.
