from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.user) if self.user is not None else "DefaultString"

class Product(models.Model):
    category = [
        ("M", "Men"),
        ("W", "Woman"),
        ("K", "Kids"),
    ]
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits = 7, decimal_places= 2)
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True)
    category = models.CharField(max_length = 1, null=True, choices=category)

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try: 
            url = self.image.url
        except:
            url = ''
        return url
    
class DiscountProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_price = models.DecimalField(max_digits = 7, decimal_places= 2, default = 0) #I ADDED THIS AFTER
    original_price = models.DecimalField(max_digits = 7, decimal_places= 2, default = 0)  # Add a field for the original price

    def __str__(self):
        return f"Discount for {self.product.name}"
    
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)

    @property
    def qnt_total(self):
        total = 0
        orderitems = self.orderitem_set.all()
        for item in orderitems:
            total += item.quantity
        return total
    
    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping
    
    @property
    def cart_total(self):

        discount_product = DiscountProduct.objects.all()
        total = 0
        orderitems = self.orderitem_set.all()

        for item in orderitems:
            try:
                discount_product = DiscountProduct.objects.get(product=item.product)
                total += item.quantity * discount_product.discount_price
            except DiscountProduct.DoesNotExist:
                total += item.quantity * item.product.price
        
        return total

    def __str__(self):
        return str(self.id)
    
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        try:
            discount_product = DiscountProduct.objects.get(product=self.product)
        except DiscountProduct.DoesNotExist:
            discount_product = None

        if discount_product:
            total = self.quantity * discount_product.discount_price
        else:
            total = self.quantity * self.product.price
        return total

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address