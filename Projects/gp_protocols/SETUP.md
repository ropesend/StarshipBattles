# GP System Setup (one-time per machine)

This document lists the one-time setup steps required to use the new
`claude-gp-*` skill family. Run these once per machine before invoking
`/claude-gp-add` or any other GP skill.

The label list, asset directory, protocols, and skills are already
committed. The remaining steps require **you** because they involve
GitHub-remote mutations or per-machine `gh` auth scope.

---

## 1. Verify `gh` is authenticated with the `project` scope

```bash
gh auth status
```

Look for `'project'` in the listed token scopes. If missing:

```bash
gh auth refresh -s project
```

This is required for creating Projects v2 board items and editing custom
fields. Without it, `claude-gp-add` will warn and skip the board-write step
(the issue still gets created with correct labels; board membership can be
added later).

---

## 2. Sync labels to GitHub

The new project labels are declared in [.github/labels.yml](../../.github/labels.yml).
Apply them with:

```bash
python Tools/agent_coordination/sync_github_labels.py
```

Expected output: `Plan: create N, update 0, delete 0 (prune=False)` where
`N` is the number of new GP labels (~53 on first run).

Dry-run first if you want to preview:

```bash
python Tools/agent_coordination/sync_github_labels.py --dry-run
```

---

## 3. Create the GitHub Project (v2) board

Once per repo:

```bash
gh project create --owner @me --title "Starship Battles — Refactor Projects"
```

Capture the project number printed (e.g., `1`, `2`). Save it; the skills
need it for the `gh project item-add` calls. The simplest place to store
it is in your local `.claude/settings.local.json` as an env var, or in a
short note pinned to the project board itself.

### 3a. Add custom fields

The plan calls for these fields on the board (in addition to GitHub's
defaults: Title, Status, Assignees, Labels, Linked pull requests, Reviewers,
Repository, Milestone, Sub-issues progress):

| Field | Type | Options |
|---|---|---|
| Priority | single select | Critical, High, Medium, Low |
| Phase | single select | 1, 2, 3, 4, 5, 6, 7, 8, 9, audit, closed |
| Type | single select | Refactor, Performance, Feature, Quality |
| Source | single select | manual, triage, audit-shrink, audit-docs, audit-error, audit-legacy, audit-pattern, audit-state, audit-test-review, audit-testcoverage, audit-type, extract, revise |
| Consult | single select | pending, passed, overridden, failed |
| Execution | single select | sequential, phase-aware, parallel-eligible |

(The default Status field is reused with options: Planning, In Progress,
Awaiting Audit, Awaiting Confirmation, Closed.)

You can add fields through the GitHub Projects web UI (faster for the
first-time setup) or via CLI:

```bash
gh project field-create <project-number> --owner @me \
  --name "Priority" --data-type SINGLE_SELECT \
  --single-select-options "Critical,High,Medium,Low"
```

Repeat per field. The skills reference fields by ID, which you discover
with:

```bash
gh project field-list <project-number> --owner @me
```

Capture the field IDs for use in skill invocations.

### 3b. Create board views

In the GitHub Projects web UI (easiest path), create five views:

1. **Active board** — group by Status, filter `label:type:project status:!Closed`
2. **By phase** — group by Phase (table layout)
3. **By priority** — sort by Priority then created-date (table layout)
4. **By consult state** — group by Consult; surfaces `consult:overridden` and
   `consult:failed` for process-erosion monitoring
5. **Closed** — filter `label:type:project status:Closed`, last 30 days

---

## 4. Sanity check

After setup, run:

```bash
gh label list --search "type:project"
gh label list --search "phase:"
gh label list --search "consult:"
gh project list --owner @me
```

You should see the 53 new labels and your newly-created board.

---

## 5. (Optional) Add the project number to your local config

To avoid passing the project number on every skill invocation, you can set
it in a machine-local config. Suggested location:
`.claude/settings.local.json` (already gitignored per
[Projects/README.md](../README.md) setup guidance):

```json
{
  "env": {
    "GP_PROJECT_NUMBER": "1"
  }
}
```

The skills will read `$GP_PROJECT_NUMBER` if present; otherwise they prompt.

---

## What happens on a second machine

The shared setup (labels, board, fields) is already on GitHub from machine
one. On machine two you only need:

1. `gh auth refresh -s project` — per-machine
2. Optionally set `GP_PROJECT_NUMBER` in machine-local config

No need to re-sync labels or re-create the board.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `gh issue create` succeeds but skill reports board-add failure | `project` scope missing | `gh auth refresh -s project` |
| `sync_github_labels.py` reports "permission denied" | repo scope or admin perms missing | `gh auth refresh -s repo` and verify you have write access |
| `gh project field-create` fails with "field already exists" | re-running setup; idempotent skip | safe to ignore; the field exists |
| Skill complains about missing project number | `GP_PROJECT_NUMBER` not set and no `--project` flag | pass `--project <n>` or set the env var |
| Asset commit lands but `asset-state:committed` label not set | network race during the atomic flip | re-run `gh issue edit <gp> --remove-label asset-state:pending --add-label asset-state:committed` manually |
