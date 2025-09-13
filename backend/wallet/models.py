from django.db import models
from users.models import CustomUser
from packs.models import Pack

class Deposit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sum = models.DecimalField(max_digits=20, decimal_places=3)
    date = models.DateTimeField()
    wallet = models.TextField()

    def __str__(self):
        return self.user


class Withdrawal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    pack = models.ForeignKey(Pack, on_delete=models.CASCADE)
    date = models.DateTimeField()

    def __str__(self):
        return self.user
