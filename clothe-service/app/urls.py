from django.urls import path
from .views import ClothingListCreate, ClothingDetail, ClothingStockCheck

urlpatterns = [
    path('clothes/', ClothingListCreate.as_view(), name='clothing-list-create'),
    path('clothes/<int:pk>/', ClothingDetail.as_view(), name='clothing-detail'),
    path('clothes/<int:pk>/stock/', ClothingStockCheck.as_view(), name='clothing-stock'),
]
