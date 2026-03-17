import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class OrderAction(APIView):
    # Dùng pk=None để khớp với URL orders/<int:pk>/ nếu có gọi GET
    def get(self, request, pk=None):
        return Response({"message": "Order Service is active"}, status=200)

    def post(self, request, pk=None):
        customer_id = request.data.get('customer_id')
        # Danh sách ID sách người dùng đã tick từ trang Cart
        selected_items = request.data.get('selected_items', [])

        if not selected_items:
            return Response({"error": "Bạn chưa chọn sản phẩm nào để thanh toán!"}, status=400)

        try:
            # 1. Gọi sang Cart Service để lấy danh sách món hàng hiện có
            # Gọi nội bộ Docker nên dùng http://cart-service:8000/
            cart_res = requests.get(f"http://cart-service:8000/carts/{customer_id}/")
            if cart_res.status_code != 200:
                return Response({"error": "Không thể lấy dữ liệu giỏ hàng"}, status=404)

            cart_data = cart_res.json()
            all_items = cart_data.get('items', [])

            # 2. Lọc ra những món hàng thực sự nằm trong danh sách đã tick
            # Ép kiểu string để so sánh cho chắc
            sel_ids = [str(sid) for sid in selected_items]
            items_to_delete = [i for i in all_items if str(i['book_id']) in sel_ids]

            # 3. LOGIC XÓA: Gọi lệnh DELETE sang Cart Service cho từng món
            # Dùng đúng cái URL carts/<uid>/items/<bid>/ mà Dũng bảo là chạy ổn rồi
            for item in items_to_delete:
                book_id = item['book_id']
                requests.delete(f"http://cart-service:8000/carts/{customer_id}/items/{book_id}/")

            # 4. Trả về thành công để Frontend hiện Overlay
            return Response({
                "status": "Success",
                "message": f"Đã thanh toán và xóa {len(items_to_delete)} món khỏi giỏ hàng"
            }, status=201)

        except Exception as e:
            return Response({"error": f"Lỗi kết nối giữa các service: {str(e)}"}, status=500)