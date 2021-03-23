import datetime

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models


class TypeChoices(models.TextChoices):
    foot = 'foot'
    bike = 'bike'
    car = 'car'


class Courier(models.Model):
    courier_id = models.PositiveIntegerField(primary_key=True,
                                             unique=True)
    courier_type = models.CharField(
        max_length=4,
        choices=TypeChoices.choices,
        verbose_name='Courier type',
        blank=False,
    )
    regions = ArrayField(models.CharField(max_length=200), blank=False)
    working_hours = ArrayField(models.CharField(max_length=200), blank=False)
    allowed_orders_weight = models.DecimalField(
        decimal_places=4,
        max_digits=6,
        default=10,
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

    def clean(self, *args, **kwargs):
        # Проверка типа курьера
        if self.courier_type not in ('foot', 'bike', 'car'):
            return ValidationError(f'invalid courier_type value')
        # Проверка регионов
        for num in self.regions:
            try:
                if int(num) < 1:
                    raise ValueError('invalid values in regions list')
            except ValueError as e:
                raise ValidationError(e)
        # Проверка времени доставки
        for period in self.working_hours:
            try:
                # Проверяем что конец позже начала, т.к. рабочие часы
                # формируются максимум на одни сутки
                start, end = period.split('-')
                start = datetime.datetime.strptime(start, "%H:%M")
                end = datetime.datetime.strptime(end, "%H:%M")
                interval = end - start
                if interval.days >= 1 or interval.days < 0:
                    raise ValueError
            except ValueError:
                raise ValidationError('invalid values in working_hours list')
        super(Courier, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        super(Courier, self).save(*args, **kwargs)
