"""
Modern Django Starter - Generator Package

This package contains modular generators for different aspects of Django project generation.
Each generator handles a specific concern, making the codebase maintainable and testable.
"""

from .ci import CIGenerator
from .configuration import ConfigurationGenerator
from .django_apps import DjangoAppsGenerator
from .django_project import DjangoProjectGenerator
from .docker import DockerGenerator
from .project import ProjectGenerator
from .requirements import RequirementsGenerator
from .static_files import StaticFilesGenerator
from .templates import TemplateGenerator

__all__ = [
    'ProjectGenerator',
    'DjangoProjectGenerator',
    'DjangoAppsGenerator',
    'RequirementsGenerator',
    'ConfigurationGenerator',
    'TemplateGenerator',
    'StaticFilesGenerator',
    'DockerGenerator',
    'CIGenerator',
]