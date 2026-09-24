# Contributing

Thanks for considering contributing to Modern Django Starter! This page covers setting
up a development environment, running the checks, and maintaining the docs.

## Prerequisites

- **Python 3.12+**
- [uv](https://docs.astral.sh/uv/)
- Node.js and npm — only needed if you test frontend pipeline generation

## Setup

```bash
git clone https://github.com/CasualEngineerZombie/modern-django-starter.git
cd modern-django-starter
uv sync
```

Run the CLI in development mode:

```bash
uv run modern-django-starter create demo_project --output-dir /tmp/demo
```

or invoke the tests:

```bash
uv run pytest
```

## Running the checks

CI runs linting, formatting, type checking, and tests on Python 3.12, 3.13, and 3.14.
Run the same checks locally:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

## Integration tests

`tests/test_generated_projects_e2e.py` contains an end-to-end *matrix* that generates a
representative project for each major configuration combination, installs its
dependencies into a temporary virtual environment, runs `manage.py check`,
runs migrations, and executes the generated project's own test suite.
Docker-enabled configurations are also validated with `docker compose config`
(when Docker is available).

These tests download and install packages, so they are skipped unless you opt in:

```bash
RUN_DJANGO_INTEGRATION_TESTS=1 uv run pytest -q \
  tests/test_api_only_integration.py \
  tests/test_storage_dependencies.py \
  tests/test_stripe_webhook_secret.py \
  tests/test_generated_projects_e2e.py \
  tests/test_aws_s3_integration.py
```

The matrix lives at the top of `test_generated_projects_e2e.py`:

- `MATRIX` — runnable configurations (SQLite) that must pass check, migrate,
  and the generated test suite.
- `CHECK_ONLY_MATRIX` — feature-maximal PostgreSQL configurations that must
  install and pass `manage.py check`, but cannot migrate without a live
  database; their Docker setups are covered by the Compose validation.
- `POSTGRES_ENTRY` — a PostgreSQL configuration that `PostgresProjectIntegrationTests`
  boots against a real database: it starts the generated project's own `db`
  service with `docker compose up -d db`, then runs migrate and the generated
  test suite against it (requires Docker).
- `DockerComposeStackIntegrationTests` — a full-stack boot (issue
  [#16](https://github.com/CasualEngineerZombie/modern-django-starter/issues/16)): it
  runs `docker compose up -d --build web` on a docker+PostgreSQL configuration,
  waits for the `web` healthcheck to report `healthy`, and asserts the
  entrypoint applied migrations and static files. This proves a fresh
  `docker compose up` produces a bootable, initialized project.

When you add a configuration option to the generator, add (or extend) a matrix
entry here so the new combination is proven to boot, not just render.

### AWS S3 round trip (kumo emulator)

`tests/test_aws_s3_integration.py` generates an AWS-storage project and runs a
real django-storages round trip (save → open → delete) against
[kumo](https://github.com/sivchari/kumo), an AWS emulator with an S3-compatible
API. The generated project is pointed at the emulator via its
`AWS_S3_ENDPOINT_URL` setting, so the exact storage code path production uses
is exercised. To run it against the compose kumo:

```bash
docker compose -f docker-compose.act.yml up -d kumo
RUN_DJANGO_INTEGRATION_TESTS=1 AWS_S3_ENDPOINT_URL=http://localhost:4566 \
  AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
  uv run pytest -q tests/test_aws_s3_integration.py
```

Without `AWS_S3_ENDPOINT_URL` the test skips, so unit runs stay hermetic.

### Run CI locally with act

`ci-local.sh` runs the CI workflow locally with
[act](https://nektosact.com) (install: `winget install nektos.act`), so there
is no wait for GitHub Actions results on every push:

```bash
./ci-local.sh                  # every ci.yml job
./ci-local.sh -j integration   # just the kumo-backed integration job
```

The integration tests reach the compose kumo on `localhost:4566` (act runs job
containers on the host network, and `ci-local.sh` starts the emulator first);
GitHub-hosted runners use the workflow's own kumo service container instead.
`.act.env` is machine-local (gitignored) — tracked defaults live in
`.act.env.example`. One caveat: `DockerComposeStackIntegrationTests` is
skipped under act (`ACT=true`), because its `./staticfiles` bind mount points
at a path inside the job container that the outer Docker daemon cannot see.

## Project layout

```text
modern_django_starter/
├── cli.py          # Click CLI + interactive prompts
├── generator.py    # ProjectGenerator — writes all project files
└── templates/      # Jinja2 templates used to render generated files
    ├── settings/
    ├── templates/
    ├── static/
    ├── requirements/
    ├── .github/workflows/
    └── *.j2
```

- `cli.py` collects choices and prints the summary table.
- `generator.py` renders templates and writes the project tree.
- The `templates/` directory mirrors the layout of a generated project. Each `.j2`
  file is a Jinja2 template rendered with `project_name` and `config`.

When you change generated output, make sure the existing tests still pass and add a
test for new behavior. The existing suite lives in [`tests/`](https://github.com/CasualEngineerZombie/modern-django-starter/tree/main/tests).

## Keeping the docs in sync

The documentation site sources live in `docs/`. When you change generated output or
the CLI, update the relevant page:

- New/renamed options → [`configuration.md`](configuration.md) and [`cli-reference.md`](cli-reference.md)
- New generated files → [`generated-project.md`](generated-project.md)
- New integrations → [`integrations.md`](integrations.md)

### Preview docs locally

```bash
uv sync --group docs
uv run mkdocs serve        # http://127.0.0.1:8000
uv run mkdocs build --strict
```

The build must pass in strict mode, since CI deploys with `--strict`.

!!! tip "Docs deployment"
    Pushing to `main` automatically rebuilds and deploys the site to
    <https://mds.rianbarriga.com> via `.github/workflows/docs.yml`.

## Submitting changes

1. Fork the repository and create a feature branch
   (`git checkout -b feature/your-feature`).
2. Make your changes.
3. Run all checks above.
4. Update or add tests and docs as needed.
5. Push and open a pull request against `main`.

## Releases

### Versioning policy (SemVer)

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **Patch** (`0.3.x`, `1.0.x`) — bug fixes and backward-compatible corrections only.
  Bug fixes ship in patches; features never ship in patches.
- **Minor** (`0.x.0`, `1.x.0`) — new features, new configuration options, or new
  integrations that stay backward compatible.
- **Major** (`1.0.0`, `2.0.0`) — breaking API changes. **1.0.0** freezes and
  stabilizes the public API (CLI flags, generated project layout, template names);
  nothing that consumers rely on changes without a major bump.

The roadmap milestones (currently `v0.3.x` patches through `1.0.0`) are tracked in
Linear; each patch milestone maps to one bug-fix+regression-test GitHub issue and
one single-commit PR.

### Cutting a patch release

Before you start, the **Integration gate** must pass: run the full E2E matrix
([integration tests](#integration-tests)) with `RUN_DJANGO_INTEGRATION_TESTS=1`
and confirm it is green, since that is the only suite that proves a generated
project *boots*, not just renders.

1. **Merge** the patch PRs to `main` and confirm CI is green (Lint, Type check,
   Test × 3, Integration, Package).
2. **Bump the version in two places** — `__version__` in
   `modern_django_starter/__init__.py` and `version` in `pyproject.toml` — and let
   `tests/test_metadata.py` prove they match.
3. **Update `CHANGELOG.md`** — move the patch entry out of its "Unreleased"
   section into a dated `## [0.3.x] - YYYY-MM-DD` section, and update the version
   links at the bottom.
4. **Tag and push:**

   ```bash
   git tag v0.3.x
   git push origin v0.3.x
   ```

   Pushing the tag triggers `publish.yml` (PyPI release); pushing `main` already
   redeployed the docs via `docs.yml`.
5. **Update the roadmap in Linear** — flip the milestone's issues to Done.

## License

MIT — see the [LICENSE](https://github.com/CasualEngineerZombie/modern-django-starter/blob/main/LICENSE) file.