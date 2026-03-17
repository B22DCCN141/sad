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
            return Response({"error": "Service not found"}, status=404)

        # 1. Tạo URL gốc sạch (ví dụ: http://cart-service:8000/carts/)
        url = base_url.rstrip('/') + '/'

        # 2. Nối phần path (ví dụ: 3/items/1)
        if path:
            # strip('/') để dọn dẹp dấu gạch chéo thừa, sau đó thêm / ở cuối
            url += str(path).strip('/') + '/'

        # Log để Dũng xem link cuối cùng trong Docker terminal
        print(f"\n[GATEWAY] Forwarding to: {url}")

        try:
            method = request.method.lower()
            request_kwargs = {
                "method": method,
                "url": url,
                "params": request.GET,
                "timeout": 10
            }
            if method in ['post', 'put', 'patch', 'delete'] and request.data:
                request_kwargs["json"] = request.data

            resp = requests.request(**request_kwargs)

            if resp.status_code == 204 or not resp.text.strip():
                return Response(None, status=resp.status_code)

            try:
                return Response(resp.json(), status=resp.status_code)
            except ValueError:
                return Response({"detail": "Not JSON", "raw": resp.text[:100]}, status=resp.status_code)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    # Chấp nhận mọi phương thức
    def get(self, request, service_name, path=None):
        return self.handle_request(request, service_name, path)

    def post(self, request, service_name, path=None):
        return self.handle_request(request, service_name, path)

    def put(self, request, service_name, path=None):
        return self.handle_request(request, service_name, path)

    def delete(self, request, service_name, path=None):
        return self.handle_request(request, service_name, path)