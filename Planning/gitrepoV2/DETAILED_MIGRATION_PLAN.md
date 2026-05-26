# Stellar Hegemony Git Repo V2 — Detailed Step-by-Step Migration Plan

This document is the executable planning guide for migrating the current `StarshipBattles` repository into a cleaner V2 repository for **Stellar Hegemony**.

It is written for future agents and human continuation. Agents should update this file as decisions are made, but should avoid performing irreversible destructive actions without explicit user instruction.

## Core migration principle

This is a **repository hygiene migration**, not a game rewrite.

The goal is to preserve the current working game/source/design state while creating a new canonical repository with:

- cleaner history,
- smaller clone size,
- clear artifact boundaries,
- better multi-machine development support,
- a name that matches the full strategic scope of the game.

The current repo remains useful as a historical archive. Do not delete it or rewrite it unless explicitly instructed.

## Target name

Game title:

```text
Stellar Hegemony
```

Preferred repository name candidate:

```text
StellarHegemony
```

Alternate candidates:

```text
stellar-hegemony
Stellar-Hegemony
```

Unless the user chooses otherwise, future agents should assume `StellarHegemony` as the working V2 repo name.

---

# Phase 0 — Safety and scope freeze

## Objective

Prevent accidental loss of source, issues, artifacts, or historical context before the migration begins.

## Steps

1. Confirm the current source repository is:

   ```text
   ropesend/StarshipBattles
   ```

2. Confirm the current default branch is:

   ```text
   main
   ```

3. Confirm the user still wants a new clean V2 repo rather than an in-place history rewrite.

4. Record the current head commit SHA of `main` in this file under `Migration source snapshot` before migration begins.

5. Do not delete, force-push, archive, or rename the old repo during this phase.

6. Do not run `git filter-repo`, BFG Repo-Cleaner, `git lfs migrate`, or any destructive history rewrite during this phase.

7. Make a local full clone or backup of `StarshipBattles` before doing any large file movement.

8. If using a local clone for analysis, run:

   ```bash
   git status
   git branch --show-current
   git rev-parse HEAD
   ```

9. Save the outputs into `Planning/gitrepoV2/MIGRATION_LOG.md` if/when that file is created.

## Exit criteria

- [ ] Source repo and branch confirmed.
- [ ] Source commit SHA recorded.
- [ ] User has not requested destructive cleanup of the old repo.
- [ ] Old repo is treated as historical archive during migration.

---

# Phase 1 — Repository inventory

## Objective

Map what exists in the old repo before deciding what goes into V2.

## Steps

1. Generate a high-level top-level directory inventory.

   Suggested local command:

   ```bash
   find . -maxdepth 2 -type d | sort > Planning/gitrepoV2/inventory_directories.txt
   ```

   On Windows PowerShell:

   ```powershell
   Get-ChildItem -Directory -Recurse -Depth 2 | Select-Object -ExpandProperty FullName | Sort-Object > Planning/gitrepoV2/inventory_directories.txt
   ```

2. Generate a tracked-file size report.

   Suggested local command:

   ```bash
   git ls-files -s | sort -k4 > Planning/gitrepoV2/inventory_tracked_files.txt
   ```

3. Generate a large tracked file report.

   Suggested Python script:

   ```python
   from pathlib import Path
   import subprocess

   files = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
   rows = []
   for f in files:
       p = Path(f)
       if p.exists() and p.is_file():
           rows.append((p.stat().st_size, f))
   rows.sort(reverse=True)
   with open("Planning/gitrepoV2/inventory_large_tracked_files.txt", "w", encoding="utf-8") as out:
       for size, f in rows[:500]:
           out.write(f"{size:12d}  {f}\n")
   ```

4. Generate extension summary.

   Suggested Python script:

   ```python
   from pathlib import Path
   import subprocess
   from collections import defaultdict

   files = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
   stats = defaultdict(lambda: [0, 0])
   for f in files:
       p = Path(f)
       if p.exists() and p.is_file():
           ext = p.suffix.lower() or "<no extension>"
           stats[ext][0] += 1
           stats[ext][1] += p.stat().st_size

   with open("Planning/gitrepoV2/inventory_extension_summary.txt", "w", encoding="utf-8") as out:
       for ext, (count, size) in sorted(stats.items(), key=lambda item: item[1][1], reverse=True):
           out.write(f"{ext:20s} {count:8d} {size:14d}\n")
   ```

5. Identify the largest directories by tracked file size.

   Suggested Python script:

   ```python
   from pathlib import Path
   import subprocess
   from collections import defaultdict

   files = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
   stats = defaultdict(int)
   for f in files:
       p = Path(f)
       if p.exists() and p.is_file():
           parts = p.parts
           for depth in (1, 2, 3):
               if len(parts) >= depth:
                   stats["/".join(parts[:depth])] += p.stat().st_size

   with open("Planning/gitrepoV2/inventory_directory_sizes.txt", "w", encoding="utf-8") as out:
       for d, size in sorted(stats.items(), key=lambda item: item[1], reverse=True)[:500]:
           out.write(f"{size:14d}  {d}\n")
   ```

6. Search for files that are likely generated or local-only:

   Suggested search terms:

   ```text
   generated
   output
   cache
   backup
   session
   scratch
   worktree
   preview
   artifact
   log
   transcript
   consult
   __pycache__
   .pytest_cache
   ```

7. Create or update `Planning/gitrepoV2/MIGRATION_INVENTORY_SUMMARY.md` with:

   - total tracked files,
   - approximate tracked file size,
   - top 20 largest files,
   - top 20 largest directories,
   - obvious V2 exclusions,
   - obvious LFS candidates.

## Exit criteria

- [ ] Directory inventory created.
- [ ] Large file report created.
- [ ] Extension summary created.
- [ ] Directory size report created.
- [ ] Inventory summary written.
- [ ] Candidate exclusions identified.

---

# Phase 2 — Classify repository content

## Objective

Sort existing content into clear migration buckets.

## Classification buckets

Use these buckets for every major directory and large-file cluster.

### Bucket A — migrate as normal Git

Use for source truth that should be cloned on every machine.

Likely examples:

- `game/`
- `tests/`
- `data/`
- `docs/`
- `Planning/` selected canonical docs
- active project plans that still matter
- `pyproject.toml`
- root config files required to run tools
- small JSON/data files required at runtime

### Bucket B — migrate through Git LFS

Use for large binary files that are required runtime assets or canonical reference assets.

Likely examples:

- final `.png`, `.jpg`, `.jpeg`, `.webp` assets
- final audio files
- final video/image files required by the game
- large runtime data packs that should version with the game

### Bucket C — migrate to GitHub Issues or Releases

Use for bug evidence, reproduction bundles, and human-facing artifacts.

Likely examples:

- bug screenshots
- bug videos
- zipped reproduction saves
- large QA bundles
- milestone playable builds

### Bucket D — migrate to external/cloud/NAS storage

Use for large or transient material useful to the user but not appropriate for source history.

Likely examples:

- raw agent transcripts
- consult logs
- raw screenshots and videos
- generated art previews
- build outputs
- long-running QA artifacts
- archived project history not needed by agents every day

### Bucket E — do not migrate

Use for disposable local state.

Likely examples:

- caches
- `__pycache__`
- `.pytest_cache`
- local worktrees
- scratchpads
- generated timing files
- local settings
- machine-specific logs

## Steps

1. Create `Planning/gitrepoV2/MIGRATION_CLASSIFICATION.md`.

2. Add a table with columns:

   ```text
   Path | Bucket | Reason | V2 destination | Notes | Decision status
   ```

3. Fill in every top-level directory.

4. Fill in every directory over 50 MB from the inventory report.

5. Fill in every individual file over 25 MB from the large-file report.

6. Mark each row as one of:

   ```text
   Proposed
   Approved
   Rejected
   Needs user decision
   ```

7. Do not migrate anything marked `Needs user decision` until the user resolves it.

## Exit criteria

- [ ] Every top-level directory classified.
- [ ] Every large directory classified.
- [ ] Every large file classified.
- [ ] LFS candidates identified.
- [ ] External artifact candidates identified.
- [ ] Exclusions identified.

---

# Phase 3 — Decide V2 repository structure

## Objective

Define the clean target layout before creating the first V2 commit.

## Proposed V2 layout

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
    asset_manifest.json
    images/                 # post-reorg layout: snake_case, flat under images/
    audio/                  # placeholder
    fonts/                  # placeholder; license-gated tracking
  Tools/
    setup/
    migration/
    qa/
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

## Folder policy

### `game/`

Canonical runtime source.

### `tests/`

Canonical tests. Do not include generated test output.

### `data/`

Runtime data that must ship with the game.

### `docs/`

Human/agent documentation that remains current.

### `Planning/`

Current design planning only. Do not import the entire old planning archive blindly.

### `Projects/`

Only active or recently relevant project management material. Deep archives should be externalized unless the user explicitly wants them in V2.

### `assets/`

Final runtime assets only. Use LFS for large binaries. Generated previews and raw AI iterations should not live here unless explicitly promoted to final assets.

### `AgentCoordination/`

Keep templates and protocols only. Do not track per-machine local state, generated summaries, or session logs.

## Steps

1. Create `Planning/gitrepoV2/V2_FOLDER_STRUCTURE.md`.

2. Copy the proposed layout above into it.

3. For each proposed folder, write:

   - purpose,
   - allowed content,
   - forbidden content,
   - whether content is normal Git, LFS, or external.

4. Add unresolved structure questions to an `Open questions` section.

5. Do not begin import until the folder structure file exists and is reviewed.

## Exit criteria

- [ ] V2 folder structure documented.
- [ ] Allowed/forbidden content documented per folder.
- [ ] Structure open questions listed.

---

# Phase 4 — Draft V2 `.gitignore`

## Objective

Prevent reintroducing the same bloat in the first V2 commit.

## Required rules

The V2 `.gitignore` must be created before importing files.

Minimum starting rules:

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
.venv/
venv/
env/

# Test/cache output
.pytest_cache/
.testmondata*
.test_durations.json
.test_file_duration_history.json
coverage.json
htmlcov/

# Runtime output
output/
logs/
*.log
combat_lab/output/
combat_lab/battle_states/
combat_lab/test_history/

# Local IDE/editor
.vscode/
.idea/
.VSCodeCounter/

# Local environment
.env
*.local
*.local.json

# Agent local/generated state
AgentCoordination/local/
AgentCoordination/generated/
AgentCoordination/Scratchpad/
.agent_reports/
.codex/sessions/
.claude/worktrees/
.worktrees/

# Generated previews and scratch assets
generated/
previews/
*_preview/
*_previews/
assets/**/_processed_preview*/
assets/**/_ai_*preview*/

# Build/package output
build/
dist/
*.egg-info/

# Temporary files
*.tmp
*.bak
*.backup
*.corrupt
nul
MagicMock/

# External artifact mount point if created locally
ExternalArtifacts/
```

## Steps

1. Create `Planning/gitrepoV2/V2_GITIGNORE_DRAFT.md`.

2. Include the initial `.gitignore` draft.

3. Cross-check against the old repo inventory.

4. Add project-specific patterns found during inventory.

5. Identify any patterns that could accidentally hide real source files.

6. Do not use broad ignores like `*.json` unless there is an explicit exception strategy.

## Exit criteria

- [ ] Draft `.gitignore` written.
- [ ] Inventory-derived patterns added.
- [ ] Risky broad patterns reviewed.
- [ ] `.gitignore` ready before first V2 import commit.

---

# Phase 5 — Draft V2 `.gitattributes` and Git LFS rules

## Objective

Define how large binary assets will be tracked before importing assets.

## LFS draft — path-scoped (NOT extension-scoped)

**Superseded:** the earlier extension-scoped draft (`*.png filter=lfs`, etc.) would LFS-track generated derivative PNGs alongside masters, which the per-family `image_derivatives` engine produces on every startup. Use path-scoped rules instead. See `STAGE_0_PLAN.md` Phase 5 for the canonical skeleton; the new agent generates `V2_GITATTRIBUTES_DRAFT.md` from that.

## Important font warning

Before migrating fonts, verify licensing. Do not move commercial font files into a public repo unless their license permits redistribution.

## Steps

1. Create `Planning/gitrepoV2/V2_GITATTRIBUTES_DRAFT.md`.

2. Include the LFS draft above.

3. Compare against asset file extensions discovered in Phase 1.

4. Decide whether images under `assets/` should all use LFS or only files above a threshold.

5. Decide whether generated preview image folders should be excluded entirely rather than LFS-tracked.

6. Add a `Git LFS setup notes` section:

   ```bash
   git lfs install
   git lfs track "*.png"
   git lfs track "*.jpg"
   git lfs track "*.jpeg"
   git lfs track "*.webp"
   git lfs track "*.wav"
   git lfs track "*.ogg"
   git add .gitattributes
   ```

## Exit criteria

- [ ] `.gitattributes` draft written.
- [ ] LFS extensions reviewed against inventory.
- [ ] Font licensing question flagged.
- [ ] Generated-preview folders excluded from LFS unless explicitly promoted.

---

# Phase 6 — Decide external artifact policy

## Objective

Make multi-machine development seamless without storing every artifact in Git.

## Recommended external artifact root

Each machine should have a local path outside the Git repo, such as:

```text
D:/StarshipHegemonyVault/
```

or

```text
C:/Users/<user>/Cloud/StarshipHegemonyVault/
```

Possible synced providers:

- Google Drive
- Dropbox
- OneDrive
- Syncthing
- NAS SMB share

Do not put the active Git repo itself inside a cloud-sync folder unless the user explicitly accepts the risk.

## Proposed external vault layout

```text
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

## Steps

1. Create `Planning/gitrepoV2/EXTERNAL_ARTIFACT_POLICY.md`.

2. Document the vault layout.

3. Document that GitHub Issues should be preferred for bug screenshots tied to open issues.

4. Document that large videos and reproduction bundles should go to Releases or external storage.

5. Document that agent transcripts should not be tracked in Git by default.

6. Create an example config file in planning:

   ```text
   Planning/gitrepoV2/external_artifacts.example.json
   ```

   Suggested content:

   ```json
   {
     "external_artifact_root": "D:/StellarHegemonyVault",
     "screenshots": "screenshots",
     "videos": "videos",
     "agent_transcripts": "agent_transcripts",
     "repro_bundles": "repro_bundles",
     "generated_previews": "generated_previews"
   }
   ```

7. Later, in V2, create a local-only file ignored by Git:

   ```text
   external_artifacts.local.json
   ```

## Exit criteria

- [ ] External artifact policy documented.
- [ ] Vault structure documented.
- [ ] Example config created.
- [ ] Rule established: Git repo is not the artifact vault.

---

# Phase 7 — Curate planning and project history

## Objective

Keep the useful agent/project continuity without dragging all historical process debris into V2.

## Migration rules

### Migrate

- Current active project plans.
- Current architecture/design documents.
- Current conventions and patterns documents.
- Current agent instructions.
- Current long-term game design documents.
- Current migration plan.

### Do not migrate by default

- Deep archived projects.
- Raw consult logs.
- Raw agent transcripts.
- Generated reports.
- Fully completed old checklists.
- Historical temporary issue scaffolds.

### Maybe migrate after review

- Important decisions logs.
- Critical postmortems.
- Architecture audits still relevant to current source.
- Bug history that is not captured in GitHub Issues.

## Steps

1. Create `Planning/gitrepoV2/PLANNING_AND_PROJECTS_CURATION.md`.

2. List all planning/project directories from the inventory.

3. Classify them as:

   ```text
   Migrate
   External archive
   Do not migrate
   Needs user decision
   ```

4. For every `Migrate` item, add a one-sentence justification.

5. For every `External archive` item, identify the target vault location.

6. For every `Needs user decision` item, write a concise question.

7. Do not import deep archives until this curation file is complete.

## Exit criteria

- [ ] Planning/project curation file created.
- [ ] Active project material identified.
- [ ] Deep archive policy applied.
- [ ] User-decision items listed.

---

# Phase 8 — Curate assets

## Objective

Bring only useful runtime/final assets into V2, with LFS where appropriate.

## Steps

1. Create `Planning/gitrepoV2/ASSET_MIGRATION_PLAN.md`.

2. List all asset directories.

3. Classify each asset directory as:

   ```text
   Runtime required
   Final art but optional
   Generated preview
   Raw source art
   Test/reference asset
   External archive
   Do not migrate
   Needs user decision
   ```

4. For runtime assets, decide normal Git vs Git LFS.

5. For generated previews, default to external archive or no migration.

6. For raw source art, decide whether it should be in LFS, external vault, or a separate private asset repo.

7. Verify that all assets required for game startup remain available.

8. Verify that tests do not depend on ignored preview folders.

9. Identify missing asset fallback tests that should be added after migration.

## Exit criteria

- [ ] Asset migration plan created.
- [ ] Runtime asset set identified.
- [ ] Generated preview directories excluded.
- [ ] LFS asset set identified.
- [ ] Asset licensing concerns flagged.

---

# Phase 9 — Curate GitHub issues

## Objective

Preserve active bug/feature workflow while avoiding stale issue clutter in V2.

## Issue migration options

### Option A — manually recreate active issues

Best if the issue count is manageable.

### Option B — script issue migration through GitHub API

Best if many issues must move.

### Option C — keep issues in old repo and link from V2

Best if V2 is mostly source cleanup and old issue history remains valuable.

## Recommended approach

Use a hybrid:

1. Recreate only active/high-value issues in V2.
2. Add a backlink to the old issue.
3. Keep old repo issue history as archive.
4. Prefer uploading screenshots directly to the new issue rather than tracking screenshot files in the repo.

## Steps

1. Create `Planning/gitrepoV2/ISSUE_MIGRATION_PLAN.md`.

2. Export current open issue list.

3. Classify each issue as:

   ```text
   Recreate in V2
   Leave in old repo
   Close before migration
   Needs user decision
   ```

4. Prioritize high/correctness issues first.

5. For each issue recreated in V2, include:

   - original issue number,
   - original title,
   - short summary,
   - acceptance criteria,
   - old repo link,
   - screenshot links or re-uploaded screenshots.

6. Do not import low-value stale issues unless the user asks.

## Exit criteria

- [ ] Issue migration plan created.
- [ ] Open issues classified.
- [ ] High-priority issues selected for V2.
- [ ] Screenshot policy applied.

---

# Phase 10 — Create V2 repository

## Objective

Create the new clean repository with safe defaults before importing source.

## Steps

1. Create new GitHub repository:

   ```text
   StellarHegemony
   ```

2. Recommended initial visibility: private until the migration is validated.

3. Do not initialize with a README if performing a prepared local first commit, unless the workflow requires it.

4. Clone the empty repo locally outside any cloud-sync folder.

   Example:

   ```bash
   cd C:/Dev
   git clone https://github.com/ropesend/StellarHegemony.git
   cd StellarHegemony
   ```

5. Install Git LFS before adding assets:

   ```bash
   git lfs install
   ```

6. Add `.gitignore` and `.gitattributes` first.

7. Commit only repo hygiene files first:

   ```bash
   git add .gitignore .gitattributes README.md
   git commit -m "Initialize Stellar Hegemony repository hygiene"
   ```

## Exit criteria

- [ ] New repo created.
- [ ] Repo visibility chosen.
- [ ] Local clean clone exists.
- [ ] Git LFS installed.
- [ ] `.gitignore` committed before source import.
- [ ] `.gitattributes` committed before asset import.

---

# Phase 11 — Import source and tests

## Objective

Copy the core source tree into V2 without historical baggage.

## Steps

1. From a clean local copy of old repo, copy approved Bucket A folders into the V2 repo.

2. Start with source and tests only:

   ```text
   game/
   tests/
   data/
   docs/
   pyproject.toml
   ```

3. Do not copy assets yet unless required for import-time tests.

4. Run `git status` and inspect for accidental generated files.

5. Run a file count and size check before committing.

6. Commit source import:

   ```bash
   git add game tests data docs pyproject.toml
   git commit -m "Import current Stellar Hegemony source and tests"
   ```

7. Run focused smoke tests if dependencies are installed.

8. If tests fail due to missing assets, note that in `MIGRATION_LOG.md` and continue to asset import.

## Exit criteria

- [ ] Source copied.
- [ ] Tests copied.
- [ ] Data copied.
- [ ] Docs copied.
- [ ] No generated files accidentally staged.
- [ ] Source import committed.

---

# Phase 12 — Import assets using LFS/external rules

## Objective

Import only approved assets, with LFS where appropriate.

## Steps

1. Confirm `.gitattributes` is already committed.

2. Copy only approved runtime/final asset folders.

3. Run:

   ```bash
   git lfs status
   git status
   ```

4. Verify large binaries are recognized as LFS-tracked.

5. Check that generated preview folders are not staged.

6. Commit assets:

   ```bash
   git add assets
   git commit -m "Import approved runtime assets"
   ```

7. If any asset is too large or questionable, move it to the external vault or release plan instead of committing it.

## Exit criteria

- [ ] Approved assets copied.
- [ ] LFS tracking verified.
- [ ] Generated previews excluded.
- [ ] Asset import committed.

---

# Phase 13 — Import selected planning/project system

## Objective

Preserve agent continuity without importing every old artifact.

## Steps

1. Copy approved planning documents from `PLANNING_AND_PROJECTS_CURATION.md`.

2. Copy this `gitrepoV2` folder into the new repo as migration history.

3. Copy active project plans only.

4. Copy agent guidance files only after trimming them:

   - `AGENTS.md`
   - `CLAUDE.md`
   - Codex/OpenCode guidance
   - project protocol templates actually used by active workflows

5. Do not copy raw consult logs unless specifically approved.

6. Do not copy generated coordination summaries.

7. Commit:

   ```bash
   git add Planning Projects AgentCoordination AGENTS.md CLAUDE.md .codex
   git commit -m "Import curated planning and agent workflow docs"
   ```

## Exit criteria

- [ ] Planning docs curated.
- [ ] Active projects copied.
- [ ] Agent instructions copied and trimmed.
- [ ] Historical/generated process artifacts excluded.
- [ ] Planning import committed.

---

# Phase 14 — Fresh clone validation

## Objective

Prove V2 can be used from a new machine without hidden local state.

## Steps

1. Clone V2 into a new empty directory.

2. Confirm LFS files download correctly:

   ```bash
   git lfs pull
   ```

3. Create virtual environment.

4. Install dependencies according to the repo README.

5. Run import smoke test.

6. Run focused unit tests.

7. Run broader test suite if practical.

8. Launch the game if practical.

9. Record results in `Planning/gitrepoV2/POST_MIGRATION_VALIDATION.md`.

## Minimum validation checklist

- [ ] Fresh clone succeeds.
- [ ] LFS pull succeeds.
- [ ] Python environment creates cleanly.
- [ ] Dependencies install.
- [ ] Game imports without missing files.
- [ ] Focused tests pass.
- [ ] Game launches or known launch blockers are documented.
- [ ] No required files are being pulled from old repo local paths.

---

# Phase 15 — Multi-machine workflow validation

## Objective

Verify the migration actually improves the user's real workflow.

## Steps

1. Clone V2 on Machine A.

2. Clone V2 on Machine B.

3. Configure `external_artifacts.local.json` on each machine if used.

4. Confirm both machines can run tests from the same repo state.

5. Confirm agents can read the project guidance files.

6. Confirm generated/local agent files do not appear in `git status`.

7. Confirm screenshots/videos can be stored in the external vault or attached to issues.

8. Make a small test branch on Machine A.

9. Push it.

10. Pull it on Machine B.

11. Confirm no generated/local files conflict.

## Exit criteria

- [ ] Multi-machine clone works.
- [ ] Branch handoff works.
- [ ] Agent local files stay ignored.
- [ ] External artifacts accessible by intended method.

---

# Phase 16 — Old repo transition

## Objective

Make it clear which repo is canonical while preserving historical access.

## Steps

1. Add a notice to old `StarshipBattles` README once V2 is validated:

   ```text
   This repository is now a historical archive. Active development has moved to StellarHegemony.
   ```

2. Add a link to the new repo.

3. Decide whether to archive the old repo through GitHub settings.

4. If not archiving, at least reduce new active work in old repo.

5. Avoid merging new feature work into old repo after the transition date unless it is part of migration.

6. Keep old issues open only if they remain useful as historical references.

## Exit criteria

- [ ] Old repo archive notice added.
- [ ] New repo link added.
- [ ] Canonical development repo identified.
- [ ] Old repo archive decision made.

---

# Phase 17 — Post-migration cleanup and improvement

## Objective

Use the clean repo as the base for better workflow practices.

## Recommended follow-up tasks

1. Add GitHub issue templates:

   - bug report,
   - feature request,
   - agent task,
   - migration task.

2. Add PR template.

3. Add CI workflow for focused tests.

4. Add asset policy document.

5. Add `Tools/setup/bootstrap_windows.ps1`.

6. Add `Tools/setup/bootstrap_python.ps1` or equivalent.

7. Add `Tools/qa/collect_repro_bundle.py` that exports repro bundles to external storage, not Git.

8. Add `Tools/migration/check_repo_hygiene.py` to detect large non-LFS files and forbidden folders before commit.

9. Add pre-commit checks if the user wants them.

10. Add documentation for how future agents should create project folders without committing transient outputs.

## Exit criteria

- [ ] Basic CI exists or is explicitly deferred.
- [ ] Issue/PR templates exist or are explicitly deferred.
- [ ] Setup docs exist.
- [ ] Repo hygiene checks exist or are explicitly deferred.

---

# Agent operating rules for this migration

Future agents working on this migration should follow these rules:

1. Do not delete the old repo.
2. Do not rewrite old repo history unless explicitly instructed.
3. Do not migrate everything blindly.
4. Do not put the active Git repo inside Dropbox/Google Drive/OneDrive unless explicitly instructed.
5. Do not commit generated previews, raw transcripts, local scratchpads, or worktrees.
6. Do not use Git LFS as a dumping ground for constantly regenerated files.
7. Do not migrate commercial fonts or third-party assets without license review.
8. Do not mark the migration complete until a fresh clone can run the game/tests at least to the agreed validation level.
9. Prefer small, reviewable commits in the V2 repo.
10. Keep this plan updated as decisions change.

---

# Migration source snapshot

Fill this in when Phase 0 begins.

```text
Old repo: ropesend/StarshipBattles
Old default branch: main
Old source commit SHA: TBD
Migration started: TBD
Migration completed: TBD
New repo: TBD, likely ropesend/StellarHegemony
```

---

# Current status

```text
Status: Planning created; V1 asset cleanup substantially done in-place (2026-05-27);
        Stage 0 V2-repo work has not started.
Last reviewed: 2026-05-27
Next phase: Phase 0 — Safety and scope freeze (record source SHA, take backup snapshot)
Pre-migration asset cleanup (already complete in V1):
- snake_case asset folder names throughout (commits 327d6824b → 9aab233d7).
- stellar_objects/ grouping flattened (827a75124).
- flags/Processed/ collapsed (169e46b92).
- Master+regenerate derivative pipeline applied to components / flags / stars /
  planets (10829b2ed) and refactored into a shared engine (then per-family
  wrappers).
- ShipThemes moved under assets/images/ (8eb25514d); non-runtime
  Production/Original Art/processed_output/etc. dropped (e46116350).
- Stale asset_manifest.json sections + workflow leftovers (altcomponents,
  Cursor source image) cleaned up (9aab233d7).
- Test suite is derivative-state-independent (96df30384): unit tests pass on
  a fresh checkout without first running ensure_*_derivatives().
Blocking user decisions (proposed direction documented in STAGE_0_DECISIONS.md):
- Exact V2 repository name (proposed: StellarHegemony)
- Public vs private initial V2 repo visibility (proposed: Private)
- Whether to archive old repo after validation (proposed: only after user approval)
- External artifact vault provider/location (proposed: Google Drive)
- Asset / LFS policy (proposed: LFS for canonical images & audio, local cache
  for scaled variants — note: master sizes only; derivatives regenerate locally)
- Issue migration policy (proposed: resolve/archive most old issues first,
  minimal migration)
```

`STAGE_0_DECISIONS.md` is the canonical place to track per-item status (`settled` / `proposed` / `deferred`). Keep this status block in sync with that file when items move from `proposed` to `settled`.
