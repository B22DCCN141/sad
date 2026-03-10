from django.db import models
class Rating(models.Model):
    book_id = models.IntegerField()
    customer_id = models.IntegerField()
    stars = models.IntegerField() # 1-5
    comment = models.TextField()