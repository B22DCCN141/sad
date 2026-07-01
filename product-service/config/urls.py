"""
URL configuration cho toàn bộ Product Service.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Catalog module: tất cả product API
    path('', include('modules.catalog.presentation.api.urls')),
]
