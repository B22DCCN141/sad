from rest_framework import generics
from .models import Rating
from .serializers import RatingSerializer

class RatingListCreate(generics.ListCreateAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        queryset = Rating.objects.all()
        # Lấy book_id từ URL (ví dụ: ?book_id=7)
        book_id = self.request.query_params.get('book_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        return queryset

    def perform_create(self, serializer):
        # Lưu đánh giá mới
        serializer.save()