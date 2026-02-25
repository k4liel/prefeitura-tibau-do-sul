from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework.schemas import get_schema_view


def healthcheck(_request):
    return JsonResponse({"status": "ok", "service": "tibau-backend"})


urlpatterns = [
    path("", include("apps.web.urls")),
    path("admin/", admin.site.urls),
    path("health/", healthcheck, name="healthcheck"),
    path(
        "api/schema/",
        get_schema_view(title="Tibau API", version="1.0.0"),
        name="api-schema",
    ),
    path("api/", include("apps.api_urls")),
]
