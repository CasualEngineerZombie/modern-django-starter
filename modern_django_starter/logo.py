"""ASCII logo and info banner for the Modern Django Starter CLI.

Contains the ``MDS_v2`` logo art, the ``INFO_BOX`` metadata panel, and
the Django-green ``LOGO`` banner built from both.
"""

from . import __version__

MDS_v2 = """
██████▄       ███ ▄███████▄ ███▄▄  ███ ▄███████▄    ▄██████▄      
███  ███      ███ ███   ███ ███▀██▄███ ███▀  ▀▀▀   ███▀  ▀███     
███  ▐██ ███  ███ █████████ ███  ▀▀███ ███  ▀▀███▀ ███    ███     
███▄▄██▀ ███▄▄███ ███   ███ ███    ███ ████▄▄████  ▀███▄▄███▀     
▀▀▀▀▀▀    ▀▀▀▀▀▀  ▀▀▀   ▀▀▀ ▀▀▀    ▀▀▀  ▀▀▀▀▀▀▀ ▀    ▀▀▀▀▀▀       
▄███████▄ █████████ ▄███████▄ ███████▄  █████████ ████████ ███████▄ 
███▄▄▄▄      ███    ███   ███ ███   ███    ███    ███      ███   ███
 ▀██████▄    ███    █████████ ████████     ███    ███▀▀▀   ████████ 
▄▄▄▄▄▄███    ███    ███   ███ ███   ███    ███    ███▄▄▄▄▄ ███   ███
 ▀▀▀▀▀▀▀     ▀▀▀    ▀▀▀   ▀▀▀ ▀▀▀   ▀▀▀    ▀▀▀    ▀▀▀▀▀▀▀▀ ▀▀▀   ▀▀▀
"""


def _build_info_box() -> str:
    """Build the metadata panel, pulling the version from ``__version__``."""
    width = 73  # number of box-drawing characters between the corners

    def key_value_row(label: str, value: str) -> str:
        # Aligns the interior "│" separator across all key/value rows.
        return '  │' + ('  ' + label.ljust(9) + '│  ' + value).ljust(width) + '│'

    lines = [
        '  ┌' + '─' * width + '┐',
        '  │' + '  Modern Django Starter'.ljust(width) + '│',
        '  ├' + '─' * width + '┤',
        key_value_row('Version', f'v{__version__}'),
        key_value_row('Author', 'Rian Barriga'),
        key_value_row('License', 'MIT'),
        key_value_row('GitHub', 'CasualEngineerZombie/modern-django-starter'),
        '  └' + '─' * width + '┘',
    ]
    return '\n' + '\n'.join(lines) + '\n'


INFO_BOX = _build_info_box()

DJANGO_GREEN = '\033[38;5;34m'
RESET = '\033[0m'

# Full banner: the MDS logo plus the info box, colored Django green.
LOGO = f'{DJANGO_GREEN}{MDS_v2}{INFO_BOX}{RESET}'


def print_logo():
    """Print the full Django-green MDS banner to stdout."""
    print(LOGO)
