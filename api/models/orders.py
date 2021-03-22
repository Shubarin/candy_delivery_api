from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from api.models import Courier


class Order(models.Model):
    order_id = models.PositiveIntegerField(primary_key=True)
    weight = models.DecimalField(
        validators=[MinValueValidator(0.01), MaxValueValidator(50)],
        decimal_places=4,
        max_digits=6,
        verbose_name='Weight',
        blank=False,
        db_index=True
    )
    region = models.PositiveSmallIntegerField(verbose_name='Region',
                                              db_index=True,
                                              blank=False)
    delivery_hours = ArrayField(models.CharField(max_length=200),
                                blank=False)
    assign_courier = models.ForeignKey(
        Courier,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='assign_courier',
        related_name='order'
    )
    assign_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='assign_time'
    )
    complete_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='complete_time'
    )
    allow_to_assign = models.BooleanField(
        blank=True,
        null=True,
        default=True,
        verbose_name='allow_to_assign'
    )
    is_complete = models.BooleanField(
        blank=True,
        null=True,
        verbose_name='is_complete',
        default=False
    )

    def cancel_assign(self):
        self.assign_courier = None
        self.allow_to_assign = True
        self.save()
