from django.db import models


class Clothing(models.Model):
    """Model đại diện cho một sản phẩm quần áo."""

    CATEGORY_CHOICES = [
        ('shirt', 'Áo sơ mi'),
        ('tshirt', 'Áo thun'),
        ('pants', 'Quần dài'),
        ('shorts', 'Quần short'),
        ('dress', 'Đầm / Váy'),
        ('jacket', 'Áo khoác'),
        ('sportswear', 'Đồ thể thao'),
        ('underwear', 'Đồ lót'),
        ('accessory', 'Phụ kiện thời trang'),
        ('other', 'Khác'),
    ]

    SIZE_CHOICES = [
        ('XS', 'XS'), ('S', 'S'), ('M', 'M'),
        ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL'),
        ('freesize', 'Free Size'),
    ]

    GENDER_CHOICES = [
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('unisex', 'Unisex'),
        ('kid', 'Trẻ em'),
    ]

    name        = models.CharField(max_length=255, verbose_name='Tên sản phẩm')
    brand       = models.CharField(max_length=100, verbose_name='Thương hiệu')
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name='Danh mục')
    size        = models.CharField(max_length=10, choices=SIZE_CHOICES, default='M', verbose_name='Kích cỡ')
    color       = models.CharField(max_length=50, blank=True, verbose_name='Màu sắc')
    gender      = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex', verbose_name='Giới tính')
    material    = models.CharField(max_length=100, blank=True, verbose_name='Chất liệu')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    price       = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Giá (VNĐ)')
    stock       = models.IntegerField(default=0, verbose_name='Tồn kho')
    is_active   = models.BooleanField(default=True, verbose_name='Đang bán')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sản phẩm quần áo'
        verbose_name_plural = 'Sản phẩm quần áo'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand} – {self.name} ({self.size} / {self.color})"
