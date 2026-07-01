from django.db import models


class Electronic(models.Model):
    """Model đại diện cho một sản phẩm điện tử."""

    CATEGORY_CHOICES = [
        ('phone', 'Điện thoại'),
        ('laptop', 'Laptop'),
        ('tablet', 'Máy tính bảng'),
        ('tv', 'Tivi'),
        ('audio', 'Âm thanh'),
        ('camera', 'Camera'),
        ('accessory', 'Phụ kiện'),
        ('other', 'Khác'),
    ]

    name = models.CharField(max_length=255, verbose_name='Tên sản phẩm')
    brand = models.CharField(max_length=100, verbose_name='Thương hiệu')
    model_number = models.CharField(max_length=100, blank=True, verbose_name='Mã model')
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name='Danh mục'
    )
    description = models.TextField(blank=True, verbose_name='Mô tả')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Giá (VNĐ)')
    image_url = models.URLField(blank=True, null=True, verbose_name='Ảnh sản phẩm')
    stock = models.IntegerField(default=0, verbose_name='Tồn kho')
    warranty_months = models.IntegerField(default=12, verbose_name='Bảo hành (tháng)')
    is_active = models.BooleanField(default=True, verbose_name='Đang bán')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sản phẩm điện tử'
        verbose_name_plural = 'Sản phẩm điện tử'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand} {self.name} ({self.model_number})"
