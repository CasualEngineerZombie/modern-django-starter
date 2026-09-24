"""Generator for requirements files."""

from pathlib import Path

from .base import BaseGenerator


class RequirementsGenerator(BaseGenerator):
    """Generates requirements files (base, development, production)."""

    def generate(self) -> None:
        """Generate requirements files based on config."""
        self.log('📋 Creating requirements files...')

        requirements_dir = self.project_dir / 'requirements'
        requirements_dir.mkdir(exist_ok=True)

        if self.config.get('api_only'):
            self._generate_api_only_requirements(requirements_dir)
        else:
            self._generate_full_requirements(requirements_dir)

    def _generate_api_only_requirements(self, requirements_dir: Path) -> None:
        """Generate minimal requirements for API-only projects."""
        base_reqs = [
            'Django>=6.1',
            'djangorestframework',
            'django-cors-headers',
            'drf-spectacular',
            'djangorestframework-simplejwt',
            'dj-rest-auth',
            'django-allauth',
            # dj-rest-auth registration pulls in
            # allauth.socialaccount.providers.oauth2.client, which requires
            # requests at import time.
            'requests',
            'python-decouple',
        ]

        if self.config.get('use_postgresql'):
            base_reqs.append('psycopg2-binary')

        storage_provider = self.config.get('storage_provider', 'local')
        if storage_provider != 'local':
            base_reqs.append('django-storages')
            if storage_provider in ('aws', 'cloudflare-r2'):
                base_reqs.append('boto3')
            elif storage_provider == 'gcp':
                base_reqs.append('google-cloud-storage')
            elif storage_provider == 'azure':
                base_reqs.append('azure-storage-blob')

        # The shared settings templates emit Celery/Sentry configuration
        # for API-only projects too, so those packages must be installed
        # or ``manage.py check`` fails on the first import.
        if self.config.get('use_celery'):
            base_reqs.append('celery')
            base_reqs.append('redis')
        if self.config.get('use_sentry'):
            base_reqs.append('sentry-sdk')
        if self.config.get('use_stripe'):
            base_reqs.append('dj-stripe')
            base_reqs.append('stripe')

        self.write_file(
            requirements_dir / 'base.txt',
            '\n'.join(base_reqs) + '\n'
        )
        self.write_file(requirements_dir / 'development.txt', '-r base.txt\n')
        self.write_file(requirements_dir / 'production.txt', '-r base.txt\n')
        self.write_file(self.project_dir / 'requirements.txt', '-r requirements/development.txt\n')

    def _generate_full_requirements(self, requirements_dir: Path) -> None:
        """Generate requirements using templates for full projects."""
        # Base requirements
        content = self.render_template('requirements/base.txt.j2')
        self.write_file(requirements_dir / 'base.txt', content)

        # Development requirements
        content = self.render_template('requirements/development.txt.j2')
        self.write_file(requirements_dir / 'development.txt', content)

        # Production requirements
        content = self.render_template('requirements/production.txt.j2')
        self.write_file(requirements_dir / 'production.txt', content)

        # Main requirements.txt
        self.write_file(self.project_dir / 'requirements.txt', '-r requirements/development.txt\n')