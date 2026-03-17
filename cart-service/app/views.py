import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer


class CartAction(APIView):
    # Xem giỏ hàng theo customer_id
    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            # Gọi Book Service lấy thông tin sách để hiển thị tên/giá
            try:
                book_res = requests.get("http://book-service:8000/books/", timeout=2)
                all_books = {b['id']: b for b in book_res.json()}
            except:
                all_books = {}

            items = CartItem.objects.filter(cart=cart)
            detailed_items = []
            total = 0
            for item in items:
                b_info = all_books.get(item.book_id, {})
                subtotal = float(b_info.get('price', 0)) * item.quantity
                total += subtotal
                detailed_items.append({
                    "book_id": item.book_id,
                    "title": b_info.get('title', 'N/A'),
                    "quantity": item.quantity,
                    "price": b_info.get('price', 0),
                    "subtotal": subtotal
                })
            return Response({"customer_id": customer_id, "total_price": total, "items": detailed_items})
        except Cart.DoesNotExist:
            return Response({"error": "Cart empty"}, status=404)

    # Thêm sản phẩm vào giỏ
        # 2. Thêm/Sửa sản phẩm
    def post(self, request):
        cust_id = request.data.get('customer_id')
        book_id = request.data.get('book_id')
        qty = int(request.data.get('quantity', 1))
        mode = request.data.get('mode', 'add')

        # Tìm hoặc tạo Giỏ hàng cha
        cart, _ = Cart.objects.get_or_create(customer_id=cust_id)

        # Tìm hoặc tạo Dòng chi tiết (CartItem)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            book_id=book_id,
            defaults={'quantity': 0}
        )

        if mode == 'overwrite':
            item.quantity = qty
        else:
            item.quantity += qty

        item.save()
        return Response({"status": "Success"}, status=200)

    # 3. Xóa sản phẩm
    def delete(self, request, customer_id, book_id=None):
        cart = Cart.objects.filter(customer_id=customer_id).first()
        if not cart:
            return Response(status=204)

        if book_id:
            # Xóa đúng món đó trong giỏ
            cart.items.filter(book_id=book_id).delete()
        else:
            # Xóa cả giỏ (khi thanh toán xong)
            cart.delete()

        return Response(status=204)