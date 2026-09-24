"""ASCII logo and info banner for the Modern Django Starter CLI.

Contains the ``MDS_v2`` logo art, the ``INFO_BOX`` metadata panel, and
the Django-green ``LOGO`` banner built from both.
"""

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

INFO_BOX = """
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Modern Django Starter                                                  │
  ├─────────────────────────────────────────────────────────────────────────┤
  │  Version  │  v1.0.0                                                     │
  │  Author   │  Rian Barriga                                               │
  │  License  │  MIT                                                        │
  │  GitHub   │  CasualEngineerZombie/modern-django-starter                 │
  └─────────────────────────────────────────────────────────────────────────┘
"""

DJANGO_GREEN = '\033[38;5;34m'
RESET = '\033[0m'

# Full banner: the MDS logo plus the info box, colored Django green.
LOGO = f'{DJANGO_GREEN}{MDS_v2}{INFO_BOX}{RESET}'


def print_logo():
    """Print the full Django-green MDS banner to stdout."""
    print(LOGO)