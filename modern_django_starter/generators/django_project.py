"""Generator for Django project structure (settings, urls, wsgi, asgi)."""

from pathlib import Path

from .base import BaseGenerator


class DjangoProjectGenerator(BaseGenerator):
    """Generates Django project structure including settings, URLs, WSGI/ASGI."""

    def generate(self) -> None:
        """Generate the Django project structure."""
        self.log('📦 Creating Django project structure...')

        # Create manage.py
        self._generate_manage_py()

        # Create project package
        project_package = self.project_dir / self.project_name
        project_package.mkdir(exist_ok=True)
        self._create_init_file(project_package)

        # Create settings
        self._generate_settings(project_package)

        # Create urls.py
        self._generate_urls(project_package)

        # Create wsgi.py and asgi.py
        self._generate_wsgi(project_package)
        if self.config.get('use_async'):
            self._generate_asgi(project_package)

    def _generate_manage_py(self) -> None:
        """Generate manage.py."""
        content = self.render_template('manage.py.j2')
        self.write_file(self.project_dir / 'manage.py', content)

    def _create_init_file(self, package_dir: Path) -> None:
        """Create __init__.py in a package directory."""
        self.write_file(package_dir / '__init__.py', '')

    def _generate_settings(self, project_package: Path) -> None:
        """Generate settings files (base, development, production)."""
        settings_dir = project_package / 'settings'
        settings_dir.mkdir(exist_ok=True)
        self._create_init_file(settings_dir)

        for settings_file in ['base.py', 'development.py', 'production.py']:
            content = self.render_template(f'settings/{settings_file}.j2')
            self.write_file(settings_dir / settings_file, content)

    def _generate_urls(self, project_package: Path) -> None:
        """Generate urls.py."""
        content = self.render_template('urls.py.j2')
        self.write_file(project_package / 'urls.py', content)

    def _generate_wsgi(self, project_package: Path) -> None:
        """Generate wsgi.py."""
        content = self.render_template('wsgi.py.j2')
        self.write_file(project_package / 'wsgi.py', content)

    def _generate_asgi(self, project_package: Path) -> None:
        """Generate asgi.py."""
        content = self.render_template('asgi.py.j2')
        self.write_file(project_package / 'asgi.py', content)