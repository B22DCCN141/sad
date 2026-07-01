from django.urls import path
from .views import ElectronicListCreate, ElectronicDetail, ElectronicStockCheck

urlpatterns = [
    # Danh sách & Thêm mới
    path('electronics/', ElectronicListCreate.as_view(), name='electronic-list-create'),

    # Chi tiết, Sửa, Xóa
    path('electronics/<int:pk>/', ElectronicDetail.as_view(), name='electronic-detail'),

    # Endpoint kiểm tra tồn kho (dùng bởi cart-service / order-service)
    path('electronics/<int:pk>/stock/', ElectronicStockCheck.as_view(), name='electronic-stock'),
]
