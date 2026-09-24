"""
Modern Django Starter - Generator Package

This package contains modular generators for different aspects of Django project generation.
Each generator handles a specific concern, making the codebase maintainable and testable.
"""

from .project import ProjectGenerator
from .django_project import DjangoProjectGenerator
from .django_apps import DjangoAppsGenerator
from .requirements import RequirementsGenerator
from .configuration import ConfigurationGenerator
from .templates import TemplateGenerator
from .static_files import StaticFilesGenerator
from .docker import DockerGenerator
from .ci import CIGenerator

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