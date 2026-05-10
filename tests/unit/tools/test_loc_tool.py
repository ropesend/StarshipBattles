import builtins
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from Tools.loc import loc


def _load_loc_without_tiktoken(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    original_import = builtins.__import__

    def blocked_import(
        name: str,
        globals_: dict[str, Any] | None = None,
        locals_: dict[str, Any] | None = None,
        fromlist: Any = (),
        level: int = 0,
    ) -> Any:
        if name == "tiktoken" or name.startswith("tiktoken."):
            exc = ModuleNotFoundError("No module named 'tiktoken'")
            exc.name = "tiktoken"
            raise exc
        return original_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", blocked_import)
    spec = importlib.util.spec_from_file_location(
        "loc_without_tiktoken",
        Path(loc.__file__),
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_loc_tool_token_counter_is_available() -> None:
    assert loc._count_tokens("Starship Battles") > 0


def test_loc_tool_imports_without_tiktoken(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_loc_without_tiktoken(monkeypatch)

    assert module._ENCODING is None


def test_loc_tool_reports_repo_local_install_command_when_tiktoken_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_loc_without_tiktoken(monkeypatch)
    monkeypatch.setattr(module, "print_simple", lambda: module._count_tokens("Starship"))
    monkeypatch.setattr(module.sys, "argv", ["loc.py"])

    assert module.main() == 1

    captured = capsys.readouterr()
    assert "Missing Python dependency: tiktoken" in captured.err
    assert "python -m pip install -r" in captured.err
    assert str(module.ROOT / "requirements-dev.txt") in captured.err
    assert "Traceback" not in captured.err
