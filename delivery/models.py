from django.db import models

from accounts.models import User


class DeliveryPartner(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    phone = models.CharField(max_length=15)

    vehicle_number = models.CharField(max_length=100)

    available = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username