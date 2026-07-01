"""
Serializers - Presentation Layer.
Chuyển đổi dữ liệu giữa HTTP request/response và domain entities.
"""
from rest_framework import serializers
from modules.catalog.infrastructure.models.product_model import (
    ProductModel, CategoryModel, BrandModel
)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandModel
        fields = ['id', 'name', 'slug', 'description', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = CategoryModel
        fields = ['id', 'name', 'slug', 'description', 'parent', 'parent_name', 'is_active']


class ProductSerializer(serializers.ModelSerializer):
    """
    Product serializer với category và brand nested (read) / id (write).
    attributes là JSONField linh hoạt theo từng loại sản phẩm.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)

    class Meta:
        model = ProductModel
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock',
            'category',
            'category_name',
            'brand',
            'brand_name',
            'attributes',  # JSONB linh hoạt
            'image_url',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_name', 'brand_name']


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer rút gọn cho danh sách sản phẩm."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)

    class Meta:
        model = ProductModel
        fields = ['id', 'name', 'price', 'stock', 'category_name', 'brand_name',
                  'attributes', 'image_url', 'is_active']
