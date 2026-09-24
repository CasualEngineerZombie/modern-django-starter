"""Tests for the requirements generator."""

import tempfile
from pathlib import Path

import pytest

from modern_django_starter.generators.requirements import RequirementsGenerator


class TestRequirementsGenerator:
    """Test RequirementsGenerator."""

    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name) / "test_project"
        self.template_dir = Path(self.temp_dir.name) / "templates"
        self.template_dir.mkdir(parents=True)

        # Create project directory
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Create requirements templates for full mode
        req_dir = self.template_dir / "requirements"
        req_dir.mkdir(parents=True)
        (req_dir / "base.txt.j2").write_text("Django==6.1.1\npython-decouple==3.8\n")
        (req_dir / "development.txt.j2").write_text("-r base.txt\npytest==8.0.0\n")
        (req_dir / "production.txt.j2").write_text("-r base.txt\ngunicorn==23.0.0\n")

    def teardown_method(self):
        self.temp_dir.cleanup()

    def _make_generator(self, config):
        return RequirementsGenerator("test_project", self.project_dir, config, self.template_dir)

    # --- API-only mode tests ---

    def test_api_only_base_requirements(self):
        config = {
            "api_only": True,
            "use_postgresql": False,
            "storage_provider": "local",
            "use_celery": False,
            "use_sentry": False,
            "use_stripe": False,
            "use_drf": True,
        }
        gen = self._make_generator(config)
        gen.generate()

        base = (self.project_dir / "requirements" / "base.txt").read_text()
        assert "Django>=6.1" in base
        assert "djangorestframework" in base
        assert "django-cors-headers" in base
        assert "drf-spectacular" in base
        assert "djangorestframework-simplejwt" in base
        assert "dj-rest-auth" in base
        assert "django-allauth" in base
        assert "requests" in base
        assert "python-decouple" in base

    def test_api_only_with_postgresql(self):
        config = {
            "api_only": True,
            "use_postgresql": True,
            "storage_provider": "local",
            "use_celery": False,
            "use_sentry": False,
            "use_stripe": False,
        }
        gen = self._make_generator(config)
        gen.generate()

        base = (self.project_dir / "requirements" / "base.txt").read_text()
        assert "psycopg2-binary" in base

    def test_api_only_with_celery(self):
        config = {
            "api_only": True,
            "use_postgresql": False,
            "storage_provider": "local",
            "use_celery": True,
            "use_sentry": False,
            "use_stripe": False,
        }
        gen = self._make_generator(config)
        gen.generate()

        base = (self.project_dir / "requirements" / "base.txt").read_text()
        assert "celery" in base
        assert "redis" in base

    def test_api_only_with_sentry(self):
        config = {
            "api_only": True,
            "use_postgresql": False,
            "storage_provider": "local",
            "use_celery": False,
            "use_sentry": True,
            "use_stripe": False,
        }
        gen = self._make_generator(config)
        gen.generate()

        base = (self.project_dir / "requirements" / "base.txt").read_text()
        assert "sentry-sdk" in base

    def test_api_only_with_stripe(self):
        config = {
            "api_only": True,
            "use_postgresql": False,
            "storage_provider": "local",
            "use_celery": False,
            "use_sentry": False,
            "use_stripe": True,
        }
        gen = self._make_generator(config)
        gen.generate()

        base = (self.project_dir / "requirements" / "base.txt").read_text()
        assert "dj-stripe" in base
        assert "stripe" in base
        # Ensure correct package name (with hyphen)
        assert "djstripe" not in base or "dj-stripe" in base

    @pytest.mark.parametrize("provider,expected", [
        ("aws", ["django-storages", "boto3"]),
        ("cloudflare-r2", ["django-storages", "boto3"]),
        ("gcp", ["django-storages", "google-cloud-storage"]),
        ("azure", ["django-storages", "azure-storage-blob"]),
    ])
    def test_api_only_with_storage_provider(self, provider, expected):
        config = {
            "api_only": True,
            "use_postgresql": False,
            "storage_provider": provider,
            "use_celery": False,
            "use_sentry": False,
            "use_stripe": False,
        }
        gen = self._make_generator(config)
        gen.generate()

        base = (self.project_dir / "requirements" / "base.txt").read_text()
        for pkg in expected:
            assert pkg in base, f"{pkg} missing for {provider}"

    def test_api_only_local_storage_no_extra_packages(self):
        config = {
            "api_only": True,
            "use_postgresql": False,
            "storage_provider": "local",
            "use_celery": False,
            "use_sentry": False,
            "use_stripe": False,
        }
        gen = self._make_generator(config)
        gen.generate()

        base = (self.project_dir / "requirements" / "base.txt").read_text()
        assert "django-storages" not in base
        assert "boto3" not in base

    def test_api_only_dev_and_prod_inherit_base(self):
        config = {"api_only": True, "use_postgresql": False, "storage_provider": "local"}
        gen = self._make_generator(config)
        gen.generate()

        dev = (self.project_dir / "requirements" / "development.txt").read_text()
        prod = (self.project_dir / "requirements" / "production.txt").read_text()

        assert dev.strip() == "-r base.txt"
        assert prod.strip() == "-r base.txt"

    def test_api_only_root_requirements_txt(self):
        config = {"api_only": True, "use_postgresql": False, "storage_provider": "local"}
        gen = self._make_generator(config)
        gen.generate()

        root = (self.project_dir / "requirements.txt").read_text()
        assert root.strip() == "-r requirements/development.txt"

    # --- Full mode tests ---

    def test_full_mode_uses_templates(self):
        config = {"api_only": False, "use_postgresql": False}
        gen = self._make_generator(config)
        gen.generate()

        base = (self.project_dir / "requirements" / "base.txt").read_text()
        assert "Django==6.1.1" in base
        assert "python-decouple==3.8" in base

    def test_full_mode_dev_and_prod_inherit_base(self):
        config = {"api_only": False}
        gen = self._make_generator(config)
        gen.generate()

        dev = (self.project_dir / "requirements" / "development.txt").read_text()
        prod = (self.project_dir / "requirements" / "production.txt").read_text()

        assert "-r base.txt" in dev
        assert "-r base.txt" in prod