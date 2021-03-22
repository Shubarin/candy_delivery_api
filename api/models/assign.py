from django.db import models

from api.models import Courier, Order


class Assign(models.Model):
    courier = models.ForeignKey(
        Courier,
        related_name='assign',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    orders = models.ManyToManyField(
        Order,
        blank=True,
        related_name='orders',
        verbose_name='Orders'
    )
    assign_time = models.DateTimeField(
        auto_now=True,
        db_index=True,
        verbose_name='assign_time'
    )
