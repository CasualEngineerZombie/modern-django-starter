"""Tests for the Django apps generator."""

import tempfile
from pathlib import Path

from modern_django_starter.generators.django_apps import DjangoAppsGenerator


class TestDjangoAppsGenerator:
    """Test DjangoAppsGenerator."""

    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name) / "test_project"
        self.template_dir = Path(self.temp_dir.name) / "templates"
        self.template_dir.mkdir(parents=True)

        # Create project directory
        self.project_dir.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        self.temp_dir.cleanup()

    def _make_generator(self, config):
        return DjangoAppsGenerator("test_project", self.project_dir, config, self.template_dir)

    def _read_file(self, rel_path):
        return (self.project_dir / rel_path).read_text()

    # --- API-only mode tests ---

    def test_api_only_creates_api_app(self):
        config = {"api_only": True, "use_drf": True, "use_stripe": False}
        gen = self._make_generator(config)
        gen.generate()

        # Check apps directory
        assert (self.project_dir / "apps" / "__init__.py").exists()
        assert (self.project_dir / "apps" / "api" / "__init__.py").exists()
        assert (self.project_dir / "apps" / "api" / "apps.py").exists()
        assert (self.project_dir / "apps" / "api" / "models.py").exists()
        assert (self.project_dir / "apps" / "api" / "views.py").exists()
        assert (self.project_dir / "apps" / "api" / "urls.py").exists()

        # Check api app content
        views = self._read_file("apps/api/views.py")
        assert "health_check" in views
        assert "@api_view" in views

        urls = self._read_file("apps/api/urls.py")
        assert "api_health" in urls

    def test_api_only_with_stripe_creates_payments_app(self):
        config = {"api_only": True, "use_drf": True, "use_stripe": True}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.project_dir / "apps" / "payments" / "__init__.py").exists()
        assert (self.project_dir / "apps" / "payments" / "apps.py").exists()
        assert (self.project_dir / "apps" / "payments" / "models.py").exists()
        assert (self.project_dir / "apps" / "payments" / "views.py").exists()
        assert (self.project_dir / "apps" / "payments" / "serializers.py").exists()
        assert (self.project_dir / "apps" / "payments" / "urls.py").exists()

        # Check DRF views (not template views)
        views = self._read_file("apps/payments/views.py")
        assert "OrderViewSet" in views
        assert "CheckoutViewSet" in views
        assert "StripeWebhookView" in views
        assert "checkout_view" not in views  # No template views
        assert "success_view" not in views

        # Check serializers
        serializers = self._read_file("apps/payments/serializers.py")
        assert "OrderSerializer" in serializers
        assert "CheckoutSessionSerializer" in serializers

        # Check URLs use DRF router
        urls = self._read_file("apps/payments/urls.py")
        assert "DefaultRouter" in urls
        assert "OrderViewSet" in urls
        assert "CheckoutViewSet" in urls

    def test_api_only_no_core_or_accounts_apps(self):
        config = {"api_only": True, "use_drf": True, "use_stripe": False}
        gen = self._make_generator(config)
        gen.generate()

        assert not (self.project_dir / "apps" / "core").exists()
        assert not (self.project_dir / "apps" / "accounts").exists()

    # --- Full mode tests ---

    def test_full_mode_creates_core_and_accounts(self):
        config = {"api_only": False, "use_drf": True, "use_stripe": False}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.project_dir / "apps" / "core" / "__init__.py").exists()
        assert (self.project_dir / "apps" / "accounts" / "__init__.py").exists()
        assert (self.project_dir / "apps" / "api" / "__init__.py").exists()

    def test_full_mode_core_app_has_home_view(self):
        config = {"api_only": False}
        gen = self._make_generator(config)
        gen.generate()

        views = self._read_file("apps/core/views.py")
        assert "HomeView" in views
        assert "TemplateView" in views
        assert "time_view" in views

    def test_full_mode_accounts_app_basic(self):
        config = {"api_only": False}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.project_dir / "apps" / "accounts" / "models.py").exists()
        assert (self.project_dir / "apps" / "accounts" / "views.py").exists()
        assert (self.project_dir / "apps" / "accounts" / "admin.py").exists()

    def test_full_mode_with_stripe_creates_payments_app(self):
        config = {"api_only": False, "use_stripe": True}
        gen = self._make_generator(config)
        gen.generate()

        assert (self.project_dir / "apps" / "payments" / "__init__.py").exists()

        # Check template views (not DRF)
        views = self._read_file("apps/payments/views.py")
        assert "checkout_view" in views
        assert "success_view" in views
        assert "cancel_view" in views
        assert "StripeWebhookView" in views
        assert "OrderViewSet" not in views  # No DRF viewsets

        # No serializers in full mode
        assert not (self.project_dir / "apps" / "payments" / "serializers.py").exists()

    def test_full_mode_payments_urls_use_django_paths(self):
        config = {"api_only": False, "use_stripe": True}
        gen = self._make_generator(config)
        gen.generate()

        urls = self._read_file("apps/payments/urls.py")
        assert "checkout_view" in urls
        assert "success_view" in urls
        assert "cancel_view" in urls
        assert "StripeWebhookView" in urls
        assert "DefaultRouter" not in urls

    def test_full_mode_without_drf_no_api_app(self):
        config = {"api_only": False, "use_drf": False}
        gen = self._make_generator(config)
        gen.generate()

        assert not (self.project_dir / "apps" / "api").exists()

    # --- App structure tests ---

    def test_each_app_has_required_files(self):
        config = {"api_only": False, "use_drf": True}
        gen = self._make_generator(config)
        gen.generate()

        for app_name in ["core", "accounts", "api"]:
            app_dir = self.project_dir / "apps" / app_name
            assert (app_dir / "__init__.py").exists()
            assert (app_dir / "apps.py").exists()
            assert (app_dir / "models.py").exists()
            assert (app_dir / "views.py").exists()
            assert (app_dir / "admin.py").exists()
            assert (app_dir / "tests.py").exists()
            assert (app_dir / "urls.py").exists()

    def test_apps_py_has_correct_config_class(self):
        config = {"api_only": False, "use_drf": True}
        gen = self._make_generator(config)
        gen.generate()

        for app_name in ["core", "accounts", "api"]:
            apps_py = self._read_file(f"apps/{app_name}/apps.py")
            expected_class = f"{app_name.title()}Config"
            assert expected_class in apps_py
            assert f"name = 'apps.{app_name}'" in apps_py

    def test_models_py_has_base_import(self):
        config = {"api_only": False, "use_drf": True}
        gen = self._make_generator(config)
        gen.generate()

        for app_name in ["core", "accounts", "api"]:
            models = self._read_file(f"apps/{app_name}/models.py")
            assert "from django.db import models" in models

    def test_admin_py_has_base_import(self):
        config = {"api_only": False, "use_drf": True}
        gen = self._make_generator(config)
        gen.generate()

        for app_name in ["core", "accounts", "api"]:
            admin = self._read_file(f"apps/{app_name}/admin.py")
            assert "from django.contrib import admin" in admin

    def test_tests_py_has_test_case(self):
        config = {"api_only": False, "use_drf": True}
        gen = self._make_generator(config)
        gen.generate()

        for app_name in ["core", "accounts", "api"]:
            tests = self._read_file(f"apps/{app_name}/tests.py")
            expected_class = f"{app_name.title()}TestCase"
            assert expected_class in tests
            assert "def test_placeholder" in tests

    # --- Payments app specific tests ---

    def test_payments_models_has_order_and_orderitem(self):
        config = {"api_only": False, "use_stripe": True}
        gen = self._make_generator(config)
        gen.generate()

        models = self._read_file("apps/payments/models.py")
        assert "class Order" in models
        assert "class OrderItem" in models
        assert "stripe_checkout_session_id" in models
        assert "total_price" in models

    def test_payments_apps_py_has_ready_method(self):
        config = {"api_only": False, "use_stripe": True}
        gen = self._make_generator(config)
        gen.generate()

        apps_py = self._read_file("apps/payments/apps.py")
        assert "def ready(self)" in apps_py
        assert "import apps.payments.signals" in apps_py

    def test_payments_signals_creates_stripe_customer(self):
        config = {"api_only": False, "use_stripe": True}
        gen = self._make_generator(config)
        gen.generate()

        signals = self._read_file("apps/payments/signals.py")
        assert "create_stripe_customer" in signals
        assert "@receiver(post_save, sender=User)" in signals
        assert "Customer.get_or_create" in signals

    def test_payments_admin_registers_models(self):
        config = {"api_only": False, "use_stripe": True}
        gen = self._make_generator(config)
        gen.generate()

        admin = self._read_file("apps/payments/admin.py")
        assert "@admin.register(Order)" in admin
        assert "@admin.register(OrderItem)" in admin
        assert "OrderItemInline" in admin

    # --- Edge cases ---

    def test_apps_directory_created_once(self):
        config = {"api_only": False}
        gen = self._make_generator(config)
        gen.generate()

        # Should not raise error if called again
        gen.generate()

    def test_init_files_are_empty(self):
        config = {"api_only": False, "use_drf": True}
        gen = self._make_generator(config)
        gen.generate()

        for app_name in ["core", "accounts", "api"]:
            init_content = self._read_file(f"apps/{app_name}/__init__.py")
            assert init_content == ""