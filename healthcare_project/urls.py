from django.contrib import admin
from django.urls import path, include
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import connection
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


class HealthCheckView(APIView):
    """
    Health check endpoint to test API server and PostgreSQL connectivity.
    Endpoint: GET /api/health/
    """
    permission_classes = [AllowAny]

    def get(self, request):
        db_status = "ok"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
        except Exception as e:
            db_status = f"error: {str(e)}"

        return Response(
            {
                "status": "healthy" if db_status == "ok" else "degraded",
                "database": db_status,
                "service": "Healthcare Backend System",
                "version": "1.0.0",
            }
        )


class RootWelcomeView(APIView):
    """
    Root API discovery index.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "message": "Welcome to the Healthcare Management Backend API",
                "version": "1.0.0",
                "documentation": {
                    "swagger_ui": "/api/docs/",
                    "redoc": "/api/redoc/",
                    "openapi_schema": "/api/schema/",
                },
                "endpoints": {
                    "auth": {
                        "register": "/api/auth/register/",
                        "login": "/api/auth/login/",
                        "profile": "/api/auth/me/",
                        "refresh": "/api/auth/token/refresh/",
                    },
                    "patients": "/api/patients/",
                    "doctors": "/api/doctors/",
                    "mappings": "/api/mappings/",
                    "health": "/api/health/",
                },
            }
        )


urlpatterns = [
    path("", RootWelcomeView.as_view(), name="root-index"),
    path("admin/", admin.site.urls),
    path("api/health/", HealthCheckView.as_view(), name="health-check"),
    # API Endpoints
    path("api/auth/", include("authentication.urls")),
    path("api/patients/", include("patients.urls")),
    path("api/doctors/", include("doctors.urls")),
    path("api/mappings/", include("mappings.urls")),
    # OpenAPI & Swagger Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
