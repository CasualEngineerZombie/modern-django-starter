"""Unit tests for the hardened API-only generator path (issue #11).

The ``--api-only`` path previously emitted hard-coded settings/URL strings and
defaulted ``DEBUG`` to on, opened CORS to every origin, and used legacy allauth
configuration. These tests assert that API-only projects now reuse the shared
Jinja2 settings/URL templates and inherit the hardened defaults (MAILERS,
modern allauth config, JWT auth, allowlisted CORS, DEBUG off in production).
"""

import tempfile
import unittest
from pathlib import Path

from modern_django_starter.generator import ProjectGenerator

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


class APIOnlyHardeningTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        ProjectGenerator('test_api', self._tmp.name, dict(API_ONLY_CONFIG)).generate()
        self.project = Path(self._tmp.name) / 'test_api'
        self.pkg = self.project / 'test_api'

    def read(self, rel_path):
        return (self.pkg / rel_path).read_text(encoding='utf-8')

    # --- Settings layout --------------------------------------------------

    def test_settings_reuse_the_three_module_layout(self):
        base = self.read('settings/base.py')
        dev = self.read('settings/development.py')
        prod = self.read('settings/production.py')
        # Development forces DEBUG on; production forces it off.
        self.assertIn('DEBUG = True', dev)
        self.assertIn('DEBUG = False', prod)
        # The three modules are no longer identical copies.
        self.assertNotEqual(dev, base)
        self.assertNotEqual(prod, base)

    def test_base_settings_read_configuration_via_decouple(self):
        base = self.read('settings/base.py')
        self.assertIn('from decouple import config, Csv', base)
        self.assertIn(
            "config('SECRET_KEY', default='django-insecure-change-me-in-production')", base
        )

    def test_base_settings_default_debug_to_off(self):
        base = self.read('settings/base.py')
        self.assertIn("DEBUG = config('DEBUG', default=False, cast=bool)", base)

    def test_base_settings_define_django_61_mailers(self):
        base = self.read('settings/base.py')
        self.assertIn('MAILERS = {', base)
        self.assertNotIn('EMAIL_BACKEND', base)

    def test_base_settings_use_modern_allauth_configuration(self):
        base = self.read('settings/base.py')
        self.assertIn('ACCOUNT_LOGIN_METHODS', base)
        self.assertIn('ACCOUNT_SIGNUP_FIELDS', base)
        self.assertIn('allauth.account.middleware.AccountMiddleware', base)

    def test_base_settings_include_sites_for_allauth(self):
        base = self.read('settings/base.py')
        self.assertIn("'django.contrib.sites',", base)
        self.assertIn('SITE_ID = 1', base)

    def test_base_settings_use_jwt_auth_and_spectacular(self):
        base = self.read('settings/base.py')
        self.assertIn("'rest_framework_simplejwt.authentication.JWTAuthentication',", base)
        self.assertIn("'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema'", base)
        self.assertIn('SPECTACULAR_SETTINGS = {', base)
        self.assertIn("'USE_JWT': True", base)
        self.assertIn("'TOKEN_MODEL': None", base)

    def test_base_settings_do_not_allow_all_cors_origins(self):
        base = self.read('settings/base.py')
        self.assertNotIn('CORS_ALLOW_ALL_ORIGINS', base)
        self.assertIn(
            "CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=Csv())",
            base,
        )

    def test_base_settings_omit_full_mode_only_apps(self):
        base = self.read('settings/base.py')
        self.assertNotIn("'rest_framework.authtoken',", base)
        self.assertNotIn("'widget_tweaks',", base)
        self.assertNotIn("'apps.core',", base)
        self.assertNotIn("'apps.accounts',", base)
        self.assertIn("'drf_spectacular',", base)
        self.assertIn("'dj_rest_auth',", base)
        self.assertIn("'apps.api',", base)

    def test_development_settings_skip_frontend_debug_tooling(self):
        dev = self.read('settings/development.py')
        self.assertNotIn('debug_toolbar', dev)
        self.assertNotIn('django_extensions', dev)

    def test_production_settings_force_secure_defaults(self):
        prod = self.read('settings/production.py')
        self.assertIn('SECURE_SSL_REDIRECT = True', prod)
        self.assertIn('SESSION_COOKIE_SECURE = True', prod)
        self.assertIn('CSRF_COOKIE_SECURE = True', prod)

    # --- URLs -------------------------------------------------------------

    def test_urls_include_api_only_endpoints(self):
        urls = self.read('urls.py')
        for fragment in [
            'from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView',
            'from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView',
            "path('api/schema/', SpectacularAPIView.as_view(), name='schema')",
            "path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui')",
            "path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair')",
            "path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh')",
            "path('api/auth/', include('dj_rest_auth.urls'))",
            "path('api/auth/registration/', include('dj_rest_auth.registration.urls'))",
            "path('api/', include('apps.api.urls'))",
        ]:
            self.assertIn(fragment, urls)
        self.assertNotIn('apps.core.urls', urls)

    # --- Requirements -----------------------------------------------------

    def test_requirements_include_decouple_and_django_61(self):
        base_txt = (self.project / 'requirements' / 'base.txt').read_text(encoding='utf-8')
        self.assertIn('Django>=6.1', base_txt)
        self.assertIn('python-decouple', base_txt)


if __name__ == '__main__':
    unittest.main()
