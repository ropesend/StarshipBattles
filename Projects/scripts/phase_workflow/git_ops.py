"""Git operations: worktrees, branches, temp-integration merges.

All commands shell-out to `git` via subprocess with shell=False; pathlib for
paths; Windows-friendly. No external dependencies.

Conventions:
    - GitOpsError is raised on git errors (non-zero exit).
    - IntegrationTestFailure is raised by callers' test runner to signal red.
"""
from __future__ import annotations

import dataclasses
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable


class GitOpsError(RuntimeError):
    pass


class IntegrationTestFailure(RuntimeError):
    pass


def _run(args: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            args,
            cwd=str(cwd),
            check=check,
            capture_output=True,
            text=True,
            shell=False,
        )
    except subprocess.CalledProcessError as e:
        raise GitOpsError(
            f"git command failed: {' '.join(args)}\n  cwd={cwd}\n"
            f"  stdout: {e.stdout}\n  stderr: {e.stderr}"
        ) from e
    except FileNotFoundError as e:
        raise GitOpsError(f"git not found on PATH: {e}") from e


# ---------------------------------------------------------------------------
# SHA / branch primitives
# ---------------------------------------------------------------------------


def current_sha(repo: Path, ref: str) -> str:
    """Resolve a ref to its 40-char SHA. Raises GitOpsError if unknown."""
    res = _run(["git", "rev-parse", "--verify", ref], cwd=repo)
    return res.stdout.strip()


def branch_exists(repo: Path, branch: str) -> bool:
    res = _run(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=repo,
        check=False,
    )
    return res.returncode == 0


def create_branch(repo: Path, branch: str, *, base_ref: str) -> None:
    if branch_exists(repo, branch):
        raise GitOpsError(f"branch already exists: {branch}")
    _run(["git", "branch", branch, base_ref], cwd=repo)


def delete_branch(repo: Path, branch: str, *, force: bool = True) -> None:
    flag = "-D" if force else "-d"
    _run(["git", "branch", flag, branch], cwd=repo)


# ---------------------------------------------------------------------------
# Worktrees
# ---------------------------------------------------------------------------


def worktree_add(
    repo: Path,
    worktree_path: Path,
    *,
    ref: str,
    new_branch: str | None = None,
    detach: bool = False,
) -> None:
    """Add a git worktree at `worktree_path`.

    `new_branch`: if provided, creates this branch at `ref` and checks it out
    in the worktree. `detach`: if True, checks out `ref` detached.
    Otherwise checks out the existing `ref` (must be a branch).
    """
    args = ["git", "worktree", "add"]
    if detach:
        args.append("--detach")
        args.extend([str(worktree_path), ref])
    elif new_branch:
        args.extend(["-b", new_branch, str(worktree_path), ref])
    else:
        args.extend([str(worktree_path), ref])
    _run(args, cwd=repo)


def worktree_remove(repo: Path, worktree_path: Path, *, force: bool = False) -> None:
    """Remove a worktree. Refuses if dirty unless force=True."""
    if not Path(worktree_path).exists():
        # Already gone — call git worktree prune to clean up metadata.
        _run(["git", "worktree", "prune"], cwd=repo)
        return
    # Check for uncommitted changes.
    if not force:
        res = _run(
            ["git", "status", "--porcelain"],
            cwd=Path(worktree_path),
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            raise GitOpsError(
                f"worktree {worktree_path} has uncommitted changes; pass force=True to override"
            )
    args = ["git", "worktree", "remove"]
    if force:
        args.append("--force")
    args.append(str(worktree_path))
    _run(args, cwd=repo)


def worktree_list(repo: Path) -> list[dict[str, Any]]:
    """List worktrees; each entry has 'path', 'branch', 'sha', 'detached'."""
    res = _run(["git", "worktree", "list", "--porcelain"], cwd=repo)
    out: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for line in res.stdout.splitlines():
        if not line.strip():
            if current:
                out.append(current)
                current = {}
            continue
        if line.startswith("worktree "):
            current["path"] = line[len("worktree "):].strip()
        elif line.startswith("HEAD "):
            current["sha"] = line[len("HEAD "):].strip()
        elif line.startswith("branch "):
            current["branch"] = line[len("branch "):].strip()
        elif line == "detached":
            current["detached"] = True
    if current:
        out.append(current)
    for entry in out:
        entry.setdefault("detached", False)
        entry.setdefault("branch", None)
    return out


def detect_orphan_worktrees(
    repo: Path,
    *,
    search_root: Path,
    branch_prefix: str,
    live_worktrees: set[Path],
) -> list[Path]:
    """Return worktrees under search_root not present in live_worktrees set.

    Caller is responsible for defining "live" — typically reading review
    request payloads or phase_state.json to determine which worktrees are
    expected to exist.
    """
    listed = worktree_list(repo)
    candidates = []
    live_resolved = {Path(p).resolve() for p in live_worktrees}
    for entry in listed:
        path = Path(entry["path"]).resolve()
        try:
            path.relative_to(Path(search_root).resolve())
        except ValueError:
            continue
        branch = entry.get("branch") or ""
        if branch and not branch.startswith(f"refs/heads/{branch_prefix}"):
            continue
        if path in live_resolved:
            continue
        candidates.append(path)
    return candidates


# ---------------------------------------------------------------------------
# Temp-integration merge
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class IntegrationResult:
    green: bool
    merge_sha: str | None
    temp_branch: str
    merge_conflict: bool = False
    test_failure_message: str | None = None


def temp_integration_merge(
    repo: Path,
    *,
    project_branch: str,
    phase_branch: str,
    phase_id: str,
    integration_worktree_path: Path,
    run_tests: Callable[[Path], None],
) -> IntegrationResult:
    """Merge a phase branch into a temp branch off project tip; test there.

    Flow:
        1. Create temp branch `tmp/<project_branch_leaf>/integrate-<phase_id>-<shortsha>`
           from project tip.
        2. Add a worktree at `integration_worktree_path` on the temp branch.
        3. Merge `phase_branch` into temp.
        4. Run `run_tests(integration_worktree_path)`. Raises
           IntegrationTestFailure or returns None.
        5. Green: fast-forward `project_branch` to temp commit. Delete temp
           branch + worktree.
        6. Red (test failure or merge conflict): delete temp + worktree;
           leave phase branch and project branch unchanged.
    """
    project_leaf = project_branch.split("/", 1)[-1]
    project_tip = current_sha(repo, project_branch)
    short_sha = project_tip[:8]
    temp_branch = f"tmp/{project_leaf}/integrate-{phase_id}-{short_sha}"

    # Step 1+2: create temp branch + worktree.
    create_branch(repo, temp_branch, base_ref=project_branch)
    worktree_add(repo, integration_worktree_path, ref=temp_branch)

    try:
        # Step 3: merge phase branch into temp.
        merge_res = _run(
            ["git", "merge", "--no-ff", "--no-edit", phase_branch],
            cwd=integration_worktree_path,
            check=False,
        )
        if merge_res.returncode != 0:
            # Abort the merge to leave the worktree clean for removal.
            _run(["git", "merge", "--abort"], cwd=integration_worktree_path, check=False)
            return _cleanup_red(
                repo,
                integration_worktree_path,
                temp_branch,
                merge_conflict=True,
                test_failure_message=None,
            )

        # Step 4: tests.
        try:
            run_tests(integration_worktree_path)
        except IntegrationTestFailure as e:
            return _cleanup_red(
                repo,
                integration_worktree_path,
                temp_branch,
                merge_conflict=False,
                test_failure_message=str(e),
            )

        # Step 5: green. Fast-forward project branch.
        merge_sha = current_sha(repo, temp_branch)
        _run(
            ["git", "branch", "-f", project_branch, merge_sha],
            cwd=repo,
        )
        # Cleanup temp branch + worktree.
        worktree_remove(repo, integration_worktree_path, force=True)
        delete_branch(repo, temp_branch, force=True)
        return IntegrationResult(
            green=True,
            merge_sha=merge_sha,
            temp_branch=temp_branch,
            merge_conflict=False,
        )
    except GitOpsError:
        # Best-effort cleanup, then re-raise.
        try:
            worktree_remove(repo, integration_worktree_path, force=True)
        except GitOpsError:
            pass
        try:
            delete_branch(repo, temp_branch, force=True)
        except GitOpsError:
            pass
        raise


def _cleanup_red(
    repo: Path,
    integration_worktree_path: Path,
    temp_branch: str,
    *,
    merge_conflict: bool,
    test_failure_message: str | None,
) -> IntegrationResult:
    try:
        worktree_remove(repo, integration_worktree_path, force=True)
    except GitOpsError:
        if Path(integration_worktree_path).exists():
            shutil.rmtree(integration_worktree_path, ignore_errors=True)
    try:
        delete_branch(repo, temp_branch, force=True)
    except GitOpsError:
        pass
    return IntegrationResult(
        green=False,
        merge_sha=None,
        temp_branch=temp_branch,
        merge_conflict=merge_conflict,
        test_failure_message=test_failure_message,
    )
