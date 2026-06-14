# Generic HTTP Template — Agent Architecture Context

Copy-paste `curl` commands for fetching guidelines from the
`hayesgb/agent-architecture-context` repository via the GitHub Contents API.
Adapt these for your agent platform (Gemini extension, MCP server, Copilot plugin, etc.).

See [`agent-integration/skill-spec.yaml`](../skill-spec.yaml) for the full contract and
[`agent-integration/README.md`](../README.md) for setup instructions including PAT
generation and secure token storage.

---

## Prerequisites

- A fine-grained GitHub Personal Access Token (PAT) with **Contents: Read-only** permission
  scoped to `hayesgb/agent-architecture-context`.
- The token stored in your OS-native credential store (not in a file or env var).
  See `agent-integration/README.md` for storage instructions.

---

## Step 1 — Retrieve Your Token at Runtime

Retrieve the token from your OS-native credential store before making API calls.
**Never hardcode the token or read it from a plaintext file.**

### macOS — Keychain

```bash
GITHUB_PAT=$(security find-generic-password -s "agent-architecture-context-pat" -a "$USER" -w)
```

### Linux — libsecret / secret-tool

```bash
GITHUB_PAT=$(secret-tool lookup service agent-architecture-context-pat username "$USER")
```

### Windows — Credential Manager (PowerShell)

```powershell
# Using cmdkey / Windows Credential Manager
$cred = Get-StoredCredential -Target "agent-architecture-context-pat"
$GITHUB_PAT = $cred.GetNetworkCredential().Password
```

Alternatively, use the cross-platform [`keyring`](https://pypi.org/project/keyring/) Python library:

```python
import keyring
GITHUB_PAT = keyring.get_password("agent-architecture-context-pat", "github-pat")
```

---

## Step 2 — Fetch manifest.yaml

Fetch the manifest to discover which guideline files are available and their `applies_to` tags.

```bash
curl -s \
  -H "Accept: application/vnd.github.raw+json" \
  -H "Authorization: Bearer ${GITHUB_PAT}" \
  "https://api.github.com/repos/hayesgb/agent-architecture-context/contents/manifest.yaml"
```

**Expected response:** Raw YAML content of `manifest.yaml`.

**On 401/403:** Your PAT is missing, expired, or lacks Contents read permission.
See `agent-integration/README.md` for troubleshooting.

---

## Step 3 — Filter by Task Type

Parse the manifest YAML and filter `categories.*.files` by `applies_to` values that match
your current task. Allowed values: `all`, `pipeline-development`, `code-review`, `architecture-review`.

Example (bash with `yq`):

```bash
# Fetch manifest and extract paths relevant to pipeline-development
MANIFEST=$(curl -s \
  -H "Accept: application/vnd.github.raw+json" \
  -H "Authorization: Bearer ${GITHUB_PAT}" \
  "https://api.github.com/repos/hayesgb/agent-architecture-context/contents/manifest.yaml")

echo "$MANIFEST" | yq '.categories[].files[] | select(.applies_to[] == "pipeline-development") | .path'
```

---

## Step 4 — Fetch a Specific File

Replace `<path>` with any `path` value from the manifest (e.g., `agent-guidelines/general.md`).

```bash
curl -s \
  -H "Accept: application/vnd.github.raw+json" \
  -H "Authorization: Bearer ${GITHUB_PAT}" \
  "https://api.github.com/repos/hayesgb/agent-architecture-context/contents/{path}"
```

**Concrete example:**

```bash
curl -s \
  -H "Accept: application/vnd.github.raw+json" \
  -H "Authorization: Bearer ${GITHUB_PAT}" \
  "https://api.github.com/repos/hayesgb/agent-architecture-context/contents/agent-guidelines/general.md"
```

---

## Full One-Shot Script

```bash
#!/usr/bin/env bash
# Fetch all guidelines relevant to a given task type and print them.
# Usage: ./fetch-guidelines.sh pipeline-development

set -euo pipefail

TASK_TYPE="${1:-all}"
REPO="hayesgb/agent-architecture-context"
API_BASE="https://api.github.com/repos/${REPO}/contents"

# --- Retrieve token from OS-native credential store ---
# macOS:
GITHUB_PAT=$(security find-generic-password -s "agent-architecture-context-pat" -a "$USER" -w)
# Linux (uncomment and comment out the macOS line above):
# GITHUB_PAT=$(secret-tool lookup service agent-architecture-context-pat username "$USER")

AUTH_HEADER="Authorization: Bearer ${GITHUB_PAT}"
ACCEPT_HEADER="Accept: application/vnd.github.raw+json"

# Fetch manifest
MANIFEST=$(curl -sf -H "${ACCEPT_HEADER}" -H "${AUTH_HEADER}" "${API_BASE}/manifest.yaml")

# Extract paths matching task type (requires yq or python3)
PATHS=$(echo "$MANIFEST" | python3 -c "
import sys, yaml
data = yaml.safe_load(sys.stdin)
task = '${TASK_TYPE}'
for cat in data.get('categories', []):
    for f in cat.get('files', []):
        if task in f.get('applies_to', []) or 'all' in f.get('applies_to', []):
            print(f['path'])
")

# Fetch and print each relevant file
for path in $PATHS; do
    echo "=== $path ==="
    curl -sf -H "${ACCEPT_HEADER}" -H "${AUTH_HEADER}" "${API_BASE}/${path}"
    echo
done
```

---

## Error Reference

| HTTP Status | Meaning | Action |
|---|---|---|
| 200 | Success | Parse the response body |
| 401 | PAT missing or expired | Regenerate PAT; see README |
| 403 | PAT lacks Contents permission | Re-scope PAT to Contents: Read-only |
| 404 | Path not found | Check the path value from manifest.yaml |
