"""Tests for the template generator."""

import tempfile
from pathlib import Path

from modern_django_starter.generators.templates import TemplateGenerator


class TestTemplateGenerator:
    """Test TemplateGenerator."""

    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name) / 'test_project'
        self.template_dir = Path(self.temp_dir.name) / 'templates'
        self.template_dir.mkdir(parents=True)

        # Create project directory
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Create template files
        self._create_templates()

    def teardown_method(self):
        self.temp_dir.cleanup()

    def _create_templates(self):
        """Create minimal templates for testing (no Jinja2 syntax to avoid escaping issues)."""
        tpl_dir = self.template_dir / 'templates'
        tpl_dir.mkdir(parents=True)
        # Base template - simple HTML without Jinja2 extends
        (tpl_dir / 'base.html.j2').write_text('<html><body>BASE</body></html>')
        # Home template - simple HTML without Jinja2 extends
        (tpl_dir / 'home.html.j2').write_text('<html><body>HOME</body></html>')

        auth_dir = tpl_dir / 'account'
        auth_dir.mkdir(parents=True)
        for name in ['login.html.j2', 'signup.html.j2', 'logout.html.j2']:
            (auth_dir / name).write_text(f'<!-- {name} -->')

        payments_dir = tpl_dir / 'payments'
        payments_dir.mkdir(parents=True)
        for name in ['checkout.html.j2', 'success.html.j2', 'cancel.html.j2', 'orders.html.j2']:
            (payments_dir / name).write_text(f'<!-- {name} -->')

    def _make_generator(self, config):
        return TemplateGenerator('test_project', self.project_dir, config, self.template_dir)

    def _read_file(self, rel_path):
        return (self.project_dir / rel_path).read_text()

    def test_generate_base_and_home_templates(self):
        config = {'use_stripe': False}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.project_dir / 'templates' / 'base.html').exists()
        assert (self.project_dir / 'templates' / 'home.html').exists()

        base = self._read_file('templates/base.html')
        assert 'BASE' in base

        home = self._read_file('templates/home.html')
        assert 'HOME' in home

    def test_generate_auth_templates(self):
        config = {'use_stripe': False}
        gen = self._make_generator(config)
        gen.generate()

        auth_dir = self.project_dir / 'templates' / 'account'
        assert auth_dir.exists()
        for name in ['login.html', 'signup.html', 'logout.html']:
            assert (auth_dir / name).exists()
            content = (auth_dir / name).read_text()
            # Template file is named login.html.j2, so check for that
            expected = name.replace('.html', '.html.j2')
            assert expected in content

    def test_generate_payment_templates_when_stripe_enabled(self):
        config = {'use_stripe': True}
        gen = self._make_generator(config)
        gen.generate()

        payments_dir = self.project_dir / 'templates' / 'payments'
        assert payments_dir.exists()
        for name in ['checkout.html', 'success.html', 'cancel.html', 'orders.html']:
            assert (payments_dir / name).exists()
            content = (payments_dir / name).read_text()
            expected = name.replace('.html', '.html.j2')
            assert expected in content

    def test_payment_templates_not_generated_when_stripe_disabled(self):
        config = {'use_stripe': False}
        gen = self._make_generator(config)
        gen.generate()

        payments_dir = self.project_dir / 'templates' / 'payments'
        assert not payments_dir.exists()

    def test_template_dirs_created(self):
        config = {'use_stripe': True}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.project_dir / 'templates').exists()
        assert (self.project_dir / 'templates' / 'account').exists()
        assert (self.project_dir / 'templates' / 'payments').exists()
