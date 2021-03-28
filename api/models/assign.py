from api.models import Courier, Order
from api.models.couriers import TypeChoices
from django.db import models


class Assign(models.Model):
    courier = models.ForeignKey(
        Courier,
        related_name='assign',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    courier_type = models.CharField(
        max_length=4,
        choices=TypeChoices.choices,
        verbose_name='Courier type',
        blank=True,
        null=True
    )
    orders = models.ManyToManyField(
        Order,
        blank=True,
        related_name='assigns',
        verbose_name='Orders'
    )
    assign_time = models.DateTimeField(
        auto_now=True,
        db_index=True,
        verbose_name='assign_time'
    )

    is_complete = models.BooleanField(
        blank=True,
        null=True,
        verbose_name='is_complete',
        default=False
    )

    def can_close(self):
        return len(self.orders.all()) == len(
            self.orders.filter(is_complete=True))
