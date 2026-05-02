# Support Systems Cleanup Plan

Author: Claude Code (Opus 4.7, 1M context)
Date created: 2026-04-29
Status: Proposed — awaiting user sign-off on Phase 0 decisions
Source critical review: [`support_systems_critical_review.md`](support_systems_critical_review.md)

This plan is the actionable response to the critical review of the
repository's support systems. It is written for handoff: any agent picking it
up cold should be able to read this document plus the critical review and
execute without further context from chat.

The plan is **not** about game code. Every change is in process/tooling
infrastructure (`AgentCoordination/`, `Projects/`, `Tracking/`, `Reviews/`,
`Tools/`, `*/skills/`, the three adapter files, `docs/`).

---

## 1. Goals

By plan completion the repository will have:

1. **One clear status per support subsystem.** Loops, reviews, tracking,
   tools — every directory either presents itself as actively maintained or
   is moved into a clearly-marked archive.
2. **No stale "in progress" state files.** No JSON status files claiming a
   process is running when it stopped 75 days ago. No reviews idle since
   January.
3. **Adapter docs at their target sizes.** `CLAUDE.md` ≤ 120 lines (target
   80) with reinforcement markers retained. `AGENTS.md` and `.agents/CODEX.md`
   already meet target.
4. **Every tool documented and located correctly.** `Tools/README.md`
   matches the filesystem; no loose `.py` files at the top level; redundant
   tools labeled or removed.
5. **Validator catches regressions.** New checks added so future audits are
   automated: SLA on `In Progress` reviews, skill-content divergence between
   `.claude/skills/` and `.agent/skills/`, presence of expected READMEs.
6. **Clean test status.** All 161+ coordination tests still green; full
   sharded suite green; baseline updated.

## 2. Non-goals

- **No changes to `game/` code.** The cleanup is process-only.
- **No new features.** The agent coordination tooling stays as it is — only
  net-additive checks and net-subtractive deletions.
- **No retroactive rewriting** of `Projects/archived_projects/` or
  `Projects/deep_archive/` — those are historical and should not change.
- **No migration of `Reviews/results/`** beyond closing stale entries —
  individual review result folders stay where they are.
- **No removal of the agent coordination tooling itself** — `Tools/agent_coordination/`,
  the validator, the sanitizer, the prefix renamer, the usage counters, and
  the hook adapter are all current and stay.

## 3. Branch strategy

- New branch off current head: `cleanup/support-systems`. Do not work on
  `main` directly.
- One commit per phase below. Some phases produce two or three commits if
  the diff is large enough that smaller commits help review.
- Run `python Tools/agent_coordination/validate_agent_surfaces.py` before
  every commit. It must exit 0.
- Run focused tooling tests (`python -m pytest tests/unit/tools/ -q`) after
  any phase that touches `Tools/agent_coordination/`. Must be green.
- Run the full sharded suite (`python Tools/test_sharded/test_sharded.py
  --refresh-baseline-timestamp`) before merging back to `main`. Must be
  green or have only known flakes.

## 4. Phase 0 — User decisions required

These items block everything downstream. Surface to user before starting any
later phase.

| # | Decision | Options | Default if user is unreachable |
|---|---|---|---|
| 0.1 | Three abandoned loops in `Projects/` | (a) revive one (which?) with locking + tests; (b) archive all three to `Projects/_archive/automated_loops/`; (c) delete from working tree (git history retains) | (b) archive all three |
| 0.2 | Antigravity skill mirror | (a) build a generator that produces `.agent/skills/anti-*` from `.claude/skills/claude-*` with frontmatter normalization; (b) prune `.agent/skills/` to ~6 skills Antigravity actually uses (asset generation, browser/UI, tooling); (c) keep current 33 hand-maintained parallel copies | (b) prune to ~6 |
| 0.3 | The `Sweep` sub-system | (a) write the missing protocol + document Sweep formally in `Reviews/`; (b) delete the 8 Sweep prompts and remove all Sweep entries from `reviews_index.md` | (b) delete |
| 0.4 | Stale `In Progress` reviews older than 60 days | (a) bulk-close as `Abandoned` with one-line reason; (b) bulk-close as `Archived`; (c) prune entirely from index and move folders to `Reviews/_archive/` | (a) close as Abandoned |
| 0.5 | `Tools/migrate_ai_strategy.py` | (a) delete (migration is complete); (b) keep + move into a subdirectory with a `COMPLETED.md` note | (a) delete |
| 0.6 | `Tools/background_eraser/` | (a) delete (minimal value; just an asset browser); (b) keep | (a) delete |
| 0.7 | `Tools/captioning/` | (a) move to `docs/guides/captioning.md` (no Python entry point); (b) keep in `Tools/` | (a) move to docs |

If the user explicitly directs "use defaults," proceed with the defaults
above. Otherwise wait for an answer per item.

## 5. Phase plan

Phases are ordered by dependency and risk. Each phase has its own commit and
its own verification gate.

### Phase 1 — Quiet deletions (low risk, no logic changes)

**Scope**

- Delete `Tracking/prompts/` (or move to `Tracking/_legacy/` with a
  `DELETE_BY_2026-09-01.md`). README already calls these "legacy."
- Delete `Projects/Triage/fleet_system_review.md` if not converted to a
  PROJ. (Confirm with user if it is the only file in `Triage/`; if so,
  remove the directory too.)
- Delete `Tools/migrate_ai_strategy.py` (per Phase 0.5).
- Delete `Tools/background_eraser/` (per Phase 0.6).
- Move `Tools/captioning/` → `docs/guides/captioning.md` (per Phase 0.7).
- Move `Tools/check_file_size.py` → `Tools/check_file_size/check_file_size.py`
  with a 5-line README.

**Touched files**

- `Tracking/prompts/*.txt` (delete)
- `Projects/Triage/fleet_system_review.md` (delete or convert)
- `Tools/migrate_ai_strategy.py` (delete)
- `Tools/background_eraser/**` (delete)
- `Tools/captioning/**` → `docs/guides/captioning.md` (move + flatten)
- `Tools/check_file_size.py` → `Tools/check_file_size/` (move + add README)
- `Tools/README.md` (update inventory: remove deleted, relocate moved)
- `Tracking/README.md` (drop the legacy-prompt line)

**Verification**

- `python Tools/agent_coordination/inventory_agent_surfaces.py` regenerates
  cleanly.
- `python Tools/agent_coordination/validate_agent_surfaces.py` exits 0.
- `python -m pytest tests/unit/tools/ -q` passes.
- `git status` shows only the expected deletions/moves.

**Commit message template**

```
chore(cleanup): Phase 1 — remove legacy prompts, completed migration, dead tools

- Tracking/prompts/ removed; README already marked these legacy in favor
  of /claude-ticket-* skills.
- Projects/Triage/fleet_system_review.md removed; not converted to a PROJ
  in 38 days.
- Tools/migrate_ai_strategy.py removed; the schema migration completed
  before this PR.
- Tools/background_eraser/ removed; was an asset browser with no
  processing logic.
- Tools/captioning/ moved to docs/guides/captioning.md; it never had a
  Python entry point.
- Tools/check_file_size.py moved into Tools/check_file_size/ subdir per
  Tools/README.md convention.
- Tools/README.md inventory updated.
```

### Phase 2 — Stale review cleanup

**Scope**

- Read `Reviews/reviews_index.md` and identify every entry with status
  `In Progress` whose date is older than 60 days from today.
- For each, set status to `Abandoned: stale > 60 days, no recent activity`
  (per Phase 0.4 default).
- Update `reviews_index.md` with the new statuses; keep the date and
  finding count as historical record.
- Do **not** delete anything under `Reviews/results/`. The per-review
  folders remain as a research archive; only the index status changes.

**Touched files**

- `Reviews/reviews_index.md` (status updates)

**Verification**

- Visual review of the diff — every `In Progress` → `Abandoned` change
  should be on a row dated > 60 days ago.
- Validator green.

**Commit message template**

```
chore(reviews): Phase 2 — close 44 stale "In Progress" reviews

Status updated from "In Progress" to "Abandoned" for reviews dated
2026-01-23 through 2026-02-27 (>60 days idle). Result folders under
Reviews/results/ remain as research archive. SLA enforcement to follow
in a later phase.
```

### Phase 3 — Sweep decision and action

**Scope (default per Phase 0.3 = delete)**

- Delete the 8 `Reviews/Prompts/Sweep - *.txt` files.
- Remove every "Sweep Review" row from `Reviews/reviews_index.md`.
- Add a short note in `Reviews/README.md` (created in Phase 7 below)
  explaining that Sweep was an experimental codebase-wide review type from
  Feb 2026 that was retired.

**Alternative (if Phase 0.3 = formalize)**

- Create `Reviews/protocols/11_sweep_review.md` documenting the
  multi-agent sweep workflow.
- Add a `Sweep Review` section to `reviews_index.md` schema documentation.
- Cross-reference each Sweep prompt to the new protocol.

**Touched files**

- `Reviews/Prompts/Sweep - *.txt` (delete OR cross-link)
- `Reviews/reviews_index.md` (purge OR document)
- `Reviews/protocols/11_sweep_review.md` (only if formalizing)

**Verification**

- Validator green.
- `grep -ri "sweep" Reviews/` shows expected residue only.

### Phase 4 — Loop archival or revival

**Scope (default per Phase 0.1 = archive)**

- Create `Projects/_archive/automated_loops/` directory.
- Move `Projects/refactor_loop/`, `Projects/complexity_loop/`, and
  `Projects/continuous_loop/` into it.
- Write `Projects/_archive/automated_loops/README.md` (~150 lines)
  containing:
  - One paragraph each on what the loop did, when it ran, what it
    achieved, why it stopped.
  - The decision date and the decision-maker (user).
  - Pointer to the relevant `cycle_state.json` files for anyone who wants
    to inspect.
- Update `Projects/README.md` to remove references to the loops as if
  they were active.

**Alternative (if Phase 0.1 = revive one)**

- Pick the chosen loop. Implement:
  - File-locking on `Projects/active_projects/PROJ-XXX/plan.md` writes.
  - Reservation of project IDs.
  - Pre-flight check: refuse to start if another loop's `cycle_state.json`
    is in `executing` state.
  - Unit tests for the new locking and reservation logic.
- Archive the other two loops as in the default.

**Touched files**

- `Projects/refactor_loop/**`, `Projects/complexity_loop/**`,
  `Projects/continuous_loop/**` (move)
- `Projects/_archive/automated_loops/` (new)
- `Projects/README.md` (de-reference loops)
- Possibly `Projects/protocols/08_automated_loop_protocol.md` (mark
  archived if all three loops are gone)

**Verification**

- Validator green.
- No references to `Projects/refactor_loop/` etc. in any current README,
  protocol, or skill outside the archive directory.
  - Quick check: `grep -rn "refactor_loop\|complexity_loop\|continuous_loop" --include='*.md' --include='*.py' . | grep -v _archive | grep -v archived_projects | grep -v deep_archive`

### Phase 5 — AgentCoordination archive cleanup

**Scope**

- Create `AgentCoordination/_archive/` directory.
- Move into it the 18 historical review files:
  - `claude_code_agent_coordination_*.md` (4 versions of comments + V2/V3/V4 review files)
  - `opencode_deepseek_v4_pro_agent_coordination_*.md` (3 versions)
  - `antigravity_agent_coordination_*.md` (3 versions)
  - `claude_code_agent_coordination_v[2-4]_comments.md`
  - `claude_code_baseline_inventory_review.md`
  - `opencode_deepseek_baseline_inventory_review.md`
  - `opencode_deepseek_implementation_review.md`
  - `codex_agent_coordination_system_review.md`
  - `codex_agent_coordination_claim_responses.md`
  - `codex_agent_coordination_plan_v[2-4].md`
  - `codex_agent_coordination_plan.md` (V1)
- Keep at top level: `codex_agent_coordination_plan_final.md`, `README.md`,
  `SKILL_RENAMES.md`, `skill_rename_map.toml`, `user_response.md`,
  `support_systems_critical_review.md`, this plan file, `generated/`.
- Add `AgentCoordination/_archive/README.md` with a one-paragraph index of
  the archived files.
- Update `AgentCoordination/README.md` to reflect the new structure (the
  current README mentions `*_v[1-4]_*.md` as historical; rewrite to point
  at `_archive/`).

**Touched files**

- 18 files moved into `AgentCoordination/_archive/`
- `AgentCoordination/_archive/README.md` (new)
- `AgentCoordination/README.md` (path updates)

**Verification**

- `ls AgentCoordination/*.md | wc -l` returns ≤ 6.
- Validator green (the legacy-slash check excludes `AgentCoordination/`
  but verify anyway).
- No skill or doc references the moved files except the new archive
  README.

### Phase 6 — CLAUDE.md trim

**Scope**

- Reduce CLAUDE.md from 377 lines to ≤ 120 lines (target 80).
- Replace each section that duplicates `AGENTS.md` content with a
  reference: `See AGENTS.md §"<heading>".`
- Keep verbatim:
  - The `## Skill Usage Logging` block (Claude-specific).
  - The `## Subagent Report Output` block (Claude-specific).
  - The interactive-mode framing at the top.
  - All four reinforcement markers (`tdd`, `docs-first`,
    `code-doc-consistency`, `root-cause`, `no-ignore-folder`).
- Use `@AGENTS.md` import at the top of CLAUDE.md to inherit shared rules.

**Touched files**

- `CLAUDE.md`

**Verification**

- `wc -l CLAUDE.md` ≤ 120.
- Validator green.
- Manual sanity-check: read the trimmed file end-to-end; nothing
  Claude-specific should be lost.

### Phase 7 — Reviews README + naming standardization

**Scope**

- Create `Reviews/README.md` (parallel to `Tracking/README.md` and
  `Projects/README.md`):
  - Purpose of the review system.
  - Index of `protocols/` (one line per protocol).
  - Index of `Prompts/` after rename (see below).
  - SLA: reviews must complete or be marked Abandoned within 30 days.
  - Cross-link: `reviews_index.md` is the live state; `results/<date>_<type>_<scope>/`
    is the artifact directory.
- Rename `Reviews/Prompts/` → `Reviews/prompts/` (lowercase, matching
  `Tracking/prompts/` even though that is being deleted in Phase 1 — the
  convention persists).
- If Phase 1 deleted `Tracking/prompts/`, this phase replaces the
  capitalization concern with a one-time alignment.
- Update any references to `Reviews/Prompts/` in scripts and docs.

**Touched files**

- `Reviews/README.md` (new)
- `Reviews/Prompts/*.txt` (rename to `Reviews/prompts/`)
- `Reviews/scripts/*.py` (update path references)
- `reviews_index.md` (if it references `Prompts/` directly)

**Verification**

- Validator green.
- `python Reviews/scripts/create_review.py --help` (or whichever script
  is the entry point) runs without error.
- Quick: `grep -r "Reviews/Prompts" .` returns nothing outside
  `_archive/`.

### Phase 8 — Antigravity skill pruning (or generator)

**Scope (default per Phase 0.2 = prune)**

- Identify the ~6 skills Antigravity actually uses. Confirm with user.
  Likely candidates based on user's prior statement that Antigravity is
  for "tooling and asset generation":
  - `anti-validate-designs`
  - `anti-fix-crash`
  - One or two analysis skills
  - Asset/tooling skills if any exist
- Delete the other ~27 `anti-*` skill directories.
- Run `python Tools/agent_coordination/inventory_agent_surfaces.py` and
  commit the regenerated inventory in the same change.
- Update `AGENTS.md` "Skill Usage Logging" examples if any reference a
  pruned skill.

**Alternative (if Phase 0.2 = generator)**

- Create `Tools/agent_coordination/generate_anti_skills.py` that:
  - Reads `.claude/skills/claude-*/SKILL.md`.
  - Strips Claude-specific frontmatter (`disable-model-invocation`,
    `argument-hint`, `paths`, `hooks`, `model`, `effort`, `context`,
    `agent`).
  - Writes `.agent/skills/anti-<name>/SKILL.md`.
- Run the generator; verify the 33 `anti-*` files become regenerable.
- Add a CI check: regenerate, fail if committed `.agent/skills/` differs
  from generator output.

**Verification**

- Validator green.
- Inventory regenerates cleanly.
- Skill counts in `agent_surface_inventory.json` match expectation.

### Phase 9 — Tools/ inventory and README cleanup

**Scope**

- Update `Tools/README.md` so its inventory matches the directory listing.
  Specifically add: `audit_shrink`, `check_context`,
  `component_transparency_viewer`, `process_components`. Remove
  references to anything deleted in Phase 1.
- Add `Tools/process_components/README.md` (~50 lines covering the three
  processing scripts and their inputs/outputs).
- Mark `Tools/check_orphans/` as legacy in its README:
  *"Superseded by `Tools/analyze_dependency_graph/`. Kept as a faster
  regex-only check for ad-hoc use."* — or delete if user confirms.

**Touched files**

- `Tools/README.md`
- `Tools/process_components/README.md` (new)
- `Tools/check_orphans/README.md`

**Verification**

- Validator green.
- `Tools/README.md` lists every directory in `Tools/` (cross-check via
  `diff <(ls -d Tools/*/) <(grep -oE 'Tools/[a-z_]+' Tools/README.md | sort -u)`).

### Phase 10 — Validator extensions

**Scope**

Add three new checks to `Tools/agent_coordination/validate_agent_surfaces.py`,
each with TDD tests under `tests/unit/tools/test_validate_agent_surfaces.py`:

1. **`reviews_sla`** — read `Reviews/reviews_index.md`; fail any entry
   marked `In Progress` whose date is older than 30 days. Recommend
   action: close as `Abandoned` or update status. Severity: warn (not
   fail) initially; flip to fail after one cleanup cycle.

2. **`tools_inventory`** — diff `Tools/README.md`'s tool list against
   `ls -d Tools/*/`. Fail if any directory exists but is not listed (or
   vice versa). Severity: fail.

3. **`skill_content_equivalence`** (only if Phase 0.2 = generator). For
   every `claude-X` and `anti-X` pair, regenerate the `anti-X` from
   `claude-X` and diff. Fail on any mismatch. Severity: fail.

**Touched files**

- `Tools/agent_coordination/validate_agent_surfaces.py`
- `tests/unit/tools/test_validate_agent_surfaces.py`
- `AgentCoordination/README.md` (document new checks)

**Verification**

- New tests green; existing tests still green.
- Live validator now exits 0 with the new checks active.

### Phase 11 — Final verification

**Scope**

- `python -m pytest tests/unit/tools/ -q` — all green.
- `python Tools/agent_coordination/validate_agent_surfaces.py` — 0 fail,
  0 warn (or warnings only on the SLA check if intentional).
- `python Tools/agent_coordination/inventory_agent_surfaces.py` — output
  matches committed file.
- `python Tools/test_sharded/test_sharded.py --refresh-baseline-timestamp`
  — full suite green; baseline updated if counts changed (the new
  validator checks add tests).
- `git log --oneline cleanup/support-systems` — every phase has at least
  one clearly-labeled commit.

## 6. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Deleting a "legacy" prompt that an external workflow still calls | Low | Medium | Phase 1 commits the deletions in one PR so they can be reverted as a unit. The user's QA workflow is the only known consumer; verify with user before Phase 1 ships. |
| Loop archival breaks an existing automation | Low | High | Phase 0.1 is a user decision. If user keeps a loop, Phase 4 implements locking; otherwise the loops are already not running per the audit. |
| Antigravity skill pruning removes a skill the user actually invokes | Medium | Low | Phase 0.2 explicitly asks the user which ~6 to keep. Deleted skills are recoverable from git history at commit `c1b774b29`. |
| Reviews `In Progress` → `Abandoned` mislabels a review the user genuinely intends to finish | Low | Low | Phase 2 only touches reviews older than 60 days. The user's recent reviews (post-2026-03-01) are untouched. Status is recoverable from git. |
| CLAUDE.md trim removes guidance the user relies on | Medium | Low | Phase 6 is the riskiest doc change. Recommend a manual user pass on the trimmed file before commit. |
| Validator's new SLA check fails the build immediately on landing | High by default | Low | Phase 10 ships SLA as warn-only initially. Flip to fail after one cleanup cycle. |
| `Tools/captioning/` move loses workflow steps | Low | Low | Move preserves all `.md` content; only the directory location changes. |

## 7. Estimated effort

Rough estimate per phase, assuming an agent with this plan and access to
the repo. Numbers are calendar-time including verification gates, not
person-hours.

| Phase | Estimate |
|---|---|
| 0 — User decisions | 1–2 days (waiting on user) |
| 1 — Quiet deletions | 1 hour |
| 2 — Stale review cleanup | 30 min |
| 3 — Sweep decision | 30 min (delete) or 2 hours (formalize) |
| 4 — Loop archival | 1 hour (archive) or 1 day (revive one) |
| 5 — AgentCoordination archive | 30 min |
| 6 — CLAUDE.md trim | 1 hour + manual user review |
| 7 — Reviews README + rename | 1 hour |
| 8 — Antigravity prune | 1 hour (prune) or 1 day (generator) |
| 9 — Tools/ inventory | 1 hour |
| 10 — Validator extensions | 3 hours (TDD) |
| 11 — Final verification | 30 min |
| **Total (default path)** | **~10 hours** + Phase 0 wait |

## 8. Acceptance criteria (plan-done)

The plan is complete when **all** of the following are true:

- [ ] `git diff main..cleanup/support-systems --stat` shows only changes
      in: `AgentCoordination/`, `Projects/` (additions to `_archive/` and
      removal of loops), `Tracking/` (removal of legacy prompts),
      `Reviews/`, `Tools/`, the three adapter files, `docs/guides/`, and
      `tests/unit/tools/`. **Zero changes to `game/`.**
- [ ] `wc -l CLAUDE.md` ≤ 120.
- [ ] `ls AgentCoordination/*.md | wc -l` ≤ 6.
- [ ] `ls Projects/refactor_loop/ Projects/complexity_loop/ Projects/continuous_loop/`
      returns "no such directory" (unless one was revived per Phase 0.1).
- [ ] No `In Progress` review in `Reviews/reviews_index.md` is older than
      60 days.
- [ ] `Tools/README.md` lists every subdirectory in `Tools/`.
- [ ] No loose `.py` file at the root of `Tools/`.
- [ ] `python Tools/agent_coordination/validate_agent_surfaces.py` exits
      0 with the new checks active.
- [ ] `python -m pytest tests/unit/tools/ -q` passes.
- [ ] Full sharded suite passes; `test_baseline.json` updated.
- [ ] User has reviewed and approved the cleanup branch.

## 9. Handoff context

**For an agent picking this up cold:**

- Read `AgentCoordination/codex_agent_coordination_plan_final.md` for the
  baseline coordination policy.
- Read `AgentCoordination/support_systems_critical_review.md` (the
  evidence base for this plan).
- Read this file end-to-end before starting any phase.
- The user is **solo** on this project. No team approvals. No multi-agent
  reviews are required for low-risk phases (1, 2, 5, 7, 9, 11). Phases 3,
  4, 6, 8, 10 may benefit from a Codex or OpenCode review of the diff
  before commit.
- The branch protocol: feature branch off main, atomic per-phase commits,
  PR opened only after Phase 11 passes.
- The user uses **Antigravity (a VS Code fork)** for git operations via
  the GUI. The push will trigger
  `.github/workflows/agent_coordination.yml`, which now hard-fails on
  validator regressions. CI must be green before merge.
- The user's stated priorities (recorded in `user_response.md`):
  - Antigravity is lower priority and used mainly for tooling/assets.
  - Claude, Codex, and DeepSeek/OpenCode are the workhorse agents.
  - Some duplication of stable rules across adapter docs is *intentional*
    (the closed reinforcement-marker list).
  - Counters are advisory; never auto-delete a skill based on count.

**Things that look weird but aren't bugs:**

- `AgentCoordination/generated/test_baseline.json`'s `git_sha` field
  always lags by one commit. This is intentional — see
  `Tools/test_sharded/README.md` § "Test baseline schema."
- `.claude/skills/claude-*/SKILL.md` and `.agent/skills/anti-*/SKILL.md`
  files are intentionally divergent (Claude-specific frontmatter is
  stripped from the `anti-*` versions). Phase 8 either formalizes this
  with a generator or eliminates the divergence by pruning.
- `Projects/active_projects/PROJ-300` through `PROJ-318` are *not* part
  of this cleanup. They are the user's current real work.

**Things to ask the user before deviating:**

- Any change to `game/` or `tests/` outside `tests/unit/tools/`.
- Any change to `Projects/active_projects/` content.
- Any change to the agent-coordination tooling beyond the validator
  extensions in Phase 10.
- Any phase that changes more than ~50 files in one commit.

## 10. What this plan does not solve

- The 70+ untested process scripts across `Projects/scripts/`,
  `Tracking/scripts/`, `Reviews/scripts/`. Phase 10 adds validator checks
  but does not unit-test those scripts. A follow-up plan should.
- The two skill philosophies (Codex routers vs Claude/Anti fine-grained).
  This plan keeps them as-is. A future round can decide whether to
  consolidate.
- `docs/` size (5,722 lines across 6 numbered files + guides + systems).
  The audit found `docs/` substantively current; size is intentional.
- The CI workflow's coverage of more script directories. Currently CI
  runs `tests/unit/tools/`; expanding coverage is out of scope here.

These are recorded so the next plan does not re-discover them.

---

End of plan. Awaiting user sign-off on Phase 0 decisions.
