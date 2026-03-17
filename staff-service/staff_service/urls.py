# staff-service/staff_service/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Quan trọng: Để trống đường dẫn để nó trỏ thẳng vào app.urls
    path('staff/', include('app.urls')),
]