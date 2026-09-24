"""Integration test for the API-only generator path (issue #11).

Generates a real API-only project, installs its requirements into a fresh
virtual environment, and runs ``manage.py check`` and ``manage.py migrate`` to
prove the generated settings/URLs/requirements are consistent with Django 6.1
and the pinned dependencies.

Skipped unless ``RUN_DJANGO_INTEGRATION_TESTS=1`` is set, because it downloads
and installs packages into a temporary virtual environment.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from modern_django_starter.generator import ProjectGenerator

RUN_INTEGRATION = os.getenv('RUN_DJANGO_INTEGRATION_TESTS') == '1'

API_ONLY_CONFIG = {
    'use_docker': False,
    'use_postgresql': False,
    'storage_provider': 'local',
    'email_provider': 'none',
    'use_async': False,
    'use_drf': True,
    'use_celery': False,
    'use_sentry': False,
    'use_stripe': False,
    'frontend_pipeline': 'none',
    'ci_tool': 'none',
    'api_only': True,
}


@unittest.skipUnless(RUN_INTEGRATION, 'set RUN_DJANGO_INTEGRATION_TESTS=1 to run')
class APIOnlyIntegrationTests(unittest.TestCase):
    def test_generated_api_only_project_passes_check_and_migrate(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            ProjectGenerator('test_api', tmp_dir, dict(API_ONLY_CONFIG)).generate()
            project_dir = Path(tmp_dir) / 'test_api'

            # Create a fresh virtual environment and install the generated
            # requirements to keep the current environment untouched.
            venv_dir = Path(tmp_dir) / 'venv'
            subprocess.run(
                [sys.executable, '-m', 'venv', str(venv_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
            python = venv_dir / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
            subprocess.run(
                [
                    str(python),
                    '-m',
                    'pip',
                    'install',
                    '--quiet',
                    '-r',
                    str(project_dir / 'requirements' / 'base.txt'),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            env = {**os.environ, 'DJANGO_SETTINGS_MODULE': 'test_api.settings.development'}

            check = subprocess.run(
                [str(python), 'manage.py', 'check'],
                cwd=str(project_dir),
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

            migrate = subprocess.run(
                [str(python), 'manage.py', 'migrate', '--noinput'],
                cwd=str(project_dir),
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(migrate.returncode, 0, migrate.stdout + migrate.stderr)
            self.assertIn('Running migrations', migrate.stdout)


if __name__ == '__main__':
    unittest.main()
