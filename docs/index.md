# Modern Django Starter

A CLI tool that scaffolds **Django 6.1** projects with modern tooling pre-wired and production-ready
— HTMX, AlpineJS, TailwindCSS & DaisyUI, docker-allauth authentication, Docker, PostgreSQL,
Django REST Framework, Celery, Sentry, Stripe, and cloud integrations.

[![PyPI version](https://img.shields.io/pypi/v/modern-django-starter)](https://pypi.org/project/modern-django-starter/)
[![Python](https://img.shields.io/pypi/pyversions/modern-django-starter)](https://pypi.org/project/modern-django-starter/)
[![CI](https://github.com/CasualEngineerZombie/modern-django-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/CasualEngineerZombie/modern-django-starter/actions/workflows/ci.yml)

<div class="grid cards" markdown>

-   :material-rocket-launch: __One command, one project__

    Generate a complete, working Django project in seconds — no boilerplate copying.

-   :material-heart: __Modern frontend, zero build pain__

    HTMX and AlpineJS included. Optionally wire up Vite, webpack, or Parcel.

-   :material-database: __Pick your stack__

    PostgreSQL, DRF, Celery, Sentry, Stripe, cloud storage, email providers — all optional.

-   :material-docker: __Docker-friendly__

    Get a production-grade `Dockerfile` and `docker-compose.yml` out of the box.

-   :material-api: __API-first mode__

    Generate a pure DRF backend with JWT auth, CORS, and Swagger docs via `--api-only`.

-   :material-source-branch: __CI included__

    Optionally scaffold GitHub Actions (or GitLab, Travis, CircleCI) workflows.

</div>

## Quick start

Requires **Python 3.12+**.

```bash
# uv (recommended)
uv tool install modern-django-starter

# or pip
pip install modern-django-starter
```

Then generate a project:

```bash
modern-django-starter create my_project
```

You'll be guided through a few questions (Docker, PostgreSQL, DRF, Celery, Stripe, and more).
When you're done, you have a working Django app:

```bash
cd my_project
docker compose up -d                  # with Docker
docker compose exec web python manage.py migrate
```

or without Docker:

```bash
python -m venv venv
source venv/bin/activate              # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open <http://localhost:8000> and you're up and running.

!!! tip "API-only?"
    Prefer a headless backend? See [API-Only Projects](api-only.md) for the `--api-only` mode.

## What you get

<div class="grid cards" markdown>

-   **Django 6.1** — split settings (`base`, `development`, `production`)
-   **HTMX + AlpineJS** — interactive pages without a JS framework
-   **TailwindCSS + DaisyUI** — utility-first styling with ready components
-   **django-allauth** — email-based signup/login wired to the templates
-   **Optional** — Docker, PostgreSQL, DRF, Celery, Sentry, Stripe, cloud storage,
    email providers, frontend build pipeline, and CI workflows

</div>

## Installing the generated project requirements

Each generated project ships a `requirements/` directory split into
`base.txt`, `development.txt`, and `production.txt`. `requirements.txt`
pulls in the development set by default:

```bash
pip install -r requirements.txt
```

## Next steps

-   [Getting Started](getting-started.md) — install and create your first project
-   [CLI Reference](cli-reference.md) — every command and option
-   [Configuration](configuration.md) — all configurable options and environment variables
-   [Generated Project](generated-project.md) — what the generated code looks like
-   [API-Only Projects](api-only.md) — headless DRF backends
-   [Integrations](integrations.md) — Docker, storage, email, CI, and more
-   [Deployment](deployment.md) — pushing your project to production
-   [Contributing](contributing.md) — building this tool itself