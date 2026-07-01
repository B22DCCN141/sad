"""
Category API Views - Presentation Layer.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.catalog.infrastructure.models.product_model import CategoryModel
from modules.catalog.infrastructure.repositories.category_repository_impl import DjangoCategoryRepository
from modules.catalog.presentation.api.serializers.product_serializer import CategorySerializer


class CategoryListCreateView(APIView):
    """
    GET  /categories/  → Danh sách danh mục
    POST /categories/  → Tạo danh mục mới
    """

    def get(self, request):
        repo = DjangoCategoryRepository()
        categories = repo.get_all(active_only=False)
        ids = [c.id for c in categories]
        qs = CategoryModel.objects.select_related('parent').filter(pk__in=ids)
        serializer = CategorySerializer(qs, many=True)
        return Response({'count': qs.count(), 'results': serializer.data})

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    """
    GET  /categories/<pk>/  → Chi tiết danh mục
    PUT  /categories/<pk>/  → Cập nhật danh mục
    """

    def get(self, request, pk):
        try:
            cat = CategoryModel.objects.select_related('parent').get(pk=pk)
        except CategoryModel.DoesNotExist:
            return Response({'error': 'Danh mục không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CategorySerializer(cat).data)

    def put(self, request, pk):
        try:
            cat = CategoryModel.objects.get(pk=pk)
        except CategoryModel.DoesNotExist:
            return Response({'error': 'Danh mục không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(cat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
