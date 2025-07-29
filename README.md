# EL-Project--Secure_Chat_E2EE-
#!/usr/bin/env bash
set -euo pipefail

# === Configuration ===
REPO_NAME="secure-chat-e2ee"
REPO_DESC="Python E2EE Chat • RSA-OAEP & AES-256-GCM"
LICENSE="mit"         # Options: mit, apache, gpl-3.0, etc.
GITHUB_VISIBILITY="public"

# === 1. Initialize local Git and commit ===
git init
git add .
git commit -m "chore: initial import of secure-chat E2EE project"

# === 2. Authenticate via GitHub CLI ===
#   (Prompts if not already logged in)
gh auth status 2>/dev/null || gh auth login --hostname github.com --git-protocol https

# === 3. Create remote repo and push ===
gh repo create "$REPO_NAME" \
  --description "$REPO_DESC" \
  --"$GITHUB_VISIBILITY" \
  --source=. \
  --remote=origin \
  --push

# === 4. Add license via gh CLI ===
gh repo edit "$REPO_NAME" --add-license $LICENSE

echo "✅ Repository '$REPO_NAME' created and initial commit pushed."
echo "You can now view it at: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)"
