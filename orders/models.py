from django.db import models
from accounts.models import User
from menu.models import MenuItem
from delivery.models import DeliveryPartner

class Cart(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.menu_item.price


class Order(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    delivery_partner = models.ForeignKey(
    DeliveryPartner,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
    )

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)

    quantity = models.IntegerField()

    price = models.DecimalField(max_digits=10, decimal_places=2)


class Payment(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    payment_id = models.CharField(max_length=200)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)


class Coupon(models.Model):

    code = models.CharField(max_length=50)

    discount = models.IntegerField()

    active = models.BooleanField(default=True)

    expiry_date = models.DateField()

    minimum_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.code


class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message