import requests
from rest_framework.views import APIView
from rest_framework.response import Response


class OrderCreateView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        # Gọi Cart Service lấy tổng tiền
        cart_res = requests.get(f"http://cart-service:8000/carts/{customer_id}/")
        total = cart_res.json().get('total_price', 0)

        # Lưu Order vào DB của mình (tự viết model Order nhé)
        # order = Order.objects.create(customer_id=customer_id, total=total)

        # GỌI LIÊN DỊCH VỤ (Req 4.3.4)
        requests.post("http://pay-service:8000/payments/", json={"amount": total})
        requests.post("http://ship-service:8000/shipping/", json={"customer_id": customer_id})

        return Response({"status": "Order Placed", "total": total})