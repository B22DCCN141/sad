from django.db import models


class Order(models.Model):
    # Thông tin khách hàng
    customer_id = models.IntegerField()

    # Thông tin thanh toán & vận chuyển
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    ship_method = models.CharField(max_length=100, null=True, blank=True)
    pay_method = models.CharField(max_length=100, null=True, blank=True)

    # Trạng thái đơn hàng
    status = models.CharField(max_length=50, default='Pending')  # Pending, Processing, Shipped, Delivered

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - User {self.customer_id}"


class OrderItem(models.Model):
    # Liên kết với bảng Order ở trên
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)

    # Legacy field for old flows
    book_id = models.IntegerField(null=True, blank=True)
    product_type = models.CharField(max_length=20, default='book')
    product_id = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=15, decimal_places=2)  # Lưu giá tại thời điểm mua

    def __str__(self):
        pid = self.product_id if self.product_id is not None else self.book_id
        return f"{self.quantity} x {self.product_type}:{pid} (Order {self.order.id})"