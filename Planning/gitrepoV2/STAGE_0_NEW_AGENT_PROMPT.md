# Stage 0 Preparation — New Agent Onboarding Prompt

> Hand this to a fresh Claude Code session when you're ready to start
> V2-repo preparation work. The prompt assumes Claude Code conventions
> (`TodoWrite`, `AskUserQuestion`, `CLAUDE.md`); adapt for Codex /
> OpenCode by rephrasing those surfaces.

---

## Your role

You are picking up the **Stage 0 repository migration** for the Starship Battles project. The user is preparing to migrate the codebase from `ropesend/StarshipBattles` to a new clean repo called `ropesend/StellarHegemony`. Your job is **preparation work only** — generating the artifacts, decisions, and validations the user needs to execute the migration themselves. **You do not create the V2 GitHub repo, push to any remote, archive the V1 repo, or rewrite V1 history.** Those actions are user-triggered.

You are working in `c:/Dev2/StarshipBattles` on Windows 11. Work interactively and surface decisions via `AskUserQuestion` rather than guessing.

## Read order

Read these in this order:

1. `AGENTS.md` — non-negotiable repo rules.
2. `CLAUDE.md` — Claude Code-specific norms over AGENTS.md.
3. `docs/README.md` — doc routing.
4. `docs/01_ARCHITECTURE.md` — layers + dependency direction.
5. `docs/02_PATTERNS.md` — repeated patterns.
6. `docs/03_CONVENTIONS.md` — naming, organization, test rules. The **"Image Asset Derivatives — canonical pattern"** section is the contract for the asset-derivative model.
7. `Planning/README.md` — staged-planning overview.
8. `Planning/gitrepoV2/STAGE_0_PLAN.md` — the canonical Stage 0 plan. Read the "Pre-Migration Cleanup Complete (2026-05-27)" section first.
9. `Planning/gitrepoV2/STAGE_0_DECISIONS.md` — settled vs proposed decisions. **Items marked `proposed` are still open** and need user confirmation before any irreversible Stage 0 action.
10. `Planning/gitrepoV2/DETAILED_MIGRATION_PLAN.md` — phase walkthrough; the bottom "Current status" block lists the cleanup commits that already shipped.

## Conflict resolution

When sources disagree:

- **`AGENTS.md`** wins for non-negotiable process rules (TDD, root-cause fixes, etc.).
- **The live tree wins for factual state.** `game/core/paths.py` is the single source of truth for asset paths; `assets/asset_manifest.json` is the runtime catalog. Comments / docstrings / older Stage 0 prose are explanatory, not authoritative.
- **`STAGE_0_DECISIONS.md`** wins over older Stage 0 plan prose for open-decision status and LFS policy. `STAGE_0_PLAN.md` Phase 5 still contains an extension-scoped `*.png filter=lfs` LFS draft that is **superseded** by the path-scoped policy in `STAGE_0_DECISIONS.md`. Use path-scoped LFS.

## Ignore these for Stage 0 work

- **`Planning/**/CURRENT_STATE.md`** — intentionally-empty scaffolds, not authoritative audits.
- **Auxiliary expansion notes** for Stages 2 / 2.5 / 3 (`STAGE_2_REVIEW_AND_EXPANSION_NOTES.md`, `STAGE_2_5_INTEGRATION_NOTES.md`, `RUST_MIGRATION_UI_GUIDE.md`).
- **Stages 1–8 design docs** (`Planning/01_*/`, `02_*/`, …, `08_*/` `README.md`s). Long-range gameplay/architecture roadmap; *not* Stage 0 input.
- **Frozen archives:** `Projects/deep_archive/`, `Projects/archived_projects/`, `AgentCoordination/legacy_tickets/`, `Reviews/results/_archive_*`, `_marked_for_deletion_*`, `tracking-assets/logs/`.

## What's already done — do NOT redo

The recent asset reorganization is finished on `main`. The bottom "Current status" block of `Planning/gitrepoV2/DETAILED_MIGRATION_PLAN.md` lists the exact commits. **Read that block instead of relying on per-row SHAs in this prompt** — branch-local SHAs are fragile.

The durable facts you should know:

- Asset paths are uniformly **snake_case under `assets/images/`**. No `Images/`, no `ShipThemes/`, no `Stellar Objects/`, no `Sphere world`, no `Warp Points`, no `Flags/Processed/`.
- `stellar_objects/` grouping is **flattened**: planets, stars, sphere_world, warp_points, nebulae, asteroids are direct children of `assets/images/`.
- A generalized **master+regenerate derivative pipeline** lives at `game/assets/image_derivatives.py` with per-family wrappers for components / flags / stars / planets. Each family stores only its master size in source control; sibling sizes regenerate at startup. Master sizes are family-specific: 1024 for components / flags / stars; 2048 for planets.
- `app_bootstrap.py` calls each family's `ensure_*_derivatives()` in sequence before sprite loading.
- ~1 GB of regenerable / non-runtime content was removed from the V1 working tree. The `.git` pack history still carries the bloat — which is precisely why Stage 0 (clean cutover) remains worthwhile.

**Things you must not re-introduce:**

- PascalCase / Title-Case-With-Spaces asset folder names.
- The `stellar_objects/` grouping layer.
- The `flags/Processed/` nesting.
- A central `asset_cache/scaled_images/` cache scheme. **That scheme was never implemented.** Per-family in-place is what shipped.
- Treating generated derivative size folders as canonical tracked content.

### Past consult records worth reading

In `AgentCoordination/Scratchpad/Consult/`:

- `20260524T193500Z_stage0-strategy/response.md`
- `20260526T180000Z_asset-org/response.md`
- `20260527T100000Z_docs-planning-stage0-prompt/response.md`
- `20260527T103000Z_stage0-prompt-review/response.md` (this very prompt's review)

## Proposed rows from STAGE_0_DECISIONS.md (still open)

Items currently `proposed`. Re-confirm (or revise) with the user before any Phase 10+ irreversible action. Group into 3–4 focused `AskUserQuestion` calls; don't dump all at once.

- **V2 repository name.** Proposed: `StellarHegemony`. Worth one more sanity check — once chosen, harder to walk back.
- **Initial visibility.** Proposed: private.
- **External artifact vault provider.** Proposed: Google Drive.
- **Git LFS policy.** Proposed: **path-scoped** LFS for canonical runtime image/audio masters. (Not extension-scoped — `*.png filter=lfs` would catch derivatives.)
- **Issue migration policy.** Proposed: resolve/archive most old GitHub issues first, minimal migration into V2.
- **Old repo handling.** Proposed: leave unarchived until V2 is validated; archive only after explicit user approval.

## Additional scope questions from the docs audit

Not in `STAGE_0_DECISIONS.md` yet; surface to the user when relevant:

- **GitHub plan tier for V2.** Free/Pro (10 GiB LFS storage + bandwidth) vs Team/Enterprise (250 GiB). Free/Pro fits the current curated set but leaves little headroom.
- **Curation boundaries:** which `Projects/active_projects/` PROJ-XXX folders make the V2 cut; which `AgentCoordination/protocols/` files are still load-bearing; whether any non-runtime art deserves a private *asset* repo rather than Google Drive only.

## Your concrete preparation tasks

Do these in roughly this order. Each is reviewable in isolation; commit small. Plan each before executing.

### A. Re-baseline (one focused session, ~30 minutes)

1. Capture current `.git` pack metrics and source commit SHA in a new tracked file `Planning/gitrepoV2/MIGRATION_SOURCE_SNAPSHOT.md`:
   - `git rev-parse HEAD`
   - `git count-objects -vH`
   - `git status --short`
2. Re-run the asset inventory analysis. The prior subagent report at `.agent_reports/stage0_inventory/inventory_report.md` predates the cleanup and overstates sizes by roughly 1 GB. Write a small **delta** addendum or a fresh `inventory_post_cleanup.md` showing current numbers.
3. Verification grep: confirm zero remaining stale PascalCase asset path references in live tracked sources that matter for migration decisions — production code, tests, tools, repo-root config files (especially `.gitignore`), and the active Stage 0 planning docs. If anything turns up, it's a leftover bug — fix as a small standalone commit before continuing.

### B. Draft the V2 hygiene files

These are tracked Planning artifacts that the user reviews before any V2-import action.

1. **`Planning/gitrepoV2/V2_GITIGNORE_DRAFT.md`** — proposed V2 `.gitignore`. Start from the live V1 `.gitignore` (already well-tuned post-reorg). Drop entries that target frozen-archive paths that won't exist in V2.
2. **`Planning/gitrepoV2/V2_GITATTRIBUTES_DRAFT.md`** — path-scoped LFS rules. List the specific master-size paths under `assets/images/` that should be LFS-tracked. Do *not* use extension-scoped `*.png filter=lfs` — that catches derivatives.
3. **`Planning/gitrepoV2/MIGRATION_CLASSIFICATION.md`** — for every top-level directory in V1, classify as: `IMPORT_GIT` / `IMPORT_LFS` / `RELEASE_ARTIFACT` / `VAULT` / `SKIP`.
4. **`Planning/gitrepoV2/EXTERNAL_ARTIFACT_POLICY.md`** — finalize the Google Drive vault layout (see `STAGE_0_PLAN.md` Phase 6) and the list of what gets vaulted.
5. **`Planning/gitrepoV2/V2_FOLDER_STRUCTURE.md`** — the target V2 tree, written as a verbatim copy of the current cleaned V1 shape.

### C. Identify the V2 import scope

Generate `Planning/gitrepoV2/V2_IMPORT_CHECKLIST.md`:

- **Copy verbatim:** everything under `game/`, `tests/`, `data/`, `docs/`, and the live parts of `Tools/`.
- **Copy with curation:** `Planning/` (drop empty `CURRENT_STATE.md` scaffolds unless they have real content), `Projects/active_projects/` (current PROJ-XXX folders only), `AgentCoordination/protocols/`, `.github/` configs if they exist. For `.claude/`, `.agents/`, `.codex/`, `.opencode/`: copy reusable instructions/skills, not session state.
- **Do not copy:** `Projects/deep_archive/`, `Projects/archived_projects/`, `AgentCoordination/legacy_tickets/`, `AgentCoordination/Scratchpad/`, `Reviews/results/_archive_*`, anything under `output/`, `_marked_for_deletion_*`, `tracking-assets/logs/`, `combat_lab/test_history/`, `.agent_reports/`, `.testmondata*`, `.coverage*`, `.pytest_cache/`.
- The V1 `.git` pack history (~16 GB historical) is deliberately not preserved. Clean cutover.

### D. Decisions to surface to the user

For each open item (proposed in `STAGE_0_DECISIONS.md` plus the audit scope questions), draft an `AskUserQuestion` with the recommended option labeled "(Recommended)" plus 2–3 alternatives. Group into 3–4 focused questions.

## What you are NOT allowed to do

- **Do not create the V2 GitHub repo.** `gh repo create` is forbidden. The user creates it when ready.
- **Do not push to any remote, force-push, or `git lfs migrate` against the live tree.**
- **Do not archive the V1 repo on GitHub.** That decision is gated on V2 validation + explicit user approval.
- **Do not delete tracked content from V1.** Further deletions need the user's explicit OK.
- **Do not rewrite history with `git filter-repo`, BFG, or any other tool** against the live working tree. If the user wants the optional "filter-repo experiment," do it in a separate clone outside this checkout.
- **Do not skip the strict-TDD rule** when writing or modifying code. Any code change needs a failing test first.
- **Do not edit frozen archives.**
- **Do not modify the recent asset reorganization commits.** They are merged.
- **Do not redesign derivative caching.** The per-family in-place model is shipped and tested.
- **Do not start Stage 1+ architecture work.** Stage 0 is repo hygiene only.

## Working norms

- Use `TodoWrite` to track multi-step prep work. Mark items completed as you go.
- Surface decisions via `AskUserQuestion`. Recommended option first, labeled "(Recommended)".
- Commits are cheap; group related prep work into one commit each.
- For any analysis that takes >2 minutes of agent time, write it as a tracked Planning doc — don't lose it in conversation.
- If you discover anything wrong with the post-reorg state (a forgotten reference, a broken test, etc.), fix it as a small standalone commit before continuing. Don't bundle into the V2-prep work.
- **Discovered-issues inbox:** if you notice out-of-scope issues during Stage 0 inventory work (a real bug, a security smell, a perf pathology, dead code, a lying docstring, a test gap), log via `/claude-di-log` and keep going — don't detour. Full rules: `AgentCoordination/discovered_issues/README.md`.
- If `docs/` and the live tree disagree on a path, the live tree wins — and surface the doc bug to the user.

## Success criteria

You're done when all of the following exist as committed planning artifacts:

- `Planning/gitrepoV2/MIGRATION_SOURCE_SNAPSHOT.md` with source SHA + `.git` pack metrics + working-tree snapshot.
- `Planning/gitrepoV2/V2_GITIGNORE_DRAFT.md`.
- `Planning/gitrepoV2/V2_GITATTRIBUTES_DRAFT.md` with path-scoped LFS rules.
- `Planning/gitrepoV2/MIGRATION_CLASSIFICATION.md`.
- `Planning/gitrepoV2/EXTERNAL_ARTIFACT_POLICY.md`.
- `Planning/gitrepoV2/V2_FOLDER_STRUCTURE.md`.
- `Planning/gitrepoV2/V2_IMPORT_CHECKLIST.md`.
- A refreshed `Planning/gitrepoV2/STAGE_0_DECISIONS.md` where every previously-`proposed` row has either become `settled` (user confirmed) or stays `proposed` with an explicit reason and a question logged for the user.

After that, the user is ready to execute Phase 10 (create the V2 GitHub repo) and the import phases themselves.

## First turn

1. Confirm you've read the **Read order** list, the **Conflict resolution** rules, and the **Ignore these** list.
2. Run the three non-mutating baseline commands to ground yourself: `git status --short`, `git rev-parse HEAD`, `git count-objects -vH`. Capture the output.
3. Then ask the user: **"Should I start with task A (re-baseline artifact + verification grep) or do you want to settle any of the `proposed` decisions first?"** Don't begin generating Planning artifacts until that's answered.
