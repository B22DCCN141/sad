from django.urls import path
from .views import RatingListCreate # Hoặc tên Class View Dũng đã viết ở views.py

urlpatterns = [
    # Đây là đường dẫn mà Gateway sẽ gọi tới
    path('ratings/', RatingListCreate.as_view(), name='rating-list-create'),
]