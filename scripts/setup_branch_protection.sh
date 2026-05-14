#!/usr/bin/env bash
# scripts/setup_branch_protection.sh
# Applies branch protection rules for DERMS as per BRANCHING_STRATEGY.md
# Requires: GitHub CLI (gh) authenticated with repo admin permissions
# Usage: bash scripts/setup_branch_protection.sh

set -euo pipefail

REPO="${REPO:-}"
if [ -z "$REPO" ]; then
  REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)"
fi

if [ -z "$REPO" ]; then
  echo "Error: Unable to determine repository slug." >&2
  echo "Set REPO=<owner/name> or run this script from within a GitHub repository that 'gh repo view' can resolve." >&2
  exit 1
fi

echo "=================================================="
echo " DERMS Branch Protection Setup"
echo " Repo: $REPO"
echo "=================================================="

# ── PROTECT: main ─────────────────────────────────────
echo ""
echo "→ Applying protection to: main"
echo '{
  "required_status_checks": {
    "strict": true,
    "contexts": ["lint-and-test", "security-scan"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": false,
  "block_creations": false
}' | gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/${REPO}/branches/main/protection \
  --input -

echo "  ✅ main: protected"
echo "     - No direct commits"
echo "     - 1 approving review required"
echo "     - CI must pass (lint-and-test, security-scan)"
echo "     - Enforced for admins"

# ── PROTECT: develop ──────────────────────────────────
echo ""
echo "→ Applying protection to: develop"
echo '{
  "required_status_checks": {
    "strict": true,
    "contexts": ["lint-and-test"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": false,
  "block_creations": false
}' | gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/${REPO}/branches/develop/protection \
  --input -

echo "  ✅ develop: protected"
echo "     - No direct commits from contributors"
echo "     - 1 approving review required"
echo "     - CI must pass (lint-and-test)"

echo ""
echo "=================================================="
echo " Branch protection setup complete!"
echo "=================================================="
echo ""
echo "Verify at: https://github.com/${REPO}/settings/branches"
