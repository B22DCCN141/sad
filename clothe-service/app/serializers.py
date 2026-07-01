from rest_framework import serializers
from .models import Clothing


class ClothingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clothing
        fields = [
            'id', 'name', 'brand', 'category', 'size', 'color',
            'gender', 'material', 'description', 'price', 'stock',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
