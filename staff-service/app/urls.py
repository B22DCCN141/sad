# staff-service/app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StaffViewSet

router = DefaultRouter()
# Để r'' (trống) vì tiền tố 'staff/' đã được định nghĩa ở file urls.py tổng
router.register(r'', StaffViewSet, basename='staff')

urlpatterns = [
    path('', include(router.urls)),
]