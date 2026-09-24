"""Tests for the Stripe webhook secret mismatch (issue #14).

The generated settings defined ``DJSTRIPE_WEBHOOK_SECRET`` but the generated
webhook view read ``settings.STRIPE_WEBHOOK_SECRET``, and the environment
template advertised both variables — so the webhook endpoint could blow up at
runtime with an ``AttributeError``. These tests pin the canonical name
``DJSTRIPE_WEBHOOK_SECRET`` (dj-stripe's own convention) across the env
template, settings, webhook view, and documentation, and prove end-to-end that
a signed ``checkout.session.completed`` payload flips an order to
``completed``.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from modern_django_starter.generator import ProjectGenerator

RUN_INTEGRATION = os.getenv('RUN_DJANGO_INTEGRATION_TESTS') == '1'

STRIPE_CONFIG = {
    'use_docker': False,
    'use_postgresql': False,
    'cloud_provider': 'none',
    'storage_provider': 'local',
    'email_provider': 'none',
    'use_async': False,
    'use_drf': True,
    'use_celery': False,
    'use_sentry': False,
    'use_stripe': True,
    'frontend_pipeline': 'none',
    'ci_tool': 'none',
    'api_only': False,
}

SETTINGS_SECRET_LINE = "DJSTRIPE_WEBHOOK_SECRET = config('DJSTRIPE_WEBHOOK_SECRET', default='')"
VIEW_SECRET_LINE = '        endpoint_secret = settings.DJSTRIPE_WEBHOOK_SECRET'


class StripeWebhookSecretGenerationTests(unittest.TestCase):
    """Generated files agree on the canonical webhook secret name."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        ProjectGenerator('test_stripe', self._tmp.name, dict(STRIPE_CONFIG)).generate()
        self.project = Path(self._tmp.name) / 'test_stripe'
        self.pkg = self.project / 'test_stripe'

    def read_lines(self, rel_path):
        return (self.pkg / rel_path).read_text(encoding='utf-8').splitlines()

    def read_views(self):
        return (
            (self.project / 'apps' / 'payments' / 'views.py')
            .read_text(encoding='utf-8')
            .splitlines()
        )

    def read_project_file(self, rel_path):
        return (self.project / rel_path).read_text(encoding='utf-8').splitlines()

    def test_settings_define_the_canonical_secret(self):
        lines = self.read_lines('settings/base.py')
        self.assertIn(SETTINGS_SECRET_LINE, lines)
        self.assertFalse(
            [line for line in lines if line.startswith('STRIPE_WEBHOOK_SECRET')],
            'settings still defines a bare STRIPE_WEBHOOK_SECRET',
        )

    def test_webhook_view_reads_the_canonical_secret(self):
        lines = self.read_views()
        self.assertIn(VIEW_SECRET_LINE, lines)
        self.assertFalse(
            [line for line in lines if 'settings.STRIPE_WEBHOOK_SECRET' in line],
            'webhook view still reads settings.STRIPE_WEBHOOK_SECRET',
        )

    def test_env_example_exposes_a_single_webhook_secret(self):
        lines = self.read_project_file('.env.example')
        self.assertIn('DJSTRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret', lines)
        self.assertFalse(
            [line for line in lines if line.startswith('STRIPE_WEBHOOK_SECRET=')],
            '.env.example still lists STRIPE_WEBHOOK_SECRET',
        )

    def test_readme_references_a_single_webhook_secret(self):
        lines = self.read_project_file('README.md')
        self.assertTrue(
            any('Copy webhook secret to `DJSTRIPE_WEBHOOK_SECRET`' in line for line in lines),
            'README does not document DJSTRIPE_WEBHOOK_SECRET',
        )
        self.assertFalse(
            [line for line in lines if line.startswith('- `STRIPE_WEBHOOK_SECRET`')],
            'README still documents STRIPE_WEBHOOK_SECRET',
        )

    def test_urls_register_the_debug_toolbar_namespace(self):
        # The dev settings add debug_toolbar, so its URL namespace must be wired
        # or the toolbar crashes on every response in development.
        lines = self.read_lines('urls.py')
        self.assertTrue(
            any("path('__debug__/', include('debug_toolbar.urls'))" in line for line in lines),
            'urls.py does not wire the debug_toolbar namespace',
        )


WEBHOOK_TEST_SCRIPT = """\
import hashlib
import hmac
import json
import os
import time

os.environ['DJANGO_SETTINGS_MODULE'] = 'test_stripe_payments.settings.development'
os.environ['DJSTRIPE_WEBHOOK_SECRET'] = 'whsec_test_secret'

import django

django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client

from apps.payments.models import Order

assert settings.DJSTRIPE_WEBHOOK_SECRET == 'whsec_test_secret'

# bulk_create avoids the post_save signal that would sync a Stripe Customer.
user = User.objects.bulk_create([User(username='webhook_user', email='wh@example.com')])[0]
order = Order.objects.create(user=user, total_amount=29.99, currency='USD')
assert order.status == 'pending'

payload = json.dumps({
    'id': 'evt_test_123',
    'object': 'event',
    'type': 'checkout.session.completed',
    'data': {
        'object': {
            'id': 'cs_test_123',
            'object': 'checkout.session',
            'metadata': {'order_id': str(order.id)},
        },
    },
}).encode('utf-8')

# Build the Stripe-Signature header the way Stripe does: the HMAC-SHA256 is
# computed over "{timestamp}.{payload}" with the webhook secret;
# stripe.Webhook.construct_event verifies against it on the server side.
timestamp = int(time.time())
signed_payload = f'{timestamp}.'.encode() + payload
signature = 't={},v1={}'.format(
    timestamp,
    hmac.new(
        settings.DJSTRIPE_WEBHOOK_SECRET.encode(), signed_payload, hashlib.sha256
    ).hexdigest(),
)

import stripe  # noqa: E402

# Sanity-check the signature against the payload locally, before transport.
stripe.Webhook.construct_event(payload, signature, settings.DJSTRIPE_WEBHOOK_SECRET)

response = Client().post(
    '/payments/webhook/',
    data=payload,
    content_type='application/json',
    HTTP_STRIPE_SIGNATURE=signature,
)
assert response.status_code == 200, response.content

order.refresh_from_db()
assert order.status == 'completed', order.status

print('WEBHOOK_TEST_PASSED')
"""


@unittest.skipUnless(RUN_INTEGRATION, 'set RUN_DJANGO_INTEGRATION_TESTS=1 to run')
class StripeWebhookIntegrationTests(unittest.TestCase):
    """A signed webhook payload updates the order (issue #14)."""

    def test_signed_webhook_payload_updates_order(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_name = 'test_stripe_payments'
            ProjectGenerator(project_name, tmp_dir, dict(STRIPE_CONFIG)).generate()
            project_dir = Path(tmp_dir) / project_name

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
                    str(project_dir / 'requirements' / 'development.txt'),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            env = {
                **os.environ,
                'DJANGO_SETTINGS_MODULE': f'{project_name}.settings.development',
                # Django's test client sends Host: testserver, which the
                # generated ALLOWED_HOSTS does not include by default.
                'ALLOWED_HOSTS': 'testserver,localhost,127.0.0.1',
            }
            # The generator does not ship migration files for the payments app;
            # generate them the way a developer would before migrating.
            makemigrations = subprocess.run(
                [str(python), 'manage.py', 'makemigrations', 'payments'],
                cwd=str(project_dir),
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                makemigrations.returncode, 0, makemigrations.stdout + makemigrations.stderr
            )
            migrate = subprocess.run(
                [str(python), 'manage.py', 'migrate', '--noinput'],
                cwd=str(project_dir),
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(migrate.returncode, 0, migrate.stdout + migrate.stderr)

            script = project_dir / 'webhook_test.py'
            script.write_text(WEBHOOK_TEST_SCRIPT, encoding='utf-8')
            run = subprocess.run(
                [str(python), str(script)],
                cwd=str(project_dir),
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn('WEBHOOK_TEST_PASSED', run.stdout)


if __name__ == '__main__':
    unittest.main()
