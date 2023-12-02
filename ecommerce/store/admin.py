from django.contrib import admin
from .models import Product

# Register your models here.

from .models import *

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Product)
admin.site.register(DiscountProduct)
