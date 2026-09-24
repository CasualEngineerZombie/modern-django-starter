"""Tests for the Django project generator."""

import tempfile
from pathlib import Path

from modern_django_starter.generators.django_project import DjangoProjectGenerator


class TestDjangoProjectGenerator:
    """Test DjangoProjectGenerator."""

    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name) / "test_project"
        self.template_dir = Path(self.temp_dir.name) / "templates"
        self.template_dir.mkdir(parents=True)

        # Create project directory
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Create minimal template structure
        self._create_templates()

        self.config = {
            "project_name": "test_project",
            "use_async": False,
            "use_drf": True,
            "use_celery": False,
            "use_sentry": False,
            "use_stripe": False,
            "use_postgresql": False,
            "storage_provider": "local",
            "email_provider": "none",
            "api_only": False,
        }
        self.generator = DjangoProjectGenerator(
            "test_project", self.project_dir, self.config, self.template_dir
        )

    def teardown_method(self):
        self.temp_dir.cleanup()

    def _create_templates(self):
        """Create minimal templates for testing."""
        # manage.py.j2
        (self.template_dir / "manage.py.j2").write_text(
            "#!/usr/bin/env python\nimport os\nimport sys\n\n"
            "if __name__ == '__main__':\n    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{ project_name }}.settings')\n"
        )

        # settings templates
        settings_dir = self.template_dir / "settings"
        settings_dir.mkdir(parents=True)
        for name in ["base.py.j2", "development.py.j2", "production.py.j2"]:
            # Use double braces to escape in f-string: {{ becomes {, }} becomes }
            # We want the template to have {{ project_name }} so we need {{{{ project_name }}}}
            (settings_dir / name).write_text(f"# {name}\nPROJECT = '{{{{ project_name }}}}'\n")

        # urls.py.j2
        (self.template_dir / "urls.py.j2").write_text(
            "from django.urls import path, include\n"
            "urlpatterns = [\n    path('', include('apps.core.urls')),\n]\n"
        )

        # wsgi.py.j2
        (self.template_dir / "wsgi.py.j2").write_text(
            "import os\nfrom django.core.wsgi import get_wsgi_application\n"
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{ project_name }}.settings')\n"
            "application = get_wsgi_application()\n"
        )

        # asgi.py.j2
        (self.template_dir / "asgi.py.j2").write_text(
            "import os\nfrom django.core.asgi import get_asgi_application\n"
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{ project_name }}.settings')\n"
            "application = get_asgi_application()\n"
        )

    def test_generate_creates_project_structure(self):
        self.generator.generate()

        # Check manage.py
        assert (self.project_dir / "manage.py").exists()

        # Check project package
        pkg = self.project_dir / "test_project"
        assert pkg.exists()
        assert (pkg / "__init__.py").exists()

        # Check settings
        settings_dir = pkg / "settings"
        assert settings_dir.exists()
        assert (settings_dir / "__init__.py").exists()
        assert (settings_dir / "base.py").exists()
        assert (settings_dir / "development.py").exists()
        assert (settings_dir / "production.py").exists()

        # Check urls.py
        assert (pkg / "urls.py").exists()

        # Check wsgi.py
        assert (pkg / "wsgi.py").exists()

        # asgi.py should NOT exist when use_async=False
        assert not (pkg / "asgi.py").exists()

    def test_generate_creates_asgi_when_use_async_true(self):
        self.config["use_async"] = True
        gen = DjangoProjectGenerator("test_project", self.project_dir, self.config, self.template_dir)
        gen.generate()

        assert (self.project_dir / "test_project" / "asgi.py").exists()

    def test_settings_files_have_correct_content(self):
        self.generator.generate()

        base_content = (self.project_dir / "test_project" / "settings" / "base.py").read_text()
        assert "PROJECT = 'test_project'" in base_content or 'PROJECT = "test_project"' in base_content

        dev_content = (self.project_dir / "test_project" / "settings" / "development.py").read_text()
        assert "PROJECT = 'test_project'" in dev_content or 'PROJECT = "test_project"' in dev_content

        prod_content = (self.project_dir / "test_project" / "settings" / "production.py").read_text()
        assert "PROJECT = 'test_project'" in prod_content or 'PROJECT = "test_project"' in prod_content

    def test_manage_py_has_project_name(self):
        self.generator.generate()
        content = (self.project_dir / "manage.py").read_text()
        assert "test_project.settings" in content

    def test_wsgi_py_has_project_name(self):
        self.generator.generate()
        content = (self.project_dir / "test_project" / "wsgi.py").read_text()
        assert "test_project.settings" in content

    def test_asgi_py_has_project_name_when_async(self):
        self.config["use_async"] = True
        gen = DjangoProjectGenerator("test_project", self.project_dir, self.config, self.template_dir)
        gen.generate()

        content = (self.project_dir / "test_project" / "asgi.py").read_text()
        assert "test_project.settings" in content

    def test_urls_py_generated(self):
        self.generator.generate()
        content = (self.project_dir / "test_project" / "urls.py").read_text()
        assert "urlpatterns" in content
        assert "django.urls" in content