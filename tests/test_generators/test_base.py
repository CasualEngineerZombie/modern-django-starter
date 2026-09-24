"""Tests for the base generator class."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from modern_django_starter.generators.base import BaseGenerator


class ConcreteGenerator(BaseGenerator):
    """Concrete implementation for testing abstract base class."""

    def generate(self) -> None:
        pass


class TestBaseGenerator:
    """Test BaseGenerator common functionality."""

    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name) / 'test_project'
        self.template_dir = Path(self.temp_dir.name) / 'templates'
        self.template_dir.mkdir(parents=True)

        # Create a simple test template
        (self.template_dir / 'test.txt.j2').write_text('Hello {{ project_name }}!')

        self.config = {'project_name': 'test_project', 'use_docker': False}
        self.generator = ConcreteGenerator(
            'test_project', self.project_dir, self.config, self.template_dir
        )

    def teardown_method(self):
        self.temp_dir.cleanup()

    def test_init_sets_attributes(self):
        assert self.generator.project_name == 'test_project'
        assert self.generator.project_dir == self.project_dir
        assert self.generator.config == self.config
        assert self.generator.template_dir == self.template_dir
        assert self.generator.env is not None

    def test_render_template(self):
        result = self.generator.render_template('test.txt.j2')
        assert result == 'Hello test_project!'

    def test_render_template_with_extra_context(self):
        # Create template that uses config
        (self.template_dir / 'config.txt.j2').write_text('Docker: {{ config.use_docker }}')
        result = self.generator.render_template('config.txt.j2')
        assert result == 'Docker: False'

    def test_write_file_creates_parent_dirs(self):
        file_path = self.project_dir / 'deep' / 'nested' / 'file.txt'
        self.generator.write_file(file_path, 'content')
        assert file_path.exists()
        assert file_path.read_text() == 'content'

    def test_write_file_with_newline(self):
        file_path = self.project_dir / 'lf.txt'
        self.generator.write_file(file_path, 'line1\nline2\n', newline='\n')
        content = file_path.read_bytes()
        assert b'\r\n' not in content  # No CRLF
        assert b'\n' in content

    def test_write_file_with_encoding(self):
        file_path = self.project_dir / 'utf8.txt'
        self.generator.write_file(file_path, 'café', encoding='utf-8')
        assert file_path.read_text(encoding='utf-8') == 'café'

    @patch('modern_django_starter.generators.base.console')
    def test_log_without_style(self, mock_console):
        self.generator.log('test message')
        mock_console.print.assert_called_once_with('test message')

    @patch('modern_django_starter.generators.base.console')
    def test_log_with_style(self, mock_console):
        self.generator.log('styled message', style='bold red')
        mock_console.print.assert_called_once_with('[bold red]styled message[/bold red]')
