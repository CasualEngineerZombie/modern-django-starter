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
  tests/test_generated_projects_e2e.py
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

When you add a configuration option to the generator, add (or extend) a matrix
entry here so the new combination is proven to boot, not just render.

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

## License

MIT — see the [LICENSE](https://github.com/CasualEngineerZombie/modern-django-starter/blob/main/LICENSE) file.