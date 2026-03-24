"""
Tests that the root pyproject.toml exists and satisfies the infographic-eval
project spec (task-1).

RED phase: these tests fail because pyproject.toml does not yet exist.
GREEN phase: they pass once the file is created correctly.
"""

import tomllib
from pathlib import Path

ROOT = Path(__file__).parent.parent
PYPROJECT = ROOT / "pyproject.toml"


def _load() -> dict:
    with PYPROJECT.open("rb") as f:
        return tomllib.load(f)


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------


def test_pyproject_exists():
    assert PYPROJECT.exists(), "pyproject.toml must exist at project root"


# ---------------------------------------------------------------------------
# [project] metadata
# ---------------------------------------------------------------------------


def test_project_name():
    data = _load()
    assert data["project"]["name"] == "infographic-eval"


def test_project_version():
    data = _load()
    assert data["project"]["version"] == "0.1.0"


def test_requires_python():
    data = _load()
    assert data["project"]["requires-python"] == ">=3.11"


def test_core_dependency_openai():
    data = _load()
    deps = data["project"]["dependencies"]
    assert any("openai" in d for d in deps), "openai must be in dependencies"


def test_core_dependency_pyyaml():
    data = _load()
    deps = data["project"]["dependencies"]
    assert any("pyyaml" in d.lower() for d in deps), "pyyaml must be in dependencies"


# ---------------------------------------------------------------------------
# [project.optional-dependencies]  dev extras
# ---------------------------------------------------------------------------


def test_dev_extra_pytest():
    data = _load()
    dev_deps = data["project"]["optional-dependencies"]["dev"]
    assert any("pytest" in d for d in dev_deps), "pytest must be in [dev] extras"


# ---------------------------------------------------------------------------
# [tool.pytest.ini_options]
# ---------------------------------------------------------------------------


def test_pytest_testpaths():
    data = _load()
    opts = data["tool"]["pytest"]["ini_options"]
    assert opts["testpaths"] == ["tests"]


def test_pytest_pythonpath_includes_dot():
    data = _load()
    opts = data["tool"]["pytest"]["ini_options"]
    assert "." in opts["pythonpath"], "pythonpath must include '.' so eval/ is importable"


def test_pytest_pythonpath_includes_tests():
    data = _load()
    opts = data["tool"]["pytest"]["ini_options"]
    assert "tests" in opts["pythonpath"], (
        "pythonpath must include 'tests' so bare imports like "
        "'from helpers import read_guide' keep working"
    )
