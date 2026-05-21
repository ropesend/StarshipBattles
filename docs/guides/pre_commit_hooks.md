# Pre-commit Hook Card

> **Last verified:** 2026-05-20 - Checked against the local Git pre-commit hook contract and `.github/workflows/agent_coordination.yml` (PROJ-468; the only G3 guide previously lacking a freshness stamp).

This hook is a raw local Git hook in the checkout's Git hooks directory
(usually `.git/hooks/`); this guide does not require the `pre-commit`
framework. The CI copy of the same check is tracked in
`.github/workflows/agent_coordination.yml`.

## Hook Contract

`lint_test_files` runs:

```bash
python Tools/lint_test_files.py
```

Current behavior:

- Scans Python files under `tests/` by default.
- Skips `conftest.py`, `__init__.py`, and `__pycache__/`.
- Flags scanned test files with zero detected `game` imports unless allowlisted.
- Treats AST parse failures as hard failures.
- Exits `0` on no violations; exits `1` on violations or parse errors.
- Uses AST inspection, not regex matching.

Imports that satisfy the check:

- `import game` or `import game.foo`
- `from game import foo` or `from game.foo import bar`
- Constant dynamic imports such as `importlib.import_module("game.foo")`
  or `import_module("game.foo")`

Runtime-built dynamic import names, comments, docstrings, and strings do not
count. If a test genuinely needs a deferred import, include one constant
`game` import somewhere or add a narrow allowlist entry with rationale.

## Allowlist

Legitimate exceptions live in `Tools/lint_test_files_allowlist.txt`.

Format:

- One repo-relative path or glob per line.
- Blank lines and lines starting with `#` are ignored.
- Inline comments after a path are not supported.
- Globs use the linter's internal POSIX-style translator, including recursive
  `**`; do not infer behavior from `pathlib.PurePosixPath.match`.

Only allowlist tests that legitimately do not import `game.*`, such as tooling
tests, test infrastructure, data fixtures, or tests whose nearest `conftest.py`
provides the real `game.*` dependency. Do not allowlist tests that reimplement
production logic locally; delete or rewrite them.

## Install

From the repo root:

```bash
hook_path="$(git rev-parse --git-path hooks/pre-commit)"
mkdir -p "$(dirname "$hook_path")"
cat > "$hook_path" <<'EOF'
#!/bin/sh
# Skip transient Git states where partial trees are normal.
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    exit 0
fi
if [ -f "$(git rev-parse --git-path MERGE_HEAD)" ] \
   || [ -f "$(git rev-parse --git-path CHERRY_PICK_HEAD)" ] \
   || [ -d "$(git rev-parse --git-path rebase-merge)" ] \
   || [ -d "$(git rev-parse --git-path rebase-apply)" ]; then
    exit 0
fi
python Tools/lint_test_files.py
EOF
chmod +x "$hook_path"
```

```powershell
$hookPath = git rev-parse --git-path hooks/pre-commit
New-Item -ItemType Directory -Force -Path (Split-Path $hookPath) | Out-Null
@'
#!/bin/sh
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    exit 0
fi
if [ -f "$(git rev-parse --git-path MERGE_HEAD)" ] \
   || [ -f "$(git rev-parse --git-path CHERRY_PICK_HEAD)" ] \
   || [ -d "$(git rev-parse --git-path rebase-merge)" ] \
   || [ -d "$(git rev-parse --git-path rebase-apply)" ]; then
    exit 0
fi
python Tools/lint_test_files.py
'@ | Set-Content -Path $hookPath -Encoding ASCII
```

The `git rev-parse --git-path ...` form works for both hook installation and
state checks in normal checkouts and linked worktrees. The old `.git/hooks/...`
and `.git/MERGE_HEAD` style is stale for worktree-heavy agent flows because
`.git` may be a pointer file.

## Run / Skip

```bash
python Tools/lint_test_files.py
python Tools/lint_test_files.py --root tests/
python Tools/lint_test_files.py --allowlist Tools/lint_test_files_allowlist.txt
python Tools/lint_test_files.py --strict
```

`--strict` bypasses the allowlist and is useful for audits. For one intentional
local commit bypass, use:

```bash
git commit --no-verify
```

Prefer fixing the file or allowlist entry; hooks are local and bypassable.

## CI

`.github/workflows/agent_coordination.yml` already runs:

```yaml
- name: Lint test files (zero-game-import detector)
  run: python Tools/lint_test_files.py
```

If the linter or allowlist path changes, update that workflow, this guide, and
`tests/unit/tools/test_lint_test_files.py` in the same change.

## Extension Recipes

Adding a legitimate allowlist entry:

1. Put rationale on a `#` comment line above the path.
2. Add the narrowest repo-relative path or glob.
3. Run `python Tools/lint_test_files.py`.

Changing the linter contract:

1. Update `Tools/lint_test_files.py`.
2. Add or adjust focused coverage in `tests/unit/tools/test_lint_test_files.py`.
3. Run the focused test file and `python Tools/lint_test_files.py`.
4. Keep CI paths in `.github/workflows/agent_coordination.yml` in sync.

Adding another raw hook command:

1. Keep it deterministic, fast, offline, and read-only unless the command's job
   is explicitly formatting.
2. Skip merge, rebase, and cherry-pick states when partial trees are expected.
3. Add a CI step if the invariant must hold for shared branches.
