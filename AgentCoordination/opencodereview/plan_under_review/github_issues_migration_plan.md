# GitHub Issues Migration — Tracking System

## Context

The project currently uses a markdown-on-disk ticket system at [Tracking/](Tracking/) with 165 tickets (132 archived bugs, 22 archived features, 5 active bugs, 6 active features), 11 protocols in [Tracking/protocols/](Tracking/protocols/), and 16 `/claude-ticket-*` slash commands. The system is mature and protocol-driven, but the user wants to move to GitHub Issues so tracking is visible on the project's GitHub page (`https://github.com/ropesend/StarshipBattles`), discoverable to outside contributors, and cross-linkable to commits/PRs.

The new system must be **agent-first**: agents (primarily Claude Code) interact with it for the bulk of operations — creating, working, updating, querying, closing. Screenshots and logs must be fully agent-manageable (no drag-drop reliance).

The migration is **parallel**, not destructive: the existing system at `Tracking/` keeps running. The new system is built alongside under new skills (`/claude-gi-*`). Once the user is satisfied, the old system is sunset and frozen as a historical archive.

**Out of scope: the Projects system.** [Projects/](Projects/) (15 active + 21 archived multi-phase architectural programs) was reviewed and deliberately excluded. Reasoning summarised below; the system stays 100% on disk with all existing protocols, skills (`claude-proj-*`), and Python tooling untouched. Cross-referencing between the two systems is handled by simple citation conventions, not by tooling — see "Cross-References" below.

---

## Design — Locked Decisions

| Decision | Choice |
|---|---|
| Migration scope | **New tickets only.** The 154 archived markdown files stay in `Tracking/` as a frozen historical archive. |
| ID strategy | **Raw GitHub issue numbers** (#127, #128, …). Drop BUG-/FEAT- prefixes. One global namespace. |
| Type distinction | **Labels:** `type:bug`, `type:feature`. |
| Status model | **Labels only**, `status:*` prefix. Issue open = work-in-flight; issue closed = resolved/archived. |
| Close authority | **Convention + label gate.** Agents may only set `status:awaiting-confirmation`; user closes. Optional safety-net GitHub Action auto-reopens unauthorized closes. |
| Screenshots | **Plain repo folder** `tracking-assets/screenshots/YYYY-MM/issue-NNN-slug.png`. No LFS. |
| Logs | **Plain repo folder** `tracking-assets/logs/issue-NNN/<filename>`. Linked from a comment. |
| Issue body | **Stable spec only:** Description, Reproduction (bugs), Acceptance Criteria, Priority. Everything else (work log, root cause, investigation, design review) becomes **comments** — chronological audit trail. |
| Skills | New parallel set under `/claude-gi-*` prefix. Old `/claude-ticket-*` remains untouched. |
| gh CLI | Plan includes install + first-time auth (`winget install GitHub.cli`, `gh auth login`). |

---

## Projects System — Out of Scope (Decision Recorded)

The `Projects/` system was reviewed alongside `Tracking/` and **explicitly excluded from this migration**. Recap:

- Projects are multi-phase architectural programs (~11 files per project: `plan.md`, `design.md`, `decisions.md`, `manifest.md`, `phase_N_checklist.md`), not single-shot tickets.
- They depend on local-first features that GitHub doesn't model cleanly: manifest-based file-conflict detection for parallel projects, handoff-prompt files for multi-session continuity, 80% context-threshold awareness, multi-cycle skeptical audit gates, and explicit role rotation (Architect → Developer → Auditor → Archivist).
- 13 protocols, 10+ Python scripts (`Projects/scripts/`), and 10 `claude-proj-*` skills are recent, working tooling. Migrating would mean rewriting a substantial Action layer to recover what already works.
- Tickets benefit from GitHub because they're public-facing. Projects are internal architectural plans — no equivalent discoverability win.
- A Milestones-based bridge was considered and declined for now to keep this migration small.

**Cross-references between systems:**
- Issues reference projects in their body: `Related: PROJ-313`.
- Projects reference issues in `decisions.md` / `manifest.md`: `Resolves #127`, `Discovered via #128`. GitHub auto-renders these in any commit message that cites them.
- No tooling enforces this — it's a convention, same as today.

If the case for migrating Projects strengthens later (e.g. you want public visibility of the roadmap, or unified search becomes painful), revisit in a separate plan.

---

## Repository Layout (additions)

```
tracking-assets/                         (NEW — committed to repo)
├── screenshots/
│   └── YYYY-MM/
│       └── issue-NNN-<slug>.png
└── logs/
    └── issue-NNN/
        └── <log-filename>

.github/
├── ISSUE_TEMPLATE/                      (NEW)
│   ├── bug.yml                          # GitHub form template — bug
│   ├── feature.yml                      # GitHub form template — feature
│   └── config.yml                       # disable blank issues
├── labels.yml                           (NEW — declarative label set)
└── workflows/
    └── tracking-guard.yml               (NEW, optional — close-authority safety net)

.claude/skills/
├── claude-gi-add/                       (NEW skills, ~10 directories)
├── claude-gi-work/
├── claude-gi-next/
├── claude-gi-deep-dive/
├── claude-gi-close/
├── claude-gi-batch-close/
├── claude-gi-update/
├── claude-gi-answer/
├── claude-gi-reject/
└── claude-gi-continue/

Tracking/                                (UNCHANGED — kept as legacy + archive)
```

---

## Label Schema

Declared in `.github/labels.yml`. Apply via [`EndBug/label-sync`](https://github.com/marketplace/actions/label-sync) on push, or one-shot via `gh label create`.

| Label | Color | Notes |
|---|---|---|
| `type:bug` | red | exactly one of type:* required |
| `type:feature` | green | |
| `priority:critical` | dark-red | exactly one of priority:* required |
| `priority:high` | orange | |
| `priority:medium` | yellow | |
| `priority:low` | grey | |
| `status:pending` | light-blue | default after creation |
| `status:in-progress` | blue | agent set when work begins |
| `status:awaiting-confirmation` | purple | agent set when ready for user smoke (replaces old `[Awaiting Confirmation]`) |
| `status:needs-clarification` | yellow | agent set when blocked on user answer |
| `status:deep-investigation` | dark-purple | bug-only |
| `status:needs-human-debug` | dark-red | bug-only |
| `status:blocked` | black | bug-only |
| `status:needs-refactor` | brown | feature-only |
| `status:needs-project` | brown | feature-only — promote to a PROJ-XX |
| `status:analysis` | light-purple | feature-only |
| `verified` | bright-green | added by user before closing — used by safety-net Action |

**Invariant:** exactly one `type:*`, one `priority:*`, one `status:*` per open issue. The new skills enforce this; a future Action can audit it.

---

## Issue Templates

`.github/ISSUE_TEMPLATE/bug.yml`:
- Title prefix: none (raw description)
- Fields: Description (textarea, required), Steps to Reproduce (textarea), Expected vs Actual (textarea), Acceptance Criteria (textarea), Screenshot (textarea — markdown link to `tracking-assets/screenshots/...`), Priority (dropdown: critical/high/medium/low)
- Default labels: `type:bug`, `status:pending`

`.github/ISSUE_TEMPLATE/feature.yml`:
- Fields: Description, Motivation, Acceptance Criteria, Priority
- Default labels: `type:feature`, `status:pending`

`config.yml` disables blank issues so every ticket goes through a template.

---

## Skill Designs (new `/claude-gi-*` set)

Each skill is a directory under `.claude/skills/claude-gi-<name>/` with a `SKILL.md` describing role, procedure, and the exact `gh` invocations. Mirrors the current `Tracking/protocols/` pattern. Reuse the structure and tone of [.claude/skills/](.) `claude-ticket-*` skills (locations findable by globbing the project's existing skill directories).

| Skill | Maps to old | What it does |
|---|---|---|
| `/claude-gi-add bug "<desc>"` | `01_ingest_ticket.md` | Calls `gh issue create --template bug.yml`, parses description, sets `priority:*`, posts initial scaffold. Records issue # in response. |
| `/claude-gi-add feature "<desc>"` | same | Same but with `feature.yml`. |
| `/claude-gi-work <#>` | `02_work_ticket.md` | Reads issue + comments via `gh issue view --comments`, runs the existing TDD/docs/root-cause workflow, adds work-log comments, sets `status:in-progress` then `status:awaiting-confirmation`. **Never closes.** |
| `/claude-gi-next bug\|feature` | (new convenience) | `gh issue list --label type:bug --label status:pending --json number,title,labels` → pick highest priority → invoke gi-work. |
| `/claude-gi-continue bug\|feature` | `02a_batch_work.md` | Autonomous batch loop until context limit. |
| `/claude-gi-deep-dive <#>` | `02b_deep_dive.md` | Investigation-only mode; posts findings as comments; sets `status:deep-investigation` or `status:needs-clarification`. |
| `/claude-gi-update <#> "<text>"` | `04_update_ticket.md` | `gh issue comment <#> --body` with a `### User Update [TIMESTAMP]` block. |
| `/claude-gi-answer <#> "<answers>"` | `06_answer_questions.md` | Post answers as comment, flip `status:needs-clarification` → `status:pending`. |
| `/claude-gi-reject <#> "<reason>"` | `05_reject_ticket.md` | Post rejection comment, flip `status:awaiting-confirmation` → `status:in-progress`. |
| `/claude-gi-close <#>` | `03_close_ticket.md` | **User-only.** Adds `verified` label, closes issue, optional `gh issue close --reason completed`. |
| `/claude-gi-batch-close <# # #>` | `03a_batch_close.md` | Same for multiple issues. |

**Authority rule (encoded in every work/deep-dive/update skill):** `Agents MUST NOT call 'gh issue close'. Agents MUST NOT add the 'verified' label. Final closure is the user's prerogative.`

---

## Screenshot & Log Workflow (agent-managed)

Screenshots:
1. Agent saves PNG to `tracking-assets/screenshots/YYYY-MM/issue-NNN-<slug>.png` (slug derived from issue title).
2. `git add` + commit message `"chore(tracking): add screenshot for #NNN"`.
3. `git push` (or batch with the work-log commit).
4. Reference in issue body or comment as: `![alt](https://github.com/ropesend/StarshipBattles/blob/main/tracking-assets/screenshots/YYYY-MM/issue-NNN-<slug>.png?raw=1)` — the `?raw=1` query renders the image inline.

Logs: same pattern under `tracking-assets/logs/issue-NNN/`, linked from a comment (not embedded — keeps the issue body lean).

QA-observer integration: when the existing QA observer at [Tools/qa_observer/](Tools/qa_observer/) creates a bug, its capture pipeline copies the relevant screenshot from `Tools/qa_observer/session_data/<id>/images/` into `tracking-assets/screenshots/...` before invoking `/claude-gi-add bug`. (The QA observer's existing skill `anti-qa-triage` will need a small update, **scoped as out-of-plan follow-up** unless you want it bundled — see Open Questions.)

---

## Optional Safety-Net Action

`.github/workflows/tracking-guard.yml` (recommended but optional — implement after the main rollout if you want it):

```yaml
on:
  issues:
    types: [closed]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - if: github.event.sender.login != 'ropesend' && !contains(github.event.issue.labels.*.name, 'verified')
        run: gh issue reopen ${{ github.event.issue.number }} --repo ${{ github.repository }} --comment "Reopened: only the repo owner may close issues, and only after applying the 'verified' label."
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

If you don't want the action, the convention rule in every skill prompt is sufficient.

---

## Critical Files to Create

- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/ISSUE_TEMPLATE/feature.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/labels.yml`
- `.github/workflows/tracking-guard.yml` *(optional)*
- `tracking-assets/screenshots/.gitkeep`
- `tracking-assets/logs/.gitkeep`
- `tracking-assets/README.md` — explains conventions
- `.claude/skills/claude-gi-<name>/SKILL.md` × ~10 skills
- Update [CLAUDE.md](CLAUDE.md) and [AGENTS.md](AGENTS.md) — add a "GitHub Issues (parallel system)" section pointing at the new skills and noting the legacy system is still authoritative until cutover.

## Files NOT Touched

- `Tracking/` — entire directory remains as-is (legacy system still runs).
- The 16 existing `/claude-ticket-*` skills — untouched.
- Existing protocols in `Tracking/protocols/` — untouched.

---

## Reuse from Existing Codebase

- The TDD / docs-discrepancy-check / root-cause-only workflow already encoded in [Tracking/protocols/02_work_ticket.md](Tracking/protocols/02_work_ticket.md) is the spine of `/claude-gi-work`. Lift the prose verbatim, swap file-write steps for `gh issue comment` calls.
- Priority guidelines in [Tracking/protocols/01_ingest_ticket.md](Tracking/protocols/01_ingest_ticket.md) lines 32-44 transfer unchanged into the issue templates.
- Authority limits in [Tracking/README.md](Tracking/README.md) lines 94-99 transfer unchanged into every skill prompt.
- The skill-usage logger at [Tools/agent_coordination/log_skill_usage.py](Tools/agent_coordination/log_skill_usage.py) already auto-logs `claude-*` skills via the [.claude/settings.json](.claude/settings.json) hook — `claude-gi-*` will be picked up with no additional wiring.

---

## Verification Plan

End-to-end, in order:

1. **gh CLI works.** `gh --version`; `gh auth status` shows authenticated as ropesend with `repo` scope.
2. **Labels exist.** `gh label list` shows all entries from `.github/labels.yml`.
3. **Issue templates render.** Visit `https://github.com/ropesend/StarshipBattles/issues/new/choose` — both bug and feature templates appear.
4. **Create via skill.** `/claude-gi-add bug "test ticket — please ignore"` creates an issue; `gh issue view <#>` shows correct labels (`type:bug`, `priority:*`, `status:pending`) and the templated body.
5. **Screenshot round-trip.** Create a bug with a screenshot reference: confirm the image renders inline on github.com and the file is committed under `tracking-assets/screenshots/`.
6. **Work skill.** `/claude-gi-work <#>` reads context, posts work-log comments, flips `status:in-progress` → `status:awaiting-confirmation`. Verify it never calls `gh issue close`.
7. **Authority gate.** Manually attempt `gh issue close <#>` from your account — should succeed (you're the owner). If the safety-net Action is enabled, attempt close from a different account/token — should auto-reopen.
8. **Close skill.** `/claude-gi-close <#>` adds `verified` and closes. `gh issue list --state closed` shows the issue.
9. **Cleanup.** Delete the test issue or close as `not planned`; remove the test screenshot commit if you don't want it in history.
10. **Coexistence smoke.** Run an old-system flow (`/claude-ticket-add bug "..."`) — confirm zero interaction with the new system.

Once 1–10 pass, run the new system on **one real bug** end-to-end before broader cutover. Sunset of the old system happens later, on your call, in a separate plan.

---

## Open Questions / Out-of-Plan Follow-Ups

These are deliberately *not* in this plan but flagged for later if you want them:

- **QA-observer integration.** [Tools/qa_observer/](Tools/qa_observer/) currently writes screenshots into `Tools/qa_observer/session_data/.../images/` and invokes `/claude-ticket-add`. To use the new system, the `anti-qa-triage` skill (and any auto-capture path) needs a one-line redirect to copy → `tracking-assets/screenshots/` and invoke `/claude-gi-add`. Cheap to do but requires a small audit. Suggest a follow-up ticket once the new system is proven.
- **`debug_plan.md` / `feature_plan.md` dashboards.** GitHub's native filtered views (`gh issue list --label status:in-progress`) plus a saved search URL replace these. If you want a markdown mirror auto-generated for git-grep convenience, that's a small follow-up Action.
- **PROJ-XX cross-references.** Existing PROJ-XX docs reference legacy BUG-/FEAT- IDs and stay frozen. Future PROJ-XX docs cite GitHub `#NNN` directly in `decisions.md` / `manifest.md` (auto-linked by GitHub). Projects system is not migrating — see "Projects System — Out of Scope" above.
- **Revisit Projects → GitHub later (optional).** If single-source-of-truth pain grows, the lightest possible bridge is one GitHub Milestone per active project, with tickets opt-in tagged. Out of scope here, recorded as a future option.
- **Bulk historical migration.** If you ever change your mind on importing the 154 archived tickets, a one-shot script using `gh issue create --label status:archived` + close is straightforward. Not in scope here.
