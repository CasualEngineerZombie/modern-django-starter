#!/usr/bin/env bash
# Run the CI workflow locally with act, so there is no wait for GitHub Actions
# results on every push. Requires Docker Desktop and act:
#   winget install nektos.act   (or: choco install act-cli / scoop install act)
#
# Usage:
#   ./ci-local.sh                    run every ci.yml job (lint, test, integration, ...)
#   ./ci-local.sh -j integration     run only the kumo-backed integration job
#   ./ci-local.sh --list             list the jobs in the workflow
#
# Any extra arguments are passed through to act. act runs job containers on
# the host network, so the integration tests reach the compose kumo on
# localhost:4566 — this script starts that emulator first (the workflow's own
# kumo service container is what GitHub-hosted runners use).
#
# To run the AWS round-trip test directly on the host instead of through act:
#   docker compose -f docker-compose.act.yml up -d kumo
#   RUN_DJANGO_INTEGRATION_TESTS=1 AWS_S3_ENDPOINT_URL=http://localhost:4566 \
#       uv run pytest -q tests/test_aws_s3_integration.py
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v act >/dev/null 2>&1; then
  echo "act is not installed. Install it with: winget install nektos.act" >&2
  exit 1
fi

# act job containers hit localhost:4566 (.act.env), which is the compose kumo.
docker compose -f docker-compose.act.yml up -d --wait kumo

# .act.env is machine-local (gitignored); fall back to the tracked defaults.
ENV_FILE=.act.env
if [ ! -f "$ENV_FILE" ]; then
  ENV_FILE=.act.env.example
fi

exec act push \
  -W .github/workflows/ci.yml \
  --env-file "$ENV_FILE" \
  "$@"
