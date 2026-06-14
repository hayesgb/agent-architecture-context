"""S-002 & S-003: Validate manifest.yaml schema and file references."""
import os
import yaml
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(REPO_ROOT, "manifest.yaml")

ALLOWED_TASK_TYPES = {"all", "pipeline-development", "code-review", "architecture-review"}

REQUIRED_TOP_LEVEL_KEYS = {"version", "last_updated", "categories"}


@pytest.fixture(scope="module")
def manifest():
    assert os.path.isfile(MANIFEST_PATH), "manifest.yaml does not exist at repo root"
    with open(MANIFEST_PATH) as f:
        data = yaml.safe_load(f)
    assert data is not None, "manifest.yaml is empty or not valid YAML"
    return data


def test_manifest_has_required_top_level_keys(manifest):
    missing = REQUIRED_TOP_LEVEL_KEYS - set(manifest.keys())
    assert not missing, f"manifest.yaml missing required top-level keys: {sorted(missing)}"


def test_manifest_categories_is_a_list(manifest):
    assert isinstance(manifest["categories"], list), \
        "manifest.yaml 'categories' must be a list"


def test_manifest_every_file_entry_has_path(manifest):
    for cat in manifest["categories"]:
        cat_name = cat.get("name", "<unnamed>")
        for entry in cat.get("files", []):
            assert "path" in entry, (
                f"manifest.yaml category '{cat_name}': file entry missing 'path' field: {entry}"
            )


def test_manifest_every_file_entry_has_applies_to(manifest):
    for cat in manifest["categories"]:
        cat_name = cat.get("name", "<unnamed>")
        for entry in cat.get("files", []):
            assert "applies_to" in entry, (
                f"manifest.yaml category '{cat_name}': file entry at path "
                f"'{entry.get('path', '?')}' missing 'applies_to' field"
            )


def test_manifest_applies_to_values_are_allowed(manifest):
    for cat in manifest["categories"]:
        cat_name = cat.get("name", "<unnamed>")
        for entry in cat.get("files", []):
            for value in entry.get("applies_to", []):
                assert value in ALLOWED_TASK_TYPES, (
                    f"manifest.yaml category '{cat_name}', path '{entry.get('path')}': "
                    f"invalid applies_to value '{value}'. "
                    f"Allowed values: {sorted(ALLOWED_TASK_TYPES)}"
                )


def test_manifest_all_referenced_files_exist(manifest):
    for cat in manifest["categories"]:
        for entry in cat.get("files", []):
            path = entry.get("path")
            if path:
                full_path = os.path.join(REPO_ROOT, path)
                assert os.path.isfile(full_path), (
                    f"manifest.yaml references missing file: {path}"
                )
