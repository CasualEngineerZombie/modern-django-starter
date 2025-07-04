"""Project generator for modern Django projects."""

import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.progress import Progress, TaskID, track
import subprocess
import sys

console = Console()

class ProjectGenerator:
    """Generates Django projects with modern features."""
    
    def __init__(self, project_name, output_dir, config):
        self.project_name = project_name
        self.output_dir = Path(output_dir)
        self.config = config
        self.project_dir = self.output_dir / project_name
        
        # Get template directory
        self.template_dir = Path(__file__).parent / "templates"
        
        # Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def generate(self):
        """Generate the project."""
        console.print(f"[bold blue]🔨 Generating project '{self.project_name}'...[/bold blue]")
        
        # Create project directory
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate files
        self._generate_django_project()
        self._generate_django_apps()
        self._generate_requirements()
        self._generate_configuration_files()
        self._generate_templates()
        self._generate_static_files()
        self._generate_docker_files()
        self._generate_ci_files()
        
        console.print("[green]✅ Project structure generated successfully![/green]")
    
    def _generate_django_project(self):
        """Generate Django project structure."""
        console.print("📦 Creating Django project structure...")
        
        # Create manage.py
        manage_py = self.env.get_template("manage.py.j2")
        content = manage_py.render(project_name=self.project_name)
        (self.project_dir / "manage.py").write_text(content)
        
        # Create project package
        project_package = self.project_dir / self.project_name
        project_package.mkdir(exist_ok=True)
        
        # Create __init__.py
        (project_package / "__init__.py").write_text("")
        
        # Create settings
        settings_dir = project_package / "settings"
        settings_dir.mkdir(exist_ok=True)
        (settings_dir / "__init__.py").write_text("")
        
        # Generate settings files
        for settings_file in ["base.py", "development.py", "production.py"]:
            template = self.env.get_template(f"settings/{settings_file}.j2")
            content = template.render(
                project_name=self.project_name,
                config=self.config
            )
            (settings_dir / settings_file).write_text(content)
        
        # Create urls.py
        urls_template = self.env.get_template("urls.py.j2")
        content = urls_template.render(config=self.config)
        (project_package / "urls.py").write_text(content)
        
        # Create wsgi.py and asgi.py
        wsgi_template = self.env.get_template("wsgi.py.j2")
        content = wsgi_template.render(project_name=self.project_name)
        (project_package / "wsgi.py").write_text(content)
        
        if self.config.get('use_async'):
            asgi_template = self.env.get_template("asgi.py.j2")
            content = asgi_template.render(project_name=self.project_name)
            (project_package / "asgi.py").write_text(content)
    
    def _generate_django_apps(self):
        """Generate Django applications."""
        console.print("🏗️  Creating Django applications...")
        
        # Create apps directory
        apps_dir = self.project_dir / "apps"
        apps_dir.mkdir(exist_ok=True)
        (apps_dir / "__init__.py").write_text("")
        
        # Create core app
        self._create_django_app(apps_dir, "core")
        
        # Create accounts app
        self._create_django_app(apps_dir, "accounts")
        
        # Create API app if DRF is enabled
        if self.config.get('use_drf'):
            self._create_django_app(apps_dir, "api")
    
    def _create_django_app(self, apps_dir, app_name):
        """Create a Django app with basic structure."""
        app_dir = apps_dir / app_name
        app_dir.mkdir(exist_ok=True)
        
        # Create __init__.py
        (app_dir / "__init__.py").write_text("")
        
        # Create apps.py
        apps_py_content = f"""from django.apps import AppConfig


class {app_name.title()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
"""
        (app_dir / "apps.py").write_text(apps_py_content)
        
        # Create models.py
        (app_dir / "models.py").write_text("from django.db import models\n\n# Create your models here.\n")
        
        # Create views.py
        if app_name == "core":
            views_content = """from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from datetime import datetime


class HomeView(TemplateView):
    template_name = 'home.html'


def time_view(request):
    \"\"\"HTMX endpoint for time demo.\"\"\"
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return JsonResponse({'time': current_time})
"""
        elif app_name == "api" and self.config.get('use_drf'):
            views_content = """from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def health_check(request):
    \"\"\"API health check endpoint.\"\"\"
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)
"""
        else:
            views_content = "from django.shortcuts import render\n\n# Create your views here.\n"
        
        (app_dir / "views.py").write_text(views_content)
        
        # Create admin.py
        (app_dir / "admin.py").write_text("from django.contrib import admin\n\n# Register your models here.\n")
        
        # Create tests.py
        tests_content = f"""from django.test import TestCase


class {app_name.title()}TestCase(TestCase):
    def test_placeholder(self):
        \"\"\"Placeholder test.\"\"\"
        self.assertTrue(True)
"""
        (app_dir / "tests.py").write_text(tests_content)
        
        # Create urls.py for specific apps
        if app_name == "core":
            urls_content = """from django.urls import path
from .views import HomeView, time_view

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('time/', time_view, name='time'),
]
"""
        elif app_name == "api" and self.config.get('use_drf'):
            urls_content = """from django.urls import path
from .views import health_check

urlpatterns = [
    path('health/', health_check, name='api_health'),
]
"""
        else:
            urls_content = """from django.urls import path

urlpatterns = [
    # Add your URL patterns here
]
"""
        (app_dir / "urls.py").write_text(urls_content)
    
    def _generate_requirements(self):
        """Generate requirements files."""
        console.print("📋 Creating requirements files...")
        
        # Base requirements
        requirements_template = self.env.get_template("requirements/base.txt.j2")
        content = requirements_template.render(config=self.config)
        
        requirements_dir = self.project_dir / "requirements"
        requirements_dir.mkdir(exist_ok=True)
        (requirements_dir / "base.txt").write_text(content)
        
        # Development requirements
        dev_requirements_template = self.env.get_template("requirements/development.txt.j2")
        content = dev_requirements_template.render(config=self.config)
        (requirements_dir / "development.txt").write_text(content)
        
        # Production requirements
        prod_requirements_template = self.env.get_template("requirements/production.txt.j2")
        content = prod_requirements_template.render(config=self.config)
        (requirements_dir / "production.txt").write_text(content)
        
        # Main requirements.txt
        (self.project_dir / "requirements.txt").write_text("-r requirements/development.txt\n")
    
    def _generate_configuration_files(self):
        """Generate configuration files."""
        console.print("⚙️  Creating configuration files...")
        
        # .env.example
        env_template = self.env.get_template("env.example.j2")
        content = env_template.render(
            project_name=self.project_name,
            config=self.config
        )
        (self.project_dir / ".env.example").write_text(content)
        
        # .gitignore
        gitignore_template = self.env.get_template("gitignore.j2")
        content = gitignore_template.render(config=self.config)
        (self.project_dir / ".gitignore").write_text(content)
        
        # README.md
        readme_template = self.env.get_template("README.md.j2")
        content = readme_template.render(
            project_name=self.project_name,
            config=self.config
        )
        (self.project_dir / "README.md").write_text(content)
    
    def _generate_templates(self):
        """Generate HTML templates."""
        console.print("🎨 Creating HTML templates...")
        
        templates_dir = self.project_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # Base template
        base_template = self.env.get_template("templates/base.html.j2")
        content = base_template.render(config=self.config)
        (templates_dir / "base.html").write_text(content)
        
        # Home template
        home_template = self.env.get_template("templates/home.html.j2")
        content = home_template.render(config=self.config)
        (templates_dir / "home.html").write_text(content)
        
        # Authentication templates if allauth is enabled
        if True:  # Always include auth templates
            auth_dir = templates_dir / "account"
            auth_dir.mkdir(exist_ok=True)
            
            for template_name in ["login.html", "signup.html", "logout.html"]:
                template = self.env.get_template(f"templates/account/{template_name}.j2")
                content = template.render(config=self.config)
                (auth_dir / template_name).write_text(content)
    
    def _generate_static_files(self):
        """Generate static files."""
        console.print("🎯 Creating static files...")
        
        static_dir = self.project_dir / "static"
        static_dir.mkdir(exist_ok=True)
        
        # CSS directory
        css_dir = static_dir / "css"
        css_dir.mkdir(exist_ok=True)
        
        # JavaScript directory
        js_dir = static_dir / "js"
        js_dir.mkdir(exist_ok=True)
        
        # Images directory
        img_dir = static_dir / "img"
        img_dir.mkdir(exist_ok=True)
        
        # Generate main CSS file
        css_template = self.env.get_template("static/css/main.css.j2")
        content = css_template.render(config=self.config)
        (css_dir / "main.css").write_text(content)
        
        # Generate main JS file
        js_template = self.env.get_template("static/js/main.js.j2")
        content = js_template.render(config=self.config)
        (js_dir / "main.js").write_text(content)
        
        # Generate package.json if frontend pipeline is used
        if self.config.get('frontend_pipeline') != 'none':
            package_json_template = self.env.get_template("package.json.j2")
            content = package_json_template.render(
                project_name=self.project_name,
                config=self.config
            )
            (self.project_dir / "package.json").write_text(content)
            
            # Generate build configuration
            if self.config.get('frontend_pipeline') == 'vite':
                vite_config_template = self.env.get_template("vite.config.js.j2")
                content = vite_config_template.render(config=self.config)
                (self.project_dir / "vite.config.js").write_text(content)
    
    def _generate_docker_files(self):
        """Generate Docker files."""
        if not self.config.get('use_docker'):
            return
        
        console.print("🐳 Creating Docker files...")
        
        # Dockerfile
        dockerfile_template = self.env.get_template("Dockerfile.j2")
        content = dockerfile_template.render(config=self.config)
        (self.project_dir / "Dockerfile").write_text(content)
        
        # docker-compose.yml
        docker_compose_template = self.env.get_template("docker-compose.yml.j2")
        content = docker_compose_template.render(
            project_name=self.project_name,
            config=self.config
        )
        (self.project_dir / "docker-compose.yml").write_text(content)
        
        # .dockerignore
        dockerignore_template = self.env.get_template("dockerignore.j2")
        content = dockerignore_template.render(config=self.config)
        (self.project_dir / ".dockerignore").write_text(content)
    
    def _generate_ci_files(self):
        """Generate CI configuration files."""
        if self.config.get('ci_tool') == 'none':
            return
        
        console.print("🔄 Creating CI configuration...")
        
        if self.config.get('ci_tool') == 'github-actions':
            github_dir = self.project_dir / ".github" / "workflows"
            github_dir.mkdir(parents=True, exist_ok=True)
            
            ci_template = self.env.get_template("github-actions.yml.j2")
            content = ci_template.render(
                project_name=self.project_name,
                config=self.config
            )
            (github_dir / "ci.yml").write_text(content)