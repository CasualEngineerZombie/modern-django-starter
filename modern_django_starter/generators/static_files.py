"""Generator for static files."""

from pathlib import Path

from .base import BaseGenerator


class StaticFilesGenerator(BaseGenerator):
    """Generates static files (CSS, JS, images, package.json)."""

    def generate(self) -> None:
        """Generate static files."""
        self.log('🎯 Creating static files...')

        static_dir = self.project_dir / 'static'
        static_dir.mkdir(exist_ok=True)

        # Create subdirectories
        css_dir = static_dir / 'css'
        css_dir.mkdir(exist_ok=True)

        js_dir = static_dir / 'js'
        js_dir.mkdir(exist_ok=True)

        img_dir = static_dir / 'img'
        img_dir.mkdir(exist_ok=True)

        # Generate main CSS file
        content = self.render_template('static/css/main.css.j2')
        self.write_file(css_dir / 'main.css', content)

        # Generate main JS file
        content = self.render_template('static/js/main.js.j2')
        self.write_file(js_dir / 'main.js', content)

        # Generate package.json if frontend pipeline is used
        if self.config.get('frontend_pipeline') != 'none':
            self._generate_package_json()
            if self.config.get('frontend_pipeline') == 'vite':
                self._generate_vite_config()

    def _generate_package_json(self) -> None:
        """Generate package.json."""
        content = self.render_template('package.json.j2')
        self.write_file(self.project_dir / 'package.json', content)

    def _generate_vite_config(self) -> None:
        """Generate vite.config.js."""
        content = self.render_template('vite.config.js.j2')
        self.write_file(self.project_dir / 'vite.config.js', content)