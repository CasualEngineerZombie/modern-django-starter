"""Main project generator that orchestrates all sub-generators."""

from pathlib import Path

from .base import BaseGenerator
from .ci import CIGenerator
from .configuration import ConfigurationGenerator
from .django_apps import DjangoAppsGenerator
from .django_project import DjangoProjectGenerator
from .docker import DockerGenerator
from .requirements import RequirementsGenerator
from .static_files import StaticFilesGenerator
from .templates import TemplateGenerator


class ProjectGenerator(BaseGenerator):
    """
    Main project generator that coordinates all sub-generators.
    
    This class follows the Facade pattern, providing a simple interface
    while delegating to specialized generator classes.
    """

    def __init__(self, project_name: str, output_dir: str | Path, config: dict):
        super().__init__(project_name, Path(output_dir) / project_name, config, 
                        Path(__file__).parent.parent / 'templates')
        self.output_dir = Path(output_dir)
        self.project_dir = self.output_dir / project_name

    def generate(self) -> None:
        """Generate the complete project by running all sub-generators in order."""
        self.log(f"[bold blue]🔨 Generating project '{self.project_name}'...[/bold blue]")

        # Create project directory
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Initialize all sub-generators
        generators = [
            DjangoProjectGenerator(self.project_name, self.project_dir, self.config, self.template_dir),
            DjangoAppsGenerator(self.project_name, self.project_dir, self.config, self.template_dir),
            RequirementsGenerator(self.project_name, self.project_dir, self.config, self.template_dir),
            ConfigurationGenerator(self.project_name, self.project_dir, self.config, self.template_dir),
        ]

        # Add optional generators based on config
        if not self.config.get('api_only'):
            generators.append(
                TemplateGenerator(self.project_name, self.project_dir, self.config, self.template_dir)
            )
            generators.append(
                StaticFilesGenerator(self.project_name, self.project_dir, self.config, self.template_dir)
            )

        generators.extend([
            DockerGenerator(self.project_name, self.project_dir, self.config, self.template_dir),
            CIGenerator(self.project_name, self.project_dir, self.config, self.template_dir),
        ])

        # Run all generators
        for generator in generators:
            generator.generate()

        self.log('[green]✅ Project structure generated successfully![/green]')