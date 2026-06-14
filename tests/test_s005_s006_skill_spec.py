"""S-005 & S-006: Validate skill-spec.yaml exists and contains required keys."""
import os
import yaml
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_SPEC_PATH = os.path.join(REPO_ROOT, "agent-integration", "skill-spec.yaml")

REQUIRED_TOP_LEVEL_KEYS = ["name", "description", "auth", "endpoints", "output_format"]
REQUIRED_ENDPOINT_KEYS = ["manifest", "file"]


@pytest.fixture(scope="module")
def skill_spec():
    assert os.path.isfile(SKILL_SPEC_PATH), \
        "agent-integration/skill-spec.yaml does not exist"
    with open(SKILL_SPEC_PATH) as f:
        data = yaml.safe_load(f)
    assert data is not None, "skill-spec.yaml is empty or not valid YAML"
    return data


@pytest.mark.parametrize("key", REQUIRED_TOP_LEVEL_KEYS)
def test_skill_spec_has_required_key(skill_spec, key):
    assert key in skill_spec, f"skill-spec.yaml missing required key: {key}"


def test_skill_spec_auth_type_is_github_pat(skill_spec):
    auth = skill_spec.get("auth", {})
    assert auth.get("type") == "github-pat", \
        f"skill-spec.yaml auth.type must be 'github-pat', got: {auth.get('type')!r}"


def test_skill_spec_auth_has_scope(skill_spec):
    auth = skill_spec.get("auth", {})
    assert "scope" in auth, "skill-spec.yaml auth section missing 'scope' field"


def test_skill_spec_auth_has_header_format(skill_spec):
    auth = skill_spec.get("auth", {})
    assert "header" in auth, "skill-spec.yaml auth section missing 'header' field"


@pytest.mark.parametrize("endpoint_key", REQUIRED_ENDPOINT_KEYS)
def test_skill_spec_endpoints_has_required_key(skill_spec, endpoint_key):
    endpoints = skill_spec.get("endpoints", {})
    assert endpoint_key in endpoints, \
        f"skill-spec.yaml endpoints missing required key: {endpoint_key}"


def test_skill_spec_endpoints_are_github_contents_api_paths(skill_spec):
    endpoints = skill_spec.get("endpoints", {})
    for key, value in endpoints.items():
        url = value.get("url", "") if isinstance(value, dict) else str(value)
        assert "api.github.com/repos" in url, \
            f"skill-spec.yaml endpoints.{key} does not reference the GitHub Contents API: {url!r}"
