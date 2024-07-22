from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify



class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.categoryName


class Listing(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=900)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField(max_length=2000, blank=True)
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, related_name="category" )
    slug = models.SlugField(unique=True, blank=True, null=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name='watchlist')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.listing}"
    
class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid of {self.amount} by {self.user} on {self.listing}"


