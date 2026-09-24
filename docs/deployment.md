# Deployment

This page covers deploying a **generated Django project** to production, and how this
documentation site itself is published.

## Before you deploy

1. **Copy and fill in your environment** — every deploy target needs the same core
   variables:

   ```bash
   cp .env.example .env
   ```

   | Variable | Production value |
   |---|---|
   | `SECRET_KEY` | A fresh long random string — never commit it |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com` |
   | `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | Your managed database |
   | `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` | Redis instances (if Celery enabled) |
   | `SENTRY_DSN` | Sentry project DSN (if Sentry enabled) |
   | Stripe / storage / email variables | As described in [Configuration](configuration.md) |

2. **Run migrations and collect static files:**

   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

## Deploying with Docker

The generated `Dockerfile` and `docker-compose.yml` are production-capable.

Development startup is fully automatic (see [Integrations](integrations.md)):
`docker compose up` waits for dependencies, applies migrations, and collects
static files before the server starts. **Production differs** — the image's
default command is `gunicorn` and it does **not** auto-migrate. Apply
migrations once as an explicit release step before rolling out new containers:

```bash
# Build and run (development)
docker compose up -d --build

# One-shot migration against the release database
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py collectstatic --noinput

# First time only
docker compose exec web python manage.py createsuperuser
```

> `docker compose run` one-offs go through `entrypoint.sh`, which re-applies
> migrations and static setup (idempotent) before the command. Use
> `docker compose exec` against a running stack to skip that.

Then put a reverse proxy (nginx, Caddy, Traefik, or your platform's TLS terminator) in
front of `web` and terminate TLS for your domain.

## Cloud provider quick references

If you selected a cloud provider at generation time, the project README includes
provider-specific instructions. Summary:

=== "Render"

    1. Connect the repository in the Render dashboard.
    2. Add a **Web Service** using the Dockerfile (or the Python runtime).
    3. Set the environment variables from `.[env.example](.env.example)`.
    4. Deploys automatically on push to your branch.

=== "Railway"

    1. Create a new project and link the repository.
    2. Provision a **PostgreSQL** plugin (and Redis if Celery is enabled).
    3. Add the environment variables.
    4. Deploys automatically on push.

=== "Heroku"

    1. `heroku create my_project`
    2. `heroku addons:create heroku-postgresql:hobby-dev`
    3. `heroku config:set DEBUG=False SECRET_KEY=...`
    4. `git push heroku main && heroku run python manage.py migrate`

=== "Fly.io"

    1. `fly auth login`
    2. `fly launch` inside the project (uses the Dockerfile)
    3. `fly secrets set SECRET_KEY=... DEBUG=False`
    4. `fly deploy`

=== "AWS / GCP / Azure"

    Containerize with the provided Dockerfile and push to ECR/GAR/ACR, or use each
    platform's PaaS. Set the database, Redis, storage, and app environment variables
    in the platform's secrets manager.

=== "Dokku"

    ```bash
    dokku apps:create my-project
    dokku config:set my-project SECRET_KEY=... DEBUG=False
    git remote add dokku dokku@your-host:my-project
    git push dokku main
    ```

=== "PythonAnywhere"

    1. Push the repo to GitHub and clone it inside a virtualenv on PythonAnywhere.
    2. `pip install -r requirements/development.txt`
    3. Configure a manual WSGI file pointing at `my_project.wsgi.application`.
    4. Run `migrate` and `collectstatic` from a Bash console, then reload the app.

## Production settings overrides

`settings/production.py` is the right place to tighten things:
`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`,
`SECURE_HSTS_SECONDS`, and so on. The generated file already points you in the right
direction.

---

## Publishing this documentation site

The docs you're reading run on **GitHub Pages** at **https://mds.rianbarriga.com**,
built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

### How it works

The [GitHub Actions workflow](https://github.com/CasualEngineerZombie/modern-django-starter/blob/main/.github/workflows/docs.yml)
(`.github/workflows/docs.yml`) runs on every push to `main`:

1. Installs uv + Python and the `docs` dependency group
2. Builds the site with `uv run mkdocs build --strict`
3. Uploads the `site/` directory as a Pages artifact
4. Deploys it with `actions/deploy-pages`

The repository's Pages configuration must use **"GitHub Actions"** as the source
(Settings → Pages → Source → GitHub Actions).

The custom domain is declared in the `docs/CNAME` file, which MkDocs copies verbatim
into the site root.

### Pointing the DNS at GitHub

To serve `mds.rianbarriga.com` from this Pages site, configure a **CNAME** record:

```text
mds  CNAME  CasualEngineerZombie.github.io
```

!!! warning "CNAME vs apex"
    Since the target is a subdomain, a single `CNAME` (or ALIAS) record is all you need.
    For an apex domain you would instead add GitHub's Pages IP **A** records
    (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`).

After DNS propagates, GitHub issues a TLS certificate for `mds.rianbarriga.com`
automatically.

### Adding or editing pages

- Sources live in [`docs/`](https://github.com/CasualEngineerZombie/modern-django-starter/tree/main/docs).
- The sidebar and page order are defined in [`mkdocs.yml`](https://github.com/CasualEngineerZombie/modern-django-starter/blob/main/mkdocs.yml).
- Build locally before pushing:

  ```bash
  uv sync --group docs
  uv run mkdocs serve       # preview at http://127.0.0.1:8000
  uv run mkdocs build --strict
  ```