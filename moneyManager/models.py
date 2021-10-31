from typing import AbstractSet
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):

    totalMoney = models.IntegerField(default=0)
    currentMoney = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username}"
        

class Categories(models.Model):

    name = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")

    def __str__(self):
        return f"{self.name} : {self.user}"


class Transaction(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactionFor")
    amount = models.IntegerField(default=0)
    date = models.DateField(auto_now=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="category")

    def __str__(self):
        return f"{self.amount} spent on {self.date}"


