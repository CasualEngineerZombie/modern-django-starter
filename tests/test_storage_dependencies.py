"""Generation tests for cloud storage dependencies (issue #13).

The generator adds ``'storages'`` to ``INSTALLED_APPS`` and emits
provider-specific ``STORAGES`` backends for non-local providers, so generated
projects must install ``django-storages`` plus the provider SDK in *every*
environment (base requirements feed development and production). Earlier
versions only pinned those packages in ``production.txt.j2``, so a fresh
project failed ``python manage.py check`` with ``ModuleNotFoundError:
No module named 'storages'``.

These tests generate projects for every supported provider and assert the
generated requirements contain exactly the packages the selected backend needs,
and that the generated settings reference the matching backend.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from modern_django_starter.generator import ProjectGenerator

RUN_INTEGRATION = os.getenv('RUN_DJANGO_INTEGRATION_TESTS') == '1'

# provider -> (expected deps in base.txt, STORAGES backend, SDK package names)
EXPECTED = {
    'local': (
        [],
        'django.core.files.storage.FileSystemStorage',
        [],
    ),
    'aws': (
        ['django-storages==1.14.4', 'boto3==1.35.95'],
        'storages.backends.s3.S3Storage',
        ['boto3'],
    ),
    'cloudflare-r2': (
        ['django-storages==1.14.4', 'boto3==1.35.95'],
        'storages.backends.s3.S3Storage',
        ['boto3'],
    ),
    'gcp': (
        ['django-storages==1.14.4', 'google-cloud-storage==2.18.2'],
        'storages.backends.gcloud.GoogleCloudStorage',
        ['google-cloud-storage'],
    ),
    'azure': (
        ['django-storages==1.14.4', 'azure-storage-blob==12.24.0'],
        'storages.backends.azure_storage.AzureStorage',
        ['azure-storage-blob'],
    ),
}

ALL_SDKS = ['boto3', 'google-cloud-storage', 'azure-storage-blob']


def full_mode_config(storage_provider):
    return {
        'use_docker': False,
        'use_postgresql': False,
        'cloud_provider': 'none',
        'storage_provider': storage_provider,
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


def api_only_config(storage_provider):
    return {
        'use_docker': False,
        'use_postgresql': False,
        'cloud_provider': 'none',
        'storage_provider': storage_provider,
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


class StorageDependencyGenerationTests(unittest.TestCase):
    """Generated requirements match the selected storage provider (full mode)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def generate(self, storage_provider, config_builder):
        ProjectGenerator('test_storage', self._tmp.name, config_builder(storage_provider)).generate()
        self.project = Path(self._tmp.name) / 'test_storage'
        self.pkg = self.project / 'test_storage'

    def read_requirements(self, name):
        return (self.project / 'requirements' / name).read_text(encoding='utf-8')

    def read_settings(self):
        return (self.pkg / 'settings' / 'base.py').read_text(encoding='utf-8')

    def assert_full_mode_requirements(self, provider):
        expected_deps, backend, sdks = EXPECTED[provider]
        self.generate(provider, full_mode_config)

        base_txt = self.read_requirements('base.txt')
        dev_txt = self.read_requirements('development.txt')
        prod_txt = self.read_requirements('production.txt')
        settings = self.read_settings()

        # base.txt (feeds development and production) carries the storage stack.
        for dep in expected_deps:
            self.assertIn(dep, base_txt, f'{dep} missing from base.txt for {provider}')
        for sdk in set(ALL_SDKS) - set(sdks):
            self.assertNotIn(sdk, base_txt, f'unexpected {sdk} in base.txt for {provider}')

        # Production factors through base and never re-pins the storage stack.
        self.assertIn('-r base.txt', dev_txt)
        self.assertIn('-r base.txt', prod_txt)
        self.assertNotIn('django-storages==1.14.4', prod_txt, 'production.txt re-pins django-storages')
        for sdk in ALL_SDKS:
            self.assertNotIn(f'{sdk}==', prod_txt, f'production.txt re-pins {sdk}')

        # Settings reference the backend for the selected provider only.
        self.assertIn(f"'{backend}'", settings)

    def test_full_mode_local_installs_no_storage_packages(self):
        self.assert_full_mode_requirements('local')

    def test_full_mode_aws_installs_storages_and_boto3(self):
        self.assert_full_mode_requirements('aws')

    def test_full_mode_cloudflare_r2_installs_storages_and_boto3(self):
        self.assert_full_mode_requirements('cloudflare-r2')

    def test_full_mode_gcp_installs_storages_and_google_cloud_storage(self):
        self.assert_full_mode_requirements('gcp')

    def test_full_mode_azure_installs_storages_and_azure_blob(self):
        self.assert_full_mode_requirements('azure')

    def test_full_mode_installed_apps_include_storages_only_for_cloud(self):
        expected_deps, backend, sdks = EXPECTED['aws']
        self.generate('aws', full_mode_config)
        self.assertIn("'storages',", self.read_settings())

    def test_full_mode_installed_apps_omit_storages_for_local(self):
        self.generate('local', full_mode_config)
        self.assertNotIn("'storages',", self.read_settings())

    def test_full_mode_gcp_settings_do_not_require_credentials_at_import(self):
        self.generate('gcp', full_mode_config)
        settings = self.read_settings()
        self.assertIn('GOOGLE_APPLICATION_CREDENTIALS = config(', settings)
        self.assertIn('GS_CREDENTIALS = None', settings)
        self.assertIn('if GOOGLE_APPLICATION_CREDENTIALS:', settings)


class APIOnlyStorageDependencyTests(unittest.TestCase):
    """The API-only requirement path is also storage-aware (issue #13)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def generate(self, storage_provider):
        ProjectGenerator(
            'test_storage_api', self._tmp.name, api_only_config(storage_provider)
        ).generate()
        self.project = Path(self._tmp.name) / 'test_storage_api'

    def read_base_txt(self):
        return (self.project / 'requirements' / 'base.txt').read_text(encoding='utf-8')

    def test_api_only_local_installs_no_storage_packages(self):
        self.generate('local')
        base_txt = self.read_base_txt()
        self.assertNotIn('django-storages', base_txt)
        for sdk in ALL_SDKS:
            self.assertNotIn(sdk, base_txt)

    def test_api_only_aws_installs_storages_and_boto3(self):
        self.generate('aws')
        base_txt = self.read_base_txt()
        self.assertIn('django-storages', base_txt)
        self.assertIn('boto3', base_txt)
        self.assertNotIn('google-cloud-storage', base_txt)
        self.assertNotIn('azure-storage-blob', base_txt)

    def test_api_only_cloudflare_r2_installs_storages_and_boto3(self):
        self.generate('cloudflare-r2')
        base_txt = self.read_base_txt()
        self.assertIn('django-storages', base_txt)
        self.assertIn('boto3', base_txt)

    def test_api_only_gcp_installs_storages_and_google_cloud_storage(self):
        self.generate('gcp')
        base_txt = self.read_base_txt()
        self.assertIn('django-storages', base_txt)
        self.assertIn('google-cloud-storage', base_txt)
        self.assertNotIn('boto3', base_txt)
        self.assertNotIn('azure-storage-blob', base_txt)

    def test_api_only_azure_installs_storages_and_azure_blob(self):
        self.generate('azure')
        base_txt = self.read_base_txt()
        self.assertIn('django-storages', base_txt)
        self.assertIn('azure-storage-blob', base_txt)
        self.assertNotIn('boto3', base_txt)
        self.assertNotIn('google-cloud-storage', base_txt)


@unittest.skipUnless(RUN_INTEGRATION, 'set RUN_DJANGO_INTEGRATION_TESTS=1 to run')
class StorageIntegrationTests(unittest.TestCase):
    """Generated cloud-storage projects pass ``manage.py check`` (issue #13)."""

    def test_cloud_storage_projects_pass_manage_check(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects = {}
            for provider in ('aws', 'cloudflare-r2', 'gcp', 'azure'):
                project_dir = Path(tmp_dir) / provider
                ProjectGenerator(provider, tmp_dir, full_mode_config(provider)).generate()
                projects[provider] = project_dir

            venv_dir = Path(tmp_dir) / 'venv'
            subprocess.run(
                [sys.executable, '-m', 'venv', str(venv_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
            python = venv_dir / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')

            for project_dir in projects.values():
                subprocess.run(
                    [
                        str(python),
                        '-m',
                        'pip',
                        'install',
                        '--quiet',
                        # development.txt references base.txt and adds the tools
                        # the development settings import (debug-toolbar, ...).
                        '-r',
                        str(project_dir / 'requirements' / 'development.txt'),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )

            for provider, project_dir in projects.items():
                env = {
                    **os.environ,
                    'DJANGO_SETTINGS_MODULE': f'{provider}.settings.development',
                }
                check = subprocess.run(
                    [str(python), 'manage.py', 'check'],
                    cwd=str(project_dir),
                    env=env,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    check.returncode, 0, f'{provider}: {check.stdout} {check.stderr}'
                )


if __name__ == '__main__':
    unittest.main()