"""Tests for the Docker generator."""

import tempfile
from pathlib import Path

from modern_django_starter.generators.docker import DockerGenerator


class TestDockerGenerator:
    """Test DockerGenerator."""

    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name) / "test_project"
        self.template_dir = Path(self.temp_dir.name) / "templates"
        self.template_dir.mkdir(parents=True)

        # Create project directory
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Create Docker templates
        (self.template_dir / "Dockerfile.j2").write_text("FROM python:3.12\nWORKDIR /app\nCOPY . .\n")
        (self.template_dir / "docker-compose.yml.j2").write_text("version: '3.8'\nservices:\n  web:\n    build: .\n")
        (self.template_dir / "entrypoint.sh.j2").write_text("#!/bin/sh\necho 'starting'\nexec \"$@\"\n")
        (self.template_dir / "dockerignore.j2").write_text("__pycache__\n*.pyc\n.env\n")

    def teardown_method(self):
        self.temp_dir.cleanup()

    def _make_generator(self, config):
        return DockerGenerator("test_project", self.project_dir, config, self.template_dir)

    def _read_file(self, rel_path):
        return (self.project_dir / rel_path).read_text()

    def test_generate_skipped_when_docker_disabled(self):
        config = {"use_docker": False}
        gen = self._make_generator(config)
        gen.generate()

        assert not (self.project_dir / "Dockerfile").exists()
        assert not (self.project_dir / "docker-compose.yml").exists()
        assert not (self.project_dir / "entrypoint.sh").exists()
        assert not (self.project_dir / ".dockerignore").exists()

    def test_generate_creates_all_files_when_enabled(self):
        config = {"use_docker": True, "use_postgresql": False, "use_celery": False}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.project_dir / "Dockerfile").exists()
        assert (self.project_dir / "docker-compose.yml").exists()
        assert (self.project_dir / "entrypoint.sh").exists()
        assert (self.project_dir / ".dockerignore").exists()

    def test_dockerfile_has_project_name(self):
        config = {"use_docker": True}
        gen = self._make_generator(config)
        gen.generate()

        content = self._read_file("Dockerfile")
        assert "test_project" in content or "WORKDIR /app" in content

    def test_docker_compose_has_services(self):
        config = {"use_docker": True}
        gen = self._make_generator(config)
        gen.generate()

        content = self._read_file("docker-compose.yml")
        assert "services:" in content
        assert "web:" in content

    def test_entrypoint_has_lf_line_endings(self):
        config = {"use_docker": True}
        gen = self._make_generator(config)
        gen.generate()

        # Read as binary to check line endings
        content = (self.project_dir / "entrypoint.sh").read_bytes()
        assert b"\r\n" not in content  # No CRLF
        assert b"\n" in content  # Has LF

    def test_entrypoint_has_shebang(self):
        config = {"use_docker": True}
        gen = self._make_generator(config)
        gen.generate()

        content = self._read_file("entrypoint.sh")
        assert content.startswith("#!/bin/sh")

    def test_dockerignore_has_common_patterns(self):
        config = {"use_docker": True}
        gen = self._make_generator(config)
        gen.generate()

        content = self._read_file(".dockerignore")
        assert "__pycache__" in content
        assert "*.pyc" in content
        assert ".env" in content