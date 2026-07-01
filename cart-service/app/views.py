import requests
from urllib.parse import quote
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem


def _safe_get_json(url, timeout=2):
    try:
        res = requests.get(url, timeout=timeout)
        if res.status_code != 200:
            return []
        return res.json()
    except Exception:
        return []


def _placeholder_image(text):
        import base64
        safe_text = str(text or 'Product')[:28]
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="800" viewBox="0 0 600 800">
    <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#0f172a"/>
            <stop offset="100%" stop-color="#334155"/>
        </linearGradient>
    </defs>
    <rect width="600" height="800" fill="url(#g)"/>
    <rect x="86" y="108" width="428" height="584" rx="30" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.14)"/>
    <text x="50%" y="44%" text-anchor="middle" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#ffffff">Bookstore</text>
    <text x="50%" y="53%" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" fill="#cbd5e1">{safe_text}</text>
    <text x="50%" y="89%" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#e2e8f0">No image</text>
</svg>'''
        encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{encoded}"


def _build_product_maps():
    books = _safe_get_json("http://book-service:8000/books/")
    electronics_raw = _safe_get_json("http://electronic-service:8000/electronics/")
    products_raw = _safe_get_json("http://product-service:8000/products/")

    electronics = electronics_raw if isinstance(electronics_raw, list) else electronics_raw.get("results", [])
    products = products_raw if isinstance(products_raw, list) else products_raw.get("results", [])

    return {
        "book": {
            int(b["id"]): {
                "title": b.get("title", "Book"),
                "subtitle": b.get("author", "Book Service"),
                "price": float(b.get("price", 0)),
                "image_url": b.get("image_url") or _placeholder_image(b.get("title", "Book")),
            }
            for b in books if isinstance(b, dict) and b.get("id") is not None
        },
        "electronic": {
            int(e["id"]): {
                "title": e.get("name", "Electronic"),
                "subtitle": e.get("brand", "Electronic Service"),
                "price": float(e.get("price", 0)),
                "image_url": e.get("image_url") or _placeholder_image(e.get("name", "Electronic")),
            }
            for e in electronics if isinstance(e, dict) and e.get("id") is not None
        },
        "product": {
            int(p["id"]): {
                "title": p.get("name", "Product"),
                "subtitle": p.get("category_name") or p.get("brand_name") or "Product Service",
                "price": float(p.get("price", 0)),
                "image_url": p.get("image_url") or _placeholder_image(p.get("name", "Product")),
            }
            for p in products if isinstance(p, dict) and p.get("id") is not None
        },
    }


class CartAction(APIView):
    # Xem giỏ hàng theo customer_id
    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            product_maps = _build_product_maps()

            items = CartItem.objects.filter(cart=cart)
            detailed_items = []
            total = 0
            for item in items:
                item_type = item.product_type or 'book'
                item_id = item.product_id if item.product_id is not None else item.book_id
                if item_id is None:
                    continue

                p_info = product_maps.get(item_type, {}).get(int(item_id), {})
                unit_price = float(p_info.get('price', 0))
                subtotal = unit_price * item.quantity
                total += subtotal
                detailed_items.append({
                    "book_id": item.book_id,
                    "product_type": item_type,
                    "product_id": int(item_id),
                    "item_key": f"{item_type}:{int(item_id)}",
                    "title": p_info.get('title', 'N/A'),
                    "subtitle": p_info.get('subtitle', ''),
                    "image_url": p_info.get('image_url', _placeholder_image('No Image')),
                    "quantity": item.quantity,
                    "price": unit_price,
                    "subtotal": subtotal
                })
            return Response({"customer_id": customer_id, "total_price": total, "items": detailed_items})
        except Cart.DoesNotExist:
            return Response({"error": "Cart empty"}, status=404)

    # Thêm sản phẩm vào giỏ
        # 2. Thêm/Sửa sản phẩm
    def post(self, request):
        cust_id = request.data.get('customer_id')
        product_type = request.data.get('product_type', 'book')
        product_id = request.data.get('product_id', request.data.get('book_id'))
        qty = int(request.data.get('quantity', 1))
        mode = request.data.get('mode', 'add')

        if not cust_id or product_id is None:
            return Response({"error": "customer_id và product_id là bắt buộc"}, status=400)

        product_type = str(product_type).strip().lower()
        if product_type not in ['book', 'electronic', 'product']:
            return Response({"error": "product_type không hợp lệ"}, status=400)

        product_id = int(product_id)

        # Tìm hoặc tạo Giỏ hàng cha
        cart, _ = Cart.objects.get_or_create(customer_id=cust_id)

        # Tìm hoặc tạo Dòng chi tiết (CartItem)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_type=product_type,
            product_id=product_id,
            defaults={'quantity': 0, 'book_id': product_id if product_type == 'book' else None}
        )

        if item.product_type == 'book' and item.book_id is None:
            item.book_id = item.product_id

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
            product_type = request.query_params.get('product_type', 'book')
            cart.items.filter(product_type=product_type, product_id=book_id).delete()
        else:
            # Xóa cả giỏ (khi thanh toán xong)
            cart.delete()

        return Response(status=204)