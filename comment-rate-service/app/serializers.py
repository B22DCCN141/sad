from rest_framework import serializers
from .models import Rating

class RatingSerializer(serializers.ModelSerializer):
    # Thêm trường created_at nếu Dũng muốn hiển thị thời gian đánh giá
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)

    class Meta:
        model = Rating
        # Liệt kê các trường trùng với Model Rating của Dũng
        fields = ['id', 'book_id', 'customer_id', 'stars', 'comment', 'created_at']