# Getting Started

## Requirements

- **Python 3.12 or newer**
- [uv](https://docs.astral.sh/uv/) (recommended) or `pip`
- [Docker](https://www.docker.com/) — only if you plan to use the included Docker tooling
- Node.js and npm — only needed if you elect to generate a frontend build pipeline

## 1. Install the CLI

=== "uv (recommended)"

    ```bash
    uv tool install modern-django-starter
    ```

    This installs the CLI into an isolated tool environment and puts the
    `modern-django-starter` command on your `PATH`.

=== "pip"

    ```bash
    pip install modern-django-starter
    ```

    Install it in a dedicated environment (e.g. `python -m venv`, uvx, pipx)
    so it doesn't pollute your global site-packages.

You can verify the install:

```bash
modern-django-starter --version
modern-django-starter --help
```

## 2. Create your first project

```bash
modern-django-starter create my_project
```

The CLI asks a series of questions and shows a summary table before generating.
Here's what an interactive run looks like:

```text
██████▄       ███ ▄███████▄ ███▄▄  ███ ▄███████▄    ▄██████▄
███  ███      ███ ███   ███ ███▀██▄███ ███▀  ▀▀▀   ███▀  ▀███
███  ▐██ ███  ███ █████████ ███  ▀▀███ ███  ▀▀███▀ ███    ███
███▄▄██▀ ███▄▄███ ███   ███ ███    ███ ████▄▄████  ▀███▄▄███▀
▀▀▀▀▀▀    ▀▀▀▀▀▀  ▀▀▀   ▀▀▀ ▀▀▀    ▀▀▀  ▀▀▀▀▀▀▀ ▀    ▀▀▀▀▀▀
▄███████▄ █████████ ▄███████▄ ███████▄  █████████ ████████ ███████▄
███▄▄▄▄      ███    ███   ███ ███   ███    ███    ███      ███   ███
 ▀██████▄    ███    █████████ ████████     ███    ███▀▀▀   ████████
▄▄▄▄▄▄███    ███    ███   ███ ███   ███    ███    ███▄▄▄▄▄ ███   ███
 ▀▀▀▀▀▀▀     ▀▀▀    ▀▀▀   ▀▀▀ ▀▀▀   ▀▀▀    ▀▀▀    ▀▀▀▀▀▀▀▀ ▀▀▀   ▀▀▀

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Modern Django Starter                                                  │
  ├─────────────────────────────────────────────────────────────────────────┤
  │  Version  │  v0.3.0                                                     │
  │  Author   │  Rian Barriga                                               │
  │  License  │  MIT                                                        │
  │  GitHub   │  CasualEngineerZombie/modern-django-starter                 │
  └─────────────────────────────────────────────────────────────────────────┘

Generate Django 6.1 projects with HTMX, AlpineJS, and more!

📋 Configuration Options
Add Docker support? [y/n] (y): y
Use PostgreSQL database? [y/n] (y): y
PostgreSQL version (15/16/17/18) (18): 18
Cloud provider (none/aws/azure/gcp/render/railway/pythonanywhere/flyio/dokku/heroku) (none): none
Storage provider for media files (local/aws/gcp/azure/cloudflare-r2) (local): local
Email provider (none/sendgrid/mailgun/ses/postmark) (none): none
Enable asynchronous support? [y/n] (n): n
Add Django Rest Framework? [y/n] (y): y
Add Celery for background tasks? [y/n] (y): y
Add Sentry error tracking? [y/n] (y): y
Add Stripe for payments? [y/n] (n): n
Frontend pipeline (none/webpack/vite/parcel) (vite): vite
CI tool (none/github-actions/gitlab-ci/travis/circleci) (github-actions): github-actions

📊 Configuration Summary
┌────────────────────────┬──────────────────────┐
│ Option                 │ Value                │
...
Generate project 'my_project'? [y/n] (y): y
🔨 Generating project 'my_project'...
```

!!! warning "Project name rules"
    The project name must be a **valid Python identifier**: letters, digits, and
    underscores, and it cannot start with a digit. Hyphens like `my-project` are
    rejected because the name becomes a Python package:

    ```text
    ❌ Project name must be a valid Python identifier
    ```

    Use `snake_case`: `my_project`, `shop_api`, `analytics_platform`.

### Create elsewhere

By default the project is created in the current directory. Pass `--output-dir` (or `-o`)
to choose another location:

```bash
modern-django-starter create my_project --output-dir ~/projects
```

## 3. Run your new project

=== "With Docker"

    ```bash
    cd my_project
    cp .env.example .env          # fill in values if needed
    docker compose up -d --build
    docker compose exec web python manage.py createsuperuser
    ```

    On startup the `web` container waits for its dependencies, applies
    migrations, and collects static files before starting the dev server. Visit
    <http://localhost:8000> and the admin at <http://localhost:8000/admin>.
    Production containers do not auto-migrate — see [Deployment](deployment.md).

=== "Without Docker"

    ```bash
    cd my_project
    python -m venv venv
    source venv/bin/activate      # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver
    ```

!!! tip "PostgreSQL"
    If you chose PostgreSQL and run without Docker, make sure a PostgreSQL server is
    running and its values match `DB_*` in your `.env`. SQLite is used when you
    answer "no" to PostgreSQL.

## What's next

-   [CLI Reference](cli-reference.md) — full command and option reference
-   [Configuration](configuration.md) — every question, its choices, and all env vars
-   [Generated Project](generated-project.md) — walkthrough of the generated code
-   [API-Only Projects](api-only.md) — quickly build a headless DRF backend