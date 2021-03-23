import datetime
from collections import defaultdict

from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models.couriers import Courier
from api.utils import Interval


class CourierSerializer(serializers.ModelSerializer):
    courier_id = serializers.IntegerField()

    class Meta:
        fields = ('courier_id', 'courier_type', 'regions', 'working_hours')
        model = Courier

    @classmethod
    def validate_courier_id(self, courier_id):
        courier = Courier.objects.filter(pk=courier_id).first()
        if courier:
            raise ValidationError('invalid value courier_id: '
                                  f'({courier_id}) id already exists')
        return courier_id

    @staticmethod
    def validate_courier_type(courier_type):
        if courier_type not in ['foot', 'bike', 'car']:
            raise ValidationError('invalid value courier_type')
        return courier_type

    @staticmethod
    def validate_regions(regions):
        for num in regions:
            try:
                if int(num) < 1:
                    raise ValueError('invalid values in regions list')
            except ValueError as e:
                raise ValidationError(e)
        return regions

    @staticmethod
    def validate_working_hours(working_hours):
        for period in working_hours:
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
        return working_hours

    def to_internal_value(self, data):
        extra_field_in_request = any(
            [field not in self.fields for field in data])
        if extra_field_in_request:
            raise ValidationError(
                {"validation_error": 'extra fields in request'})
        if len(data) == 0:
            raise ValidationError('empty request')
        return super(CourierSerializer, self).to_internal_value(data)

    def update(self, instance, validated_data):
        regions = validated_data.get('regions')
        working_hours = validated_data.get('working_hours')
        courier_type = validated_data.get('courier_type')
        # Проверяем, что смена региона не помешает доставить заказ
        if regions:
            orders = instance.order.exclude(Q(region__in=regions) |
                                            Q(is_complete=True))
            # Снимаем назначение с курьера, делаем заказ доступным для других
            for order in orders:
                order.cancel_assign()
        # Проверяем, что смена рабочего времени не помешает доставить заказ
        if working_hours:
            orders = instance.order.filter(is_complete=False)
            intervals = Interval()
            intervals.set_working_hours(working_hours)
            for order in orders:
                intervals.set_delivery_hours(order.delivery_hours)
                # Снимаем назначение с курьера,
                # делаем заказ доступным для других
                if not intervals.delivery_allowed():
                    order.cancel_assign()
        if courier_type:
            new_max_weight = instance.get_max_weight(courier_type)
            # TODO: вынести текущий максимум в свойство
            if new_max_weight < instance.get_max_weight(instance.courier_type):
                orders = instance.order.filter(is_complete=False)
                instance.allowed_orders_weight = instance.get_max_weight(
                    courier_type)
                # сортируем заказы по возрастанию веса, чтобы сохранить
                # как можно больше заказов без изменений
                for order in sorted(orders, key=lambda x: x.weight):
                    if instance.allowed_orders_weight - order.weight < 0:
                        order.cancel_assign()
                    else:
                        instance.allowed_orders_weight -= order.weight
        return super(CourierSerializer, self).update(instance, validated_data)


class CourierListSerializer(serializers.Serializer):
    data = CourierSerializer(required=False, many=True, write_only=True)

    def create(self, validated_data):
        data = validated_data.get('data')
        if not data:
            raise ValidationError({'validation_error': 'empty request'})
        # проверяем что нет повторяющихся id в запросе
        couriers_ids = [item.get('courier_id') for item in data]
        if len(couriers_ids) != len(set(couriers_ids)):
            ids = defaultdict(int)
            for id in couriers_ids:
                ids[id] += 1
            failed_ids = [{'id': item} for item in ids if ids[item] != 1]
            raise ValidationError({'validation_error': failed_ids})
        couriers = [Courier(**item) for item in data]
        return Courier.objects.bulk_create(couriers)

    def to_representation(self, instance):
        data = {'couriers': [{'id': courier.pk} for courier in instance]}
        return data
