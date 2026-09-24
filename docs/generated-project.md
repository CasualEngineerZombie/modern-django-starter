# Generated Project

A typical full-mode project (Docker, PostgreSQL, DRF, Celery, Sentry, Stripe, Vite,
GitHub Actions) looks like this:

```text
my_project/
├── manage.py                       # Django management entry point
├── my_project/                     # Project package
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                 # Shared settings
│   │   ├── development.py          # Development overrides
│   │   └── production.py           # Production overrides
│   ├── urls.py                     # Root URL configuration
│   ├── wsgi.py                     # WSGI application
│   └── asgi.py                     # ASGI application (only with async support)
├── apps/
│   ├── core/                       # Home page + HTMX demo
│   ├── accounts/                   # User accounts
│   ├── api/                        # DRF API app (with DRF)
│   └── payments/                   # Stripe orders & checkout (with Stripe)
├── templates/
│   ├── base.html                   # Base layout (Tailwind + DaisyUI)
│   ├── home.html                   # Landing page with HTMX demo
│   └── account/
│       ├── login.html
│       ├── signup.html
│       └── logout.html
│   └── payments/                   # (with Stripe)
│       ├── checkout.html
│       ├── success.html
│       ├── cancel.html
│       └── orders.html
├── static/
│   ├── css/main.css
│   ├── js/main.js
│   └── img/
├── requirements/
│   ├── base.txt                    # Runtime dependencies
│   ├── development.txt             # Development extras
│   └── production.txt              # Production extras
├── .env.example                    # Environment template
├── .gitignore
├── README.md                       # Project-specific quick start
├── Dockerfile                      # (with Docker)
├── docker-compose.yml              # (with Docker)
├── .dockerignore                   # (with Docker)
├── .github/workflows/ci.yml        # (with CI = GitHub Actions)
├── package.json                    # (with a frontend pipeline)
└── vite.config.js                  # (with frontend pipeline = Vite)
```

## Apps

| App | Purpose | Key routes |
|---|---|---|
| `apps.core` | Landing page and HTMX demo | `/` (home), `/time/` (HTMX time endpoint) |
| `apps.accounts` | User accounts (allauth) | `/accounts/login/`, `/accounts/signup/`, `/accounts/logout/` |
| `apps.api` | DRF API (when DRF enabled) | `/api/health/` health check |
| `apps.payments` | Stripe checkout & orders (when Stripe enabled) | see [Stripe](integrations.md#stripe) |

## What's pre-wired

- **django-allauth** with email-only signup: `ACCOUNT_LOGIN_METHODS = {'email'}`,
  `ACCOUNT_EMAIL_VERIFICATION = 'mandatory'`
- **DRF** with Session + Token authentication, `IsAuthenticated` by default,
  page-based pagination (`page_size = 20`), and CORS support
- **Celery** with a Redis broker and result backend
- **Sentry** initialized with the Django (and Celery, if enabled) integrations
- **dj-stripe** with an `Order`/`OrderItem` model, checkout sessions, and webhooks
- **django-storages** backends when a cloud storage provider is selected
- **TailwindCSS + DaisyUI** stylesheet and a `main.js` wiring HTMX + Alpine + HyperScript

## Default endpoints

| Path | Description |
|---|---|
| `/` | Home page |
| `/time/` | HTMX demo endpoint returning the current time as JSON |
| `/admin/` | Django admin |
| `/accounts/login/`, `/accounts/signup/`, `/accounts/logout/` | Allauth pages |
| `/api/health/` | DRF health check (`{"status": "healthy"}`) |
| `/payments/checkout/` | Stripe checkout session (with Stripe) |
| `/payments/webhook/` | Stripe webhook endpoint (with Stripe) |

## Settings highlights

- `DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS` separation keeps `INSTALLED_APPS` tidy
- Environment-driven configuration through python-decouple
- `ALLOWED_HOSTS` read from the `ALLOWED_HOSTS` env var (comma-separated)
- Static files served from `/static/`, uploads from `/media/`
- MAILERS-style email configuration (Django 6.1): console by default, SMTP for
  SendGrid/Mailgun

## Daily commands

```bash
python manage.py runserver        # dev server on :8000
python manage.py migrate          # apply database migrations
python manage.py makemigrations   # create new migrations
python manage.py createsuperuser  # admin user
python manage.py collectstatic    # assemble static files
python manage.py test             # run the test suite
```

### Celery (when enabled)

```bash
celery -A my_project worker -l info
celery -A my_project beat -l info
```

### Frontend pipeline (when enabled)

=== "Vite"

    ```bash
    npm install
    npm run dev      # start Vite dev server
    npm run build    # production build
    ```

=== "webpack"

    ```bash
    npm install
    npm run dev
    npm run build
    ```

=== "Parcel"

    ```bash
    npm install
    npm run dev
    npm run build
    ```