"""Tests for the static files generator."""

import tempfile
from pathlib import Path

import pytest

from modern_django_starter.generators.static_files import StaticFilesGenerator


class TestStaticFilesGenerator:
    """Test StaticFilesGenerator."""

    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name) / "test_project"
        self.template_dir = Path(self.temp_dir.name) / "templates"
        self.template_dir.mkdir(parents=True)

        # Create project directory
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Create static templates
        static_dir = self.template_dir / "static"
        static_dir.mkdir(parents=True)
        css_dir = static_dir / "css"
        css_dir.mkdir(parents=True)
        js_dir = static_dir / "js"
        js_dir.mkdir(parents=True)
        (css_dir / "main.css.j2").write_text("/* Main CSS */\nbody { margin: 0; }")
        (js_dir / "main.js.j2").write_text("// Main JS\nconsole.log('loaded');")

        # Create package.json and vite templates
        (self.template_dir / "package.json.j2").write_text('{"name": "{{ project_name }}", "version": "1.0.0"}')
        (self.template_dir / "vite.config.js.j2").write_text("export default {}")

    def teardown_method(self):
        self.temp_dir.cleanup()

    def _make_generator(self, config):
        return StaticFilesGenerator("test_project", self.project_dir, config, self.template_dir)

    def _read_file(self, rel_path):
        return (self.project_dir / rel_path).read_text()

    def test_generate_static_dirs(self):
        config = {"frontend_pipeline": "none"}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.project_dir / "static").exists()
        assert (self.project_dir / "static" / "css").exists()
        assert (self.project_dir / "static" / "js").exists()
        assert (self.project_dir / "static" / "img").exists()

    def test_generate_css_and_js(self):
        config = {"frontend_pipeline": "none"}
        gen = self._make_generator(config)
        gen.generate()

        css = self._read_file("static/css/main.css")
        assert "Main CSS" in css

        js = self._read_file("static/js/main.js")
        assert "Main JS" in js

    @pytest.mark.parametrize("pipeline", ["vite", "webpack", "parcel"])
    def test_generate_package_json_when_pipeline_enabled(self, pipeline):
        config = {"frontend_pipeline": pipeline}
        gen = self._make_generator(config)
        gen.generate()

        pkg = self._read_file("package.json")
        assert '"name": "test_project"' in pkg

    def test_generate_vite_config_when_vite(self):
        config = {"frontend_pipeline": "vite"}
        gen = self._make_generator(config)
        gen.generate()

        vite = self._read_file("vite.config.js")
        assert "export default {}" in vite

    def test_no_vite_config_when_not_vite(self):
        config = {"frontend_pipeline": "webpack"}
        gen = self._make_generator(config)
        gen.generate()

        assert not (self.project_dir / "vite.config.js").exists()

    def test_no_package_json_when_pipeline_none(self):
        config = {"frontend_pipeline": "none"}
        gen = self._make_generator(config)
        gen.generate()

        assert not (self.project_dir / "package.json").exists()
        assert not (self.project_dir / "vite.config.js").exists()