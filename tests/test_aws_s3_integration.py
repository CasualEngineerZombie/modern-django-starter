"""Live S3 integration test for generated AWS-storage projects (kumo emulator).

The dependency tests in ``test_storage_dependencies.py`` prove an AWS-storage
project *installs*; this module proves it actually *talks to S3*. It generates
a project, points its ``AWS_S3_ENDPOINT_URL`` at the kumo AWS emulator, and
runs a real django-storages round trip (save -> open -> delete) through the
generated settings — the same code path production uses, minus real AWS.

Run locally against the compose kumo::

    docker compose -f docker-compose.act.yml up -d kumo
    RUN_DJANGO_INTEGRATION_TESTS=1 AWS_S3_ENDPOINT_URL=http://localhost:4566 \\
        uv run pytest -q tests/test_aws_s3_integration.py

The CI integration job starts kumo as a service container; ``act`` runs use
``.act.env`` to point at it. Skipped unless ``RUN_DJANGO_INTEGRATION_TESTS=1``
and an S3 endpoint is configured, so plain local and unit-CI runs stay
hermetic. With the endpoint set, the test waits up to 60s for the emulator to
answer before failing.

The round trip runs inside the generated project's virtual environment (which
installs boto3 via the generated requirements); this package itself never
depends on boto3.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from modern_django_starter.generator import ProjectGenerator

RUN_INTEGRATION = os.getenv('RUN_DJANGO_INTEGRATION_TESTS') == '1'

# The endpoint the generated project should talk to. Both host runs and act
# runs use localhost:4566 (the compose kumo); CI uses the service container.
S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL') or os.getenv('AWS_ENDPOINT_URL') or ''
S3_BUCKET = os.getenv('AWS_STORAGE_BUCKET_NAME', 'test-bucket')
S3_REGION = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
S3_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID', 'test')
S3_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'test')

AWS_CONFIG = {
    'use_docker': False,
    'use_postgresql': False,
    'cloud_provider': 'none',
    'storage_provider': 'aws',
    'email_provider': 'none',
    'use_async': False,
    'use_drf': False,
    'use_celery': False,
    'use_sentry': False,
    'use_stripe': False,
    'frontend_pipeline': 'none',
    'ci_tool': 'none',
    'api_only': False,
}


def project_env(project_name):
    return {
        **os.environ,
        'DJANGO_SETTINGS_MODULE': f'{project_name}.settings.development',
        'AWS_S3_ENDPOINT_URL': S3_ENDPOINT_URL,
        'AWS_STORAGE_BUCKET_NAME': S3_BUCKET,
        'AWS_S3_REGION_NAME': S3_REGION,
        'AWS_ACCESS_KEY_ID': S3_ACCESS_KEY,
        'AWS_SECRET_ACCESS_KEY': S3_SECRET_KEY,
    }


class AwsSettingsEndpointUnitTests(unittest.TestCase):
    """Generated AWS settings expose the S3-compatible endpoint knob."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def test_aws_settings_support_custom_endpoint(self):
        ProjectGenerator('endpoint_aws', self._tmp.name, dict(AWS_CONFIG)).generate()
        settings = (
            Path(self._tmp.name) / 'endpoint_aws' / 'endpoint_aws' / 'settings' / 'base.py'
        ).read_text(encoding='utf-8')
        self.assertIn(
            "AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL', default='') or None", settings
        )
        self.assertIn("'endpoint_url': AWS_S3_ENDPOINT_URL,", settings)


@unittest.skipUnless(RUN_INTEGRATION, 'set RUN_DJANGO_INTEGRATION_TESTS=1 to run')
@unittest.skipUnless(S3_ENDPOINT_URL, 'set AWS_S3_ENDPOINT_URL (kumo emulator) to run')
class KumoS3StorageIntegrationTests(unittest.TestCase):
    """A generated AWS-storage project round-trips files through the emulator."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tmp = tempfile.TemporaryDirectory()
        cls._tmp = tmp
        cls.addClassCleanup(tmp.cleanup)
        cls.root = Path(tmp.name)
        cls.project_name = 'kumo_aws'
        ProjectGenerator(cls.project_name, str(cls.root), dict(AWS_CONFIG)).generate()
        cls.project = cls.root / cls.project_name

        venv = cls.root / 'venv'
        result = subprocess.run(
            [sys.executable, '-m', 'venv', str(venv)],
            check=True,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f'venv creation failed:\n{result.stdout}{result.stderr}')
        cls.venv_python = venv / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')

        install = subprocess.run(
            [
                str(cls.venv_python),
                '-m',
                'pip',
                'install',
                '--quiet',
                '-r',
                str(cls.project / 'requirements' / 'development.txt'),
            ],
            capture_output=True,
            text=True,
        )
        if install.returncode != 0:
            raise RuntimeError(f'pip install failed:\n{install.stdout}{install.stderr}')

    @classmethod
    def _run_script(cls, name, body):
        script = cls.project / name
        script.write_text(body, encoding='utf-8')
        return subprocess.run(
            [str(cls.venv_python), str(script)],
            cwd=str(cls.project),
            env=project_env(cls.project_name),
            capture_output=True,
            text=True,
        )

    @classmethod
    def _ensure_bucket(cls):
        """Wait for the emulator, then create the target bucket if missing."""
        result = cls._run_script(
            '_kumo_setup.py',
            f"""
import os
import time

import boto3

s3 = boto3.client(
    's3',
    endpoint_url={S3_ENDPOINT_URL!r},
    region_name={S3_REGION!r},
    aws_access_key_id={S3_ACCESS_KEY!r},
    aws_secret_access_key={S3_SECRET_KEY!r},
)

deadline = time.time() + 60
while True:
    try:
        buckets = {{b['Name'] for b in s3.list_buckets()['Buckets']}}
        break
    except Exception as exc:
        if time.time() > deadline:
            raise SystemExit(f'kumo emulator not ready: {{exc}}')
        time.sleep(2)

bucket = {S3_BUCKET!r}
if bucket not in buckets:
    s3.create_bucket(Bucket=bucket)
print('KUMO_BUCKET_READY', bucket)
""",
        )
        if result.returncode != 0:
            raise RuntimeError(f'kumo setup failed:\n{result.stdout}{result.stderr}')

    def test_aws_storage_round_trips_through_emulator(self):
        self._ensure_bucket()
        result = self._run_script(
            '_kumo_roundtrip.py',
            """
import os

import django

django.setup()

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

content = b'hello from the kumo emulator'
name = default_storage.save('kumo-e2e/hello.txt', ContentFile(content))
try:
    with default_storage.open(name) as stored:
        data = stored.read()
    assert data == content, f'round trip content mismatch: {data!r}'
finally:
    default_storage.delete(name)
assert not default_storage.exists(name), 'file survived delete'
print('KUMO_ROUNDTRIP_OK', name)
""",
        )
        self.assertEqual(
            result.returncode,
            0,
            f'round trip failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}',
        )
        self.assertIn('KUMO_ROUNDTRIP_OK', result.stdout)


if __name__ == '__main__':
    unittest.main()
