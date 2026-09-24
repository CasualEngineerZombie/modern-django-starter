# CLI Reference

## Global options

Installing the package provides the `modern-django-starter` command.

| Option | Description |
|---|---|
| `--version` | Show the installed version and exit |
| `--help` | Show command help and exit |

```bash
modern-django-starter --version
modern-django-starter --help
```

## `modern-django-starter create`

Creates a new Django project.

```text
Usage: modern-django-starter create [OPTIONS] [PROJECT_NAME]
```

### Arguments

| Argument | Description |
|---|---|
| `PROJECT_NAME` | *(optional)* Name of the project. Must be a valid Python identifier (`snake_case`, cannot start with a digit). If omitted, you are prompted for it with a default of `my_django_project`. |

### Options

| Option | Description |
|---|---|
| `-o, --output-dir PATH` | Directory to create the project in. Defaults to `.` (current directory). |
| `--api-only` | Generate an API-only project: a pure DRF backend with JWT auth, CORS, and drf-spectacular docs. No frontend or HTML templates are generated. See [API-Only Projects](api-only.md). |

```bash
# Create in the current directory
modern-django-starter create blog

# Create somewhere specific
modern-django-starter create blog --output-dir ~/code

# Short flag form
modern-django-starter create blog -o /tmp/projects

# API-only backend
modern-django-starter create blog_api --api-only
```

### Interactive prompts

Everything else is selected through interactive prompts. The set of questions
depends on whether `--api-only` was passed:

| Question | Full mode choices | Default | API-only default |
|---|---|---|---|
| Docker support | yes / no | yes | yes |
| PostgreSQL | yes / no | yes | yes |
| PostgreSQL version | 15, 16, 17, 18 | 18 | 18 |
| Cloud provider | none, AWS, Azure, GCP, Render, Railway, PythonAnywhere, Fly.io, Dokku, Heroku | none | none |
| Storage provider | local, AWS, GCP, Azure, Cloudflare R2 | local | local |
| Email provider | none, SendGrid, Mailgun, SES, Postmark | none | none |
| Async support | yes / no | no | no |
| Django REST Framework | yes / no | yes | **always enabled** |
| Celery | yes / no | yes | no |
| Sentry | yes / no | yes | no |
| Stripe | yes / no | no | no |
| Frontend pipeline | none, webpack, vite, parcel | vite | **always none** |
| CI tool | none, GitHub Actions, GitLab CI, Travis, CircleCI | GitHub Actions | none |

!!! note "About defaults"
    In full mode Celery, Sentry, and CI default to **yes**; in API-only mode they
    default to **no** to keep the backend minimal. DRF and the frontend pipeline are
    fixed in API-only mode (`DRF = yes`, `pipeline = none`).

### Confirmation summary

Before anything is written, the CLI prints a summary table of every selected option
and asks for confirmation:

```text
Generate project 'my_project'? [y/n] (y):
```

Answering **no** cancels the run (exit code 0) without writing any files.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Success, or generation explicitly cancelled |
| `1` | Invalid project name, or an error occurred during generation |