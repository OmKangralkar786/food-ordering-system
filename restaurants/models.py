from django.db import models
from accounts.models import User

class Restaurant(models.Model):

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)

    image = models.ImageField(upload_to='restaurants/')

    address = models.TextField()

    cuisine = models.CharField(max_length=100)

    rating = models.FloatField(default=0)

    def __str__(self):
        return self.name


class Review(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username