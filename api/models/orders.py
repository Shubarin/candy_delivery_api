import datetime

from api.models import Courier
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Order(models.Model):
    order_id = models.PositiveIntegerField(primary_key=True)
    weight = models.DecimalField(
        validators=[MaxValueValidator(50)],
        decimal_places=4,
        max_digits=6,
        verbose_name='Weight',
        blank=False,
        db_index=True
    )
    region = models.PositiveSmallIntegerField(
        verbose_name='Region',
        db_index=True,
        validators=[MinValueValidator(1)],
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

    def assign_order(self, courier, assign):
        """Назначает заказ на доставку"""
        if not courier.allowed_orders_weight:
            return None
        # назначаем время выдачи заказа
        self.assign_time = datetime.datetime.now()
        # уменьшаем доступный вес заказов курьера
        courier.allowed_orders_weight -= self.weight
        # помечаем заказ как назначенный
        self.allow_to_assign = False
        self.assign_courier = courier
        assign.orders.add(self)
        assign.courier_type = courier.courier_type
        self.save()

    def cancel_assign(self):
        """Удаляет заказ из назначенной доставки"""
        self.assigns.remove(self.assigns.first())
        self.assign_courier = None
        self.allow_to_assign = True
        self.save()

    def clean(self, *args, **kwargs):
        # Проверка веса
        if self.weight * 100 < 1 or self.weight > 50:
            return ValidationError(f'invalid weight value {self.weight}')
        # Проверка региона
        if not isinstance(self.region, int) or int(self.region) < 1:
            raise ValidationError(f'invalid value in region {self.region}')
        # Проверка времени доставки
        from api.utils import Interval
        try:
            for period in self.delivery_hours:
                Interval.parse_interval(period)
                super(Order, self).clean(*args, **kwargs)
        except ValueError:
            raise ValidationError('invalid values in delivery_hours list')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Order, self).save(*args, **kwargs)
