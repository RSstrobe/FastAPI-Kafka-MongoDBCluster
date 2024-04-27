"""config URL Configuration"""
from django.contrib import admin
from django.urls import include, path

from config import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("movies.api.urls")),
]

if settings.DEBUG:
    urlpatterns.append(path("debug/", include("debug_toolbar.urls")))
