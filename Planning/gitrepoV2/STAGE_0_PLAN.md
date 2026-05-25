# Stage 0 Plan — GitRepoV2 / Stellar Hegemony Repository Migration

Stage 0 is the prerequisite repository and workflow migration stage for the Starship Battles / Stellar Hegemony project.

The purpose is to create a clean canonical V2 repository named `StellarHegemony` before major Stage 1 architectural implementation begins.

This plan is intended for future agents and human continuation. It documents the user-approved direction and the practical execution sequence. Future agents should expand individual tasks, add implementation checklists, and update status files as work proceeds.

## Stage 0 summary

> **Status note (2026-05-24):** All "proposed direction" rows below remain open pending final user confirmation. See `STAGE_0_DECISIONS.md` for the canonical status of each item. Do not treat values as binding until the user confirms.

| Field | Proposed direction | Status |
|---|---|---|
| Stage name | GitRepoV2 / Stellar Hegemony repository migration | settled |
| Stage number | 0 | settled |
| New repository | `ropesend/StellarHegemony` | proposed |
| Initial visibility | Private | proposed |
| Old repository | `ropesend/StarshipBattles` | settled |
| Old repository status during migration | Keep unarchived and available | settled |
| Old repository status after validation | Archive only after user approval | settled |
| External artifact provider | Prefer Google Drive | proposed |
| Git LFS policy | Use for canonical runtime image/audio assets | proposed |
| Generated scaled assets | Local cache only; ignored by Git | proposed |

## Why this is Stage 0

The existing numbered planning stages make large architectural changes to the game. Stage 1 separates authoritative game state from player-visible state. Stage 2 introduces server-style player turn packages and command batches. Later stages build research, AI, tactical persistence, multiplayer, and eventual language migration on those boundaries.

Those changes should happen in a clean canonical repository rather than in a known-bloated historical repository.

Stage 0 therefore comes before Stage 1 implementation. It does not replace Stage 1. It prepares the repository and workflow so Stage 1 and later work can proceed cleanly.

Design discussion and planning can continue during Stage 0. Large architecture-changing implementation should wait until the new repository is created, imported, and validated.

## Core principle

This is a repository hygiene migration, not a game rewrite.

Do not rewrite gameplay systems as part of Stage 0 unless a tiny compatibility or path fix is required to make the migrated repo run. Do not use the migration as an excuse to redesign source architecture, game rules, UI systems, combat, research, or AI.

The goal is to preserve the current working source/design state while removing repository bloat, separating external artifacts, clarifying asset policy, and improving multi-machine development.

## Proposed direction (still open)

The following items remain **proposed** as of 2026-05-24. Re-confirm with the user before executing any irreversible Stage 0 phase that depends on them.

1. The V2 repository name is `StellarHegemony`. *(proposed — name itself is worth re-examining; downstream URLs, branding, and documentation depend on it)*
2. The V2 repository should initially be private. *(proposed)*
3. The old `StarshipBattles` repository should remain unarchived until V2 is validated. *(settled)*
4. The old repository may be archived later, but only after user approval. *(settled)*
5. Google Drive is the preferred external artifact vault provider, provided the active Git repo is not stored inside Google Drive. *(proposed)*
6. The user intends to resolve/archive most old GitHub issues before migration. Expect little or no issue migration unless active high-value issues remain. *(proposed)*
7. Canonical runtime image and audio assets should be tracked with Git LFS. *(proposed)*
8. Scaled versions of images should not be stored in Git. Store originals in Git LFS and generate scaled versions locally. *(proposed)*
9. Local scaled-image caches should be retained on each machine and regenerated only if the source original changes. *(proposed)*

See `STAGE_0_DECISIONS.md` for the canonical status of each item. When the user confirms any of these, update both files at the same time.

## Non-goals

Stage 0 must not include:

- Gameplay rewrite.
- Major architecture rewrite.
- Deleting the old repository.
- Rewriting old repository history.
- Force pushing or destructive cleanup of the old repository.
- Blindly migrating all historical archives.
- Storing raw agent transcripts in Git.
- Storing generated previews or scaled images in Git.
- Storing the active Git repo inside a cloud-sync folder.
- Using Git LFS as a dumping ground for transient/generated files.
- Migrating commercial fonts or third-party assets without license review.

## Recommended execution phases

The detailed original migration plan remains in `DETAILED_MIGRATION_PLAN.md`. This Stage 0 plan summarizes the intended execution order and adds the user-approved decisions.

### Phase 0 — Safety and scope freeze

Objective: prevent loss of source, issues, artifacts, or historical context.

Required actions:

1. Confirm source repo: `ropesend/StarshipBattles`.
2. Confirm default branch: `main`.
3. Record the current source commit SHA.
4. Confirm the user still wants a new clean V2 repo, not an in-place history rewrite.
5. Make a full local clone or backup before large file movement.
6. Do not delete, archive, rename, force-push, or rewrite old repo history.

Deliverables:

- `MIGRATION_LOG.md`
- Source commit SHA recorded.
- Backup location recorded.

Exit criteria:

- Old repo is safe.
- Current source snapshot is known.
- No destructive operation has occurred.

### Phase 1 — Repository inventory

Objective: know what exists before deciding what moves.

Required inventory:

- Top-level directory list.
- Tracked file list.
- Largest tracked files.
- Extension summary.
- Largest directories by tracked file size.
- Candidate generated/local/transient files.
- Candidate LFS files.
- Candidate external-artifact files.

Deliverables:

- `MIGRATION_INVENTORY_SUMMARY.md`
- Optional raw inventory files under `Planning/gitrepoV2/` or external vault.

Exit criteria:

- Every large directory and large file can be explained.
- Obvious exclusions and LFS candidates are identified.

### Phase 2 — Classify repository content

Objective: decide what goes into V2, LFS, external storage, issues/releases, or nowhere.

Use these buckets:

| Bucket | Meaning |
|---|---|
| A | Migrate as normal Git |
| B | Migrate through Git LFS |
| C | Move to GitHub Issues or Releases |
| D | Move to external artifact vault |
| E | Do not migrate |

Deliverable:

- `MIGRATION_CLASSIFICATION.md`

Required columns:

```text
Path | Bucket | Reason | V2 destination | Notes | Decision status
```

Exit criteria:

- Every top-level directory is classified.
- Every large directory is classified.
- Every large file is classified.
- User-decision items are clearly listed.

### Phase 3 — Decide V2 repository structure

Objective: define the target structure before import.

Recommended V2 layout:

```text
StellarHegemony/
  game/
  tests/
  data/
  docs/
  Planning/
    README.md
    current_design/
    gitrepoV2/
  Projects/
    active_projects/
    README.md
    index.md
  assets/
    Images/
    Audio/
    Fonts/
  Tools/
    setup/
    migration/
    qa/
    assets/
  AgentCoordination/
    README.md
    templates/
  .github/
    ISSUE_TEMPLATE/
    workflows/
  .codex/
    config.toml
  .gitignore
  .gitattributes
  README.md
  AGENTS.md
  CLAUDE.md
  pyproject.toml
```

Deliverable:

- `V2_FOLDER_STRUCTURE.md`

Exit criteria:

- Each folder has documented purpose, allowed content, forbidden content, and storage policy.

### Phase 4 — Draft V2 `.gitignore`

Objective: prevent regenerated/local material from entering the first V2 commit.

Must ignore:

- Python caches.
- Test output.
- Runtime output.
- IDE/editor state.
- Local environment files.
- Agent local/generated state.
- Worktrees.
- Generated previews.
- Scaled asset cache.
- Build/package output.
- Temporary files.
- External artifact mount points.

Required new ignore for local scaled assets:

```gitignore
asset_cache/
assets/**/_generated*/
assets/**/_scaled*/
assets/**/scaled_cache*/
```

Deliverable:

- `V2_GITIGNORE_DRAFT.md`

Exit criteria:

- `.gitignore` draft exists and is ready before source import.

### Phase 5 — Draft V2 `.gitattributes` and Git LFS rules

Objective: make sure canonical binary assets are handled correctly before import.

Default policy:

- Track canonical runtime image/audio assets with Git LFS.
- Track fonts only if licensing permits redistribution.
- Do not track generated scaled images.
- Do not track generated previews.
- Do not track raw AI art iterations unless explicitly promoted.

Recommended LFS patterns:

```gitattributes
*.png filter=lfs diff=lfs merge=lfs -text
*.jpg filter=lfs diff=lfs merge=lfs -text
*.jpeg filter=lfs diff=lfs merge=lfs -text
*.webp filter=lfs diff=lfs merge=lfs -text
*.psd filter=lfs diff=lfs merge=lfs -text
*.kra filter=lfs diff=lfs merge=lfs -text
*.xcf filter=lfs diff=lfs merge=lfs -text
*.wav filter=lfs diff=lfs merge=lfs -text
*.ogg filter=lfs diff=lfs merge=lfs -text
*.mp3 filter=lfs diff=lfs merge=lfs -text
*.flac filter=lfs diff=lfs merge=lfs -text
*.mp4 filter=lfs diff=lfs merge=lfs -text
*.mov filter=lfs diff=lfs merge=lfs -text
*.zip filter=lfs diff=lfs merge=lfs -text
*.7z filter=lfs diff=lfs merge=lfs -text
*.rar filter=lfs diff=lfs merge=lfs -text
*.ttf filter=lfs diff=lfs merge=lfs -text
*.otf filter=lfs diff=lfs merge=lfs -text
```

Deliverable:

- `V2_GITATTRIBUTES_DRAFT.md`

Exit criteria:

- LFS policy is reviewed against inventory.
- Font licensing concern is flagged.
- Generated/scaled assets are excluded.

### Phase 6 — External artifact policy

Objective: keep useful artifacts accessible across machines without putting them in Git.

Preferred provider: Google Drive.

Critical rule: do not put the active Git repo inside Google Drive.

Suggested local development repo path:

```text
C:/Dev/StellarHegemony/
```

or:

```text
D:/Dev/StellarHegemony/
```

Suggested Google Drive vault layout:

```text
Google Drive/
  StellarHegemonyVault/
    screenshots/
      issues/
      raw_qa/
    videos/
    repro_bundles/
    agent_transcripts/
      codex/
      claude/
      opencode/
    consult_logs/
    generated_previews/
    builds/
    releases/
    archived_projects/
    old_repo_exports/
```

Deliverables:

- `EXTERNAL_ARTIFACT_POLICY.md`
- `external_artifacts.example.json`

Suggested example config:

```json
{
  "external_artifact_root": "G:/My Drive/StellarHegemonyVault",
  "screenshots": "screenshots",
  "videos": "videos",
  "agent_transcripts": "agent_transcripts",
  "repro_bundles": "repro_bundles",
  "generated_previews": "generated_previews",
  "builds": "builds",
  "archived_projects": "archived_projects",
  "old_repo_exports": "old_repo_exports"
}
```

Exit criteria:

- Vault policy exists.
- Vault layout is documented.
- Local-only config path is documented.
- Active Git repo is outside cloud sync.

### Phase 7 — Planning and project curation

Objective: preserve useful planning/agent continuity without importing every historical process artifact.

Migrate:

- Current planning docs.
- Current architecture/design docs.
- Current conventions/patterns docs.
- Active project plans.
- Current agent instructions.
- Current migration docs.

Do not migrate by default:

- Deep archived projects.
- Raw consult logs.
- Raw agent transcripts.
- Generated reports.
- Completed old checklists.
- Temporary scaffolding.

Deliverable:

- `PLANNING_AND_PROJECTS_CURATION.md`

Exit criteria:

- Current planning material is selected.
- Deep archive policy is applied.
- User-decision items are listed.

### Phase 8 — Asset curation and scaled-image cache design

Objective: import only useful canonical runtime/final assets and define local generation of scaled variants.

Asset policy:

1. Store original/canonical images in Git LFS.
2. Store runtime audio in Git LFS.
3. Do not store scaled/generated derivatives in Git.
4. Store local scaled variants under ignored cache paths.
5. Regenerate scaled variants only when the source original changes.

Recommended cache location:

```text
asset_cache/
  scaled_images/
  scaled_images_manifest.json
```

Suggested manifest fields:

```json
{
  "generator_version": "1",
  "entries": [
    {
      "source_path": "assets/Images/originals/example.png",
      "source_hash": "sha256:...",
      "source_modified_utc": "2026-05-24T00:00:00Z",
      "target_path": "asset_cache/scaled_images/example_128.png",
      "target_size": [128, 128],
      "resample_method": "lanczos"
    }
  ]
}
```

The first implementation may use source hash only, timestamp only, or both. Hash is safer; timestamp is faster. A hybrid is acceptable.

Deliverables:

- `ASSET_MIGRATION_PLAN.md`
- Optional future `Tools/assets/build_scaled_cache.py`
- Optional future asset cache design document.

Exit criteria:

- Runtime assets are identified.
- Generated previews are excluded.
- Scaled-image cache policy is documented.
- Required startup assets are present or generation path is documented.

### Phase 9 — GitHub issue curation

Objective: avoid stale issue clutter in V2.

Approved direction:

The user intends to work through and resolve/archive old issues before migration. Expect little issue migration.

Recommended policy:

1. Resolve/archive stale issues in old repo first.
2. Recreate only active high-value issues in V2.
3. Include backlinks to old issues if recreated.
4. Prefer new clean issue templates in V2.

Deliverable:

- `ISSUE_MIGRATION_PLAN.md`

Exit criteria:

- Open old issues are reviewed.
- Any issues that must survive into V2 are identified.
- Stale issues are not blindly imported.

### Phase 10 — Create V2 repository

Objective: create the clean repository safely.

Approved settings:

- Repository name: `StellarHegemony`
- Initial visibility: private

Required sequence:

1. Create `ropesend/StellarHegemony` as private.
2. Clone outside cloud sync.
3. Install Git LFS.
4. Add `.gitignore`, `.gitattributes`, and initial README before importing source/assets.
5. Make the first hygiene commit.

Exit criteria:

- V2 repo exists.
- V2 is private.
- Local clean clone exists outside cloud sync.
- LFS is installed.
- Hygiene files are committed first.

### Phase 11 — Import source and tests

Objective: import core source without historical baggage.

Start with:

```text
game/
tests/
data/
docs/
pyproject.toml
```

Do not copy assets until LFS rules are confirmed.

Exit criteria:

- Source import committed.
- No generated files accidentally staged.
- Basic import/smoke tests attempted or blockers documented.

### Phase 12 — Import approved assets

Objective: import canonical runtime assets using LFS.

Rules:

- Copy only approved assets.
- Verify `git lfs status` before commit.
- Exclude scaled image caches and generated previews.
- Move questionable large/raw/generated assets to Google Drive vault or separate future review.

Exit criteria:

- Approved assets are committed through LFS.
- Generated/scaled assets are absent from Git.
- Startup asset needs are satisfied or documented.

### Phase 13 — Import selected planning/project system

Objective: preserve continuity without historical clutter.

Import:

- Current planning docs.
- Stage 0 docs.
- Active project plans.
- Trimmed agent guidance.

Do not import:

- Deep archives unless approved.
- Raw agent transcripts.
- Generated coordination summaries.

Exit criteria:

- Planning docs are curated and committed.
- Agent guidance is present and trimmed.
- Historical/generated process artifacts are excluded.

### Phase 14 — Fresh clone validation

Objective: prove the repo works from a clean environment.

Validation checklist:

- Fresh clone succeeds.
- LFS pull succeeds.
- Python environment creates cleanly.
- Dependencies install.
- Game imports without missing files.
- Focused tests pass or blockers are documented.
- Game launches or launch blockers are documented.
- No required file is pulled from old local paths.
- Scaled asset cache can be generated locally if required.

Deliverable:

- `POST_MIGRATION_VALIDATION.md`

### Phase 15 — Multi-machine validation

Objective: confirm the migration improves the real workflow.

Checklist:

- Clone V2 on Machine A.
- Clone V2 on Machine B.
- Configure local artifact settings on both if needed.
- Confirm both machines can run tests from same repo state.
- Confirm generated/local files do not appear in `git status`.
- Confirm branch push/pull works between machines.
- Confirm Google Drive vault is usable for external artifacts.

Exit criteria:

- Multi-machine clone works.
- Branch handoff works.
- Agent local files stay ignored.
- External artifacts are accessible.

### Phase 16 — Old repo transition

Objective: identify the canonical repo while preserving old history.

Approved direction:

- Do not archive old repo immediately.
- Add an archive notice only after V2 is validated.
- Archive old repo only after user approval.

Exit criteria:

- V2 is canonical.
- Old repo remains accessible.
- User decides when to archive old repo.

### Phase 17 — Post-migration improvements

Recommended follow-up work:

- Issue templates.
- PR template.
- Focused CI workflow.
- Setup/bootstrap scripts.
- Asset policy doc.
- Repo hygiene check script.
- Scaled asset cache generation tool.
- Repro bundle collection tool that writes to external vault, not Git.

## Stage 0 master acceptance criteria

Stage 0 is complete only when all of the following are true:

- `ropesend/StellarHegemony` exists and is private.
- Old source snapshot is recorded.
- Old repo is safe and unmodified destructively.
- Repo inventory/classification is complete.
- V2 folder structure is approved.
- `.gitignore` and `.gitattributes` are committed before imports.
- Source/tests/data/docs are imported.
- Approved assets are imported through LFS.
- Generated scaled assets are ignored and locally regenerable.
- Google Drive artifact vault is documented and separate from Git repo.
- Planning/project history is curated.
- Issues are resolved/archived or selectively recreated.
- Fresh clone validation is complete.
- Multi-machine workflow validation is complete.
- Old repo remains unarchived until the user explicitly approves archival.

## Handoff guidance for future agents

Future agents should:

1. Read `STAGE_0_DECISIONS.md` first.
2. Read this file second.
3. Read `DETAILED_MIGRATION_PLAN.md` third.
4. Create or update the deliverable files listed in each phase.
5. Keep changes small and reviewable.
6. Avoid destructive actions.
7. Ask the user only for unresolved decisions that block progress.
8. Prefer documenting uncertainty rather than guessing.
9. Leave a clear migration log after every substantive step.
