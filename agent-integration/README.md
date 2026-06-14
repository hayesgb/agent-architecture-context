# Agent Integration Guide

This directory contains everything a team member needs to wire any AI coding agent
(Gemini, Claude, Copilot, or any HTTP-capable agent) into the
`agent-architecture-context` repository so the agent can retrieve relevant guidelines
before generating code.

---

## Contents

| Path | Description |
|---|---|
| `skill-spec.yaml` | Platform-agnostic contract: auth method, endpoints, output format |
| `agent-integration/templates/generic-http-template.md` | Copy-paste `curl` commands and a full shell script |

---

## 1 — Generate a Fine-Grained GitHub PAT

A **fine-grained Personal Access Token** scoped read-only to this repository is required.
Each team member creates their own; tokens are never shared.

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens**.
2. Click **Generate new token**.
3. Set **Resource owner** to `hayesgb` (or the org that owns this repo).
4. Under **Repository access**, choose **Only select repositories** and select
   `agent-architecture-context`.
5. Under **Permissions → Repository permissions**, set **Contents** to **Read-only**.
   No other permissions are needed.
6. Set an expiration (90 days recommended; calendar a renewal reminder).
7. Click **Generate token** and copy it — you will not see it again.

---

## 2 — Store the Token Securely

Store the token in your OS-native credential store. **Do not** write it to a file,
environment variable, `.env`, or shell profile.

### macOS — Keychain

```bash
security add-generic-password \
  -s "agent-architecture-context-pat" \
  -a "$USER" \
  -w "<paste-your-token-here>"
```

Retrieve at runtime:

```bash
GITHUB_PAT=$(security find-generic-password -s "agent-architecture-context-pat" -a "$USER" -w)
```

### Linux — libsecret / secret-tool

```bash
secret-tool store \
  --label="Agent Architecture Context PAT" \
  service agent-architecture-context-pat \
  username "$USER"
# You will be prompted to enter the token value
```

Retrieve at runtime:

```bash
GITHUB_PAT=$(secret-tool lookup service agent-architecture-context-pat username "$USER")
```

### Windows — Credential Manager

```powershell
# Store
cmdkey /generic:"agent-architecture-context-pat" /user:"github-pat" /pass:"<paste-your-token-here>"

# Retrieve (PowerShell, requires CredentialManager module)
$cred = Get-StoredCredential -Target "agent-architecture-context-pat"
$GITHUB_PAT = $cred.GetNetworkCredential().Password
```

### Cross-Platform — Python `keyring` library

```python
import keyring

# Store (run once)
keyring.set_password("agent-architecture-context-pat", "github-pat", "<paste-your-token-here>")

# Retrieve at runtime
GITHUB_PAT = keyring.get_password("agent-architecture-context-pat", "github-pat")
```

---

## 3 — Select and Adapt a Template

| Template | Best for |
|---|---|
| [`agent-integration/templates/generic-http-template.md`](agent-integration/templates/generic-http-template.md) | Any agent that can execute shell commands or make HTTP requests; a good starting point for all platforms |

Open the template and follow its instructions. Key adaptation points:

- Replace the credential-store retrieval block with whichever OS variant matches your
  environment (macOS / Linux / Windows — all three are shown in the template).
- Wire the fetched content into your agent's context window before code generation.
- For platform-specific integrations (Gemini extensions, MCP servers, Copilot plugins),
  use the `curl` examples as the reference HTTP pattern and re-implement in your
  platform's native language/config.

The authoritative contract for all endpoint URLs, headers, and auth requirements is
[`skill-spec.yaml`](skill-spec.yaml).

---

## 4 — Verify Your Setup

Confirm your PAT and network access are working by fetching `manifest.yaml`:

### macOS / Linux

```bash
# Retrieve token
GITHUB_PAT=$(security find-generic-password -s "agent-architecture-context-pat" -a "$USER" -w)
# Linux: GITHUB_PAT=$(secret-tool lookup service agent-architecture-context-pat username "$USER")

# Fetch manifest
curl -s \
  -H "Accept: application/vnd.github.raw+json" \
  -H "Authorization: Bearer ${GITHUB_PAT}" \
  "https://api.github.com/repos/hayesgb/agent-architecture-context/contents/manifest.yaml"
```

**A successful response** returns the raw YAML content of `manifest.yaml` with HTTP 200.

### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| HTTP 401 | PAT expired or not found in credential store | Regenerate PAT; re-run the `security add-generic-password` / `secret-tool store` command |
| HTTP 403 | PAT lacks Contents read permission | Re-create token with Contents: Read-only permission |
| HTTP 404 | Wrong repo path or repo not found | Verify the URL includes `hayesgb/agent-architecture-context` |
| Empty output | `security find-generic-password` returned nothing | Confirm you stored the token under the correct service name `agent-architecture-context-pat` |

---

## Running the Validation Test Suite

From the repo root:

```bash
pip install -r requirements.txt
pytest
```

All tests must pass before committing changes to `manifest.yaml` or any content file.
