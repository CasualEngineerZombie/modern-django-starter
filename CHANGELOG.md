# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Sections without a date below are pre-tag; the date is filled in when the tag
is cut (see the release process in [`docs/contributing.md`](docs/contributing.md)).

## [Unreleased]

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

## [0.3.9] - Unreleased

### Added

- Root `CHANGELOG.md` in the Keep a Changelog format ([#44](https://github.com/CasualEngineerZombie/modern-django-starter/issues/44), PR [#48](https://github.com/CasualEngineerZombie/modern-django-starter/pull/48)).
- Release process + SemVer policy documented in `docs/contributing.md` ([#44](https://github.com/CasualEngineerZombie/modern-django-starter/issues/44), PR [#48](https://github.com/CasualEngineerZombie/modern-django-starter/pull/48)).

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