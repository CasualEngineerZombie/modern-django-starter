# Integrations

Every integration is optional and toggled at generation time. This page describes what
each one adds to the generated project.

## Docker

When enabled, the project includes:

- `Dockerfile` — multi-stage Python image
- `docker-compose.yml` — web service plus any required services (PostgreSQL, Redis)
- `.dockerignore`

```bash
cp .env.example .env
docker compose up -d
docker compose exec web python manage.py migrate
```

## PostgreSQL

When enabled, the project targets **PostgreSQL** (versions 15–18, default 18) and the
settings read `DB_*` environment variables. The docker-compose file includes a matching
`postgres` service. Answer **no** to fall back to the default SQLite database.

Versions selectable: **15, 16, 17, 18**.

## Django REST Framework

When enabled, the generated project includes:

- `djangorestframework` with **Session** and **Token** authentication
- `django-cors-headers` with configurable `CORS_ALLOWED_ORIGINS`
- An `apps/api` app with a `/api/health/` endpoint
- Page-number pagination (`page_size = 20`) and `IsAuthenticated` as the default
  permission class

The Django admin, allauth, and the API health check all work out of the box.

## Celery

When enabled, the project includes:

- `celery` with a **Redis** broker (`CELERY_BROKER_URL`, defaults to
  `redis://localhost:6379`) and result backend (`CELERY_RESULT_BACKEND`)

```bash
celery -A my_project worker -l info
celery -A my_project beat -l info
```

!!! note "Django 6.1 compatibility"
    `django-celery-beat` (the admin UI and database scheduler) is not emitted
    because its latest release caps at `Django<6.1` and cannot be installed
    next to the generated `Django==6.1.1`. Re-add it once upstream supports
    Django 6.x.

## Sentry

When enabled, `sentry_sdk` is initialized with the Django integration (+ the Celery
integration if Celery is enabled), reading `SENTRY_DSN` and `ENVIRONMENT` from the
environment. `traces_sample_rate` is set to `1.0` and `send_default_pii` is on.

## Stripe

If Stripe is enabled, a full **payments** app is generated using `dj-stripe`:

- `Order` / `OrderItem` models with a `checkout.session.completed` flow
- Checkout sessions created server-side with `stripe.checkout.Session.create`
- A CSRF-exempt **webhook endpoint** at `/payments/webhook/`
- Automatic Stripe `Customer` creation via a `post_save` signal on user creation
- Admin views for orders and order items

| Route | Purpose |
|---|---|
| `/payments/checkout/` | POST creates a checkout session; GET shows the checkout page |
| `/payments/success/` | Post-payment success page |
| `/payments/cancel/` | Post-payment cancellation page |
| `/payments/orders/` | The current user's orders |
| `/payments/webhook/` | Stripe webhook endpoint |

Required env vars: `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, and
`DJSTRIPE_WEBHOOK_SECRET` (the single webhook secret used by both dj-stripe and
the generated webhook view).

!!! tip "Testing"
    Use Stripe's test cards — `4242 4242 4242 4242` for a successful payment,
    `4000 0000 0000 0002` for a declined card. Configure webhook events such as
    `checkout.session.completed` pointing at `https://yourapp/payments/webhook/`.

## Cloud storage

Choosing a storage provider wires **django-storages** into the `STORAGES` default backend
for media files. Static files remain on the local filesystem. The matching
`django-storages` and provider SDK packages are pinned in the generated
`requirements/base.txt`, which both `development.txt` and `production.txt`
include, so every environment has exactly the packages the selected backend
needs.

| Provider | Backend |
|---|---|
| local (default) | `FileSystemStorage` |
| AWS | `storages.backends.s3.S3Storage` |
| Cloudflare R2 | `storages.backends.s3.S3Storage` (S3-compatible) |
| Google Cloud | `storages.backends.gcloud.GoogleCloudStorage` |
| Azure | `storages.backends.azure_storage.AzureStorage` |

The required credentials come from environment variables — see
[Storage providers](configuration.md#storage-providers).

## Email

The generated settings use the Django 6.1 **MAILERS** configuration.

| Provider | Behavior |
|---|---|
| none (default) | Console email backend (prints to terminal) |
| SendGrid | SMTP via `smtp.sendgrid.net` using `SENDGRID_API_KEY` |
| Mailgun | SMTP via `smtp.mailgun.org` using `MAILGUN_USERNAME` / `MAILGUN_PASSWORD` |
| SES / Postmark | Selectable in the CLI; currently generated settings fall back to the console backend |

!!! note
    SES and Postmark are valid prompt choices, but the generated settings only wire
    wiring for SendGrid and Mailgun at the moment. Picking SES or Postmark still builds
    a working project — mail is just delivered to the console until you add the backend.

## Frontend pipelines

Choosing a frontend pipeline generates a `package.json` with ready npm scripts. Vite
additionally gets a `vite.config.js` (with the legacy plugin).

| Pipeline | Dev command | Build command |
|---|---|---|
| none | — | — |
| vite | `npm run dev` | `npm run build` |
| webpack | `npm run dev` (webpack serve) | `npm run build` |
| parcel | `npm run dev` (parcel serve) | `npm run build` |

## CI

Selecting a CI tool generates CI configuration for the generated project.

| Tool | Result |
|---|---|
| none (default for API-only) | Nothing generated |
| GitHub Actions | `.github/workflows/ci.yml` — lint (flake8, black, isort), tests with pytest + coverage→Codecov, frontend build when a pipeline is used, and a Docker build/check job when Docker is enabled. Spins up PostgreSQL (`postgres:{version}`) and Redis (`redis:7-alpine`) as service containers when applicable |
| GitLab CI / Travis / CircleCI | Selectable today; no workflow file is generated yet |

!!! note
    Only GitHub Actions currently emits a workflow file. The other options are reserved
    for future releases.