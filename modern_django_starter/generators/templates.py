"""Generator for HTML templates."""

from pathlib import Path

from .base import BaseGenerator


class TemplateGenerator(BaseGenerator):
    """Generates HTML templates for the project."""

    def generate(self) -> None:
        """Generate HTML templates."""
        self.log('🎨 Creating HTML templates...')

        templates_dir = self.project_dir / 'templates'
        templates_dir.mkdir(exist_ok=True)

        # Base template
        content = self.render_template('templates/base.html.j2')
        self.write_file(templates_dir / 'base.html', content)

        # Home template
        content = self.render_template('templates/home.html.j2')
        self.write_file(templates_dir / 'home.html', content)

        # Authentication templates
        self._generate_auth_templates(templates_dir)

        # Payment templates if Stripe is enabled
        if self.config.get('use_stripe'):
            self._generate_payment_templates(templates_dir)

    def _generate_auth_templates(self, templates_dir: Path) -> None:
        """Generate authentication templates."""
        auth_dir = templates_dir / 'account'
        auth_dir.mkdir(exist_ok=True)

        for template_name in ['login.html', 'signup.html', 'logout.html']:
            content = self.render_template(f'templates/account/{template_name}.j2')
            self.write_file(auth_dir / template_name, content)

    def _generate_payment_templates(self, templates_dir: Path) -> None:
        """Generate payment templates."""
        payments_dir = templates_dir / 'payments'
        payments_dir.mkdir(exist_ok=True)

        for template_name in ['checkout.html', 'success.html', 'cancel.html', 'orders.html']:
            content = self.render_template(f'templates/payments/{template_name}.j2')
            self.write_file(payments_dir / template_name, content)
