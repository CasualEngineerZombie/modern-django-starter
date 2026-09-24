"""Project generator for modern Django projects."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from rich.console import Console

console = Console()


class ProjectGenerator:
    """Generates Django projects with modern features."""

    def __init__(self, project_name, output_dir, config):
        self.project_name = project_name
        self.output_dir = Path(output_dir)
        self.config = config
        self.project_dir = self.output_dir / project_name

        # Get template directory
        self.template_dir = Path(__file__).parent / 'templates'

        # Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)), trim_blocks=True, lstrip_blocks=True
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
        if not self.config.get('api_only'):
            self._generate_templates()
            self._generate_static_files()
        self._generate_docker_files()
        self._generate_ci_files()
        console.print('[green]✅ Project structure generated successfully![/green]')

    def _generate_django_project(self):
        """Generate Django project structure."""
        console.print('📦 Creating Django project structure...')
        # Create manage.py
        manage_py = self.env.get_template('manage.py.j2')
        content = manage_py.render(project_name=self.project_name)
        (self.project_dir / 'manage.py').write_text(content, encoding='utf-8')
        # Create project package
        project_package = self.project_dir / self.project_name
        project_package.mkdir(exist_ok=True)
        # Create __init__.py
        (project_package / '__init__.py').write_text('', encoding='utf-8')
        # Create settings
        settings_dir = project_package / 'settings'
        settings_dir.mkdir(exist_ok=True)
        (settings_dir / '__init__.py').write_text('', encoding='utf-8')
        # Generate settings from the shared templates. API-only projects reuse
        # the same base/development/production split; the templates branch on
        # `config.api_only` for the DRF/JWT/schema-specific settings instead of
        # hard-coding a second set of settings files.
        for settings_file in ['base.py', 'development.py', 'production.py']:
            template = self.env.get_template(f'settings/{settings_file}.j2')
            content = template.render(project_name=self.project_name, config=self.config)
            (settings_dir / settings_file).write_text(content, encoding='utf-8')
        # Create urls.py from the shared template (API-only branch included).
        urls_path = project_package / 'urls.py'
        urls_template = self.env.get_template('urls.py.j2')
        content = urls_template.render(project_name=self.project_name, config=self.config)
        urls_path.write_text(content, encoding='utf-8')
        # Create wsgi.py and asgi.py
        wsgi_template = self.env.get_template('wsgi.py.j2')
        content = wsgi_template.render(project_name=self.project_name)
        (project_package / 'wsgi.py').write_text(content, encoding='utf-8')
        if self.config.get('use_async'):
            asgi_template = self.env.get_template('asgi.py.j2')
            content = asgi_template.render(project_name=self.project_name)
            (project_package / 'asgi.py').write_text(content, encoding='utf-8')

    def _generate_django_apps(self):
        """Generate Django applications."""
        console.print('🏗️  Creating Django applications...')
        apps_dir = self.project_dir / 'apps'
        apps_dir.mkdir(exist_ok=True)
        (apps_dir / '__init__.py').write_text('', encoding='utf-8')
        if self.config.get('api_only'):
            # Only API app for api_only
            self._create_django_app(apps_dir, 'api')
            if self.config.get('use_stripe'):
                self._create_payments_app_api(apps_dir)
        else:
            self._create_django_app(apps_dir, 'core')
            self._create_django_app(apps_dir, 'accounts')
            if self.config.get('use_drf'):
                self._create_django_app(apps_dir, 'api')
            if self.config.get('use_stripe'):
                self._create_payments_app(apps_dir)

    def _create_django_app(self, apps_dir, app_name):
        """Create a Django app with basic structure."""
        app_dir = apps_dir / app_name
        app_dir.mkdir(exist_ok=True)

        # Create __init__.py
        (app_dir / '__init__.py').write_text('', encoding='utf-8')

        # Create apps.py
        apps_py_content = f"""from django.apps import AppConfig


class {app_name.title()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
"""
        (app_dir / 'apps.py').write_text(apps_py_content, encoding='utf-8')

        # Create models.py
        (app_dir / 'models.py').write_text(
            'from django.db import models\n\n# Create your models here.\n', encoding='utf-8'
        )

        # Create views.py
        if app_name == 'core':
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
        elif app_name == 'api' and self.config.get('use_drf'):
            views_content = """from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def health_check(request):
    \"\"\"API health check endpoint.\"\"\"
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)
"""
        else:
            views_content = 'from django.shortcuts import render\n\n# Create your views here.\n'

        (app_dir / 'views.py').write_text(views_content, encoding='utf-8')

        # Create admin.py
        (app_dir / 'admin.py').write_text(
            'from django.contrib import admin\n\n# Register your models here.\n', encoding='utf-8'
        )

        # Create tests.py
        tests_content = f"""from django.test import TestCase


class {app_name.title()}TestCase(TestCase):
    def test_placeholder(self):
        \"\"\"Placeholder test.        \"\"\"
        self.assertTrue(True)
"""
        (app_dir / 'tests.py').write_text(tests_content, encoding='utf-8')

        # Create urls.py for specific apps
        if app_name == 'core':
            urls_content = """from django.urls import path
from .views import HomeView, time_view

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('time/', time_view, name='time'),
]
"""
        elif app_name == 'api' and self.config.get('use_drf'):
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
        (app_dir / 'urls.py').write_text(urls_content, encoding='utf-8')

    def _create_payments_app(self, apps_dir):
        """Create a payments app with Stripe integration."""
        app_dir = apps_dir / 'payments'
        app_dir.mkdir(exist_ok=True)

        # Create __init__.py
        (app_dir / '__init__.py').write_text('', encoding='utf-8')

        # Create apps.py
        apps_py_content = """from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments'
    
    def ready(self):
        import apps.payments.signals
"""
        (app_dir / 'apps.py').write_text(apps_py_content, encoding='utf-8')

        # Create models.py
        models_content = """from django.db import models
from django.contrib.auth.models import User
from djstripe.models import Customer, Subscription


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.price * self.quantity
"""
        (app_dir / 'models.py').write_text(models_content, encoding='utf-8')

        # Create views.py
        views_content = """from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views import View
import stripe
import json

from .models import Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout_view(request):
    \"\"\"Create a Stripe checkout session.\"\"\"
    if request.method == 'POST':
        try:
            # Sample items - you would get these from your cart/request
            items = [
                {
                    'name': 'Sample Product',
                    'quantity': 1,
                    'price': 29.99
                }
            ]
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=sum(item['price'] * item['quantity'] for item in items),
                currency='USD'
            )
            
            # Create order items
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    name=item['name'],
                    quantity=item['quantity'],
                    price=item['price']
                )
            
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': item['name'],
                            },
                            'unit_amount': int(item['price'] * 100),  # Convert to cents
                        },
                        'quantity': item['quantity'],
                    } for item in items
                ],
                mode='payment',
                success_url=request.build_absolute_uri('/payments/success/'),
                cancel_url=request.build_absolute_uri('/payments/cancel/'),
                metadata={
                    'order_id': order.id,
                    'user_id': request.user.id,
                }
            )
            
            # Update order with session ID
            order.stripe_checkout_session_id = session.id
            order.save()
            
            return JsonResponse({'checkout_url': session.url})
            
        except Exception as e:
            messages.error(request, f'Error creating checkout session: {str(e)}')
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'payments/checkout.html')


@login_required
def success_view(request):
    \"\"\"Handle successful payment.\"\"\"
    return render(request, 'payments/success.html')


@login_required
def cancel_view(request):
    \"\"\"Handle cancelled payment.\"""
    messages.info(request, 'Payment was cancelled.')
    return render(request, 'payments/cancel.html')


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    \"\"\"Handle Stripe webhooks.\"""
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.DJSTRIPE_WEBHOOK_SECRET
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return JsonResponse({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return JsonResponse({'error': 'Invalid signature'}, status=400)
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._handle_checkout_session_completed(session)
        
        return JsonResponse({'status': 'success'})
    
    def _handle_checkout_session_completed(self, session):
        \"\"\"Handle successful checkout session.\"""
        order_id = session.get('metadata', {}).get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.status = 'completed'
                order.save()
            except Order.DoesNotExist:
                pass


class OrderListView(ListView):
    \"\"\"List user's orders.\"""
    model = Order
    template_name = 'payments/orders.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
"""
        (app_dir / 'views.py').write_text(views_content, encoding='utf-8')

        # Create admin.py
        admin_content = """from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'stripe_checkout_session_id']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'name', 'quantity', 'price', 'total_price']
    list_filter = ['order__created_at']
    search_fields = ['name', 'order__user__email']
"""
        (app_dir / 'admin.py').write_text(admin_content, encoding='utf-8')

        # Create signals.py
        signals_content = """from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from djstripe.models import Customer


@receiver(post_save, sender=User)
def create_stripe_customer(sender, instance, created, **kwargs):
    \"\"\"Create a Stripe customer when a user is created.\"""
    if created:
        Customer.get_or_create(subscriber=instance)
"""
        (app_dir / 'signals.py').write_text(signals_content, encoding='utf-8')

        # Create tests.py
        tests_content = """from django.test import TestCase
from django.contrib.auth.models import User
from .models import Order, OrderItem


class PaymentsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_order_creation(self):
        \"\"\"Test order creation.\"""
        order = Order.objects.create(
            user=self.user,
            total_amount=29.99,
            currency='USD'
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_amount, 29.99)
        self.assertEqual(order.status, 'pending')
    
    def test_order_item_creation(self):
        \"\"\"Test order item creation.\"""
        order = Order.objects.create(
            user=self.user,
            total_amount=29.99,
            currency='USD'
        )
        
        item = OrderItem.objects.create(
            order=order,
            name='Test Product',
            quantity=2,
            price=14.99
        )
        
        self.assertEqual(item.total_price, 29.98)
        self.assertEqual(order.items.count(), 1)
"""
        (app_dir / 'tests.py').write_text(tests_content, encoding='utf-8')

        # Create urls.py
        urls_content = """from django.urls import path
from .views import (
    checkout_view, success_view, cancel_view,
    StripeWebhookView, OrderListView
)

urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
    path('success/', success_view, name='payment_success'),
    path('cancel/', cancel_view, name='payment_cancel'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
]
"""
        (app_dir / 'urls.py').write_text(urls_content, encoding='utf-8')

    def _create_payments_app_api(self, apps_dir):
        """Create a payments app with Stripe integration for API-only projects (DRF views)."""
        app_dir = apps_dir / 'payments'
        app_dir.mkdir(exist_ok=True)

        # Create __init__.py
        (app_dir / '__init__.py').write_text('', encoding='utf-8')

        # Create apps.py
        apps_py_content = """from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments'
    
    def ready(self):
        import apps.payments.signals
"""
        (app_dir / 'apps.py').write_text(apps_py_content, encoding='utf-8')

        # Create models.py - same as regular payments app
        models_content = """from django.db import models
from django.contrib.auth.models import User
from djstripe.models import Customer, Subscription


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.price * self.quantity
"""
        (app_dir / 'models.py').write_text(models_content, encoding='utf-8')

        # Create serializers.py for DRF
        serializers_content = """from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'name', 'quantity', 'price', 'total_price']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'stripe_checkout_session_id', 'total_amount', 'currency', 'status', 'created_at', 'updated_at', 'items', 'total_price']
        read_only_fields = ['id', 'user', 'stripe_checkout_session_id', 'status', 'created_at', 'updated_at', 'total_price']


class CheckoutSessionSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        write_only=True
    )
    success_url = serializers.URLField(required=False)
    cancel_url = serializers.URLField(required=False)
"""
        (app_dir / 'serializers.py').write_text(serializers_content, encoding='utf-8')

        # Create views.py with DRF views
        views_content = """from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import stripe
import json

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer, CheckoutSessionSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    \"\"\"ViewSet for listing and retrieving user's orders.\"\"\"
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(viewsets.ViewSet):
    \"\"\"Handle Stripe webhooks.\"\"\"
    permission_classes = []  # Webhooks don't use auth

    def create(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.DJSTRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return JsonResponse({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return JsonResponse({'error': 'Invalid signature'}, status=400)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._handle_checkout_session_completed(session)

        return JsonResponse({'status': 'success'})

    def _handle_checkout_session_completed(self, session):
        \"\"\"Handle successful checkout session.\"\"\"
        order_id = session.get('metadata', {}).get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.status = 'completed'
                order.save()
            except Order.DoesNotExist:
                pass


class CheckoutViewSet(viewsets.ViewSet):
    \"\"\"Create Stripe checkout sessions.\"\"\"
    permission_classes = [IsAuthenticated]

    def create(self, request):
        \"\"\"Create a Stripe checkout session.\"\"\"
        serializer = CheckoutSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            items = data['items']

            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=sum(float(item['price']) * int(item['quantity']) for item in items),
                currency=data.get('currency', 'USD')
            )

            # Create order items
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    name=item['name'],
                    quantity=int(item['quantity']),
                    price=item['price']
                )

            # Create Stripe checkout session
            success_url = data.get('success_url', request.build_absolute_uri('/api/payments/success/'))
            cancel_url = data.get('cancel_url', request.build_absolute_uri('/api/payments/cancel/'))

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': data.get('currency', 'USD').lower(),
                            'product_data': {
                                'name': item['name'],
                            },
                            'unit_amount': int(float(item['price']) * 100),  # Convert to cents
                        },
                        'quantity': int(item['quantity']),
                    } for item in items
                ],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'order_id': order.id,
                    'user_id': request.user.id,
                }
            )

            # Update order with session ID
            order.stripe_checkout_session_id = session.id
            order.save()

            return Response({'checkout_url': session.url, 'order_id': order.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def success(self, request):
        \"\"\"Handle successful payment redirect.\"\"\"
        return Response({'status': 'success', 'message': 'Payment completed successfully'})

    @action(detail=False, methods=['get'])
    def cancel(self, request):
        \"\"\"Handle cancelled payment redirect.\"\"\"
        return Response({'status': 'cancelled', 'message': 'Payment was cancelled'}, status=status.HTTP_400_BAD_REQUEST)
"""
        (app_dir / 'views.py').write_text(views_content, encoding='utf-8')

        # Create admin.py
        admin_content = """from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'stripe_checkout_session_id']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'name', 'quantity', 'price', 'total_price']
    list_filter = ['order__created_at']
    search_fields = ['name', 'order__user__email']
"""
        (app_dir / 'admin.py').write_text(admin_content, encoding='utf-8')

        # Create signals.py
        signals_content = """from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from djstripe.models import Customer


@receiver(post_save, sender=User)
def create_stripe_customer(sender, instance, created, **kwargs):
    \"\"\"Create a Stripe customer when a user is created.\"\"\"
    if created:
        Customer.get_or_create(subscriber=instance)
"""
        (app_dir / 'signals.py').write_text(signals_content, encoding='utf-8')

        # Create tests.py
        tests_content = """from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Order, OrderItem


class PaymentsAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_order_creation(self):
        \"\"\"Test order creation.\"\"\"
        order = Order.objects.create(
            user=self.user,
            total_amount=29.99,
            currency='USD'
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_amount, 29.99)
        self.assertEqual(order.status, 'pending')

    def test_order_item_creation(self):
        \"\"\"Test order item creation.\"\"\"
        order = Order.objects.create(
            user=self.user,
            total_amount=29.99,
            currency='USD'
        )

        item = OrderItem.objects.create(
            order=order,
            name='Test Product',
            quantity=2,
            price=14.99
        )

        self.assertEqual(item.total_price, 29.98)
        self.assertEqual(order.items.count(), 1)
"""
        (app_dir / 'tests.py').write_text(tests_content, encoding='utf-8')

        # Create urls.py for API
        urls_content = """from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CheckoutViewSet, StripeWebhookView

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'checkout', CheckoutViewSet, basename='checkout')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', StripeWebhookView.as_view({'post': 'create'}), name='stripe_webhook'),
]
"""
        (app_dir / 'urls.py').write_text(urls_content, encoding='utf-8')

    def _generate_requirements(self):
        """Generate requirements files."""
        console.print('📋 Creating requirements files...')
        requirements_dir = self.project_dir / 'requirements'
        requirements_dir.mkdir(exist_ok=True)
        if self.config.get('api_only'):
            # Minimal DRF API requirements. Kept deliberately lean for API-only
            # projects, but complete enough to run the shared settings templates:
            # python-decouple is required (settings/base.py.j2 reads configuration
            # through decouple) and cloud-storage packages are added when a
            # non-local storage provider is selected. The Django floor is 6.1 to
            # match the shared templates.
            base_reqs = [
                'Django>=6.1',
                'djangorestframework',
                'django-cors-headers',
                'drf-spectacular',
                'djangorestframework-simplejwt',
                'dj-rest-auth',
                'django-allauth',
                # dj-rest-auth registration pulls in
                # allauth.socialaccount.providers.oauth2.client, which requires
                # requests at import time.
                'requests',
                'python-decouple',
            ]
            if self.config.get('use_postgresql'):
                base_reqs.append('psycopg2-binary')
            storage_provider = self.config.get('storage_provider', 'local')
            if storage_provider != 'local':
                base_reqs.append('django-storages')
                if storage_provider in ('aws', 'cloudflare-r2'):
                    base_reqs.append('boto3')
                elif storage_provider == 'gcp':
                    base_reqs.append('google-cloud-storage')
                elif storage_provider == 'azure':
                    base_reqs.append('azure-storage-blob')
            # The shared settings templates emit Celery/Sentry configuration
            # for API-only projects too, so those packages must be installed
            # or ``manage.py check`` fails on the first import.
            if self.config.get('use_celery'):
                base_reqs.append('celery')
                base_reqs.append('redis')
            if self.config.get('use_sentry'):
                base_reqs.append('sentry-sdk')
            if self.config.get('use_stripe'):
                base_reqs.append('dj-stripe')
                base_reqs.append('stripe')
            (requirements_dir / 'base.txt').write_text(
                '\n'.join(base_reqs) + '\n', encoding='utf-8'
            )
            (requirements_dir / 'development.txt').write_text('-r base.txt\n', encoding='utf-8')
            (requirements_dir / 'production.txt').write_text('-r base.txt\n', encoding='utf-8')
            (self.project_dir / 'requirements.txt').write_text(
                '-r requirements/development.txt\n', encoding='utf-8'
            )
        else:
            # Base requirements
            requirements_template = self.env.get_template('requirements/base.txt.j2')
            content = requirements_template.render(config=self.config)
            (requirements_dir / 'base.txt').write_text(content, encoding='utf-8')

            # Development requirements
            dev_requirements_template = self.env.get_template('requirements/development.txt.j2')
            content = dev_requirements_template.render(config=self.config)
            (requirements_dir / 'development.txt').write_text(content, encoding='utf-8')

            # Production requirements
            prod_requirements_template = self.env.get_template('requirements/production.txt.j2')
            content = prod_requirements_template.render(config=self.config)
            (requirements_dir / 'production.txt').write_text(content, encoding='utf-8')

            # Main requirements.txt
            (self.project_dir / 'requirements.txt').write_text(
                '-r requirements/development.txt\n', encoding='utf-8'
            )

    def _generate_configuration_files(self):
        """Generate configuration files."""
        console.print('⚙️  Creating configuration files...')
        # .env.example
        env_template = self.env.get_template('env.example.j2')
        content = env_template.render(project_name=self.project_name, config=self.config)
        (self.project_dir / '.env.example').write_text(content, encoding='utf-8')
        # .gitignore
        gitignore_template = self.env.get_template('gitignore.j2')
        content = gitignore_template.render(config=self.config)
        (self.project_dir / '.gitignore').write_text(content, encoding='utf-8')
        # README.md
        readme_template = self.env.get_template('README.md.j2')
        content = readme_template.render(project_name=self.project_name, config=self.config)
        (self.project_dir / 'README.md').write_text(content, encoding='utf-8')

    def _generate_templates(self):
        """Generate HTML templates."""
        console.print('🎨 Creating HTML templates...')

        templates_dir = self.project_dir / 'templates'
        templates_dir.mkdir(exist_ok=True)

        # Base template
        base_template = self.env.get_template('templates/base.html.j2')
        content = base_template.render(config=self.config)
        (templates_dir / 'base.html').write_text(content, encoding='utf-8')

        # Home template
        home_template = self.env.get_template('templates/home.html.j2')
        content = home_template.render(config=self.config)
        (templates_dir / 'home.html').write_text(content, encoding='utf-8')

        # Authentication templates if allauth is enabled
        if True:  # Always include auth templates
            auth_dir = templates_dir / 'account'
            auth_dir.mkdir(exist_ok=True)

            for template_name in ['login.html', 'signup.html', 'logout.html']:
                template = self.env.get_template(f'templates/account/{template_name}.j2')
                content = template.render(config=self.config)
                (auth_dir / template_name).write_text(content, encoding='utf-8')

        # Payment templates if Stripe is enabled
        if self.config.get('use_stripe'):
            payments_dir = templates_dir / 'payments'
            payments_dir.mkdir(exist_ok=True)

            for template_name in ['checkout.html', 'success.html', 'cancel.html', 'orders.html']:
                template = self.env.get_template(f'templates/payments/{template_name}.j2')
                content = template.render(config=self.config)
                (payments_dir / template_name).write_text(content, encoding='utf-8')

    def _generate_static_files(self):
        """Generate static files."""
        console.print('🎯 Creating static files...')

        static_dir = self.project_dir / 'static'
        static_dir.mkdir(exist_ok=True)

        # CSS directory
        css_dir = static_dir / 'css'
        css_dir.mkdir(exist_ok=True)

        # JavaScript directory
        js_dir = static_dir / 'js'
        js_dir.mkdir(exist_ok=True)

        # Images directory
        img_dir = static_dir / 'img'
        img_dir.mkdir(exist_ok=True)

        # Generate main CSS file
        css_template = self.env.get_template('static/css/main.css.j2')
        content = css_template.render(config=self.config)
        (css_dir / 'main.css').write_text(content, encoding='utf-8')

        # Generate main JS file
        js_template = self.env.get_template('static/js/main.js.j2')
        content = js_template.render(config=self.config)
        (js_dir / 'main.js').write_text(content, encoding='utf-8')

        # Generate package.json if frontend pipeline is used
        if self.config.get('frontend_pipeline') != 'none':
            package_json_template = self.env.get_template('package.json.j2')
            content = package_json_template.render(
                project_name=self.project_name, config=self.config
            )
            (self.project_dir / 'package.json').write_text(content, encoding='utf-8')

            # Generate build configuration
            if self.config.get('frontend_pipeline') == 'vite':
                vite_config_template = self.env.get_template('vite.config.js.j2')
                content = vite_config_template.render(config=self.config)
                (self.project_dir / 'vite.config.js').write_text(content, encoding='utf-8')

    def _generate_docker_files(self):
        """Generate Docker files."""
        if not self.config.get('use_docker'):
            return

        console.print('🐳 Creating Docker files...')

        # Dockerfile
        dockerfile_template = self.env.get_template('Dockerfile.j2')
        content = dockerfile_template.render(project_name=self.project_name, config=self.config)
        (self.project_dir / 'Dockerfile').write_text(content, encoding='utf-8')

        # docker-compose.yml
        docker_compose_template = self.env.get_template('docker-compose.yml.j2')
        content = docker_compose_template.render(project_name=self.project_name, config=self.config)
        (self.project_dir / 'docker-compose.yml').write_text(content, encoding='utf-8')

        # entrypoint.sh — the development stack's initializer (issue #16): the
        # compose services run it to wait for dependencies, migrate, collect
        # static files, and then start the application. Written with explicit
        # LF line endings because /bin/sh rejects CRLF scripts and the default
        # text write would translate newlines on Windows hosts.
        entrypoint_template = self.env.get_template('entrypoint.sh.j2')
        content = entrypoint_template.render(project_name=self.project_name, config=self.config)
        entrypoint_path = self.project_dir / 'entrypoint.sh'
        entrypoint_path.write_text(content, encoding='utf-8', newline='\n')

        # .dockerignore
        dockerignore_template = self.env.get_template('dockerignore.j2')
        content = dockerignore_template.render(config=self.config)
        (self.project_dir / '.dockerignore').write_text(content, encoding='utf-8')

    def _generate_ci_files(self):
        """Generate CI configuration files."""
        if self.config.get('ci_tool') == 'none':
            return

        console.print('🔄 Creating CI configuration...')

        if self.config.get('ci_tool') == 'github-actions':
            github_dir = self.project_dir / '.github' / 'workflows'
            github_dir.mkdir(parents=True, exist_ok=True)

            ci_template = self.env.get_template('.github/workflows/ci.yml.j2')
            content = ci_template.render(project_name=self.project_name, config=self.config)
            (github_dir / 'ci.yml').write_text(content, encoding='utf-8')
