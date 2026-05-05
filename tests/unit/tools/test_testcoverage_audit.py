from __future__ import annotations

from pathlib import Path

from Tools.testcoverage_audit import testcoverage_audit as audit


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_PATH = REPO_ROOT / ".opencode" / "skills" / "ocode-testcoverage-audit" / "SKILL.md"


def test_method_symbols_have_bare_aliases(tmp_path, monkeypatch) -> None:
    prod_file = tmp_path / "game" / "core" / "sample.py"
    prod_file.parent.mkdir(parents=True)
    prod_file.write_text(
        "class Vector2:\n"
        "    def length(self):\n"
        "        return 1\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(audit, "PROJECT_ROOT", str(tmp_path))

    result = audit._scan_production_file(str(prod_file))

    assert result is not None
    symbols = result["symbols"]
    method = next(sym for sym in symbols if sym["name"] == "Vector2.length")
    assert method["aliases"] == ["length"]
    assert not any(sym["name"] == "length" for sym in symbols)


def test_coverage_matrix_matches_method_aliases(tmp_path, monkeypatch) -> None:
    test_file = tmp_path / "tests" / "unit" / "test_vector.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(
        "from game.core.math import Vector2\n"
        "\n"
        "def test_length():\n"
        "    assert Vector2(3, 4).length() == 5\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(audit, "PROJECT_ROOT", str(tmp_path))

    matrix = audit._build_coverage_matrix(
        [
            {
                "file": "game/core/math.py",
                "layer": "core",
                "loc": 10,
                "symbols": [
                    {
                        "name": "Vector2.length",
                        "type": "method",
                        "line": 1,
                        "aliases": ["length"],
                    }
                ],
            }
        ],
        [
            {
                "file": "tests/unit/test_vector.py",
                "imported_modules": ["game.core.math"],
                "imported_symbols": {},
            }
        ],
    )

    coverage = matrix["game/core/math.py"]["symbol_coverage"]["Vector2.length"]
    assert coverage["heuristic_match"] is True
    assert coverage["candidate_test_files"] == ["tests/unit/test_vector.py"]
    assert coverage["matched_names"] == ["length"]


def test_skill_does_not_claim_coverage_json_is_supported() -> None:
    text = SKILL_PATH.read_text(encoding="utf-8")

    assert "scanner CLI supports `--coverage-json <path>`" not in text
    assert "future extension point" in text.lower()


def test_skill_does_not_create_literal_review_dir() -> None:
    text = SKILL_PATH.read_text(encoding="utf-8")

    assert "Path('REVIEW_DIR/findings')" not in text
    assert "Path(r'{REVIEW_DIR}').joinpath('findings')" in text


def test_skill_verification_contract_distinguishes_sampled_claims() -> None:
    text = SKILL_PATH.read_text(encoding="utf-8")

    assert "independently verify every claim made by the Phase 2 discovery agent" not in text
    assert "independently verify every CRITICAL and MAJOR claim" in text
    assert "sampled MINOR and ADVISORY claims" in text
