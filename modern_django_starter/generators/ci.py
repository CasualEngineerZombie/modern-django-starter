"""Generator for CI configuration files."""

from .base import BaseGenerator


class CIGenerator(BaseGenerator):
    """Generates CI configuration files."""

    def generate(self) -> None:
        """Generate CI configuration if enabled."""
        if self.config.get('ci_tool') == 'none':
            return

        self.log('🔄 Creating CI configuration...')

        if self.config.get('ci_tool') == 'github-actions':
            self._generate_github_actions()

    def _generate_github_actions(self) -> None:
        """Generate GitHub Actions workflow."""
        github_dir = self.project_dir / '.github' / 'workflows'
        github_dir.mkdir(parents=True, exist_ok=True)

        content = self.render_template('.github/workflows/ci.yml.j2')
        self.write_file(github_dir / 'ci.yml', content)
