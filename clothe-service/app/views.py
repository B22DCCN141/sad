from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Clothing
from .serializers import ClothingSerializer


class ClothingListCreate(APIView):
    """
    GET  /clothes/   → Danh sách (hỗ trợ filter: category, size, gender, brand)
    POST /clothes/   → Thêm sản phẩm mới
    """

    def get(self, request):
        qs = Clothing.objects.all()
        for field in ['category', 'size', 'gender', 'brand']:
            val = request.GET.get(field)
            if val:
                qs = qs.filter(**{f'{field}__icontains' if field == 'brand' else field: val})
        is_active = request.GET.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        serializer = ClothingSerializer(qs, many=True)
        return Response({'count': qs.count(), 'results': serializer.data})

    def post(self, request):
        serializer = ClothingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClothingDetail(APIView):
    """
    GET    /clothes/<pk>/  → Chi tiết
    PUT    /clothes/<pk>/  → Cập nhật
    DELETE /clothes/<pk>/  → Soft delete (is_active = False)
    """

    def get(self, request, pk):
        obj = get_object_or_404(Clothing, pk=pk)
        return Response(ClothingSerializer(obj).data)

    def put(self, request, pk):
        obj = get_object_or_404(Clothing, pk=pk)
        serializer = ClothingSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = get_object_or_404(Clothing, pk=pk)
        obj.is_active = False
        obj.save()
        return Response(
            {'message': f'Sản phẩm "{obj.name}" đã được ẩn.'},
            status=status.HTTP_200_OK,
        )


class ClothingStockCheck(APIView):
    """
    GET /clothes/<pk>/stock/  → Kiểm tra tồn kho (dùng bởi cart/order-service)
    """

    def get(self, request, pk):
        obj = get_object_or_404(Clothing, pk=pk, is_active=True)
        return Response({
            'id': obj.id,
            'name': obj.name,
            'size': obj.size,
            'color': obj.color,
            'stock': obj.stock,
            'available': obj.stock > 0,
        })
