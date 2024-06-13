from django.db import models
from django.core.files.storage import default_storage
import uuid
# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="images/", storage=default_storage)

class OptionList(models.Model):
    name= models.CharField(max_length=255)
    SELECTION_TYPE_CHOICES = (
        ('SINGLE', 'Single Selection'),
        ('MULTIPLE', 'Multiple Selection')
    )
    selection_type = models.CharField(max_length=10, choices=SELECTION_TYPE_CHOICES)
class Option(models.Model):
    name = models.CharField(max_length=255)
    surcharge = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    option_list = models.ForeignKey(OptionList, on_delete=models.CASCADE)
    
class TemporaryUserID(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    options = models.ManyToManyField(Option, blank=True)
    temporary_user = models.ForeignKey(TemporaryUserID, on_delete=models.CASCADE)