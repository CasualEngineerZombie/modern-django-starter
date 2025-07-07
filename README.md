# Modern Django Starter 🚀

[![PyPI version](https://badge.fury.io/py/modern-django-starter.svg)](https://badge.fury.io/py/modern-django-starter)
[![PyPI](https://img.shields.io/pypi/v/modern-django-starter)](https://pypi.org/project/modern-django-starter/)
[![Python](https://img.shields.io/pypi/pyversions/modern-django-starter)](https://pypi.org/project/modern-django-starter/)
[![Downloads](https://pepy.tech/badge/modern-django-starter)](https://pepy.tech/project/modern-django-starter)

A CLI tool for generating Django 5.x projects with HTMX, AlpineJS, and more. Streamline your setup with customizable options for Docker, databases, cloud providers, and frontend pipelines. Build modern, reactive Django apps faster! 

## Installation

Install from PyPI:

```bash
pip install modern-django-starter
```

📦 **PyPI Package**: https://pypi.org/project/modern-django-starter/

## Quick Start

Generate a new Django project:

```bash
modern-django-starter create my_awesome_project
```

Or with options:

```bash
modern-django-starter create my_project --output-dir /path/to/projects
```

## API-Only Projects

Generate a Django REST API project (no frontend, no templates/static) with all the essentials:

- Django REST Framework (DRF)
- JWT authentication (djangorestframework-simplejwt)
- CORS support (django-cors-headers)
- API schema & docs (drf-spectacular)
- Registration/auth endpoints (dj-rest-auth, django-allauth)

Example:

```bash
modern-django-starter create my_api_project --api-only
```

This will generate a minimal, production-ready Django API backend with all the above features and no frontend code.

## Features

- Django 5.x
- HTMX for dynamic HTML updates
- AlpineJS for lightweight JavaScript interactions
- Django-allauth for authentication
- HyperScript for easy DOM manipulation
- TailwindCSS and DaisyUI for styling
- Docker support (optional)
- PostgreSQL database
- Cloud provider integration options
- Email provider integration
- Django Rest Framework (DRF) support
- **API-only mode**: Generate a DRF-only backend with JWT, CORS, Spectacular, dj-rest-auth, and allauth
- Frontend pipeline options
- Celery for background task processing
- Sentry for error tracking
- CI tool integration options

## Prerequisites

- Python 3.8+
- pip

Optional:
- Node.js and npm (for frontend pipelines)
- Docker (for containerized development)

## Development Installation

If you want to contribute or install from source:

1. Clone this repository:
   ```bash
   git clone https://github.com/CasualEngineerZombie/modern-django-starter.git
   cd modern-django-starter
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

## Usage

Generate a new Django project:

```bash
modern-django-starter create my_awesome_project
```

Or specify an output directory:

```bash
modern-django-starter create my_project --output-dir /path/to/projects
```

The CLI will guide you through configuration options interactively.

## Configuration Options

- Docker support
- PostgreSQL version
- Cloud provider (AWS, Azure, GCP, Render, Railway, PythonAnywhere, Flyio, Dokku, Heroku, or none)
- Email provider
- Asynchronous support
- Django Rest Framework
- **API-only mode** (`--api-only`): DRF, JWT, CORS, Spectacular, dj-rest-auth, allauth, no frontend
- Frontend pipeline
- Celery
- Sentry
- CI tools

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
