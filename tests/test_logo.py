"""Tests for the ASCII logo/banner module (v0.3.1 regression).

The ``MDS_v3`` art previously used a regular triple-quoted string full of
lone backslashes (an invalid-escape ``SyntaxWarning`` — a ``SyntaxError``
under ``-W error``). These tests pin that the module compiles warning-free
and that the rendered art is still the v3 banner the CLI shows.
"""

import pathlib
import unittest
import warnings

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / 'modern_django_starter' / 'logo.py'


class TestLogoCompilesCleanly(unittest.TestCase):
    def test_logo_module_compiles_without_escape_warnings(self):
        source = MODULE_PATH.read_text(encoding='utf-8')
        with warnings.catch_warnings():
            warnings.simplefilter('error', SyntaxWarning)
            # A SyntaxWarning raised during compilation is promoted to an
            # error by the filter above, failing the test on any invalid
            # escape sequence (e.g. the old '\_' in MDS_v3).
            compile(source, str(MODULE_PATH), 'exec')


class TestLogoRendersV3(unittest.TestCase):
    def test_mds_v3_art_is_present_and_within_banner(self):
        from modern_django_starter import logo

        self.assertTrue(logo.MDS_v3.strip())
        # First art line is the "Modern Django Starter" header block.
        self.assertTrue(logo.MDS_v3.lstrip().startswith('________'))
        # The full banner embeds the v3 art plus the info box.
        self.assertIn(logo.MDS_v3.strip(), logo.LOGO)
        self.assertIn(logo.INFO_BOX.strip(), logo.LOGO)
