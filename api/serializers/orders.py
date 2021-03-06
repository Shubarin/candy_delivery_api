import datetime

import pytz
from api.models import Courier, Order
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator


class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(validators=[UniqueValidator])

    class Meta:
        fields = ('order_id', 'weight', 'region', 'delivery_hours')
        model = Order

    @staticmethod
    def check_correct_complete_time(instance, complete_time) -> None:
        utc = pytz.UTC
        format_datetime = '%Y-%m-%dT%H:%M:%S.%f%z'
        try:
            date = datetime.datetime.strptime(complete_time, format_datetime)
            asign_date = utc.localize(instance.assign_time)
            if asign_date >= date:
                raise ValidationError('invalid interval to complete time')
        except TypeError:
            raise ValidationError('invalid type complete time')
        except ValueError:
            raise ValidationError('invalid value complete time')

    def to_internal_value(self, data):
        extra_field_in_request = any(
            [field not in self.fields for field in data])
        if extra_field_in_request:
            raise ValidationError(
                {"validation_error": 'extra fields in request'})
        if len(data) == 0:
            raise ValidationError('empty request')
        return super(OrderSerializer, self).to_internal_value(data)

    def update(self, instance, validated_data):
        complete_time = self.context.get('complete_time')
        courier_id = self.context.get('courier_id')
        courier = Courier.objects.get(courier_id=courier_id)
        self.check_correct_complete_time(instance, complete_time)
        instance.complete_time = complete_time
        instance.assign_courier = courier
        instance.is_complete = True
        instance.save()
        # Если все заказы в развозе завершены - завершаем развоз
        assign = instance.assigns.first()
        if assign.can_close():
            assign.is_complete = True
            assign.save()
        return super(OrderSerializer, self).update(instance, validated_data)

    @classmethod
    def validate_order_id(self, order_id):
        order = Order.objects.filter(pk=order_id).exists()
        if order:
            raise ValidationError('invalid value order_id'
                                  f'({order_id}) this id already exists')
        return order_id

    @staticmethod
    def validate_weight(weight):
        if weight * 100 < 1 or weight > 50:
            raise ValidationError('Serializer error invalid value weight')
        return weight

    @staticmethod
    def validate_region(region):
        if region < 1:
            raise ValidationError('invalid value in region')
        return region

    @staticmethod
    def validate_delivery_hours(delivery_hours):
        try:
            for period in delivery_hours:
                # Не проверяем что конец позже начала,
                # т.к. заказ могут ждать ночью с 23:00-02:00
                start, end = period.split('-')
                start = datetime.datetime.strptime(start, "%H:%M")
                end = datetime.datetime.strptime(end, "%H:%M")
            return delivery_hours
        except ValueError:
            raise ValidationError('invalid values in delivery_hours list')


class OrderListSerializer(serializers.Serializer):
    data = OrderSerializer(required=False, many=True, write_only=True)

    def create(self, validated_data):
        data = validated_data.get('data')
        if not data:
            raise ValidationError({'validation_error': 'empty request'})

        orders = [Order(**item) for item in data]
        return Order.objects.bulk_create(orders)

    def to_representation(self, instance):
        data = {'orders': [{'id': order.pk} for order in instance]}
        return data
