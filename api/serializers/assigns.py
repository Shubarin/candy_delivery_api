import datetime
from collections import OrderedDict

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator

from api.models import Order, Assign, Courier
from api.utils import Interval


class AssignSerializer(serializers.ModelSerializer):
    courier_id = serializers.IntegerField(validators=[UniqueValidator],
                                          write_only=True)
    orders = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        many=True,
        required=False)

    class Meta:
        fields = ('courier_id', 'orders', 'assign_time')
        model = Assign

    @classmethod
    def validate_courier_id(self, courier_id):
        courier = Courier.objects.filter(pk=courier_id).exists()
        if not courier:
            raise ValidationError('invalid value courier_id'
                                  f'({courier_id}) is not exists')
        return courier_id

    def to_internal_value(self, data):
        extra_field_in_request = any(
            [field != 'courier_id' for field in data])
        if extra_field_in_request:
            raise ValidationError(
                {"validation_error": 'extra fields in request'})
        if len(data) == 0:
            raise ValidationError('empty request')
        return super(AssignSerializer, self).to_internal_value(data)
    
    def to_representation(self, instance):
        if not instance or isinstance(instance, OrderedDict):
            return {'orders': []}
        orders = [{'id': item.pk} for item in instance.orders.all()]
        assign_time = instance.assign_time
        response = {'orders': orders}
        if orders:
            response['assign_time'] = str(assign_time)
        return response

    def save(self, **kwargs):
        # Получаем курьера, для которого будем назначать заказы
        courier_id = self.validated_data.get('courier_id')
        courier = get_object_or_404(Courier, pk=courier_id)
        # Пересчитываем максимальный вес, с учетом возможных изменений типа
        courier.allowed_orders_weight = courier.get_max_weight(
            courier.courier_type)
        intervals = Interval()
        intervals.set_working_hours(courier.working_hours)
        # ищем подходящие заказы, без учета времени
        orders = Order.objects.filter(weight__lte=courier.allowed_orders_weight,
                                      region__in=courier.regions,
                                      allow_to_assign=True)
        if not orders:
            return None
        assign = Assign.objects.create(courier=courier)
        for order in orders:
            if not courier.allowed_orders_weight:
                break
            intervals.set_delivery_hours(order.delivery_hours)
            if intervals.delivery_allowed() and courier.can_take_weight(order):
                # назначаем время выдачи заказа
                order.assign_time = datetime.datetime.now()
                # уменьшаем доступный вес заказов курьера
                courier.allowed_orders_weight -= order.weight
                # помечаем заказ как назначенный
                order.allow_to_assign = False
                order.assign_courier = courier
                assign.orders.add(order)
                order.save()
        courier.save()
        kwargs = {'orders': assign.orders.all()}
        return super(AssignSerializer, self).save(**kwargs)
