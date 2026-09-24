# Configuration

Everything about a generated project is chosen at generation time through the
interactive prompts. The choices are baked into the generated settings, requirements,
and config files — no flags to memorize.

## Generation options

| Option | Choices | Default | Notes |
|---|---|---|---|
| **Docker** | yes / no | yes | Adds `Dockerfile`, `docker-compose.yml`, `entrypoint.sh`, `.dockerignore` |
| **PostgreSQL** | yes / no | yes | `no` falls back to SQLite |
| PostgreSQL version | 15, 16, 17, 18 | 18 | Applied to the compose file |
| **Cloud provider** | none, AWS, Azure, GCP, Render, Railway, PythonAnywhere, Fly.io, Dokku, Heroku | none | Adds deployment guidance in the generated README |
| **Storage provider** | local, AWS, GCP, Azure, Cloudflare R2 | local | Wires django-storages backends for media files |
| **Email provider** | none, SendGrid, Mailgun, SES, Postmark | none | See [Email providers](integrations.md#email) |
| **Async support** | yes / no | no | Generates `asgi.py` and sets `ASGI_APPLICATION` |
| **Django REST Framework** | yes / no | yes | Adds DRF + Token auth + CORS + API app |
| **Celery** | yes / no | full: yes · api-only: no | Adds Celery with a Redis broker (see [Celery](integrations.md#celery)) |
| **Sentry** | yes / no | full: yes · api-only: no | Error tracking + performance monitoring |
| **Stripe** | yes / no | no | Adds djstripe + a payments app |
| **Frontend pipeline** | none, webpack, vite, parcel | full: vite · api-only: none | Generates `package.json` (+ `vite.config.js` for Vite) |
| **CI tool** | none, GitHub Actions, GitLab CI, Travis, CircleCI | full: GitHub Actions · api-only: none | See [CI integration](integrations.md#ci) |

!!! tip "Full mode vs API-only"
    In **full mode** projects include the frontend (templates + static files) and default
    to Celery/Sentry/CI **on**. In **API-only mode** (`--api-only`) only a backend is
    generated; DRF is forced on, the frontend pipeline is forced off, and
    Celery/Sentry/CI default to **off**. See [API-Only Projects](api-only.md).

## Generated settings layout

Settings are split across three modules:

- `settings/base.py` — shared configuration
- `settings/development.py` — local development overrides
- `settings/production.py` — production overrides

!!! info "API-only projects"
    API-only projects keep the same three-module settings layout and reuse the same
    templates. The API-only branch of `settings/base.py` enables DRF with JWT auth,
    drf-spectacular schema docs, and dj-rest-auth; `settings/development.py` skips the
    frontend debug tooling (`django-debug-toolbar`, `django-extensions`) that has no
    use in a headless backend.

## Environment variables

Generated projects read configuration from environment variables via
[python-decouple](https://github.com/henriquebastos/python-decouple). Copy
`.env.example` to `.env` and edit the values you need.

### Core Django

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `django-insecure-change-me-in-production` | **Always override in production.** |
| `DEBUG` | `True` | Set to `False` in production. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowlist of hostnames. |
| `DEFAULT_FROM_EMAIL` | `noreply@<project>.com` | Sender address for outgoing mail. |

### Database (when PostgreSQL is enabled)

| Variable | Default |
|---|---|
| `DB_NAME` | `<project_name>` |
| `DB_USER` | `postgres` |
| `DB_PASSWORD` | *(empty)* |
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |

### Celery (when enabled)

| Variable | Default |
|---|---|
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` |

### DRF / CORS (when enabled)

| Variable | Default |
|---|---|
| `CORS_ALLOWED_ORIGINS` | *(empty)* — comma-separated origins |

### Sentry (when enabled)

| Variable | Default |
|---|---|
| `SENTRY_DSN` | *(empty)* |
| `ENVIRONMENT` | `development` |

### Stripe (when enabled)

| Variable | Default |
|---|---|
| `STRIPE_PUBLISHABLE_KEY` | *—* |
| `STRIPE_SECRET_KEY` | *—* |
| `DJSTRIPE_WEBHOOK_SECRET` | *—* |

### Storage providers

=== "AWS S3"

    | Variable | Default |
    |---|---|
    | `AWS_ACCESS_KEY_ID` | *—* |
    | `AWS_SECRET_ACCESS_KEY` | *—* |
    | `AWS_STORAGE_BUCKET_NAME` | *—* |
    | `AWS_S3_REGION_NAME` | `us-east-1` |
    | `AWS_S3_CUSTOM_DOMAIN` | *(empty)* |
    | `MEDIA_URL` | `https://<domain>/media/` |

=== "Cloudflare R2"

    | Variable | Default |
    |---|---|
    | `AWS_ACCESS_KEY_ID` | *R2 access key* |
    | `AWS_SECRET_ACCESS_KEY` | *R2 secret key* |
    | `AWS_STORAGE_BUCKET_NAME` | *R2 bucket* |
    | `AWS_S3_ENDPOINT_URL` | *e.g. `https://<account-id>.r2.cloudflarestorage.com`* |
    | `AWS_S3_REGION_NAME` | `auto` |

=== "Google Cloud Storage"

    | Variable | Default |
    |---|---|
    | `GCS_BUCKET_NAME` | *—* |
    | `GOOGLE_APPLICATION_CREDENTIALS` | *path to service-account JSON* |

=== "Azure Blob Storage"

    | Variable | Default |
    |---|---|
    | `AZURE_ACCOUNT_NAME` | *—* |
    | `AZURE_ACCOUNT_KEY` | *—* |
    | `AZURE_CONTAINER` | *—* |

### Email providers

| Variable | Used by |
|---|---|
| `SENDGRID_API_KEY` | SendGrid |
| `MAILGUN_USERNAME` / `MAILGUN_PASSWORD` | Mailgun |

## Non-interactive generation

The CLI is intentionally interactive — the only flag-driven choices are `--output-dir`
and `--api-only`. To script generation non-interactively, pipe answers into the prompt,
for example:

```bash
printf 'my_project\ny\ny\n18\nnone\nlocal\nnone\nn\ny\ny\ny\nn\nvite\ngithub-actions\ny\n' \
  | modern-django-starter create
```

!!! warning
    Prompt order is stable but not part of the public API — it may change between
    releases. Prefer the interactive flow for anything important.