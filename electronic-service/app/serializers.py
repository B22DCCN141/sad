from rest_framework import serializers
from .models import Electronic


class ElectronicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Electronic
        fields = [
            'id', 'name', 'brand', 'model_number', 'category',
            'description', 'price', 'image_url', 'stock', 'warranty_months',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
