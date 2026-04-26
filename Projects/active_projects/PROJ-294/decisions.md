# PROJ-294: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Starting point for QA Observer Path Bootstrap (ModuleNotFoundError fix) |
| 2026-04-26 | Fix in observer.py, NOT in qa_launcher.py | Launcher's `cwd=observer_dir` is required for `.env` resolution. Modifying cwd would force a separate refactor of `load_dotenv('.env')` to be file-relative. Self-bootstrapping inside observer.py is more local, more robust, and follows the established Tools/ pattern (13 prior scripts). |
| 2026-04-26 | Use `Path(__file__).resolve().parents[2]` for project root | Standard Tools/ pattern. Avoids relying on `os.path` string manipulation. Works regardless of cwd or symlinks. |
| 2026-04-26 | No automated tests | The observer is a developer tool with no existing test surface. Verification is manual smoke via `python qa_launcher.py`. Adding tests would require mocking pyaudio + watchdog + subprocess machinery — disproportionate for a 4-line bootstrap fix. |
| 2026-04-26 | Don't audit the other 12 Tools/ scripts that import game.* | Per research, only observer.py is launched with a non-root cwd, so only observer.py crashes. The others either use the bootstrap already (13 scripts confirmed) or run from project root. Scope creep risk; defer to a separate audit if/when one is launched. |
