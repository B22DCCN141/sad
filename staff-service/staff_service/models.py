from django.db import models

class Staff(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255) # Thêm mật khẩu
    role = models.CharField(max_length=50, default="staff") # Để phân biệt cấp độ
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name