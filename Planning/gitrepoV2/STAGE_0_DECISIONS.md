# Stage 0 Decisions — GitRepoV2 / Stellar Hegemony

This file records the **proposed** and **settled** direction for the repository V2 migration. Each row carries its current status.

> **Status note (2026-05-25):** Task D pass complete. The six original `proposed` rows have been confirmed; three additional audit-scope items were settled; one prompt erratum was resolved. The "do not perform irreversible actions" guardrail still applies — settled decisions inform the V2-prep planning artifacts, but the actual V2 repo creation, push, V1 archive, and history rewrite remain user-triggered.

Status legend:

- `settled` — confirmed by the user; do not reopen without explicit instruction.
- `proposed` — current best direction, but the user has not finally confirmed.
- `deferred` — will be decided later in the migration.

## Stage placement

GitRepoV2 is **Stage 0** of the long-range planning sequence. *(Status: settled)*

Stage 0 should be completed before major Stage 1 implementation work begins. Design refinement may continue, but large architecture-changing code work should happen in the clean V2 repository after validation.

## Core direction

The migration is a repository hygiene and workflow migration. It is **not** a game rewrite. *(Status: settled)*

The old `StarshipBattles` repository remains useful as historical context. Do not delete it, rewrite its history, or archive it until the V2 repository has been validated and the user explicitly approves archiving. *(Status: settled)*

## Settled choices (2026-05-25)

| Topic | Decision | Status |
|---|---|---|
| V2 repository name | `StellarHegemony` (CamelCase) | **settled 2026-05-25** |
| Initial V2 visibility | **Private** until the migration is validated; flip later if/when desired | **settled 2026-05-25** |
| Old repository handling | Leave `StarshipBattles` unarchived for now; archive only after V2 is validated *and* the user explicitly approves | **settled 2026-05-25** |
| Git LFS policy | **Path-scoped** LFS for canonical runtime image/audio masters. See `V2_GITATTRIBUTES_DRAFT.md`. NOT extension-scoped (`*.png filter=lfs` etc.). Confirmed via codex consult `20260526T033109Z_stage0-lfs-policy`. | **settled 2026-05-25** |
| Scaled image variants | Do **not** store generated scaled variants in Git. Each multi-size family stores only its canonical master size; sibling sizes regenerate locally at startup via `game.assets.image_derivatives`. | **settled 2026-05-25** |
| Image/audio asset policy | Track canonical runtime image and audio masters with Git LFS. Audio + fonts pre-armed in `.gitattributes` for when populated. Fonts license-gated. | **settled 2026-05-25** |
| External artifact vault provider | **Google Drive**. Layout in `EXTERNAL_ARTIFACT_POLICY.md`. The active Git repo must NOT live inside the vault sync folder. | **settled 2026-05-25** |
| Issue migration policy | **Resolve/archive most old issues first**, then recreate only active high-value issues in V2 with backlinks. Minimal migration. | **settled 2026-05-25** |
| GitHub plan tier for V2 | **Free / Pro** (10 GiB LFS storage + 10 GiB/month bandwidth). Projected V2 LFS payload ~4.1 GiB. **Risk:** bandwidth, not storage, is the binding constraint at this tier — two fresh full-LFS clones per month consumes ~82% of the bandwidth cap. CI and secondary-machine workflows should avoid routine full `git lfs pull`. | **settled 2026-05-25** |
| `Reviews/` import scope | **Import top-level only** (`README.md`, `Review_Report_2026_01_27.md`, `prompts/`, `protocols/`, `scripts/`, `reviews_index.md`); send `Reviews/results/` (40.1 MiB / 2,435 files) to `<vault>/old_repo_exports/v1_reviews_results/`. | **settled 2026-05-25** |
| `Projects/active_projects/` content | **Drop all V1 active project content** (PROJ-481..499 + `Batch_*_Prompt.txt` + `_doc_consolidation/`). Vault under `<vault>/old_repo_exports/v1_active_projects/`. V2's `Projects/active_projects/` is empty at import. | **settled 2026-05-25** |
| `Projects/` infrastructure (README, index, protocols, gp_protocols) | **Keep as scaffolding** in V2. Project-system infrastructure stays so agents have a tree to operate against; new V2 projects land in `Projects/active_projects/` when needed. | **settled 2026-05-25** |
| `AgentCoordination/protocols/` curation | **All six files** (`consult_prompt_block.md`, `group_execution_protocol.md`, `interagent_discussion.md`, `partner_cli.md`, `ticket_deep_dive.md`, `ticket_workflow.md`) are load-bearing and imported as-is. | **settled 2026-05-25** |
| `AgentCoordination/templates/` (prompt erratum) | Path **does not exist** in V1 despite being referenced by `STAGE_0_NEW_AGENT_PROMPT.md:91,121`, `STAGE_0_PLAN.md` Phase 3, and `DETAILED_MIGRATION_PLAN.md` Phase 3. **Resolution:** drop the references from those files. Do NOT create the folder in V2. If a real template later needs a home, add the folder then. | **settled 2026-05-25** |

## Decision rationale highlights

### V2 repository name (StellarHegemony)

Matches the game's full strategic-scope title; CamelCase single-word URL works cleanly in GitHub navigation, IDE titlebars, and command-line paths. The kebab-case alternative would match Python-package conventions but the user does not currently publish a package. Reversible-with-friction: GitHub allows repo renames with automatic redirects.

### Initial visibility (private)

Lets the migration window — partial imports, missing context, ongoing curation — happen without a public URL leaking incomplete state. Flip-to-public is a one-click toggle once Phase 14/15 validation passes.

### LFS policy (path-scoped)

Confirmed via codex consult (response: `AgentCoordination/Scratchpad/Consult/20260526T033109Z_stage0-lfs-policy/response.md`):
- Matches the existing "track only canonical masters, regenerate derivatives locally" contract documented at `docs/03_CONVENTIONS.md:250-267`.
- An extension-wide `*.png filter=lfs` umbrella rule silently routes accidentally-tracked derivatives through LFS instead of exposing them — works against the gitignore contract.
- Tiny single-resolution image families (cursor 0.05 MiB, modifier_icons 0.07 MiB, etc.) don't move the bandwidth needle if moved to plain Git; the meaningful single-res weight (system_backgrounds 91 MiB, race_portraits 43 MiB, warp_points 19 MiB) is real LFS material.

### GitHub plan tier (Free/Pro)

Storage fits comfortably (4.1 GiB of 10 GiB). Bandwidth is the binding constraint: ~2.5 fresh full-LFS clones per month before throttling. Operational mitigation:
- Don't routinely run `git lfs pull` on CI or scratch checkouts.
- For secondary machines, use `git lfs pull --include="<targeted-glob>"` to pull only the masters needed for the current work.
- Reassess if multi-machine + CI clone cadence rises (escalation paths: buy a 50 GiB LFS pack at $5/month, or move to Team tier at $4/user/month + transfer to a paid org).

### Vault provider (Google Drive)

User has substantial storage via Google AI Ultra subscription. Provider is reversible: the `external_artifacts.example.json` schema isolates the provider name + root path, so switching to OneDrive / Syncthing / NAS later is a config edit. The active Git repo *must not* live inside the vault sync folder — that's a non-negotiable rule regardless of provider.

### Issue migration (resolve/archive first, minimal migration)

User intends to triage the V1 issue backlog in-place before V2, closing stale issues and resolving anything still tractable. The V2 issue tracker starts mostly empty; the few active-and-high-value issues that survive get recreated in V2 with backlinks.

### Old-repo handling (archive only after V2 validated)

Phase 14/15 validation must pass — fresh clone works, dependencies install, focused tests pass, multi-machine workflow verified — before any archive notice goes on V1. Then archival is reversible-with-friction (GitHub allows unarchive).

### Projects/active_projects/ content (drop all)

Surprise vs the original `STAGE_0_DECISIONS.md` proposed direction (which assumed "current PROJ-XXX folders only" would migrate). The user's actual position is more aggressive: **none of the PROJ-481..499 content is needed in V2.** The V1 project material is forensically interesting but not load-bearing for V2 development. Vault preserves the content; V2 starts the project tracker clean.

### Projects/ infrastructure (keep)

Without this scaffolding, agent tooling that references `Projects/active_projects/`, the `claude-proj-*` skills, or the `claude-gp-*` skills would have no tree to operate against. The README + index + protocols + gp_protocols folders are cheap to carry (~1 MiB total) and unblock immediate post-V2 project work.

### AgentCoordination/templates/ (drop the reference)

Path does not exist in V1; was referenced in three Stage 0 docs as if it did. The reference was speculative scaffolding. Drop from all three references; if a real template later needs a home, create the folder then.

## Google Drive artifact vault policy

Google Drive is acceptable for the external artifact vault because the user prefers it and has substantial available storage through a Google AI Ultra subscription.

The active Git repository must **not** live inside Google Drive, OneDrive, Dropbox, or any other cloud-sync folder. The Git repo should live in a normal development path such as:

```text
C:/Dev/StellarHegemony/
```

or:

```text
D:/Dev/StellarHegemony/
```

Detailed vault layout, per-machine config schema, and cutover sequence: see [`EXTERNAL_ARTIFACT_POLICY.md`](EXTERNAL_ARTIFACT_POLICY.md).

## Asset policy

The V2 repository stores canonical assets only, not every generated derivative.

| Category | Location | Git treatment |
|---|---|---|
| Canonical runtime images (size-tiered masters) | `assets/images/<family>/<master>/` (`components/1024/`, `flags/flag_*/1024/`, `stars/1024/`, `planets/2048/`) | **Git LFS** (path-scoped) |
| Canonical runtime images (single-resolution) | `assets/images/{cursor,modifier_icons,nebulae,race_portraits,resource_icons,resource_portraits,sphere_world,system_backgrounds,warp_points,asteroids}/`, `default_ship_portrait.png` | **Git LFS** (path-scoped) |
| Ship-theme art | `assets/images/ship_themes/<Theme>/{skins,portraits}/` | **Git LFS** (path-scoped) |
| Theme / flag / race-portrait metadata | `*.json` colocated with the art | Plain Git |
| Canonical runtime audio (when added) | `assets/audio/` (placeholder; no tracked audio yet) | **Git LFS** when populated |
| Fonts | `assets/fonts/` only if license permits redistribution | **Git LFS** when populated; license-gated |
| Generated scaled images | In-place sibling size folders next to each family's master (`components/{64,128,256,512,2048}/`, `flags/flag_*/{32,64,128,256,512}/`, `stars/{128,256,512}/`, `planets/{128,256,512,1024}/`) | **Gitignored** (regenerated locally) |
| Generated previews / AI iterations | `<vault>/generated_previews/` | Not tracked |
| Raw source art | `<vault>/old_repo_exports/` or separate private asset repo after review | Not tracked in V2 by default |

Scaled images regenerate locally at startup via the shared `game.assets.image_derivatives` engine (per-family wrappers: `component_derivatives`, `flag_derivatives`, `star_derivatives`, `planet_derivatives`). Each family stores **only its canonical master size** in source control (1024 for components/flags/stars, 2048 for planets). All other sibling sizes generate on first startup and refresh when the master file's hash/mtime changes. Per-family hidden hash manifest (`.<family>_derivatives_manifest.json`) fast-paths subsequent runs.

This replaced the earlier draft proposal of a central `asset_cache/scaled_images/` tree — that scheme was never implemented; the in-place per-family layout is what shipped. See `docs/03_CONVENTIONS.md` "Image Asset Derivatives — canonical pattern" for the full per-family table and contracts.

The V2 `.gitignore` (see `V2_GITIGNORE_DRAFT.md`) ignores every per-family derivative size folder and per-family manifest.

## Stage 0 exit criteria

Stage 0 is complete only when:

- `StellarHegemony` exists as a private repository.
- The old repo source commit SHA is recorded. *(Done: `bc755f012`, see [`MIGRATION_SOURCE_SNAPSHOT.md`](MIGRATION_SOURCE_SNAPSHOT.md).)*
- A non-destructive backup/full clone exists.
- Repository inventory and classification are complete. *(Done: see [`inventory_post_cleanup.md`](inventory_post_cleanup.md) and [`MIGRATION_CLASSIFICATION.md`](MIGRATION_CLASSIFICATION.md).)*
- V2 folder structure is documented. *(Done: [`V2_FOLDER_STRUCTURE.md`](V2_FOLDER_STRUCTURE.md).)*
- `.gitignore` is created before source import. *(Drafted: [`V2_GITIGNORE_DRAFT.md`](V2_GITIGNORE_DRAFT.md).)*
- `.gitattributes` / Git LFS rules are created before asset import. *(Drafted: [`V2_GITATTRIBUTES_DRAFT.md`](V2_GITATTRIBUTES_DRAFT.md).)*
- Canonical source, tests, data, docs, selected planning, and approved assets are imported. *(Checklist: [`V2_IMPORT_CHECKLIST.md`](V2_IMPORT_CHECKLIST.md).)*
- Generated/scaled asset outputs are ignored and locally regenerable.
- Google Drive artifact vault policy is documented. *(Done: [`EXTERNAL_ARTIFACT_POLICY.md`](EXTERNAL_ARTIFACT_POLICY.md).)*
- Fresh clone validation passes or has clearly documented blockers. *(Pending Phase 14.)*
- Multi-machine workflow validation passes. *(Pending Phase 15.)*
- The old repo remains available until the user approves final archival.

## Guidance for future agents

Future agents should execute this plan using small, reviewable steps. They should update planning files as decisions are made, but **must not** perform destructive actions against the old repo (force-push, history rewrite, archive) without explicit user approval.

Before executing Phase 10 (create V2 repository) or any later import phase, re-confirm with the user that this file's settled rows still reflect the user's intent. If the user changes a row, update both this file and the planning drafts that depend on it (see the "Decision-sensitive assumptions" sections in `MIGRATION_CLASSIFICATION.md`, `V2_IMPORT_CHECKLIST.md`, `EXTERNAL_ARTIFACT_POLICY.md`, `V2_FOLDER_STRUCTURE.md`).
