import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerSerializer

class CustomerListCreate(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            # Tự động gọi sang Cart Service
            try:
                requests.post("http://cart-service:8000/carts/", json={"customer_id": customer.id})
            except:
                pass
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# Trong hàm perform_create hoặc logic sau khi save Customer thành công
def create_cart_for_customer(customer_id):
    cart_data = {"customer_id": customer_id}
    # Gọi sang Cart Service thông qua tên service trong Docker
    requests.post("http://cart-service:8003/api/carts/", json=cart_data)