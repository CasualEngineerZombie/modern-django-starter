import unittest
from unittest.mock import patch

from click.testing import CliRunner

from modern_django_starter import __version__, logo
from modern_django_starter.cli import cli
from modern_django_starter.logo import INFO_BOX, MDS_v3


class TestCLIBanner(unittest.TestCase):
    """The MDS logo banner should appear on every initial CLI invocation."""

    def setUp(self):
        self.runner = CliRunner()

    def test_info_box_version_matches_package(self):
        self.assertIn(f'v{__version__}', INFO_BOX)

    def test_banner_uses_v3_art_only(self):
        # The legacy MDS_v2 art was removed in v0.3.2; guard the banner
        # contract so it can never silently regress back to the v2 logo.
        self.assertNotIn('MDS_v2', dir(logo))
        self.assertIn(MDS_v3.strip(), logo.LOGO)

    def test_no_args_shows_logo(self):
        result = self.runner.invoke(cli, [])
        # Click >= 8.2 raises NoArgsIsHelpError (exit 2) for a bare group
        # invocation; older versions exit 0. Either way the help/banner shows.
        self.assertIn(result.exit_code, (0, 2))
        self.assertIn(MDS_v3.strip(), result.output)
        self.assertIn(INFO_BOX.strip(), result.output)

    def test_help_shows_logo(self):
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(MDS_v3.strip(), result.output)
        self.assertIn(INFO_BOX.strip(), result.output)

    def test_version_shows_logo(self):
        result = self.runner.invoke(cli, ['--version'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(MDS_v3.strip(), result.output)
        self.assertIn(INFO_BOX.strip(), result.output)
        self.assertIn('version', result.output)

    def test_create_help_shows_logo(self):
        result = self.runner.invoke(cli, ['create', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(MDS_v3.strip(), result.output)
        self.assertIn(INFO_BOX.strip(), result.output)

    def test_create_command_shows_logo(self):
        # Answer every prompt non-interactively, then decline generation so no
        # project is written to disk.
        prompt_answers = ['none', 'local', 'none', 'vite', 'none']
        with (
            patch('modern_django_starter.cli.Confirm.ask', return_value=False),
            patch('modern_django_starter.cli.Prompt.ask', side_effect=prompt_answers),
        ):
            result = self.runner.invoke(cli, ['create', 'my_project'])

        self.assertEqual(result.exit_code, 0)
        self.assertIn(MDS_v3.strip(), result.output)
        self.assertIn(INFO_BOX.strip(), result.output)


if __name__ == '__main__':
    unittest.main()
