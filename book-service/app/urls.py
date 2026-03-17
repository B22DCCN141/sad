from django.urls import path
from .views import BookListCreate, BookDetailUpdateDelete

urlpatterns = [
    # Cho danh sách và thêm mới
    path('books/', BookListCreate.as_view(), name='book-list-create'),

    # CHO SỬA VÀ XÓA (Cần có <int:pk>)
    path('books/<int:pk>/', BookDetailUpdateDelete.as_view(), name='book-detail-update-delete'),
]