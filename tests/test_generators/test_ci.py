"""Tests for the CI generator."""

import tempfile
from pathlib import Path

from modern_django_starter.generators.ci import CIGenerator


class TestCIGenerator:
    """Test CIGenerator."""

    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name) / "test_project"
        self.template_dir = Path(self.temp_dir.name) / "templates"
        self.template_dir.mkdir(parents=True)

        # Create project directory
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Create CI template
        github_dir = self.template_dir / ".github" / "workflows"
        github_dir.mkdir(parents=True)
        (github_dir / "ci.yml.j2").write_text("name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n")

    def teardown_method(self):
        self.temp_dir.cleanup()

    def _make_generator(self, config):
        return CIGenerator("test_project", self.project_dir, config, self.template_dir)

    def _read_file(self, rel_path):
        return (self.project_dir / rel_path).read_text()

    def test_generate_skipped_when_ci_none(self):
        config = {"ci_tool": "none"}
        gen = self._make_generator(config)
        gen.generate()

        assert not (self.project_dir / ".github").exists()

    def test_generate_github_actions(self):
        config = {"ci_tool": "github-actions"}
        gen = self._make_generator(config)
        gen.generate()

        ci_file = self.project_dir / ".github" / "workflows" / "ci.yml"
        assert ci_file.exists()

        content = self._read_file(".github/workflows/ci.yml")
        assert "name: CI" in content
        assert "on: [push]" in content

    def test_generate_other_ci_tools_not_implemented(self):
        # These should not create files (only github-actions is implemented)
        for tool in ["gitlab-ci", "travis", "circleci"]:
            config = {"ci_tool": tool}
            gen = self._make_generator(config)
            gen.generate()

            # Should not create .github dir for non-github tools
            # (current implementation only handles github-actions)
            if tool != "github-actions":
                assert not (self.project_dir / ".github").exists()