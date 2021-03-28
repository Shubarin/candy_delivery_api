from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class TypeChoices(models.TextChoices):
    foot = 'foot'
    bike = 'bike'
    car = 'car'


class Courier(models.Model):
    courier_id = models.PositiveIntegerField(primary_key=True, unique=True)
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

    def can_take_weight(self, order):
        return self.allowed_orders_weight >= order.weight

    def clean(self, *args, **kwargs):
        # Проверка типа курьера
        if self.courier_type not in ('foot', 'bike', 'car'):
            return ValidationError('invalid courier_type value')
        # Проверка регионов
        for num in self.regions:
            try:
                if int(num) < 1:
                    raise ValueError('invalid values in regions list')
            except ValueError as e:
                raise ValidationError(e)
        # Проверка времени доставки
        from api.utils import Interval
        try:
            for period in self.working_hours:
                # Проверяем что конец позже начала, т.к. рабочие часы
                # формируются максимум на одни сутки
                start, end = Interval.parse_interval(period)
                interval = end - start
                if interval.days >= 1 or interval.days < 0:
                    raise ValueError
            super(Courier, self).clean(*args, **kwargs)
        except ValueError:
            raise ValidationError('invalid values in working_hours list')

    def can_take_assign(self):
        return len(self.assign.filter(is_complete=False)) < 1

    def check_change_regions(self, regions) -> None:
        if not regions:
            return None
        orders = self.order.exclude(
            Q(region__in=regions) | Q(is_complete=True))
        # Снимаем назначение с курьера, делаем заказ доступным для других
        for order in orders:
            order.cancel_assign()

    def check_change_working_hours(self, working_hours) -> None:
        if not working_hours:
            return None
        orders = self.order.filter(is_complete=False)
        from api.utils import Interval

        intervals = Interval()
        intervals.set_working_hours(working_hours)
        for order in orders:
            intervals.set_delivery_hours(order.delivery_hours)
            # Если интервал не подходит, то снимаем назначение с курьера,
            # делаем заказ доступным для других
            if not intervals.delivery_allowed():
                order.cancel_assign()

    def check_change_courier_type(self, courier_type) -> None:
        if not courier_type:
            return None
        new_max_weight = self.get_max_weight(courier_type)
        current_max_weight = self.get_max_weight(self.courier_type)
        if new_max_weight >= current_max_weight:
            return None
        orders = self.order.filter(is_complete=False)
        self.allowed_orders_weight = new_max_weight
        # сортируем заказы по возрастанию веса, чтобы сохранить
        # как можно больше заказов без изменений
        for order in sorted(orders, key=lambda order: order.weight):
            if self.allowed_orders_weight - order.weight < 0:
                order.cancel_assign()
            else:
                self.allowed_orders_weight -= order.weight

    @staticmethod
    def get_max_weight(key):
        units = {'foot': 10, 'bike': 15, 'car': 50}
        return units.get(key, 0)

    def save(self, *args, **kwargs):
        self.clean()
        super(Courier, self).save(*args, **kwargs)

    def update_allowed_weight(self):
        self.allowed_orders_weight = self.get_max_weight(self.courier_type)
