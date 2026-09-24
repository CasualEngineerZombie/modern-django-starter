"""Tests for the configuration generator."""

import tempfile
from pathlib import Path

from modern_django_starter.generators.configuration import ConfigurationGenerator


class TestConfigurationGenerator:
    """Test ConfigurationGenerator."""

    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name) / "test_project"
        self.template_dir = Path(self.temp_dir.name) / "templates"
        self.template_dir.mkdir(parents=True)

        # Create project directory
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Create config templates
        (self.template_dir / "env.example.j2").write_text(
            "SECRET_KEY=django-insecure-change-me\nDEBUG=True\n"
        )
        (self.template_dir / "gitignore.j2").write_text("__pycache__\n.env\n*.pyc\n")
        (self.template_dir / "README.md.j2").write_text("# {{ project_name }}\n\nGenerated project.")

    def teardown_method(self):
        self.temp_dir.cleanup()

    def _make_generator(self, config):
        return ConfigurationGenerator("test_project", self.project_dir, config, self.template_dir)

    def _read_file(self, rel_path):
        return (self.project_dir / rel_path).read_text()

    def test_generate_env_example(self):
        config = {}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.project_dir / ".env.example").exists()
        content = self._read_file(".env.example")
        assert "SECRET_KEY" in content
        assert "DEBUG" in content

    def test_generate_gitignore(self):
        config = {}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.project_dir / ".gitignore").exists()
        content = self._read_file(".gitignore")
        assert "__pycache__" in content
        assert ".env" in content

    def test_generate_readme(self):
        config = {}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.project_dir / "README.md").exists()
        content = self._read_file("README.md")
        assert "# test_project" in content

    def test_all_three_files_generated(self):
        config = {}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.project_dir / ".env.example").exists()
        assert (self.project_dir / ".gitignore").exists()
        assert (self.project_dir / "README.md").exists()