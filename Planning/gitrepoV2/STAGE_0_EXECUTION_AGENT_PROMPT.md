# Stage 0 Execution — New Agent Prompt (Phases 10–14)

> Hand this to a fresh Claude Code session when you're ready to **execute** the
> V2 repository cutover. This prompt is the execution-half counterpart to
> [`STAGE_0_NEW_AGENT_PROMPT.md`](STAGE_0_NEW_AGENT_PROMPT.md), which covered
> the planning-half (Tasks A–D). All Stage 0 decisions are now settled; the
> drafts in [`Planning/gitrepoV2/`](.) are the source of truth.
>
> Adapt for Codex / OpenCode by rephrasing the `TodoWrite` / `AskUserQuestion`
> surfaces; the substance is portable.

---

## Your role

You are picking up **Stage 0 execution** for the Starship Battles →
StellarHegemony migration. The planning pass is finished (commit
`be8049cf8` on `main`). Your job is to **create the V2 repository
locally, populate it with curated V1 content + LFS-tracked assets,
push it to a new private GitHub repo, and validate that a fresh clone
of V2 works**. Phases 15 (multi-machine), 16 (V1 archive notice), and
17 (post-migration polish) are out of scope — they have their own gates.

You are working interactively on Windows 11. Use `AskUserQuestion`
whenever a step has user-gated implications. Use `TodoWrite` to track
the multi-phase work. Use the Bash tool (POSIX shell) for `git`,
`cp -r`, and validation scripts; use PowerShell for Windows-specific
file operations only when Bash is inconvenient.

## Local working-tree layout

```text
C:\Dev2\StarshipBattles\        # V1 (read-mostly during this work; the source)
C:\Dev2\StellarHegemony\        # V2 (you create + populate this)
<vault-root>                     # Google Drive vault path; see EXTERNAL_ARTIFACT_POLICY.md
```

The V2 path is deliberately outside any cloud-sync folder per
`STAGE_0_DECISIONS.md`. **The active V2 Git checkout must not live
inside Google Drive / OneDrive / Dropbox.** If `C:\Dev2\StellarHegemony`
turns out to be under a cloud sync, stop and surface that to the user
before any `git init` or clone.

## Read order

Read these in this order; do not re-derive what they already document:

1. `AGENTS.md` — non-negotiable repo rules.
2. `CLAUDE.md` — Claude-Code-specific delta over `AGENTS.md`.
3. **`Planning/gitrepoV2/STAGE_0_DECISIONS.md`** — every Task D row is now `settled 2026-05-25`. This is the source of truth for V2 name, visibility, LFS policy, vault provider, issue policy, curation boundaries, etc.
4. **`Planning/gitrepoV2/V2_IMPORT_CHECKLIST.md`** — your phase-by-phase command source of truth. Read end-to-end before starting.
5. `Planning/gitrepoV2/V2_GITIGNORE_DRAFT.md` — the literal V2 `.gitignore` you'll write in Phase 10 step 4.
6. `Planning/gitrepoV2/V2_GITATTRIBUTES_DRAFT.md` — the literal V2 `.gitattributes` you'll write in Phase 10 step 4.
7. `Planning/gitrepoV2/V2_FOLDER_STRUCTURE.md` — target V2 tree shape (verifiable post-import).
8. `Planning/gitrepoV2/MIGRATION_CLASSIFICATION.md` — IMPORT_GIT / IMPORT_LFS / VAULT / SKIP for every V1 path. Authoritative when V2_IMPORT_CHECKLIST.md is ambiguous.
9. `Planning/gitrepoV2/EXTERNAL_ARTIFACT_POLICY.md` — Google Drive vault layout + cutover sequence + per-machine config schema.
10. `Planning/gitrepoV2/MIGRATION_SOURCE_SNAPSHOT.md` — V1 source SHA (`bc755f012`) + `.git` pack metrics + working-tree snapshot at the moment the cutover was authorized.
11. `Planning/gitrepoV2/inventory_post_cleanup.md` — projected V2 size (~150 MiB plain Git + ~4.1 GiB LFS + ~528 MiB vault seed).

You can skim the original `STAGE_0_NEW_AGENT_PROMPT.md` and `STAGE_0_PLAN.md` / `DETAILED_MIGRATION_PLAN.md` for historical context, but **the settled rows in `STAGE_0_DECISIONS.md` and the checklists in `V2_IMPORT_CHECKLIST.md` win** if there's any conflict with older prose.

## Conflict resolution

- **`AGENTS.md`** wins for non-negotiable process rules (TDD, root-cause fixes, etc.).
- **The live V1 tree** wins for "what content actually exists." If `MIGRATION_CLASSIFICATION.md` references a path that turns out not to exist in V1 today, the live tree wins — drop the reference and tell the user.
- **`STAGE_0_DECISIONS.md`** wins over any older Stage 0 prose for settled-row content.
- **`V2_IMPORT_CHECKLIST.md`** wins for "what's the actual command for this phase."

## Authorization matrix

| Action | Status |
|---|---|
| Run `gh repo create ropesend/StellarHegemony --private ...` | **Ask first.** The user creates the GitHub repo. You may suggest the exact command, but do NOT run it autonomously. |
| Run `git init`, `git lfs install`, `git add`, `git commit` inside `C:\Dev2\StellarHegemony` | **Authorized.** Local V2 work. |
| Run `git remote add origin ...`, `git push -u origin main` | **Ask first** on the first push. Subsequent pushes during this same session are authorized once the user has confirmed the remote is correct. |
| Run `git lfs pull`, `git lfs status`, `git lfs ls-files` | **Authorized.** Read/sync LFS. |
| Run any `git filter-repo`, `bfg`, `git lfs migrate`, `git reset --hard`, force-push | **Forbidden.** Stage 0 is a clean cutover; no history rewrite. |
| Delete tracked content from V1 (`C:\Dev2\StarshipBattles`) | **Forbidden** unless the user explicitly asks. V1 remains intact until validation completes. |
| Archive V1 on GitHub | **Forbidden in this session.** Phase 16 gate; user-triggered after V2 is validated. |
| Copy V1 content to V2 via `cp -r` | **Authorized.** That's the work. |
| Copy V1 SKIP-to-VAULT content to the Google Drive vault | **Ask first** — the user supplies the actual vault root path. Then authorized. |
| Run smoke tests / launch the game in V2 | **Authorized** (Phase 14). |
| Edit `Planning/gitrepoV2/` planning artifacts in V1 | **Allowed sparingly** — only if you discover the drafts are wrong about something material. Surface the discrepancy to the user first. |
| Edit code/docs/data in V2 | **Forbidden.** V2 is a verbatim curated copy of V1 at the cutover SHA; do not re-architect anything. The single exception is the `pyproject.toml` `name = "stellar-hegemony"` edit and the placeholder `README.md` Phase 13.5 calls for. |

## What's already settled (don't re-litigate)

From `STAGE_0_DECISIONS.md`, all rows are `settled 2026-05-25`:

- V2 repo: **`StellarHegemony`** (CamelCase), **private**.
- LFS policy: **path-scoped**, per `V2_GITATTRIBUTES_DRAFT.md`. Confirmed via codex consult.
- GitHub plan tier: **Free/Pro** (10 GiB storage + 10 GiB/mo bandwidth). Bandwidth is the binding constraint — avoid routine full `git lfs pull` on CI or scratch checkouts.
- Vault provider: **Google Drive**. Layout in `EXTERNAL_ARTIFACT_POLICY.md`.
- Issue migration: resolve/archive most V1 issues first; recreate only active high-value ones in V2 with backlinks. **Out of scope for THIS prompt** — Phase 9 happens in parallel or before, not as part of execution.
- Old-repo handling: leave V1 unarchived until V2 validated. **No V1 archive in this session.**
- `Reviews/`: import top-level only; `results/` to vault.
- `Projects/active_projects/` content: **drop everything** (PROJ-481..499 + Batch + _doc_consolidation) to vault. V2 ships with `Projects/active_projects/` empty (plus the README placeholder that the checklist generates).
- `Projects/` infrastructure (README, index, protocols, gp_protocols): keep as scaffolding.
- `AgentCoordination/protocols/`: all six files imported.
- `AgentCoordination/templates/`: does not exist in V1; references already removed from planning docs. Do not create.

## Phase-by-phase walkthrough

### Phase 10 — Create V2 repository

1. Pre-check: verify V1 working tree is clean.
   ```bash
   cd C:/Dev2/StarshipBattles
   git status --short        # expect empty
   git rev-parse HEAD         # expect bc755f012... (or later if more planning commits land)
   git count-objects -vH      # capture current pack metrics for the log
   ```
2. **Ask the user** for confirmation that they want to proceed with `gh repo create`. Propose the exact command:
   ```bash
   gh repo create ropesend/StellarHegemony --private --description "Stellar Hegemony — clean V2 of Starship Battles"
   ```
   Wait for explicit user "yes" before running. If they prefer to run it themselves, that's fine — wait for them to confirm the repo exists, then move on.
3. Clone the empty repo:
   ```bash
   cd C:/Dev2
   git clone https://github.com/ropesend/StellarHegemony.git
   cd StellarHegemony
   git lfs install
   ```
   **Verify:** `C:\Dev2\StellarHegemony` is NOT under any cloud-sync folder (`echo $env:USERPROFILE` and check; if user's Google Drive sync uses an unusual path, ask).
4. Write the V2 `.gitignore` (verbatim from `V2_GITIGNORE_DRAFT.md`'s code block), `.gitattributes` (verbatim from `V2_GITATTRIBUTES_DRAFT.md`'s code block), and a placeholder `README.md`. Then:
   ```bash
   git add .gitignore .gitattributes README.md
   git commit -m "Initialize Stellar Hegemony repository hygiene (from V1 SHA <V1-HEAD>)"
   ```
   Do NOT push yet.

### Phase 11 — Source import

Run the commands in `V2_IMPORT_CHECKLIST.md` Phase 11. Use `C:/Dev2/StarshipBattles` as `<v1-checkout>` and `C:/Dev2/StellarHegemony` as `<v2-checkout>`. Notable details:

- `cp -r` on Windows works via Git Bash / WSL; if you're using PowerShell, prefer `Copy-Item -Recurse -Force`.
- After copying `combat_lab/`, delete `battle.log`, `battle_states/`, `test_history/` from V2 even though they're gitignored — keeps `git status` clean.
- Edit `pyproject.toml` to set `name = "stellar-hegemony"` (and verify nothing else needs updating for the rename).
- Run the verification commands in V2_IMPORT_CHECKLIST.md's "Verify before commit" block.
- Commit:
  ```bash
  git commit -m "Import V1 source, tests, data, docs, combat_lab, Tools (from <V1-HEAD>)"
  ```

### Phase 12 — Asset import (LFS-routed)

Run `V2_IMPORT_CHECKLIST.md` Phase 12. Critical verifications:

- `git lfs status` should show every master-size PNG/JPG routed through LFS, not plain Git.
- `git lfs ls-files | wc -l` should land near 1,400 (per `inventory_post_cleanup.md`'s projection).
- `git check-attr filter assets/images/ship_themes/Federation/theme.json` should print `filter: unspecified` (JSON metadata stays plain Git).
- No file under `assets/images/components/{64,128,256,512,2048}/`, `assets/images/flags/flag_*/{32,64,128,256,512}/`, `assets/images/stars/{128,256,512}/`, or `assets/images/planets/{128,256,512,1024}/` should be present (those are gitignored, but spot-check).

Commit:
```bash
git commit -m "Import V1 runtime assets via LFS (from <V1-HEAD>)"
```

### Phase 13 — Curated import (Planning, Projects, AgentCoordination, Reviews, tracking-assets, dotfile dirs)

**Vault step first** — copy V1's SKIP-to-VAULT buckets to Google Drive. **Ask the user for the absolute vault root path** (e.g. `G:/My Drive/StellarHegemonyVault`). Then run:

```bash
VAULT="<user-supplied-vault-root>"
mkdir -p "$VAULT/old_repo_exports/v1_projects_deep_archive"
mkdir -p "$VAULT/old_repo_exports/v1_active_projects"
mkdir -p "$VAULT/old_repo_exports/v1_legacy_tickets"
mkdir -p "$VAULT/old_repo_exports/v1_reviews_results"
mkdir -p "$VAULT/repro_bundles/v1_tracking_logs"

cp -r C:/Dev2/StarshipBattles/Projects/deep_archive/*                          "$VAULT/old_repo_exports/v1_projects_deep_archive/"
cp -r C:/Dev2/StarshipBattles/Projects/active_projects/PROJ-*                  "$VAULT/old_repo_exports/v1_active_projects/"
cp    C:/Dev2/StarshipBattles/Projects/active_projects/Batch_*_Prompt.txt      "$VAULT/old_repo_exports/v1_active_projects/" 2>/dev/null || true
cp -r C:/Dev2/StarshipBattles/Projects/active_projects/_doc_consolidation      "$VAULT/old_repo_exports/v1_active_projects/" 2>/dev/null || true
cp -r C:/Dev2/StarshipBattles/AgentCoordination/legacy_tickets/*               "$VAULT/old_repo_exports/v1_legacy_tickets/"
cp -r C:/Dev2/StarshipBattles/Reviews/results/*                                "$VAULT/old_repo_exports/v1_reviews_results/"
cp -r C:/Dev2/StarshipBattles/tracking-assets/logs/*                           "$VAULT/repro_bundles/v1_tracking_logs/"
```

Then verify in Google Drive that the upload completes before continuing.

Optional but recommended: also seed `<vault>/old_repo_exports/v1_full_clone/` with a bare clone of V1 at the cutover SHA for forensic access:
```bash
cd "$VAULT/old_repo_exports"
git clone --bare C:/Dev2/StarshipBattles v1_full_clone
```

Then run the V2 import side per `V2_IMPORT_CHECKLIST.md` Phase 13. Includes:
- `Planning/` (drop empty `CURRENT_STATE.md` scaffolds; drop `STAGE_0_NEW_AGENT_PROMPT.md` + `STAGE_0_EXECUTION_AGENT_PROMPT.md` — those are V1-only onboarding artifacts).
- `Projects/` infrastructure only (no active_projects content; generates an `active_projects/README.md` placeholder).
- `AgentCoordination/` README + protocols + discovered_issues only.
- `Reviews/` top-level only.
- `tracking-assets/` README + projects + screenshots only.
- `.github/`, `.codex/config.toml`, `.claude/skills + settings.example.json`, `.agent/skills`, `.agents/`, `.opencode/commands + skills + package*.json`.

Verify the "must not enter V2" sweep block from `V2_IMPORT_CHECKLIST.md`. Any FAIL halts the import.

Commit:
```bash
git commit -m "Import V1 planning, projects, agent config (curated; from <V1-HEAD>)"
```

### Phase 13.5 — V2-specific tracked files

Write a fresh `README.md` (more substantial than the Phase-10 placeholder) and `external_artifacts.example.json` per `V2_IMPORT_CHECKLIST.md` Phase 13.5. Commit:

```bash
git commit -m "Add V2 top-level README + external-artifact example config"
```

### Phase 14 — Fresh clone validation

**This is the gate that decides whether V2 is canonical.**

1. **Ask the user** to confirm push authorization. Then:
   ```bash
   cd C:/Dev2/StellarHegemony
   git push -u origin main      # first push; expect 4+ GiB of LFS upload
   ```
   Monitor `git lfs push` progress; this may take several minutes on a typical home connection.
2. After push completes, clone V2 into a separate validation directory:
   ```bash
   mkdir C:/Dev2/StellarHegemonyValidate
   cd C:/Dev2/StellarHegemonyValidate
   git clone https://github.com/ropesend/StellarHegemony.git .
   git lfs pull
   ```
3. Validate:
   - Python venv creates cleanly (`python -m venv .venv`).
   - Dependencies install (`pip install -r requirements.txt -r requirements-dev.txt`).
   - Game imports without missing files (`python -c "import game"`).
   - Focused smoke tests pass (`python Tools/test_sharded/test_sharded.py` — long, or a targeted subset).
   - Game launches or known launch blockers are documented (`python launcher.py`).
   - `git status` shows clean tree.
   - `git ls-files | wc -l` close to ~12,000 (V2 file count).
4. Write `Planning/gitrepoV2/POST_MIGRATION_VALIDATION.md` in V2 with results. Commit + push. (This is the only V2 planning-artifact edit you do; treat it as the validation receipt.)

## Open carry-over items from the planning pass

These came up during planning but were deferred to execution-time judgment:

1. **DI-2026-05-26-001** — accidentally-tracked V1 tool output (`--help/`, `--output-dir/`, `.coverage`, `panel_profile.prof`, `test_profiling_*.json*`). They're all SKIP-classified for V2 (won't enter V2 anyway). Optional cleanup commit in V1 before cutover; ask the user if they want it done.
2. **`profiling/`** top-level directory in V1 — content not audited during planning. Read its contents during Phase 11; if it's an empty scaffold or stale, drop. If it has real content, treat as IMPORT_GIT.
3. **`Projects/protocols/` and `Projects/gp_protocols/`** — referenced by `CLAUDE.md` but not enumerated in the planning inventory. Verify they exist and copy their content during Phase 13.
4. **`Projects/archived_projects/`** — listed in the prompt's SKIP set but may not exist in V1. Run `ls C:/Dev2/StarshipBattles/Projects/archived_projects 2>/dev/null` first; if it exists, vault it; if not, skip.
5. **`.github/`** content audit — verify whether V1's `.github/ISSUE_TEMPLATE/` and `.github/workflows/` are still current; outdated workflows may need a Phase 17 refresh, but for THIS pass copy verbatim and flag any obviously stale items.
6. **`tracking-assets/screenshots/`** content sweep — verify LFS routing matches expected file sizes. If anything is < 50 KB and clearly not benefiting from LFS, that's fine (the `.gitattributes` rule is harmless overhead for tiny files); if anything is suspiciously huge, surface to user.

## What you are NOT allowed to do

- **No history rewrite.** No `git filter-repo`, `bfg`, `git lfs migrate`, force-push, `git reset --hard` against a published branch.
- **No V1 destructive operations.** `git rm` in V1 only with explicit user authorization (and ideally as a follow-up commit, separate from V2 work).
- **No V1 archive.** GitHub repo archival of `ropesend/StarshipBattles` is a separate user-gated step after this session.
- **No code/data/docs re-architecture in V2.** V2 is a verbatim curated copy of V1 at the cutover SHA. The single permitted edits are the `pyproject.toml` name swap, the placeholder `README.md`, the `external_artifacts.example.json`, and the `Planning/gitrepoV2/POST_MIGRATION_VALIDATION.md` validation receipt.
- **No skipping the gitignore + gitattributes first-hygiene commit.** They must land BEFORE any source or asset import, or LFS routing won't trigger and you'll have to redo it.
- **No `gh repo create` without explicit user yes.** Suggest the command, wait for confirmation.
- **No push without explicit user yes** for the first push.
- **No V2 work inside a cloud-sync folder.** If `C:\Dev2\StellarHegemony` turns out to be inside Google Drive / OneDrive / Dropbox, stop.

## Working norms

- Use `TodoWrite` to track the phase progression. Mark items completed in real time.
- Surface user-gated decisions via `AskUserQuestion`. Recommended option first.
- Commits per phase. Don't squash phase commits — the user reviews them individually.
- Per the discovered-issues policy in `CLAUDE.md`: if you notice an out-of-scope V1 bug while doing this work, log it via `/claude-di-log` and keep going. **Do not detour to fix V1 bugs during V2 cutover.** Exception: a bug that breaks the cutover itself (e.g. `pyproject.toml` is malformed) gets fixed as a small standalone V1 commit before continuing.
- For long-running operations (`git push`, `git lfs pull`, full test suite): run in background where possible (`run_in_background=true`) and check back when the user signals or the harness re-invokes you.
- If validation in Phase 14 fails, do NOT try to "fix V2 in place" by patching. Identify the missing/broken content, surface to user, and either re-run the affected import phase or schedule a follow-up commit. V2 history can grow forward; it cannot be rewritten.

## Success criteria

Stage 0 execution is complete (within this prompt's scope) when:

- `ropesend/StellarHegemony` exists on GitHub, private. ✓
- `C:\Dev2\StellarHegemony` exists locally outside cloud sync. ✓
- V2 first hygiene commit (.gitignore + .gitattributes + placeholder README) landed. ✓
- V1 source/tests/data/docs/combat_lab/Tools imported (Phase 11). ✓
- V1 assets imported with LFS (Phase 12). ✓
- V1 SKIP-to-VAULT content uploaded to Google Drive (Phase 13 prerequisite). ✓
- V1 curated planning/projects/agent-config imported (Phase 13). ✓
- V2-specific tracked files authored (Phase 13.5). ✓
- V2 pushed to GitHub. ✓
- Fresh clone in `C:\Dev2\StellarHegemonyValidate` succeeds and passes smoke tests + game launches (Phase 14). ✓
- `Planning/gitrepoV2/POST_MIGRATION_VALIDATION.md` written in V2 documenting the validation result. ✓

What's still **out of scope** after success:

- Phase 15 (multi-machine validation). Gate: user has a second machine ready.
- Phase 16 (V1 archive notice + GitHub archive). Gate: explicit user approval.
- Phase 17 (post-migration polish: CI workflows, issue templates, PR template, bootstrap scripts). Separate prompt.

## First turn

1. Confirm you've read the **Read order** list and the **Authorization matrix**.
2. Run the three non-mutating baseline commands to ground yourself:
   ```bash
   cd C:/Dev2/StarshipBattles
   git status --short
   git rev-parse HEAD
   git count-objects -vH
   ```
   Note the current HEAD; if it has moved past `bc755f012`, that's the new cutover SHA. Update the snapshot file or surface the change.
3. Confirm `C:\Dev2\StellarHegemony` does not yet exist (`ls C:/Dev2 | grep StellarHegemony` should print nothing). If it does, ask the user what state it's in before touching it.
4. Confirm `gh` CLI is installed and authenticated: `gh auth status`.
5. Then ask the user: **"Ready to start Phase 10 (create the V2 GitHub repo)? Confirm the `gh repo create` command I should propose, and the absolute path of your Google Drive vault root for Phase 13."**

Do not start any phase commands until the user has answered.
