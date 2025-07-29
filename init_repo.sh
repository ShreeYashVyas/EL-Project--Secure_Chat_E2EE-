#!/usr/bin/env bash
set -e
REPO_NAME="secure-chat-e2ee"
gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
echo "✅ Repo created: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)"
