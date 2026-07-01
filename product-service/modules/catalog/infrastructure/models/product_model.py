"""
Django ORM Models - Infrastructure Layer.
Đây là các database model (không phải domain entity).
Tách biệt hoàn toàn với Domain entities.

Thiết kế database theo DDD Cách 2:
- Bảng products với cột attributes (JSONField) - linh hoạt cho mọi loại sản phẩm
- Bảng categories - dữ liệu, có cấu trúc tree (parent)
- Bảng brands - thương hiệu
"""
from django.db import models


class BrandModel(models.Model):
    """ORM model cho thương hiệu sản phẩm."""

    name = models.CharField(max_length=100, unique=True, verbose_name='Thương hiệu')
    slug = models.SlugField(max_length=120, unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    is_active = models.BooleanField(default=True, verbose_name='Hoạt động')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'catalog'
        db_table = 'brands'
        verbose_name = 'Thương hiệu'
        verbose_name_plural = 'Thương hiệu'
        ordering = ['name']

    def __str__(self):
        return self.name


class CategoryModel(models.Model):
    """
    ORM model cho danh mục sản phẩm.
    Hỗ trợ category tree với self-referential FK (parent).

    Danh mục mẫu:
    - Điện tử (root)
      ↳ Điện thoại
      ↳ Laptop
      ↳ Máy tính bảng
    - Thời trang (root)
      ↳ Nam
      ↳ Nữ
    - Mỹ phẩm (root)
    - Đồ gia dụng (root)
    - Sách (root)
    """

    name = models.CharField(max_length=150, verbose_name='Tên danh mục')
    slug = models.SlugField(max_length=180, unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name='Danh mục cha',
    )
    is_active = models.BooleanField(default=True, verbose_name='Hoạt động')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'catalog'
        db_table = 'categories'
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class ProductModel(models.Model):
    """
    ORM model cho sản phẩm - Core model trong Catalog bounded context.

    Thiết kế theo PDF DDD Cách 2:
    - category là FK (dữ liệu), không phải service riêng
    - attributes là JSONField linh hoạt cho mọi loại sản phẩm:
        Phone:   {"ram": "8GB", "storage": "256GB", "screen_size": "6.7 inch", "os": "Android 14"}
        Laptop:  {"ram": "16GB", "cpu": "Intel Core i7", "gpu": "RTX 4060", "storage": "1TB SSD"}
        Fashion: {"size": "L", "color": "Đen", "material": "Cotton", "gender": "Nam"}
        Cosmetic:{"volume": "100ml", "skin_type": "Da hỗn hợp", "expiry": "36 tháng"}
        Book:    {"author": "Nam Cao", "publisher": "NXB Hội Nhà Văn", "pages": 320}
    """

    name = models.CharField(max_length=255, verbose_name='Tên sản phẩm')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    price = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Giá (VNĐ)')
    stock = models.IntegerField(default=0, verbose_name='Tồn kho')

    # Category là DỮ LIỆU - không phải service riêng (DDD Cách 2)
    category = models.ForeignKey(
        CategoryModel,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Danh mục',
    )
    brand = models.ForeignKey(
        BrandModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products',
        verbose_name='Thương hiệu',
    )

    # Attributes JSONB - linh hoạt theo loại sản phẩm (Phone/Laptop/Fashion/...)
    attributes = models.JSONField(default=dict, blank=True, verbose_name='Thuộc tính')

    image_url = models.URLField(blank=True, verbose_name='Ảnh sản phẩm')
    is_active = models.BooleanField(default=True, verbose_name='Đang bán')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'catalog'
        db_table = 'products'
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
