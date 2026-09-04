"""Lint: every shipped recipe that references an agent must be schema-v2 portable.

A recipe that says ``agent: infographic-builder:infographic-builder`` but
declares no dependency manifest only works when the *caller's* session bundle
already happens to ship that agent. Run it from any other bundle and the step
fails at dispatch with "agent not found in configuration" -- a silent
portability bug that no amount of YAML-shape testing catches.

The fix is structural: declare ``schema_version: 2`` plus a ``dependencies``
block naming the source that supplies each referenced agent. These tests hold
that invariant for every recipe under ``recipes/``, so a newly-added legacy
recipe fails CI instead of shipping broken-for-everyone-else.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = REPO_ROOT / "recipes"

#: Recipes deliberately left on the legacy schema, each with the reason why.
#: A file listed here is exempt from the schema-v2 requirement and MUST carry
#: a matching top-of-file comment explaining its exemption to a reader who
#: never opens this test. Empty today -- every shipped recipe is portable.
#:
#: The canonical reason to add an entry is ``agent: self``: a self-referential
#: step has no declarable source, so such a recipe cannot be made v2-safe.
LEGACY_EXEMPT: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def recipe_paths() -> list[Path]:
    """Every recipe YAML shipped by this bundle, sorted for stable test ids."""
    return sorted(
        p
        for p in RECIPES_DIR.rglob("*.yaml")
        if p.is_file()
    )


def load(path: Path) -> dict:
    """Parse a recipe file into a plain mapping."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path.name}: recipe must be a YAML mapping"
    return data


def _walk(node: object):
    """Yield every mapping nested anywhere inside ``node``."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def agent_refs(recipe: dict) -> set[str]:
    """Every ``agent:`` value in the recipe, at any nesting depth.

    Steps nest -- ``foreach`` bodies, ``parallel`` groups and stage steps all
    carry their own ``agent:`` -- so a top-level scan of ``steps`` would miss
    references and let a non-portable recipe pass.
    """
    return {
        mapping["agent"]
        for mapping in _walk(recipe)
        if isinstance(mapping.get("agent"), str)
    }


def declared_agents(recipe: dict) -> set[str]:
    """Every agent named by a ``dependencies[].required_agents`` entry."""
    declared: set[str] = set()
    for dep in recipe.get("dependencies") or []:
        if isinstance(dep, dict):
            declared.update(dep.get("required_agents") or [])
    return declared


ALL_RECIPES = recipe_paths()
RECIPE_IDS = [p.name for p in ALL_RECIPES]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_recipes_directory_is_not_empty() -> None:
    """Guard: an empty glob would make every parametrised test vacuously pass."""
    assert ALL_RECIPES, f"no recipe YAML found under {RECIPES_DIR}"


@pytest.mark.parametrize("path", ALL_RECIPES, ids=RECIPE_IDS)
def test_recipe_with_agent_refs_declares_schema_v2(path: Path) -> None:
    """A recipe referencing an agent must declare ``schema_version: 2``."""
    recipe = load(path)
    if not agent_refs(recipe):
        pytest.skip(f"{path.name} references no agents")
    if path.name in LEGACY_EXEMPT:
        pytest.skip(f"{path.name} exempt: {LEGACY_EXEMPT[path.name]}")

    assert recipe.get("schema_version") == 2, (
        f"{path.name} references agents {sorted(agent_refs(recipe))} but does not "
        "declare `schema_version: 2`. Without it the recipe only runs from a "
        "session bundle that already ships those agents. Add the manifest, or "
        "add the file to LEGACY_EXEMPT with a reason."
    )


@pytest.mark.parametrize("path", ALL_RECIPES, ids=RECIPE_IDS)
def test_schema_v2_recipe_declares_dependencies(path: Path) -> None:
    """``schema_version: 2`` requires a non-empty, well-formed ``dependencies``."""
    recipe = load(path)
    if recipe.get("schema_version") != 2:
        pytest.skip(f"{path.name} is not schema v2")

    deps = recipe.get("dependencies")
    assert isinstance(deps, list) and deps, (
        f"{path.name}: `dependencies` must be a non-empty list under schema v2"
    )
    for dep in deps:
        assert isinstance(dep, dict), f"{path.name}: each dependency must be a mapping"
        assert isinstance(dep.get("source"), str) and dep["source"], (
            f"{path.name}: every dependency needs a non-empty `source`"
        )
        assert dep.get("kind") in {"bundle", "behavior"}, (
            f"{path.name}: dependency `kind` must be 'bundle' or 'behavior', "
            f"got {dep.get('kind')!r}"
        )


@pytest.mark.parametrize("path", ALL_RECIPES, ids=RECIPE_IDS)
def test_every_referenced_agent_is_declared(path: Path) -> None:
    """Each namespaced agent a step uses must appear in ``required_agents``.

    Declaring ``schema_version: 2`` is not enough on its own: a manifest that
    forgets one of the agents the recipe actually dispatches to still fails at
    run time, just later and with a less obvious message.
    """
    recipe = load(path)
    if recipe.get("schema_version") != 2:
        pytest.skip(f"{path.name} is not schema v2")

    # Bare (un-namespaced) refs like `self` have no declarable source.
    referenced = {a for a in agent_refs(recipe) if ":" in a}
    missing = referenced - declared_agents(recipe)
    assert not missing, (
        f"{path.name}: agents {sorted(missing)} are dispatched by a step but not "
        "listed in any `dependencies[].required_agents`. Add them to the entry "
        "for the bundle that ships them."
    )


@pytest.mark.parametrize("path", ALL_RECIPES, ids=RECIPE_IDS)
def test_no_step_level_agent_config(path: Path) -> None:
    """Schema v2 rejects the historical step-level ``agent_config`` field."""
    recipe = load(path)
    if recipe.get("schema_version") != 2:
        pytest.skip(f"{path.name} is not schema v2")

    offenders = [m for m in _walk(recipe) if "agent_config" in m]
    assert not offenders, (
        f"{path.name}: `agent_config` is rejected at parse under schema v2; "
        "move the setting or remove it."
    )


def test_legacy_exempt_entries_point_at_real_files() -> None:
    """An exemption for a file that no longer exists silently weakens the lint."""
    known = set(RECIPE_IDS)
    stale = sorted(set(LEGACY_EXEMPT) - known)
    assert not stale, f"LEGACY_EXEMPT names recipes that do not exist: {stale}"
