"""Tests for package metadata consistency (v0.3.4).

The release pipeline (``publish.yml``) insists that ``pyproject.toml`` and
``modern_django_starter.__version__`` agree, but that check only runs at
release time. This test fails a PR up front instead, so version drift never
reaches the release step.
"""

import pathlib
import tomllib
import unittest

from modern_django_starter import __version__

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestVersionConsistency(unittest.TestCase):
    def test_pyproject_version_matches_package_version(self):
        pyproject = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))
        self.assertEqual(pyproject['project']['version'], __version__)

    def test_package_docstring_mentions_django_61(self):
        # Regression guard for the stale "Django 5.x" package description.
        from modern_django_starter import __doc__

        self.assertIn('Django 6.1', __doc__)
