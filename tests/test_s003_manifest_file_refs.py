"""S-003: Confirm every path in manifest.yaml categories.*.files exists on disk."""
import os
import yaml
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(REPO_ROOT, "manifest.yaml")


def _all_manifest_paths():
    with open(MANIFEST_PATH) as f:
        manifest = yaml.safe_load(f)
    paths = []
    for cat in manifest.get("categories", []):
        for entry in cat.get("files", []):
            path = entry.get("path")
            if path:
                paths.append(path)
    return paths


@pytest.mark.parametrize("path", _all_manifest_paths())
def test_manifest_referenced_file_exists(path):
    full = os.path.join(REPO_ROOT, path)
    assert os.path.isfile(full), f"Missing file: {path}"
