from rest_framework import generics
from .models import Rating
from .serializers import RatingSerializer

class RatingListCreate(generics.ListCreateAPIView):
    serializer_class = RatingSerializer

    def get_queryset(self):
        queryset = Rating.objects.all()
        product_type = self.request.query_params.get('product_type')
        product_id = self.request.query_params.get('product_id')

        if product_type and product_id:
            return queryset.filter(product_type=product_type, product_id=product_id)

        # Legacy filter: ?book_id=7
        book_id = self.request.query_params.get('book_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        return queryset

    def perform_create(self, serializer):
        product_type = self.request.data.get('product_type', 'book')
        product_id = self.request.data.get('product_id')
        book_id = self.request.data.get('book_id')

        # Backward compatibility for old book payload
        if product_id is None and book_id is not None:
            product_id = book_id
            product_type = 'book'

        serializer.save(
            product_type=product_type,
            product_id=product_id,
            book_id=product_id if product_type == 'book' else None,
        )