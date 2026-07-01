from django.db import models

class Cart(models.Model):
    customer_id = models.IntegerField(unique=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    # Legacy field kept for backward compatibility with existing book-only flows.
    book_id = models.IntegerField(null=True, blank=True)
    product_type = models.CharField(max_length=20, default='book')
    product_id = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(default=1)