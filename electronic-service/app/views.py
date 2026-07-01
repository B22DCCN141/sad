from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Electronic
from .serializers import ElectronicSerializer


class ElectronicListCreate(APIView):
    """
    GET  /electronics/         → Lấy danh sách tất cả sản phẩm điện tử
    POST /electronics/         → Thêm sản phẩm điện tử mới (Manager/Staff)
    """

    def get(self, request):
        # Hỗ trợ lọc theo category, is_active
        queryset = Electronic.objects.all()
        category = request.GET.get('category')
        is_active = request.GET.get('is_active')
        brand = request.GET.get('brand')

        if category:
            queryset = queryset.filter(category=category)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        serializer = ElectronicSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data,
        })

    def post(self, request):
        serializer = ElectronicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ElectronicDetail(APIView):
    """
    GET    /electronics/<pk>/  → Chi tiết sản phẩm
    PUT    /electronics/<pk>/  → Cập nhật sản phẩm
    DELETE /electronics/<pk>/  → Xóa sản phẩm (soft delete)
    """

    def get(self, request, pk):
        electronic = get_object_or_404(Electronic, pk=pk)
        return Response(ElectronicSerializer(electronic).data)

    def put(self, request, pk):
        electronic = get_object_or_404(Electronic, pk=pk)
        serializer = ElectronicSerializer(electronic, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        electronic = get_object_or_404(Electronic, pk=pk)
        # Soft delete: đánh dấu is_active = False thay vì xóa thật
        electronic.is_active = False
        electronic.save()
        return Response(
            {'message': f'Sản phẩm "{electronic.name}" đã bị ẩn.'},
            status=status.HTTP_200_OK,
        )


class ElectronicStockCheck(APIView):
    """
    GET /electronics/<pk>/stock/  → Kiểm tra tồn kho (dùng bởi cart-service, order-service)
    """

    def get(self, request, pk):
        electronic = get_object_or_404(Electronic, pk=pk, is_active=True)
        return Response({
            'id': electronic.id,
            'name': electronic.name,
            'stock': electronic.stock,
            'available': electronic.stock > 0,
        })
