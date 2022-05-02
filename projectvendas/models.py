from django.db import models


class Order(models.Model):
    date = models.DateTimeField()
    value = models.DecimalField(max_digits=9, decimal_places=2)
    quantity = models.IntegerField()
    status = models.CharField(max_length=9)
 