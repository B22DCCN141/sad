from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    # Thêm null=True vào đây tạm thời
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name