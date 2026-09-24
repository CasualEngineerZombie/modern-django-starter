# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Sections without a date below are pre-tag; the date is filled in when the tag
is cut (see the release process in [`docs/contributing.md`](docs/contributing.md)).

## [Unreleased]

### Added

- **Live AWS S3 integration test (kumo emulator)**: `tests/test_aws_s3_integration.py` generates an AWS-storage project and runs a real django-storages round trip (save → open → delete) against the kumo AWS emulator from `docker-compose.act.yml`. Gated behind `RUN_DJANGO_INTEGRATION_TESTS=1` plus `AWS_S3_ENDPOINT_URL`, so unit runs stay hermetic; the CI integration job starts kumo as a service container.
- **`AWS_S3_ENDPOINT_URL` for AWS storage projects**: generated AWS settings now accept an S3-compatible endpoint (MinIO, kumo, LocalStack) like the Cloudflare R2 branch already did; `MEDIA_URL` falls back to the endpoint URL when no custom domain is set.
- **Local CI runs with act**: `ci-local.sh` runs the CI workflow locally via act with `.act.env` overrides (tracked defaults in `.act.env.example`; `.act.env` stays gitignored), so pushes no longer have to wait on GitHub Actions results.

### Fixed

- **CI integration job failed on the coverage gate**: the generated-project E2E job ran pytest with the 70% coverage gate meant for the unit suite and failed at ~1% package coverage even though all 48 tests passed; the job now runs with `--no-cov`.
- **kumo compose healthcheck probed a dead port**: the image serves only the AWS APIs on `KUMO_PORT` (4566) and nothing listens on 4567, so the container was permanently `unhealthy`; the healthcheck now probes the S3 endpoint itself.

## [0.3.11] - 2026-09-25

### Added

- **Modular generator architecture**: Refactored monolithic `generator.py` (1067 lines) into 10 focused generators in `modern_django_starter/generators/`:
  - `base.py` - BaseGenerator with common utilities
  - `django_project.py` - Django project structure (settings, urls, wsgi/asgi)
  - `django_apps.py` - Django apps (core, accounts, api, payments - both template & DRF variants)
  - `requirements.py` - Requirements files (API-only & full mode)
  - `configuration.py` - Config files (.env.example, .gitignore, README.md)
  - `templates.py` - HTML templates
  - `static_files.py` - Static files (CSS, JS, package.json, vite config)
  - `docker.py` - Docker files (Dockerfile, compose, entrypoint)
  - `ci.py` - CI configuration (GitHub Actions)
  - `project.py` - Main orchestrator (Facade pattern)

- **Comprehensive generator test suite** (86 tests in `tests/test_generators/`):
  - Unit tests for all 10 generators with 100% coverage on generator modules
  - Parametrized tests for requirements combinations (PostgreSQL, Celery, Sentry, Stripe, storage providers)
  - Edge case tests for API-only vs full mode, Docker enable/disable, CI tools

- **pytest-cov integration**: Coverage reporting (terminal, HTML, XML) with 86.94% total coverage

- **Local CI testing with act + kumo-aws-emu**: Added `docker-compose.act.yml` and `.act.env` for running GitHub Actions locally with AWS S3 emulator

### Fixed

- **Stripe package name bug** (issue #51 follow-up): Fixed `djstripe` → `dj-stripe` in API-only requirements (PyPI package name uses hyphen)
- **mypy type errors**: Fixed implicit Optional types in `BaseGenerator.write_file` and `BaseGenerator.log`
- **pytest discovery on CI**: Added `__init__.py` to `tests/` and `tests/test_generators/` for reliable test collection on Linux

### Changed

- Generator modules now follow Single Responsibility Principle and are independently testable
- Test coverage improved from 34.5% → 86.94% (all generator modules at 100%)
- `pytest-cov` added to dev dependencies with `--cov-fail-under=70` threshold

## [0.3.10] - 2026-09-24

### Added

- Stripe DRF endpoints for API-only projects ([#51](https://github.com/CasualEngineerZombie/modern-django-starter/issues/51), PR [#51](https://github.com/CasualEngineerZombie/modern-django-starter/pull/51)):
  API-only projects (`--api-only`) can now enable Stripe payments with full DRF API support:
  `OrderViewSet` (list/retrieve orders), `CheckoutViewSet` (create checkout sessions, success/cancel handlers),
  and `StripeWebhookView` (handle `checkout.session.completed` webhooks).
  No frontend templates required — just add `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, and `DJSTRIPE_WEBHOOK_SECRET` to `.env`.

### Fixed

- API-only Stripe generation was completely missing; now properly generates payments app with DRF serializers, views, and URLs.

## [0.3.9] - 2026-09-24

### Added

- Root `CHANGELOG.md` in the Keep a Changelog format ([#44](https://github.com/CasualEngineerZombie/modern-django-starter/issues/44), PR [#48](https://github.com/CasualEngineerZombie/modern-django-starter/pull/48)).
- Release process + SemVer policy documented in `docs/contributing.md` ([#44](https://github.com/CasualEngineerZombie/modern-django-starter/issues/44), PR [#48](https://github.com/CasualEngineerZombie/modern-django-starter/pull/48)).

### Fixed

- The generated Docker stack is now bootable and initialized out of the box
  ([#16](https://github.com/CasualEngineerZombie/modern-django-starter/issues/16),
  PR [#49](https://github.com/CasualEngineerZombie/modern-django-starter/pull/49)):
  a new `entrypoint.sh` makes `docker compose up` wait for dependencies, apply
  migrations, and collect static files before starting the dev server; the
  `web` service gained a healthcheck; the `web`/`celery`/`celery-beat` services
  run as the host user so bind-mount files stay owned by the developer; the
  image now builds reliably (Pillow compiles from source on
  `python:3.14-slim`, so the Dockerfile carries its zlib/JPEG dev headers, and
  the build-time `collectstatic` runs under the production settings module
  since the image doesn't install dev-only apps such as `debug_toolbar`);
  the compose dev stack builds with `requirements/development.txt` (via a
  Dockerfile `REQUIREMENTS` build arg, so plain `docker build` stays a slim
  production image) because the development settings module needs the dev-only
  apps at runtime;
  and the README/CLI/docs no longer tell users to run a manual `migrate` step.
  Production startup (plain `gunicorn`, no auto-migrate) is now documented.

### Changed

- `pytest` 8.4.2 → 9.1.1 (PR [#39](https://github.com/CasualEngineerZombie/modern-django-starter/pull/39)).
- `mypy` 1.20.2 → 2.3.1 (PR [#40](https://github.com/CasualEngineerZombie/modern-django-starter/pull/40)).

## [0.3.8] - Unreleased

### Added

- `package` CI job: `uv build` + `uvx twine check dist/*` + template package-data
  verification in the wheel, run on every PR (PR [#47](https://github.com/CasualEngineerZombie/modern-django-starter/pull/47)).

## [0.3.7] - Unreleased

### Fixed

- `mkdocs build --strict` was red on main: Material for MkDocs 9.7.2+ injects an
  MkDocs 2.0 warning banner that `--strict` turns into an error. Pinned
  `mkdocs-material==9.7.1`, the last release before the banner (PR [#46](https://github.com/CasualEngineerZombie/modern-django-starter/pull/46)).

## [0.3.6] - Unreleased

### Fixed

- CI Test jobs now fail the build on Syntax/Deprecation warnings
  (`PYTHONWARNINGS=error::SyntaxWarning,error::DeprecationWarning` on the pytest
  step), so the logo-style `SyntaxWarning` regression can never slip through again
  (PR [#45](https://github.com/CasualEngineerZombie/modern-django-starter/pull/45)).
- `actions/checkout@v4` upgraded to v7 across all workflows via Dependabot
  (PR [#38](https://github.com/CasualEngineerZombie/modern-django-starter/pull/38)).

## [0.3.5] - Unreleased

### Changed

- Removed the unused `cookiecutter` dependency (PR [#37](https://github.com/CasualEngineerZombie/modern-django-starter/pull/37)).

### Added

- Dependabot config (`.github/dependabot.yml`) for `uv` and `github-actions`,
  weekly with the actions group (PR [#37](https://github.com/CasualEngineerZombie/modern-django-starter/pull/37)).

## [0.3.4] - Unreleased

### Fixed

- Package docstring still said "Django 5.1 projects" — now says 6.1
  (PR [#36](https://github.com/CasualEngineerZombie/modern-django-starter/pull/36)).
- Pinned version consistency: a new `tests/test_metadata.py` guard fails if
  `pyproject.toml` and `__version__` drift apart (PR [#36](https://github.com/CasualEngineerZombie/modern-django-starter/pull/36)).

## [0.3.3] - Unreleased

### Fixed

- Generated templates still referenced Django 5.1 (README, home page, `asgi.py`,
  `wsgi.py`) — bumped to 6.1, with a regression test against generated output
  (PR [#35](https://github.com/CasualEngineerZombie/modern-django-starter/pull/35)).

## [0.3.2] - Unreleased

### Changed

- Removed the dead `MDS_v2` ASCII art; the banner is pinned to the v3 art
  (PR [#34](https://github.com/CasualEngineerZombie/modern-django-starter/pull/34)).

## [0.3.1] - Unreleased

### Fixed

- The `MDS_v3` logo emitted an `invalid escape sequence` `SyntaxWarning` (and
  accidentally merged two art lines via a line continuation) — converted to a raw
  string and covered by a warnings-as-errors compile test
  (PR [#33](https://github.com/CasualEngineerZombie/modern-django-starter/pull/33)).

## [0.3.0] - 2026-09-24

Initial public release.

### Added

- `modern-django-starter create <name>` CLI (Click): interactive prompts for Docker,
  PostgreSQL, cloud/storage/email providers, DRF, Celery, Sentry, Stripe, frontend
  pipeline, and CI tooling.
- Generates Django 6.1 projects with HTMX, AlpineJS, TailwindCSS, django-allauth,
  and split settings (`base`/`development`/`production`).
- `--api-only` mode for pure DRF backends (JWT, CORS, drf-spectacular, dj-rest-auth).
- ASCII logo + info banner in the CLI.
- `uv`-based tooling (`pyproject.toml`, `uv.lock`), lint/typecheck/test CI (matrix
  3.12/3.13/3.14), integration E2E test matrix for generated projects.
- MkDocs Material documentation site, deployed to GitHub Pages by `docs.yml`.
- PyPI publishing workflow (`publish.yml`).

[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
[0.3.10]: https://github.com/CasualEngineerZombie/modern-django-starter/compare/v0.3.9...v0.3.10
[0.3.9]: https://github.com/CasualEngineerZombie/modern-django-starter/compare/v0.3.8...v0.3.9
[0.3.8]: https://github.com/CasualEngineerZombie/modern-django-starter/compare/v0.3.7...v0.3.8
[0.3.7]: https://github.com/CasualEngineerZombie/modern-django-starter/compare/v0.3.6...v0.3.7
[0.3.6]: https://github.com/CasualEngineerZombie/modern-django-starter/compare/v0.3.5...v0.3.6
[0.3.5]: https://github.com/CasualEngineerZombie/modern-django-starter/compare/v0.3.4...v0.3.5
[0.3.4]: https://github.com/CasualEngineerZombie/modern-django-starter/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/CasualEngineerZombie/modern-django-starter/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/CasualEngineerZombie/modern-django-starter/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/CasualEngineerZombie/modern-django-starter/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/CasualEngineerZombie/modern-django-starter/releases/tag/v0.3.0