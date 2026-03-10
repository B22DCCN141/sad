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
    def post(self, request):
        customer_id = request.data.get("customer_id")
        book_id = request.data.get("book_id")
        quantity = int(request.data.get("quantity", 1))

        cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
        item, created = CartItem.objects.get_or_create(cart=cart, book_id=book_id)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        return Response({"message": "Updated"}, status=201)