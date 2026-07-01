# comment-rate-service/app/models.py
from django.db import models
from django.utils import timezone

class Rating(models.Model):
    # Legacy field for existing book-only records
    book_id = models.IntegerField(null=True, blank=True)
    product_type = models.CharField(max_length=20, default='book')
    product_id = models.IntegerField(null=True, blank=True)
    customer_id = models.IntegerField()
    stars = models.IntegerField()
    comment = models.TextField(null=True, blank=True)
    # Thêm null=True và blank=True để database không bắt buộc các dòng cũ phải có ngày
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)