from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Trỏ vào file app/urls.py mà Dũng vừa tạo
    path('orders/', include('app.urls')),
]