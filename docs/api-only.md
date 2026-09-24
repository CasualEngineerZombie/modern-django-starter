# API-Only Projects

Pass `--api-only` to skip the frontend entirely and generate a **pure Django REST
Framework backend** — no templates, no static files, no build tooling.

```bash
modern-django-starter create shop_api --api-only
```

The remaining prompts still apply (Docker, PostgreSQL, cloud, storage, email, async,
Celery, Sentry, Stripe, CI), but a few choices are fixed to keep the backend minimal:

| Setting | API-only value |
|---|---|
| Django REST Framework | always enabled |
| Frontend pipeline | always `none` |
| Celery / Sentry defaults | `no` |
| CI tool default | `none` |

## Included

- **Django REST Framework** — `IsAuthenticated` by default, JWT as the default auth class
- **JWT auth** — `djangorestframework-simplejwt`
- **CORS** — `django-cors-headers` with `CORS_ALLOW_ALL_ORIGINS = True` in dev
- **API schema & docs** — `drf-spectacular` (Swagger UI)
- **Registration & auth endpoints** — `dj-rest-auth` + `django-allauth`

## Root URL configuration

The generated `urls.py` wires up everything for you:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    # API schema and docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Auth endpoints (JWT, registration, password reset)
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    # Main API
    path('api/', include('apps.api.urls')),
]
```

## Endpoints

| Path | Purpose |
|---|---|
| `/api/schema/` | OpenAPI schema (JSON) |
| `/api/docs/` | Swagger UI for the API |
| `/api/auth/login/` | JWT token obtain |
| `/api/auth/refresh/` | JWT token refresh |
| `/api/auth/` | dj-rest-auth endpoints (password reset, user, etc.) |
| `/api/auth/registration/` | User registration |
| `/api/health/` | Health check (`{"status": "healthy"}`) |
| `/admin/` | Django admin |

## Scope

The generated project includes a single `apps/api` app with a placeholder
`health_check` view. You add your own models, serializers, and views in `apps/api/` —
the auth, schema, and docs plumbing is already done.

!!! tip "Getting a token"
    ```bash
    curl -X POST http://localhost:8000/api/auth/login/ \
      -H 'Content-Type: application/json' \
      -d '{"username": "you", "password": "secret"}'
    ```

    Then send the JWT on every request:

    ```bash
    curl http://localhost:8000/api/health/ \
      -H 'Authorization: Bearer <access_token>'
    ```