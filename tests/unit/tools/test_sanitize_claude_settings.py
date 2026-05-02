from __future__ import annotations

import json
from pathlib import Path

import pytest

from Tools.agent_coordination import sanitize_claude_settings as sanitizer


# ---------------------------------------------------------------------------
# classify_entry — pure function tests
# ---------------------------------------------------------------------------


def test_classify_simple_command_is_ok() -> None:
    result = sanitizer.classify_entry("Bash(pytest:*)")
    assert result.level == "OK"
    assert result.proposed_rewrite is None


def test_classify_repo_relative_glob_is_ok() -> None:
    result = sanitizer.classify_entry("Read(tests/unit/**)")
    assert result.level == "OK"


def test_classify_current_starshipbattles_path_is_ok() -> None:
    result = sanitizer.classify_entry("Read(//c/Developer/StarshipBattles/**)")
    assert result.level == "OK"


def test_classify_alt_starshipbattles_path_is_ok() -> None:
    result = sanitizer.classify_entry("Read(//c/Dev2/StarshipBattles/**)")
    assert result.level == "OK"


def test_classify_old_dev_starship_with_space_is_stale() -> None:
    result = sanitizer.classify_entry("Read(//c/Dev/Starship Battles/**)")
    assert result.level == "STALE_WARN"
    assert "Starship Battles" in result.reason


def test_classify_bash_embedded_old_dev_path_is_stale() -> None:
    rule = 'Bash(git -C "c:\\\\Dev\\\\Starship Battles" log)'
    result = sanitizer.classify_entry(rule)
    assert result.level == "STALE_WARN"


def test_classify_external_user_documents_review() -> None:
    result = sanitizer.classify_entry("Read(//c/Users/rossr/Documents/MyProject/**)")
    assert result.level == "EXTERNAL_REVIEW"


def test_classify_safe_system_library_is_ok() -> None:
    rule = "Read(//c/Users/rossr/AppData/Roaming/Python/Python311/site-packages/pygame_gui/elements/**)"
    result = sanitizer.classify_entry(rule)
    assert result.level == "OK"


def test_classify_dangerous_rm_rf() -> None:
    result = sanitizer.classify_entry("Bash(rm -rf:*)")
    assert result.level == "DANGEROUS"


def test_classify_dangerous_force_push() -> None:
    result = sanitizer.classify_entry("Bash(git push --force:*)")
    assert result.level == "DANGEROUS"


def test_classify_dangerous_broad_read() -> None:
    result = sanitizer.classify_entry("Read(//**)")
    assert result.level == "DANGEROUS"


def test_classify_secret_aws_key_fails() -> None:
    result = sanitizer.classify_entry("Bash(export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE)")
    assert result.level == "SECRET"


def test_classify_secret_openai_key_fails() -> None:
    result = sanitizer.classify_entry('Bash(echo "sk-1234567890abcdefghij1234567890")')
    assert result.level == "SECRET"


# ---------------------------------------------------------------------------
# Rewrite proposals — must not broaden
# ---------------------------------------------------------------------------


def test_stale_read_glob_proposes_rewrite_to_relative() -> None:
    result = sanitizer.classify_entry("Read(//c/Dev/Starship Battles/**)")
    assert result.proposed_rewrite is not None
    # Rewrite must preserve the `**` and not become `Read(**)`
    assert result.proposed_rewrite != "Read(**)"
    assert "**" in result.proposed_rewrite


def test_rewrite_preserves_specific_subpath() -> None:
    result = sanitizer.classify_entry(
        "Read(//c/Dev/Starship Battles/tests/unit/ui/test_panel.py)"
    )
    assert result.proposed_rewrite is not None
    # Should still reference tests/unit/ui/test_panel.py somewhere
    assert "tests/unit/ui/test_panel.py" in result.proposed_rewrite or \
           "tests\\unit\\ui\\test_panel.py" in result.proposed_rewrite


def test_no_broadening_check_rejects_globalization() -> None:
    assert sanitizer._broadens_permission(
        "Read(//c/Dev/Starship Battles/specific.py)",
        "Read(**)",
    )
    assert sanitizer._broadens_permission(
        "Read(//c/Dev/Starship Battles/sub/**)",
        "Read(**)",
    )
    # Renaming the checkout segment from old to new without changing scope is fine.
    assert not sanitizer._broadens_permission(
        "Read(//c/Dev/Starship Battles/**)",
        "Read(//c/Developer/StarshipBattles/**)",
    )
    assert not sanitizer._broadens_permission(
        "Read(//c/Dev/Starship Battles/sub/**)",
        "Read(//c/Developer/StarshipBattles/sub/**)",
    )


# ---------------------------------------------------------------------------
# File-level scan
# ---------------------------------------------------------------------------


def _write_settings(path: Path, *, rules: list[str], extra: dict | None = None) -> None:
    data: dict = {"permissions": {"allow": rules}}
    if extra is not None:
        data.update(extra)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def test_scan_file_returns_one_classification_per_rule(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    _write_settings(
        settings,
        rules=[
            "Bash(pytest:*)",
            "Read(//c/Dev/Starship Battles/**)",
            "Bash(rm -rf:*)",
        ],
    )

    report = sanitizer.scan_file(settings)
    assert report.path == settings
    assert len(report.classifications) == 3
    levels = [c.level for c in report.classifications]
    assert levels == ["OK", "STALE_WARN", "DANGEROUS"]


def test_scan_missing_file_returns_empty_report(tmp_path: Path) -> None:
    missing = tmp_path / ".claude" / "settings.local.json"
    report = sanitizer.scan_file(missing)
    assert report.path == missing
    assert report.classifications == []
    assert report.parse_error is None
    assert report.missing is True


def test_scan_malformed_json_records_parse_error(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text("{not valid", encoding="utf-8")
    report = sanitizer.scan_file(settings)
    assert report.parse_error is not None
    assert report.classifications == []


def test_scan_skips_non_permission_settings(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.json"
    _write_settings(
        settings,
        rules=["Bash(pytest:*)"],
        extra={"effortLevel": "high", "hooks": {"Stop": []}},
    )
    report = sanitizer.scan_file(settings)
    # effortLevel and hooks should not generate findings
    assert len(report.classifications) == 1
    assert report.classifications[0].level == "OK"


def test_scan_includes_additional_directories(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    settings.parent.mkdir(parents=True)
    settings.write_text(
        json.dumps({
            "permissions": {
                "allow": [],
                "additionalDirectories": [
                    "c:\\\\Dev\\\\Starship Battles\\\\Projects\\\\active_projects\\\\PROJ-216\\\\findings"
                ],
            }
        }),
        encoding="utf-8",
    )
    report = sanitizer.scan_file(settings)
    assert any(c.level == "STALE_WARN" for c in report.classifications)


# ---------------------------------------------------------------------------
# CLI / main
# ---------------------------------------------------------------------------


def test_main_dry_run_does_not_write_files(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    _write_settings(settings, rules=["Read(//c/Dev/Starship Battles/**)"])
    before = settings.read_text(encoding="utf-8")

    rc = sanitizer.main(["--repo-root", str(tmp_path)])

    assert rc == 0  # warnings only, dry-run still passes
    assert settings.read_text(encoding="utf-8") == before
    captured = capsys.readouterr()
    assert "STALE_WARN" in captured.out


def test_main_returns_nonzero_on_dangerous(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    _write_settings(settings, rules=["Bash(rm -rf:*)"])
    rc = sanitizer.main(["--repo-root", str(tmp_path)])
    assert rc != 0


def test_main_returns_nonzero_on_secret(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    _write_settings(settings, rules=["Bash(echo AKIAIOSFODNN7EXAMPLE)"])
    rc = sanitizer.main(["--repo-root", str(tmp_path)])
    assert rc != 0


def test_main_emits_json_report_when_requested(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    _write_settings(settings, rules=["Bash(pytest:*)", "Read(//c/Dev/Starship Battles/**)"])

    rc = sanitizer.main(["--repo-root", str(tmp_path), "--format", "json"])
    assert rc == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["schema_version"] == 1
    assert "files" in data
    assert any(
        any(c["level"] == "STALE_WARN" for c in entry["classifications"])
        for entry in data["files"]
    )


# ---------------------------------------------------------------------------
# Apply mode
# ---------------------------------------------------------------------------


def test_apply_rewrites_stale_entries_in_allow_list(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    _write_settings(
        settings,
        rules=[
            "Bash(pytest:*)",
            "Read(//c/Dev/Starship Battles/**)",
        ],
    )

    rc = sanitizer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc == 0

    data = json.loads(settings.read_text(encoding="utf-8"))
    rules = data["permissions"]["allow"]
    assert "Bash(pytest:*)" in rules
    assert "Read(//c/Dev/Starship Battles/**)" not in rules
    assert "Read(//c/Developer/StarshipBattles/**)" in rules


def test_apply_creates_backup(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    _write_settings(settings, rules=["Read(//c/Dev/Starship Battles/**)"])

    rc = sanitizer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc == 0
    backups = list(settings.parent.glob("settings.local.json.backup.*"))
    assert backups, "Expected at least one backup file after --apply"


def test_apply_refuses_when_secret_present(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    _write_settings(settings, rules=["Bash(echo AKIAIOSFODNN7EXAMPLE)"])

    before = settings.read_text(encoding="utf-8")
    rc = sanitizer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc != 0
    # File must not be modified when a SECRET is found.
    assert settings.read_text(encoding="utf-8") == before


def test_apply_refuses_when_dangerous_present(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    _write_settings(settings, rules=["Bash(rm -rf:*)", "Read(//c/Dev/Starship Battles/**)"])

    before = settings.read_text(encoding="utf-8")
    rc = sanitizer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc != 0
    assert settings.read_text(encoding="utf-8") == before


def test_apply_is_idempotent(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    _write_settings(settings, rules=["Read(//c/Dev/Starship Battles/**)"])

    rc1 = sanitizer.main(["--repo-root", str(tmp_path), "--apply"])
    rc2 = sanitizer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc1 == 0
    assert rc2 == 0
    data = json.loads(settings.read_text(encoding="utf-8"))
    assert "Read(//c/Developer/StarshipBattles/**)" in data["permissions"]["allow"]
    # Second run finds nothing to rewrite.


def test_apply_preserves_unchanged_entries(tmp_path: Path) -> None:
    settings = tmp_path / ".claude" / "settings.local.json"
    _write_settings(
        settings,
        rules=[
            "Bash(pytest:*)",
            "Bash(grep:*)",
            "Read(//c/Dev/Starship Battles/**)",
        ],
    )
    rc = sanitizer.main(["--repo-root", str(tmp_path), "--apply"])
    assert rc == 0
    rules = json.loads(settings.read_text(encoding="utf-8"))["permissions"]["allow"]
    assert "Bash(pytest:*)" in rules
    assert "Bash(grep:*)" in rules
