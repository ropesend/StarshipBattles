"""Tests for Projects/scripts/phase_workflow/git_ops.py."""
import subprocess
import sys
from pathlib import Path

import pytest

PROJECTS_SCRIPTS = Path(__file__).parent.parent.parent.parent / "Projects" / "scripts"
sys.path.insert(0, str(PROJECTS_SCRIPTS))

from phase_workflow import git_ops


def _run(args, cwd):
    return subprocess.run(args, cwd=str(cwd), check=True, capture_output=True, text=True)


def _commit(repo, name, content="x"):
    (repo / name).write_text(content, encoding="utf-8")
    _run(["git", "add", name], cwd=repo)
    _run(["git", "commit", "-m", f"add {name}"], cwd=repo)


@pytest.fixture
def repo(tmp_path):
    """Initialize a fresh git repo with a single commit on main."""
    r = tmp_path / "repo"
    r.mkdir()
    _run(["git", "init", "-b", "main"], cwd=r)
    _run(["git", "config", "user.email", "test@example.com"], cwd=r)
    _run(["git", "config", "user.name", "Test"], cwd=r)
    _commit(r, "README.md", "initial")
    return r


def test_current_sha_returns_full_hash(repo):
    sha = git_ops.current_sha(repo, "main")
    assert len(sha) == 40
    assert all(c in "0123456789abcdef" for c in sha)


def test_current_sha_unknown_ref_raises(repo):
    with pytest.raises(git_ops.GitOpsError):
        git_ops.current_sha(repo, "nonexistent-branch")


def test_create_branch_from_ref(repo):
    base_sha = git_ops.current_sha(repo, "main")
    git_ops.create_branch(repo, "proj/PROJ-TEST-001", base_ref="main")
    assert git_ops.current_sha(repo, "proj/PROJ-TEST-001") == base_sha


def test_create_branch_already_exists_raises(repo):
    git_ops.create_branch(repo, "proj/PROJ-TEST-001", base_ref="main")
    with pytest.raises(git_ops.GitOpsError):
        git_ops.create_branch(repo, "proj/PROJ-TEST-001", base_ref="main")


def test_branch_exists(repo):
    assert not git_ops.branch_exists(repo, "proj/PROJ-TEST-001")
    git_ops.create_branch(repo, "proj/PROJ-TEST-001", base_ref="main")
    assert git_ops.branch_exists(repo, "proj/PROJ-TEST-001")


def test_delete_branch(repo):
    git_ops.create_branch(repo, "tmp/foo", base_ref="main")
    assert git_ops.branch_exists(repo, "tmp/foo")
    git_ops.delete_branch(repo, "tmp/foo")
    assert not git_ops.branch_exists(repo, "tmp/foo")


def test_worktree_add_creates_directory_and_checks_out(repo, tmp_path):
    wt = tmp_path / "wt"
    # main is already checked out at the bare repo, so detach for the second worktree.
    git_ops.worktree_add(repo, wt, ref="main", detach=True)
    assert wt.exists()
    assert (wt / "README.md").exists()


def test_worktree_add_with_new_branch(repo, tmp_path):
    wt = tmp_path / "wt"
    git_ops.worktree_add(repo, wt, ref="main", new_branch="proj/PROJ-TEST-001/phase_1")
    assert git_ops.branch_exists(repo, "proj/PROJ-TEST-001/phase_1")


def test_worktree_remove(repo, tmp_path):
    wt = tmp_path / "wt"
    git_ops.worktree_add(repo, wt, ref="main", detach=True)
    git_ops.worktree_remove(repo, wt)
    assert not wt.exists()


def test_worktree_list_includes_added(repo, tmp_path):
    wt = tmp_path / "wt"
    git_ops.worktree_add(repo, wt, ref="main", detach=True)
    listed = git_ops.worktree_list(repo)
    paths = [Path(w["path"]).resolve() for w in listed]
    assert wt.resolve() in paths


def test_worktree_remove_with_uncommitted_refuses(repo, tmp_path):
    wt = tmp_path / "wt"
    git_ops.worktree_add(repo, wt, ref="main", new_branch="dirty")
    (wt / "extra.txt").write_text("dirty work", encoding="utf-8")
    with pytest.raises(git_ops.GitOpsError, match="uncommitted"):
        git_ops.worktree_remove(repo, wt, force=False)


def test_worktree_remove_force_removes_dirty(repo, tmp_path):
    wt = tmp_path / "wt"
    git_ops.worktree_add(repo, wt, ref="main", new_branch="dirty2")
    (wt / "extra.txt").write_text("dirty work", encoding="utf-8")
    git_ops.worktree_remove(repo, wt, force=True)
    assert not wt.exists()


def test_temp_integration_merge_green_fast_forwards_project_branch(repo, tmp_path):
    """Phase branch merges cleanly into project branch via temp integration."""
    git_ops.create_branch(repo, "proj/PROJ-TEST-001/main", base_ref="main")
    project_tip_before = git_ops.current_sha(repo, "proj/PROJ-TEST-001/main")

    # Create phase branch from project tip and add a commit.
    git_ops.create_branch(repo, "proj/PROJ-TEST-001/phase_1", base_ref="proj/PROJ-TEST-001/main")
    pwt = tmp_path / "phase_wt"
    git_ops.worktree_add(repo, pwt, ref="proj/PROJ-TEST-001/phase_1")
    _commit(pwt, "feature.py", "feature")
    phase_head = git_ops.current_sha(repo, "proj/PROJ-TEST-001/phase_1")
    assert phase_head != project_tip_before

    # Run temp-integration merge with green tests.
    integration_wt = tmp_path / "integration_wt"
    result = git_ops.temp_integration_merge(
        repo,
        project_branch="proj/PROJ-TEST-001/main",
        phase_branch="proj/PROJ-TEST-001/phase_1",
        phase_id="phase_1",
        integration_worktree_path=integration_wt,
        run_tests=lambda _wt: None,  # green
    )
    assert result.green is True
    assert result.merge_sha is not None
    # Project branch fast-forwarded to integration commit.
    assert git_ops.current_sha(repo, "proj/PROJ-TEST-001/main") == result.merge_sha
    # Temp branch and worktree cleaned up.
    assert not git_ops.branch_exists(repo, result.temp_branch)
    assert not integration_wt.exists()


def test_temp_integration_merge_red_keeps_phase_branch_cleans_temp(repo, tmp_path):
    """Test failure leaves phase branch alive, temp branch/worktree gone."""
    git_ops.create_branch(repo, "proj/PROJ-TEST-001/main", base_ref="main")
    project_tip_before = git_ops.current_sha(repo, "proj/PROJ-TEST-001/main")

    git_ops.create_branch(repo, "proj/PROJ-TEST-001/phase_1", base_ref="proj/PROJ-TEST-001/main")
    pwt = tmp_path / "phase_wt"
    git_ops.worktree_add(repo, pwt, ref="proj/PROJ-TEST-001/phase_1")
    _commit(pwt, "feature.py", "feature")

    integration_wt = tmp_path / "integration_wt"

    def fail_tests(_wt):
        raise git_ops.IntegrationTestFailure("simulated test failure")

    result = git_ops.temp_integration_merge(
        repo,
        project_branch="proj/PROJ-TEST-001/main",
        phase_branch="proj/PROJ-TEST-001/phase_1",
        phase_id="phase_1",
        integration_worktree_path=integration_wt,
        run_tests=fail_tests,
    )
    assert result.green is False
    assert result.merge_sha is None
    # Project branch unchanged.
    assert git_ops.current_sha(repo, "proj/PROJ-TEST-001/main") == project_tip_before
    # Phase branch still alive.
    assert git_ops.branch_exists(repo, "proj/PROJ-TEST-001/phase_1")
    # Temp cleanup happened.
    assert not git_ops.branch_exists(repo, result.temp_branch)
    assert not integration_wt.exists()


def test_temp_integration_merge_conflict_returns_red(repo, tmp_path):
    """Merge conflict treated as red, project branch unchanged, temp cleaned."""
    git_ops.create_branch(repo, "proj/PROJ-TEST-001/main", base_ref="main")
    # Project branch adds conflict.txt with content 'A'
    pwt = tmp_path / "proj_wt"
    git_ops.worktree_add(repo, pwt, ref="proj/PROJ-TEST-001/main")
    _commit(pwt, "conflict.txt", "A")

    project_tip = git_ops.current_sha(repo, "proj/PROJ-TEST-001/main")

    # Phase branch from earlier base; adds conflict.txt with content 'B'
    git_ops.create_branch(repo, "proj/PROJ-TEST-001/phase_1", base_ref="main")
    phwt = tmp_path / "phase_wt"
    git_ops.worktree_add(repo, phwt, ref="proj/PROJ-TEST-001/phase_1")
    _commit(phwt, "conflict.txt", "B")

    integration_wt = tmp_path / "integration_wt"
    result = git_ops.temp_integration_merge(
        repo,
        project_branch="proj/PROJ-TEST-001/main",
        phase_branch="proj/PROJ-TEST-001/phase_1",
        phase_id="phase_1",
        integration_worktree_path=integration_wt,
        run_tests=lambda _wt: None,
    )
    assert result.green is False
    assert result.merge_conflict is True
    assert git_ops.current_sha(repo, "proj/PROJ-TEST-001/main") == project_tip
    assert not git_ops.branch_exists(repo, result.temp_branch)


def test_detect_orphan_worktrees_only_returns_unlisted(repo, tmp_path):
    """A live worktree should not be flagged orphan."""
    wt = tmp_path / "live_wt"
    git_ops.worktree_add(repo, wt, ref="main", detach=True)
    orphans = git_ops.detect_orphan_worktrees(
        repo, search_root=tmp_path, branch_prefix="proj/", live_worktrees={wt.resolve()}
    )
    assert wt.resolve() not in {Path(o).resolve() for o in orphans}
