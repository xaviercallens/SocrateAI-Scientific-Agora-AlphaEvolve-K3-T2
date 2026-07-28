#!/usr/bin/env bash
set -e

echo "=== T0 DIRECTIVE: PARALLEL GCP-ALPHA-ANTIGRAVITY ENVIRONMENT INITIALIZATION ==="

# 1. Initialize git repo if not existing
if [ ! -d ".git" ]; then
  git init
  echo "Initialized git repository."
fi

# 2. Create and switch to the new parallel testing branch across all repos
git checkout -b feature/gcp-alpha-antigravity || git checkout feature/gcp-alpha-antigravity

# 3. Create parallel architecture directories
mkdir -p gcp_infrastructure/agent_kit
mkdir -p pipeline/antigravity_compute
mkdir -p pipeline/alphaevolve_search
mkdir -p core
mkdir -p scripts

# 4. Stage and commit baseline infrastructure
git add .
git commit -m "feat(architecture): scaffold GCP Agent Kit, Antigravity, and AlphaEvolve integration" || true

echo "=== Environment successfully initialized on branch feature/gcp-alpha-antigravity ==="
