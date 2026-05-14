#!/usr/bin/env bash
# scripts/setup_branch_protection.sh
# Applies branch protection rules for DERMS as per BRANCHING_STRATEGY.md
# Requires: GitHub CLI (gh) authenticated with repo admin permissions
# Usage: bash scripts/setup_branch_protection.sh

set -euo pipefail

REPO="AUREX-ML/DERMS"

echo "=================================================="
echo " DERMS Branch Protection Setup"
echo " Repo: $REPO"
echo "=================================================="

# ── PROTECT: main ─────────────────────────────────────
echo ""
echo "→ Applying protection to: main"
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/${REPO}/branches/main/protection \
  --field required_status_checks='{"strict":true,"contexts":["lint-and-test","security-scan"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":false}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false \
  --field required_linear_history=false \
  --field block_creations=false

echo "  ✅ main: protected"
echo "     - No direct commits"
echo "     - 1 approving review required"
echo "     - CI must pass (lint-and-test, security-scan)"
echo "     - Enforced for admins"

# ── PROTECT: develop ──────────────────────────────────
echo ""
echo "→ Applying protection to: develop"
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/${REPO}/branches/develop/protection \
  --field required_status_checks='{"strict":true,"contexts":["lint-and-test"]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":false}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false \
  --field required_linear_history=false \
  --field block_creations=false

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
