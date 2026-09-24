"""Tests for the main project generator."""

import tempfile
from pathlib import Path

from modern_django_starter.generators.project import ProjectGenerator


class TestProjectGenerator:
    """Test ProjectGenerator (main orchestrator)."""

    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)
        self.template_dir = Path(self.temp_dir.name) / "templates"
        self.template_dir.mkdir(parents=True)

        # Create minimal template structure for all generators
        self._create_all_templates()

    def teardown_method(self):
        self.temp_dir.cleanup()

    def _create_all_templates(self):
        """Create minimal templates for all generators."""
        # Django project templates
        (self.template_dir / "manage.py.j2").write_text("manage.py for {{ project_name }}")
        settings_dir = self.template_dir / "settings"
        settings_dir.mkdir(parents=True)
        for name in ["base.py.j2", "development.py.j2", "production.py.j2"]:
            (settings_dir / name).write_text(f"# {name}")
        (self.template_dir / "urls.py.j2").write_text("urlpatterns = []")
        (self.template_dir / "wsgi.py.j2").write_text("wsgi")
        (self.template_dir / "asgi.py.j2").write_text("asgi")

        # Requirements templates
        req_dir = self.template_dir / "requirements"
        req_dir.mkdir(parents=True)
        for name in ["base.txt.j2", "development.txt.j2", "production.txt.j2"]:
            (req_dir / name).write_text(f"# {name}")

        # Config templates
        (self.template_dir / "env.example.j2").write_text("SECRET_KEY=test")
        (self.template_dir / "gitignore.j2").write_text("*.pyc")
        (self.template_dir / "README.md.j2").write_text("# {{ project_name }}")

        # Template templates
        tpl_dir = self.template_dir / "templates"
        tpl_dir.mkdir(parents=True)
        (tpl_dir / "base.html.j2").write_text("<html></html>")
        (tpl_dir / "home.html.j2").write_text("Home")
        auth_dir = tpl_dir / "account"
        auth_dir.mkdir(parents=True)
        for n in ["login.html.j2", "signup.html.j2", "logout.html.j2"]:
            (auth_dir / n).write_text("auth")

        # Static templates
        static_dir = self.template_dir / "static"
        static_dir.mkdir(parents=True)
        css_dir = static_dir / "css"
        css_dir.mkdir(parents=True)
        js_dir = static_dir / "js"
        js_dir.mkdir(parents=True)
        (css_dir / "main.css.j2").write_text("/* css */")
        (js_dir / "main.js.j2").write_text("// js")
        (self.template_dir / "package.json.j2").write_text('{"name": "{{ project_name }}"}')
        (self.template_dir / "vite.config.js.j2").write_text("vite")

        # Docker templates
        (self.template_dir / "Dockerfile.j2").write_text("FROM python:3.12")
        (self.template_dir / "docker-compose.yml.j2").write_text("services:")
        (self.template_dir / "entrypoint.sh.j2").write_text("#!/bin/sh")
        (self.template_dir / "dockerignore.j2").write_text("*.pyc")

        # CI templates
        github_dir = self.template_dir / ".github" / "workflows"
        github_dir.mkdir(parents=True)
        (github_dir / "ci.yml.j2").write_text("name: CI")

    def _make_generator(self, config):
        return ProjectGenerator("test_project", self.output_dir, config)

    def test_generate_creates_project_directory(self):
        config = {"api_only": False, "use_docker": False, "ci_tool": "none"}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.output_dir / "test_project").exists()

    def test_api_only_generates_correct_structure(self):
        config = {"api_only": True, "use_docker": False, "ci_tool": "none"}
        gen = self._make_generator(config)
        gen.generate()

        project_dir = self.output_dir / "test_project"
        assert (project_dir / "manage.py").exists()
        assert (project_dir / "test_project" / "settings" / "base.py").exists()
        assert (project_dir / "apps" / "api").exists()
        # No templates, static, core, accounts
        assert not (project_dir / "templates").exists()
        assert not (project_dir / "static").exists()
        assert not (project_dir / "apps" / "core").exists()
        assert not (project_dir / "apps" / "accounts").exists()

    def test_full_mode_generates_correct_structure(self):
        config = {"api_only": False, "use_docker": False, "ci_tool": "none", "use_drf": True}
        gen = self._make_generator(config)
        gen.generate()

        project_dir = self.output_dir / "test_project"
        assert (project_dir / "manage.py").exists()
        assert (project_dir / "test_project" / "settings" / "base.py").exists()
        assert (project_dir / "apps" / "core").exists()
        assert (project_dir / "apps" / "accounts").exists()
        assert (project_dir / "apps" / "api").exists()
        assert (project_dir / "templates").exists()
        assert (project_dir / "static").exists()

    def test_docker_generator_included_when_enabled(self):
        config = {"api_only": False, "use_docker": True, "ci_tool": "none"}
        gen = self._make_generator(config)
        gen.generate()

        project_dir = self.output_dir / "test_project"
        assert (project_dir / "Dockerfile").exists()
        assert (project_dir / "docker-compose.yml").exists()
        assert (project_dir / "entrypoint.sh").exists()
        assert (project_dir / ".dockerignore").exists()

    def test_docker_generator_excluded_when_disabled(self):
        config = {"api_only": False, "use_docker": False, "ci_tool": "none"}
        gen = self._make_generator(config)
        gen.generate()

        project_dir = self.output_dir / "test_project"
        assert not (project_dir / "Dockerfile").exists()

    def test_ci_generator_included_when_github_actions(self):
        config = {"api_only": False, "use_docker": False, "ci_tool": "github-actions"}
        gen = self._make_generator(config)
        gen.generate()

        project_dir = self.output_dir / "test_project"
        assert (project_dir / ".github" / "workflows" / "ci.yml").exists()

    def test_ci_generator_excluded_when_none(self):
        config = {"api_only": False, "use_docker": False, "ci_tool": "none"}
        gen = self._make_generator(config)
        gen.generate()

        project_dir = self.output_dir / "test_project"
        assert not (project_dir / ".github").exists()

    def test_static_files_excluded_in_api_only(self):
        config = {"api_only": True, "use_docker": False, "ci_tool": "none"}
        gen = self._make_generator(config)
        gen.generate()

        project_dir = self.output_dir / "test_project"
        assert not (project_dir / "static").exists()
        assert not (project_dir / "package.json").exists()

    def test_templates_excluded_in_api_only(self):
        config = {"api_only": True, "use_docker": False, "ci_tool": "none"}
        gen = self._make_generator(config)
        gen.generate()

        project_dir = self.output_dir / "test_project"
        assert not (project_dir / "templates").exists()

    def test_requirements_generated_for_both_modes(self):
        for api_only in [True, False]:
            config = {"api_only": api_only, "use_docker": False, "ci_tool": "none"}
            gen = self._make_generator(config)
            gen.generate()

            project_dir = self.output_dir / "test_project"
            assert (project_dir / "requirements" / "base.txt").exists()
            assert (project_dir / "requirements.txt").exists()