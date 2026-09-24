# Modern Django Starter

[![PyPI version](https://img.shields.io/pypi/v/modern-django-starter)](https://pypi.org/project/modern-django-starter/)
[![Python](https://img.shields.io/pypi/pyversions/modern-django-starter)](https://pypi.org/project/modern-django-starter/)
[![CI](https://github.com/CasualEngineerZombie/modern-django-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/CasualEngineerZombie/modern-django-starter/actions/workflows/ci.yml)

A CLI tool that generates Django 6.1 projects with HTMX, AlpineJS, TailwindCSS, and more — with optional Docker, PostgreSQL, DRF, Celery, Sentry, Stripe, and cloud integrations.

## Installation

Requires Python 3.12+.

```bash
# uv (recommended)
uv tool install modern-django-starter

# pip
pip install modern-django-starter
```

## Usage

```bash
modern-django-starter create my_project
```

To create a project somewhere else:

```bash
modern-django-starter create my_project --output-dir /path/to/projects
```

Project names must be valid Python identifiers because they become the Django package name.

Without extra flags, the CLI asks for your choices interactively:

| Option | Choices |
|---|---|
| Docker | yes / no |
| PostgreSQL | 15, 16, 17, 18 |
| Cloud provider | none, AWS, Azure, GCP, Render, Railway, PythonAnywhere, Fly.io, Dokku, Heroku |
| Storage provider | local, AWS, GCP, Azure, Cloudflare R2 |
| Email provider | none, SendGrid, Mailgun, SES, Postmark |
| Async support | yes / no |
| Django REST Framework | yes / no |
| Celery | yes / no |
| Sentry | yes / no |
| Stripe | yes / no |
| Frontend pipeline | none, webpack, vite, parcel |
| CI tool | none, GitHub Actions, GitLab CI, Travis, CircleCI |

### API-only projects

Pass `--api-only` to skip the frontend and generate a pure DRF backend:

```bash
modern-django-starter create my_api --api-only
```

Includes:

- Django REST Framework
- JWT auth (djangorestframework-simplejwt)
- CORS (django-cors-headers)
- API schema and docs (drf-spectacular)
- Registration/auth endpoints (dj-rest-auth, django-allauth)

## Generated project

- Django 6.1
- HTMX and AlpineJS
- Django-allauth authentication
- TailwindCSS and DaisyUI styling
- Settings split into `base`, `development`, and `production`
- Optional: Docker, PostgreSQL, DRF, Celery, Sentry, Stripe, CI workflow, frontend pipeline

## Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Node.js and npm (only needed if you test frontend pipeline generation)

### Setup

```bash
git clone https://github.com/CasualEngineerZombie/modern-django-starter.git
cd modern-django-starter
uv sync
```

### Checks

Run the same checks as CI:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

CI runs lint, type checking, and tests on Python 3.12, 3.13, and 3.14.

## Contributing

Pull requests are welcome. Run the checks above before submitting.

## License

MIT — see the [LICENSE](LICENSE) file.