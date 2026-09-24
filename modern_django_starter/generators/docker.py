"""Generator for Docker files."""

from pathlib import Path

from .base import BaseGenerator


class DockerGenerator(BaseGenerator):
    """Generates Docker files (Dockerfile, docker-compose.yml, entrypoint.sh)."""

    def generate(self) -> None:
        """Generate Docker files if enabled."""
        if not self.config.get('use_docker'):
            return

        self.log('🐳 Creating Docker files...')

        # Dockerfile
        content = self.render_template('Dockerfile.j2')
        self.write_file(self.project_dir / 'Dockerfile', content)

        # docker-compose.yml
        content = self.render_template('docker-compose.yml.j2')
        self.write_file(self.project_dir / 'docker-compose.yml', content)

        # entrypoint.sh — written with explicit LF line endings because /bin/sh rejects CRLF scripts
        content = self.render_template('entrypoint.sh.j2')
        entrypoint_path = self.project_dir / 'entrypoint.sh'
        self.write_file(entrypoint_path, content, newline='\n')

        # .dockerignore
        content = self.render_template('dockerignore.j2')
        self.write_file(self.project_dir / '.dockerignore', content)