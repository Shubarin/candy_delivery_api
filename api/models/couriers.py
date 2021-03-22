from django.contrib.postgres.fields import ArrayField
from django.db import models


class Courier(models.Model):
    courier_id = models.PositiveIntegerField(primary_key=True,
                                             unique=True)
    courier_type = models.CharField(
        max_length=4,
        verbose_name='Courier type',
        blank=False,
    )
    regions = ArrayField(models.CharField(max_length=200), blank=False)
    working_hours = ArrayField(models.CharField(max_length=200), blank=False)
    allowed_orders_weight = models.DecimalField(
        decimal_places=4,
        max_digits=6,
        blank=True,
        null=True,
        verbose_name='allowed_orders_weight',
    )

    @staticmethod
    def get_max_weight(key):
        units = {
            'foot': 10,
            'bike': 15,
            'car': 50
        }
        return units.get(key, 0)

    def can_take_weight(self, order):
        return self.allowed_orders_weight >= order.weight
