# External Artifact Policy — Stellar Hegemony Vault

> **Drafted:** 2026-05-25 against V1 HEAD `bc755f012`. Status: **draft, pending user review.**
>
> Defines the off-Git artifact vault: what goes there, how it's organized, how machines find it, and how V2's existing VAULT-classified material (per `MIGRATION_CLASSIFICATION.md`) gets seeded.

## Decision-sensitive assumptions (settle in Task D)

The whole document is written against the current Task D proposal of **Google Drive as the vault provider**. If the user picks a different provider, the layout below transfers verbatim; only the `external_artifact_root` value in `external_artifacts.example.json` changes. Provider-sensitive rows are flagged with **[provider-sensitive]** below.

1. **Provider = Google Drive** (proposed in `STAGE_0_DECISIONS.md`). Reasons cited there: user preference + substantial Google AI Ultra subscription storage. Alternative providers considered: OneDrive (single-Microsoft-account simplicity, smaller default storage), Dropbox (less integrated), Syncthing (P2P, no provider dependency, more setup), NAS SMB share (zero cloud, requires LAN/VPN access).
2. **Active Git repo must NOT live inside the vault sync folder.** Settled. The risk: cloud-sync clients can rewrite, lock, or partially-sync files in a Git working tree, corrupting `.git/index` or interrupting `pack-objects` mid-write. This is non-negotiable across all candidate providers.
3. **Vault paths use forward slashes in tracked example configs**; per-machine local configs use the platform's native path style (Windows uses `G:/My Drive/...` or `G:\My Drive\...`; macOS uses `~/Library/CloudStorage/GoogleDrive-<...>/My Drive/...`).

## Vault layout

```text
StellarHegemonyVault/                  # the vault root (provider-managed sync folder)
  screenshots/
    issues/                             # per-GitHub-issue screenshot folders
      issue-NNN/
    raw_qa/                             # QA-session raw screenshots
  videos/                               # demo / repro videos
  repro_bundles/                        # zipped save+config+logs per bug
    v1_tracking_logs/                   # seeded from V1 tracking-assets/logs/
      issue-17/                         #   Battle logs from closed issues
      issue-19/
      issue-8/
      issue-31/
  agent_transcripts/                    # raw agent session transcripts (rarely-needed)
    claude/
    codex/
    opencode/
    antigravity/
  consult_logs/                         # AgentCoordination/Scratchpad/Consult/ snapshots
                                        # (current Scratchpad is local-only; promote selected
                                        #  consults here if they have lasting value)
  generated_previews/                   # AI-generated component / ship-portrait iterations
                                        # that may be reviewed but not promoted to assets/
  builds/                               # local build outputs (Windows installer, etc.)
  releases/                             # mirror of GitHub Release zips for offline access
  archived_projects/                    # projects archived since V2 cutover
  old_repo_exports/                     # one-time V1 history dumps
    v1_projects_deep_archive/           # seeded from Projects/deep_archive/
    v1_projects_archived/               # seeded from Projects/archived_projects/ (if exists)
    v1_legacy_tickets/                  # seeded from AgentCoordination/legacy_tickets/
    v1_reviews_results/                 # seeded from Reviews/results/
    v1_full_clone/                      # optional: a full bare clone of V1 for "what did
                                        #          we have at cutover" forensics
```

## Tracked example config

A single tracked file in V2 documents the vault contract. Each developer's machine adds a gitignored `external_artifacts.local.json` with their actual mount path.

```json
// external_artifacts.example.json (TRACKED in V2)
{
  "provider": "google_drive",
  "external_artifact_root": "<path-to-vault-root-on-this-machine>",
  "categories": {
    "screenshots": "screenshots",
    "videos": "videos",
    "repro_bundles": "repro_bundles",
    "agent_transcripts": "agent_transcripts",
    "consult_logs": "consult_logs",
    "generated_previews": "generated_previews",
    "builds": "builds",
    "releases": "releases",
    "archived_projects": "archived_projects",
    "old_repo_exports": "old_repo_exports"
  },
  "notes": "Copy this file to external_artifacts.local.json and replace external_artifact_root with the real per-machine path. The .local.json is gitignored. The active StellarHegemony Git checkout must NOT live inside external_artifact_root."
}
```

Per-machine override (gitignored):

```json
// external_artifacts.local.json (Windows example, gitignored)
{
  "provider": "google_drive",
  "external_artifact_root": "G:/My Drive/StellarHegemonyVault",
  "categories": { ... }
}
```

```json
// external_artifacts.local.json (macOS example, gitignored)
{
  "provider": "google_drive",
  "external_artifact_root": "/Users/<user>/Library/CloudStorage/GoogleDrive-<acct>/My Drive/StellarHegemonyVault",
  "categories": { ... }
}
```

## What goes in the vault, by category

### `screenshots/`

- GitHub issue screenshots before they're uploaded as issue attachments. Once uploaded to a GitHub Issue, the issue attachment is the canonical copy; the vault copy is a backup.
- Raw QA screenshots from `Tools/qa_observer/` sessions before triage.
- Game session screenshots a developer wants to keep but that aren't tied to a bug yet.

Not in scope: artwork iterations (those go to `generated_previews/`); promotional screenshots (those go in marketing assets, outside this vault).

### `videos/`

- Bug reproduction videos.
- Feature demo clips.
- Long-form gameplay recordings.

### `repro_bundles/`

- Zipped reproduction state per bug: a save file + configs + relevant logs + a README. Issues link to a specific bundle.
- **Seeded at V2 cutover with `v1_tracking_logs/`** from `tracking-assets/logs/` (~64 MiB, 14 files, includes the 25 MiB issue-17 and issue-19 battle logs and the 49 MiB BUG-122 log).

### `agent_transcripts/`

- Per-agent raw session transcripts (`claude/`, `codex/`, `opencode/`, `antigravity/`).
- Generally not consulted post-session; vaulted as audit trail.
- Specifically NOT in Git: transcripts are noisy, contain quoted code snippets that duplicate the repo, and have no merge semantics.

### `consult_logs/`

- Snapshots of selected `AgentCoordination/Scratchpad/Consult/<leaf>/` directories that have lasting value (architectural decisions, post-mortems, multi-round investigations).
- The live `Scratchpad/` directory itself is and stays gitignored (per V1 `.gitignore`); the vault is the long-term home for the ones worth keeping.

### `generated_previews/`

- AI-generated component portrait iterations from `Tools/process_components/`.
- AI-generated ship-portrait regenerations from `Tools/regenerate_ship_portraits/`.
- AI-generated planet sphere previews from `Tools/process_planet_spheres/`.
- These are not the canonical runtime assets; only promoted images land in `assets/images/*/1024/` or `assets/images/*/2048/` and enter Git LFS.

### `builds/`

- Locally produced installers / packaged builds (Windows installer, macOS bundle, Linux tarball).
- One per release-candidate.

### `releases/`

- Mirror of GitHub Releases zips for offline access.
- Authoritative copy: GitHub Releases. Vault is convenience.

### `archived_projects/`

- Projects archived **after** V2 cutover (the V1-side archive is in `old_repo_exports/v1_projects_deep_archive/`).
- Same shape as V1's `Projects/deep_archive/` but populated incrementally.

### `old_repo_exports/`

- One-time V1 history dumps, seeded as part of V2 cutover.
- Subfolders per V1 SKIP-to-VAULT bucket from `MIGRATION_CLASSIFICATION.md`:
  - `v1_projects_deep_archive/` (335.8 MiB, 3,997 files)
  - `v1_projects_archived/` (if `Projects/archived_projects/` exists in V1; verify)
  - `v1_active_projects/` (~16 MiB, all 19 V1 PROJ-481..499 + Batch_*_Prompt.txt + _doc_consolidation/ per Task D decision to start V2's project tracker clean)
  - `v1_legacy_tickets/` (72.5 MiB, 195 files)
  - `v1_reviews_results/` (40.1 MiB, 2,479 files)
  - `v1_full_clone/` (optional) — a bare clone of V1 captured at the migration SHA, for forensic access without spinning up V1 GitHub access

Total seed: ~528 MiB / ~6,800 files.

## What does NOT go in the vault

- Active Git working trees (cloud sync corrupts `.git/`).
- Generated derivative sizes (those regenerate locally from masters via `game.assets.image_derivatives`).
- `__pycache__/`, `.pytest_cache/`, `node_modules/`, virtual environments.
- Personally identifying information beyond the scope of project work.
- **[provider-sensitive]** Anything with restrictive licensing terms that conflict with the provider's TOS. Google Drive is broadly permissive for personal storage; commercial fonts may have separate license issues regardless of provider.

## Cutover sequence (Stage 0 Phase 12 / 13 dependency)

The vault gets populated **before** V1 is archived, never after. Order:

1. Pick provider (Task D); install/sign-in on Machine A.
2. Create vault root (`StellarHegemonyVault/`) and the top-level category subdirs.
3. Copy V1's SKIP-to-VAULT buckets into `old_repo_exports/` and `repro_bundles/`:
   ```bash
   # Pseudocode; actual paths per machine
   cp -r Projects/deep_archive                            <vault>/old_repo_exports/v1_projects_deep_archive
   cp -r Projects/active_projects/PROJ-*                  <vault>/old_repo_exports/v1_active_projects/
   cp    Projects/active_projects/Batch_*_Prompt.txt      <vault>/old_repo_exports/v1_active_projects/ 2>/dev/null || true
   cp -r Projects/active_projects/_doc_consolidation      <vault>/old_repo_exports/v1_active_projects/ 2>/dev/null || true
   cp -r AgentCoordination/legacy_tickets                 <vault>/old_repo_exports/v1_legacy_tickets
   cp -r Reviews/results                                  <vault>/old_repo_exports/v1_reviews_results
   cp -r tracking-assets/logs                             <vault>/repro_bundles/v1_tracking_logs
   ```
4. **[provider-sensitive]** Confirm sync to the cloud completes; note the upload time as a sanity figure for future cutover planning.
5. On the second machine (if multi-machine in scope), wait for the vault to sync down; verify the V1 dumps are visible.
6. Proceed with V2 import (Phases 11–13).
7. **Do NOT delete the V1 source directories from V1.** V1 remains unarchived per the settled "leave unarchived until V2 validated" decision. The vault is a copy, not a replacement.

## Storage and cost considerations

**[provider-sensitive]** Google Drive's free tier is 15 GiB. The user's Google AI Ultra plan grants 30 TiB (per the assumption documented in `STAGE_0_DECISIONS.md`). V2 cutover seeds ~512 MiB — well under 1% of either tier. Long-term growth: a few GiB per year is realistic if `agent_transcripts/` and `generated_previews/` accumulate; nowhere near plan limits.

If the user later switches providers, the same ~512 MiB seed transfers; copy-on-write tools (rsync / Rclone) handle the migration.

## Open questions

1. **Vault provider confirmation** — currently `proposed`. See Task D.
2. **`v1_full_clone/`** — optional. If included, captures the entire V1 `.git` pack (~16 GiB) outside Git, so forensic queries don't need V1 GitHub access. If excluded, V1 remains the only source of pre-cutover history. Recommendation: **include it** because GitHub archive operations are reversible-with-friction and the 16 GiB is negligible against vault storage.
3. **Provider TOS check for commercial fonts** if any get added later. **[provider-sensitive]** — flagged here so font addition doesn't silently violate provider TOS.
4. **Multi-machine sync verification** (Phase 15) — needs an explicit test: write a file from Machine A to the vault, observe it sync to Machine B before declaring vault workflow validated.
