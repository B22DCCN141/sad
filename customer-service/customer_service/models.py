from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)  # Mới: Dùng cho Ship
    address = models.TextField(blank=True, null=True)  # Mới: Dùng cho Ship
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name