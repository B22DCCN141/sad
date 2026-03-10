from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)  # Quan trọng: Kiểm kho khi mua
    category_id = models.IntegerField(null=True)  # Kết nối với catalog-service