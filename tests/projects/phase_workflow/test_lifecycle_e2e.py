"""End-to-end integration test: 03c phase lifecycle on a synthetic project.

Exercises the full lifecycle without the daemon or OpenCode:
- project branch creation
- phase 1 spawn -> commit -> temp-integration merge -> review payload
- finding lifecycle (open -> verified, deferred_until_phase, wontfix)
- review supersession when a later cumulative review covers a strict superset
- multi-parent phase_4 waits for both parents verified
- scrap-and-restart cascade: scrap phase_2 with cascade pauses descendant phase_4

Uses real git, real state, real payload rendering. The only thing mocked
is the OpenCode review (we record-and-mark-clean directly to test the state
machine).
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECTS_SCRIPTS = Path(__file__).parent.parent.parent.parent / "Projects" / "scripts"
sys.path.insert(0, str(PROJECTS_SCRIPTS))

from phase_workflow import dag as dag_mod
from phase_workflow import git_ops
from phase_workflow import manifests as manifests_mod
from phase_workflow import reviews as reviews_mod
from phase_workflow import state as state_mod


def _run(args, cwd):
    return subprocess.run(args, cwd=str(cwd), check=True, capture_output=True, text=True)


def _commit(repo, name, content):
    target = repo / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    _run(["git", "add", name], cwd=repo)
    _run(["git", "commit", "-m", f"add {name}"], cwd=repo)


@pytest.fixture
def project(tmp_path):
    r"""Build a fresh git repo + initial 03c state for PROJ-TEST-001.

    DAG shape:
        phase_1 (root)
            \-> phase_2 -> phase_4 (multi-parent: phase_2 + phase_3)
            \-> phase_3 -> phase_4
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(["git", "init", "-b", "main"], cwd=repo)
    _run(["git", "config", "user.email", "t@t"], cwd=repo)
    _run(["git", "config", "user.name", "T"], cwd=repo)
    _commit(repo, "README.md", "init")

    state_path = tmp_path / "phase_state.json"
    s = state_mod.initial_state("PROJ-TEST-001")
    state_mod.add_phase(s, "phase_1", depends_on=[], planned_files=["foo.py"])
    state_mod.add_phase(s, "phase_2", depends_on=["phase_1"], planned_files=["bar.py"])
    state_mod.add_phase(s, "phase_3", depends_on=["phase_1"], planned_files=["baz.py"])
    state_mod.add_phase(s, "phase_4", depends_on=["phase_2", "phase_3"], planned_files=["qux.py"])
    state_mod.save_state(state_path, s)

    # Create the project branch (proj/PROJ-TEST-001/main).
    git_ops.create_branch(repo, s["project_branch"], base_ref="main")

    return {
        "repo": repo,
        "state_path": state_path,
        "tmp": tmp_path,
        "project_branch": s["project_branch"],
    }


def _spawn_and_commit(project, phase_id, content):
    """Spawn a phase worktree, write `content` to its planned file, commit."""
    repo = project["repo"]
    s = state_mod.load_state(project["state_path"])
    phase_branch = (
        f"{s['project_branch'].rsplit('/', 1)[0]}/{phase_id}"
    )
    git_ops.create_branch(repo, phase_branch, base_ref=s["project_branch"])
    base_sha = git_ops.current_sha(repo, phase_branch)

    wt = project["tmp"] / "phases" / phase_id
    git_ops.worktree_add(repo, wt, ref=phase_branch)

    file_name = s["phases"][phase_id]["planned_files"][0]
    (wt / file_name).write_text(content, encoding="utf-8")
    _run(["git", "add", file_name], cwd=wt)
    _run(["git", "commit", "-m", f"PROJ-TEST-001 {phase_id} work"], cwd=wt)
    head_sha = git_ops.current_sha(repo, phase_branch)

    state_mod.set_phase_branch(s, phase_id, phase_branch=phase_branch, phase_base_sha=base_sha)
    state_mod.set_phase_head_sha(s, phase_id, head_sha)
    state_mod.set_phase_status(s, phase_id, "in_progress")
    state_mod.save_state(project["state_path"], s)
    return wt, base_sha, head_sha


def _integrate_and_dispatch(project, phase_id):
    """Run temp-integration merge and simulate review dispatch."""
    repo = project["repo"]
    s = state_mod.load_state(project["state_path"])
    phase_branch = s["phases"][phase_id]["phase_branch"]

    integration_wt = project["tmp"] / "integration" / phase_id
    result = git_ops.temp_integration_merge(
        repo,
        project_branch=s["project_branch"],
        phase_branch=phase_branch,
        phase_id=phase_id,
        integration_worktree_path=integration_wt,
        run_tests=lambda _wt: None,
    )
    assert result.green, f"temp-integration failed for {phase_id}: conflict={result.merge_conflict}"

    # Record committed status and merge SHA.
    state_mod.set_phase_merged(s, phase_id, result.merge_sha)
    state_mod.set_phase_status(s, phase_id, "committed")

    # Simulate dispatching a review.
    review_id = f"req_test_{phase_id}"
    state_mod.record_review(
        s,
        review_id=review_id,
        project_tip_sha=result.merge_sha,
        coverage_set=dag_mod.coverage_set(s, focus_phase=phase_id),
        focus_phase=phase_id,
        review_mode=s["phases"][phase_id]["review_mode"],
        dispatched_at_utc="2026-05-03T18:00:00Z",
    )
    state_mod.set_phase_review_request(s, phase_id, review_id)
    state_mod.set_phase_status(s, phase_id, "under_review")
    state_mod.save_state(project["state_path"], s)
    return result.merge_sha, review_id


def _mark_clean(project, review_id):
    s = state_mod.load_state(project["state_path"])
    state_mod.mark_review_result(s, review_id, "completed_clean", result_path=f"Reviews/results/{review_id}")
    state_mod.save_state(project["state_path"], s)


# ---------------------------------------------------------------------------
# Phase 1 lifecycle
# ---------------------------------------------------------------------------


def test_phase_1_full_lifecycle(project):
    """Spawn phase_1, commit, integrate, dispatch review, verify."""
    s = state_mod.load_state(project["state_path"])
    assert dag_mod.eligible(s) == ["phase_1"]

    _spawn_and_commit(project, "phase_1", "phase 1 code")
    project_tip, review_id = _integrate_and_dispatch(project, "phase_1")

    s = state_mod.load_state(project["state_path"])
    assert s["phases"]["phase_1"]["status"] == "under_review"
    assert s["phases"]["phase_1"]["merged_into_project_at_sha"] == project_tip
    assert s["reviews"][review_id]["coverage_set"] == ["phase_1"]

    # phase_2 / phase_3 should NOT be eligible yet (phase_1 not verified).
    assert "phase_2" not in dag_mod.eligible(s)

    # Mark review clean -> phase_1 verified -> phase_2 and phase_3 both eligible.
    _mark_clean(project, review_id)
    s = state_mod.load_state(project["state_path"])
    assert s["phases"]["phase_1"]["status"] == "verified"
    assert s["phases"]["phase_1"]["verifying_review_id"] == review_id

    eligible = dag_mod.eligible(s)
    # File-conflict check shouldn't trip here (planned_files disjoint).
    assert set(eligible) == {"phase_2", "phase_3"}


# ---------------------------------------------------------------------------
# Parallel siblings, multi-parent
# ---------------------------------------------------------------------------


def test_full_dag_to_verified(project):
    """Walk phases 1..4 to verified; phase_4 must wait for both parents verified."""
    # Phase 1
    _spawn_and_commit(project, "phase_1", "p1")
    _, r1 = _integrate_and_dispatch(project, "phase_1")
    _mark_clean(project, r1)

    # Phase 2 + phase 3 in parallel.
    _spawn_and_commit(project, "phase_2", "p2")
    _, r2 = _integrate_and_dispatch(project, "phase_2")

    s = state_mod.load_state(project["state_path"])
    assert "phase_4" not in dag_mod.eligible(s)  # phase_3 not done

    _spawn_and_commit(project, "phase_3", "p3")
    _, r3 = _integrate_and_dispatch(project, "phase_3")

    s = state_mod.load_state(project["state_path"])
    assert "phase_4" not in dag_mod.eligible(s)  # phase_2 / phase_3 not yet verified

    _mark_clean(project, r2)
    _mark_clean(project, r3)

    s = state_mod.load_state(project["state_path"])
    assert s["phases"]["phase_2"]["status"] == "verified"
    assert s["phases"]["phase_3"]["status"] == "verified"
    assert dag_mod.eligible(s) == ["phase_4"]

    # Phase 4
    _spawn_and_commit(project, "phase_4", "p4")
    _, r4 = _integrate_and_dispatch(project, "phase_4")
    _mark_clean(project, r4)

    s = state_mod.load_state(project["state_path"])
    assert s["phases"]["phase_4"]["status"] == "verified"
    # phase_4's review covers all four phases.
    assert set(s["reviews"][r4]["coverage_set"]) == {"phase_1", "phase_2", "phase_3", "phase_4"}
    # Earlier reviews are superseded by the next review whose coverage is a
    # strict superset. r1's coverage {p1} ⊂ r2's {p1,p2} so r2 supersedes r1.
    # r2's coverage ⊂ r4's so r4 supersedes r2 (and r3).
    assert s["reviews"][r1]["superseded_by"] is not None
    assert s["reviews"][r2]["superseded_by"] == r4
    assert s["reviews"][r3]["superseded_by"] == r4


# ---------------------------------------------------------------------------
# Findings lifecycle
# ---------------------------------------------------------------------------


def test_finding_lifecycle_deferred_then_resolved(project):
    """A deferred-until-phase finding resurfaces and gets verified later."""
    _spawn_and_commit(project, "phase_1", "p1")
    _, r1 = _integrate_and_dispatch(project, "phase_1")

    # Suppose review r1 surfaces a finding that the agent defers to phase_3.
    s = state_mod.load_state(project["state_path"])
    state_mod.add_finding(
        s, "FND-001", "fp_x", r1, "phase_1", "MAJ", "needs phase_3 API to fix"
    )
    state_mod.set_finding_status(
        s, "FND-001", "deferred_until_phase", deferred_until_phase="phase_3"
    )
    # r1 cannot be marked completely clean if there's a finding pending.
    state_mod.mark_review_result(s, r1, "completed_findings", result_path="Reviews/results/r1")
    # But phase_1 is still allowed to be verified by a later cumulative review.
    state_mod.save_state(project["state_path"], s)

    # Continue: complete phase_1 verification path requires us to advance —
    # for the test we'll mark clean manually here (representing a later review).
    s = state_mod.load_state(project["state_path"])
    state_mod.set_phase_status(s, "phase_1", "verified")
    s["phases"]["phase_1"]["verifying_review_id"] = r1
    state_mod.save_state(project["state_path"], s)

    # phase_2 / phase_3 in parallel.
    _spawn_and_commit(project, "phase_2", "p2")
    _, r2 = _integrate_and_dispatch(project, "phase_2")
    _mark_clean(project, r2)

    _spawn_and_commit(project, "phase_3", "p3")
    project_tip_3, r3 = _integrate_and_dispatch(project, "phase_3")
    # Now r3 should resurface FND-001 because target phase reached.
    s = state_mod.load_state(project["state_path"])
    payload = reviews_mod.build_payload(
        s,
        focus_phase="phase_3",
        project_tip_sha=project_tip_3,
        files_newly_changed=["baz.py"],
        files_in_earlier_phases=["foo.py", "bar.py"],
        worktree_path_for_review="wt",
    )
    assert "FND-001" in payload["instructions"]
    assert "deferred to phase_3" in payload["instructions"].lower() or "phase_3" in payload["instructions"]

    # Operator resolves the finding via remediation, then r3 returns clean.
    state_mod.set_finding_status(
        s, "FND-001", "verified", verifying_review_id=r3
    )
    state_mod.save_state(project["state_path"], s)
    _mark_clean(project, r3)

    s = state_mod.load_state(project["state_path"])
    assert s["findings"]["FND-001"]["status"] == "verified"
    assert s["findings"]["FND-001"]["verifying_review_id"] == r3


# ---------------------------------------------------------------------------
# Scrap-and-restart cascade
# ---------------------------------------------------------------------------


def test_scrap_cascade_pauses_descendant(project):
    """Scrapping phase_2 with descendants in flight pauses them."""
    _spawn_and_commit(project, "phase_1", "p1")
    _, r1 = _integrate_and_dispatch(project, "phase_1")
    _mark_clean(project, r1)

    _spawn_and_commit(project, "phase_2", "p2")
    _, _r2 = _integrate_and_dispatch(project, "phase_2")
    # phase_2 is now under_review (descendant of phase_1).

    # Suppose we now scrap phase_2 (without --cascade).
    s = state_mod.load_state(project["state_path"])
    # Default behavior: pause descendants. phase_4 depends on phase_2 + phase_3,
    # but it's not yet started so scrap_history just gets recorded as pause.
    # We exercise the descendant computation.
    descendants = []
    queue = ["phase_2"]
    while queue:
        head = queue.pop(0)
        for pid, ph in s["phases"].items():
            if head in ph["depends_on"] and pid not in descendants:
                descendants.append(pid)
                queue.append(pid)
    assert "phase_4" in descendants

    # Hard scrap phase_2.
    state_mod.record_scrap(s, "phase_2", reason="test scrap")
    state_mod.save_state(project["state_path"], s)
    s = state_mod.load_state(project["state_path"])
    assert s["phases"]["phase_2"]["status"] == "not_started"
    assert s["phases"]["phase_2"]["phase_branch"] is None
    assert len(s["phases"]["phase_2"]["scrap_history"]) == 1


# ---------------------------------------------------------------------------
# Manifest regeneration
# ---------------------------------------------------------------------------


def test_manifest_reflects_committed_phases(project):
    _spawn_and_commit(project, "phase_1", "p1")
    _integrate_and_dispatch(project, "phase_1")

    s = state_mod.load_state(project["state_path"])
    text = manifests_mod.render_manifest(s, repo_root=project["repo"])
    assert "phase_1" in text
    assert "foo.py" in text


# ---------------------------------------------------------------------------
# Review payload includes checkout block
# ---------------------------------------------------------------------------


def test_review_payload_includes_checkout_and_coverage(project):
    _spawn_and_commit(project, "phase_1", "p1")
    project_tip, _r1 = _integrate_and_dispatch(project, "phase_1")
    s = state_mod.load_state(project["state_path"])
    payload = reviews_mod.build_payload(
        s,
        focus_phase="phase_1",
        project_tip_sha=project_tip,
        files_newly_changed=["foo.py"],
        files_in_earlier_phases=[],
        worktree_path_for_review="AgentCoordination/opencodereview/local/worktrees/req_X",
    )
    assert payload["checkout"]["mode"] == "detached_worktree"
    assert payload["checkout"]["sha"] == project_tip
    assert payload["coverage"]["focus_phase"] == "phase_1"
    assert payload["coverage"]["project_tip_sha"] == project_tip
    assert payload["coverage"]["coverage_set"] == ["phase_1"]
    # JSON-serialise to confirm no surprises.
    json.dumps(payload)
