# Stage 0 Decisions — GitRepoV2 / Stellar Hegemony

This file records user-approved decisions for the repository V2 migration. Future agents should treat these decisions as settled unless the user explicitly changes them.

## Stage placement

GitRepoV2 is **Stage 0** of the long-range planning sequence.

Stage 0 should be completed before major Stage 1 implementation work begins. Design refinement may continue, but large architecture-changing code work should happen in the clean V2 repository after validation.

## Core decision

The migration is a repository hygiene and workflow migration. It is **not** a game rewrite.

The old `StarshipBattles` repository remains useful as historical context. Do not delete it, rewrite its history, or archive it until the V2 repository has been validated and the user explicitly approves archiving.

## Approved choices

| Topic | Decision |
|---|---|
| V2 repository name | `StellarHegemony` |
| Initial V2 visibility | Private |
| Old repository handling | Leave `StarshipBattles` unarchived for now; archive later only after validation confirms nothing important broke or was missed |
| External artifact provider | Prefer Google Drive, provided it is used only for external artifacts and not as the live Git working tree |
| Issue migration | User intends to resolve/archive old issues before migration; expect little or no issue migration unless active high-value issues remain |
| Image/audio asset policy | Track canonical runtime image and audio assets with Git LFS |
| Scaled image variants | Do not store generated scaled variants in Git; generate and cache them locally per machine |

## Google Drive artifact vault policy

Google Drive is acceptable for the external artifact vault because the user prefers it and has substantial available storage through a Google AI Ultimate subscription.

The active Git repository must **not** live inside Google Drive, OneDrive, Dropbox, or any other cloud-sync folder unless the user explicitly accepts the risks. The Git repo should live in a normal development path such as:

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

## Asset policy

The V2 repository should store canonical assets, not every generated derivative.

Recommended categories:

| Category | Location | Git treatment |
|---|---|---|
| Canonical runtime images | `assets/Images/` or approved equivalent | Git LFS |
| Canonical runtime audio | `assets/Audio/` or approved equivalent | Git LFS |
| Fonts | Only if license permits redistribution | Git LFS if tracked |
| Generated scaled images | Local cache outside tracked source, such as `asset_cache/scaled_images/` | Ignored by Git |
| Generated previews / AI iterations | Google Drive vault unless explicitly promoted | Not tracked |
| Raw source art | Google Drive vault, separate private asset repo, or LFS only after review | Needs classification |

Scaled images should be regenerated locally only when the source/original changes. Use a local manifest based on file hash, timestamp, source path, target size, and generator version.

Suggested local cache shape:

```text
asset_cache/
  scaled_images/
  scaled_images_manifest.json
```

`asset_cache/` should be ignored by Git.

## Stage 0 exit criteria

Stage 0 is not complete merely because the new repo exists. It is complete only when:

- `StellarHegemony` exists as a private repository.
- The old repo source commit SHA is recorded.
- A non-destructive backup/full clone exists.
- Repository inventory and classification are complete.
- V2 folder structure is documented.
- `.gitignore` is created before source import.
- `.gitattributes` / Git LFS rules are created before asset import.
- Canonical source, tests, data, docs, selected planning, and approved assets are imported.
- Generated/scaled asset outputs are ignored and locally regenerable.
- Google Drive artifact vault policy is documented.
- Fresh clone validation passes or has clearly documented blockers.
- Multi-machine workflow validation passes.
- The old repo remains available until the user approves final archival.

## Guidance for future agents

Future agents should flesh out and execute this plan using small, reviewable steps. They should update planning files as decisions are made, but they must not perform destructive actions against the old repo without explicit user approval.
