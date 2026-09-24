"""Generator for configuration files."""

from pathlib import Path

from .base import BaseGenerator


class ConfigurationGenerator(BaseGenerator):
    """Generates configuration files (.env.example, .gitignore, README.md)."""

    def generate(self) -> None:
        """Generate configuration files."""
        self.log('⚙️  Creating configuration files...')

        # .env.example
        content = self.render_template('env.example.j2')
        self.write_file(self.project_dir / '.env.example', content)

        # .gitignore
        content = self.render_template('gitignore.j2')
        self.write_file(self.project_dir / '.gitignore', content)

        # README.md
        content = self.render_template('README.md.j2')
        self.write_file(self.project_dir / 'README.md', content)