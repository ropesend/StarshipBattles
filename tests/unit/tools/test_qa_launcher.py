from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import qa_launcher


def test_resolve_python_executable_uses_current_interpreter(tmp_path: Path) -> None:
    assert qa_launcher.resolve_python_executable(tmp_path) == sys.executable


def test_find_missing_qa_dependencies_reports_package_names(monkeypatch) -> None:
    missing_modules = {"dotenv", "sounddevice"}
    checked_modules: list[str] = []

    def fake_run(cmd, **kwargs) -> subprocess.CompletedProcess[str]:
        checked_modules.append(cmd[-1].removeprefix("import "))
        return subprocess.CompletedProcess(
            cmd,
            returncode=1 if checked_modules[-1] in missing_modules else 0,
            stdout="",
            stderr="missing",
        )

    monkeypatch.setattr(qa_launcher.subprocess, "run", fake_run)

    missing = qa_launcher.find_missing_qa_dependencies("python")

    assert missing == ["python-dotenv", "sounddevice"]
    assert "google.cloud.speech" in checked_modules
    assert "audioop" in checked_modules


def test_get_python_version_reports_major_minor(monkeypatch) -> None:
    def fake_run(cmd, **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(cmd, returncode=0, stdout="3.14\n", stderr="")

    monkeypatch.setattr(qa_launcher.subprocess, "run", fake_run)

    assert qa_launcher.get_python_version("python") == (3, 14)


def test_qa_python_version_requires_314() -> None:
    assert qa_launcher.is_supported_qa_python_version((3, 14))
    assert not qa_launcher.is_supported_qa_python_version((3, 13))
    assert not qa_launcher.is_supported_qa_python_version((3, 15))


def test_dependency_error_recommends_python_314(capsys) -> None:
    qa_launcher.print_dependency_error("python", ["sounddevice"])

    captured = capsys.readouterr()

    assert "pip install -r requirements-dev.txt" in captured.out
