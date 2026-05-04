
from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)

    city = models.CharField(max_length=100)
    address_line = models.TextField()
    postal_code = models.CharField(max_length=20, blank=True)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')