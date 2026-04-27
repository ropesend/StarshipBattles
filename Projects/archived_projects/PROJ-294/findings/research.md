# PROJ-294 Research Findings

## 1. Scripts Under Tools/ Importing from `game.*`

22 files under `Tools/` import from `game.*`. Only one is currently broken — `Tools/qa_observer/observer.py:222` (`from game.core.paths import Paths`). The others either:
- Run with cwd at the project root (no path issue), OR
- Already perform a `sys.path.insert(0, project_root)` bootstrap.

The observer is the only Tools script launched with `cwd=observer_dir` (see [qa_launcher.py:32](qa_launcher.py#L32)).

## 2. Established sys.path Bootstrap Patterns in Tools/

13 scripts under `Tools/` already use this pattern. Representative examples:

- [Tools/visual_test_galaxy/visual_test_galaxy.py:17](Tools/visual_test_galaxy/visual_test_galaxy.py#L17) — `sys.path.insert(0, str(_find_project_root()))`
- [Tools/analyze_dependency_graph/analyze_dependency_graph.py:26](Tools/analyze_dependency_graph/analyze_dependency_graph.py#L26) — `sys.path.insert(0, PROJECT_ROOT)`

All use parent-directory traversal from `__file__` to locate the project root. This is the canonical Tools/ pattern — observer.py should adopt it.

## 3. `.env` Resolution in observer.py

Lines 18–19 of [Tools/qa_observer/observer.py](Tools/qa_observer/observer.py#L18-L19):
```python
load_dotenv()
load_dotenv('.env')
```

The second call is **cwd-dependent** — loads `./.env` relative to current directory. Since `qa_launcher.py:32` sets `cwd=observer_dir`, observer's local `Tools/qa_observer/.env` loads correctly today. Any change that moves cwd to project root would break .env loading unless we also make .env loading file-relative.

**Recommendation:** keep cwd as observer_dir, add sys.path bootstrap. Don't touch the launcher.

## 4. Files in Tools/qa_observer/

- `observer.py` — imports `from game.core.paths` at line 222 (in a `finally` block, runs after main loop)
- `processor.py` — does not import from `game.*`
- `audio_monitor.py` — does not import from `game.*`
- `.env`, `.env.example`, `requirements.txt`, `README.md`, `session_data/`

Only observer.py needs the bootstrap.

## 5. Existing Tests

**None.** Grep for `test.*observer|test.*qa_launcher` returned 0 hits. The QA observer is a developer/QA tool — not in the standard test surface.

---

## Fix Strategy

Add `sys.path.insert(0, ...)` at top of `observer.py` (after stdlib imports, before any `game.*` import), following the canonical Tools/ pattern. Verification is manual: run `python qa_launcher.py`, exit the game, confirm no `ModuleNotFoundError`.
