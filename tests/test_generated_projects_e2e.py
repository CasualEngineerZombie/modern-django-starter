"""End-to-end generation tests for the major configuration matrix (issue #15).

The generator has many conditional branches (API-only, DRF, PostgreSQL,
Celery, Sentry, Stripe, storage providers, Docker, frontend pipelines, CI/cloud
options), and a syntax-valid template is not enough: a generated project can
contain incompatible settings, missing dependencies, missing files, or broken
imports.

For every representative configuration in the matrix this module:

1. Generates the project into a temporary directory.
2. Installs the generated dependencies into a fresh virtual environment.
3. Runs ``python manage.py check``.
4. Runs ``python manage.py migrate``.
5. Runs the generated project's own test suite.

PostgreSQL configurations cannot ``migrate`` without a live database server, so
they are validated with ``manage.py check`` (which never opens a DB connection)
and the Docker Compose validation below. Docker-enabled configurations are
validated with both a YAML parse and ``docker compose config`` whenever Docker
is available.

Skipped unless ``RUN_DJANGO_INTEGRATION_TESTS=1`` is set, mirroring the other
integration tests, because installing the generated dependencies downloads
packages into temporary virtual environments.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

import yaml

from modern_django_starter.generator import ProjectGenerator

RUN_INTEGRATION = os.getenv('RUN_DJANGO_INTEGRATION_TESTS') == '1'


def _sqlite_config(**overrides):
    """A shared baseline config: SQLite, local storage, no extras."""
    config = {
        'use_docker': False,
        'use_postgresql': False,
        'cloud_provider': 'none',
        'storage_provider': 'local',
        'email_provider': 'none',
        'use_async': False,
        'use_drf': True,
        'use_celery': False,
        'use_sentry': False,
        'use_stripe': False,
        'frontend_pipeline': 'none',
        'ci_tool': 'none',
        'api_only': False,
    }
    config.update(overrides)
    return config


# Runnable matrix: these projects must pass check, migrate, and their own
# test suite (SQLite so migrations can run without an external database).
MATRIX = [
    {
        'name': 'minimal',
        'project_name': 'e2e_minimal',
        'test_labels': ['apps.core', 'apps.accounts'],
        'config': _sqlite_config(use_drf=False),
    },
    {
        'name': 'full-default',
        'project_name': 'e2e_full_default',
        'test_labels': ['apps.core', 'apps.accounts', 'apps.api'],
        'config': _sqlite_config(
            use_docker=True,
            use_celery=True,
            use_sentry=True,
            frontend_pipeline='vite',
            ci_tool='github-actions',
        ),
    },
    {
        'name': 'api-only',
        'project_name': 'e2e_api_only',
        'test_labels': ['apps.api'],
        'config': _sqlite_config(api_only=True, use_docker=True, ci_tool='github-actions'),
    },
]

# Check-only matrix: feature-maximal PostgreSQL configurations that need a live
# database for migrate/test. They must still install cleanly and pass
# ``manage.py check``, which covers the settings/URL/requirements branches and
# dependency resolution without spinning up PostgreSQL.
CHECK_ONLY_MATRIX = [
    {
        'name': 'full-maximal',
        'project_name': 'e2e_full_maximal',
        'config': {
            'use_docker': True,
            'use_postgresql': True,
            'postgresql_version': '18',
            'cloud_provider': 'none',
            'storage_provider': 'aws',
            'email_provider': 'sendgrid',
            'use_async': True,
            'use_drf': True,
            'use_celery': True,
            'use_sentry': True,
            'use_stripe': True,
            'frontend_pipeline': 'vite',
            'ci_tool': 'github-actions',
            'api_only': False,
        },
    },
    {
        'name': 'api-only-maximal',
        'project_name': 'e2e_api_maximal',
        'config': {
            'use_docker': True,
            'use_postgresql': True,
            'postgresql_version': '16',
            'cloud_provider': 'none',
            'storage_provider': 'azure',
            'email_provider': 'mailgun',
            'use_async': True,
            'use_drf': True,
            'use_celery': True,
            'use_sentry': True,
            'use_stripe': False,
            'frontend_pipeline': 'none',
            'ci_tool': 'github-actions',
            'api_only': True,
        },
    },
]

DOCKER_ENTRIES = [
    entry for entry in MATRIX + CHECK_ONLY_MATRIX if entry['config'].get('use_docker')
]

MATRIX_BY_NAME = {entry['name']: entry for entry in MATRIX + CHECK_ONLY_MATRIX}

# PostgreSQL configuration booted against a real database by
# PostgresProjectIntegrationTests (not part of MATRIX/CHECK_ONLY_MATRIX, which
# share one virtualenv and cannot migrate without a live database server).
POSTGRES_ENTRY = {
    'name': 'postgres',
    'project_name': 'e2e_postgres',
    'test_labels': ['apps.core', 'apps.accounts', 'apps.api'],
    'config': _sqlite_config(
        use_docker=True,
        use_postgresql=True,
        postgresql_version='18',
        use_celery=True,
        use_sentry=True,
        use_async=True,
        frontend_pipeline='vite',
        ci_tool='github-actions',
    ),
}


def _venv_python(venv_dir):
    return venv_dir / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def _run_command(*args, cwd=None, env=None):
    """Run a subprocess and return the completed process."""
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=str(cwd) if cwd else None,
        env=env,
        capture_output=True,
        text=True,
    )


def _generate(entry, output_dir):
    """Generate one matrix entry and return the project directory."""
    ProjectGenerator(entry['project_name'], str(output_dir), dict(entry['config'])).generate()
    return Path(output_dir) / entry['project_name']


class DockerComposeYamlUnitTests(unittest.TestCase):
    """docker-compose.yml for every Docker-enabled matrix entry is valid YAML.

    This runs without the integration flag so the default test suite always
    covers the compose template branches; ``docker compose config`` itself is
    checked by the gated integration test below.
    """

    def test_docker_compose_files_are_valid_yaml(self):
        for entry in DOCKER_ENTRIES:
            with self.subTest(name=entry['name']):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    project = _generate(entry, tmp_dir)
                    data = yaml.safe_load(
                        (project / 'docker-compose.yml').read_text(encoding='utf-8')
                    )
                    self.assertIn('web', data['services'])
                    self.assertEqual(data['services']['web']['build'], '.')
                    if entry['config'].get('use_postgresql'):
                        self.assertIn('db', data['services'])
                    if entry['config'].get('use_celery'):
                        self.assertIn('redis', data['services'])


class GeneratedProjectRegressionUnitTests(unittest.TestCase):
    """Fast generation checks that lock in fixes uncovered by the E2E matrix.

    The integration matrix needs ``RUN_DJANGO_INTEGRATION_TESTS=1``, so these
    cheap checks pin the behaviors the matrix depends on: generated
    requirements must be installable next to Django 6.1, and generated
    docker-compose.yml files must be accepted by ``docker compose``.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def generate(self, name, config):
        entry = {'name': name, 'project_name': name, 'config': config}
        return _generate(entry, self._tmp.name)

    def read(self, project, rel_path):
        return (project / rel_path).read_text(encoding='utf-8')

    def test_celery_requirements_stay_compatible_with_django_61(self):
        project = self.generate('celery_full', _sqlite_config(use_celery=True))
        base = self.read(project, 'requirements/base.txt')
        # django-celery-beat/django-celery-results must not be emitted: the
        # latest django-celery-beat caps at Django<6.1 and cannot be installed
        # next to the generated Django==6.1.1.
        self.assertNotIn('django-celery-beat==', base)
        self.assertNotIn('django-celery-results==', base)
        self.assertIn('celery==5.4.0', base)
        self.assertIn('redis==5.2.1', base)
        settings = self.read(project, 'celery_full/settings/base.py')
        self.assertNotIn('django_celery_beat', settings)
        self.assertNotIn('django_celery_results', settings)

    def test_api_only_requirements_include_celery_and_sentry(self):
        project = self.generate(
            'api_celery', _sqlite_config(api_only=True, use_celery=True, use_sentry=True)
        )
        base = self.read(project, 'requirements/base.txt')
        for dep in ('celery', 'redis', 'sentry-sdk'):
            self.assertIn(dep, base)

    def test_docker_compose_omits_depends_on_without_db_or_broker(self):
        project = self.generate('api_compose', _sqlite_config(api_only=True, use_docker=True))
        data = yaml.safe_load(self.read(project, 'docker-compose.yml'))
        self.assertNotIn('depends_on', data['services']['web'])

    def test_docker_compose_includes_depends_on_for_db_and_broker(self):
        project = self.generate(
            'full_compose',
            _sqlite_config(
                use_docker=True, use_postgresql=True, postgresql_version='18', use_celery=True
            ),
        )
        data = yaml.safe_load(self.read(project, 'docker-compose.yml'))
        self.assertEqual(set(data['services']['web']['depends_on']), {'db', 'redis'})

    def test_api_only_stripe_is_not_emitted(self):
        project = self.generate('api_stripe', _sqlite_config(api_only=True, use_stripe=True))
        settings = self.read(project, 'api_stripe/settings/base.py')
        urls = self.read(project, 'api_stripe/urls.py')
        # API-only projects have no frontend checkout flow, so Stripe must not
        # add djstripe/payments references that would fail at import time.
        self.assertNotIn('djstripe', settings)
        self.assertNotIn('payments', urls)

    def test_postgres_18_compose_mounts_version_aware_data_dir(self):
        # The postgres:18+ image refuses to start when data is mounted at the
        # legacy /var/lib/postgresql/data path; it requires the volume at
        # /var/lib/postgresql so it can create a version-specific subdirectory.
        pg18 = self.generate(
            'pg18', _sqlite_config(use_docker=True, use_postgresql=True, postgresql_version='18')
        )
        data18 = yaml.safe_load(self.read(pg18, 'docker-compose.yml'))
        self.assertEqual(data18['services']['db']['volumes'], ['postgres_data:/var/lib/postgresql'])

        # Pre-18 images keep the historical data-directory layout.
        pg16 = self.generate(
            'pg16', _sqlite_config(use_docker=True, use_postgresql=True, postgresql_version='16')
        )
        data16 = yaml.safe_load(self.read(pg16, 'docker-compose.yml'))
        self.assertEqual(
            data16['services']['db']['volumes'], ['postgres_data:/var/lib/postgresql/data/']
        )


@unittest.skipUnless(RUN_INTEGRATION, 'set RUN_DJANGO_INTEGRATION_TESTS=1 to run')
class GeneratedProjectMatrixIntegrationTests(unittest.TestCase):
    """Boot the generated projects for every matrix configuration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tmp = tempfile.TemporaryDirectory()
        cls._tmp = tmp
        cls.addClassCleanup(tmp.cleanup)
        cls.root = Path(tmp.name)
        cls.projects = {}

        venv = cls.root / 'venv'
        result = _run_command(sys.executable, '-m', 'venv', venv)
        if result.returncode != 0:
            raise RuntimeError(f'venv creation failed:\n{result.stdout}{result.stderr}')
        cls.venv_python = _venv_python(venv)

        for entry in MATRIX + CHECK_ONLY_MATRIX:
            project = _generate(entry, cls.root / entry['name'])
            cls.projects[entry['name']] = project
            install = _run_command(
                cls.venv_python,
                '-m',
                'pip',
                'install',
                '--quiet',
                '-r',
                project / 'requirements' / 'development.txt',
            )
            if install.returncode != 0:
                raise RuntimeError(
                    f'pip install failed for {entry["name"]}:\n{install.stdout}{install.stderr}'
                )

    def _run_manage(self, name, *args):
        entry = MATRIX_BY_NAME[name]
        env = {
            **os.environ,
            'DJANGO_SETTINGS_MODULE': f'{entry["project_name"]}.settings.development',
        }
        result = _run_command(
            self.venv_python, 'manage.py', *args, cwd=self.projects[name], env=env
        )
        self.assertEqual(
            result.returncode,
            0,
            f'{name}: python manage.py {" ".join(args)}:\n'
            f'STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}',
        )
        return result

    def _assert_boots(self, name):
        """A runnable project must pass check, migrate, and its test suite."""
        entry = MATRIX_BY_NAME[name]
        self._run_manage(name, 'check')
        self._run_manage(name, 'migrate', '--noinput')
        for label in entry['test_labels']:
            self._run_manage(name, 'test', label)

    def test_minimal_generated_project_boots(self):
        self._assert_boots('minimal')

    def test_full_default_generated_project_boots(self):
        self._assert_boots('full-default')

    def test_api_only_generated_project_boots(self):
        self._assert_boots('api-only')

    def test_full_maximal_passes_manage_check(self):
        self._run_manage('full-maximal', 'check')

    def test_api_only_maximal_passes_manage_check(self):
        self._run_manage('api-only-maximal', 'check')


@unittest.skipUnless(RUN_INTEGRATION, 'set RUN_DJANGO_INTEGRATION_TESTS=1 to run')
class DockerComposeConfigIntegrationTests(unittest.TestCase):
    """``docker compose config`` accepts every generated Docker setup."""

    @unittest.skipUnless(shutil.which('docker'), 'docker is not available')
    def test_docker_compose_config_validates(self):
        for entry in DOCKER_ENTRIES:
            with self.subTest(name=entry['name']):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    project = _generate(entry, tmp_dir)
                    result = _run_command(
                        'docker',
                        'compose',
                        '-f',
                        project / 'docker-compose.yml',
                        'config',
                        '--quiet',
                        cwd=project,
                    )
                    self.assertEqual(result.returncode, 0, f'{result.stdout}{result.stderr}')


@unittest.skipUnless(RUN_INTEGRATION, 'set RUN_DJANGO_INTEGRATION_TESTS=1 to run')
@unittest.skipUnless(shutil.which('docker'), 'docker is not available')
class PostgresProjectIntegrationTests(unittest.TestCase):
    """A PostgreSQL configuration boots against a real database.

    The generated project ships its own ``db`` service, so this test starts it
    from the generated ``docker-compose.yml`` and runs check, migrations, and
    the generated test suite against live PostgreSQL. This proves the
    PostgreSQL settings, the psycopg2 dependency, and the generated migrations
    are sound end to end.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tmp = tempfile.TemporaryDirectory()
        cls._tmp = tmp
        cls.addClassCleanup(tmp.cleanup)
        cls.root = Path(tmp.name)
        cls.project = _generate(POSTGRES_ENTRY, cls.root)

        venv = cls.root / 'venv'
        result = _run_command(sys.executable, '-m', 'venv', venv)
        if result.returncode != 0:
            raise RuntimeError(f'venv creation failed:\n{result.stdout}{result.stderr}')
        cls.venv_python = _venv_python(venv)
        install = _run_command(
            cls.venv_python,
            '-m',
            'pip',
            'install',
            '--quiet',
            '-r',
            cls.project / 'requirements' / 'development.txt',
        )
        if install.returncode != 0:
            raise RuntimeError(f'pip install failed:\n{install.stdout}{install.stderr}')

        cls.compose_file = cls.project / 'docker-compose.yml'
        cls._compose = ['docker', 'compose', '-f', cls.compose_file]
        up = _run_command(*cls._compose, 'up', '-d', 'db')
        if up.returncode != 0:
            raise RuntimeError(f'docker compose up db failed:\n{up.stdout}{up.stderr}')
        cls.addClassCleanup(_run_command, *cls._compose, 'down', '-v')
        _wait_for_healthy(cls._compose)

    def _manage(self, *args):
        env = {
            **os.environ,
            'DJANGO_SETTINGS_MODULE': f'{POSTGRES_ENTRY["project_name"]}.settings.development',
            # The generated compose file publishes the db service on the host.
            'DB_NAME': POSTGRES_ENTRY['project_name'],
            'DB_USER': 'postgres',
            'DB_PASSWORD': 'postgres',
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
        }
        result = _run_command(self.venv_python, 'manage.py', *args, cwd=self.project, env=env)
        self.assertEqual(
            result.returncode,
            0,
            f'postgres: python manage.py {" ".join(args)}:\n'
            f'STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}',
        )
        return result

    def test_postgres_project_migrates_and_runs_tests(self):
        self._manage('check')
        self._manage('migrate', '--noinput')
        for label in POSTGRES_ENTRY['test_labels']:
            self._manage('test', label)


def _wait_for_healthy(compose_args, timeout=120):
    """Wait until the ``db`` service health check reports healthy."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        cid = _run_command(*compose_args, 'ps', '-q', 'db')
        container_id = cid.stdout.strip()
        if container_id:
            status = _run_command(
                'docker', 'inspect', '--format', '{{.State.Health.Status}}', container_id
            )
            state = status.stdout.strip()
            if state == 'healthy':
                return
            if state == 'unhealthy':
                raise RuntimeError(f'db service unhealthy: {status.stderr}')
        time.sleep(2)
    raise RuntimeError(f'timed out after {timeout}s waiting for db service to be healthy')


if __name__ == '__main__':
    unittest.main()
