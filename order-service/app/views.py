import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem


class OrderAction(APIView):
    # Dùng pk=None để khớp với URL orders/<int:pk>/ nếu có gọi GET
    def get(self, request, pk=None):
        return Response({"message": "Order Service is active"}, status=200)

    def post(self, request, pk=None):
        customer_id = request.data.get('customer_id')
        ship_method = request.data.get('ship_method')
        pay_method = request.data.get('pay_method')
        # Danh sách item_key dạng "type:id" người dùng đã tick từ trang Cart
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
            sel_keys = [str(sid) for sid in selected_items]
            items_to_order = [i for i in all_items if str(i.get('item_key')) in sel_keys]

            if not items_to_order:
                return Response({"error": "Không có sản phẩm hợp lệ để thanh toán"}, status=400)

            # 3. Tạo order và order items
            total = sum(float(i.get('subtotal', 0)) for i in items_to_order)
            order = Order.objects.create(
                customer_id=customer_id,
                total=total,
                ship_method=ship_method,
                pay_method=pay_method,
                status='Processing',
            )

            for item in items_to_order:
                p_type = item.get('product_type', 'book')
                p_id = item.get('product_id', item.get('book_id'))
                OrderItem.objects.create(
                    order=order,
                    book_id=p_id if p_type == 'book' else None,
                    product_type=p_type,
                    product_id=p_id,
                    quantity=int(item.get('quantity', 1)),
                    price=float(item.get('price', 0)),
                )

            # 4. Xóa item đã thanh toán khỏi cart
            for item in items_to_order:
                p_type = item.get('product_type', 'book')
                p_id = item.get('product_id', item.get('book_id'))
                requests.delete(
                    f"http://cart-service:8000/carts/{customer_id}/items/{p_id}/",
                    params={'product_type': p_type},
                    timeout=3,
                )

            # 5. Trả về thành công để Frontend hiện Overlay
            return Response({
                "status": "Success",
                "order_id": order.id,
                "message": f"Đã thanh toán và xóa {len(items_to_order)} món khỏi giỏ hàng"
            }, status=201)

        except Exception as e:
            return Response({"error": f"Lỗi kết nối giữa các service: {str(e)}"}, status=500)