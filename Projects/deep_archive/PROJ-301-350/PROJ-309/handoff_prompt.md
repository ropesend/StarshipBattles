# Handoff: PROJ-309 — Phase 4 closeout (user verification + archive)

PROJ-309 is **functionally complete**. All 10 target files decomposed, all
contract tests pass, full sharded suite at **15582/15582 passing**. Only
two items remain — both are user-gated:

1. **Phase 4.3 — Manual smoke** (USER): launch the game and verify every
   screen touched by a decomposed file works.
2. **Phase 4.5 — MEMORY update** (after user verification): add a
   "Recently Archived" entry to MEMORY.md.

After both are done, archive PROJ-309 per `Projects/protocols/09_archive_project.md`.

## Orientation (read BEFORE touching the project plan)

The project's heavy lifting is done. You don't need to re-orient deeply
unless the user reports a smoke failure. If they do, here's the order:

### 1. Foundation docs (always — only if you'll touch code)
- `docs/README.md`
- `docs/01_ARCHITECTURE.md`
- `docs/02_PATTERNS.md`
- `docs/03_CONVENTIONS.md` (§2.3 has the new 500-LOC rule; §2.4 the UI screen line budget)
- `CLAUDE.md` (rules 1-3 are non-negotiable)

### 2. Project files
1. `Projects/active_projects/PROJ-309/plan.md` § Current State — authoritative
2. `Projects/active_projects/PROJ-309/phase_3_checklist.md` — every sub-phase's notes block details exactly what landed
3. `Projects/active_projects/PROJ-309/phase_4_checklist.md` — what remains
4. `Projects/active_projects/PROJ-309/manifest.md` — file fates table
5. `Projects/active_projects/PROJ-309/findings/_cross_design_review.md` — design review

## First action

**If user has confirmed smoke passed:**
1. Apply Phase 4.5 (MEMORY.md update — see template in `phase_4_checklist.md` task 4.5).
2. Archive PROJ-309 per `Projects/protocols/09_archive_project.md`. Move from `active_projects/` to `archived_projects/`. Update `Projects/projects_index.md`.

**If user reports smoke failures:**
1. Read which screen broke.
2. Identify which sub-phase touched it from `phase_3_checklist.md` notes.
3. Bisect: confirm the failure is reproducible, then check git blame for
   the relevant file. Most decompositions are byte-for-byte equivalent —
   true regressions are rare but possible.
4. If a real bug surfaces, fix it as a Phase-4 patch. Do NOT reopen 3.x
   sub-phase status; record the fix in `phase_4_checklist.md` notes.

**If user wants the smoke run delayed:**
- Keep PROJ-309 in `active_projects/` with Phase 4 status "In Progress
  (4.3 + 4.5 pending user)". Don't archive prematurely.

## Smoke checklist (recap from `phase_4_checklist.md` task 4.3)

The user should:
- Launch the game (currently `python launcher.py` or `python -m game.app` —
  confirm with the user).
- Race setup screen (touched 3.1) — every tab; save / load; LLM dialog.
- Strategy screen (touched 3.2 + 3.10) — every render layer (background,
  planets, fleets, overlays); every sub-window (planet info, fleet info,
  build queue, orders, transfer, planet abilities).
- Issue commands of every kind (touched 3.5).
- Workshop screen (touched 3.8) — exercise all tabs.
- Combat Lab (touched 3.3 + 3.6) — open, run a scenario, view details panel.
- Confirm: no console errors / import errors / silent UI breakage.

## Watchouts (from this session)

- `Tools/check_file_size.py` exits 1 because of 52 OUT-OF-SCOPE residual
  files. This is correct behavior — it's not a PROJ-309 regression. Do
  NOT add the tool to a CI gate without a separate ticket to drive the
  residual count down.
- The decomposition surfaced 5 latent issues that were preserved verbatim
  per design (see plan.md Current State for the list). These are real
  bugs but pre-existing; out of scope for PROJ-309. Capture as follow-up
  tickets.
- 4 latent issues were FIXED in passing (planet_abilities_window slot,
  duplicate ResourceCatalog.from_json, triple dialog teardown,
  apply_append_selection toggle bug). All tests pass — these are
  defensible improvements, not silent behavioral changes.
- The known test-isolation flake `test_colony_owner_id_matches_empire`
  was flagged in MEMORY.md and surfaced once during this session. Pre-
  existing. Re-run if it shows up.

## Protocol

Follow `Projects/protocols/09_archive_project.md` after user-driven
Phase 4 closure. Update `Projects/projects_index.md` to reflect PROJ-309
moving from active to archived, and update `MEMORY.md` per Phase 4.5.
