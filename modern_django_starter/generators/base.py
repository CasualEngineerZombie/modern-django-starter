"""Base generator class with common functionality."""

from abc import ABC, abstractmethod
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from rich.console import Console

console = Console()


class BaseGenerator(ABC):
    """Base class for all generators providing common utilities."""

    def __init__(self, project_name: str, project_dir: Path, config: dict, template_dir: Path):
        self.project_name = project_name
        self.project_dir = project_dir
        self.config = config
        self.template_dir = template_dir

        # Shared Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    @abstractmethod
    def generate(self) -> None:
        """Generate the project files. Must be implemented by subclasses."""
        pass

    def render_template(self, template_name: str, **context) -> str:
        """Render a Jinja2 template with the given context."""
        template = self.env.get_template(template_name)
        return template.render(project_name=self.project_name, config=self.config, **context)

    def write_file(
        self, path: Path, content: str, encoding: str = 'utf-8', newline: str | None = None
    ) -> None:
        """Write content to a file, creating parent directories if needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding, newline=newline)

    def log(self, message: str, style: str | None = None) -> None:
        """Log a message using rich console."""
        if style:
            console.print(f'[{style}]{message}[/{style}]')
        else:
            console.print(message)
