"""Generator for Django applications."""

from pathlib import Path

from .base import BaseGenerator


class DjangoAppsGenerator(BaseGenerator):
    """Generates Django applications (core, accounts, api, payments)."""

    def generate(self) -> None:
        """Generate Django applications based on config."""
        self.log('🏗️  Creating Django applications...')

        apps_dir = self.project_dir / 'apps'
        apps_dir.mkdir(exist_ok=True)
        self._create_init_file(apps_dir)

        if self.config.get('api_only'):
            self._create_api_app(apps_dir)
            if self.config.get('use_stripe'):
                self._create_payments_app_api(apps_dir)
        else:
            self._create_core_app(apps_dir)
            self._create_accounts_app(apps_dir)
            if self.config.get('use_drf'):
                self._create_api_app(apps_dir)
            if self.config.get('use_stripe'):
                self._create_payments_app(apps_dir)

    def _create_init_file(self, package_dir: Path) -> None:
        """Create __init__.py in a package directory."""
        self.write_file(package_dir / '__init__.py', '')

    def _create_core_app(self, apps_dir: Path) -> None:
        """Create the core app with HTMX demo."""
        self._create_django_app(apps_dir, 'core', is_core=True)

    def _create_accounts_app(self, apps_dir: Path) -> None:
        """Create the accounts app."""
        self._create_django_app(apps_dir, 'accounts')

    def _create_api_app(self, apps_dir: Path) -> None:
        """Create the API app with DRF health check."""
        self._create_django_app(apps_dir, 'api', is_api=True)

    def _create_django_app(
        self,
        apps_dir: Path,
        app_name: str,
        is_core: bool = False,
        is_api: bool = False,
    ) -> None:
        """Create a Django app with basic structure."""
        app_dir = apps_dir / app_name
        app_dir.mkdir(exist_ok=True)

        # Create __init__.py
        self._create_init_file(app_dir)

        # Create apps.py
        self._create_apps_py(app_dir, app_name)

        # Create models.py
        self._create_models_py(app_dir)

        # Create views.py
        self._create_views_py(app_dir, is_core=is_core, is_api=is_api)

        # Create admin.py
        self._create_admin_py(app_dir)

        # Create tests.py
        self._create_tests_py(app_dir, app_name)

        # Create urls.py
        self._create_app_urls_py(app_dir, app_name, is_core=is_core, is_api=is_api)

    def _create_apps_py(self, app_dir: Path, app_name: str) -> None:
        """Create apps.py for the app."""
        content = f"""from django.apps import AppConfig


class {app_name.title()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
"""
        self.write_file(app_dir / 'apps.py', content)

    def _create_models_py(self, app_dir: Path) -> None:
        """Create models.py for the app."""
        content = 'from django.db import models\n\n# Create your models here.\n'
        self.write_file(app_dir / 'models.py', content)

    def _create_views_py(self, app_dir: Path, is_core: bool = False, is_api: bool = False) -> None:
        """Create views.py based on app type."""
        if is_core:
            content = """from django.shortcuts import render
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
        elif is_api and self.config.get('use_drf'):
            content = """from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def health_check(request):
    \"\"\"API health check endpoint.\"\"\"
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)
"""
        else:
            content = 'from django.shortcuts import render\n\n# Create your views here.\n'

        self.write_file(app_dir / 'views.py', content)

    def _create_admin_py(self, app_dir: Path) -> None:
        """Create admin.py for the app."""
        content = 'from django.contrib import admin\n\n# Register your models here.\n'
        self.write_file(app_dir / 'admin.py', content)

    def _create_tests_py(self, app_dir: Path, app_name: str) -> None:
        """Create tests.py for the app."""
        content = f"""from django.test import TestCase


class {app_name.title()}TestCase(TestCase):
    def test_placeholder(self):
        \"\"\"Placeholder test.\"\"\"
        self.assertTrue(True)
"""
        self.write_file(app_dir / 'tests.py', content)

    def _create_app_urls_py(
        self, app_dir: Path, app_name: str, is_core: bool = False, is_api: bool = False
    ) -> None:
        """Create urls.py for the app."""
        if is_core:
            content = """from django.urls import path
from .views import HomeView, time_view

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('time/', time_view, name='time'),
]
"""
        elif is_api and self.config.get('use_drf'):
            content = """from django.urls import path
from .views import health_check

urlpatterns = [
    path('health/', health_check, name='api_health'),
]
"""
        else:
            content = """from django.urls import path

urlpatterns = [
    # Add your URL patterns here
]
"""
        self.write_file(app_dir / 'urls.py', content)

    def _create_payments_app(self, apps_dir: Path) -> None:
        """Create a payments app with Stripe integration (template views)."""
        app_dir = apps_dir / 'payments'
        app_dir.mkdir(exist_ok=True)

        self._create_init_file(app_dir)
        self._create_payments_apps_py(app_dir)
        self._create_payments_models_py(app_dir)
        self._create_payments_views_py(app_dir)
        self._create_payments_admin_py(app_dir)
        self._create_payments_signals_py(app_dir)
        self._create_payments_tests_py(app_dir)
        self._create_payments_urls_py(app_dir)

    def _create_payments_apps_py(self, app_dir: Path) -> None:
        """Create apps.py for payments app."""
        content = """from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments'
    
    def ready(self):
        import apps.payments.signals
"""
        self.write_file(app_dir / 'apps.py', content)

    def _create_payments_models_py(self, app_dir: Path) -> None:
        """Create models.py for payments app."""
        content = """from django.db import models
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
        self.write_file(app_dir / 'models.py', content)

    def _create_payments_views_py(self, app_dir: Path) -> None:
        """Create views.py for payments app (template-based)."""
        content = """from django.shortcuts import render, redirect
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
    \"\"\"Handle cancelled payment.\"\"\"
    messages.info(request, 'Payment was cancelled.')
    return render(request, 'payments/cancel.html')


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    \"\"\"Handle Stripe webhooks.\"\"\"
    
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
        \"\"\"Handle successful checkout session.\"\"\"
        order_id = session.get('metadata', {}).get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.status = 'completed'
                order.save()
            except Order.DoesNotExist:
                pass


class OrderListView(ListView):
    \"\"\"List user's orders.\"\"\"
    model = Order
    template_name = 'payments/orders.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
"""
        self.write_file(app_dir / 'views.py', content)

    def _create_payments_admin_py(self, app_dir: Path) -> None:
        """Create admin.py for payments app."""
        content = """from django.contrib import admin
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
        self.write_file(app_dir / 'admin.py', content)

    def _create_payments_signals_py(self, app_dir: Path) -> None:
        """Create signals.py for payments app."""
        content = """from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from djstripe.models import Customer


@receiver(post_save, sender=User)
def create_stripe_customer(sender, instance, created, **kwargs):
    \"\"\"Create a Stripe customer when a user is created.\"\"\"
    if created:
        Customer.get_or_create(subscriber=instance)
"""
        self.write_file(app_dir / 'signals.py', content)

    def _create_payments_tests_py(self, app_dir: Path) -> None:
        """Create tests.py for payments app."""
        content = """from django.test import TestCase
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
        self.write_file(app_dir / 'tests.py', content)

    def _create_payments_urls_py(self, app_dir: Path) -> None:
        """Create urls.py for payments app."""
        content = """from django.urls import path
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
        self.write_file(app_dir / 'urls.py', content)

    def _create_payments_app_api(self, apps_dir: Path) -> None:
        """Create a payments app with Stripe integration for API-only projects (DRF views)."""
        app_dir = apps_dir / 'payments'
        app_dir.mkdir(exist_ok=True)

        self._create_init_file(app_dir)
        self._create_payments_apps_py(app_dir)
        self._create_payments_models_py(app_dir)
        self._create_payments_serializers_py(app_dir)
        self._create_payments_api_views_py(app_dir)
        self._create_payments_admin_py(app_dir)
        self._create_payments_signals_py(app_dir)
        self._create_payments_api_tests_py(app_dir)
        self._create_payments_api_urls_py(app_dir)

    def _create_payments_serializers_py(self, app_dir: Path) -> None:
        """Create serializers.py for payments API app."""
        content = """from rest_framework import serializers
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
        self.write_file(app_dir / 'serializers.py', content)

    def _create_payments_api_views_py(self, app_dir: Path) -> None:
        """Create views.py for payments API app (DRF-based)."""
        content = """from rest_framework import status, viewsets
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
        self.write_file(app_dir / 'views.py', content)

    def _create_payments_api_tests_py(self, app_dir: Path) -> None:
        """Create tests.py for payments API app."""
        content = """from django.test import TestCase
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
        self.write_file(app_dir / 'tests.py', content)

    def _create_payments_api_urls_py(self, app_dir: Path) -> None:
        """Create urls.py for payments API app."""
        content = """from django.urls import path, include
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
        self.write_file(app_dir / 'urls.py', content)
