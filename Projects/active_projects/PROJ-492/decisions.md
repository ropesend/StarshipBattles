# PROJ-492 Decisions Log

## Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-23 | Bundle HLP-002, HLP-004, HLP-005 in one project | Per Codex planning consult: all three are mechanical follow-through on canonical helpers that already exist; one project is enough. |
| 2026-05-23 | HLP-005 strategy: standardize on patching `Paths.SAVES_DIR`; rewrite `test_auto_save.py` to drop chdir | Codex consult evidence — production code creates new saves under `os.path.join(Paths.SAVES_DIR, save_name)` when `game_session.save_path` is absent (`game/strategy/systems/save_game_service.py:107-121`). `test_save_selection.py` already follows this contract. `test_auto_save.py` is the outlier. No production caller relies on cwd-relative save paths. |
| 2026-05-23 | HLP-005 strategy decision goes in decisions.md, not as a blocker | Per Codex consult — Phases 1 (HLP-002) and 2 (HLP-004) are independent of the tmpdir strategy. The decision is recorded and Phase 3 implements it; no need to block 1/2 on it. |
| 2026-05-23 | _make_fleet sweep uses 4-category triage (A/B/C/D) | Codex consult noted "remaining ~40 sites have signature/kwarg variation that requires per-site triage". The triage classification makes the work tractable without forcing semantically-different fleets into one shape. |
| 2026-05-23 | Reject dual-mode setup_tmpdir fixture | Codex consult: no evidence cwd-relative contract serves a real production caller need. Adding dual-mode doubles maintenance surface; can be added later if a real case emerges. |

## Permanently Deferred Items (NOT in PROJ-492)

| Item | Why deferred | Required user input |
|------|--------------|---------------------|
| `_make_fleet` Category D files (semantically different fleets) | Force-merging would obscure intent. Better to rename per-purpose locally than DRY them. | None — applied at per-file judgment during Phase 2 triage. |
| `MockPlanetType` consumers that need an enum member not in the canonical | If a new member is genuinely needed by tests, extend the canonical first. Otherwise leave the test using a name that won't conflict. | None — handled during Phase 1. |

## Reconciliation Notes (My Proposal vs Codex)

My initial proposal had PROJ-492 = "HLP mechanical sweeps (6.2, 6.4) + 6.5 strategy decision". Codex agreed but added two refinements:

1. **HLP-005 has a clear answer, not just a "decision needed"** — Codex provided file:line evidence that the production contract is `Paths.SAVES_DIR`, not cwd. My proposal would have left the decision open; Codex's evidence lets us pre-commit in `decisions.md`.

2. **The decision should not block 6.2 / 6.4** — my proposal was ambiguous about whether 6.5 was a blocking prereq. Codex clarified: bundle but execute independently. Reflected in plan.md Quick Status (3 separate phases).
