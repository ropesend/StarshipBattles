from __future__ import annotations

import json
from pathlib import Path

from Tools.test_sharded import test_sharded as runner


def _summary(
    *,
    total: int = 10,
    passed: int = 10,
    failed: int = 0,
    errors: int = 0,
    skipped: int = 0,
) -> dict[str, int]:
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
    }


def _baseline_payload(
    *,
    total: int = 10,
    passed: int = 10,
    failed: int = 0,
    errors: int = 0,
    skipped: int = 0,
    changed_at: str = "2026-04-28T00:00:00Z",
) -> dict[str, object]:
    return {
        "schema_version": 2,
        "command": "python Tools/test_sharded/test_sharded.py",
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "baseline_changed_at": changed_at,
    }


def _configure_baseline_paths(
    tmp_path: Path,
    monkeypatch,
    *,
    install_id: str = "local-install",
) -> tuple[Path, Path]:
    baseline = tmp_path / "test_baseline.json"
    by_install = tmp_path / "test_baseline" / "by_install"
    local_install_id = tmp_path / "local" / "install_id.json"
    local_install_id.parent.mkdir(parents=True)
    local_install_id.write_text(json.dumps({"install_id": install_id}), encoding="utf-8")
    monkeypatch.setattr(runner, "TEST_BASELINE_FILE", baseline)
    monkeypatch.setattr(runner, "TEST_BASELINE_BY_INSTALL_DIR", by_install)
    monkeypatch.setattr(runner, "LOCAL_INSTALL_ID_FILE", local_install_id)
    return baseline, by_install / f"{install_id}.json"


def test_parse_shard_xml_includes_skipped_count(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(runner, "SHARD_RESULTS_DIR", tmp_path)
    (tmp_path / "shard_0.xml").write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
  <testsuite tests="4" failures="1" errors="1" skipped="1" time="1.25">
    <testcase classname="tests.unit.tools.test_demo" name="test_passes" time="0.10" />
    <testcase classname="tests.unit.tools.test_demo" name="test_skips" time="0.00">
      <skipped />
    </testcase>
  </testsuite>
</testsuites>
""",
        encoding="utf-8",
    )

    tests, failures, errors, skipped, shard_time, durations = runner.parse_shard_xml(0)

    assert tests == 4
    assert failures == 1
    assert errors == 1
    assert skipped == 1
    assert shard_time == 1.25
    assert 0.10 in durations.values()


def test_parse_shard_xml_prefers_exact_duration_sidecar_node_ids(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(runner, "SHARD_RESULTS_DIR", tmp_path)
    (tmp_path / "shard_0.xml").write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
  <testsuite tests="1" failures="0" errors="0" skipped="0" time="0.25">
    <testcase classname="tests.integration.ui.test_smoke" name="test_widget" time="0.25" />
  </testsuite>
</testsuites>
""",
        encoding="utf-8",
    )
    exact_node_id = "tests/integration/ui/test_smoke.py::test_widget"
    (tmp_path / "shard_0_durations.json").write_text(
        json.dumps({exact_node_id: 0.25}),
        encoding="utf-8",
    )

    *_, durations = runner.parse_shard_xml(0)

    assert durations == {exact_node_id: 0.25}


def test_assign_by_duration_uses_mean_duration_for_unknown_tests() -> None:
    test_ids = [
        "tests/test_known.py::test_fast",
        "tests/test_known.py::test_slow",
        "tests/test_unknown.py::test_new",
    ]
    durations = {
        "tests/test_known.py::test_fast": 1.0,
        "tests/test_known.py::test_slow": 3.0,
    }

    _, shard_times = runner.assign_by_duration(test_ids, 1, durations)

    assert shard_times == [6.0]


def test_assign_by_duration_prefers_matching_file_history_median() -> None:
    test_ids = [
        "tests/test_flaky_runtime.py::test_a",
        "tests/test_flaky_runtime.py::test_b",
        "tests/test_regular.py::test_a",
    ]
    durations = {
        "tests/test_flaky_runtime.py::test_a": 10.0,
        "tests/test_flaky_runtime.py::test_b": 10.0,
        "tests/test_regular.py::test_a": 2.0,
    }
    history = {
        "schema_version": 1,
        "files": {
            "tests/test_flaky_runtime.py": [
                {"duration": 4.0, "test_count": 2, "shards": 8, "shard": 0, "recorded_at": "t1"},
                {"duration": 6.0, "test_count": 2, "shards": 16, "shard": 0, "recorded_at": "t2"},
            ],
        },
    }

    _, shard_times = runner.assign_by_duration(test_ids, 1, durations, history)

    assert shard_times == [7.0]


def test_file_estimate_errors_identify_files_driving_shard_misses() -> None:
    shards = [
        [
            "tests/test_good.py::test_a",
            "tests/test_bad.py::test_a",
        ]
    ]
    historical_durations = {
        "tests/test_good.py::test_a": 1.0,
        "tests/test_bad.py::test_a": 2.0,
    }
    actual_durations = {
        "tests/test_good.py::test_a": 1.1,
        "tests/test_bad.py::test_a": 7.0,
    }

    errors = runner._file_estimate_errors(shards, actual_durations, historical_durations, {})

    assert errors[0]["file_path"] == "tests/test_bad.py"
    assert errors[0]["estimated_time"] == 2.0
    assert errors[0]["actual_time"] == 7.0
    assert errors[0]["error"] == 5.0


def test_build_shard_diagnostics_reports_file_stats_and_history_variability() -> None:
    shards = [
        [
            "tests/test_fast.py::test_a",
            "tests/test_fast.py::test_b",
            "tests/test_slow.py::test_a",
        ]
    ]
    historical_durations = {
        "tests/test_fast.py::test_a": 1.0,
        "tests/test_fast.py::test_b": 1.0,
        "tests/test_slow.py::test_a": 4.0,
    }
    actual_durations = {
        "tests/test_fast.py::test_a": 1.5,
        "tests/test_fast.py::test_b": 0.5,
        "tests/test_slow.py::test_a": 6.0,
    }
    history = {
        "schema_version": 1,
        "files": {
            "tests/test_fast.py": [
                {"duration": 2.0, "test_count": 2, "shards": 4, "shard": 0, "recorded_at": "t1"},
                {"duration": 3.0, "test_count": 2, "shards": 8, "shard": 1, "recorded_at": "t2"},
            ],
            "tests/test_slow.py": [
                {"duration": 4.0, "test_count": 1, "shards": 4, "shard": 0, "recorded_at": "t1"},
                {"duration": 8.0, "test_count": 1, "shards": 8, "shard": 1, "recorded_at": "t2"},
            ],
        },
    }

    diagnostics = runner._build_shard_diagnostics(
        shards,
        actual_durations,
        historical_durations,
        [9.0],
        history,
    )

    assert diagnostics[0]["file_min"] == 2.0
    assert diagnostics[0]["file_median"] == 4.0
    assert diagnostics[0]["file_max"] == 6.0
    assert diagnostics[0]["known_pct"] == 100.0
    assert diagnostics[0]["variability_max_pct"] > diagnostics[0]["variability_median_pct"]


def test_baseline_created_after_successful_whole_suite(
    tmp_path: Path,
    monkeypatch,
) -> None:
    baseline, verification = _configure_baseline_paths(tmp_path, monkeypatch)
    monkeypatch.setattr(runner, "_utc_timestamp", lambda: "2026-04-29T00:00:00Z")
    monkeypatch.setattr(runner, "_git_sha", lambda: "new-sha")

    status = runner._write_test_baseline_if_needed(
        _summary(total=12, passed=11, skipped=1),
        full_suite_success=True,
        refresh_baseline_timestamp=False,
    )

    assert status == "created"
    data = json.loads(baseline.read_text(encoding="utf-8"))
    assert data["total"] == 12
    assert data["passed"] == 11
    assert data["skipped"] == 1
    assert data["baseline_changed_at"] == "2026-04-29T00:00:00Z"
    assert "verified_at" not in data
    assert "git_sha" not in data

    verification_data = json.loads(verification.read_text(encoding="utf-8"))
    assert verification_data["install_id"] == "local-install"
    assert verification_data["total"] == 12
    assert verification_data["verified_at"] == "2026-04-29T00:00:00Z"
    assert verification_data["git_sha"] == "new-sha"


def test_baseline_unchanged_counts_do_not_rewrite_canonical_but_record_verification(
    tmp_path: Path,
    monkeypatch,
) -> None:
    baseline, verification = _configure_baseline_paths(tmp_path, monkeypatch)
    baseline.write_text(
        json.dumps(_baseline_payload(), indent=2),
        encoding="utf-8",
    )
    before = baseline.read_text(encoding="utf-8")
    monkeypatch.setattr(runner, "_utc_timestamp", lambda: "2026-04-29T00:00:00Z")
    monkeypatch.setattr(runner, "_git_sha", lambda: "new-sha")

    status = runner._write_test_baseline_if_needed(
        _summary(),
        full_suite_success=True,
        refresh_baseline_timestamp=False,
    )

    assert status == "verified"
    assert baseline.read_text(encoding="utf-8") == before
    data = json.loads(verification.read_text(encoding="utf-8"))
    assert data["verified_at"] == "2026-04-29T00:00:00Z"
    assert data["git_sha"] == "new-sha"


def test_refresh_baseline_timestamp_flag_keeps_canonical_counts_unchanged(
    tmp_path: Path,
    monkeypatch,
) -> None:
    baseline, verification = _configure_baseline_paths(tmp_path, monkeypatch)
    baseline.write_text(
        json.dumps(_baseline_payload(), indent=2),
        encoding="utf-8",
    )
    before = baseline.read_text(encoding="utf-8")
    monkeypatch.setattr(runner, "_utc_timestamp", lambda: "2026-04-29T00:00:00Z")
    monkeypatch.setattr(runner, "_git_sha", lambda: "new-sha")

    status = runner._write_test_baseline_if_needed(
        _summary(),
        full_suite_success=True,
        refresh_baseline_timestamp=True,
    )

    data = json.loads(baseline.read_text(encoding="utf-8"))
    assert status == "verified"
    assert baseline.read_text(encoding="utf-8") == before
    assert data["baseline_changed_at"] == "2026-04-28T00:00:00Z"
    verification_data = json.loads(verification.read_text(encoding="utf-8"))
    assert verification_data["verified_at"] == "2026-04-29T00:00:00Z"
    assert verification_data["git_sha"] == "new-sha"


def test_count_change_updates_baseline_changed_at(
    tmp_path: Path,
    monkeypatch,
) -> None:
    baseline, verification = _configure_baseline_paths(tmp_path, monkeypatch)
    baseline.write_text(
        json.dumps(_baseline_payload(), indent=2),
        encoding="utf-8",
    )
    monkeypatch.setattr(runner, "_utc_timestamp", lambda: "2026-04-29T00:00:00Z")
    monkeypatch.setattr(runner, "_git_sha", lambda: "new-sha")

    status = runner._write_test_baseline_if_needed(
        _summary(total=11, passed=11),
        full_suite_success=True,
        refresh_baseline_timestamp=False,
    )

    data = json.loads(baseline.read_text(encoding="utf-8"))
    assert status == "updated"
    assert data["total"] == 11
    assert data["baseline_changed_at"] == "2026-04-29T00:00:00Z"
    assert "verified_at" not in data
    verification_data = json.loads(verification.read_text(encoding="utf-8"))
    assert verification_data["total"] == 11
    assert verification_data["verified_at"] == "2026-04-29T00:00:00Z"


def test_failed_or_partial_run_never_updates_baseline(
    tmp_path: Path,
    monkeypatch,
) -> None:
    baseline, verification = _configure_baseline_paths(tmp_path, monkeypatch)

    status = runner._write_test_baseline_if_needed(
        _summary(total=10, passed=9, failed=1),
        full_suite_success=False,
        refresh_baseline_timestamp=True,
    )

    assert status == "skipped"
    assert not baseline.exists()
    assert not verification.exists()
