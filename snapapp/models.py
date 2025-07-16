from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class EbayItem(models.Model):
    ebay_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    condition = models.CharField(max_length=50)
    image_url = models.URLField(max_length=500, blank=True)
    item_url = models.URLField(max_length=500, blank=True)
    seller_username = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)
    results_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Search histories"

    def __str__(self):
        return f"{self.user.username} - {self.query}"

class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ebay_id = models.CharField(max_length=50)
    item_title = models.CharField(max_length=255, blank=True)
    item_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    item_image_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['user', 'ebay_id']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.item_title}"