from django.urls import path
from .views import CartAction  # Phải khớp với tên class trong views.py

urlpatterns = [
    # Đường dẫn để Customer Service gọi tự động hoặc để POST thêm hàng
    path('carts/', CartAction.as_view()),

    # Đường dẫn để xem chi tiết giỏ hàng của một khách hàng cụ thể
    path('carts/<int:customer_id>/', CartAction.as_view()),
]