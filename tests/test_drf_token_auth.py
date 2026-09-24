import tempfile
import unittest
from pathlib import Path

from modern_django_starter.generator import ProjectGenerator


class DRFTokenAuthenticationGenerationTests(unittest.TestCase):
    def test_drf_generation_includes_token_auth_app(self):
        config = {
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
            'api_only': False,
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            ProjectGenerator('test_project', tmp_dir, config).generate()

            settings_path = Path(tmp_dir) / 'test_project' / 'test_project' / 'settings' / 'base.py'
            settings = settings_path.read_text(encoding='utf-8')

        self.assertIn("'rest_framework',", settings)
        self.assertIn("'rest_framework.authtoken',", settings)
        self.assertIn(
            "'rest_framework.authentication.TokenAuthentication',",
            settings,
        )

    def test_api_only_generation_includes_allauth_account_middleware(self):
        config = {
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

        with tempfile.TemporaryDirectory() as tmp_dir:
            ProjectGenerator('test_api', tmp_dir, config).generate()

            settings_path = Path(tmp_dir) / 'test_api' / 'test_api' / 'settings' / 'base.py'
            settings = settings_path.read_text(encoding='utf-8')

        self.assertIn("'allauth',", settings)
        self.assertIn(
            "'allauth.account.middleware.AccountMiddleware',",
            settings,
        )


if __name__ == '__main__':
    unittest.main()
