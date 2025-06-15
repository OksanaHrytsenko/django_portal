from django.urls import path, re_path
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import SwaggerApiDoc


schema_view = get_schema_view(
    openapi.Info(
        title='Главный дед мороз',
        default_version='v 0.0.1',
        description='Документация по АРI к ресурсу кулинария',
        terms_of_service='https://www.google.com/policies/terms',
        contact=openapi.Contact(email='0682112130o@gmail.com'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)
urlpatterns = [
    path("swagger-ui/", SwaggerApiDoc.as_view(), name="swagger-ui"),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=1), name='schema-json'),
]