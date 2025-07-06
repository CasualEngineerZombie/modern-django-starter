"""CLI interface for modern-django-starter."""

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
import os
import sys

from .generator import ProjectGenerator

console = Console()

@click.group()
@click.version_option()
def cli():
    """Modern Django Starter - Generate Django 5.x projects with modern features."""
    pass

@cli.command()
@click.argument('project_name', required=False)
@click.option('--output-dir', '-o', default='.', help='Output directory for the project')
@click.option('--api-only', is_flag=True, default=False, help='Generate an API-only project (no frontend/templates, only DRF/CORS/JWT/Spectacular)')
def create(project_name, output_dir, api_only):
    """Create a new Django project with modern features or API-only DRF backend."""
    console.print("[bold green]🚀 Modern Django Starter[/bold green]")
    if api_only:
        console.print("Generate Django 5.x API-only DRF backend (no frontend, no templates)\n")
    else:
        console.print("Generate Django 5.x projects with HTMX, AlpineJS, and more!\n")
    
    # Get project name if not provided
    if not project_name:
        project_name = Prompt.ask("Enter your project name", default="my_django_project")
    
    # Validate project name
    if not project_name.replace('_', '').replace('-', '').isalnum():
        console.print("[red]❌ Project name should only contain letters, numbers, hyphens, and underscores[/red]")
        sys.exit(1)
    
    config = {}
    
    if api_only:
        # API-only config, now with full prompts
        config['use_docker'] = Confirm.ask("Add Docker support?", default=True)
        config['use_postgresql'] = Confirm.ask("Use PostgreSQL database?", default=True)
        if config['use_postgresql']:
            config['postgresql_version'] = Prompt.ask(
                "PostgreSQL version",
                choices=['13', '14', '15', '16'],
                default='16'
            )
        # Cloud provider
        cloud_providers = [
            'none', 'aws', 'azure', 'gcp', 'render', 'railway', 
            'pythonanywhere', 'flyio', 'dokku', 'heroku'
        ]
        config['cloud_provider'] = Prompt.ask(
            "Cloud provider", 
            choices=cloud_providers, 
            default='none'
        )
        # Storage provider for media files
        storage_providers = [
            'local', 'aws', 'gcp', 'azure', 'cloudflare-r2'
        ]
        config['storage_provider'] = Prompt.ask(
            "Storage provider for media files", 
            choices=storage_providers, 
            default='local'
        )
        # Email provider
        config['email_provider'] = Prompt.ask(
            "Email provider", 
            choices=['none', 'sendgrid', 'mailgun', 'ses', 'postmark'], 
            default='none'
        )
        # Framework features
        config['use_async'] = Confirm.ask("Enable asynchronous support?", default=False)
        config['use_drf'] = True
        config['use_celery'] = Confirm.ask("Add Celery for background tasks?", default=False)
        config['use_sentry'] = Confirm.ask("Add Sentry error tracking?", default=False)
        config['use_stripe'] = Confirm.ask("Add Stripe for payments?", default=False)
        config['frontend_pipeline'] = 'none'
        config['ci_tool'] = Prompt.ask(
            "CI tool", 
            choices=['none', 'github-actions', 'gitlab-ci', 'travis', 'circleci'], 
            default='none'
        )
        config['api_only'] = True
        # DRF extras
        config['use_cors'] = True
        config['use_drf_spectacular'] = True
        config['use_jwt'] = True
    else:
        console.print("\n[bold blue]📋 Configuration Options[/bold blue]")
        # Basic options
        config['use_docker'] = Confirm.ask("Add Docker support?", default=True)
        config['use_postgresql'] = Confirm.ask("Use PostgreSQL database?", default=True)
        if config['use_postgresql']:
            config['postgresql_version'] = Prompt.ask(
                "PostgreSQL version", 
                choices=['13', '14', '15', '16'], 
                default='16'
            )
        # Cloud provider
        cloud_providers = [
            'none', 'aws', 'azure', 'gcp', 'render', 'railway', 
            'pythonanywhere', 'flyio', 'dokku', 'heroku'
        ]
        config['cloud_provider'] = Prompt.ask(
            "Cloud provider", 
            choices=cloud_providers, 
            default='none'
        )
        # Storage provider for media files
        storage_providers = [
            'local', 'aws', 'gcp', 'azure', 'cloudflare-r2'
        ]
        config['storage_provider'] = Prompt.ask(
            "Storage provider for media files", 
            choices=storage_providers, 
            default='local'
        )
        # Email provider
        config['email_provider'] = Prompt.ask(
            "Email provider", 
            choices=['none', 'sendgrid', 'mailgun', 'ses', 'postmark'], 
            default='none'
        )
        # Framework features
        config['use_async'] = Confirm.ask("Enable asynchronous support?", default=False)
        config['use_drf'] = Confirm.ask("Add Django Rest Framework?", default=True)
        config['use_celery'] = Confirm.ask("Add Celery for background tasks?", default=True)
        config['use_sentry'] = Confirm.ask("Add Sentry error tracking?", default=True)
        config['use_stripe'] = Confirm.ask("Add Stripe for payments?", default=False)
        # Frontend pipeline
        config['frontend_pipeline'] = Prompt.ask(
            "Frontend pipeline", 
            choices=['none', 'webpack', 'vite', 'parcel'], 
            default='vite'
        )
        # CI tools
        config['ci_tool'] = Prompt.ask(
            "CI tool", 
            choices=['none', 'github-actions', 'gitlab-ci', 'travis', 'circleci'], 
            default='github-actions'
        )
        config['api_only'] = False
    
    # Display configuration summary
    console.print("\n[bold blue]📊 Configuration Summary[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Option", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Project Name", project_name)
    table.add_row("Output Directory", output_dir)
    table.add_row("Docker Support", "✅" if config['use_docker'] else "❌")
    table.add_row("PostgreSQL", "✅" if config['use_postgresql'] else "❌")
    if config['use_postgresql']:
        table.add_row("PostgreSQL Version", config['postgresql_version'])
    table.add_row("Cloud Provider", config['cloud_provider'])
    table.add_row("Storage Provider", config['storage_provider'])
    table.add_row("Email Provider", config['email_provider'])
    table.add_row("Async Support", "✅" if config['use_async'] else "❌")
    table.add_row("Django Rest Framework", "✅" if config['use_drf'] else "❌")
    if api_only:
        table.add_row("CORS Support", "✅")
        table.add_row("DRF Spectacular", "✅")
        table.add_row("JWT Auth", "✅")
    table.add_row("Celery", "✅" if config['use_celery'] else "❌")
    table.add_row("Sentry", "✅" if config['use_sentry'] else "❌")
    table.add_row("Stripe Payments", "✅" if config['use_stripe'] else "❌")
    table.add_row("Frontend Pipeline", config['frontend_pipeline'])
    table.add_row("CI Tool", config['ci_tool'])
    
    console.print(table)
    
    # Confirm generation
    if not Confirm.ask(f"\n[bold yellow]Generate project '{project_name}'?[/bold yellow]", default=True):
        console.print("[yellow]❌ Project generation cancelled[/yellow]")
        sys.exit(0)
    
    # Generate project
    try:
        generator = ProjectGenerator(project_name, output_dir, config)
        generator.generate()
        console.print(f"\n[bold green]✅ Project '{project_name}' generated successfully![/bold green]")
        console.print(f"[dim]📁 Location: {os.path.abspath(os.path.join(output_dir, project_name))}[/dim]")
        
        # Show next steps
        console.print("\n[bold blue]🎯 Next Steps:[/bold blue]")
        console.print(f"1. cd {project_name}")
        if config['use_docker']:
            console.print("2. docker-compose up -d")
        else:
            console.print("2. python -m venv venv")
            console.print("3. source venv/bin/activate  # or venv\\Scripts\\activate on Windows")
            console.print("4. pip install -r requirements.txt")
            console.print("5. python manage.py migrate")
            console.print("6. python manage.py runserver")
        
    except Exception as e:
        console.print(f"[red]❌ Error generating project: {e}[/red]")
        sys.exit(1)

def main():
    """Main entry point for the CLI."""
    cli()

if __name__ == "__main__":
    main()