"""
Product API Views - Presentation Layer.
Gọi Application Service thay vì trực tiếp ORM.
Đây là pattern DDD: Presentation → Application → Domain → Infrastructure.
"""
from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.catalog.application.commands.create_product import CreateProductCommand
from modules.catalog.application.commands.update_product import UpdateProductCommand
from modules.catalog.application.queries.product_queries import (
    CheckStockQuery, GetProductQuery, ListProductsQuery,
)
from modules.catalog.application.services.product_service import ProductService
from modules.catalog.infrastructure.models.product_model import ProductModel
from modules.catalog.infrastructure.repositories.product_repository_impl import DjangoProductRepository
from modules.catalog.presentation.api.serializers.product_serializer import (
    ProductSerializer, ProductListSerializer
)


def _get_product_service() -> ProductService:
    """Factory: khởi tạo ProductService với concrete repository (DI thủ công)."""
    return ProductService(product_repository=DjangoProductRepository())


class ProductListCreateView(APIView):
    """
    GET  /products/   → Danh sách sản phẩm (filter theo category, brand, price)
    POST /products/   → Tạo sản phẩm mới
    """

    def get(self, request):
        service = _get_product_service()
        query = ListProductsQuery(
            category_id=request.GET.get('category_id'),
            brand_id=request.GET.get('brand_id'),
            is_active=request.GET.get('is_active', 'true').lower() != 'false',
            min_price=request.GET.get('min_price'),
            max_price=request.GET.get('max_price'),
        )
        products_domain = service.list_products(query)

        # Lấy ORM objects để serialize (presentation layer dùng ORM serializer)
        ids = [p.id for p in products_domain]
        qs = ProductModel.objects.select_related('category', 'brand').filter(pk__in=ids)
        # Preserve ordering
        id_order = {pid: idx for idx, pid in enumerate(ids)}
        qs_sorted = sorted(qs, key=lambda obj: id_order.get(obj.id, 999))

        serializer = ProductListSerializer(qs_sorted, many=True)
        return Response({
            'count': len(qs_sorted),
            'results': serializer.data,
        })

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            price = Decimal(str(data['price']))
        except InvalidOperation:
            return Response({'price': 'Giá không hợp lệ.'}, status=status.HTTP_400_BAD_REQUEST)

        command = CreateProductCommand(
            name=data['name'],
            description=data.get('description', ''),
            price=price,
            stock=data.get('stock', 0),
            category_id=data['category'].id,
            brand_id=data['brand'].id if data.get('brand') else None,
            attributes=data.get('attributes', {}),
            image_url=data.get('image_url', ''),
        )

        service = _get_product_service()
        try:
            product = service.create_product(command)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        orm = ProductModel.objects.select_related('category', 'brand').get(pk=product.id)
        return Response(ProductSerializer(orm).data, status=status.HTTP_201_CREATED)


class ProductDetailView(APIView):
    """
    GET    /products/<pk>/  → Chi tiết sản phẩm
    PUT    /products/<pk>/  → Cập nhật sản phẩm
    DELETE /products/<pk>/  → Ẩn sản phẩm (soft delete)
    """

    def get(self, request, pk):
        service = _get_product_service()
        product = service.get_product(GetProductQuery(product_id=pk))
        if product is None:
            return Response({'error': 'Sản phẩm không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)
        orm = ProductModel.objects.select_related('category', 'brand').get(pk=pk)
        return Response(ProductSerializer(orm).data)

    def put(self, request, pk):
        serializer = ProductSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        command = UpdateProductCommand(
            product_id=pk,
            name=data.get('name'),
            description=data.get('description'),
            price=Decimal(str(data['price'])) if data.get('price') else None,
            stock=data.get('stock'),
            category_id=data['category'].id if data.get('category') else None,
            brand_id=data['brand'].id if data.get('brand') else None,
            attributes=data.get('attributes'),
            image_url=data.get('image_url'),
            is_active=data.get('is_active'),
        )

        service = _get_product_service()
        try:
            product = service.update_product(command)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        orm = ProductModel.objects.select_related('category', 'brand').get(pk=product.id)
        return Response(ProductSerializer(orm).data)

    def delete(self, request, pk):
        service = _get_product_service()
        try:
            product = service.deactivate_product(pk)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {'message': f'Sản phẩm "{product.name}" đã bị ẩn.'},
            status=status.HTTP_200_OK,
        )


class ProductStockView(APIView):
    """
    GET /products/<pk>/stock/  → Kiểm tra tồn kho
    Endpoint dùng bởi cart-service và order-service.
    """

    def get(self, request, pk):
        service = _get_product_service()
        result = service.check_stock(CheckStockQuery(product_id=pk))
        if not result['found']:
            return Response({'error': 'Sản phẩm không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class ProductByCategoryView(APIView):
    """
    GET /categories/<category_id>/products/  → Sản phẩm theo danh mục
    Minh họa: category là dữ liệu, filter theo category_id.
    """

    def get(self, request, category_id):
        service = _get_product_service()
        query = ListProductsQuery(category_id=category_id, is_active=True)
        products_domain = service.list_products(query)

        ids = [p.id for p in products_domain]
        qs = ProductModel.objects.select_related('category', 'brand').filter(pk__in=ids)
        serializer = ProductListSerializer(qs, many=True)
        return Response({
            'category_id': category_id,
            'count': len(ids),
            'results': serializer.data,
        })
