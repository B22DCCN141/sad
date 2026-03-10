import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class GatewayView(APIView):
    """
    API Gateway xử lý điều hướng yêu cầu đến 11 Microservices.
    """
    # Bản đồ các service chạy trong Docker
    SERVICE_MAP = {
        'staff': 'http://staff-service:8000/staff/',
        'manager': 'http://manager-service:8000/manager/',
        'customers': 'http://customer-service:8000/customers/',
        'catalog': 'http://catalog-service:8000/catalog/',
        'books': 'http://book-service:8000/books/',
        'carts': 'http://cart-service:8000/carts/',
        'orders': 'http://order-service:8000/orders/',
        'ship': 'http://ship-service:8000/shipping/',
        'pay': 'http://pay-service:8000/payments/',
        'ratings': 'http://comment-rate-service:8000/ratings/',
        'recommend': 'http://recommender-ai-service:8000/recommend/',
    }

    def handle_request(self, request, service_name, path=None):
        base_url = self.SERVICE_MAP.get(service_name)
        if not base_url:
            return Response({"error": f"Service '{service_name}' không tồn tại."}, status=404)

        # Xây dựng URL đầy đủ
        url = base_url if not path else f"{base_url}{path}/"

        try:
            method = request.method.lower()
            # Chuyển tiếp request đi
            resp = requests.request(
                method=method,
                url=url,
                json=request.data if method != 'get' else None,
                params=request.GET,
                timeout=10
            )
            return Response(resp.json(), status=resp.status_code)
        except Exception as e:
            return Response({"error": f"Lỗi Gateway: {str(e)}"}, status=500)

    # Chấp nhận mọi phương thức
    def get(self, request, service_name, path=None):
        return self.handle_request(request, service_name, path)

    def post(self, request, service_name, path=None):
        return self.handle_request(request, service_name, path)

    def put(self, request, service_name, path=None):
        return self.handle_request(request, service_name, path)

    def delete(self, request, service_name, path=None):
        return self.handle_request(request, service_name, path)